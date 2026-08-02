# -*- coding: utf-8 -*-
"""
Tests de fetch_media.download: garantiza que las imagenes quedan EMAIL-SAFE
(nunca .webp; ancho tope; JPG comprimido) sin tocar la red (mock de _get).
"""
import os
import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

fetch_media = pytest.importorskip("fetch_media")
Image = pytest.importorskip("PIL.Image")


class _FakeResp:
    def __init__(self, content, content_type):
        self.content = content
        self.headers = {"content-type": content_type}

    def raise_for_status(self):
        return None


def _webp_bytes(w=2000, h=1200, color=(80, 120, 200)):
    buf = BytesIO()
    Image.new("RGB", (w, h), color).save(buf, "WEBP", quality=90)
    return buf.getvalue()


def _png_alpha_bytes(w=400, h=400):
    buf = BytesIO()
    Image.new("RGBA", (w, h), (0, 0, 0, 0)).save(buf, "PNG")
    return buf.getvalue()


def test_webp_transcodes_to_jpg_and_compresses(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch_media, "_get",
                        lambda url, **kw: _FakeResp(_webp_bytes(), "image/webp"))
    out = fetch_media.download("https://x/y.webp", str(tmp_path / "hero"))
    assert out.endswith(".jpg"), f"webp debe transcodificarse a jpg, no {out}"
    p = tmp_path / out
    assert p.exists()
    assert p.stat().st_size <= fetch_media.MAXKB * 1024, "el jpg debe quedar <=200KB"
    with Image.open(p) as im:
        assert im.width <= fetch_media.MAXW, "el ancho debe respetar el tope"


def test_png_with_alpha_stays_png(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch_media, "_get",
                        lambda url, **kw: _FakeResp(_png_alpha_bytes(), "image/png"))
    out = fetch_media.download("https://x/logo.png", str(tmp_path / "logo"))
    assert out.endswith(".png"), "un PNG con transparencia debe conservarse como PNG"


def test_no_webp_ever_returned(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch_media, "_get",
                        lambda url, **kw: _FakeResp(_webp_bytes(800, 600), "image/webp"))
    out = fetch_media.download("https://x/z.webp", str(tmp_path / "img"))
    assert not out.endswith(".webp"), "jamas debe salir un .webp (Outlook no lo renderiza)"
