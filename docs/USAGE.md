# Usage Guide / Guía de Uso
## REGO — Purple Team AI Agent

---

## Starting REGO / Iniciar REGO

```bash
rego              # Interactive chat / Chat interactivo
rego scan.txt     # Analyze file / Analizar archivo
rego scan.txt "context"   # Analyze with context / Analizar con contexto
```

REGO works from **any directory** / REGO funciona desde **cualquier directorio**.

---

## Analyzing tool output / Analizar output de herramientas

```bash
# nmap
nmap -sV -sC 10.10.x.x -oN scan.txt
rego scan.txt "THM lab, Windows machine"

# gobuster
gobuster dir -u http://10.10.x.x -w /usr/share/wordlists/dirb/common.txt | tee web.txt
rego web.txt "web enumeration, looking for admin panels"

# linpeas (Linux privilege escalation)
./linpeas.sh | tee linpeas.txt
rego linpeas.txt "Linux privesc"

# nikto
nikto -h http://10.10.x.x | tee nikto.txt
rego nikto.txt "web vulnerability scan"

# From inside chat / Desde dentro del chat
rego
>>> file /path/to/output.txt
```

---

## In-chat commands / Comandos en el chat

### Chat
```
exit / quit     → End session (asks to save) / Terminar sesión (pregunta si guardar)
clear           → Clear screen / Limpiar pantalla
help            → Show help / Mostrar ayuda
file <path>     → Analyze file / Analizar archivo
```

### Memory / Memoria
```
mem stats               → Memory status / Estado de memoria
mem nota <text>         → Save a note / Guardar una nota
mem script              → Save a script manually / Guardar script manualmente
mem buscar <query>      → Search all memory / Buscar en toda la memoria
```

### CVEs
```
cve update              → Update CVEs (last 7 days) / Actualizar CVEs (últimos 7 días)
cve buscar <query>      → Search CVEs / Buscar CVEs
```

---

## Script memory workflow / Flujo de memoria de scripts

When REGO generates code, it asks to save it:

Cuando REGO genera código, pregunta si guardarlo:

```
You: write me a SUID enumeration script for Linux

REGO: [generates script]

[REGO] Detected generated code. Save to memory?
  Save? (s/n): s
  Script name: enum_suid.sh
  Brief description: Enumerates SUID files for Linux privesc
  Tags: privesc,linux,suid,enum
  Result (exitoso/fallido/pendiente): pendiente
[REGO] Script 'enum_suid.sh' saved to memory ✓
```

Next session, REGO finds it automatically when relevant.

La próxima sesión, REGO lo encuentra automáticamente cuando es relevante.

---

## CVE Updates / Actualización de CVEs

```bash
rego-update         # Last 7 days / Últimos 7 días
rego-update-30      # Last 30 days / Últimos 30 días

# Manual with options / Manual con opciones
python3 ~/purple-agent/alimentador_cves.py --dias 7
python3 ~/purple-agent/alimentador_cves.py --dias 30 --max 200

# Auto-update daemon (runs every 24h) / Daemon de actualización (cada 24h)
python3 ~/purple-agent/alimentador_cves.py --daemon
```

---

## Managing Ollama / Administrar Ollama

```bash
systemctl status ollama          # Status / Estado
sudo systemctl start ollama      # Start / Iniciar
sudo systemctl stop ollama       # Stop completely / Apagar completamente
ollama stop rego                 # Unload model from RAM / Sacar modelo de RAM
ollama list                      # Downloaded models / Modelos descargados
ollama ps                        # Models in RAM / Modelos en RAM
```

---

## Recommended weekly routine / Rutina semanal recomendada

```bash
# Monday / Lunes
rego-update

# During labs / Durante labs
rego
>>> mem nota <what you learned / lo que aprendiste>

# When a script works / Cuando un script funciona
# REGO asks automatically / REGO pregunta automáticamente
# Answer 's' and tag it: privesc,linux,suid

# Check accumulated knowledge / Ver conocimiento acumulado
rego
>>> mem stats
```

---

## Tips for better responses / Tips para mejores respuestas

```bash
# Give context / Da contexto
rego scan.txt "THM Mr Robot CTF, WordPress 4.3.1, looking for RCE"

# Paste CVE advisories directly / Pega advisories de CVE directamente
rego
>>> Here's the advisory for CVE-2024-XXXX: [paste text]
>>> Analyze and tell me how to exploit and mitigate it

# Ask for specific formats / Pide formatos específicos
>>> Give me a Python script that automates this
>>> Map this to MITRE ATT&CK TTPs
>>> What's the Blue Team mitigation for this?
```
