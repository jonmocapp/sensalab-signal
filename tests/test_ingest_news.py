"""
Tests de ingest_news.py (Cerebro Inmersivo).

REQUIERE RED: los tests marcados con @network hacen fetch REAL a Google News RSS.
Para saltarlos (CI sin red, avion): SKIP_NETWORK_TESTS=1

Se puede correr con pytest o standalone (sin dependencias extra):
    python tests/test_ingest_news.py
    python -m pytest tests/test_ingest_news.py -v
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# El proyecto no es un paquete instalable: asegura el root en sys.path.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import pytest
except ImportError:      # standalone, sin pytest instalado
    pytest = None

from models import Candidate
import ingest_news

_NETWORK_OK = os.environ.get("SKIP_NETWORK_TESTS", "") not in ("1", "true", "yes")


def network(fn):
    """Marca un test como 'requiere red' (marker pytest + guard standalone)."""
    fn._requires_network = True
    if pytest is not None:
        fn = pytest.mark.network(fn)
    return fn


def _skip_if_offline() -> bool:
    """True si hay que saltar el test. Con pytest usa pytest.skip."""
    if _NETWORK_OK:
        return False
    if pytest is not None:
        pytest.skip("SKIP_NETWORK_TESTS activo (test requiere red)")
    return True


# ---------------------------------------------------------------------------
# Offline (sin red)
# ---------------------------------------------------------------------------
def test_build_search_url():
    url = ingest_news.build_search_url("projection mapping", lookback_days=7)
    assert url.startswith("https://news.google.com/rss/search?q=")
    assert "hl=en-US" in url and "gl=US" in url and "ceid=US:en" in url
    # query urlencoded + operador de recencia
    assert "projection+mapping" in url
    assert "when%3A7d" in url
    # sin lookback no agrega when:
    assert "when" not in ingest_news.build_search_url("x", lookback_days=0)
    # no duplica un when: que ya viene en el query
    assert ingest_news.build_search_url("x when:3d", 7).count("when") == 1


def test_queries_for_entities():
    qs = ingest_news.queries_for_entities(["SIGGRAPH", "World Cup activations",
                                           "", "  ", "SIGGRAPH"])
    assert len(qs) == 2  # vacios fuera, duplicados fuera
    # multi-palabra va entre comillas; una palabra no lo necesita
    assert qs[0].startswith("SIGGRAPH ")
    assert qs[1].startswith('"World Cup activations" ')
    # todas ancladas al contexto experiencial
    assert all("immersive OR experiential" in q for q in qs)
    assert ingest_news.queries_for_entities([]) == []


def test_standing_queries_registry():
    assert len(ingest_news.STANDING_QUERIES) >= 8
    assert all(isinstance(q, str) and q.strip() for q in ingest_news.STANDING_QUERIES)


def test_search_news_empty_query():
    assert ingest_news.search_news("") == []
    assert ingest_news.search_news("   ") == []


# ---------------------------------------------------------------------------
# Con red (fetch REAL a Google News)
# ---------------------------------------------------------------------------
@network
def test_search_news_real_fetch():
    """1 fetch real: la query debe regresar Candidates con campos poblados."""
    if _skip_if_offline():
        return
    cands = ingest_news.search_news("projection mapping", lookback_days=14, limit=10)

    assert isinstance(cands, list)
    assert len(cands) > 0, "Google News no regreso nada para 'projection mapping'"
    assert len(cands) <= 10

    keys = set()
    for c in cands:
        assert isinstance(c, Candidate)
        assert c.tier == "query"
        assert c.headline.strip(), "headline vacio"
        assert c.link.startswith("http"), f"link invalido: {c.link!r}"
        assert c.source.strip(), "source vacio"
        assert isinstance(c.summary, str)
        keys.add(c.key())
    assert len(keys) == len(cands), "dedup por Candidate.key() fallo dentro de la query"

    # La mayoria de las notas traen fecha; exigimos al menos una, tz-aware y dentro
    # de la ventana (con margen por zonas horarias).
    dated = [c for c in cands if c.published is not None]
    assert dated, "ninguna candidata trajo fecha de publicacion"
    floor = datetime.now(timezone.utc) - timedelta(days=15)
    for c in dated:
        assert c.published.tzinfo is not None, "published debe ser tz-aware (UTC)"
        assert c.published >= floor, f"fuera de ventana: {c.published} ({c.headline})"


@network
def test_gather_real_dedup_and_order():
    """gather() con 2 queries que se traslapan: dedup global + orden por fecha."""
    if _skip_if_offline():
        return
    cands = ingest_news.gather(queries=['"projection mapping"',
                                        '"projection mapping" festival'],
                               lookback_days=14, per_query=8, verbose=False)
    assert isinstance(cands, list)
    assert len(cands) > 0
    assert all(isinstance(c, Candidate) and c.tier == "query" for c in cands)

    keys = [c.key() for c in cands]
    assert len(keys) == len(set(keys)), "dedup global por Candidate.key() fallo"

    # Orden: fechas descendentes; las sin fecha al final.
    dated = [c.published for c in cands if c.published is not None]
    assert dated == sorted(dated, reverse=True), "no viene ordenado por fecha desc"
    tail_undated = [c.published is None for c in cands]
    if any(tail_undated):
        first_none = tail_undated.index(True)
        assert all(tail_undated[first_none:]), "candidatas sin fecha deben ir al final"


@network
def test_resolve_link_tolerant():
    """resolve_link nunca truena y regresa un string utilizable."""
    if _skip_if_offline():
        return
    # URL que no existe -> regresa la original sin excepcion
    bad = "https://este-dominio-no-existe-sensalab-test.invalid/x"
    assert ingest_news.resolve_link(bad, timeout=3) == bad
    assert ingest_news.resolve_link("") == ""

    # Con un link real de Google News: best-effort (puede quedarse en news.google.com,
    # eso es comportamiento documentado; solo exigimos que regrese una URL http).
    cands = ingest_news.search_news("projection mapping", lookback_days=14, limit=3)
    if cands:
        resolved = ingest_news.resolve_link(cands[0].link)
        assert isinstance(resolved, str) and resolved.startswith("http")


# ---------------------------------------------------------------------------
# Runner standalone (sin pytest)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in tests:
        label = fn.__name__ + (" [red]" if getattr(fn, "_requires_network", False) else "")
        if getattr(fn, "_requires_network", False) and not _NETWORK_OK:
            print(f"[SKIP] {label} (SKIP_NETWORK_TESTS)")
            continue
        try:
            fn()
            print(f"[PASS] {label}")
        except AssertionError as e:
            failed += 1
            print(f"[FAIL] {label}: {e}")
        except Exception as e:
            failed += 1
            print(f"[ERROR] {label}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} OK")
    sys.exit(1 if failed else 0)
