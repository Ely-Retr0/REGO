# 🤖 REGO

> *A local AI trained to think like a Purple Team cybersecurity analyst.*

![Status](https://img.shields.io/badge/status-completed-39ff14?style=flat-square)
![Type](https://img.shields.io/badge/type-local%20AI-ff6a00?style=flat-square)
![Framework](https://img.shields.io/badge/framework-Python-3776AB?style=flat-square&logo=python)
![License](https://img.shields.io/badge/license-MIT-39ff14?style=flat-square)

---

## What is REGO?

REGO is a locally-run AI model trained and fine-tuned to act as a **Purple Team cybersecurity analyst**. It combines offensive (Red Team) and defensive (Blue Team) perspectives into a single agent that can assist with:

- Threat analysis and modeling
- Attack path identification (offensive lens)
- Detection and mitigation recommendations (defensive lens)
- MITRE ATT&CK framework mapping
- Incident response guidance

REGO runs entirely **offline** on your machine — no API keys, no cloud, no data leaving your system.

---

## Purple Team Philosophy

| Red Team (Offensive) | Blue Team (Defensive) |
|---|---|
| How would an attacker get in? | How do we detect this attack? |
| What can be exploited? | What controls are missing? |
| Which paths lead to crown jewels? | How do we respond and recover? |

REGO bridges both sides, giving you a full-picture security analysis.

---

## Features

- 🧠 Local inference — runs on your hardware
- 🎯 MITRE ATT&CK aware — maps threats to the framework automatically
- 🔴 Offensive analysis — identifies attack vectors and TTPs
- 🔵 Defensive recommendations — suggests detections and mitigations
- 💬 Conversational interface — ask questions in natural language
- 🔒 100% offline — your data never leaves your machine

---

## Requirements

- Python 3.10+
- 8GB RAM minimum (16GB recommended)
- GPU optional but recommended for faster inference
- ~4GB disk space for model weights

---

## Quick Start

```bash
git clone https://github.com/Ely-Retr0/REGO
cd REGO
pip install -r requirements.txt
python rego.py
```

---

## Example Usage

```
> REGO: What attack vectors exist on an exposed RDP service?

[REGO - Offensive]: RDP on port 3389 is exposed. Common vectors include:
  - Brute force / credential stuffing (T1110)
  - BlueKeep (CVE-2019-0708) if unpatched
  - Pass-the-hash with stolen NTLM hashes (T1550.002)
  - MitM via RDP downgrade attacks

[REGO - Defensive]: Recommended mitigations:
  - Restrict RDP access via firewall to known IPs only
  - Enable Network Level Authentication (NLA)
  - Deploy MFA on RDP sessions
  - Monitor Event ID 4625 for failed logon attempts
  - Alert on T1110 patterns in SIEM
```

---

## Tech Stack

- **Language:** Python
- **Model:** Fine-tuned local LLM
- **Framework:** MITRE ATT&CK
- **Interface:** CLI / optional web UI

---

## Author

**Elias Diaz Gutierrez** — [@Ely-Retr0](https://github.com/Ely-Retr0)  
*Think outside the fierrewall*
