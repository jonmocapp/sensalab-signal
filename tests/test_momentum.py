"""Tests de momentum.py (picos/temas). Correr: python -m unittest discover tests -v"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models import Candidate  # noqa: E402
from momentum import (SATURATION_SIZE, MOMENT_BONUS, cluster,  # noqa: E402
                      dominant_topic, score_momentum)


def cand(headline, topic="", moment=None, entities=None, link=""):
    c = Candidate(headline=headline, source="Test", link=link or f"https://x.io/{headline}",
                  summary="", topic=topic, moment=moment)
    if entities:
        c.entities.update(entities)
    return c


def pool_sphere_week():
    """5 candidatos del mismo topic + 2 sueltos (el caso canonico del spec)."""
    cands = [cand(f"sphere-{i}", topic="sphere-las-vegas") for i in range(5)]
    cands.append(cand("solo-1", topic="gaussian-splatting"))
    cands.append(cand("solo-2", topic="teamlab-miami"))
    return cands


class TestCluster(unittest.TestCase):
    def test_groups_by_topic(self):
        clusters = cluster(pool_sphere_week())
        self.assertEqual(len(clusters), 3)
        self.assertEqual(len(clusters["sphere-las-vegas"]), 5)
        self.assertEqual(len(clusters["gaussian-splatting"]), 1)

    def test_topic_normalized(self):
        clusters = cluster([cand("a", topic="  Sphere-Las-Vegas "),
                            cand("b", topic="sphere-las-vegas")])
        self.assertEqual(list(clusters), ["sphere-las-vegas"])
        self.assertEqual(len(clusters["sphere-las-vegas"]), 2)

    def test_empty_topic_falls_back_to_dominant_entity(self):
        # Sin topic: dos notas que comparten "cosm" deben caer juntas, aunque una
        # tambien mencione otra entidad menos frecuente en el pool.
        a = cand("a", entities={"venues": ["Cosm"], "ip": ["Harry Potter"]})
        b = cand("b", entities={"venues": ["Cosm"]})
        clusters = cluster([a, b])
        self.assertIn("cosm", clusters)
        self.assertEqual(len(clusters["cosm"]), 2)

    def test_no_topic_no_entities_is_singleton_by_key(self):
        a = cand("orphan", link="https://x.io/orphan-note")
        clusters = cluster([a])
        self.assertEqual(list(clusters.values()), [[a]])

    def test_empty_pool(self):
        self.assertEqual(cluster([]), {})


class TestScoreMomentum(unittest.TestCase):
    def test_big_cluster_saturates_and_singletons_stay_low(self):
        cands = pool_sphere_week()
        score_momentum(cands)
        for c in cands[:5]:  # cluster de 5 = SATURATION_SIZE -> tope
            self.assertEqual(c.scores["momentum"], 1.0)
        for c in cands[5:]:  # singletons sin momento -> 0
            self.assertEqual(c.scores["momentum"], 0.0)

    def test_intermediate_cluster_size(self):
        cands = [cand(f"n{i}", topic="led-volumes") for i in range(3)] + [cand("solo")]
        score_momentum(cands)
        expected = (3 - 1) / (SATURATION_SIZE - 1)  # 0.5
        for c in cands[:3]:
            self.assertAlmostEqual(c.scores["momentum"], expected)

    def test_moment_bonus_on_singleton(self):
        c = cand("siggraph-note", topic="siggraph", moment="siggraph-2026")
        score_momentum([c])
        self.assertAlmostEqual(c.scores["momentum"], MOMENT_BONUS)

    def test_moment_bonus_capped_at_one(self):
        cands = [cand(f"wc{i}", topic="world-cup", moment="world-cup-2026")
                 for i in range(6)]
        score_momentum(cands)
        for c in cands:
            self.assertEqual(c.scores["momentum"], 1.0)

    def test_all_scores_in_range(self):
        cands = pool_sphere_week() + [cand("m", moment="ces-2027")]
        score_momentum(cands)
        for c in cands:
            self.assertGreaterEqual(c.scores["momentum"], 0.0)
            self.assertLessEqual(c.scores["momentum"], 1.0)

    def test_empty_pool_noop(self):
        score_momentum([])  # no debe tronar


class TestDominantTopic(unittest.TestCase):
    def test_biggest_cluster_wins(self):
        self.assertEqual(dominant_topic(pool_sphere_week()), ("sphere-las-vegas", 5))

    def test_tie_breaks_alphabetically(self):
        cands = [cand("a1", topic="zeta"), cand("a2", topic="zeta"),
                 cand("b1", topic="alpha"), cand("b2", topic="alpha")]
        self.assertEqual(dominant_topic(cands), ("alpha", 2))

    def test_empty_pool_returns_none(self):
        self.assertIsNone(dominant_topic([]))


if __name__ == "__main__":
    unittest.main()
