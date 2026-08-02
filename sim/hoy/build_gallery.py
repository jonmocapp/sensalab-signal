# -*- coding: utf-8 -*-
"""
Genera un preview visual (una sola pagina self-contained) de las 4 ediciones de hoy,
siguiendo el sistema de marca SensaLab: solo tema claro, paleta de 5 colores para texto,
sentence case, lazo (gradiente) solo en la barra, logo real embebido como data URI.
Lee los JSON reales de sim/hoy/ -> el contenido es el que produce el motor.
"""
import base64
import glob
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
LOGO = os.path.join(ROOT, "sim", "out", "media", "sensalab-logo.png")

FECHA = "27.07.2026"


def esc(s):
    return html.escape(s or "", quote=True)


def logo_uri():
    with open(LOGO, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def frame(tag, statement, kind="signal"):
    """Bloque visual (donde va la capa de arte del otro bot). Navy tonal + statement en paper."""
    return f"""
      <div class="frame frame--{kind}">
        <span class="frame__tag">{esc(tag)}</span>
        <span class="frame__note">visual — capa de arte</span>
        <p class="frame__say">{esc(statement)}</p>
      </div>"""


def why(text):
    if not text:
        return ""
    return f"""
      <div class="why"><span class="why__lbl">Why it matters</span><span class="why__txt">{esc(text)}</span></div>"""


def card(sec):
    return f"""
    <div class="card">
      {frame(sec.get('role',''), sec.get('statement') or sec.get('headline',''))}
      <p class="body">{esc(sec.get('body',''))}</p>
      {why(sec.get('why',''))}
      <span class="cta">{esc((sec.get('cta','Read more →')).replace('›','→'))}</span>
    </div>"""


def signal_body(ed):
    return "".join(card(s) for s in ed.get("sections", []))


def teardown_body(ed):
    td = ed.get("teardown", {})
    dr = td.get("done_right", {})
    dr_html = ""
    if dr:
        dr_html = f"""
    <div class="block block--dr"><span class="block__lbl">Meanwhile, done right</span>
      <p class="body">{esc(dr.get('text',''))}</p>
      <span class="dr-tag">Done right · {esc(dr.get('label',''))}</span></div>"""
    return f"""
    <div class="card">
      {frame('Case · ' + td.get('case',''), td.get('statement',''), kind='teardown')}
      <p class="verdict">{esc(td.get('verdict',''))}</p>
      <div class="block block--flaw"><span class="block__lbl">The flaw</span><p class="body">{esc(td.get('flaw',''))}</p></div>
      <div class="block"><span class="block__lbl">The principle</span><p class="body">{esc(td.get('principle',''))}</p></div>
      {why(td.get('why',''))}
      {dr_html}
    </div>"""


def edition(ed):
    fmt = (ed.get("format") or "signal").lower()
    is_td = fmt == "teardown"
    badge = "Teardown" if is_td else "The Signal"
    hero = ed.get("hero", {})
    inv = ed.get("invitation", {})
    body = teardown_body(ed) if is_td else signal_body(ed)
    return f"""
  <article class="ed">
    <div class="ed__head">
      <span class="badge badge--{'td' if is_td else 'signal'}"><i class="dot"></i>{esc(badge)}</span>
      <span class="issue">#{esc(str(ed.get('issue_no','')))} &middot; {FECHA}</span>
    </div>
    <div class="kicker">{esc(hero.get('kicker',''))}</div>
    <h2 class="hero">{esc(hero.get('statement') or hero.get('headline',''))}</h2>
    <p class="sub">{esc(hero.get('sub',''))}</p>
    {body}
    <div class="invite">
      <h3>{esc(inv.get('headline',''))}</h3>
      <p>{esc(inv.get('body',''))}</p>
      <span class="btn">{esc(inv.get('button','Touch it'))} →</span>
    </div>
  </article>"""


CSS = """
:root{
  --paper:#F4F3F3; --ink:#0B0F0F; --navy:#1C1956; --gray:#787878; --lilac:#E4E4EF;
  --card:#FFFFFF; --line:rgba(28,25,86,.14);
  --lazo:linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7);
  --sans:'Helvetica Neue','Aeonik','Neue Haas Grotesk',Arial,system-ui,sans-serif;
}
/* Marca SensaLab: comprometido a tema CLARO (Jon: "solo claras"). No invertimos. */
:root[data-theme="dark"]{ color-scheme:light; }
*{box-sizing:border-box;margin:0;padding:0}
html{color-scheme:light}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased;line-height:1.5}
.bar{height:4px;background:var(--lazo)}
.wrap{max-width:720px;margin:0 auto;padding:0 20px 80px}

/* ---- masthead / intro a Jon ---- */
.top{display:flex;align-items:center;justify-content:space-between;padding:30px 0 22px;gap:16px;flex-wrap:wrap}
.top img{height:30px;width:auto;display:block}
.top .site{font-weight:700;font-size:11px;color:var(--gray);border:1px solid rgba(28,25,86,.28);border-radius:999px;padding:6px 13px}
.lede{border-top:1px solid var(--line);padding-top:26px;margin-bottom:8px}
.lede h1{color:var(--navy);font-size:clamp(26px,5vw,34px);line-height:1.1;letter-spacing:-.02em;text-wrap:balance;font-weight:800}
.lede p{color:var(--gray);font-size:15.5px;line-height:1.6;margin-top:12px;max-width:60ch}
.lede .meta{margin-top:16px;display:flex;gap:8px;flex-wrap:wrap}
.chip{font-size:12px;font-weight:700;color:var(--navy);background:var(--lilac);border:1px solid var(--line);border-radius:999px;padding:6px 12px}

/* ---- edicion ---- */
.ed{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:34px 30px;margin-top:34px;
    box-shadow:0 14px 40px rgba(28,25,86,.09)}
.ed__head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:20px}
.badge{display:inline-flex;align-items:center;gap:8px;font-weight:800;font-size:12.5px;border-radius:999px;padding:7px 14px}
.badge .dot{width:8px;height:8px;border-radius:50%;background:var(--lazo)}
.badge--signal{color:var(--navy);border:1px solid rgba(28,25,86,.35)}
.badge--td{color:var(--paper);background:var(--navy)}
.badge--td .dot{background:var(--lilac)}
.issue{font-weight:700;font-size:12px;color:var(--gray)}
.kicker{font-weight:800;font-size:13px;color:var(--navy)}
.hero{color:var(--navy);font-size:clamp(24px,4.4vw,31px);line-height:1.12;letter-spacing:-.02em;text-wrap:balance;margin:8px 0 4px;font-weight:800}
.sub{color:var(--gray);font-size:15.5px;line-height:1.62;margin-top:12px;font-weight:500}

/* ---- card / frame ---- */
.card{margin-top:30px;padding-top:30px;border-top:1px solid var(--line)}
.card:first-of-type{border-top:none}
.frame{position:relative;border-radius:16px;overflow:hidden;aspect-ratio:16/9;
  background:linear-gradient(150deg,#232063,#1C1956 42%,#0B0F0F);
  border:1px solid var(--line);box-shadow:0 10px 30px rgba(28,25,86,.14);display:flex;align-items:flex-end}
.frame--teardown{background:linear-gradient(150deg,#1C1956,#0B0F0F 70%)}
.frame__tag{position:absolute;top:14px;left:15px;font-weight:800;font-size:11.5px;color:var(--paper);
  background:rgba(11,15,15,.34);border:1px solid rgba(244,243,243,.28);border-radius:999px;padding:5px 12px}
.frame__note{position:absolute;top:15px;right:15px;font-size:10.5px;font-weight:600;color:rgba(244,243,243,.62)}
.frame__say{padding:20px 22px;font-weight:800;font-size:clamp(20px,3.6vw,26px);line-height:1.1;letter-spacing:-.02em;
  color:var(--paper);text-shadow:0 2px 26px rgba(0,0,0,.4)}
.body{color:var(--ink);font-size:15px;line-height:1.62;font-weight:500;margin-top:16px}
.verdict{color:var(--ink);font-size:18px;line-height:1.36;font-weight:800;letter-spacing:-.01em;margin-top:20px}

/* ---- why it matters ---- */
.why{margin-top:15px;display:flex;gap:12px;align-items:center;background:var(--lilac);
  border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.why__lbl{font-weight:800;font-size:12px;color:var(--navy);white-space:nowrap;border-right:1px solid rgba(28,25,86,.2);padding-right:12px}
.why__txt{font-weight:700;font-size:15px;line-height:1.35;letter-spacing:-.01em;color:var(--navy)}
.cta{display:inline-block;margin-top:14px;color:var(--navy);font-weight:700;font-size:13.5px;border-bottom:1.5px solid var(--navy);padding-bottom:1px}

/* ---- teardown blocks ---- */
.block{margin-top:20px;padding-left:16px;border-left:2px solid rgba(28,25,86,.18)}
.block--flaw{border-color:var(--navy)}
.block--dr{border-color:var(--gray)}
.block__lbl{font-weight:800;font-size:12px;color:var(--gray)}
.block--flaw .block__lbl{color:var(--navy)}
.dr-tag{display:inline-block;margin-top:10px;font-weight:800;font-size:11.5px;color:var(--paper);background:var(--gray);border-radius:999px;padding:5px 12px}

/* ---- invite ---- */
.invite{margin-top:30px;border:1px solid var(--line);border-radius:18px;padding:26px;background:#FBFAFE}
.invite h3{color:var(--navy);font-size:22px;line-height:1.14;letter-spacing:-.02em;font-weight:800}
.invite p{color:var(--gray);font-size:15px;line-height:1.6;margin:12px 0 18px;font-weight:500}
.btn{display:inline-block;background:var(--navy);color:var(--paper);font-weight:800;font-size:14px;border-radius:999px;padding:13px 28px}

.foot{margin-top:44px;color:var(--gray);font-size:12px;line-height:1.7;text-align:center}

@media(prefers-reduced-motion:no-preference){
  .ed{opacity:0;transform:translateY(14px);animation:rise .6s ease forwards}
  .ed:nth-child(2){animation-delay:.05s}.ed:nth-child(3){animation-delay:.1s}.ed:nth-child(4){animation-delay:.15s}
  @keyframes rise{to{opacity:1;transform:none}}
}
"""


def build():
    eds = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(HERE, "ed*.json")))]
    editions_html = "".join(edition(e) for e in eds)
    n_sig = sum(1 for e in eds if (e.get("format") or "signal") != "teardown")
    n_td = len(eds) - n_sig
    html_doc = f"""<title>SensaLab · 4 ediciones de prueba</title>
<div class="bar"></div>
<div class="wrap">
  <div class="top">
    <img src="{logo_uri()}" alt="SensaLab">
    <span class="site">sensalab.io</span>
  </div>
  <div class="lede">
    <h1>Cuatro ediciones, armadas por el motor con noticias reales de esta semana</h1>
    <p>Cada una salió del cerebro editorial (sin LLM para decidir): pasó el candado legal, el validador de esquema, y el motor eligió el formato. {n_sig} en formato <b>The Signal</b> (digest de insights) y {n_td} en <b>Teardown</b> (disección de un caso). Los bloques oscuros son donde entra la capa de arte del otro bot.</p>
    <div class="meta">
      <span class="chip">SIGGRAPH 2026</span><span class="chip">Wevr · The Blu Taiwan</span>
      <span class="chip">A.R. Rahman · Vision Pro</span><span class="chip">Experiential $128B</span>
      <span class="chip">Virtual production</span><span class="chip">AWE · Long Beach</span>
    </div>
  </div>
  {editions_html}
  <p class="foot">© 2026 SensaLab, Inc. &middot; Los Angeles, CA — USA &middot; hello@sensalab.io<br>
  Preview interno — contenido en inglés (como se envía); marco en español.</p>
</div>"""
    out = os.path.join(HERE, "preview.html")
    open(out, "w", encoding="utf-8").write("<style>" + CSS + "</style>\n" + html_doc)
    print("preview ->", out, f"({n_sig} signal + {n_td} teardown)")


if __name__ == "__main__":
    build()
