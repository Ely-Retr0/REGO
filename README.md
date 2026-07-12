<div align="center">

```
██████╗ ███████╗ ██████╗  ██████╗ 
██╔══██╗██╔════╝██╔════╝ ██╔═══██╗
██████╔╝█████╗  ██║  ███╗██║   ██║
██╔══██╗██╔══╝  ██║   ██║██║   ██║
██║  ██║███████╗╚██████╔╝╚██████╔╝
╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ 
```

# REGO — Purple Team AI Agent

**Local AI cybersecurity architect with persistent memory and auto-updated CVE database**

**Agente de IA de ciberseguridad local con memoria persistente y base de CVEs actualizada**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Powered%20by-Ollama-black)](https://ollama.com)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey)](https://www.linux.org/)

[English](#english) · [Español](#español) · [Installation](#installation--instalación) · [Usage](#usage--uso) · [Docs](docs/)

</div>

---

## English

### What is REGO?

REGO is a **100% local** AI cybersecurity agent that runs entirely on your machine. No data leaves your network, no subscription required, no usage limits.

It combines:
- **LLaMA 3.1 8B** as its brain (via Ollama)
- **ChromaDB** for persistent semantic memory
- **NVD API** for automatic CVE updates
- **RAG (Retrieval-Augmented Generation)** to answer with your own knowledge base

REGO thinks like a **Purple Team** professional — understanding both offensive and defensive security to help you hack systems in order to learn how to defend them.

### What can REGO do?

- Analyze raw output from tools like `nmap`, `gobuster`, `linpeas`, `nikto`, `wireshark`
- Generate functional Python, Bash and PowerShell scripts
- Remember scripts that worked and improve them in future sessions
- Stay updated with recent CVEs automatically from NVD
- Map techniques to **MITRE ATT&CK** TTPs
- Cover: Web security, Active Directory, Cloud (AWS/Azure/GCP), Networks, Containers

### Who is this for?

- CTF players (TryHackMe, HackTheBox)
- Cybersecurity students
- Pentesters who care about OPSEC
- Anyone learning offensive/defensive security

---

## Español

### ¿Qué es REGO?

REGO es un agente de IA de ciberseguridad **100% local** que corre completamente en tu máquina. Ningún dato sale de tu red, sin suscripción, sin límites de uso.

Combina:
- **LLaMA 3.1 8B** como cerebro (via Ollama)
- **ChromaDB** para memoria semántica persistente
- **NVD API** para actualización automática de CVEs
- **RAG (Retrieval-Augmented Generation)** para responder con tu propia base de conocimiento

REGO piensa como un profesional de **Purple Team** — entiende seguridad ofensiva y defensiva para ayudarte a hackear sistemas y aprender cómo defenderlos.

### ¿Qué puede hacer REGO?

- Analizar output de herramientas como `nmap`, `gobuster`, `linpeas`, `nikto`, `wireshark`
- Generar scripts funcionales en Python, Bash y PowerShell
- Recordar scripts que funcionaron y mejorarlos en sesiones futuras
- Mantenerse actualizado con CVEs recientes automáticamente desde NVD
- Mapear técnicas a TTPs de **MITRE ATT&CK**
- Cubrir: Seguridad web, Active Directory, Cloud (AWS/Azure/GCP), Redes, Contenedores

### ¿Para quién es esto?

- Jugadores de CTF (TryHackMe, HackTheBox)
- Estudiantes de ciberseguridad
- Pentesters que cuidan su OPSEC
- Cualquiera aprendiendo seguridad ofensiva/defensiva

---

## Architecture / Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR MACHINE / TU MÁQUINA            │
│                                                         │
│   Terminal                                              │
│      │                                                  │
│      ▼                                                  │
│   rego_v2.py  ←──────►  ChromaDB (~/.rego/chromadb/)   │
│      │                   ├── CVEs                       │
│      │                   ├── Scripts                    │
│      │                   ├── Sessions / Sesiones        │
│      │                   └── Notes / Notas             │
│      │                                                  │
│      ▼                                                  │
│   Ollama (localhost:11434)                              │
│      │                                                  │
│      ▼                                                  │
│   llama3.1:8b + REGO Modelfile                         │
│                                                         │
│   alimentador_cves.py ──► NVD API ──► ChromaDB         │
└─────────────────────────────────────────────────────────┘
         ↑
    0 bytes leave this machine / 0 bytes salen de aquí
```

---

## Requirements / Requisitos

| Component | Minimum / Mínimo | Recommended / Recomendado |
|-----------|-----------------|--------------------------|
| RAM | 8 GB | 16 GB |
| Storage / Almacenamiento | 10 GB | 20 GB |
| CPU | 4 cores | 8 cores |
| GPU | Not required / No requerida | NVIDIA (speeds up inference) |
| OS | Linux (any distro) | Debian 13 / Ubuntu 22.04+ |
| Python | 3.8+ | 3.11+ |

> **Tested on / Probado en:** ThinkPad T480 · Intel Core i7 · 16 GB RAM · Intel UHD 620 · Debian 13 Trixie

---

## Installation / Instalación

### Quick Install / Instalación Rápida

```bash
# 1. Clone the repo / Clonar el repo
git clone https://github.com/TU_USUARIO/REGO.git
cd REGO

# 2. Install Ollama / Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 3. Start Ollama / Iniciar Ollama
sudo systemctl enable --now ollama

# 4. Download base model / Descargar modelo base (~4.7 GB)
ollama pull llama3.1:8b

# 5. Run installer / Correr instalador
chmod +x scripts/instalar_rego_v2.sh
./scripts/instalar_rego_v2.sh

# 6. Reload aliases / Recargar aliases
source ~/.bashrc   # bash
# o / or
source ~/.zshrc    # zsh

# 7. Populate CVE database / Poblar base de CVEs
rego-update-30

# 8. Start REGO / Iniciar REGO
rego
```

### Step by Step / Paso a Paso

See the full installation guide: [docs/INSTALL.md](docs/INSTALL.md)

Ver guía completa de instalación: [docs/INSTALL.md](docs/INSTALL.md)

---

## Usage / Uso

### Interactive chat / Chat interactivo

```bash
rego
```

### Analyze tool output / Analizar output de herramientas

```bash
# nmap
nmap -sV -sC 10.10.x.x -oN scan.txt
rego scan.txt "THM lab, Windows machine"

# gobuster
gobuster dir -u http://10.10.x.x -w wordlist.txt | tee web.txt
rego web.txt "web enumeration"

# linpeas
./linpeas.sh | tee linpeas.txt
rego linpeas.txt "Linux privilege escalation"
```

### In-chat commands / Comandos dentro del chat

```
help                    → Show all commands / Ver todos los comandos
file <path>             → Analyze a file / Analizar un archivo
mem stats               → Memory status / Estado de la memoria
mem nota <text>         → Save a note / Guardar una nota
mem buscar <query>      → Search memory / Buscar en memoria
cve update              → Update CVEs (last 7 days)
cve buscar <query>      → Search CVEs in memory
exit                    → End session / Terminar sesión
```

### Weekly routine / Rutina semanal

```bash
rego-update        # Update CVEs / Actualizar CVEs
rego               # Start session / Iniciar sesión
```

---

## File Structure / Estructura de Archivos

```
REGO/
│
├── README.md                    ← You are here / Estás aquí
│
├── agent/                       ← Core agent files / Archivos del agente
│   ├── Modelfile                ← REGO personality / Personalidad de REGO
│   ├── rego_v2.py               ← Main script / Script principal
│   ├── memoria.py               ← ChromaDB memory module
│   └── alimentador_cves.py      ← NVD CVE updater
│
├── scripts/
│   ├── instalar_rego_v2.sh      ← Auto installer / Instalador automático
│   └── requirements.txt         ← Python dependencies
│
├── docs/
│   ├── INSTALL.md               ← Full install guide / Guía completa
│   ├── USAGE.md                 ← Full usage guide / Guía de uso
│   └── CONCEPTS.md              ← Key concepts / Conceptos clave
│
└── writeups/
    └── mr-robot-ctf.md          ← Mr. Robot CTF walkthrough
```

---

## How RAG works / Cómo funciona RAG

```
You ask something / Preguntas algo
           ↓
REGO searches ChromaDB / REGO busca en ChromaDB
(CVEs, saved scripts, notes, past sessions)
           ↓
Finds relevant context by MEANING / Encuentra contexto por SIGNIFICADO
(not exact words / no palabras exactas)
           ↓
Injects context into prompt / Inyecta contexto al prompt
           ↓
Answers with updated knowledge / Responde con conocimiento actualizado
```

---

## Demos

### REGO analyzing an nmap scan

```
┌──(tú)
└─▶ file scan.txt "THM Mr Robot lab"

[REGO] Consultando memoria... (encontré contexto relevante ✓)

[REGO] ▶
──────────────────────────────────────────────────────────────
Analizando el escaneo con perspectiva Purple Team:

RED TEAM:
Puerto 80/443 con WordPress 4.3.1 — versión desactualizada con múltiples
vulnerabilidades conocidas. Vector principal: brute force en /wp-login.php
seguido de RCE via editor de temas (T1059.004).

CVE relevante encontrado en mi memoria:
[CVE-2024-XXXX] WordPress < 6.x — CVSS 8.8 — Authenticated RCE...

BLUE TEAM:
- Actualizar WordPress inmediatamente
- Deshabilitar editor de archivos: define('DISALLOW_FILE_EDIT', true)
- Implementar fail2ban en wp-login.php
──────────────────────────────────────────────────────────────
```

---

## Manage Ollama / Administrar Ollama

```bash
# Status / Estado
systemctl status ollama

# Start / Iniciar
sudo systemctl start ollama

# Stop / Apagar
sudo systemctl stop ollama

# Unload model from RAM / Descargar modelo de RAM
ollama stop rego

# List models / Listar modelos
ollama list

# Models in RAM / Modelos en RAM
ollama ps
```

---

## Troubleshooting

| Problem / Problema | Solution / Solución |
|-------------------|---------------------|
| `command not found: rego` | `source ~/.bashrc` or `source ~/.zshrc` |
| `Connection refused` | `sudo systemctl start ollama` |
| Slow responses / Respuestas lentas | Reduce `num_ctx` to `2048` in Modelfile |
| `model not found` | `ollama list` to verify name |
| No CVEs in memory / Sin CVEs | Run `rego-update-30` first |
| Permission denied port 443 | Use `sudo nc -lvnp 443` |

---

## Disclaimer

> REGO is designed for **educational purposes**, CTF challenges, and authorized penetration testing environments such as TryHackMe, HackTheBox, and personal home labs.
>
> REGO está diseñado para **fines educativos**, desafíos CTF y entornos de pruebas de penetración autorizados como TryHackMe, HackTheBox y laboratorios personales.
>
> **Always work on infrastructure you own or have explicit authorization to test.**
> **Siempre trabaja en infraestructura que sea tuya o tengas autorización explícita de auditar.**

---

## License

MIT License — feel free to use, modify and share.

---

<div align="center">

Made with 🔥 by Regolith | Purple Team mindset

*"To defend a system, you must first know how to break it."*
*"Para defender un sistema, primero debes saber cómo romperlo."*

</div>
