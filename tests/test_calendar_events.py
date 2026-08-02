"""
Tests de calendar_events.py (CEREBRO INMERSIVO).
Fecha fija: 2026-07-23 -> Mundial "just-ended", Comic-Con "live", SIGGRAPH "live" (19-23 jul).
Corre con: python tests/test_calendar_events.py   (tambien compatible con pytest)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import date

import calendar_events as ce
from models import Candidate

TODAY = date(2026, 7, 23)


def _active_by_id(d=TODAY, **kw):
    return {m["id"]: m for m in ce.active_moments(d, **kw)}


def test_world_cup_just_ended():
    act = _active_by_id()
    assert "world-cup" in act, "el Mundial debe estar activo el 2026-07-23"
    assert act["world-cup"]["phase"] == "just-ended"
    assert act["world-cup"]["edition"] == "world-cup-2026"
    assert act["world-cup"]["days"] == 4  # termino el 19-jul


def test_comic_con_live():
    act = _active_by_id()
    assert "comic-con" in act
    assert act["comic-con"]["phase"] == "live"


def test_siggraph_live():
    # SIGGRAPH 2026 = 19-23 jul (LA). El 23-jul es su ultimo dia -> "live".
    act = _active_by_id()
    assert "siggraph" in act, "SIGGRAPH (19-23 jul) debe estar activo el 2026-07-23"
    assert act["siggraph"]["phase"] == "live"


def test_out_of_season_not_active():
    act = _active_by_id()
    for mid in ("ces", "sundance", "super-bowl", "sxsw", "gdc", "coachella",
                "nab", "milan-design-week", "wwdc", "cannes-lions",
                "art-basel-miami"):
        assert mid not in act, f"{mid} no deberia estar activo el 2026-07-23"


def test_sorted_live_first():
    phases = [m["phase"] for m in ce.active_moments(TODAY)]
    order = [ce._PHASE_ORDER[p] for p in phases]
    assert order == sorted(order)
    assert phases[0] == "live"


def test_moment_for_world_cup():
    c = Candidate(headline="The best brand activations from the World Cup final weekend",
                  source="test", link="https://example.com/wc")
    got = ce.moment_for(c, TODAY)
    assert got == "world-cup-2026"
    assert c.moment == "world-cup-2026"


def test_moment_for_spanish_mundial():
    c = Candidate(headline="Lo que dejo el Mundial: fan fests inmersivos en LA",
                  source="test", link="https://example.com/mundial")
    assert ce.moment_for(c, TODAY) == "world-cup-2026"


def test_moment_for_inactive_keyword_is_none():
    c = Candidate(headline="CES gadgets roundup for producers",
                  source="test", link="https://example.com/ces")
    assert ce.moment_for(c, TODAY) is None
    assert c.moment is None  # no se pisa ni se inventa


def test_moment_for_no_match_keeps_existing():
    c = Candidate(headline="A projection mapping show in downtown LA",
                  source="test", link="https://example.com/pm")
    c.moment = "previo"
    assert ce.moment_for(c, TODAY) is None
    assert c.moment == "previo"


def test_tag_moments():
    a = Candidate(headline="SIGGRAPH 2026 preview: real-time graphics on stage",
                  source="test", link="https://example.com/sig")
    b = Candidate(headline="Hall H lines wrap the block as SDCC opens",
                  source="test", link="https://example.com/sdcc")
    c = Candidate(headline="teamLab opens a new permanent exhibit",
                  source="test", link="https://example.com/tl")
    ce.tag_moments([a, b, c], TODAY)
    assert a.moment == "siggraph-2026"
    assert b.moment == "comic-con-2026"
    assert c.moment is None


def test_world_cup_year_locked():
    # El Mundial 2026 esta anclado: en 2027 no existe.
    assert "world-cup" not in _active_by_id(date(2027, 7, 23))


def test_recurring_next_year():
    # Comic-Con si es recurrente: en 2027 (misma fecha aprox) vuelve a salir.
    assert "comic-con" in _active_by_id(date(2027, 7, 23))


def test_year_wrap_art_basel():
    # Visto desde enero con lookback amplio, Art Basel Miami (dic del anio
    # ANTERIOR) sale como just-ended: la ventana recurrente cruza el borde de anio.
    act = _active_by_id(date(2027, 1, 5), lookback_days=45)
    assert act["art-basel-miami"]["phase"] == "just-ended"
    assert act["art-basel-miami"]["edition"] == "art-basel-miami-2026"


def test_word_boundaries():
    # "nab" suelto (verbo ingles) no debe matchear NAB Show; keywords son frases.
    c = Candidate(headline="Brands nab attention with comic relief",
                  source="test", link="https://example.com/x")
    assert ce.moment_for(c, date(2026, 4, 20)) is None


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS {name}")
            except AssertionError as e:
                failed += 1
                print(f"  FAIL {name}: {e}")
    print(f"\n{'VERDE: todos los tests pasan' if not failed else f'{failed} test(s) fallaron'}")
    sys.exit(1 if failed else 0)
