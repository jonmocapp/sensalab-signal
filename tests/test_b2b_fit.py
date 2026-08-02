"""
Tests de b2b_fit (encaje B2B con el ICP del CEREBRO INMERSIVO).

Corre con pytest o directo sin dependencias:
    python tests/test_b2b_fit.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from b2b_fit import b2b_reasons, b2b_score, score_all  # noqa: E402
from models import Candidate  # noqa: E402

ALTO = 0.6   # umbral: la noticia es municion clara para el productor
BAJO = 0.2   # umbral: la noticia no le sirve al lector B2B


def _cand(headline: str, summary: str = "", **kw) -> Candidate:
    return Candidate(headline=headline, source="test", link="https://example.test/x",
                     summary=summary, **kw)


# --- los 4 casos canonicos del modulo -------------------------------------

def test_nike_flagship_alto():
    s = b2b_score(_cand("Nike unveils immersive flagship with projection mapping"))
    assert s >= ALTO, f"esperaba ALTO (>={ALTO}), dio {s}"


def test_apple_earnings_bajo():
    s = b2b_score(_cand("Apple Q3 earnings beat estimates"))
    assert s <= BAJO, f"esperaba BAJO (<={BAJO}), dio {s}"


def test_iphone_review_bajo():
    s = b2b_score(_cand("New iPhone camera review"))
    assert s <= BAJO, f"esperaba BAJO (<={BAJO}), dio {s}"


def test_giant_spoon_ar_alto():
    s = b2b_score(_cand("Giant Spoon builds AR activation for HBO at Comic-Con"))
    assert s >= ALTO, f"esperaba ALTO (>={ALTO}), dio {s}"


def test_orden_relativo():
    nike = b2b_score(_cand("Nike unveils immersive flagship with projection mapping"))
    spoon = b2b_score(_cand("Giant Spoon builds AR activation for HBO at Comic-Con"))
    apple = b2b_score(_cand("Apple Q3 earnings beat estimates"))
    iphone = b2b_score(_cand("New iPhone camera review"))
    assert nike > apple and nike > iphone
    assert spoon > apple and spoon > iphone


# --- contrato y comportamiento ---------------------------------------------

def test_score_all_escribe_key_b2b():
    cands = [
        _cand("Netflix pop-up takes over Coachella with LED walls"),
        _cand("Senate passes new tariff bill"),
        _cand("Bitcoin hits record high as crypto rallies"),
    ]
    score_all(cands)
    for c in cands:
        assert "b2b" in c.scores
        assert 0.0 <= c.scores["b2b"] <= 1.0


def test_entities_suman_sin_keywords():
    """entities pobladas por el lexicon suman senal aunque el texto no tenga keywords."""
    neutro = _cand("Weekly industry roundup")
    con_entities = _cand("Weekly industry roundup")
    con_entities.entities["brands"].append("Netflix")
    con_entities.entities["tech"].append("projection mapping")
    assert b2b_score(neutro) == 0.0
    assert b2b_score(con_entities) > b2b_score(neutro)
    assert b2b_score(con_entities) >= 0.25


def test_negativos_puros_quedan_en_cero():
    assert b2b_score(_cand("Senate passes new tariff bill")) <= BAJO
    assert b2b_score(_cand("Bitcoin hits record high as crypto rallies")) <= BAJO
    assert b2b_score(_cand("Agency holding company reports quarterly revenue miss")) <= BAJO


def test_corporativo_gated_por_senal_experiencial():
    """La misma palabra corporativa no castiga si hay angulo experiencial."""
    puro = b2b_score(_cand("Media giant announces merger and restructuring"))
    con_angulo = b2b_score(_cand(
        "After the merger, agency unveils immersive activation with projection mapping"))
    assert puro <= BAJO
    assert con_angulo >= ALTO


def test_reasons_explican_el_score():
    razones = b2b_reasons(_cand("Nike unveils immersive flagship with projection mapping"))
    assert razones and all(isinstance(r, str) for r in razones)
    assert any(r.startswith("+") for r in razones)
    assert b2b_reasons(_cand("Weekly industry roundup")) == []


# --- runner sin pytest ------------------------------------------------------

if __name__ == "__main__":
    fallos = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                fallos += 1
                print(f"FAIL  {name}: {e}")

    print("\nScores de los 4 casos canonicos:")
    for h in ("Nike unveils immersive flagship with projection mapping",
              "Apple Q3 earnings beat estimates",
              "New iPhone camera review",
              "Giant Spoon builds AR activation for HBO at Comic-Con"):
        c = _cand(h)
        print(f"  {b2b_score(c):.2f}  {h}")
        for r in b2b_reasons(c):
            print(f"        {r}")

    sys.exit(1 if fallos else 0)
