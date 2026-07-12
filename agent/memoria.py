"""
memoria.py — Base de conocimiento local de REGO
Maneja ChromaDB para CVEs, scripts, notas y sesiones
"""

import chromadb
import os
import json
import hashlib
from datetime import datetime
from sentence_transformers import SentenceTransformer

# Rutas
BASE_DIR = os.path.expanduser("~/.rego")
DB_DIR = os.path.join(BASE_DIR, "chromadb")
os.makedirs(DB_DIR, exist_ok=True)

# Modelo de embeddings — corre 100% local, pesa ~90 MB
# Se descarga solo la primera vez
EMBED_MODEL = "all-MiniLM-L6-v2"

class MemoriaREGO:
    def __init__(self):
        print("[REGO] Cargando memoria...", end="", flush=True)
        
        # Cliente ChromaDB persistente
        self.client = chromadb.PersistentClient(path=DB_DIR)
        
        # Modelo de embeddings local
        self.embedder = SentenceTransformer(EMBED_MODEL)
        
        # Colecciones (como tablas)
        self.cves       = self.client.get_or_create_collection("cves")
        self.scripts    = self.client.get_or_create_collection("scripts")
        self.sesiones   = self.client.get_or_create_collection("sesiones")
        self.notas      = self.client.get_or_create_collection("notas")
        
        print(" listo ✓")

    def _id(self, texto):
        """Genera ID único basado en contenido."""
        return hashlib.md5(texto.encode()).hexdigest()[:16]

    def _embed(self, texto):
        """Convierte texto a vector numérico."""
        return self.embedder.encode(texto).tolist()

    # ─── CVEs ────────────────────────────────────────────────────────────────

    def guardar_cve(self, cve_id, descripcion, cvss, referencias, productos_afectados):
        """Guarda un CVE en la base de conocimiento."""
        texto = f"{cve_id}: {descripcion}. Afecta: {productos_afectados}. CVSS: {cvss}"
        doc_id = self._id(cve_id)

        self.cves.upsert(
            ids=[doc_id],
            embeddings=[self._embed(texto)],
            documents=[texto],
            metadatas=[{
                "cve_id": cve_id,
                "cvss": str(cvss),
                "fecha_guardado": datetime.now().isoformat(),
                "productos": productos_afectados[:200]
            }]
        )

    def buscar_cves(self, query, n=3):
        """Busca CVEs relevantes para una consulta."""
        resultados = self.cves.query(
            query_embeddings=[self._embed(query)],
            n_results=min(n, self.cves.count() or 1)
        )
        if not resultados["documents"][0]:
            return []
        return [
            {
                "texto": doc,
                "metadata": meta
            }
            for doc, meta in zip(
                resultados["documents"][0],
                resultados["metadatas"][0]
            )
        ]

    # ─── SCRIPTS ─────────────────────────────────────────────────────────────

    def guardar_script(self, nombre, codigo, descripcion, resultado, tags=""):
        """
        Guarda un script que funcionó (o falló) con su contexto.
        resultado: 'exitoso' | 'fallido' | 'parcial'
        tags: ej. 'privesc,linux,suid'
        """
        texto = f"Script: {nombre}. Descripción: {descripcion}. Tags: {tags}. Resultado: {resultado}.\nCódigo:\n{codigo}"
        doc_id = self._id(nombre + codigo[:50])

        self.scripts.upsert(
            ids=[doc_id],
            embeddings=[self._embed(texto)],
            documents=[texto],
            metadatas=[{
                "nombre": nombre,
                "resultado": resultado,
                "tags": tags,
                "fecha": datetime.now().isoformat(),
                "descripcion": descripcion[:200]
            }]
        )
        print(f"[REGO] Script '{nombre}' guardado en memoria ✓")

    def buscar_scripts(self, query, n=3):
        """Busca scripts relevantes por descripción o contexto."""
        if self.scripts.count() == 0:
            return []
        resultados = self.scripts.query(
            query_embeddings=[self._embed(query)],
            n_results=min(n, self.scripts.count())
        )
        if not resultados["documents"][0]:
            return []
        return [
            {
                "texto": doc,
                "metadata": meta
            }
            for doc, meta in zip(
                resultados["documents"][0],
                resultados["metadatas"][0]
            )
        ]

    # ─── SESIONES ────────────────────────────────────────────────────────────

    def guardar_sesion(self, resumen, tags=""):
        """Guarda un resumen de sesión para memoria a largo plazo."""
        doc_id = self._id(resumen + datetime.now().isoformat())
        self.sesiones.upsert(
            ids=[doc_id],
            embeddings=[self._embed(resumen)],
            documents=[resumen],
            metadatas=[{
                "fecha": datetime.now().isoformat(),
                "tags": tags
            }]
        )

    def buscar_sesiones(self, query, n=3):
        """Busca sesiones pasadas relevantes."""
        if self.sesiones.count() == 0:
            return []
        resultados = self.sesiones.query(
            query_embeddings=[self._embed(query)],
            n_results=min(n, self.sesiones.count())
        )
        if not resultados["documents"][0]:
            return []
        return [doc for doc in resultados["documents"][0]]

    # ─── NOTAS ───────────────────────────────────────────────────────────────

    def guardar_nota(self, texto, tags=""):
        """Guarda una nota libre — writeups, observaciones, técnicas."""
        doc_id = self._id(texto[:100] + datetime.now().isoformat())
        self.notas.upsert(
            ids=[doc_id],
            embeddings=[self._embed(texto)],
            documents=[texto],
            metadatas=[{
                "fecha": datetime.now().isoformat(),
                "tags": tags
            }]
        )
        print("[REGO] Nota guardada ✓")

    def buscar_notas(self, query, n=3):
        """Busca notas relevantes."""
        if self.notas.count() == 0:
            return []
        resultados = self.notas.query(
            query_embeddings=[self._embed(query)],
            n_results=min(n, self.notas.count())
        )
        if not resultados["documents"][0]:
            return []
        return [doc for doc in resultados["documents"][0]]

    # ─── CONTEXTO RAG ────────────────────────────────────────────────────────

    def obtener_contexto(self, query):
        """
        Punto central del RAG.
        Busca en todas las colecciones y arma un bloque de contexto
        para inyectar al prompt de REGO.
        """
        partes = []

        cves = self.buscar_cves(query, n=2)
        if cves:
            partes.append("=== CVEs RELEVANTES EN MI BASE DE CONOCIMIENTO ===")
            for c in cves:
                partes.append(f"• [{c['metadata']['cve_id']}] CVSS {c['metadata']['cvss']}: {c['texto']}")

        scripts = self.buscar_scripts(query, n=2)
        if scripts:
            partes.append("\n=== SCRIPTS QUE HE USADO ANTES (de mi memoria) ===")
            for s in scripts:
                estado = s['metadata']['resultado'].upper()
                partes.append(f"• [{estado}] {s['metadata']['nombre']}: {s['metadata']['descripcion']}")
                partes.append(f"  Tags: {s['metadata']['tags']}")

        sesiones = self.buscar_sesiones(query, n=2)
        if sesiones:
            partes.append("\n=== CONTEXTO DE SESIONES ANTERIORES ===")
            for ses in sesiones:
                partes.append(f"• {ses}")

        notas = self.buscar_notas(query, n=2)
        if notas:
            partes.append("\n=== NOTAS Y TÉCNICAS GUARDADAS ===")
            for nota in notas:
                partes.append(f"• {nota}")

        if not partes:
            return ""

        return "\n".join(partes)

    # ─── STATS ───────────────────────────────────────────────────────────────

    def stats(self):
        """Muestra cuánto sabe REGO."""
        print(f"""
[REGO] Estado de la memoria:
  CVEs guardados:    {self.cves.count()}
  Scripts guardados: {self.scripts.count()}
  Sesiones pasadas:  {self.sesiones.count()}
  Notas guardadas:   {self.notas.count()}
  Ubicación DB:      {DB_DIR}
        """)
