#!/usr/bin/env python3
"""
Pipeline de salidas por diff del Internet Archive — corre en TU maquina.

La idea
-------
Las agencias publican su equipo en su propia web. El Internet Archive guarda
versiones viejas de esas paginas. Quien aparecia en la pagina de equipo de 2023
y NO aparece en la de hoy, se fue. Si ademas su titulo era comercial, es
exactamente la persona que buscas.

Por que este si
---------------
- Datos publicos: paginas de marketing que las agencias publican a proposito.
- El Internet Archive tiene API documentada (CDX), abierta y gratuita. Sin llave.
- Sin LinkedIn, sin plan de pago, sin rodear ningun bloqueo.
- Cada nombre sale con EVIDENCIA: el link al snapshot y la fecha. Verificable.

Lo que no hace
--------------
No adivina. Si una agencia no publica equipo (muchos shops chicos no lo hacen),
esa agencia no da resultados y se reporta como tal. No pasa nada: con que
funcione en las grandes ya tienes nombres.

Uso
---
    pip install requests beautifulsoup4     # bs4 es opcional pero mejora mucho

    python pipeline_wayback.py --probar              # test del extractor, sin red
    python pipeline_wayback.py --solo-strong         # las 29 STRONG
    python pipeline_wayback.py --limite 10           # primeras 10
    python pipeline_wayback.py                       # las 105 con dominio

Salidas
-------
    data/salidas-detectadas.csv    personas que desaparecieron, con evidencia
    data/cobertura-equipos.csv     que agencia si publica equipo y cual no
    .cache_wayback/                snapshots crudos; re-correr no vuelve a pedir
"""
import argparse, csv, html, json, os, pathlib, re, sys, time, unicodedata
from collections import defaultdict

try:
    import requests
except ImportError:
    sys.exit("Falta la libreria: pip install requests")
try:
    from bs4 import BeautifulSoup
    HAY_BS4 = True
except ImportError:
    HAY_BS4 = False

AQUI  = pathlib.Path(__file__).resolve().parent
DATOS = AQUI / "data"
CACHE = AQUI / ".cache_wayback"
CDX   = "http://web.archive.org/cdx/search/cdx"
UA    = {"User-Agent": "SensaLab-research/1.0 (hello@sensalab.io)"}

# paginas donde una agencia publica a su gente
RUTA_EQUIPO = re.compile(
    r"/(team|our-team|about|about-us|people|our-people|leadership|staff|"
    r"who-we-are|meet-the-team|crew|company)/?$", re.I)

# titulos que nos interesan
VENTAS = re.compile(
    r"business development|new business|account director|account executive|"
    r"client partner|client services|account manager|account supervisor|"
    r"partnership|sponsorship|\bsales\b|chief revenue|group account|"
    r"managing director|chief executive|\bceo\b|president|founder|principal", re.I)

# cualquier titulo (para saber si el bloque es una ficha de persona)
TITULO = re.compile(
    r"director|manager|producer|president|founder|chief|officer|vp\b|"
    r"vice president|head of|lead\b|partner|principal|executive|coordinator|"
    r"strategist|designer|creative|supervisor|associate|senior|svp|evp", re.I)

NOMBRE = re.compile(r"^[A-Z][a-z'à-ÿ\-]{1,18}(?: [A-Z][a-zA-Z'à-ÿ\.\-]{1,18}){1,2}$")

NO_NOMBRE = {"los angeles","new york","new business","our team","about us","get in touch",
             "contact us","case studies","privacy policy","terms of service","all rights",
             "san francisco","united states","read more","learn more","view work","our work",
             "meet the team","who we are","what we do","brand experience","creative director"}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()


# ------------------------------------------------------------------ extractor
def bloques(doc):
    """Texto visible del HTML, un elemento por entrada, en orden de documento."""
    if HAY_BS4:
        s = BeautifulSoup(doc, "html.parser")
        for t in s(["script", "style", "noscript", "svg", "head"]):
            t.decompose()
        return [re.sub(r"\s+", " ", x).strip() for x in s.stripped_strings]
    doc = re.sub(r"(?is)<(script|style|noscript|svg|head).*?</\1>", " ", doc)
    doc = re.sub(r"(?i)<br\s*/?>|</(p|div|h[1-6]|li|td)>", "\n", doc)
    doc = re.sub(r"(?s)<[^>]+>", "\n", doc)
    return [re.sub(r"\s+", " ", x).strip() for x in html.unescape(doc).split("\n") if x.strip()]


def personas(doc):
    """
    Pares (nombre, titulo) de una pagina de equipo.
    Heuristica: un nombre propio seguido, dentro de 2 bloques, por algo que
    parece un cargo. Es como estan maquetadas casi todas estas paginas.
    """
    b, out, i = bloques(doc), {}, 0

    def es_nombre(s):
        # un nombre no lleva palabras de cargo: "Executive Producer" tambien
        # calza el patron de dos palabras capitalizadas, y no es una persona.
        return (4 < len(s) < 42 and NOMBRE.match(s)
                and not TITULO.search(s) and norm(s) not in NO_NOMBRE)

    while i < len(b):
        n = b[i]
        if es_nombre(n):
            for j in range(i + 1, min(i + 3, len(b))):
                t = b[j]
                if 2 < len(t) < 90 and TITULO.search(t):
                    out[norm(n)] = (n, t)
                    i = j
                    break
        i += 1
    return out


# ------------------------------------------------------------------- wayback
def cdx(dominio, pausa):
    """URLs archivadas de ese dominio que parecen pagina de equipo."""
    cache = CACHE / f"cdx__{dominio.replace('/', '_')}.json"
    if cache.exists():
        return json.loads(cache.read_text("utf-8"))
    p = {"url": f"{dominio}/*", "output": "json", "fl": "original,timestamp",
         "filter": "statuscode:200", "collapse": "urlkey", "limit": "4000"}
    try:
        r = requests.get(CDX, params=p, headers=UA, timeout=60)
        filas = r.json()[1:] if r.status_code == 200 and r.text.strip().startswith("[") else []
    except Exception:
        filas = []
    CACHE.mkdir(exist_ok=True)
    cache.write_text(json.dumps(filas), "utf-8")
    time.sleep(pausa)
    return filas


def snapshots(dominio, pausa):
    """{año: (url, timestamp)} de la mejor pagina de equipo por año."""
    porano = {}
    for fila in cdx(dominio, pausa):
        if len(fila) < 2: continue
        url, ts = fila[0], fila[1]
        ruta = re.sub(r"^https?://[^/]+", "", url).split("?")[0]
        if not RUTA_EQUIPO.search(ruta): continue
        ano = ts[:4]
        # prefiere /team y /people sobre /about
        peso = 0 if re.search(r"/(team|people|staff|leadership)", ruta, re.I) else 1
        if ano not in porano or (peso, ts) < porano[ano][2:]:
            porano[ano] = (url, ts, peso, ts)
    return {a: (v[0], v[1]) for a, v in porano.items()}


def bajar(url, ts, pausa):
    cache = CACHE / f"snap__{ts}__{re.sub(r'[^a-zA-Z0-9]', '_', url)[-60:]}.html"
    if cache.exists():
        return cache.read_text("utf-8", errors="ignore")
    # id_ entrega el HTML original, sin la barra del archivo
    try:
        r = requests.get(f"https://web.archive.org/web/{ts}id_/{url}", headers=UA, timeout=60)
        doc = r.text if r.status_code == 200 else ""
    except Exception:
        doc = ""
    CACHE.mkdir(exist_ok=True)
    cache.write_text(doc, "utf-8")
    time.sleep(pausa)
    return doc


# ---------------------------------------------------------------------- main
def autoprueba():
    muestra = """
    <html><body><div class="team">
      <div class="card"><h3>Taylor Sommer</h3><p>Vice President of Business Development</p></div>
      <div class="card"><h3>Maria Delgado</h3><p>Executive Producer</p></div>
      <div class="card"><h3>Chris Bell</h3><span>Director of Client Partnerships</span></div>
      <div class="card"><h3>Los Angeles</h3><p>Our Studio</p></div>
      <a href="/about">Meet the team</a>
    </div></body></html>"""
    p = personas(muestra)
    print(f"bs4 disponible: {HAY_BS4}")
    print(f"personas extraidas: {len(p)}")
    for k, (n, t) in p.items():
        print(f"   {n:<20}{t:<42}{'VENTAS' if VENTAS.search(t) else ''}")
    ok = len(p) == 3 and "los angeles" not in p
    print("\nextractor:", "OK" if ok else "REVISAR — esperaba 3 personas y descartar 'Los Angeles'")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probar", action="store_true", help="autoprueba del extractor, sin red")
    ap.add_argument("--solo-strong", action="store_true")
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--pausa", type=float, default=1.0, help="segundos entre peticiones al archivo")
    ap.add_argument("--desde", type=int, default=2019, help="año inicial")
    a = ap.parse_args()

    if a.probar:
        sys.exit(0 if autoprueba() else 1)

    filas = list(csv.DictReader((DATOS / "universo-agencias.csv").open(encoding="utf-8")))
    ags = [r for r in filas if r.get("dominio", "").strip()]
    if a.solo_strong:
        ags = [r for r in ags if r["fit_sl26"].startswith("STRONG")]
    if a.limite:
        ags = ags[:a.limite]

    salidas, cobertura = [], []
    for i, r in enumerate(ags, 1):
        dom, ag = r["dominio"].strip(), r["agencia"]
        snaps = {an: v for an, v in snapshots(dom, a.pausa).items() if int(an) >= a.desde}
        if len(snaps) < 2:
            cobertura.append({"agencia": ag, "dominio": dom, "anios_con_equipo": len(snaps),
                              "resultado": "sin pagina de equipo archivada suficiente"})
            print(f"[{i}/{len(ags)}] {ag[:34]:<36} sin historial util")
            continue

        porano = {}
        for an in sorted(snaps):
            doc = bajar(snaps[an][0], snaps[an][1], a.pausa)
            if doc: porano[an] = personas(doc)
        porano = {k: v for k, v in porano.items() if v}
        if len(porano) < 2:
            cobertura.append({"agencia": ag, "dominio": dom, "anios_con_equipo": len(porano),
                              "resultado": "paginas archivadas sin fichas de personas legibles"})
            print(f"[{i}/{len(ags)}] {ag[:34]:<36} sin fichas legibles")
            continue

        anios = sorted(porano)
        ultimo = porano[anios[-1]]
        idas = 0
        for an in anios[:-1]:
            for k, (nom, tit) in porano[an].items():
                if k in ultimo: continue                       # sigue ahi
                if not VENTAS.search(tit): continue            # no es comercial
                if any(k in porano[p] for p in anios[anios.index(an)+1:-1]): 
                    pass                                       # visto despues: ok, igual se fue
                url, ts = snaps[an]
                salidas.append({
                    "nombre": nom, "titulo_en_agencia": tit, "agencia": ag,
                    "fit_agencia": r["fit_sl26"], "visto_por_ultima_vez": an,
                    "ausente_desde": anios[-1],
                    "evidencia": f"https://web.archive.org/web/{ts}/{url}",
                    "verificado": "", "contactado": "", "notas": "",
                })
                idas += 1
        cobertura.append({"agencia": ag, "dominio": dom, "anios_con_equipo": len(porano),
                          "resultado": f"{idas} salidas comerciales detectadas"})
        print(f"[{i}/{len(ags)}] {ag[:34]:<36} {len(anios)} años  ->  {idas} salidas")

    # dedup: la misma persona puede aparecer en varios años
    visto, limpio = set(), []
    for s in sorted(salidas, key=lambda x: -int(x["visto_por_ultima_vez"])):
        k = (norm(s["nombre"]), norm(s["agencia"]))
        if k in visto: continue
        visto.add(k); limpio.append(s)

    DATOS.mkdir(exist_ok=True)
    if limpio:
        with (DATOS / "salidas-detectadas.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(limpio[0].keys())); w.writeheader(); w.writerows(limpio)
    with (DATOS / "cobertura-equipos.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["agencia","dominio","anios_con_equipo","resultado"])
        w.writeheader(); w.writerows(cobertura)

    print(f"\n{'='*62}")
    print(f"{len(limpio)} salidas comerciales -> data/salidas-detectadas.csv")
    print(f"cobertura por agencia -> data/cobertura-equipos.csv")
    print("\nCada fila trae el link al snapshot. Abrelo y confirma antes de escribirle a nadie.")


if __name__ == "__main__":
    main()
