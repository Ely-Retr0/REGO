# Installation Guide / Guía de Instalación
## REGO — Purple Team AI Agent

---

## Prerequisites / Requisitos previos

```bash
# Update system / Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Install dependencies / Instalar dependencias
sudo apt install -y curl python3 python3-pip git wget
```

---

## Step 1 — Install Ollama / Instalar Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify / Verificar:
```bash
systemctl status ollama
# Should show: active (running)
```

If not running / Si no corre:
```bash
sudo systemctl enable --now ollama
```

Test / Probar:
```bash
curl http://localhost:11434
# Should respond: "Ollama is running"
```

---

## Step 2 — Download base model / Descargar modelo base

```bash
ollama pull llama3.1:8b
```

> ~4.7 GB download. Only once. / ~4.7 GB de descarga. Solo una vez.

Verify / Verificar:
```bash
ollama list
# Should show llama3.1:8b
```

---

## Step 3 — Clone and install REGO / Clonar e instalar REGO

```bash
git clone https://github.com/TU_USUARIO/REGO.git
cd REGO
chmod +x scripts/instalar_rego_v2.sh
./scripts/instalar_rego_v2.sh
```

---

## Step 4 — Reload shell / Recargar shell

```bash
source ~/.bashrc   # If using bash / Si usas bash
source ~/.zshrc    # If using zsh / Si usas zsh
```

---

## Step 5 — Populate CVE database / Poblar base de CVEs

```bash
rego-update-30   # Last 30 days / Últimos 30 días
```

This downloads CVEs from NVD API filtered for offensive/defensive security relevance.

Esto descarga CVEs de NVD API filtrados por relevancia para seguridad ofensiva/defensiva.

---

## Step 6 — First launch / Primer arranque

```bash
rego
```

First time downloads embedding model (~90MB). Only once.

La primera vez descarga el modelo de embeddings (~90MB). Solo una vez.

You should see / Deberías ver:
```
[REGO] Cargando memoria... listo ✓
[REGO] Estado de la memoria:
  CVEs guardados:    XX
  Scripts guardados: 0
  Sesiones pasadas:  0
  Notas guardadas:   0
```

---

## Optional — GPU acceleration / Aceleración GPU

If you have an NVIDIA GPU / Si tienes GPU NVIDIA:

```bash
# Install CUDA drivers first, then Ollama auto-detects
# Instalar drivers CUDA primero, Ollama los detecta automáticamente
ollama run rego
# Check GPU usage / Verificar uso de GPU:
nvidia-smi
```

---

## Updating the base model / Actualizar el modelo base

```bash
# Pull latest version / Jalar versión más reciente
ollama pull llama3.1:8b

# Or try a different model / O probar modelo diferente
ollama pull qwen2.5:7b

# Update REGO's Modelfile / Actualizar Modelfile de REGO
nano ~/purple-agent/Modelfile
# Change: FROM llama3.1:8b → FROM qwen2.5:7b
ollama create rego -f ~/purple-agent/Modelfile
```
