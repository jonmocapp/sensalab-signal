# -*- coding: utf-8 -*-
"""
Email slim (email-safe) de una edicion — la pareja del diseño WEB (a1 Pearl).
Es el vehiculo: llega al inbox y LINKEA a la edicion web (todo el trafico va a NUESTRO
sitio, no a terceros). Tablas + CSS inline + 600px + fuentes con fallback + imagenes
hospedadas. Incluye UTM en cada link (tracking first-party) y target=_blank (B2B).

build_email(edition, media, *, web_url, issue_no, date, unsub, legal_name, legal_address,
            img_base="") -> html
  img_base: prefijo para las imagenes (para preview local: ""; para envio: URL hospedada)
"""
from __future__ import annotations

import html as _html
from datetime import datetime
from urllib.parse import quote

from config import BRAND

NAVY, PAPER, INK, MUTED = BRAND["navy"], BRAND["paper"], BRAND["ink"], BRAND["muted"]
G = BRAND["grad"]


def _e(s):
    return _html.escape(s or "", quote=True)


def _grad():
    return f"linear-gradient(90deg,{G[0]} 0%,{G[1]} 35%,{G[2]} 68%,{G[3]} 100%)"


def _link(web_url, issue_no, slug):
    sep = "&" if "?" in web_url else "?"
    utm = (f"{sep}utm_source=inmersivo&utm_medium=email&utm_campaign=issue-{issue_no}"
           f"&utm_content={quote(slug)}")
    anchor = f"#{slug}" if slug else ""
    return f"{web_url}{utm}{anchor}"


def _img(src, base, radius=10):
    full = (base + src) if (base and not src.startswith("http")) else src
    return (f'<img src="{_e(full)}" width="536" alt="" '
            f'style="width:100%;max-width:536px;height:auto;display:block;border-radius:{radius}px;">')


def _btn(label, href, solid=True):
    if solid:
        bg = f"background:{_grad()};background-color:{G[1]};color:#fff;"
    else:
        bg = f"background:{PAPER};color:{NAVY};border:1.5px solid {G[1]};"
    return (f'<a href="{_e(href)}" target="_blank" rel="noopener noreferrer" '
            f'style="display:inline-block;{bg}text-decoration:none;border-radius:999px;'
            f'padding:12px 26px;font:700 14px/1 Arial,Helvetica,sans-serif;">{_e(label)}</a>')


def _section(sec, media, web_url, issue_no, base):
    slug = sec.get("role", "")
    img_src = media.get("sections", {}).get(slug)
    kicker = _e(sec.get("kicker", ""))
    head = _e(sec.get("headline", ""))
    body = _e(sec.get("body", ""))
    cta = _e(sec.get("cta", "Read more ›"))
    href = _link(web_url, issue_no, slug)
    img_html = (f'<tr><td style="padding:0 0 14px;">{_img(img_src, base)}</td></tr>'
                if img_src else "")
    return f"""
    <tr><td style="padding:26px 32px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="border-top:1px solid #ECEAF3;padding-top:24px;">
        {img_html}
        <tr><td>
          <p style="margin:0 0 6px;font:600 11px/1.4 Arial,Helvetica,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:{MUTED};">{kicker}</p>
          <h2 style="margin:0 0 10px;font:700 21px/1.28 Georgia,'Times New Roman',serif;color:{NAVY};">{head}</h2>
          <p style="margin:0 0 12px;font:400 15px/1.62 Arial,Helvetica,sans-serif;color:{INK};">{body}</p>
          <a href="{_e(href)}" target="_blank" rel="noopener noreferrer"
             style="font:700 13px/1 Arial,Helvetica,sans-serif;color:{G[1]};text-decoration:none;">{cta}</a>
        </td></tr>
      </table>
    </td></tr>"""


def build_email(edition, media, *, web_url, issue_no, date, unsub="{{ unsubscribe }}",
                legal_name="SensaLab", legal_address="Los Angeles, CA, USA",
                img_base="") -> str:
    media = media or {}
    hero = edition["hero"]
    vid = edition.get("video", {})
    inv = edition.get("invitation", {})
    fecha = date.strftime("%d.%m.%Y")
    subject_prev = _e(edition.get("edition_title", ""))

    hero_img = media.get("hero")
    hero_html = f'<tr><td style="padding:0 32px 18px;">{_img(hero_img, img_base, 12)}</td></tr>' if hero_img else ""

    read_full = _btn("Read the full edition →", _link(web_url, issue_no, "hero"))

    sections_html = "".join(_section(s, media, web_url, issue_no, img_base)
                            for s in edition.get("sections", []))

    # bloque de video: poster clickable + play + duracion
    vmedia = media.get("video", {})
    video_html = ""
    if vmedia.get("poster"):
        vlink = vmedia.get("link", web_url)
        video_html = f"""
    <tr><td style="padding:26px 32px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid #ECEAF3;padding-top:24px;">
        <tr><td>
          <p style="margin:0 0 10px;font:600 11px/1.4 Arial,Helvetica,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:{MUTED};">{_e(vid.get('kicker','Watch'))} &middot; {_e(vid.get('duration',''))}</p>
          <a href="{_e(vlink)}" target="_blank" rel="noopener noreferrer" style="text-decoration:none;">{_img(vmedia['poster'], img_base, 12)}</a>
          <h2 style="margin:12px 0 8px;font:700 20px/1.3 Georgia,serif;color:{NAVY};">{_e(vid.get('headline',''))}</h2>
          <p style="margin:0 0 10px;font:400 15px/1.6 Arial,Helvetica,sans-serif;color:{INK};">{_e(vid.get('body',''))}</p>
          <a href="{_e(vlink)}" target="_blank" rel="noopener noreferrer" style="font:700 13px/1 Arial,Helvetica,sans-serif;color:{G[1]};text-decoration:none;">&#9654; Watch the film</a>
        </td></tr>
      </table>
    </td></tr>"""

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><title>{subject_prev}</title></head>
<body style="margin:0;padding:0;background:#EFEDF6;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{_e(hero.get('sub',''))}&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#EFEDF6;">
<tr><td align="center" style="padding:24px 12px;">
  <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background:{PAPER};border-radius:12px;overflow:hidden;">

    <tr><td bgcolor="{G[1]}" style="height:6px;background:{_grad()};line-height:6px;font-size:0;">&nbsp;</td></tr>

    <tr><td style="padding:28px 32px 8px;">
      <table role="presentation" width="100%"><tr>
        <td style="font:700 22px/1 Georgia,serif;letter-spacing:.02em;color:{NAVY};">SENSALAB</td>
        <td align="right" style="font:600 11px/1.4 Arial,Helvetica,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:{MUTED};">INMERSIVO &middot; #{issue_no} &middot; {fecha}</td>
      </tr></table>
      <p style="margin:8px 0 0;font:italic 400 13px/1.4 Georgia,serif;color:{MUTED};">{_e(BRAND['tagline'])}</p>
    </td></tr>

    {hero_html}
    <tr><td style="padding:0 32px;">
      <p style="margin:0 0 6px;font:600 11px/1.4 Arial,Helvetica,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:{MUTED};">{_e(hero.get('kicker',''))}</p>
      <h1 style="margin:0 0 12px;font:700 27px/1.2 Georgia,'Times New Roman',serif;color:{NAVY};">{_e(hero.get('headline',''))}</h1>
      <p style="margin:0 0 18px;font:400 16px/1.6 Arial,Helvetica,sans-serif;color:{INK};">{_e(hero.get('sub',''))}</p>
      <p style="margin:0 0 4px;">{read_full}</p>
    </td></tr>

    {sections_html}
    {video_html}

    <tr><td style="padding:28px 32px 8px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid #ECEAF3;padding-top:22px;">
        <tr><td>
          <p style="margin:0 0 6px;font:600 11px/1.4 Arial,Helvetica,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:{MUTED};">{_e(inv.get('kicker','An open invitation'))}</p>
          <h2 style="margin:0 0 10px;font:700 21px/1.3 Georgia,serif;color:{NAVY};">{_e(inv.get('headline',''))}</h2>
          <p style="margin:0 0 16px;font:400 15px/1.6 Arial,Helvetica,sans-serif;color:{INK};">{_e(inv.get('body',''))}</p>
          <p style="margin:0;">{_btn(inv.get('button','Touch it'), _link(web_url, issue_no, 'invitation'))}</p>
        </td></tr>
      </table>
    </td></tr>

    <tr><td bgcolor="{G[1]}" style="height:5px;background:{_grad()};line-height:5px;font-size:0;margin-top:20px;">&nbsp;</td></tr>
    <tr><td bgcolor="{NAVY}" style="padding:20px 32px 26px;background:{NAVY};">
      <p style="margin:0 0 6px;font:700 13px/1 Georgia,serif;color:#fff;">SensaLab &middot; <span style="font:italic 400 13px/1 Georgia,serif;color:#B9B5D6;">{_e(BRAND['signature'])}</span></p>
      <p style="margin:0 0 10px;font:400 12px/1.5 Arial,Helvetica,sans-serif;color:#B9B5D6;">{_e(BRAND['tagline'])} &middot; <a href="{_e(BRAND['site'])}" style="color:#9FE7FF;text-decoration:none;">sensalab.io</a></p>
      <p style="margin:0;font:400 11px/1.5 Arial,Helvetica,sans-serif;color:#8480A6;">{_e(legal_name)} &middot; {_e(legal_address)} &middot; <a href="{unsub}" style="color:#8480A6;text-decoration:underline;">Unsubscribe</a></p>
    </td></tr>

  </table>
</td></tr>
</table>
</body></html>"""
