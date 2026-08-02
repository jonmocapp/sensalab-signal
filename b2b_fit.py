"""
b2b_fit.py — Encaje B2B con el ICP del lector (CEREBRO INMERSIVO, ver notes/CEREBRO-INMERSIVO.md §0).

El lector: productor senior / director creativo en agencias experienciales y marcas.
La pregunta que responde este score: ¿esta noticia le da MUNICION/inspiracion para su
proximo pitch de marca? (test del productor, SL-26).

LOGICA DE PESOS (positivo se suma con cap por categoria; el total positivo se capea a 1.0;
los negativos restan; resultado final clamp a [0, 1]):

  POSITIVO  (peso por hit, cap de hits)
    activation  0.22 x hit (cap 2)  activacion/experiencia de marca: pop-up, flagship,
                                    premiere, instalacion, takeover, experiential...
                                    Es LA senal nuclear: el lector produce exactamente esto.
    tech        0.20 x hit (cap 2)  tech que una agencia puede desplegar via partner
                                    white-label: projection mapping, LED volume, AR/VR/XR,
                                    real-time 3D, virtual production, hologramas...
                                    Segunda senal mas fuerte: es lo que vende SensaLab.
    agency      0.18 x hit (cap 1)  agencia experiencial nombrada (Giant Spoon, Jack
                                    Morton...) o lenguaje "experiential agency": noticia
                                    de un par directo del lector = benchmark inmediato.
    venue       0.15 x hit (cap 2)  venue inmersivo (Sphere, Cosm, Meow Wolf, teamLab...):
                                    el escenario donde vive este mercado.
    brand       0.12 x hit (cap 2)  gran marca con presupuesto (Nike/Netflix/HBO-tier).
                                    Sola NO basta (Apple earnings sigue bajo): solo indica
                                    que hay dinero de marca en la mesa.
    event       0.12 x hit (cap 2)  tentpole/festival donde ocurren activaciones
                                    (Comic-Con, SXSW, Coachella, Super Bowl, CES...).
    production  0.12 x hit (cap 2)  lenguaje de produccion/fabricacion/white-label:
                                    habla el idioma del productor.
    ip          0.06 x hit (cap 1)  IP/franquicia (solo via entities): contexto, no senal.

  SINERGIAS (+0.10 c/u)  la combinacion vale mas que las partes:
    marca x activacion   una gran marca gastando en una experiencia = la historia
                         exacta que el lector lleva a su cliente.
    tech x activacion    tech desplegable DENTRO de una activacion = municion
                         white-label directa para el pitch.

  NEGATIVO  (resta si la categoria se dispara; con evidencia en b2b_reasons)
    -0.35  finanzas/bolsa        earnings, Q1-Q4, revenue, acciones... cero pitch-fuel.
    -0.35  review de gadget      requiere DISPOSITIVO + lenguaje de review (asi una
                                 "review" de una instalacion inmersiva no se castiga).
    -0.35  politica              elecciones, tarifas, congreso...
    -0.35  cripto                bitcoin, blockchain, NFT...
    -0.30  adtech                programmatic, ad spend, cookies... marketing de medios,
                                 no de experiencias.
    -0.25  marketing generico    SEO, social media strategy, influencer/email marketing.
    -0.15  corporativo sin       nombramientos, fusiones, demandas... SOLO castiga si no
           angulo experiencial   hay ninguna senal experiencial (activation/tech/agency/
                                 venue == 0); si la hay, la noticia se defiende sola.

Usa cand.entities si vienen pobladas (suman hits a su categoria, deduplicadas contra los
matches de keywords), pero NO depende de ellas: los lexicos propios cubren entities vacias.
Interfaz: b2b_score(cand) -> float 0..1 · score_all(cands) escribe cand.scores["b2b"] ·
b2b_reasons(cand) -> list[str] para depurar/explicar.
"""
from __future__ import annotations

import re

from models import Candidate

# ---------------------------------------------------------------------------
# Lexicos propios (con limites de palabra). "phrase" admite espacio o guion
# entre tokens ("pop up" matchea "pop-up"); los acronimos van case-sensitive
# para no confundir AR/VR/LED con palabras comunes ("are", "led"...).
# ---------------------------------------------------------------------------

def _phrase(p: str) -> str:
    toks = [re.escape(t) for t in p.split()]
    return r"\b" + r"[\s\-]+".join(toks) + r"\b"


def _compile(phrases=(), raw=(), flags=re.IGNORECASE):
    pats = sorted((_phrase(p) for p in phrases), key=len, reverse=True)
    pats += list(raw)
    if not pats:
        return None
    return re.compile("|".join(pats), flags)


_ACTIVATION = _compile(
    phrases=(
        "activation", "activations", "experiential", "immersive", "pop up", "popup",
        "premiere", "installation", "installations", "takeover", "brand experience",
        "fan experience", "interactive experience", "live experience", "launch event",
        "photo op", "exhibit", "exhibition", "pavilion",
    ),
    # "flagship" cuenta solo si NO es el flagship-phone de turno (eso es gadget-land)
    raw=(r"\bflagship\b(?!\s+(?:phone|smartphone|device|handset|model|chip|laptop|processor|tv)s?\b)",),
)

_TECH_CI = _compile(phrases=(
    "projection mapping", "projection mapped", "projected onto", "augmented reality",
    "virtual reality", "mixed reality", "extended reality", "real time 3d",
    "real time rendering", "real time graphics", "unreal engine", "game engine",
    "touchdesigner", "virtual production", "motion capture", "mocap",
    "gaussian splatting", "hologram", "holograms", "holographic", "anamorphic",
    "kinetic sculpture", "drone show", "drone light show", "interactive",
    "volumetric", "generative", "spatial computing", "vision pro",
))
_TECH_CS = _compile(
    raw=(
        r"\bAR\b", r"\bVR\b", r"\bXR\b",
        r"\bLED[\s\-]+(?i:volume|volumes|wall|walls|screen|screens|display|displays|facade)\b",
        r"\bUnity\s+(?i:engine|editor|technologies|6)\b",
    ),
    flags=0,
)

_AGENCY = _compile(
    phrases=(
        "giant spoon", "momentum worldwide", "jack morton", "superfly", "160over90",
        "becore", "little cinema", "invisible north", "imprint projects",
        "experiential agency", "experiential marketing agency", "event agency",
        "creative agency", "brand experience agency", "agency of record",
    ),
    raw=(r"\bgeorge\s+p\.?\s+johnson\b", r"\bwe'?re\s+magnetic\b"),
)

_BRAND = _compile(phrases=(
    "nike", "netflix", "disney", "hbo", "sony", "apple", "amazon", "google",
    "microsoft", "samsung", "coca cola", "pepsi", "lululemon", "skims", "fender",
    "sephora", "workday", "spotify", "red bull", "adidas", "louis vuitton", "gucci",
    "chanel", "dior", "porsche", "bmw", "mercedes", "audi", "lego", "starbucks",
    "mcdonald", "heineken", "american express", "ikea", "verizon", "t mobile",
    "marvel", "warner bros", "paramount", "nbcuniversal", "prime video",
))

_VENUE = _compile(phrases=(
    "sphere", "cosm", "meow wolf", "teamlab", "outernet", "illuminarium",
    "area15", "superblue", "frameless",
))

_EVENT_CI = _compile(phrases=(
    "comic con", "sxsw", "coachella", "super bowl", "cannes lions", "art basel",
    "siggraph", "world cup", "olympics", "fashion week", "lollapalooza",
    "sundance", "tribeca", "formula 1", "grand prix",
))
_EVENT_CS = _compile(raw=(r"\bCES\b", r"\bGDC\b", r"\bF1\b"), flags=0)

_PRODUCTION = _compile(phrases=(
    "white label", "fabrication", "fabricated", "fabricator", "creative production",
    "production company", "production studio", "production design", "scenic",
    "staging", "set design", "build out", "stagecraft", "technical production",
    "content engine", "creative technology", "creative technologist",
    "experience design",
))

# --- negativos ---
_FINANCE_CI = _compile(phrases=(
    "earnings", "quarterly", "revenue", "beat estimates", "missed estimates",
    "profit", "net income", "share price", "stock price", "stocks", "shares",
    "market cap", "valuation", "guidance", "dividend", "wall street",
    "funding round", "box office", "layoffs", "job cuts",
))
_FINANCE_CS = _compile(raw=(r"\bQ[1-4]\b", r"\bIPO\b"), flags=0)

_DEVICE = _compile(phrases=(
    "iphone", "ipad", "macbook", "galaxy s", "google pixel", "smartphone",
    "handset", "laptop", "earbuds", "headphones", "smartwatch", "gaming console",
    "graphics card", "tablet", "camera", "router",
))
_REVIEW = _compile(
    phrases=(
        "review", "reviewed", "hands on", "unboxing", "benchmark", "battery life",
        "specs", "spec sheet", "first impressions", "tested", "worth it",
        "buying guide", "deals", "discount", "price drop",
    ),
    raw=(r"\bvs\.?\b",),
)

_POLITICS = _compile(phrases=(
    "election", "senate", "congress", "white house", "tariff", "tariffs",
    "legislation", "lawmakers", "supreme court", "geopolitics", "sanctions",
    "immigration",
))

_CRYPTO_CI = _compile(phrases=(
    "crypto", "cryptocurrency", "bitcoin", "ethereum", "blockchain", "web3",
    "stablecoin", "memecoin",
))
_CRYPTO_CS = _compile(raw=(r"\bNFTs?\b", r"\bBTC\b"), flags=0)

_ADTECH = _compile(
    phrases=(
        "programmatic", "adtech", "ad tech", "ad spend", "media buying",
        "cookieless", "third party cookies", "retail media", "attribution",
    ),
    raw=(),
)
_ADTECH_CS = _compile(raw=(r"\bCPMs?\b", r"\bDSPs?\b"), flags=0)

_GENERIC_MKT_CI = _compile(phrases=(
    "social media strategy", "social media marketing", "influencer marketing",
    "email marketing", "content marketing", "engagement rate", "search ranking",
    "algorithm update",
))
_GENERIC_MKT_CS = _compile(raw=(r"\bSEO\b",), flags=0)

_CORPORATE = _compile(phrases=(
    "appoints", "names new", "steps down", "resigns", "merger", "acquires",
    "acquisition", "restructuring", "hiring freeze", "board of directors",
    "antitrust", "lawsuit", "settlement",
))

# ---------------------------------------------------------------------------
# Pesos (documentados arriba, en el docstring)
# ---------------------------------------------------------------------------

# categoria -> (peso por hit, cap de hits, regexes, etiqueta para reasons)
_POSITIVE = {
    "activation": (0.22, 2, (_ACTIVATION,),          "activacion/experiencia de marca"),
    "tech":       (0.20, 2, (_TECH_CI, _TECH_CS),    "tech desplegable por agencia"),
    "agency":     (0.18, 1, (_AGENCY,),              "agencia experiencial"),
    "venue":      (0.15, 2, (_VENUE,),               "venue inmersivo"),
    "brand":      (0.12, 2, (_BRAND,),               "gran marca (presupuesto)"),
    "event":      (0.12, 2, (_EVENT_CI, _EVENT_CS),  "tentpole/festival"),
    "production": (0.12, 2, (_PRODUCTION,),          "lenguaje de produccion/white-label"),
    "ip":         (0.06, 1, (),                      "IP/franquicia"),
}

_SYNERGY_BONUS = 0.10  # marca x activacion / tech x activacion

# categoria negativa -> (penalizacion, regexes, etiqueta)
_NEGATIVE = {
    "finance":  (0.35, (_FINANCE_CI, _FINANCE_CS),        "finanzas/bolsa"),
    "politics": (0.35, (_POLITICS,),                      "politica"),
    "crypto":   (0.35, (_CRYPTO_CI, _CRYPTO_CS),          "cripto"),
    "adtech":   (0.30, (_ADTECH, _ADTECH_CS),             "adtech"),
    "genmkt":   (0.25, (_GENERIC_MKT_CI, _GENERIC_MKT_CS), "marketing generico"),
}
_GADGET_PENALTY = 0.35     # dispositivo + lenguaje de review
_CORPORATE_PENALTY = 0.15  # solo sin senal experiencial

# entities del lexicon -> categoria positiva
_ENTITY_BUCKET = {"brands": "brand", "agencies": "agency", "tech": "tech",
                  "venues": "venue", "ip": "ip"}


def _norm(s: str) -> str:
    return re.sub(r"[\s\-]+", " ", s.lower()).strip()


def _find(regexes, text: str) -> dict:
    """dict {forma_normalizada: forma_original} de matches unicos."""
    found: dict[str, str] = {}
    for rx in regexes:
        if rx is None:
            continue
        for m in rx.finditer(text):
            found.setdefault(_norm(m.group(0)), m.group(0))
    return found


def _analyze(cand: Candidate) -> tuple[float, list[str]]:
    """Motor comun de b2b_score y b2b_reasons: (score 0..1, porques)."""
    text = f"{cand.headline} {cand.summary}"
    reasons: list[str] = []

    # 1) hits positivos por keywords propios
    hits = {name: _find(rxs, text) for name, (_, _, rxs, _) in _POSITIVE.items()}

    # 2) entities del lexicon (si vienen): suman senal, deduplicadas
    for ecat, bucket in _ENTITY_BUCKET.items():
        for item in (cand.entities or {}).get(ecat, []) or []:
            key = _norm(str(item))
            if key:
                hits[bucket].setdefault(key, f"{item} [entity]")

    # 3) suma positiva (peso x hits, con cap por categoria)
    pos = 0.0
    for name, (weight, cap, _, label) in _POSITIVE.items():
        found = list(hits[name].values())
        n = min(len(found), cap)
        if n:
            pts = weight * n
            pos += pts
            reasons.append(f"+{pts:.2f} {label}: {', '.join(found[:cap])}")

    # 4) sinergias: la combinacion es la historia
    if hits["brand"] and hits["activation"]:
        pos += _SYNERGY_BONUS
        reasons.append(f"+{_SYNERGY_BONUS:.2f} sinergia marca x activacion (pitch-fuel directo)")
    if hits["tech"] and hits["activation"]:
        pos += _SYNERGY_BONUS
        reasons.append(f"+{_SYNERGY_BONUS:.2f} sinergia tech x activacion (municion white-label)")

    pos = min(pos, 1.0)

    # 5) penalizaciones
    neg = 0.0
    for _, (penalty, rxs, label) in _NEGATIVE.items():
        found = list(_find(rxs, text).values())
        if found:
            neg += penalty
            reasons.append(f"-{penalty:.2f} {label}: {', '.join(found[:3])}")

    # gadget review: requiere dispositivo Y lenguaje de review
    devices = list(_find((_DEVICE,), text).values())
    review_terms = list(_find((_REVIEW,), text).values())
    if devices and review_terms:
        neg += _GADGET_PENALTY
        reasons.append(f"-{_GADGET_PENALTY:.2f} review de gadget de consumo: "
                       f"{', '.join((devices + review_terms)[:3])}")

    # corporativo: solo castiga si NO hay ninguna senal experiencial
    experiential_signal = any(hits[k] for k in ("activation", "tech", "agency", "venue"))
    corp = list(_find((_CORPORATE,), text).values())
    if corp and not experiential_signal:
        neg += _CORPORATE_PENALTY
        reasons.append(f"-{_CORPORATE_PENALTY:.2f} corporativo sin angulo experiencial: "
                       f"{', '.join(corp[:3])}")

    score = max(0.0, min(1.0, pos - neg))
    return score, reasons


# ---------------------------------------------------------------------------
# API publica (interfaz comun del cerebro: score puro + enrich in situ)
# ---------------------------------------------------------------------------

def b2b_score(cand: Candidate) -> float:
    """Encaje B2B con el ICP, 0.0-1.0. Alto = municion de pitch para el productor."""
    return _analyze(cand)[0]


def b2b_reasons(cand: Candidate) -> list[str]:
    """Porques legibles del score (depurar/explicar). Lista vacia = cero senal."""
    return _analyze(cand)[1]


def score_all(cands: list[Candidate]) -> None:
    """Escribe cand.scores['b2b'] en cada candidato (muta in situ)."""
    for cand in cands:
        cand.scores["b2b"] = round(b2b_score(cand), 4)
