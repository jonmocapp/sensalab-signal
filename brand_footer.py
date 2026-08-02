# -*- coding: utf-8 -*-
"""
Footer de marca (info real de sensalab.io). Tema CLARO, sentence case, paleta restringida
(#0B0F0F #F4F3F3 #787878 #1C1956 #E4E4EF).
"""
PRINCIPLE = ("Rendering Experiences is the principle that guides everything we do. "
             "We transform ideas into emotional, immersive and measurable realities by "
             "blending creativity, technology, and human experience.")
LEGAL = "© 2026 SensaLab, Inc. All rights reserved"
LOCATION = "Los Angeles, CA, USA"  # sin guiones: regla de marca (nunca - ni em dash en copy)
EMAIL = "hello@sensalab.io"
SITE = "https://sensalab.io"
SOCIAL = [("Instagram", "https://instagram.com/sensalab"),
          ("LinkedIn", "https://www.linkedin.com/company/sensalab"),
          ("Youtube", "https://youtube.com/@sensalab")]

NAVY = "#1C1956"; GRAY = "#787878"; LINE = "rgba(28,25,86,.14)"


def web_footer(ink=NAVY, mut=GRAY, line=LINE) -> str:
    socials = " &nbsp;·&nbsp; ".join(
        f'<a href="{u}" style="color:{ink};text-decoration:none;">{n}</a>' for n, u in SOCIAL)
    return f"""
  <div class="foot">
    <p class="principle"><b>SensaLab®</b> &nbsp;·&nbsp; {PRINCIPLE}</p>
    <p class="frow">{socials}</p>
    <p class="fmeta">{LEGAL} &nbsp;·&nbsp; {LOCATION} &nbsp;·&nbsp;
      <a href="mailto:{EMAIL}" style="color:{ink};">{EMAIL}</a></p>
  </div>"""


def web_footer_css(ink, mut, line):
    return f"""
 .foot{{margin-top:56px;border-top:1px solid {line};padding-top:26px}}
 .foot .principle{{color:{mut};font-size:13px;line-height:1.65;font-weight:500;max-width:580px}} .foot .principle b{{color:{ink};font-weight:800}}
 .foot .frow{{margin:16px 0 6px;font-weight:700;font-size:12.5px;letter-spacing:.01em}}
 .foot .fmeta{{color:{mut};font-size:11.5px;line-height:1.7}}"""


def email_footer(unsub, ink=NAVY, mut=GRAY, sans="'Helvetica Neue',Arial,sans-serif") -> str:
    socials = " &nbsp;·&nbsp; ".join(
        f'<a href="{u}" style="color:{ink};text-decoration:none;">{n}</a>' for n, u in SOCIAL)
    return f"""
    <tr><td style="padding:30px 32px 30px;">
      <p style="margin:0 0 12px;font:500 12px/1.6 {sans};color:{mut};"><b style="color:{ink};font-weight:800;">SensaLab®</b> &middot; {PRINCIPLE}</p>
      <p style="margin:0 0 10px;font:700 12px/1.5 {sans};">{socials}</p>
      <p style="margin:0;font:400 11px/1.6 {sans};color:{mut};">{LEGAL} &middot; {LOCATION} &middot;
        <a href="mailto:{EMAIL}" style="color:{ink};text-decoration:none;">{EMAIL}</a> &middot;
        <a href="{unsub}" style="color:{mut};text-decoration:underline;">Unsubscribe</a></p>
    </td></tr>"""
