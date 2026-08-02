# -*- coding: utf-8 -*-
"""
cover_image — pipeline ROBUSTO de portada de noticia (reutilizable para el newsletter y el blog).

Para una historia (una o varias URLs fuente) devuelve la MEJOR imagen de portada:
  1. extrae candidatas del artículo: og:image, twitter:image, JSON-LD, link image_src.
  2. FILTRO DE CALIDAD: rechaza logos / iconos / gráficos planos / banners / imágenes chicas.
  3. FALLBACK: prueba candidatas y fuentes en orden hasta que una pase el filtro.
  4. guarda email-safe (fetch_media.save_image) y evita duplicados (avoid set).

El filtro es lo que faltaba: antes se colaban logos (Bristol, AWE, la "C" de Yahoo).
"""
from __future__ import annotations

import re
from collections import Counter
from io import BytesIO
from urllib.parse import urljoin

import fetch_media
from fetch_media import Image, _PIL  # PIL opcional

# Reglas de tamaño/forma de una PORTADA real (no logo/icono/banner).
MIN_SIDE = 300        # lado corto mínimo (px)
MIN_LONG = 600        # lado largo mínimo (px)
MIN_AR, MAX_AR = 0.7, 3.3   # ni casi-cuadrada (logo) ni banner ultra-ancho

# Palabras en la URL que delatan que NO es una portada limpia (logo/icono/composite/promo).
_BAD_URL = re.compile(
    r"(logo|icon|favicon|sprite|avatar|placeholder|default|blank|spacer|1x1|badge|"
    r"pixel|button|/ads?/|-ad-|watermark|thumb_|/thumbs?/|social-share|splash-for-socials|"
    r"collage|montage|composite|promo|teaser|price|share-image|share-card|og-default)",
    re.I)


def _html(page_url):
    r = fetch_media._get(page_url)
    r.raise_for_status()
    return r.text, str(r.url)


def extract_candidates(page_url):
    """Devuelve URLs candidatas de portada, en orden de prioridad, absolutas y sin repetir."""
    html, base = _html(page_url)
    cands = []
    pats = [
        r'<meta[^>]+property=["\']og:image(?::url|:secure_url)?["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        r'<meta[^>]+name=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image["\']',
        r'<link[^>]+rel=["\']image_src["\'][^>]+href=["\']([^"\']+)',
    ]
    for pat in pats:
        for m in re.finditer(pat, html, re.I):
            cands.append(m.group(1))
    # JSON-LD "image": "..."  o  "image": {"url": "..."}  o  "image": ["...", ...]
    for blk in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.I | re.S):
        for im in re.finditer(r'"image"\s*:\s*(?:\{[^}]*?"url"\s*:\s*)?["\']([^"\']+)', blk.group(1)):
            cands.append(im.group(1))
    # dedup preservando orden + absolutizar
    seen, out = set(), []
    for u in cands:
        u = urljoin(base, u.strip())
        if u.startswith("http") and u not in seen:
            seen.add(u)
            out.append(u)
    return out


def is_cover_photo(im) -> bool:
    """True si parece una FOTO de portada; False si es logo / icono / gráfico plano / banner.
    Regla clave: un color dominante que cubre gran parte = fondo plano = logo. Rechaza TODOS
    los logos probados (incl. de alto contraste como AWE) a costa de rechazar fotos muy oscuras
    (esas se resuelven con otra candidata, no relajando el filtro)."""
    w, h = im.size
    if min(w, h) < MIN_SIDE or max(w, h) < MIN_LONG:
        return False
    ar = w / h if h else 0
    if ar < MIN_AR or ar > MAX_AR:
        return False
    rgb = im.convert("RGB").resize((48, 48))
    q = [(r >> 5, g >> 5, b >> 5) for (r, g, b) in rgb.getdata()]   # cuantiza a 3 bits/canal
    c = Counter(q)
    total = len(q)
    dominant = c.most_common(1)[0][1] / total
    distinct = len(c)
    if dominant > 0.55:      # un color cubre >55% -> fondo plano (logo/gráfico)
        return False
    if distinct < 32:        # muy pocos colores -> no es foto
        return False
    return True


def best_cover(page_urls, dest_noext, avoid=None):
    """Prueba las fuentes/candidatas y guarda la primera que pase el filtro (email-safe).
    Devuelve (basename, image_url, page_url) o (None, None, None) si ninguna sirve.
    `avoid`: set de URLs de imagen ya usadas (evita repetir entre slots)."""
    if isinstance(page_urls, str):
        page_urls = [page_urls]
    avoid = avoid if avoid is not None else set()
    if not _PIL:
        return None, None, None
    for pu in page_urls:
        try:
            candidates = extract_candidates(pu)
        except Exception:
            continue
        # elige la candidata que pase el filtro con MAYOR área (suele ser la foto principal,
        # no un thumbnail chico ni un composite promocional).
        best = None  # (area, im, cu)
        for cu in candidates:
            if cu in avoid or _BAD_URL.search(cu):
                continue
            try:
                r = fetch_media._get(cu)
                r.raise_for_status()
                im = Image.open(BytesIO(r.content))
                im.load()
            except Exception:
                continue
            if not is_cover_photo(im):
                continue
            area = im.size[0] * im.size[1]
            if best is None or area > best[0]:
                best = (area, im, cu)
        if best:
            fname = fetch_media.save_image(best[1], dest_noext)
            avoid.add(best[2])
            return fname, best[2], pu
    return None, None, None


if __name__ == "__main__":
    import sys
    for u in sys.argv[1:]:
        print(u)
        for c in extract_candidates(u):
            print("   ", c)
