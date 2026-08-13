# -*- coding: utf-8 -*-
"""
THE SIGNAL — PIPELINE (app autónoma).

El loop completo, auto-alimentado:

  1. refresca el POOL de noticias reales        -> daily_signals.run()  (RSS + Google News, sin LLM)
  2. elige las mejores nuevas del pool           -> select_candidates()
  3. baja la fuente (hechos reales + og:image)   -> fetch_source.fetch()
  4. redacta la nota con voz SensaLab            -> article_writer.write_article()  (Claude API)
  5. la mete a articles_live.json (+ imagen)     -> set_articles.main()
  6. reconstruye Latest stories + el sitio       -> build_articles / build_blog_b / build_seo
  7. recuerda qué ya publicó (no repite)         -> published.json

Corre cada día en la nube (GitHub Action) o a mano. 'Latest stories' crece solo con notas reales.

Uso:
  python pipeline.py                 # corrida real (necesita ANTHROPIC_API_KEY)
  python pipeline.py --mock          # sin LLM: plantilla, para probar la plomería local
  python pipeline.py --dry           # elige y redacta pero NO escribe ni reconstruye
  python pipeline.py --limit 2       # cuántas notas nuevas por corrida
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

import config
import daily_signals
import fetch_source
from models import normalize_url

BASE = pathlib.Path(__file__).resolve().parent
POOL = BASE / "signals.json"
LIVE_JSON = BASE / "articles_live.json"
PUBLISHED = BASE / "published.json"
EDITION = 21

MAX_NEW = int(config.env("PIPELINE_MAX_NEW", "3"))     # notas nuevas por corrida
MODEL = config.env("PIPELINE_MODEL", "claude-opus-4-8")  # calidad alta (Opus 4.8). Máxima: claude-fable-5
MODE = config.env("PIPELINE_MODE", "auto").lower()      # auto | review

TOKENS_BY_CAT = {
    "Experiential": "experiential", "Spatial & AR": "spatial", "CGI & VFX": "cgi",
    "AI": "ai", "Gaming": "gaming", "Interactive": "interactive", "Concert visuals": "concerts",
}
ART_FIELDS = ("headline", "dek", "focus_keyword", "read_minutes",
              "meta_description", "why", "takeaway", "body")


def _log(m: str) -> None:
    print(m, flush=True)


def slugify(h: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (h or "").lower()).strip("-")
    return "-".join(s.split("-")[:7]) or "story"


def _unique_slug(slug: str, taken: set[str]) -> str:
    s, i = slug, 2
    while s in taken:
        s = f"{slug}-{i}"; i += 1
    return s


def load_published() -> set[str]:
    try:
        return set(json.load(open(PUBLISHED, encoding="utf-8")).get("keys", []))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return set()


def save_published(keys: set[str]) -> None:
    json.dump({"keys": sorted(keys)}, open(PUBLISHED, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def load_live() -> list[dict]:
    try:
        return json.load(open(LIVE_JSON, encoding="utf-8")).get("articles", [])
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


# Patrones de bajo valor para un DEEP-DIVE: perfiles de personas, nombramientos, PR de agenda.
# (No los queremos como artículo completo; sí pueden seguir en el feed de Signals.)
_LOW_VALUE = re.compile(
    r"\b(fresh faces|up[- ]and[- ]coming|people on the move|on the move|appoints?|"
    r"names? (a|an|new|its)\b|promoted|new hire|hires|joins as|q&a|webinar|podcast|"
    r"obituary|milestone|anniversary|now hiring|call for)\b", re.IGNORECASE)


def select_candidates(pool: list[dict], published: set[str], n: int) -> list[dict]:
    """Nuevas del pool, fuente ASCII (medios en inglés), sin PR de bajo valor, curadas antes
    que query, top score, con un 'take' real (señal de que hay historia)."""
    def ascii_src(s):
        return all(ord(c) < 128 for c in (s.get("source") or ""))
    rank = {"core": 0, "rotate": 1, "query": 2}
    cands = [s for s in pool
             if s.get("key") and s["key"] not in published
             and s.get("link") and s.get("headline") and ascii_src(s)
             and (s.get("take") or "").strip()
             and not _LOW_VALUE.search(s.get("headline", ""))]
    cands.sort(key=lambda s: (rank.get(s.get("tier", "query"), 2), -s.get("score", 0)))
    return cands[:n]


def _mock_article(c: dict, facts: str) -> dict:
    """Plantilla sin LLM para probar la plomería local (no es prosa de marca)."""
    hl = c["headline"]
    return {
        "headline": hl, "dek": f"The news is not just this. It is the signal underneath. ({c.get('cat','')})",
        "focus_keyword": c.get("token", "experiential"), "read_minutes": 3,
        "meta_description": (facts[:150] or hl)[:150],
        "why": "It signals where budget and attention are moving for experiential producers.",
        "takeaway": "Track this and build for the format it points to.",
        "body": [{"type": "para", "text": facts[:600] or hl},
                 {"type": "subhead", "text": "Why it belongs in the toolkit"},
                 {"type": "para", "text": "This is the layer SensaLab builds, white-label, under your name."}],
    }


def _build_site() -> None:
    import set_articles
    set_articles.main()
    for script in ("build_articles.py", "build_blog_b.py", "build_seo.py", "polish_blog.py"):
        r = subprocess.run([sys.executable, script], cwd=str(BASE),
                           capture_output=True, text=True)
        tail = (r.stdout or r.stderr or "").strip().splitlines()[-1:] or [""]
        _log(f"  {script}: {tail[0]}")
        if r.returncode != 0:
            _log(f"  [!] {script} rc={r.returncode}\n{(r.stderr or '')[-400:]}")


def run(mock: bool = False, dry: bool = False, limit: int | None = None) -> int:
    n = limit or MAX_NEW
    _log(f"\n=== PIPELINE :: nuevas={n} :: modo={'MOCK' if mock else MODE} :: modelo={MODEL} ===")

    if not mock and MODE == "auto" and not config.ANTHROPIC_API_KEY:
        _log("  [config] Falta ANTHROPIC_API_KEY. Usa --mock para probar la plomería, o setea la key.")
        return 2

    # 1) refrescar pool
    _log("[1] refrescando pool de noticias...")
    try:
        daily_signals.run(verbose=False)
    except Exception as e:
        _log(f"  [aviso] daily_signals falló ({e}); uso el pool existente.")
    try:
        pool = json.load(open(POOL, encoding="utf-8")).get("signals", [])
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        _log("  Sin pool. Fin."); return 1

    live = load_live()
    published = load_published()
    # Dedup también por fuente ya publicada (curada o auto): nunca re-cubrir la misma nota.
    published |= {k for k in (normalize_url(a.get("source_url", "")) for a in live) if k}
    picks = select_candidates(pool, published, n * 3)   # sobre-selecciono: algunos fallan fetch/write
    _log(f"[2] {len(picks)} candidatas nuevas evaluables (objetivo {n}).")

    taken = {a["slug"] for a in live}
    written, attempted = 0, set()

    for c in picks:
        if written >= n:
            break
        attempted.add(c["key"])
        src = ({"text": c.get("take") or c["headline"], "image_url": None, "ok": True}
               if mock else fetch_source.fetch(c["link"]))
        facts = (src or {}).get("text") or ""
        if not mock and (not facts or len(facts) < 200):
            _log(f"  skip (sin cuerpo): {c['headline'][:56]}")
            continue
        if mock:
            art = _mock_article(c, facts)
        else:
            import article_writer
            art = article_writer.write_article(c["headline"], c.get("source", ""), c["link"],
                                               facts, model=MODEL, api_key=config.ANTHROPIC_API_KEY)
        if not art:
            continue
        slug = _unique_slug(slugify(art["headline"]), taken)
        taken.add(slug)
        cat = c.get("cat") or "Experiential"
        rec = {k: art[k] for k in ART_FIELDS}
        rec.update(slug=slug, cat=cat, tokens=TOKENS_BY_CAT.get(cat, "experiential"),
                   edition=EDITION, source_name=c.get("source", ""), source_url=c["link"],
                   date=(c.get("published", "") or "")[:10], image_url=(src or {}).get("image_url"))
        live.append(rec)
        written += 1
        _log(f"  WROTE: {slug}  [{cat}]")

    if dry:
        _log(f"[dry] {written} nota(s) nueva(s); no se escribe ni reconstruye.")
        return 0

    if written:
        json.dump({"articles": live}, open(LIVE_JSON, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        _log(f"[3] {written} nota(s) añadida(s) -> articles_live.json ({len(live)} total). Reconstruyendo...")
        _build_site()
    else:
        _log("[3] 0 notas nuevas escritas esta corrida.")

    save_published(published | attempted)
    _log(f"[ok] pipeline terminado. Latest stories crece con {written} nota(s) real(es).")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true", help="sin LLM (plantilla) para probar la plomería")
    ap.add_argument("--dry", action="store_true", help="elige y redacta pero no escribe ni reconstruye")
    ap.add_argument("--limit", type=int, default=None, help="notas nuevas por corrida")
    args = ap.parse_args()
    raise SystemExit(run(mock=args.mock, dry=args.dry, limit=args.limit))
