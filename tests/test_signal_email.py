# -*- coding: utf-8 -*-
"""
Regresion del carril de produccion (The Signal): email real de inbox + gates.

Cubre los bugs corregidos en la revision de produccion:
  1. logo del header anidaba un <img> DENTRO de src= (logo roto en todos los clientes)
  2. tabla exterior con width fija 600px (overflow/zoom en Gmail/Apple Mail movil)
  3. gate non-compete fail-closed (guard.assert_clean)
  4. peso del email < limite de clipping de Gmail (~102KB)
  5. render_signal ya no emite <img src=""> cuando falta portada
"""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

import guard
from signal_email import build_signal_email
from render_signal import build_signal

ED = {
    "issue_no": "07",
    "hero": {"kicker": "This week's signal", "statement": "Light moves live now",
             "sub": "What the show floor means for producers."},
    "sections": [
        {"role": "field-notes", "statement": "The render wait is over",
         "body": "Real time light changes the brief.", "why": "Budgets move", "cta": "Read more ›"},
        {"role": "in-the-lab", "statement": "One stage, ten cities",
         "body": "The volume replaces the location scout."},
        {"role": "craft", "statement": "Presence is the product",
         "body": "The room answers back."},
    ],
    "video": {"headline": "Watch the demo", "body": "Sixty seconds of live light."},
    "invitation": {"headline": "Own a moment", "body": "Bring a brief.", "button": "Touch it"},
}
MEDIA = {"hero": "media/hero.jpg",
         "sections": {"field-notes": "media/a.jpg", "in-the-lab": "media/b.jpg"},
         "video": {"poster": "media/hero.jpg", "link": "https://example.com/v"}}
BASE = "https://signal.sensalab.io/07/"


def _email():
    return build_signal_email(ED, MEDIA, web_url=BASE, issue_no="07",
                              date=datetime(2026, 7, 28, tzinfo=timezone.utc),
                              img_base=BASE, logo="media/sensalab-logo.png")


def test_header_logo_is_plain_url_not_nested_img():
    html = _email()
    m = re.search(r'<img src="([^"]*)" height="26" alt="SensaLab"', html)
    assert m, "el logo del header debe existir"
    assert m.group(1) == BASE + "media/sensalab-logo.png"
    assert "src=\"<img" not in html and "src=&quot;" not in html.split("</head>")[0]


def test_outer_table_is_fluid_for_mobile():
    html = _email()
    assert 'style="width:100%;max-width:600px' in html, \
        "la tabla principal debe ser fluida (hibrido: width=600 attr + max-width CSS)"
    assert 'width="600"' in html, "Outlook necesita el atributo width=600"


def test_email_has_viewport_and_fits_gmail_clip():
    html = _email()
    assert 'name="viewport"' in html
    assert len(html.encode("utf-8")) < 102 * 1024, "Gmail clippea emails > ~102KB"


def test_email_footer_has_no_dashes_in_copy():
    html = _email()
    text = re.sub(r"<[^>]+>", " ", html)
    assert "—" not in text, "regla de marca: sin em dash en copy legible"


def test_guard_fail_closed_blocks():
    with pytest.raises(guard.GuardBlocked):
        guard.assert_clean({"hero": {"statement": "work we did at Cinetica"}})


def test_guard_clean_passes():
    assert guard.assert_clean(ED) is True


def test_web_card_without_image_has_no_empty_img():
    html = build_signal(ED, {"sections": {}}, issue_no="07",
                        date=datetime(2026, 7, 28, tzinfo=timezone.utc), web_url=BASE)
    assert 'src=""' not in html, "sin portada no debe emitirse <img src=''>"
