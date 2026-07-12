#!/bin/bash
# instalar_rego_v2.sh — Setup automático de REGO v2
# Corre esto desde ~/purple-agent/

set -e  # Parar si algo falla

echo ""
echo "██████╗ ███████╗ ██████╗  ██████╗     ██╗   ██╗██████╗"
echo "██╔══██╗██╔════╝██╔════╝ ██╔═══██╗    ██║   ██║╚════██╗"
echo "██████╔╝█████╗  ██║  ███╗██║   ██║    ██║   ██║ █████╔╝"
echo "██╔══██╗██╔══╝  ██║   ██║██║   ██║    ╚██╗ ██╔╝██╔═══╝"
echo "██║  ██║███████╗╚██████╔╝╚██████╔╝     ╚████╔╝ ███████╗"
echo "╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝      ╚═══╝  ╚══════╝"
echo "  Instalador v2 — RAG + Memoria semántica"
echo ""

# ── 1. Verificar Ollama ───────────────────────────────────────────────────────
echo "[1/6] Verificando Ollama..."
if ! systemctl is-active --quiet ollama; then
    echo "  Ollama no está corriendo, iniciando..."
    sudo systemctl start ollama
    sleep 2
fi
echo "  Ollama activo ✓"

# ── 2. Verificar modelo REGO ──────────────────────────────────────────────────
echo "[2/6] Verificando modelo REGO..."
if ! ollama list | grep -q "rego"; then
    echo "  Modelo REGO no encontrado."
    echo "  Asegúrate de haber corrido: ollama create rego -f Modelfile"
    echo "  Puedes continuar la instalación y crearlo después."
else
    echo "  Modelo REGO encontrado ✓"
fi

# ── 3. Crear estructura de directorios ───────────────────────────────────────
echo "[3/6] Creando estructura de directorios..."
mkdir -p ~/purple-agent
mkdir -p ~/.rego/chromadb
echo "  Directorios creados ✓"

# ── 4. Copiar archivos al directorio del proyecto ────────────────────────────
echo "[4/6] Copiando archivos..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cp "$SCRIPT_DIR/memoria.py"          ~/purple-agent/memoria.py
cp "$SCRIPT_DIR/alimentador_cves.py" ~/purple-agent/alimentador_cves.py
cp "$SCRIPT_DIR/rego_v2.py"          ~/purple-agent/rego_v2.py
cp "$SCRIPT_DIR/requirements.txt"    ~/purple-agent/requirements.txt

chmod +x ~/purple-agent/rego_v2.py
chmod +x ~/purple-agent/alimentador_cves.py
echo "  Archivos copiados ✓"

# ── 5. Instalar dependencias Python ──────────────────────────────────────────
echo "[5/6] Instalando dependencias Python..."
echo "  (chromadb, sentence-transformers, requests, schedule)"
echo "  Nota: sentence-transformers descarga ~90MB la primera vez que REGO inicia"
echo ""

pip install --break-system-packages -r ~/purple-agent/requirements.txt

echo "  Dependencias instaladas ✓"

# ── 6. Configurar alias ───────────────────────────────────────────────────────
echo "[6/6] Configurando aliases..."

# Remover alias viejo si existe
sed -i '/alias rego=/d' ~/.bashrc

# Agregar nuevos aliases
cat >> ~/.bashrc << 'EOF'

# REGO v2 — Arquitecto de Ciberseguridad
alias rego="python3 ~/purple-agent/rego_v2.py"
alias rego-file="python3 ~/purple-agent/rego_v2.py"
alias rego-update="python3 ~/purple-agent/alimentador_cves.py --dias 7"
alias rego-update-30="python3 ~/purple-agent/alimentador_cves.py --dias 30"
EOF

source ~/.bashrc 2>/dev/null || true
echo "  Aliases configurados ✓"

# ── Resumen ───────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════"
echo "  REGO v2 instalado correctamente"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  Comandos disponibles (abre terminal nueva o 'source ~/.bashrc'):"
echo ""
echo "  rego                    → Iniciar chat con REGO"
echo "  rego-update             → Actualizar CVEs (últimos 7 días)"
echo "  rego-update-30          → Actualizar CVEs (últimos 30 días)"
echo "  rego scan.txt           → Analizar archivo de herramienta"
echo ""
echo "  Siguiente paso recomendado:"
echo "  rego-update-30   ← Poblar la memoria con CVEs del último mes"
echo ""
echo "  Luego:"
echo "  rego             ← Iniciar REGO (descarga modelo de embeddings ~90MB)"
echo ""
