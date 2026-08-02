"""
calendar_events.py — Calendario de tentpoles / momentos culturales-tech del CEREBRO INMERSIVO.

Detecta el "momento activo" por fecha para habilitar ediciones tematicas:
  - "just-ended": recien termino (util para recap / steal-this playbook)
  - "live":       esta ocurriendo ahora (edicion Momento/Tematica)
  - "upcoming":   viene pronto (util para preview)

Modelado de ventanas:
  window = {"start": (mes, dia), "end": (mes, dia)}        -> patron RECURRENTE anual
  window = {..., "year": 2026}                              -> evento ANCLADO a un anio
                                                               (ej. Mundial 2026, no anual)
  Las fechas son las reales/aproximadas de 2026; para eventos recurrentes el patron
  mes/dia se resuelve contra el anio de la fecha consultada (y anios adyacentes, para
  cubrir bordes de anio como Art Basel Miami a inicios de enero).

Overrides por momento (opcionales, se toman contra los parametros globales con max()):
  "lead_days": ventana de preview mas larga (ej. SIGGRAPH: cobertura previa ~3 semanas)
  "tail_days": ventana de recap mas larga (ej. Mundial: el steal-this vive ~1 mes)

"brand_activation": True marca los tentpoles especialmente relevantes para
activaciones de marca (el pan de cada dia del ICP: productores experienciales).

La fecha SIEMPRE llega como parametro (`date` o `datetime`): sin relojes ocultos.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta

from models import Candidate

# ---------------------------------------------------------------------------
# Calendario de tentpoles (fechas 2026 reales/aproximadas)
# ---------------------------------------------------------------------------

MOMENTS: list[dict] = [
    {
        "id": "ces",
        "name": "CES (Las Vegas)",
        "keywords": ["ces", "consumer electronics show"],
        "window": {"start": (1, 6), "end": (1, 9)},
        "brand_activation": True,   # booths/experiencias de marca en Vegas
    },
    {
        "id": "sundance",
        "name": "Sundance Film Festival",
        "keywords": ["sundance"],
        "window": {"start": (1, 22), "end": (2, 1)},
        "brand_activation": True,   # brand houses / lounges en Park City
    },
    {
        "id": "super-bowl",
        "name": "Super Bowl",
        "keywords": ["super bowl", "superbowl", "halftime show"],
        "window": {"start": (2, 2), "end": (2, 8)},   # semana del SB LX (8-feb-2026)
        "brand_activation": True,   # la semana de activaciones mas cara del anio
        "tail_days": 14,
    },
    {
        "id": "sxsw",
        "name": "SXSW (Austin)",
        "keywords": ["sxsw", "south by southwest"],
        "window": {"start": (3, 12), "end": (3, 18)},
        "brand_activation": True,   # capital mundial de la brand activation
    },
    {
        "id": "gdc",
        "name": "Game Developers Conference",
        "keywords": ["gdc", "game developers conference"],
        "window": {"start": (3, 23), "end": (3, 27)},
        "brand_activation": False,  # conferencia dev: senal tech (Unreal/Unity)
    },
    {
        "id": "coachella",
        "name": "Coachella (2 fines de semana)",
        "keywords": ["coachella"],
        "window": {"start": (4, 10), "end": (4, 19)},  # cubre ambos weekends
        "brand_activation": True,   # festival = feria de activaciones
        "tail_days": 21,            # el steal-this post-festival vive semanas
    },
    {
        "id": "nab",
        "name": "NAB Show (Las Vegas)",
        "keywords": ["nab show", "national association of broadcasters"],
        "window": {"start": (4, 18), "end": (4, 22)},
        "brand_activation": False,  # tech broadcast/produccion: senal tech
    },
    {
        "id": "milan-design-week",
        "name": "Milan Design Week / Salone del Mobile",
        "keywords": ["milan design week", "salone del mobile", "fuorisalone"],
        "window": {"start": (4, 20), "end": (4, 26)},
        "brand_activation": True,   # instalaciones de marca (tech+design)
    },
    {
        "id": "wwdc",
        "name": "Apple WWDC",
        "keywords": ["wwdc", "worldwide developers conference"],
        "window": {"start": (6, 8), "end": (6, 12)},
        "brand_activation": False,  # senal tech-unlock (Vision Pro, ARKit)
    },
    {
        "id": "world-cup",
        "name": "FIFA World Cup 2026 (US/Canada/Mexico)",
        "keywords": ["world cup", "mundial", "fifa", "copa del mundo"],
        "window": {"start": (6, 11), "end": (7, 19), "year": 2026},  # cada 4 anios
        "brand_activation": True,   # co-sede US: fan fests y activaciones masivas
        "tail_days": 30,            # recap "mejores ideas del Mundial" vive ~1 mes
    },
    {
        "id": "cannes-lions",
        "name": "Cannes Lions",
        "keywords": ["cannes lions", "cannes"],
        "window": {"start": (6, 22), "end": (6, 26)},
        "brand_activation": True,   # EL tentpole de la industria creativa
        "tail_days": 21,            # los ganadores se comentan semanas despues
    },
    {
        "id": "comic-con",
        "name": "San Diego Comic-Con",
        "keywords": ["comic-con", "comic con", "sdcc", "hall h"],
        "window": {"start": (7, 22), "end": (7, 26)},  # preview night 22-jul-2026
        "brand_activation": True,   # offsites/activaciones de studios en el Gaslamp
    },
    {
        "id": "siggraph",
        "name": "SIGGRAPH (Los Angeles)",
        "keywords": ["siggraph"],
        # SIGGRAPH 2026: 19-23 jul, LA Convention Center (fuente: s2026.siggraph.org).
        "window": {"start": (7, 19), "end": (7, 23)},
        "brand_activation": False,  # nucleo tech: real-time, splatting, graficos
        "lead_days": 21,            # el preview editorial arranca ~3 semanas antes
    },
    {
        "id": "art-basel-miami",
        "name": "Art Basel Miami Beach",
        "keywords": ["art basel", "miami art week", "design miami"],
        "window": {"start": (12, 2), "end": (12, 6)},
        "brand_activation": True,   # arte + marcas + instalaciones inmersivas
    },
]

_PHASE_ORDER = {"live": 0, "just-ended": 1, "upcoming": 2}


# ---------------------------------------------------------------------------
# Resolucion de ventanas y fases
# ---------------------------------------------------------------------------

def _as_date(d: date | datetime) -> date:
    return d.date() if isinstance(d, datetime) else d


def _occurrences(window: dict, year: int) -> list[tuple[date, date]]:
    """Ocurrencias concretas de la ventana alrededor de `year`.

    Recurrente: se resuelve en year-1, year y year+1 (cubre bordes de anio,
    ej. Art Basel en diciembre visto desde enero). Anclado ("year"): solo esa.
    """
    years = [window["year"]] if "year" in window else [year - 1, year, year + 1]
    sm, sd = window["start"]
    em, ed = window["end"]
    out = []
    for y in years:
        start = date(y, sm, sd)
        end = date(y if (em, ed) >= (sm, sd) else y + 1, em, ed)
        out.append((start, end))
    return out


def _phase_for(moment: dict, d: date, lookahead_days: int,
               lookback_days: int) -> tuple[str, int, date, date] | None:
    """(fase, distancia_en_dias, start, end) de la ocurrencia mas cercana, o None."""
    la = max(lookahead_days, moment.get("lead_days", 0))
    lb = max(lookback_days, moment.get("tail_days", 0))
    best = None
    for start, end in _occurrences(moment["window"], d.year):
        if start <= d <= end:
            hit = ("live", 0, start, end)
        elif end < d <= end + timedelta(days=lb):
            hit = ("just-ended", (d - end).days, start, end)
        elif d < start <= d + timedelta(days=la):
            hit = ("upcoming", (start - d).days, start, end)
        else:
            continue
        if best is None or (_PHASE_ORDER[hit[0]], hit[1]) < (_PHASE_ORDER[best[0]], best[1]):
            best = hit
    return best


def active_moments(d: date | datetime, lookahead_days: int = 10,
                   lookback_days: int = 14) -> list[dict]:
    """Momentos activos en la fecha `d`, ordenados live > just-ended > upcoming.

    Cada dict: id, edition (id-anio, ej. "siggraph-2026"), name, phase,
    start/end (ISO), days (0 si live; dias desde fin / hasta inicio),
    brand_activation, keywords.
    """
    d = _as_date(d)
    out = []
    for m in MOMENTS:
        hit = _phase_for(m, d, lookahead_days, lookback_days)
        if hit is None:
            continue
        phase, dist, start, end = hit
        out.append({
            "id": m["id"],
            "edition": f"{m['id']}-{start.year}",
            "name": m["name"],
            "phase": phase,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "days": dist,
            "brand_activation": m["brand_activation"],
            "keywords": list(m["keywords"]),
        })
    out.sort(key=lambda x: (_PHASE_ORDER[x["phase"]], x["days"]))
    return out


# ---------------------------------------------------------------------------
# Matching de candidatos contra momentos activos
# ---------------------------------------------------------------------------

_KW_CACHE: dict[str, re.Pattern] = {}


def _kw_pattern(kw: str) -> re.Pattern:
    """Regex con limites de palabra; espacios del keyword toleran \\s+."""
    pat = _KW_CACHE.get(kw)
    if pat is None:
        pat = re.compile(r"\b" + re.escape(kw).replace(r"\ ", r"\s+") + r"\b",
                         re.IGNORECASE)
        _KW_CACHE[kw] = pat
    return pat


def _candidate_text(cand: Candidate) -> str:
    parts = [cand.headline or "", cand.summary or "", cand.topic or ""]
    parts.extend(cand.all_entities())
    return " ".join(parts)


def _match_active(cand: Candidate, active: list[dict]) -> str | None:
    """Primer momento activo (en orden de prioridad) cuyos keywords matchean."""
    text = _candidate_text(cand)
    for m in active:
        for kw in m["keywords"]:
            if _kw_pattern(kw).search(text):
                return m["edition"]
    return None


def moment_for(cand: Candidate, d: date | datetime) -> str | None:
    """Si el candidato menciona keywords de un momento activo, escribe y
    devuelve su id de edicion (ej. "world-cup-2026"). Si no, None (no pisa
    un cand.moment previo)."""
    active = active_moments(_as_date(d))
    if not active:
        return None
    hit = _match_active(cand, active)
    if hit is not None:
        cand.moment = hit
    return hit


def tag_moments(cands: list[Candidate], d: date | datetime) -> None:
    """Etiqueta cand.moment en toda la lista (momentos activos se calculan 1 vez)."""
    active = active_moments(_as_date(d))
    if not active:
        return
    for cand in cands:
        hit = _match_active(cand, active)
        if hit is not None:
            cand.moment = hit


if __name__ == "__main__":  # inspeccion rapida: python calendar_events.py [YYYY-MM-DD]
    import sys
    d = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    print(f"Momentos activos @ {d.isoformat()}:")
    for m in active_moments(d):
        flag = " [brand-activation]" if m["brand_activation"] else ""
        print(f"  {m['phase']:>10}  {m['edition']:<22} {m['start']}..{m['end']}"
              f"  (days={m['days']}){flag}")
