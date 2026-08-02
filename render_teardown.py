# -*- coding: utf-8 -*-
"""
Motor del formato TEARDOWN (web, tema CLARO). SIN mayusculas completas; texto SOLO en la
paleta #0B0F0F #F4F3F3 #787878 #1C1956 #E4E4EF. Logo real en masthead.
"""
from __future__ import annotations
import html as _h
import re

from brand_footer import web_footer, web_footer_css

DEFAULT_FONT = "'Helvetica Neue','Aeonik','Neue Haas Grotesk',Arial,system-ui,sans-serif"
NAVY = "#1C1956"; BLACK = "#0B0F0F"; GRAY = "#787878"; PAPER = "#F4F3F3"; LILAC = "#E4E4EF"
LINE = "rgba(28,25,86,.14)"
GRAD = "linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7)"


def _e(s):
    return _h.escape(s or "", quote=True)


def _two_tone(s):
    for sep in (" — ", " – "):
        if sep in s:
            a, b = s.split(sep, 1)
            return _e(a + sep) + f'<span class="g">{_e(b)}</span>'
    m = re.search(r"\.\s+", s)
    if m and m.end() < len(s):
        return _e(s[:m.end()]) + f'<span class="g">{_e(s[m.end():])}</span>'
    return _e(s)


def _verdict(s):
    m = re.search(r"\.\s+", s)
    if m and m.end() < len(s):
        return _e(s[:m.end()]) + f'<span class="r">{_e(s[m.end():])}</span>'
    return _e(s)


def _img(src, base):
    full = (base + src) if (base and src and not src.startswith("http")) else src
    return _e(full or "")


def build_teardown(edition, media, *, issue_no, date, web_url="#",
                   font_stack=DEFAULT_FONT, img_base="", logo="media/sensalab-logo.png") -> str:
    media = media or {}
    td = edition.get("teardown", {}); inv = edition.get("invitation", {})
    sm = media.get("sections", {}); vm = media.get("video", {}); dr = td.get("done_right", {})
    case_img = _img(sm.get(td.get("case_img_role", "craft"), ""), img_base)
    dr_img = _img(sm.get(dr.get("img_role", "field-notes"), ""), img_base)
    dr_html = ""
    if dr:
        dr_img_html = f'<img src="{dr_img}" alt="" loading="lazy">' if dr_img else ""
        dr_html = f"""
  <div class="break x split"><div class="l">Meanwhile, done right</div><p>{_e(dr.get('text',''))}</p></div>
  <div class="frame">{dr_img_html}<div class="shade"></div>
    <div class="tag tag2">Done right &middot; {_e(dr.get('label',''))}</div></div>"""
    video_html = ""
    if vm.get("poster"):
        video_html = f"""
  <div class="split" style="margin-top:34px"><a href="{_e(vm.get('link', web_url))}" target="_blank" rel="noopener" style="text-decoration:none;color:inherit;">
    <div class="frame" style="aspect-ratio:16/9;margin-top:0"><img src="{_img(vm['poster'], img_base)}" alt=""><div class="shade"></div>
      <span class="play"></span><div class="say" style="font-size:22px">{_two_tone(td.get('video_statement','Watch'))}</div></div></a></div>"""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Teardown · SensaLab</title>
<style>
 :root{{--navy:{NAVY};--black:{BLACK};--gray:{GRAY};--paper:{PAPER};--lilac:{LILAC};--line:{LINE};--sans:{font_stack};}}
 *{{box-sizing:border-box;margin:0;padding:0}} body{{background:var(--paper);color:var(--black);font-family:var(--sans);-webkit-font-smoothing:antialiased}}
 .wrap{{max-width:680px;margin:0 auto;padding:0 20px 40px}} .bar{{height:4px;background:{GRAD}}}
 .mast{{display:flex;align-items:center;justify-content:space-between;padding:26px 0 22px}} .logo{{height:30px;width:auto;display:block}}
 .pill{{display:inline-block;border:1px solid rgba(28,25,86,.28);border-radius:999px;padding:6px 13px;font-weight:700;font-size:11px;letter-spacing:.02em;color:var(--gray)}}
 .issue{{font-weight:700;font-size:12px;letter-spacing:.04em;color:var(--gray)}}
 .kick{{font-weight:800;font-size:13px;letter-spacing:.02em;color:var(--navy)}}
 .frame{{position:relative;border-radius:18px;overflow:hidden;aspect-ratio:16/10;border:1px solid var(--line);margin-top:14px;box-shadow:0 12px 34px rgba(28,25,86,.10)}}
 .frame img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
 .frame .shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,15,15,.02) 30%,rgba(11,15,15,.86) 100%)}}
 .frame .tag{{position:absolute;top:14px;left:16px;font-weight:800;font-size:11.5px;letter-spacing:.01em;color:var(--paper);background:{NAVY};border-radius:999px;padding:5px 13px}} .frame .tag2{{background:{GRAY}}}
 .frame .say{{position:absolute;left:22px;right:22px;bottom:20px;font-weight:800;font-size:28px;line-height:1.08;letter-spacing:-.02em;color:var(--paper);text-shadow:0 2px 30px rgba(0,0,0,.4)}} .say .g{{color:var(--lilac)}}
 .verdict{{margin:20px 0 0;font-weight:800;font-size:19px;line-height:1.35;letter-spacing:-.01em;color:var(--black)}} .verdict .r{{color:var(--navy)}}
 .break{{margin-top:26px;padding-left:16px;border-left:2px solid rgba(28,25,86,.16)}} .break.f{{border-color:var(--navy)}} .break.x{{border-color:var(--gray)}}
 .break .l{{font-weight:800;font-size:12px;letter-spacing:.01em;color:var(--gray);margin-bottom:7px}} .break.f .l{{color:var(--navy)}} .break.x .l{{color:var(--gray)}}
 .break p{{color:var(--black);font-size:15.5px;line-height:1.62;font-weight:500}}
 .why{{margin-top:28px;display:flex;gap:12px;align-items:center;background:var(--lilac);border:1px solid rgba(28,25,86,.14);border-radius:14px;padding:16px 18px}}
 .why .lbl{{font-weight:800;font-size:12px;letter-spacing:.01em;color:var(--navy);white-space:nowrap;border-right:1px solid rgba(28,25,86,.18);padding-right:12px}} .why .txt{{font-weight:800;font-size:17px;line-height:1.3;letter-spacing:-.01em;color:var(--navy)}}
 .split{{margin-top:30px}}
 .play{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:72px;height:72px;border-radius:50%;background:rgba(11,15,15,.45);border:2px solid rgba(244,243,243,.92)}}
 .play:after{{content:"";position:absolute;top:50%;left:54%;transform:translate(-50%,-50%);border-left:20px solid {PAPER};border-top:13px solid transparent;border-bottom:13px solid transparent}}
 .invite{{margin-top:44px;border:1px solid var(--line);border-radius:20px;padding:30px 26px;background:#fff;box-shadow:0 12px 34px rgba(28,25,86,.08)}}
 .invite h3{{font-weight:800;font-size:25px;line-height:1.12;letter-spacing:-.02em;color:var(--navy)}} .invite p{{color:var(--gray);font-size:15px;line-height:1.6;margin:12px 0 20px;font-weight:500}}
 .btn{{display:inline-block;background:var(--navy);color:var(--paper);text-decoration:none;font-weight:800;font-size:14px;border-radius:999px;padding:13px 30px}}
 {web_footer_css(NAVY, GRAY, LINE)}
 @media(max-width:520px){{.frame .say{{font-size:22px}}}}
</style></head><body>
<div class="bar"></div>
<div class="wrap">
  <div class="mast"><img class="logo" src="{_img(logo, img_base)}" alt="SensaLab">
    <div style="display:flex;gap:12px;align-items:center;"><span class="issue">Teardown · #{issue_no}</span><span class="pill">sensalab.io</span></div></div>
  <div class="kick">The teardown</div>
  <div class="frame">{('<img src="' + case_img + '" alt="' + _e(td.get('case','')) + '">') if case_img else ''}<div class="shade"></div>
    <div class="tag">Case &middot; {_e(td.get('case',''))}</div><div class="say">{_two_tone(td.get('statement',''))}</div></div>
  <p class="verdict">{_verdict(td.get('verdict',''))}</p>
  <div class="break f"><div class="l">The flaw</div><p>{_e(td.get('flaw',''))}</p></div>
  <div class="break"><div class="l">The principle</div><p>{_e(td.get('principle',''))}</p></div>
  <div class="why"><span class="lbl">Why it matters</span><span class="txt">{_e(td.get('why',''))}</span></div>
  {dr_html}
  {video_html}
  <div class="invite" id="invitation"><h3>{_e(inv.get('headline',''))}</h3><p>{_e(inv.get('body',''))}</p>
    <a class="btn" href="{_e(web_url)}" target="_blank" rel="noopener">{_e(inv.get('button','Touch it'))} →</a></div>
  {web_footer()}
</div></body></html>"""
