# Key Concepts / Conceptos Clave
## Understanding how REGO works / Entendiendo cómo funciona REGO

---

## LLM (Large Language Model)

**EN:** The AI brain. llama3.1:8b is a model with 8 billion parameters (numbers) that form a neural network. When you write something, it performs billions of mathematical multiplications and predicts the next word token by token. All "knowledge" is encoded in those numbers — it doesn't query a database.

**ES:** El cerebro de IA. llama3.1:8b es un modelo con 8 mil millones de parámetros (números) que forman una red neuronal. Cuando le escribes algo, realiza billones de multiplicaciones matemáticas y predice la siguiente palabra token por token. Todo el "conocimiento" está codificado en esos números — no consulta una base de datos.

---

## Weights / Pesos

**EN:** The ~4.7 GB file you download with `ollama pull`. Contains all the numbers that make up the neural network. Once downloaded, the model works completely offline.

**ES:** El archivo de ~4.7 GB que descargas con `ollama pull`. Contiene todos los números que forman la red neuronal. Una vez descargado, el modelo funciona completamente offline.

---

## Ollama

**EN:** Local server that loads weights into RAM and serves them as an API on `localhost:11434`. It's the engine that runs REGO's brain.

**ES:** Servidor local que carga los pesos en RAM y los sirve como una API en `localhost:11434`. Es el motor que hace correr el cerebro de REGO.

---

## Modelfile

**EN:** File that defines REGO's personality. The `SYSTEM` block injects a prompt at the start of every conversation telling the neural network how to behave. Nothing is retrained — it's just persistent context.

**ES:** Archivo que define la personalidad de REGO. El bloque `SYSTEM` inyecta un prompt al inicio de cada conversación diciéndole a la red neuronal cómo comportarse. No se reentrena nada — es solo contexto persistente.

---

## RAG (Retrieval-Augmented Generation)

**EN:** The technique that gives REGO updated knowledge without retraining. Before each response, REGO searches ChromaDB for relevant context and injects it into the prompt automatically.

**ES:** La técnica que le da a REGO conocimiento actualizado sin reentrenar. Antes de cada respuesta, REGO busca en ChromaDB contexto relevante y lo inyecta al prompt automáticamente.

```
Query → ChromaDB search → Inject context → Answer with updated info
Consulta → Búsqueda ChromaDB → Inyectar contexto → Responder con info actualizada
```

---

## ChromaDB

**EN:** Local vector database that stores text as mathematical vectors (embeddings). Allows searching by MEANING, not exact words. Lives in `~/.rego/chromadb/`.

**ES:** Base de datos vectorial local que guarda texto como vectores matemáticos (embeddings). Permite buscar por SIGNIFICADO, no por palabras exactas. Vive en `~/.rego/chromadb/`.

---

## Embeddings

**EN:** Mathematical representation of text meaning as numbers. "privilege escalation linux" and "privesc SUID" are different strings but have similar embeddings — ChromaDB finds both.

**ES:** Representación matemática del significado de texto como números. "privilege escalation linux" y "privesc SUID" son strings diferentes pero tienen embeddings similares — ChromaDB encuentra ambos.

---

## num_ctx

**EN:** How many tokens the model can "see" at once (conversation memory). 2048 = faster but shorter memory. 4096 = slower but remembers more context.

**ES:** Cuántos tokens puede "ver" el modelo a la vez (memoria de conversación). 2048 = más rápido pero memoria más corta. 4096 = más lento pero recuerda más contexto.

---

## OPSEC (Operational Security)

**EN:** Not leaking sensitive data to external servers. Since REGO runs locally, your scan outputs, client data, and techniques never leave your machine.

**ES:** No filtrar datos sensibles a servidores externos. Como REGO corre localmente, tus outputs de escaneos, datos de clientes y técnicas nunca salen de tu máquina.

---

## Purple Team

**EN:** Combining offensive (Red Team) and defensive (Blue Team) mindset. Understanding how attacks work in order to build better defenses.

**ES:** Combinar mentalidad ofensiva (Red Team) y defensiva (Blue Team). Entender cómo funcionan los ataques para construir mejores defensas.

---

## CVE (Common Vulnerabilities and Exposures)

**EN:** Official registry of known vulnerabilities. Each has a unique ID (CVE-YEAR-NUMBER) and a CVSS score (0-10) indicating severity. REGO pulls these from NVD automatically.

**ES:** Registro oficial de vulnerabilidades conocidas. Cada una tiene un ID único (CVE-AÑO-NÚMERO) y un puntaje CVSS (0-10) indicando severidad. REGO los jala de NVD automáticamente.

---

## MITRE ATT&CK

**EN:** Framework that catalogs real-world attacker tactics and techniques (TTPs). REGO maps its analysis to these IDs (e.g., T1059.004 = Unix Shell execution).

**ES:** Framework que cataloga tácticas y técnicas de atacantes reales (TTPs). REGO mapea su análisis a estos IDs (ej. T1059.004 = ejecución de Unix Shell).

---

## Knowledge Cutoff

**EN:** llama3.1:8b's training data ends around early 2024. It doesn't know about newer CVEs or techniques. That's exactly why REGO has RAG + NVD auto-updates.

**ES:** Los datos de entrenamiento de llama3.1:8b terminan alrededor de principios de 2024. No sabe de CVEs o técnicas más nuevas. Por eso exactamente REGO tiene RAG + actualizaciones automáticas de NVD.
