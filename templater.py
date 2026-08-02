"""
Arma el HTML del correo (email-safe: tablas, CSS inline, 600px, con fallback de fuentes).
Autocontenido: no depende de leer plantillas de OneDrive.
Incluye {$unsubscribe} para cumplir con MailerLite.
"""
from __future__ import annotations

import html
from datetime import datetime

from config import BRAND


def _esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def _gradient_css() -> str:
    g = BRAND["grad"]
    return f"linear-gradient(90deg, {g[0]} 0%, {g[1]} 35%, {g[2]} 68%, {g[3]} 100%)"


def _story_block(story: dict, index: int) -> str:
    head = _esc(story.get("headline", ""))
    source = _esc(story.get("source", ""))
    link = _esc(story.get("link", "#"))
    body = _esc(story.get("body", ""))
    lens = _esc(story.get("lens", ""))
    image = story.get("image", "")  # data URI o URL publica (opcional)
    navy = BRAND["navy"]
    ink = BRAND["ink"]
    muted = BRAND["muted"]

    inner = f"""
          <p style="margin:0 0 6px;font:600 11px/1.4 Arial,Helvetica,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:{muted};">
            {source}
          </p>
          <h2 style="margin:0 0 10px;font:700 20px/1.28 Georgia,'Times New Roman',serif;color:{navy};">
            {head}
          </h2>
          <p style="margin:0 0 14px;font:400 15px/1.62 Arial,Helvetica,sans-serif;color:{ink};">
            {body}
          </p>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                 style="background:#F6F5FB;border-left:3px solid {BRAND['grad'][1]};border-radius:4px;">
            <tr><td style="padding:12px 16px;">
              <p style="margin:0;font:italic 400 14px/1.55 Georgia,serif;color:{navy};">
                {lens}
              </p>
            </td></tr>
          </table>
          <p style="margin:14px 0 26px;">
            <a href="{link}" target="_blank" rel="noopener noreferrer" style="font:600 13px/1 Arial,Helvetica,sans-serif;color:{BRAND['grad'][1]};text-decoration:none;">
              Leer la nota &rarr;
            </a>
          </p>"""

    if image:
        # Miniatura a la izquierda (email-safe: dos columnas en tabla)
        row = f"""
        <tr>
          <td width="112" valign="top" style="padding-right:16px;">
            <img src="{_esc(image)}" width="104" height="104" alt=""
                 style="width:104px;height:104px;border-radius:10px;display:block;
                        border:1px solid #ECEAF3;object-fit:cover;">
          </td>
          <td valign="top">{inner}</td>
        </tr>"""
    else:
        row = f"<tr><td>{inner}</td></tr>"

    return f"""
    <tr><td style="padding:0 32px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid #ECEAF3;padding-top:26px;">
        {row}
      </table>
    </td></tr>"""


def build_html(issue: dict, *, issue_number: int, date: datetime,
               unsub: str = "{$unsubscribe}",
               legal_name: str = "SensaLab",
               legal_address: str = "Los Angeles, CA, USA",
               hero_image: str = "",
               mark_image: str = "") -> str:
    navy = BRAND["navy"]
    paper = BRAND["paper"]
    ink = BRAND["ink"]
    muted = BRAND["muted"]
    subject = _esc(issue.get("subject", "INMERSIVO"))
    preview = _esc(issue.get("preview_text", ""))
    intro = _esc(issue.get("intro", ""))
    signoff = _esc(issue.get("signoff", ""))
    fecha = date.strftime("%d.%m.%Y")

    stories_html = "".join(_story_block(s, i) for i, s in enumerate(issue.get("stories", [])))

    # Marca isotipo (opcional) junto al wordmark
    mark_html = ""
    if mark_image:
        mark_html = (f'<img src="{_esc(mark_image)}" width="30" height="30" alt="" '
                     f'style="width:30px;height:30px;vertical-align:middle;margin-right:9px;'
                     f'border-radius:6px;display:inline-block;">')

    # Banda hero (opcional) debajo de la cabecera
    hero_html = ""
    if hero_image:
        hero_html = f"""
    <tr><td style="padding:6px 32px 4px;">
      <img src="{_esc(hero_image)}" width="536" alt=""
           style="width:100%;max-width:536px;height:auto;border-radius:12px;display:block;">
    </td></tr>"""

    return f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>{subject}</title>
</head>
<body style="margin:0;padding:0;background:#EFEDF6;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{preview}&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#EFEDF6;">
<tr><td align="center" style="padding:24px 12px;">
  <table role="presentation" width="600" cellpadding="0" cellspacing="0"
         style="width:600px;max-width:600px;background:{paper};border-radius:10px;overflow:hidden;">

    <!-- Barra lazo (bgcolor = fallback solido para Outlook) -->
    <tr><td bgcolor="{BRAND['grad'][1]}" style="height:6px;background:{_gradient_css()};line-height:6px;font-size:0;">&nbsp;</td></tr>

    <!-- Cabecera -->
    <tr><td style="padding:30px 32px 10px;">
      <table role="presentation" width="100%"><tr>
        <td style="font:700 22px/1 Georgia,serif;letter-spacing:.02em;color:{navy};">{mark_html}SENSALAB</td>
        <td align="right" style="font:600 11px/1.4 Arial,Helvetica,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:{muted};">
          INMERSIVO &middot; #{issue_number:02d} &middot; {fecha}
        </td>
      </tr></table>
      <p style="margin:8px 0 0;font:italic 400 13px/1.4 Georgia,serif;color:{muted};">{_esc(BRAND['tagline'])}</p>
    </td></tr>
    {hero_html}

    <!-- Intro -->
    <tr><td style="padding:14px 32px 22px;">
      <p style="margin:0;font:400 16px/1.6 Georgia,serif;color:{ink};">{intro}</p>
    </td></tr>

    {stories_html}

    <!-- Cierre -->
    <tr><td style="padding:6px 32px 30px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid #ECEAF3;">
        <tr><td style="padding-top:20px;">
          <p style="margin:0 0 4px;font:italic 400 15px/1.5 Georgia,serif;color:{navy};">{signoff}</p>
          <p style="margin:0;font:600 12px/1.5 Arial,Helvetica,sans-serif;letter-spacing:.06em;color:{muted};">
            {_esc(BRAND['signature'])}
          </p>
        </td></tr>
      </table>
    </td></tr>

    <!-- Footer -->
    <tr><td bgcolor="{BRAND['grad'][1]}" style="height:5px;background:{_gradient_css()};line-height:5px;font-size:0;">&nbsp;</td></tr>
    <tr><td bgcolor="{navy}" style="padding:18px 32px 26px;background:{navy};">
      <p style="margin:0 0 6px;font:700 13px/1 Georgia,serif;color:#fff;">SensaLab</p>
      <p style="margin:0 0 10px;font:400 12px/1.5 Arial,Helvetica,sans-serif;color:#B9B5D6;">
        {_esc(BRAND['tagline'])} &middot; <a href="{_esc(BRAND['site'])}" style="color:#9FE7FF;text-decoration:none;">sensalab.io</a>
      </p>
      <p style="margin:0 0 6px;font:400 11px/1.5 Arial,Helvetica,sans-serif;color:#8480A6;">
        Recibes esto porque te interesa el futuro de las experiencias.
        <a href="{unsub}" style="color:#8480A6;text-decoration:underline;">Cancelar suscripcion</a>.
      </p>
      <p style="margin:0;font:400 11px/1.5 Arial,Helvetica,sans-serif;color:#6B6790;">
        {_esc(legal_name)} &middot; {_esc(legal_address)}
      </p>
    </td></tr>

  </table>
</td></tr>
</table>
</body></html>"""
