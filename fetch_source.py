# -*- coding: utf-8 -*-
"""Baja el artículo de la fuente y extrae (a) el texto principal como base de HECHOS para el
redactor y (b) la og:image. Sin dependencias nuevas: extracción por regex, tolerante a fallo.

La regla dura del redactor es 'usa SOLO los hechos provistos'; por eso el pipeline le entrega
este texto real de la fuente en vez de solo el titular, para que ancle y no invente."""
from __future__ import annotations

import html
import re

import requests

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
_TIMEOUT = 20


def _meta_content(h: str, prop: str) -> str:
    for pat in (
        r'<meta[^>]+property=["\']%s["\'][^>]+content=["\']([^"\']+)["\']' % re.escape(prop),
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']%s["\']' % re.escape(prop),
        r'<meta[^>]+name=["\']%s["\'][^>]+content=["\']([^"\']+)["\']' % re.escape(prop),
    ):
        m = re.search(pat, h, re.IGNORECASE)
        if m:
            return html.unescape(m.group(1)).strip()
    return ""


def _title(h: str) -> str:
    og = _meta_content(h, "og:title")
    if og:
        return og
    m = re.search(r"<title[^>]*>(.*?)</title>", h, re.IGNORECASE | re.DOTALL)
    return html.unescape(re.sub(r"\s+", " ", m.group(1))).strip() if m else ""


def _main_text(h: str, max_chars: int = 6000) -> str:
    """Extrae el cuerpo: quita script/style/nav/aside, junta <p> y subtítulos, limpia tags."""
    body = re.sub(r"(?is)<(script|style|noscript|template|svg)[^>]*>.*?</\1>", " ", h)
    body = re.sub(r"(?is)<(nav|header|footer|aside|form)[^>]*>.*?</\1>", " ", body)
    blocks = re.findall(r"(?is)<(p|h1|h2|h3|li)[^>]*>(.*?)</\1>", body)
    out, seen = [], set()
    for _tag, chunk in blocks:
        txt = html.unescape(re.sub(r"<[^>]+>", " ", chunk))
        txt = re.sub(r"\s+", " ", txt).strip()
        if len(txt) < 40:                      # descarta migas de nav/menús
            continue
        key = txt[:80].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(txt)
        if sum(len(x) for x in out) >= max_chars:
            break
    return "\n\n".join(out)


def fetch(url: str) -> dict | None:
    """Devuelve {url, title, text, image_url} o None si no se pudo bajar/parsear."""
    try:
        r = requests.get(url, headers={"User-Agent": _UA}, timeout=_TIMEOUT, allow_redirects=True)
        r.raise_for_status()
    except requests.RequestException:
        return None
    h = r.text or ""
    text = _main_text(h)
    return {
        "url": r.url,
        "title": _title(h),
        "text": text,
        "image_url": _meta_content(h, "og:image") or _meta_content(h, "twitter:image"),
        "ok": len(text) >= 300,   # señal de que sí hay cuerpo aprovechable
    }
