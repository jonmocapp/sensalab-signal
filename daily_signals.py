# -*- coding: utf-8 -*-
"""
Carril 1 del blog: SEÑALES DIARIAS (gratis, determinista, sin LLM).

Corre el CEREBRO (brain.gather_candidates + enrich_and_score), deduplica contra lo ya
visto, clasifica cada noticia en una categoría del blog, aplica el guardarraíl non-compete,
y mantiene una ventana rodante en signals.json que el build del blog renderiza.

NO llama a ningún LLM. La "bajada" de cada tarjeta es el resumen real de la fuente
(recortado). Cada tarjeta linkea a la fuente original (atribución correcta). Las portadas
son las abstractas de marca (sin IP de terceros).

Uso:
  python daily_signals.py                # corrida real: ingesta + actualiza signals.json
  python daily_signals.py --dry-run      # ingesta y muestra el top, NO escribe signals.json
  python daily_signals.py --limit 24     # cuántas señales frescas máximo por corrida
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

import brain
from models import normalize_url

# La consola de Windows (cp1252) revienta al imprimir ·/°/… ; forzamos UTF-8 en stdout.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# El guardarraíl non-compete ya existe en writer.py; lo reusamos (única fuente de verdad).
try:
    from writer import FORBIDDEN
except Exception:  # writer importa anthropic; si no está, caemos a la lista mínima
    FORBIDDEN = ["cinetica", "cinética"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNALS_JSON = os.path.join(BASE_DIR, "signals.json")

# --- Parámetros de la ventana rodante ---
WINDOW_DAYS = 30          # cuánto tiempo vive una señal en el feed
MAX_ITEMS = 60            # tope total de señales que guarda el feed
DEFAULT_FRESH_LIMIT = 24  # cuántas señales nuevas máximo por corrida
LOOKBACK_DAYS = 7         # ventana de ingesta (más material de fuentes CORE con resumen real)
MIN_SCORE = 0.30          # piso de calidad: por debajo de esto no entra al feed


# ---------------------------------------------------------------------------
# Clasificación en categorías del blog (mismas que los filtros del index).
# Orden = prioridad; el primer patrón que dispara define la categoría.
# ---------------------------------------------------------------------------
# (label visible, token de filtro, patrón)
_CATEGORY_RULES = [
    ("Gaming", "gaming",
     r"\b(gamescom|fortnite|roblox|epic games|esports?|video game|game studio|"
     r"playstation|xbox|nintendo|steam|twitch)\b"),
    ("AI", "ai",
     r"\b(a\.?i\.?|artificial intelligence|generative ai|gen ai|genai|machine learning|"
     r"nvidia|openai|anthropic|midjourney|stable diffusion|neural)\b"),
    ("Spatial & AR", "spatial",
     r"\b(ar|vr|xr|mr|augmented reality|virtual reality|mixed reality|extended reality|"
     r"spatial computing|vision pro|smart ?glasses|specs|headset|wearable)\b"),
    ("CGI & VFX", "cgi",
     r"\b(virtual production|led volume|led wall|led floor|vfx|real-?time render\w*|"
     r"metahuman|gaussian splatting|motion capture|mocap|digital twin|cgi)\b"),
    ("Concert visuals", "concerts",
     r"\b(the sphere|sphere|cosm|concert|residency|tour|live venue|stage show|arena|stadium)\b"),
    ("Interactive", "interactive",
     r"\b(teamlab|meow wolf|interactive installation|immersive art|generative art|"
     r"museum|playable|touchdesigner|projection mapping|digital art)\b"),
    # experiential = fallback (activaciones, pop-ups, brand experiences, eventos)
]

_CAT_PATTERNS = [(lab, tok, re.compile(rx, re.IGNORECASE)) for lab, tok, rx in _CATEGORY_RULES]


def classify(headline: str, summary: str, entities: dict) -> tuple[str, str]:
    blob = f" {headline} {summary} "
    # Un empujón desde las entidades ya etiquetadas por el lexicon
    tech = " ".join(entities.get("tech", []))
    venues = " ".join(entities.get("venues", []))
    blob = f"{blob} {tech} {venues} "
    for lab, tok, rx in _CAT_PATTERNS:
        if rx.search(blob):
            return lab, tok
    return "Experiential", "experiential"


# ---------------------------------------------------------------------------
# Utilidades de texto
# ---------------------------------------------------------------------------
def _one_line(summary: str, limit: int = 160) -> str:
    """Primera frase del resumen real (recortada word-aware). Sin LLM."""
    s = re.sub(r"\s+", " ", (summary or "")).strip()
    if not s:
        return ""
    # corta en la primera frase si es razonablemente larga
    m = re.search(r"(.+?[.!?])(\s|$)", s)
    first = m.group(1).strip() if m and len(m.group(1)) >= 40 else s
    if len(first) <= limit:
        return first
    cut = first[:limit]
    cut = cut[:cut.rfind(" ")].rstrip(" ,.;:")
    return cut + "…"


def _clean_headline(h: str) -> str:
    return re.sub(r"\s+", " ", (h or "")).strip()


# Escrituras no latinas (CJK, kana, hangul, cirílico): el blog es inglés/LA, se filtran.
_NONLATIN = re.compile(r"[Ѐ-ӿ぀-ヿ㐀-鿿가-힯]")


def _latin_ok(t: str) -> bool:
    return not _NONLATIN.search(t or "")


def _strip_publisher(h: str, source: str) -> str:
    """Quita el sufijo de fuente que Google News pega al titular ('Title - Publisher',
    'Title Publisher'). Deja el titular limpio."""
    h = (h or "").strip()
    s = (source or "").strip()
    if s and h.lower().endswith(s.lower()):
        h = h[: -len(s)].rstrip(" -–—·|").strip()
    if " - " in h:
        head, tail = h.rsplit(" - ", 1)
        if head and len(tail) <= 45:
            h = head.strip()
    return h


def _take_is_weak(take: str, headline: str) -> bool:
    """El 'take' no aporta si está vacío, es muy corto, o es un subconjunto del titular
    (no añade nada). Un take más rico que contiene al titular SÍ vale."""
    if not take or len(take) < 24:
        return True
    t = re.sub(r"\W+", " ", take.lower()).strip()
    hh = re.sub(r"\W+", " ", (headline or "").lower()).strip()
    return t == hh or t in hh


def _forbidden_hit(text: str) -> bool:
    low = text.lower()
    return any(term.lower() in low for term in FORBIDDEN)


def _parse_dt(s: str | None):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Persistencia de la ventana rodante
# ---------------------------------------------------------------------------
def load_signals() -> list[dict]:
    try:
        with open(SIGNALS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("signals", []) if isinstance(data, dict) else list(data)
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, OSError) as e:
        print(f"  [ALERTA] signals.json ilegible ({e}); se arranca de cero esta vez.")
        return []


def save_signals(signals: list[dict], now: datetime) -> None:
    payload = {"generated": now.isoformat(), "count": len(signals), "signals": signals}
    tmp = SIGNALS_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, SIGNALS_JSON)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def build_fresh(cands, existing_keys: set[str], now: datetime, limit: int,
                verbose: bool = True) -> list[dict]:
    """Convierte candidatas del cerebro en señales nuevas (dedup + guardarraíl + piso)."""
    fresh: list[dict] = []
    seen = set(existing_keys)
    dropped_guard = 0
    for c in sorted(cands, key=lambda x: x.total, reverse=True):
        if len(fresh) >= limit:
            break
        key = normalize_url(c.link) or c.headline.strip().lower()
        if not key or key in seen:
            continue
        if not c.link or not c.headline:
            continue
        if c.total < MIN_SCORE:
            continue
        headline = _strip_publisher(_clean_headline(c.headline), c.source or "")
        if not headline or not _latin_ok(headline) or not _latin_ok(c.source or ""):
            continue   # descarta titulares/fuentes no latinas (off-brand para un blog en inglés)
        blob = f"{headline} {c.summary}"
        if _forbidden_hit(blob):
            dropped_guard += 1
            continue
        seen.add(key)
        lab, tok = classify(headline, c.summary, c.entities)
        take = _one_line(c.summary)
        if _take_is_weak(take, headline):
            take = ""
        pub = c.published or now
        fresh.append({
            "key": key,
            "headline": headline,
            "source": c.source or "",
            "link": c.link,
            "take": take,
            "cat": lab,
            "token": tok,
            "tier": getattr(c, "tier", "query"),
            "geo": bool(c.geo),
            "score": round(float(c.total), 3),
            "published": pub.isoformat() if hasattr(pub, "isoformat") else str(pub),
            "added": now.isoformat(),
        })
    if verbose and dropped_guard:
        print(f"  [guardarraíl] {dropped_guard} noticia(s) descartada(s) por término prohibido.")
    return fresh


def prune_and_cap(signals: list[dict], now: datetime) -> list[dict]:
    """Quita señales fuera de la ventana y ordena por fecha (recientes primero)."""
    cutoff = now - timedelta(days=WINDOW_DAYS)

    def when(s):
        return _parse_dt(s.get("published")) or _parse_dt(s.get("added")) or now

    live = [s for s in signals if when(s) >= cutoff]
    live.sort(key=lambda s: (when(s), s.get("score", 0)), reverse=True)
    return live[:MAX_ITEMS]


def run(dry_run: bool = False, limit: int = DEFAULT_FRESH_LIMIT, verbose: bool = True) -> int:
    now = datetime.now(timezone.utc)
    if verbose:
        print(f"\n=== SEÑALES DIARIAS :: {now.date().isoformat()} :: "
              f"{'DRY-RUN' if dry_run else 'REAL'} ===")

    # 1) Ingesta + scoring (reusa el cerebro; no LLM)
    cands = brain.gather_candidates(lookback_days=LOOKBACK_DAYS, verbose=verbose)
    if not cands:
        print("  Sin candidatas hoy. signals.json queda igual.")
        return 1
    try:
        brain.enrich_and_score(cands, now, {})
    except Exception as e:
        # El feed diario NO puede morir por un módulo de scoring: degradamos con relevancia.
        print(f"  [aviso] enriquecido parcial ({e}); se usa solo relevancia léxica.")
        for c in cands:
            c.scores.setdefault("total", brain._relevance(c))

    # 2) Estado previo + señales nuevas
    existing = load_signals()
    existing_keys = {s.get("key") for s in existing if s.get("key")}
    fresh = build_fresh(cands, existing_keys, now, limit, verbose=verbose)
    if verbose:
        print(f"  {len(fresh)} señal(es) nueva(s) sobre {len(existing)} en el feed.")

    # 3) Merge + poda + tope
    merged = prune_and_cap(fresh + existing, now)

    if dry_run:
        print("\n  --- TOP 12 (dry-run, no se escribe) ---")
        for s in merged[:12]:
            geo = " [geo]" if s["geo"] else ""
            print(f"  [{s['cat']:<16}]{geo} {s['headline'][:70]}")
            print(f"      {s['source']}  ·  {s['link'][:80]}")
        return 0

    save_signals(merged, now)
    by_cat: dict[str, int] = {}
    for s in merged:
        by_cat[s["cat"]] = by_cat.get(s["cat"], 0) + 1
    print(f"\n  signals.json: {len(merged)} señales en el feed  |  "
          + ", ".join(f"{k}:{v}" for k, v in sorted(by_cat.items())))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="ingesta y muestra, no escribe")
    ap.add_argument("--limit", type=int, default=DEFAULT_FRESH_LIMIT,
                    help="máximo de señales nuevas por corrida")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    sys.exit(run(dry_run=args.dry_run, limit=args.limit, verbose=not args.quiet))
