"""
CEREBRO INMERSIVO — orquestador v2 (el "editor de maquina", AI sin AI).

Conecta todos los modulos: ingesta (RSS v1 + queries) -> tag entidades (lexicon)
-> momentos (calendar) -> scoring (b2b, momentum, scoring) -> composer (formato + edicion).
Devuelve un EditionPlan que el paso de redaccion (writer/LLM) convierte en prosa.

Correr directo:  python brain.py            (dry: arma el plan de esta semana, no llama LLM)
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone

from models import Candidate
import sources
import ingest_news
import lexicon
import calendar_events
import b2b_fit
import momentum
import scoring
import composer

# Palabras que marcan controversia/craft-fail -> alimentan talkability (formato Teardown)
_TALK_RX = re.compile(
    r"\b(slammed|criticized|criticised|backlash|flop|flopped|ugly|disaster|fail(ed|s)?|"
    r"roasted|mocked|bombed|controvers\w+|panned|blasted|ripped|awkward|cringe|"
    r"criticad\w+|polemic\w+|fracas\w+|desastr\w+)\b", re.IGNORECASE)


def _relevance(c: Candidate) -> float:
    """Fuerza experiencial lexica reusando los patrones del bot v1 (STRONG/INCLUDE)."""
    blob = f" {c.headline} {c.summary} "
    strong = sources._count(sources._STRONG_RX, blob)
    inc = sources._count(sources._INCLUDE_RX, blob)
    return min(1.0, strong * 0.5 + inc * 0.15)


def _talkability(c: Candidate) -> float:
    return 0.75 if _TALK_RX.search(f"{c.headline} {c.summary}") else 0.0


def gather_candidates(lookback_days: int = 10, verbose: bool = True) -> list[Candidate]:
    """RSS fijo (v1) + queries de Google News, convertidos a Candidate y dedup."""
    cands: list[Candidate] = []
    if verbose:
        print("[ingesta] RSS fijo (v1)...")
    for st in sources.fetch_all(lookback_days=lookback_days, verbose=verbose):
        cands.append(Candidate.from_story(st))
    if verbose:
        print("[ingesta] queries (Google News)...")
    cands += ingest_news.gather(lookback_days=lookback_days, verbose=verbose)

    seen, uniq = set(), []
    for c in cands:
        k = c.key()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(c)
    if verbose:
        print(f"[ingesta] {len(uniq)} candidatas unicas")
    return uniq


def enrich_and_score(cands: list[Candidate], date: datetime, state: dict) -> None:
    lexicon.tag_all(cands)                       # entities + topic
    calendar_events.tag_moments(cands, date)     # cand.moment
    b2b_fit.score_all(cands)                      # scores["b2b"]
    momentum.score_momentum(cands)               # scores["momentum"]
    used_topics = {str(t).lower() for t in state.get("used_topics", [])}
    for c in cands:
        c.scores["relevance"] = _relevance(c)
        c.scores["timeliness"] = scoring.timeliness(c, date)
        c.scores["authority"] = scoring.authority(c)
        c.scores["novelty"] = scoring.novelty(c, used_topics)
        c.scores["geo"] = 1.0 if c.geo else 0.0
        c.scores["talkability"] = _talkability(c)
        c.scores.setdefault("angle", 0.0)
        scoring.combine(c)


def build_edition_plan(date: datetime | None = None, state: dict | None = None,
                       lookback_days: int = 10, verbose: bool = True):
    """Pipeline completo -> (EditionPlan, candidatas_scoreadas)."""
    date = date or datetime.now(timezone.utc)
    state = dict(state or {})

    cands = gather_candidates(lookback_days=lookback_days, verbose=verbose)
    if not cands:
        return None, []

    enrich_and_score(cands, date, state)

    # Pasa el estado de momentos limpio al composer (id de edicion -> fase)
    try:
        moments = {m["edition"]: m["phase"] for m in calendar_events.active_moments(date)
                   if isinstance(m, dict) and m.get("edition")}
        state.setdefault("moments", moments)
    except Exception:
        pass

    plan = composer.compose(cands, date, state)
    return plan, cands


def _print_plan(plan, cands, date):
    fmt, fit, reason = composer.choose_format(cands, date, {})
    print(f"\n=== EDICION DE LA SEMANA ({date.date()}) ===")
    print(f"Formato: {getattr(plan, 'format_id', '?')}  (fit {fit:.2f})")
    print(f"Razon:   {reason}")
    print(f"Theme:   {getattr(plan, 'theme', None)}")
    print(f"Historias ({len(plan.stories)}):")
    for i, s in enumerate(plan.stories, 1):
        geo = " [geo]" if s.geo else ""
        print(f"  {i}. [{s.angle}]{geo} b2b={s.scores.get('b2b',0):.2f} "
              f"tot={s.total:.2f} :: {s.headline[:64]}")
        print(f"       {s.source} | topic={s.topic} | moment={s.moment}")


if __name__ == "__main__":
    date = datetime.now(timezone.utc)
    plan, cands = build_edition_plan(date=date, verbose=True)
    if plan is None:
        print("Sin candidatas esta semana.")
        sys.exit(1)
    _print_plan(plan, cands, date)
