# -*- coding: utf-8 -*-
"""
Motor del formato 'THE SIGNAL' (web, tema CLARO) — tarjetas de insight.
Reglas de marca: SIN mayusculas completas (sentence case); texto SOLO en la paleta
#0B0F0F #F4F3F3 #787878 #1C1956 #E4E4EF. Logo real en el masthead.
"""
from __future__ import annotations
import html as _h
import re

from brand_footer import web_footer, web_footer_css

DEFAULT_FONT = "'Helvetica Neue','Aeonik','Neue Haas Grotesk',Arial,system-ui,sans-serif"
NAVY = "#1C1956"; BLACK = "#0B0F0F"; GRAY = "#787878"; PAPER = "#F4F3F3"; LILAC = "#E4E4EF"
LINE = "rgba(28,25,86,.14)"
GRAD = "linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7)"  # solo la barra de marca


def _e(s):
    return _h.escape(s or "", quote=True)


def _two_tone(s):
    for sep in (" — ", " – "):
        if sep in s:
            a, b = s.split(sep, 1)
            return a + sep, b
    m = re.search(r"\.\s+", s)
    if m and m.end() < len(s):
        return s[:m.end()], s[m.end():]
    return s, ""


def _statement_html(s):
    a, b = _two_tone(s)
    return f"{_e(a)}" + (f'<span class="g">{_e(b)}</span>' if b else "")


def _img(src, base):
    full = (base + src) if (base and src and not src.startswith("http")) else src
    return _e(full or "")


def _card(sec, media, base, web_url, n):
    role = sec.get("role", "")
    img = media.get("sections", {}).get(role, "")
    st = sec.get("statement") or sec.get("headline", "")
    why = sec.get("why", ""); body = sec.get("body", "")
    cta = sec.get("cta", "Read more ›").replace("›", "→")
    why_html = (f'<div class="why"><span class="lbl">Why it matters</span>'
                f'<span class="txt">{_e(why)}</span></div>' if why else "")
    # sin imagen: NO emitir <img src=""> (icono roto + request espurio); el frame queda tonal
    img_html = (f'<img src="{_img(img, base)}" alt="{_e(sec.get("alt") or st)}" loading="lazy">'
                if img else "")
    return f"""
  <div class="card" id="{_e(role)}">
    <div class="frame">{img_html}<div class="shade"></div>
      <div class="num">{n:02d}</div><div class="say">{_statement_html(st)}</div></div>
    <p class="body">{_e(body)}</p>
    {why_html}
    <a class="cta" href="{_e(web_url)}" target="_blank" rel="noopener">{_e(cta)}</a>
  </div>"""


def build_signal(edition, media, *, issue_no, date, web_url="#",
                 font_stack=DEFAULT_FONT, img_base="", logo="media/sensalab-logo.png") -> str:
    media = media or {}
    hero = edition["hero"]; vid = edition.get("video", {}); inv = edition.get("invitation", {})
    vmedia = media.get("video", {})
    cards = "".join(_card(s, media, img_base, web_url, i + 1)
                    for i, s in enumerate(edition.get("sections", [])))
    video_html = ""
    if vmedia.get("poster"):
        video_html = f"""
  <div class="card" id="video"><a href="{_e(vmedia.get('link', web_url))}" target="_blank" rel="noopener" style="text-decoration:none;color:inherit;">
    <div class="frame"><img src="{_img(vmedia['poster'], img_base)}" alt=""><div class="shade"></div>
      <div class="num">&#9654; {_e(vid.get('duration',''))}</div><span class="play"></span>
      <div class="say">{_statement_html(vid.get('statement') or vid.get('headline',''))}</div></div></a>
    <p class="body">{_e(vid.get('body',''))}</p></div>"""
    lede_a, lede_b = _two_tone(hero.get("statement") or hero.get("headline", ""))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>The Signal · SensaLab</title>
<style>
 :root{{--navy:{NAVY};--black:{BLACK};--gray:{GRAY};--paper:{PAPER};--lilac:{LILAC};--line:{LINE};--sans:{font_stack};}}
 *{{box-sizing:border-box;margin:0;padding:0}} body{{background:var(--paper);color:var(--black);font-family:var(--sans);-webkit-font-smoothing:antialiased}}
 .wrap{{max-width:680px;margin:0 auto;padding:0 20px 40px}} .bar{{height:4px;background:{GRAD}}}
 .mast{{display:flex;align-items:center;justify-content:space-between;padding:26px 0 22px}}
 .logo{{height:30px;width:auto;display:block}}
 .pill{{display:inline-block;border:1px solid rgba(28,25,86,.28);border-radius:999px;padding:6px 13px;font-weight:700;font-size:11px;letter-spacing:.02em;color:var(--gray)}}
 .issue{{font-weight:700;font-size:12px;letter-spacing:.04em;color:var(--gray)}}
 .kick{{font-weight:800;font-size:13px;letter-spacing:.02em;color:var(--navy)}}
 .lede{{font-weight:800;font-size:30px;line-height:1.12;letter-spacing:-.02em;margin:10px 0 4px;color:var(--navy)}} .lede .g{{color:var(--gray)}}
 .sub{{color:var(--gray);font-size:15px;line-height:1.6;font-weight:500;margin-top:14px;max-width:560px}}
 .card{{margin-top:40px}}
 .frame{{position:relative;border-radius:18px;overflow:hidden;aspect-ratio:16/11;border:1px solid var(--line);box-shadow:0 12px 34px rgba(28,25,86,.10)}}
 .frame img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
 .frame .shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,15,15,.02) 30%,rgba(11,15,15,.82) 100%)}}
 .frame .num{{position:absolute;top:14px;right:16px;font-weight:800;font-size:12px;color:var(--paper);background:rgba(11,15,15,.42);border:1px solid rgba(244,243,243,.32);border-radius:999px;padding:5px 11px}}
 .frame .say{{position:absolute;left:22px;right:22px;bottom:20px;font-weight:800;font-size:26px;line-height:1.1;letter-spacing:-.02em;color:var(--paper);text-shadow:0 2px 30px rgba(0,0,0,.4)}} .say .g{{color:var(--lilac)}}
 .body{{color:var(--black);font-size:15px;line-height:1.62;font-weight:500;margin:16px 0 0}}
 .why{{margin:14px 0 0;display:flex;gap:12px;align-items:center;background:var(--lilac);border:1px solid rgba(28,25,86,.14);border-radius:14px;padding:14px 16px}}
 .why .lbl{{font-weight:800;font-size:12px;letter-spacing:.01em;color:var(--navy);white-space:nowrap;border-right:1px solid rgba(28,25,86,.18);padding-right:12px}}
 .why .txt{{font-weight:700;font-size:15.5px;line-height:1.35;letter-spacing:-.01em;color:var(--navy)}}
 .cta{{display:inline-block;margin-top:14px;color:var(--navy);font-weight:700;font-size:13.5px;text-decoration:none;border-bottom:1.5px solid var(--navy);padding-bottom:1px}}
 .play{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:76px;height:76px;border-radius:50%;background:rgba(11,15,15,.45);border:2px solid rgba(244,243,243,.92)}}
 .play:after{{content:"";position:absolute;top:50%;left:54%;transform:translate(-50%,-50%);border-left:22px solid {PAPER};border-top:14px solid transparent;border-bottom:14px solid transparent}}
 .invite{{margin-top:44px;border:1px solid var(--line);border-radius:20px;padding:30px 26px;background:#fff;box-shadow:0 12px 34px rgba(28,25,86,.08)}}
 .invite h3{{font-weight:800;font-size:26px;line-height:1.12;letter-spacing:-.02em;color:var(--navy)}} .invite p{{color:var(--gray);font-size:15px;line-height:1.6;margin:12px 0 20px;font-weight:500}}
 .btn{{display:inline-block;background:var(--navy);color:var(--paper);text-decoration:none;font-weight:800;font-size:14px;border-radius:999px;padding:13px 30px}}
 {web_footer_css(NAVY, GRAY, LINE)}
 @media(max-width:520px){{.lede{{font-size:24px}}.frame .say{{font-size:21px}}.invite h3{{font-size:22px}}}}
</style></head><body>
<div class="bar"></div>
<div class="wrap">
  <div class="mast"><img class="logo" src="{_img(logo, img_base)}" alt="SensaLab">
    <div style="display:flex;gap:12px;align-items:center;"><span class="issue">The Signal · #{issue_no}</span><span class="pill">sensalab.io</span></div></div>
  <div class="kick">{_e(hero.get('kicker') or "This week's signal")}</div>
  <h1 class="lede">{_e(lede_a)}<span class="g">{_e(lede_b)}</span></h1>
  <p class="sub">{_e(hero.get('sub',''))}</p>
  {cards}
  {video_html}
  <div class="invite" id="invitation"><h3>{_e(inv.get('headline',''))}</h3><p>{_e(inv.get('body',''))}</p>
    <a class="btn" href="{_e(web_url)}" target="_blank" rel="noopener">{_e(inv.get('button','Touch it'))} →</a></div>
  {web_footer()}
</div></body></html>"""
