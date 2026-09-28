"""
Detecta senales de independencia en seed-118.csv.

No inventa nada: solo clasifica lo que YA esta en el CSV.

Senal fuerte  = DOMINIO-PROPIO-NOMBRE: el dominio del email contiene el nombre o
                apellido de la persona (leila@leilababoi.com). Registrar un dominio
                con tu propio nombre es lo que hace alguien que construye identidad
                independiente.
Senal media   = INDEPENDIENTE-EXPLICITO: el rol o la empresa dice freelance /
                fractional / independent.
Senal debil   = FREEMAIL: gmail/me.com. Casi siempre significa solo que quien armo
                la lista encontro una direccion personal. NO es evidencia de nada.
"""
import csv, re, pathlib, unicodedata

SRC = pathlib.Path("strategy/04-icp-lista/data/seed-118.csv")
OUT = pathlib.Path("strategy/11-reclutamiento-ventas/data/senales-independencia.csv")

FREEMAIL = {"gmail.com","me.com","icloud.com","yahoo.com","hotmail.com","outlook.com","aol.com"}
RUIDO = {"the","and","inc","llc","group","agency","co","company","productions","production",
         "marketing","media","studios","studio","global","usa","worldwide","experiential"}

# Cuentas vivas en el pipeline de ventas: off-limits para reclutar (ver 03-lista-candidatos.md).
PIPELINE_VIVO = {
    "petrol advertising","spacecube","wasserman","accenture song","good sense & co.","mother",
    "omnicom production","team one","whale film","mirrored media","onboard experiential (obe)",
    "nve experience agency","mkg","sony pictures television","stickerfarmer","ten advertising",
    "ebmg (sports)",
}

def strip_acc(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))

def tokens(s):
    s = strip_acc((s or "").lower())
    return {t for t in re.split(r"[^a-z0-9]+", s) if t and t not in RUIDO and len(t) > 2}

def clasificar(name, company, role, email):
    role_l, comp_l = (role or "").lower(), (company or "").lower()
    explicito = (comp_l in {"independent","freelance"} or "freelance" in role_l
                 or "fractional" in role_l or "independent" in role_l)

    if not email or "@" not in email:
        return ("INDEPENDIENTE-EXPLICITO" if explicito else "SIN-EMAIL"), "", explicito
    dom = email.split("@")[-1].strip().lower()
    base = dom.rsplit(".", 1)[0]                      # quita el TLD
    base_flat = re.sub(r"[^a-z0-9]", "", base)

    # 1. dominio que lleva el nombre de la persona -> senal mas fuerte
    partes = [p for p in re.split(r"[^A-Za-z]+", strip_acc(name or "")) if len(p) > 2]
    for p in partes:
        if p.lower() in base_flat:
            return "DOMINIO-PROPIO-NOMBRE", dom, explicito

    if dom in FREEMAIL:
        return ("INDEPENDIENTE-EXPLICITO" if explicito else "FREEMAIL"), dom, explicito

    # 2. dominio corporativo: solapamiento de tokens o prefijo compartido
    tc, td = tokens(company), tokens(base)
    corp = bool(tc & td) or any(t in base_flat for t in tc) or \
           (len(base_flat) > 4 and base_flat in re.sub(r"[^a-z0-9]", "", strip_acc(comp_l)))
    if corp:
        return ("INDEPENDIENTE-EXPLICITO" if explicito else "CORPORATIVO"), dom, explicito

    return "DOMINIO-NO-COINCIDE", dom, explicito    # anomalia: verificar el dato

rows = list(csv.DictReader(SRC.open(encoding="utf-8")))
out = []
for r in rows:
    senal, dom, _ = clasificar(r["name"], r["company"], r["role"], r["email"])
    if senal == "CORPORATIVO":
        continue
    out.append({
        "nombre": r["name"], "empresa_declarada": r["company"].strip(), "rol": r["role"],
        "familia": r["role_family"], "tier": r["fit_tier"], "email": r["email"], "senal": senal,
        "en_pipeline_ventas": "SI" if r["company"].strip().lower() in PIPELINE_VIVO else "no",
        "notas_originales": r["notes"],
    })

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

ORDEN = {"INDEPENDIENTE-EXPLICITO":0, "DOMINIO-PROPIO-NOMBRE":1, "DOMINIO-NO-COINCIDE":2,
         "FREEMAIL":3, "SIN-EMAIL":4}
print(f"Total en seed-118: {len(rows)}   |   con alguna senal: {len(out)}\n")
for s in ORDEN:
    grupo = [r for r in out if r["senal"] == s]
    if not grupo: continue
    print(f"### {s}  ({len(grupo)})")
    for r in sorted(grupo, key=lambda x: (x["familia"] != "CONNECTOR", x["tier"])):
        flag = "  [PIPELINE-VIVO: no reclutar]" if r["en_pipeline_ventas"] == "SI" else ""
        print(f"  {r['nombre'][:22]:<23}{r['familia']:<10}{r['tier']:<3}"
              f"{r['empresa_declarada'][:32]:<34}{r['email']}{flag}")
    print()
