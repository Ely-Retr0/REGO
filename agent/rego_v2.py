#!/usr/bin/env python3
"""
REGO v2 — Arquitecto de Ciberseguridad con memoria RAG
Memoria semántica local con ChromaDB + CVEs actualizados automáticamente
"""

import requests
import sys
import json
import os
import re
from datetime import datetime
from memoria import MemoriaREGO

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "rego"

BANNER = """
██████╗ ███████╗ ██████╗  ██████╗     ██╗   ██╗██████╗ 
██╔══██╗██╔════╝██╔════╝ ██╔═══██╗    ██║   ██║╚════██╗
██████╔╝█████╗  ██║  ███╗██║   ██║    ██║   ██║ █████╔╝
██╔══██╗██╔══╝  ██║   ██║██║   ██║    ╚██╗ ██╔╝██╔═══╝ 
██║  ██║███████╗╚██████╔╝╚██████╔╝     ╚████╔╝ ███████╗
╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝      ╚═══╝  ╚══════╝
  Arquitecto de Seguridad | Purple Team | RAG + Memoria
"""

AYUDA = """
┌─────────────────────────────────────────────────────────┐
│                   COMANDOS DE REGO v2                   │
├─────────────────────────────────────────────────────────┤
│  CHAT                                                   │
│  exit / quit        → Terminar sesión                  │
│  clear              → Limpiar pantalla                  │
│  help               → Esta ayuda                        │
│                                                         │
│  ARCHIVOS                                               │
│  file <ruta>        → Analizar output de herramienta   │
│                                                         │
│  MEMORIA                                                │
│  mem stats          → Ver qué sabe REGO                 │
│  mem nota <texto>   → Guardar una nota/técnica          │
│  mem script         → Guardar script de sesión         │
│  mem buscar <query> → Buscar en la memoria             │
│                                                         │
│  CVEs                                                   │
│  cve update         → Actualizar CVEs (últimos 7 días) │
│  cve buscar <query> → Buscar CVEs en memoria           │
└─────────────────────────────────────────────────────────┘
"""

def consultar_ollama(prompt):
    """Envía prompt a Ollama con streaming."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True
    }

    print("\n[REGO] ▶\n" + "─" * 65)

    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=180)
        output = []

        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                chunk = data.get("response", "")
                print(chunk, end="", flush=True)
                output.append(chunk)
                if data.get("done"):
                    break

        print("\n" + "─" * 65)
        return "".join(output)

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Ollama no responde.")
        print("  Verifica: systemctl status ollama")
        return ""

def construir_prompt_rag(mensaje_usuario, contexto_rag, historial):
    """
    Arma el prompt final con:
    - Historial de conversación
    - Contexto RAG (CVEs, scripts, notas relevantes)
    - Mensaje del usuario
    """
    partes = []

    # Historial reciente
    if historial:
        partes.append("=== HISTORIAL DE ESTA SESIÓN ===")
        partes.append("\n".join(historial[-8:]))
        partes.append("")

    # Contexto RAG si existe
    if contexto_rag:
        partes.append(contexto_rag)
        partes.append("")
        partes.append("Usa el contexto anterior de tu memoria si es relevante para responder.")
        partes.append("")

    partes.append(f"Usuario: {mensaje_usuario}")
    partes.append("REGO:")

    return "\n".join(partes)

def detectar_scripts_en_respuesta(respuesta):
    """
    Detecta si REGO generó código en la respuesta.
    Retorna lista de bloques de código encontrados.
    """
    patron = r"```(?:python|bash|sh|powershell|ps1)?\n(.*?)```"
    bloques = re.findall(patron, respuesta, re.DOTALL)
    return [b.strip() for b in bloques if len(b.strip()) > 20]

def guardar_script_interactivo(memoria, codigo, respuesta_contexto):
    """Flujo para guardar un script que REGO generó."""
    print("\n[REGO] Detecté que generé código. ¿Quieres guardarlo en mi memoria?")
    print("  Esto me permite recordarlo y mejorarlo en sesiones futuras.")
    
    confirmar = input("  ¿Guardar? (s/n): ").strip().lower()
    if confirmar != "s":
        return

    nombre = input("  Nombre del script (ej: privesc_suid.py): ").strip()
    if not nombre:
        nombre = f"script_{datetime.now().strftime('%Y%m%d_%H%M')}"

    descripcion = input("  Descripción breve: ").strip()
    tags = input("  Tags separados por coma (ej: privesc,linux,suid): ").strip()
    resultado = input("  Resultado (exitoso/fallido/pendiente): ").strip() or "pendiente"

    # Guarda el primer bloque de código detectado
    memoria.guardar_script(
        nombre=nombre,
        codigo=codigo,
        descripcion=descripcion,
        resultado=resultado,
        tags=tags
    )

def guardar_resumen_sesion(memoria, historial):
    """Guarda un resumen de la sesión al salir."""
    if len(historial) < 4:
        return  # Sesión muy corta, no vale la pena

    # Toma los primeros intercambios como resumen
    resumen = f"Sesión {datetime.now().strftime('%Y-%m-%d %H:%M')}:\n"
    resumen += "\n".join(historial[:6])

    tags_input = input("\n[REGO] ¿Tags para esta sesión? (ej: thm,privesc,linux) [Enter para omitir]: ").strip()
    
    memoria.guardar_sesion(resumen, tags=tags_input)
    print("[REGO] Sesión guardada en memoria ✓")

def modo_archivo(archivo, contexto, memoria):
    """Analiza un archivo con contexto RAG."""
    if not os.path.exists(archivo):
        print(f"[ERROR] No encuentro el archivo: {archivo}")
        return

    with open(archivo, "r", errors="ignore") as f:
        datos = f.read()

    if len(datos) > 6000:
        print(f"[REGO] Archivo grande, usando primeros 6000 caracteres...")
        datos = datos[:6000]

    # Buscar contexto relevante
    print("[REGO] Buscando en mi memoria...", end="", flush=True)
    ctx_rag = memoria.obtener_contexto(datos[:200] + " " + contexto)
    print(" ✓")

    prompt = construir_prompt_rag(
        mensaje_usuario=f"""
Contexto del análisis: {contexto}

Output de herramienta / datos:
{datos}

Analiza con perspectiva Purple Team:
1. Hallazgos ofensivos y vectores de ataque
2. TTPs de MITRE ATT&CK aplicables
3. CVEs conocidos para versiones/servicios encontrados
4. Mitigaciones técnicas concretas
""",
        contexto_rag=ctx_rag,
        historial=[]
    )

    respuesta = consultar_ollama(prompt)

    # Detectar si generó scripts
    if respuesta:
        scripts = detectar_scripts_en_respuesta(respuesta)
        if scripts:
            guardar_script_interactivo(memoria, scripts[0], respuesta)

def modo_interactivo():
    """Modo chat principal con RAG activo."""
    os.system("clear")
    print(BANNER)

    # Inicializar memoria
    memoria = MemoriaREGO()
    memoria.stats()

    print("\nEscribe 'help' para ver todos los comandos.\n")

    historial = []

    while True:
        try:
            entrada = input("\n┌──(tú)\n└─▶ ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            guardar_resumen_sesion(memoria, historial)
            print("[REGO] Stay sharp. Hasta la próxima.")
            break

        if not entrada:
            continue

        cmd = entrada.lower()

        # ── Comandos del sistema ──────────────────────────────────────────

        if cmd in ("exit", "quit"):
            guardar_resumen_sesion(memoria, historial)
            print("[REGO] Stay sharp. Hasta la próxima.")
            break

        elif cmd == "clear":
            os.system("clear")
            print(BANNER)
            continue

        elif cmd == "help":
            print(AYUDA)
            continue

        elif cmd.startswith("file "):
            ruta = entrada[5:].strip()
            ctx = input("  Contexto del análisis (Enter para omitir): ").strip() or "análisis general"
            modo_archivo(ruta, ctx, memoria)
            continue

        # ── Comandos de memoria ───────────────────────────────────────────

        elif cmd == "mem stats":
            memoria.stats()
            continue

        elif cmd.startswith("mem nota "):
            texto = entrada[9:].strip()
            tags = input("  Tags (opcional, Enter para omitir): ").strip()
            memoria.guardar_nota(texto, tags=tags)
            continue

        elif cmd == "mem script":
            nombre = input("  Nombre: ").strip()
            descripcion = input("  Descripción: ").strip()
            print("  Pega el código (termina con '---FIN---' en línea sola):")
            lineas = []
            while True:
                linea = input()
                if linea == "---FIN---":
                    break
                lineas.append(linea)
            codigo = "\n".join(lineas)
            resultado = input("  Resultado (exitoso/fallido/pendiente): ").strip() or "pendiente"
            tags = input("  Tags: ").strip()
            memoria.guardar_script(nombre, codigo, descripcion, resultado, tags)
            continue

        elif cmd.startswith("mem buscar "):
            query = entrada[11:].strip()
            print(f"\n[REGO] Buscando '{query}' en memoria...\n")
            ctx = memoria.obtener_contexto(query)
            print(ctx if ctx else "No encontré nada relevante en mi memoria.")
            continue

        # ── Comandos de CVEs ──────────────────────────────────────────────

        elif cmd == "cve update":
            print("[REGO] Actualizando CVEs de los últimos 7 días...")
            os.system("python3 ~/purple-agent/alimentador_cves.py --dias 7")
            continue

        elif cmd.startswith("cve buscar "):
            query = entrada[11:].strip()
            resultados = memoria.buscar_cves(query, n=5)
            if resultados:
                print(f"\n[REGO] CVEs relevantes para '{query}':\n")
                for r in resultados:
                    print(f"  [{r['metadata']['cve_id']}] CVSS {r['metadata']['cvss']}")
                    print(f"  {r['texto'][:200]}")
                    print()
            else:
                print("[REGO] No encontré CVEs relevantes. Prueba 'cve update' primero.")
            continue

        # ── Chat normal con RAG ───────────────────────────────────────────

        # Buscar contexto relevante en memoria
        print("[REGO] Consultando memoria...", end="", flush=True)
        ctx_rag = memoria.obtener_contexto(entrada)
        indicador = " (encontré contexto relevante ✓)" if ctx_rag else " (sin contexto previo)"
        print(indicador)

        prompt = construir_prompt_rag(entrada, ctx_rag, historial)
        respuesta = consultar_ollama(prompt)

        if respuesta:
            historial.append(f"Usuario: {entrada}")
            historial.append(f"REGO: {respuesta[:400]}")

            # Detectar código generado y ofrecer guardarlo
            scripts = detectar_scripts_en_respuesta(respuesta)
            if scripts:
                guardar_script_interactivo(memoria, scripts[0], respuesta)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        modo_interactivo()
    elif len(sys.argv) >= 2:
        memoria = MemoriaREGO()
        archivo = sys.argv[1]
        contexto = sys.argv[2] if len(sys.argv) > 2 else "análisis general"
        modo_archivo(archivo, contexto, memoria)
    else:
        print("Uso:")
        print("  Chat:     python3 rego_v2.py")
        print("  Archivo:  python3 rego_v2.py <output.txt> [contexto]")
