"""
Tests de content_model.py (fuente unica email + blog).

Correr desde la raiz del proyecto:
    python tests/test_content_model.py
    (o) python -m unittest discover -s tests -t .
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import content_model as cm
from models import Candidate


def sample_issue() -> dict:
    """Issue dict como lo devuelve writer.write_issue (mismas claves)."""
    return {
        "subject": "La Sphere sube la vara (otra vez)",
        "preview_text": "Proyeccion, IA y por que importa a quien produce experiencias.",
        "intro": "Esta semana el liston se movio en Las Vegas y en el retail.",
        "stories": [
            {
                "headline": "Harry Potter llegó a Cosm LA con proyección 8K",
                "source": "Variety",
                "link": "https://variety.com/2026/harry-potter-cosm-la/?utm_source=x",
                "body": "Cosm estrena una experiencia inmersiva de Harry Potter en Los Angeles.",
                "lens": "Para SensaLab, esto le importa a marcas, agencias y empresas porque "
                        "los venues de domo abren inventario premium para IP.",
            },
            {
                "headline": "Unreal Engine 6 & el LED volume \"barato\"",
                "source": "The Verge",
                "link": "https://www.theverge.com/2026/unreal-6-led-volume",
                "body": "Epic baja el costo de entrada a produccion virtual.",
                "lens": "Para SensaLab, esto le importa a marcas, agencias y empresas porque "
                        "desbloquea produccion virtual para presupuestos de activacion.",
                "image": "https://cdn.example.com/led.jpg",
            },
        ],
        "signoff": "Nos vemos donde la presencia es el lujo.",
    }


def sample_edition() -> cm.Edition:
    return cm.from_issue(sample_issue(), number=7, date=date(2026, 7, 23),
                         format_id="B-momento", theme="Domos e IP")


class TestSlugify(unittest.TestCase):
    def test_accents_and_symbols(self):
        self.assertEqual(cm.slugify("Harry Potter llegó a Cosm LA — 8K!"),
                         "harry-potter-llego-a-cosm-la-8k")

    def test_empty_falls_back(self):
        self.assertEqual(cm.slugify(""), "historia")

    def test_max_len_cuts_on_word(self):
        s = cm.slugify("uno dos tres cuatro cinco seis siete ocho nueve diez once doce", 30)
        self.assertLessEqual(len(s), 30)
        self.assertFalse(s.endswith("-"))


class TestIssueRoundTrip(unittest.TestCase):
    """issue -> from_issue -> to_issue debe ser identico para el templater v1."""

    def test_round_trip_fields(self):
        issue = sample_issue()
        ed = cm.from_issue(issue, number=7, date=datetime(2026, 7, 23, tzinfo=timezone.utc),
                           format_id="A-digest", theme="semana normal")
        out = cm.to_issue(ed)

        for k in ("subject", "preview_text", "intro", "signoff"):
            self.assertEqual(out[k], issue[k])
        self.assertEqual(len(out["stories"]), len(issue["stories"]))
        for got, orig in zip(out["stories"], issue["stories"]):
            for k in ("headline", "source", "link", "body", "lens"):
                self.assertEqual(got[k], orig[k], f"campo {k} no sobrevivio el round-trip")
        # la imagen opcional tambien sobrevive (story 2) y no se inventa (story 1)
        self.assertNotIn("image", out["stories"][0])
        self.assertEqual(out["stories"][1]["image"], issue["stories"][1]["image"])
        # sin canonical NO se agregan claves extra (email v1 intacto)
        self.assertNotIn("source_url", out["stories"][0])

    def test_datetime_coerced_to_date(self):
        ed = cm.from_issue(sample_issue(), number=1,
                           date=datetime(2026, 7, 23, 15, 0, tzinfo=timezone.utc),
                           format_id="A-digest", theme="t")
        self.assertEqual(ed.date, date(2026, 7, 23))

    def test_duplicate_headlines_get_unique_slugs(self):
        issue = sample_issue()
        issue["stories"].append(dict(issue["stories"][0]))
        ed = cm.from_issue(issue, number=2, date=date(2026, 7, 23),
                           format_id="A-digest", theme="t")
        slugs = [s.slug for s in ed.stories]
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_candidate_enrichment_by_link(self):
        issue = sample_issue()
        cand = Candidate(
            headline="whatever", source="Variety",
            # mismo link que story 1 pero con utm/slash distintos -> match normalizado
            link="https://variety.com/2026/harry-potter-cosm-la/",
            entities={"venues": ["Cosm"], "ip": ["Harry Potter"],
                      "brands": [], "tech": [], "agencies": []},
            angle="bar-moved",
        )
        ed = cm.from_issue(issue, number=3, date=date(2026, 7, 23),
                           format_id="B-momento", theme="domos", candidates=[cand])
        self.assertEqual(ed.stories[0].angle, "bar-moved")
        self.assertEqual(ed.stories[0].entities["venues"], ["Cosm"])
        # la story 2 no matchea -> defaults
        self.assertEqual(ed.stories[1].angle, "straight")


class TestDictAndJsonRoundTrip(unittest.TestCase):
    def test_to_dict_from_dict(self):
        ed = sample_edition()
        ed2 = cm.Edition.from_dict(ed.to_dict())
        self.assertEqual(ed, ed2)

    def test_save_load_json_file(self):
        ed = sample_edition()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            path = cm.save_edition(ed, content_dir=tmp)
            self.assertEqual(path.name, "edicion-7.json")   # content/edicion-<n>.json
            self.assertTrue(path.exists())

            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(raw["schema"], cm.SCHEMA_VERSION)
            self.assertEqual(raw["slug"], ed.slug)
            self.assertEqual(raw["date"], "2026-07-23")

            ed2 = cm.load_edition(7, content_dir=tmp)
            self.assertEqual(ed, ed2)
            self.assertEqual(cm.list_editions(tmp), [7])

    def test_invalid_angle_degrades_to_straight(self):
        s = cm.StoryContent(slug="", headline="X", source_name="S",
                            source_url="https://x.com", body="b", lens="l",
                            angle="clickbait-total")
        self.assertEqual(s.angle, "straight")


class TestCanonical(unittest.TestCase):
    def test_set_canonical_builds_url_from_slug(self):
        ed = sample_edition()
        url = cm.set_canonical(ed)
        self.assertEqual(url, ed.canonical_url)
        self.assertEqual(url, f"https://sensalab.io/blog/{ed.slug}/")
        self.assertTrue(ed.slug.startswith("inmersivo-07-domos-e-ip"))

    def test_story_url_has_anchor(self):
        ed = sample_edition()
        self.assertIsNone(cm.canonical_story_url(ed, ed.stories[0]))  # sin sitio aun
        cm.set_canonical(ed)
        u = cm.canonical_story_url(ed, ed.stories[0])
        self.assertEqual(u, ed.canonical_url + "#" + ed.stories[0].slug)

    def test_to_issue_prefer_canonical_links_to_our_post(self):
        ed = sample_edition()
        cm.set_canonical(ed)
        out = cm.to_issue(ed, prefer_canonical=True)
        for got, story in zip(out["stories"], ed.stories):
            self.assertTrue(got["link"].startswith(ed.canonical_url))
            self.assertIn("#" + story.slug, got["link"])
            self.assertEqual(got["source_url"], story.source_url)  # cita al pie v2

    def test_prefer_canonical_without_url_keeps_source(self):
        ed = sample_edition()  # canonical_url = None
        out = cm.to_issue(ed, prefer_canonical=True)
        self.assertEqual(out["stories"][0]["link"], ed.stories[0].source_url)


class TestMarkdown(unittest.TestCase):
    def _front_matter(self, md: str) -> dict:
        """Parser minimo de front-matter (clave: valor; listas/valores JSON-compatibles)."""
        self.assertTrue(md.startswith("---\n"), "el post debe abrir con ---")
        end = md.index("\n---", 4)
        block = md[4:end]
        fm = {}
        for line in block.splitlines():
            self.assertRegex(line, r"^[a-z_]+: .+$", f"linea de front-matter invalida: {line!r}")
            key, _, val = line.partition(": ")
            try:
                fm[key] = json.loads(val)   # "..." , [...], 7 y fechas fallan -> str
            except (json.JSONDecodeError, ValueError):
                fm[key] = val
        return fm

    def test_front_matter_valido(self):
        ed = sample_edition()
        # enriquecemos entidades para tags
        ed.stories[0].entities["venues"] = ["Cosm"]
        ed.stories[0].entities["ip"] = ["Harry Potter"]
        ed.stories[1].entities["tech"] = ["Unreal Engine"]
        md = cm.to_markdown(ed)
        fm = self._front_matter(md)

        self.assertEqual(fm["title"], ed.subject)
        self.assertEqual(fm["date"], "2026-07-23")
        self.assertEqual(fm["slug"], ed.slug)
        self.assertEqual(fm["tags"], ["cosm", "harry-potter", "unreal-engine"])
        self.assertEqual(fm["description"], ed.preview_text)
        self.assertEqual(fm["edition"], 7)
        self.assertEqual(fm["format"], "B-momento")
        self.assertNotIn("canonical_url", fm)  # aun sin sitio

    def test_front_matter_canonical_cuando_existe(self):
        ed = sample_edition()
        cm.set_canonical(ed)
        fm = self._front_matter(cm.to_markdown(ed))
        self.assertEqual(fm["canonical_url"], ed.canonical_url)

    def test_body_del_post(self):
        ed = sample_edition()
        md = cm.to_markdown(ed)
        self.assertIn(ed.intro, md)
        for s in ed.stories:
            self.assertIn(f"## {s.headline}", md)
            self.assertIn(f'<a id="{s.slug}"></a>', md)      # ancla estable = canonical
            self.assertIn(f"> {s.lens}", md)
            self.assertIn(f"Fuente: [{s.source_name}]({s.source_url})", md)
        self.assertIn(f"*{ed.signoff}*", md)


class TestWebHtml(unittest.TestCase):
    def test_pagina_simple_distinta_del_email(self):
        ed = sample_edition()
        h = cm.to_web_html(ed)
        self.assertIn("<article>", h)
        self.assertIn("<h1>", h)
        self.assertNotIn("role=\"presentation\"", h)   # nada de tablas de email
        for s in ed.stories:
            self.assertIn(f'<section id="{s.slug}">', h)
            self.assertIn(s.source_url, h)
        # escapado: el & del headline de story 2 sale como &amp;
        self.assertIn("Unreal Engine 6 &amp; el LED volume", h)
        self.assertNotIn('<link rel="canonical"', h)

    def test_canonical_link_en_head(self):
        ed = sample_edition()
        cm.set_canonical(ed)
        h = cm.to_web_html(ed)
        self.assertIn(f'<link rel="canonical" href="{ed.canonical_url}">', h)


if __name__ == "__main__":
    unittest.main(verbosity=2)
