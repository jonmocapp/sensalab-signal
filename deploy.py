# -*- coding: utf-8 -*-
"""Publica el sitio (carpeta blog/) en Netlify por su API — puro Python, sin CLI ni n8n.
Necesita, una sola vez, dos variables de entorno (en .env):
    NETLIFY_AUTH_TOKEN   token personal de Netlify (Settings > Applications > Personal access tokens)
    NETLIFY_SITE_ID      id del sitio (Netlify > Site settings > Site ID / API ID)
Si faltan, no publica: deja el sitio construido en blog/ y avisa (fallback seguro)."""
from __future__ import annotations

import io
import pathlib
import zipfile

import requests

import config

BASE = pathlib.Path(__file__).resolve().parent
BLOG = BASE / "blog"


def _zip_dir(d: pathlib.Path) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in d.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(d).as_posix())
    return buf.getvalue()


def deploy(verbose: bool = True) -> bool:
    token = config.env("NETLIFY_AUTH_TOKEN")
    site = config.env("NETLIFY_SITE_ID")
    if not token or not site:
        if verbose:
            print("  [deploy] sin NETLIFY_AUTH_TOKEN/NETLIFY_SITE_ID -> sitio listo en blog/ "
                  "(no se publicó en vivo). Setéalos en .env una vez para publicar solo.")
        return False
    if not BLOG.exists():
        print("  [deploy] no existe blog/; nada que publicar."); return False
    try:
        data = _zip_dir(BLOG)
        r = requests.post(
            f"https://api.netlify.com/api/v1/sites/{site}/deploys",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/zip"},
            data=data, timeout=180)
        r.raise_for_status()
        j = r.json()
        url = j.get("ssl_url") or j.get("deploy_ssl_url") or j.get("url") or ""
        if verbose:
            print(f"  [deploy] publicado en Netlify: {url}")
        return True
    except requests.RequestException as e:
        print(f"  [deploy] error publicando: {e}")
        return False


if __name__ == "__main__":
    import sys
    sys.exit(0 if deploy() else 1)
