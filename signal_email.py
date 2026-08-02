# -*- coding: utf-8 -*-
"""
Email-slim del formato THE SIGNAL (tema CLARO, email-safe). Vehiculo: llega al inbox y
linkea a la web. Tablas + CSS inline + 600px. UTM + target=_blank. Footer real (sensalab.io).
"""
from __future__ import annotations
import html as _h
from urllib.parse import quote

from brand_footer import email_footer

OUT = "#E4E4EF"; CARD = "#FFFFFF"; INK = "#1C1956"; BODY = "#0B0F0F"; MUT = "#787878"
PUR = "#1C1956"; BLU = "#1C1956"; LILAC = "#E4E4EF"
GRAD = "linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7)"  # solo barra de marca
SANS = "'Helvetica Neue',Arial,sans-serif"


def _e(s):
    return _h.escape(s or "", quote=True)


def _url(web, issue, slug):
    sep = "&" if "?" in web else "?"
    return (f"{web}{sep}utm_source=inmersivo&utm_medium=email&utm_campaign=issue-{issue}"
            f"&utm_content={quote(slug)}#{slug}")


def _src(src, base):
    """URL final (escapada) de una imagen: absolutiza contra img_base si es relativa."""
    full = (base + src) if (base and src and not src.startswith("http")) else src
    return _e(full or "")


def _img(src, base):
    return (f'<img src="{_src(src, base)}" width="536" alt="" '
            f'style="width:100%;max-width:536px;height:auto;display:block;border-radius:12px;">')


def _card(sec, media, base, web, issue):
    role = sec.get("role", "")
    img = media.get("sections", {}).get(role, "")
    st = _e(sec.get("statement") or sec.get("headline", ""))
    why = _e(sec.get("why", "")); body = _e(sec.get("body", ""))
    cta = _e((sec.get("cta", "Read more →")).replace("›", "→"))
    href = _url(web, issue, role)
    img_html = f'<tr><td style="padding:0 0 14px;">{_img(img, base)}</td></tr>' if img else ""
    why_html = (f'<tr><td style="padding:12px 0 0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
                f'style="background:{LILAC};border:1px solid rgba(123,77,255,.22);border-radius:12px;"><tr>'
                f'<td style="padding:13px 16px;font:800 12px/1.2 {SANS};letter-spacing:.01em;color:{PUR};white-space:nowrap;">Why it matters</td>'
                f'<td style="padding:13px 16px 13px 0;font:700 15px/1.35 {SANS};color:{INK};">{why}</td>'
                f'</tr></table></td></tr>') if why else ""
    return f"""
    <tr><td style="padding:34px 32px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        {img_html}
        <tr><td><p style="margin:0 0 8px;font:800 22px/1.14 {SANS};letter-spacing:-.01em;color:{INK};">{st}</p>
          <p style="margin:0;font:500 15px/1.6 {SANS};color:{BODY};">{body}</p></td></tr>
        {why_html}
        <tr><td style="padding:12px 0 0;"><a href="{_e(href)}" target="_blank" rel="noopener noreferrer" style="font:700 13px/1 {SANS};color:{BLU};text-decoration:none;">{cta}</a></td></tr>
      </table>
    </td></tr>"""


def build_signal_email(edition, media, *, web_url, issue_no, date, unsub="{{ unsubscribe }}",
                       legal_name="SensaLab", legal_address="Los Angeles, CA, USA", img_base="",
                       logo="media/sensalab-logo.png", format_label="The Signal") -> str:
    media = media or {}
    hero = edition["hero"]; vid = edition.get("video", {}); inv = edition.get("invitation", {})
    vm = media.get("video", {})
    fecha = date.strftime("%d.%m.%Y")
    cards = "".join(_card(s, media, img_base, web_url, issue_no) for s in edition.get("sections", []))
    video_html = ""
    if vm.get("poster"):
        video_html = f"""
    <tr><td style="padding:34px 32px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr><td style="padding:0 0 12px;"><a href="{_e(vm.get('link', web_url))}" target="_blank" rel="noopener noreferrer">{_img(vm['poster'], img_base)}</a></td></tr>
        <tr><td><p style="margin:0 0 8px;font:800 20px/1.2 {SANS};color:{INK};">{_e(vid.get('statement') or vid.get('headline',''))}</p>
          <p style="margin:0 0 8px;font:500 15px/1.6 {SANS};color:{BODY};">{_e(vid.get('body',''))}</p>
          <a href="{_e(vm.get('link', web_url))}" target="_blank" rel="noopener noreferrer" style="font:700 13px/1 {SANS};color:{BLU};text-decoration:none;">&#9654; Watch &middot; {_e(vid.get('duration',''))}</a></td></tr>
      </table></td></tr>"""

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light">
<title>The Signal</title></head>
<body style="margin:0;padding:0;background:{OUT};">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{_e(hero.get('statement',''))}&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" bgcolor="{OUT}" style="background:{OUT};">
<tr><td align="center" style="padding:24px 12px;">
  <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:{CARD};border-radius:14px;overflow:hidden;">
    <tr><td bgcolor="#3D76E8" style="height:4px;background:{GRAD};line-height:4px;font-size:0;">&nbsp;</td></tr>
    <tr><td style="padding:26px 32px 6px;">
      <table role="presentation" width="100%"><tr>
        <td><img src="{_src(logo, img_base)}" height="26" alt="SensaLab" style="height:26px;width:auto;display:block;"></td>
        <td align="right" style="font:700 12px/1.4 {SANS};letter-spacing:.03em;color:{MUT};">{_e(format_label)} &middot; #{issue_no} &middot; {fecha}</td>
      </tr></table>
    </td></tr>
    <tr><td style="padding:14px 32px 0;">
      <p style="margin:0 0 8px;font:800 13px/1.2 {SANS};letter-spacing:.02em;color:{PUR};">{_e(hero.get('kicker') or "This week's signal")}</p>
      <h1 style="margin:0 0 12px;font:800 28px/1.14 {SANS};letter-spacing:-.02em;color:{INK};">{_e(hero.get('statement') or hero.get('headline',''))}</h1>
      <p style="margin:0;font:500 16px/1.6 {SANS};color:{MUT};">{_e(hero.get('sub',''))}</p>
    </td></tr>
    {cards}
    {video_html}
    <tr><td style="padding:36px 32px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F7F5FD;border:1px solid rgba(28,25,86,.12);border-radius:18px;">
        <tr><td style="padding:26px;">
          <h3 style="margin:0 0 10px;font:800 22px/1.16 {SANS};letter-spacing:-.01em;color:{INK};">{_e(inv.get('headline',''))}</h3>
          <p style="margin:0 0 18px;font:500 15px/1.6 {SANS};color:{MUT};">{_e(inv.get('body',''))}</p>
          <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0;"><tr><td bgcolor="{INK}" style="background-color:{INK};border-radius:999px;"><a href="{_e(_url(web_url, issue_no,'invitation'))}" target="_blank" rel="noopener noreferrer" style="display:inline-block;color:#F4F3F3;text-decoration:none;padding:13px 28px;font:800 14px/1 {SANS};">{_e(inv.get('button','Touch it'))} →</a></td></tr></table>
        </td></tr>
      </table></td></tr>
    {email_footer(unsub, ink=INK, mut=MUT, sans=SANS)}
  </table>
</td></tr></table></body></html>"""
