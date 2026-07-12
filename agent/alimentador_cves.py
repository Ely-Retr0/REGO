"""
alimentador_cves.py — Jala CVEs nuevos de NVD y los mete a la memoria de REGO
Uso:
    python3 alimentador_cves.py              → Jala los últimos 7 días
    python3 alimentador_cves.py --dias 30    → Últimos 30 días
    python3 alimentador_cves.py --daemon     → Corre en loop, actualiza cada 24h
"""

import requests
import time
import argparse
from datetime import datetime, timedelta, timezone
from memoria import MemoriaREGO

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"

# CVEs de alta criticidad relevantes para ciberseguridad ofensiva/defensiva
KEYWORDS_RELEVANTES = [
    "remote code execution", "privilege escalation", "sql injection",
    "authentication bypass", "buffer overflow", "command injection",
    "path traversal", "xxe", "ssrf", "deserialization",
    "linux kernel", "windows", "apache", "nginx", "ssh", "smb",
    "active directory", "kerberos", "docker", "kubernetes",
    "aws", "azure", "cisco", "fortinet", "palo alto"
]

def es_relevante(descripcion):
    """Filtra CVEs relevantes para seguridad ofensiva/defensiva."""
    desc_lower = descripcion.lower()
    return any(kw in desc_lower for kw in KEYWORDS_RELEVANTES)

def jalar_cves(dias=7, max_cves=100):
    """
    Jala CVEs de NVD de los últimos N días.
    NVD API tiene rate limit: 5 requests/30s sin API key, 50/30s con key.
    """
    memoria = MemoriaREGO()

    ahora = datetime.now(timezone.utc)
    desde = ahora - timedelta(days=dias)

    # Formato que pide NVD
    fecha_inicio = desde.strftime("%Y-%m-%dT%H:%M:%S.000")
    fecha_fin = ahora.strftime("%Y-%m-%dT%H:%M:%S.000")

    params = {
        "pubStartDate": fecha_inicio,
        "pubEndDate": fecha_fin,
        "resultsPerPage": min(max_cves, 2000),
        "startIndex": 0
    }

    print(f"[CVE] Jalando CVEs de los últimos {dias} días...")
    print(f"[CVE] Rango: {fecha_inicio} → {fecha_fin}")

    try:
        # NVD pide esperar entre requests
        time.sleep(1)
        resp = requests.get(NVD_API, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] No se pudo conectar a NVD: {e}")
        return 0

    total = data.get("totalResults", 0)
    vulnerabilidades = data.get("vulnerabilities", [])

    print(f"[CVE] Total disponibles: {total} | Procesando: {len(vulnerabilidades)}")

    guardados = 0
    filtrados = 0

    for item in vulnerabilidades:
        cve = item.get("cve", {})
        cve_id = cve.get("id", "UNKNOWN")

        # Descripción en inglés
        descripciones = cve.get("descriptions", [])
        descripcion = next(
            (d["value"] for d in descripciones if d["lang"] == "en"),
            "No description available"
        )

        # Filtrar por relevancia
        if not es_relevante(descripcion):
            filtrados += 1
            continue

        # CVSS Score
        cvss = "N/A"
        metricas = cve.get("metrics", {})
        for version in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
            if version in metricas and metricas[version]:
                cvss = metricas[version][0].get("cvssData", {}).get("baseScore", "N/A")
                break

        # Solo guardar CVSS >= 6.0 para no llenar la DB de cosas triviales
        try:
            if float(cvss) < 6.0:
                filtrados += 1
                continue
        except (ValueError, TypeError):
            pass  # Si no tiene score, lo guardamos igual

        # Productos afectados
        configuraciones = cve.get("configurations", [])
        productos = []
        for config in configuraciones[:3]:  # Máximo 3 configuraciones
            for nodo in config.get("nodes", [])[:3]:
                for cpe in nodo.get("cpeMatch", [])[:2]:
                    productos.append(cpe.get("criteria", "")[:80])

        productos_str = " | ".join(productos[:5]) if productos else "Ver NVD"

        # Referencias
        referencias = [
            r["url"] for r in cve.get("references", [])[:3]
        ]

        memoria.guardar_cve(
            cve_id=cve_id,
            descripcion=descripcion[:500],
            cvss=cvss,
            referencias=str(referencias),
            productos_afectados=productos_str
        )
        guardados += 1

        # Rate limit: pequeña pausa cada 20 CVEs
        if guardados % 20 == 0:
            print(f"[CVE] Progreso: {guardados} guardados...")
            time.sleep(0.5)

    print(f"\n[CVE] Completado:")
    print(f"  Guardados en memoria: {guardados}")
    print(f"  Filtrados (no relevantes/baja severidad): {filtrados}")
    memoria.stats()
    return guardados

def modo_daemon(dias=1, intervalo_horas=24):
    """Corre en background y actualiza CVEs cada N horas."""
    import schedule

    print(f"[CVE] Modo daemon activo — actualizando cada {intervalo_horas}h")
    print("[CVE] Ctrl+C para detener\n")

    # Primera corrida inmediata
    jalar_cves(dias=dias)

    # Programar corridas futuras
    schedule.every(intervalo_horas).hours.do(jalar_cves, dias=dias)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alimentador de CVEs para REGO")
    parser.add_argument("--dias", type=int, default=7,
                        help="Días hacia atrás para buscar CVEs (default: 7)")
    parser.add_argument("--max", type=int, default=100,
                        help="Máximo de CVEs a procesar (default: 100)")
    parser.add_argument("--daemon", action="store_true",
                        help="Correr en loop, actualiza cada 24h")
    args = parser.parse_args()

    if args.daemon:
        modo_daemon(dias=1, intervalo_horas=24)
    else:
        jalados = jalar_cves(dias=args.dias, max_cves=args.max)
        print(f"\n[CVE] {jalados} CVEs nuevos listos en la memoria de REGO.")
