# -*- coding: utf-8 -*-
"""Tests del composer (meta-selector + formatos). Sin red: los momentos se pasan
via state["moments"] para no depender de calendar_events ni de la fecha real."""
import os
import re
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Candidate
import composer

NOW = datetime(2026, 7, 23, tzinfo=timezone.utc)


def mk(headline, source="Src", topic="", moment=None, geo=False, **scores):
    slug = re.sub(r"[^a-z0-9]+", "-", headline.lower()).strip("-")  # link unico por titular
    c = Candidate(headline=headline, source=source, link="https://ex.com/" + slug,
                  summary=headline, published=NOW, tier="query", geo=geo)
    c.topic = topic
    c.moment = moment
    base = {"relevance": 0.6, "b2b": 0.6, "timeliness": 0.8, "momentum": 0.0,
            "novelty": 1.0, "authority": 0.5, "talkability": 0.0, "angle": 0.0,
            "geo": 1.0 if geo else 0.0}
    base.update(scores)
    base["total"] = sum(base.values()) / len(base)
    c.scores = base
    return c


class TestComposer(unittest.TestCase):

    def test_steal_this_para_momento_just_ended(self):
        """Mundial recien terminado con cluster -> steal_this (las mejores ideas del Mundial)."""
        pool = [mk(f"World Cup activation number {i} projection mapping", source=f"S{i}",
                   topic="world-cup", moment="world-cup-2026", momentum=1.0, b2b=0.7)
                for i in range(5)]
        pool.append(mk("Some unrelated retail news", source="X", topic="retail"))
        state = {"moments": {"world-cup-2026": "just-ended"}}
        fmt, fit, reason = composer.choose_format(pool, NOW, state)
        self.assertEqual(fmt, "steal_this", reason)
        plan = composer.compose(pool, NOW, state)
        self.assertEqual(plan.format_id, "steal_this")
        self.assertTrue(all(s.moment == "world-cup-2026" for s in plan.stories))

    def test_digest_para_pool_disperso(self):
        """Pool variado sin señal fuerte -> digest."""
        pool = [mk(f"Experiential story {i}", source=f"S{i}", topic=f"topic-{i}")
                for i in range(8)]
        fmt, fit, reason = composer.choose_format(pool, NOW, {})
        self.assertEqual(fmt, "digest", reason)

    def test_teardown_para_talkability_alta(self):
        """Un craft-fail polemico -> teardown."""
        pool = [mk("Shrek short slammed as ugly by fans", source="SMT", topic="shrek",
                   talkability=0.9)]
        pool += [mk(f"Filler experiential {i}", source=f"S{i}", topic=f"t{i}") for i in range(4)]
        fmt, fit, reason = composer.choose_format(pool, NOW, {})
        self.assertEqual(fmt, "teardown", reason)

    def test_tech_unlock_exige_release_real(self):
        """Un release real de tool -> tech_unlock; una activacion con tech NO."""
        # activacion fresca con tech, SIN palabra de release -> NO debe ser tech_unlock
        activation = mk("Nike pop-up brings AR and LED floor to fans", source="BizBash",
                        topic="nike")
        activation.entities["tech"] = ["AR", "LED"]
        pool_a = [activation] + [mk(f"x {i}", topic=f"t{i}") for i in range(4)]
        fmt_a, _, _ = composer.choose_format(pool_a, NOW, {})
        self.assertNotEqual(fmt_a, "tech_unlock")

        # release real (Unreal "launches") -> tech_unlock elegible
        release = mk("Epic launches Unreal Engine 6 with real-time gaussian splatting",
                     source="AV", topic="unreal-engine", timeliness=0.9, relevance=0.8)
        release.entities["tech"] = ["Unreal", "gaussian splatting", "real-time"]
        pool_b = [release] + [mk(f"y {i}", topic=f"u{i}") for i in range(4)]
        fmt_b, fit_b, reason_b = composer.choose_format(pool_b, NOW, {})
        self.assertEqual(fmt_b, "tech_unlock", reason_b)

    def test_pool_chico_digest_degradado(self):
        pool = [mk("Only one story", topic="a")]
        fmt, fit, reason = composer.choose_format(pool, NOW, {})
        self.assertEqual(fmt, "digest")
        plan = composer.compose(pool, NOW, {})
        self.assertEqual(plan.format_id, "digest")

    def test_compose_setea_angulo_por_historia(self):
        pool = [mk(f"World Cup idea {i}", source=f"S{i}", topic="world-cup",
                   moment="world-cup-2026", momentum=1.0) for i in range(4)]
        state = {"moments": {"world-cup-2026": "just-ended"}}
        plan = composer.compose(pool, NOW, state)
        for s in plan.stories:
            self.assertTrue(s.angle)  # cada historia lleva un angulo


if __name__ == "__main__":
    unittest.main(verbosity=2)
