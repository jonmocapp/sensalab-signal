#!/usr/bin/env python3
"""
Pipeline de ex-vendedores de agencia — corre en TU maquina, no en la sesion de Claude.

Que hace
--------
Para cada agencia de universo-agencias.csv consulta Apollo por gente con titulo
comercial, y separa a quien YA NO trabaja ahi. Eso es la lista de ex-vendedores.

Por que Apollo y no raspar LinkedIn
-----------------------------------
Ya lo usas: "Apollo" es la columna de origen en tu Master List. El filtro
q_organization_domains_list de Apollo acepta empleador ACTUAL O PREVIO, que es
exactamente lo que hace falta. Raspar LinkedIn viola su contrato de usuario y el
costo del error lo pagas tu: restriccion o cierre de tu cuenta, en una industria
donde tu LinkedIn ES tu activo.

Uso
---
    pip install requests
    export APOLLO_API_KEY=...            # Windows: set APOLLO_API_KEY=...

    python pipeline_ex_ventas.py --probe          # 1) valida la API con UNA agencia
    python pipeline_ex_ventas.py --solo-strong    # 2) barre las 29 STRONG
    python pipeline_ex_ventas.py                  # 3) barre las 158

Empieza SIEMPRE por --probe: imprime la respuesta cruda para confirmar los nombres
de campo antes de gastar creditos. No pude probar la API desde la sesion de Claude
(apollo.io esta bloqueado por el proxy de red), asi que el probe es la verificacion.

Salidas
-------
    data/ex-vendedores.csv      resultado, ordenado por score
    .cache_apollo/              respuestas crudas; re-correr no vuelve a cobrar
"""
import argparse, csv, json, os, pathlib, re, sys, time, unicodedata

try:
    import requests
except ImportError:
    sys.exit("Falta la libreria: pip install requests")

AQUI  = pathlib.Path(__file__).resolve().parent
DATOS = AQUI / "data"
CACHE = AQUI / ".cache_apollo"
BASE  = "https://api.apollo.io/api/v1"

# Dos rutas segun el plan de Apollo. El probe dice cual responde en tu cuenta.
RUTAS = ["/mixed_people/search", "/mixed_people/api_search"]

TITULOS = [
    "business development", "new business", "account director", "client partner",
    "account executive", "partnerships", "sales director", "sales manager",
    "group account director", "account supervisor", "client services director",
    "chief revenue officer", "vp business development", "head of business development",
]
UBICACIONES = ["Los Angeles, California", "California, US"]


# ----------------------------------------------------------------- utilidades
def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"\b(the|inc|llc|agency|group|co|company|productions?|marketing|"
               r"studios?|experiential|global|usa|worldwide)\b", " ", s)
    return re.sub(r"[^a-z0-9]", "", s)


def clave():
    k = os.environ.get("APOLLO_API_KEY", "").strip()
    if not k:
        sys.exit("Falta APOLLO_API_KEY en el entorno. No la escribas en este archivo.")
    return k


def pedir(ruta, cuerpo, api_key):
    r = requests.post(
        BASE + ruta,
        headers={"Content-Type": "application/json", "Cache-Control": "no-cache",
                 "x-api-key": api_key, "accept": "application/json"},
        json=cuerpo, timeout=45,
    )
    return r


def buscar(dominio, api_key, ruta, pagina=1, por_pagina=100):
    """Gente con titulo comercial ligada a ese dominio (empleo actual O pasado)."""
    cuerpo = {
        "q_organization_domains_list": [dominio],
        "person_titles": TITULOS,
        "person_locations": UBICACIONES,
        "page": pagina,
        "per_page": por_pagina,
    }
    cache = CACHE / f"{dominio.replace('/', '_')}__p{pagina}.json"
    if cache.exists():
        return json.loads(cache.read_text("utf-8")), True
    r = pedir(ruta, cuerpo, api_key)
    if r.status_code == 429:
        time.sleep(20)
        r = pedir(ruta, cuerpo, api_key)
    if r.status_code >= 400:
        return {"_error": r.status_code, "_body": r.text[:400]}, False
    j = r.json()
    CACHE.mkdir(exist_ok=True)
    cache.write_text(json.dumps(j, ensure_ascii=False), "utf-8")
    return j, False


def gente(j):
    """Apollo ha usado 'people' y 'contacts' segun endpoint/plan: acepta ambos."""
    return (j.get("people") or []) + (j.get("contacts") or [])


def empleador_actual(p):
    org = p.get("organization") or {}
    return (org.get("name") or p.get("organization_name") or "",
            (org.get("website_url") or org.get("primary_domain") or "").replace("https://", "")
              .replace("http://", "").replace("www.", "").strip("/"))


def es_ex(p, dominio, agencia):
    """Ex-empleado = aparece ligado a la agencia pero su empleador actual es otro."""
    nom_act, dom_act = empleador_actual(p)
    if not nom_act and not dom_act:
        return True                         # sin empleo actual declarado: candidato fuerte
    if dom_act and norm(dom_act.split(".")[0]) == norm(dominio.split(".")[0]):
        return False
    if nom_act and norm(nom_act) == norm(agencia):
        return False
    return True


def puntua(p, es_ex_flag):
    """Score 0-25 del doc 01-perfil-ideal.md, con lo que Apollo si devuelve."""
    t = (p.get("title") or "").lower()
    s = 0
    # proximidad al comprador
    s += 5 if re.search(r"business development|new business|client partner", t) else \
         4 if re.search(r"account director|group account", t) else \
         3 if re.search(r"account executive|partnership|sales", t) else 2
    # rango (proxy de antiguedad)
    sen = (p.get("seniority") or "").lower()
    s += 5 if sen in ("vp", "head", "c_suite", "owner", "founder") else \
         4 if sen in ("director",) else 3 if sen in ("manager",) else 2
    # frescura: Apollo no da fecha de salida fiable -> se verifica a mano
    s += 3
    # disponibilidad
    nom_act, _ = empleador_actual(p)
    s += 5 if es_ex_flag and not nom_act else 4 if es_ex_flag else 1
    # apetito de comision
    s += 4 if re.search(r"founder|owner|consultant|freelance|independent", t) else 3
    return s


# ----------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true", help="una agencia, imprime respuesta cruda")
    ap.add_argument("--solo-strong", action="store_true", help="solo las 29 STRONG")
    ap.add_argument("--limite", type=int, default=0, help="tope de agencias")
    ap.add_argument("--pausa", type=float, default=1.2, help="segundos entre llamadas")
    a = ap.parse_args()

    api_key = clave()
    filas = list(csv.DictReader((DATOS / "universo-agencias.csv").open(encoding="utf-8")))
    ags = [r for r in filas if r.get("dominio", "").strip()]
    if a.solo_strong:
        ags = [r for r in ags if r["fit_sl26"].startswith("STRONG")]
    if a.limite:
        ags = ags[:a.limite]

    # ---- probe: confirma ruta y forma de la respuesta antes de gastar creditos
    if a.probe:
        r0 = ags[0]
        print(f"Probando con: {r0['agencia']} ({r0['dominio']})\n")
        for ruta in RUTAS:
            j, _ = buscar(r0["dominio"], api_key, ruta)
            if j.get("_error"):
                print(f"  {ruta}: HTTP {j['_error']} -> {j['_body'][:160]}")
                continue
            g = gente(j)
            print(f"  {ruta}: OK, {len(g)} personas (total={j.get('pagination', {}).get('total_entries')})")
            if g:
                print("\n  --- primer registro, campos disponibles ---")
                print("  " + ", ".join(sorted(g[0].keys())))
                print("\n  --- muestra ---")
                print(json.dumps(g[0], ensure_ascii=False, indent=2)[:1400])
                print(f"\n  Confirma que existan: name, title, organization, linkedin_url.")
                print(f"  Si los nombres difieren, dimelo y ajusto empleador_actual() y puntua().")
            return
        print("\nNinguna ruta respondio. Revisa el plan de tu cuenta: la busqueda de personas\n"
              "por API requiere plan de pago en Apollo.")
        return

    # ---- barrido
    out, vistos, fallos = [], set(), []
    for i, r in enumerate(ags, 1):
        dom, ag = r["dominio"], r["agencia"]
        ruta_ok = None
        for ruta in RUTAS:
            j, cacheado = buscar(dom, api_key, ruta)
            if not j.get("_error"):
                ruta_ok = ruta; break
        if ruta_ok is None:
            fallos.append((ag, j.get("_error"), j.get("_body", "")[:120])); continue

        g = gente(j)
        nuevos = 0
        for p in g:
            pid = p.get("id") or p.get("linkedin_url") or (p.get("name", "") + p.get("title", ""))
            if pid in vistos: continue
            vistos.add(pid)
            ex = es_ex(p, dom, ag)
            if not ex: continue                      # solo EX-empleados
            nom_act, _ = empleador_actual(p)
            out.append({
                "score": puntua(p, ex),
                "nombre": p.get("name") or f"{p.get('first_name','')} {p.get('last_name','')}".strip(),
                "titulo_en_agencia": p.get("title", ""),
                "agencia_origen": ag,
                "fit_agencia": r["fit_sl26"],
                "donde_esta_hoy": nom_act or "(sin empleador declarado)",
                "linkedin": p.get("linkedin_url", ""),
                "email": p.get("email", "") or "",
                "ciudad": p.get("city", ""),
                "seniority": p.get("seniority", ""),
                "verificado": "", "contactado": "", "notas": "",
            })
            nuevos += 1
        print(f"[{i}/{len(ags)}] {ag[:38]:<40} {len(g):>3} encontrados  {nuevos:>3} ex-vendedores"
              + ("  (cache)" if cacheado else ""))
        if not cacheado: time.sleep(a.pausa)

    out.sort(key=lambda x: -x["score"])
    DATOS.mkdir(exist_ok=True)
    dest = DATOS / "ex-vendedores.csv"
    with dest.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()) if out else ["score"])
        w.writeheader(); w.writerows(out)

    print(f"\n{'='*62}\n{len(out)} ex-vendedores -> {dest}")
    print(f"score >=20 (contratar):  {sum(1 for x in out if x['score'] >= 20)}")
    print(f"score 14-19 (entrevistar): {sum(1 for x in out if 14 <= x['score'] < 20)}")
    if fallos:
        print(f"\n{len(fallos)} agencias fallaron:")
        for ag, code, body in fallos[:10]:
            print(f"   {ag[:34]:<36} HTTP {code}  {body[:70]}")
    print("\nSiguiente: verifica los de score alto en LinkedIn (fecha de salida y anios de casa)\n"
          "y pasame el CSV para el scoring fino y los mensajes a medida.")


if __name__ == "__main__":
    main()
