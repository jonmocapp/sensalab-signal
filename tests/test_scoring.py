"""Tests de scoring.py (combinar + helpers + loop de aprendizaje).
Correr: python -m unittest discover tests -v"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models import Candidate, SCORE_KEYS  # noqa: E402
import scoring  # noqa: E402
from scoring import (WEIGHTS, adjust_weights, authority, combine,  # noqa: E402
                     load_weights, novelty, rank, save_weights, timeliness)

NOW = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)


def cand(**kw):
    base = dict(headline="h", source="Test", link="https://x.io/n", summary="")
    base.update(kw)
    return Candidate(**base)


class TestWeights(unittest.TestCase):
    def test_covers_all_subscores(self):
        self.assertEqual(set(WEIGHTS), set(SCORE_KEYS) - {"total"})

    def test_sums_to_one(self):
        self.assertAlmostEqual(sum(WEIGHTS.values()), 1.0)

    def test_editorial_priorities(self):
        # relevance y b2b (la puerta + el test del productor) pesan mas que el resto.
        top2 = sorted(WEIGHTS, key=WEIGHTS.get, reverse=True)[:2]
        self.assertEqual(set(top2), {"relevance", "b2b"})


class TestCombine(unittest.TestCase):
    def test_weighted_total_coherent(self):
        c = cand()
        c.scores = {"relevance": 1.0, "b2b": 1.0, "timeliness": 0.5, "momentum": 1.0,
                    "novelty": 1.0, "authority": 0.8, "talkability": 0.0,
                    "angle": 0.5, "geo": 1.0}
        combine(c)
        expected = sum(WEIGHTS[k] * c.scores[k] for k in WEIGHTS)  # pesos ya suman 1
        self.assertAlmostEqual(c.scores["total"], expected, places=4)
        self.assertGreater(c.scores["total"], 0.0)
        self.assertLessEqual(c.scores["total"], 1.0)

    def test_missing_subscores_count_as_zero(self):
        c = cand()
        c.scores = {"relevance": 1.0}  # todo lo demas falta
        combine(c)
        self.assertAlmostEqual(c.scores["total"], WEIGHTS["relevance"], places=4)

    def test_all_perfect_gives_one(self):
        c = cand()
        c.scores = {k: 1.0 for k in WEIGHTS}
        combine(c)
        self.assertAlmostEqual(c.scores["total"], 1.0, places=4)

    def test_custom_weights_are_normalized(self):
        # Pesos que suman 2.0 deben dar el mismo total que los mismos pesos /2.
        c1, c2 = cand(), cand()
        subs = {"relevance": 0.8, "momentum": 0.4}
        c1.scores = dict(subs)
        c2.scores = dict(subs)
        w = {k: v * 2 for k, v in WEIGHTS.items()}
        combine(c1, weights=w)
        combine(c2, weights=WEIGHTS)
        self.assertAlmostEqual(c1.scores["total"], c2.scores["total"], places=4)

    def test_zero_weights_give_zero(self):
        c = cand()
        c.scores = {"relevance": 1.0}
        combine(c, weights={k: 0.0 for k in WEIGHTS})
        self.assertEqual(c.scores["total"], 0.0)


class TestTimeliness(unittest.TestCase):
    def test_fresh_is_one(self):
        c = cand(published=NOW - timedelta(hours=2))
        self.assertAlmostEqual(timeliness(c, NOW), 1.0, places=1)
        self.assertIn("timeliness", c.scores)

    def test_half_window_is_half(self):
        c = cand(published=NOW - timedelta(days=5))
        self.assertAlmostEqual(timeliness(c, NOW), 0.5, places=2)

    def test_stale_is_zero(self):
        c = cand(published=NOW - timedelta(days=20))
        self.assertEqual(timeliness(c, NOW), 0.0)

    def test_unknown_date_neutral_low(self):
        c = cand(published=None)
        self.assertAlmostEqual(timeliness(c, NOW), scoring.TIMELINESS_UNKNOWN)

    def test_moment_bonus_and_cap(self):
        old = cand(published=NOW - timedelta(days=5), moment="siggraph-2026")
        self.assertAlmostEqual(timeliness(old, NOW), 0.7, places=2)
        fresh = cand(published=NOW, moment="siggraph-2026")
        self.assertEqual(timeliness(fresh, NOW), 1.0)  # cap en 1.0

    def test_naive_datetime_ok(self):
        c = cand(published=datetime(2026, 7, 22, 12, 0))  # naive -> asume UTC
        self.assertAlmostEqual(timeliness(c, NOW), 0.9, places=2)


class TestAuthority(unittest.TestCase):
    def test_tier_ordering(self):
        core = authority(cand(tier="core"))
        rotate = authority(cand(tier="rotate"))
        query = authority(cand(tier="query"))
        self.assertGreater(core, rotate)
        self.assertGreater(rotate, query)

    def test_brand_or_venue_bonus(self):
        plain = cand(tier="query")
        branded = cand(tier="query")
        branded.entities["brands"].append("Netflix")
        self.assertGreater(authority(branded), authority(plain))
        venue = cand(tier="query")
        venue.entities["venues"].append("Sphere")
        self.assertAlmostEqual(authority(venue), authority(branded))

    def test_capped_at_one(self):
        c = cand(tier="core")
        c.entities["brands"].append("Apple")
        c.entities["venues"].append("Cosm")
        self.assertLessEqual(authority(c), 1.0)


class TestNovelty(unittest.TestCase):
    def test_fresh_topic(self):
        c = cand(topic="gaussian-splatting")
        self.assertEqual(novelty(c, {"sphere", "led-volumes"}), 1.0)

    def test_repeated_topic_punished(self):
        c = cand(topic="Sphere")  # case-insensitive
        self.assertEqual(novelty(c, {"sphere"}), scoring.NOVELTY_REPEATED)

    def test_no_topic_neutral(self):
        c = cand(topic="")
        self.assertEqual(novelty(c, {"sphere"}), scoring.NOVELTY_UNKNOWN)


class TestRank(unittest.TestCase):
    def test_orders_by_total_desc(self):
        a, b, c = cand(headline="a"), cand(headline="b"), cand(headline="c")
        a.scores["total"] = 0.3
        b.scores["total"] = 0.9
        c.scores["total"] = 0.6
        self.assertEqual([x.headline for x in rank([a, b, c])], ["b", "c", "a"])

    def test_stable_on_ties_and_missing_total(self):
        a, b = cand(headline="a"), cand(headline="b")  # ambos sin total -> 0.0
        self.assertEqual([x.headline for x in rank([a, b])], ["a", "b"])

    def test_end_to_end_with_combine(self):
        hot, cold = cand(headline="hot"), cand(headline="cold")
        hot.scores = {"relevance": 1.0, "b2b": 1.0, "momentum": 1.0}
        cold.scores = {"relevance": 0.2, "b2b": 0.1}
        combine(hot)
        combine(cold)
        self.assertEqual(rank([cold, hot])[0].headline, "hot")


class TestLearningLoop(unittest.TestCase):
    def test_save_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "data" / "weights.json"  # data/ no existe aun
            tweaked = dict(WEIGHTS, momentum=0.2)
            save_weights(path, tweaked)
            loaded = load_weights(path)
            self.assertAlmostEqual(loaded["momentum"], 0.2)
            self.assertEqual(set(loaded), set(WEIGHTS))

    def test_load_missing_file_returns_defaults_copy(self):
        loaded = load_weights(Path("no") / "existe.json")
        self.assertEqual(loaded, WEIGHTS)
        loaded["geo"] = 99  # mutar la copia no toca los defaults
        self.assertNotEqual(WEIGHTS["geo"], 99)

    def test_load_corrupt_file_returns_defaults(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "weights.json"
            path.write_text("{esto no es json", encoding="utf-8")
            self.assertEqual(load_weights(path), WEIGHTS)

    def test_load_merges_over_defaults(self):
        # Un weights.json viejo sin una senal nueva no la borra.
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "weights.json"
            path.write_text(json.dumps({"momentum": 0.3}), encoding="utf-8")
            loaded = load_weights(path)
            self.assertAlmostEqual(loaded["momentum"], 0.3)
            self.assertAlmostEqual(loaded["relevance"], WEIGHTS["relevance"])

    def test_adjust_raises_winners_lowers_losers(self):
        new = adjust_weights(WEIGHTS, {"momentum": +1.0, "geo": -1.0})
        self.assertGreater(new["momentum"], WEIGHTS["momentum"])
        self.assertLess(new["geo"], WEIGHTS["geo"])
        self.assertAlmostEqual(sum(new.values()), 1.0, places=6)

    def test_adjust_does_not_mutate_input(self):
        before = dict(WEIGHTS)
        adjust_weights(WEIGHTS, {"momentum": 1.0})
        self.assertEqual(WEIGHTS, before)

    def test_adjust_ignores_unknown_signals_and_clamps_perf(self):
        new = adjust_weights(WEIGHTS, {"formato-x": 1.0, "momentum": 999})
        self.assertNotIn("formato-x", new)
        # perf 999 se clampa a 1.0 -> mismo efecto que +1.0
        ref = adjust_weights(WEIGHTS, {"momentum": 1.0})
        self.assertAlmostEqual(new["momentum"], ref["momentum"], places=6)

    def test_weights_never_die_after_many_bad_weeks(self):
        w = dict(WEIGHTS)
        for _ in range(100):
            w = adjust_weights(w, {"geo": -1.0})
        self.assertGreater(w["geo"], 0.0)  # MIN_WEIGHT (pre-normalizacion) lo protege
        self.assertAlmostEqual(sum(w.values()), 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
