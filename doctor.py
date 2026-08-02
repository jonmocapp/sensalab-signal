"""
Preflight / diagnostico del bot INMERSIVO. NO envia nada.

Revisa: dependencias, configuracion, alcance de cada fuente RSS, y (si aplica)
que las llaves del ESP esten presentes. Da un reporte claro con checks.

Uso:  python doctor.py
"""
from __future__ import annotations

import sys

OK = "[ OK ]"
WARN = "[WARN]"
FAIL = "[FALLA]"


def check_deps() -> list[str]:
    problems = []
    for mod in ("feedparser", "requests", "dotenv", "anthropic"):
        try:
            __import__(mod)
            print(f"  {OK} dependencia: {mod}")
        except ImportError:
            print(f"  {FAIL} falta dependencia: {mod}  (pip install -r requirements.txt)")
            problems.append(mod)
    return problems


def check_config() -> list[str]:
    import config
    print(f"\n  Modo de envio: SEND_MODE={config.SEND_MODE}  PROVIDER={config.PROVIDER}")
    print(f"  Modelo Claude: {config.ANTHROPIC_MODEL}")
    problems = config.validate(require_api=(config.SEND_MODE != "file"))
    for p in problems:
        tag = WARN if p.startswith("AVISO") else FAIL
        print(f"  {tag} {p}")
    if not problems:
        print(f"  {OK} configuracion coherente")
    if config.ANTHROPIC_API_KEY:
        print(f"  {OK} ANTHROPIC_API_KEY presente")
    else:
        print(f"  {WARN} ANTHROPIC_API_KEY vacia (necesaria para escribir ediciones reales)")
    return [p for p in problems if not p.startswith("AVISO")]


def check_feeds() -> list[str]:
    import requests
    import feedparser
    import sources
    problems = []
    ua = {"User-Agent": sources._UA}
    for src in sources.SOURCES:
        try:
            r = requests.get(src["url"], headers=ua, timeout=25)
            feed = feedparser.parse(r.content)
            n = len(feed.entries)
            if n == 0:
                tag = FAIL if src["tier"] == "core" else WARN
                print(f"  {tag} {src['name']} ({src['tier']}): 0 entradas")
                if src["tier"] == "core":
                    problems.append(src["name"])
            else:
                print(f"  {OK} {src['name']} ({src['tier']}): {n} entradas, HTTP {r.status_code}")
        except Exception as e:
            tag = FAIL if src["tier"] == "core" else WARN
            print(f"  {tag} {src['name']} ({src['tier']}): error {type(e).__name__}")
            if src["tier"] == "core":
                problems.append(src["name"])
    return problems


def main() -> int:
    print("=== DOCTOR :: INMERSIVO (preflight, no envia nada) ===\n")
    print("[1] Dependencias")
    dep = check_deps()
    if dep:
        print(f"\n{FAIL} Faltan dependencias. Corre: pip install -r requirements.txt")
        return 2

    print("\n[2] Configuracion")
    cfg = check_config()

    print("\n[3] Fuentes RSS")
    feeds = check_feeds()

    print("\n=== RESUMEN ===")
    if cfg:
        print(f"{FAIL} Configuracion: {len(cfg)} problema(s) que bloquean el envio.")
    else:
        print(f"{OK} Configuracion lista.")
    if feeds:
        print(f"{WARN} Fuentes CORE sin material: {', '.join(feeds)} (revisa esos feeds).")
    else:
        print(f"{OK} Fuentes CORE respondiendo.")
    print("\nListo. (Este comando nunca envia correos.)")
    return 1 if (cfg or feeds) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n{FAIL} {type(e).__name__}: {e}")
        sys.exit(3)
