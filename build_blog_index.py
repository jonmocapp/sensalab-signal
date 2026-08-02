# -*- coding: utf-8 -*-
"""Build the static blog index (archive) for The Signal, matching the light b1 look."""
import base64, pathlib

BLOG = pathlib.Path(r"C:\Dev\SensaLab-Newsletter-Bot\blog")
FDIR = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\02-Marca\KMR Apparat\KMR Apparat\WEB\WOFF2")
ISO  = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\Newsletter\ediciones\2026-08-Signal\substack\isotipo.png")

def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

FONT = "".join([
 "@font-face{font-family:'Apparat';font-weight:500;src:url(data:font/woff2;base64,%s) format('woff2')}" % b64(FDIR/"KMR-Apparat-Medium.woff2"),
 "@font-face{font-family:'Apparat';font-weight:700;src:url(data:font/woff2;base64,%s) format('woff2')}" % b64(FDIR/"KMR-Apparat-Bold.woff2"),
 "@font-face{font-family:'Apparat';font-weight:800;src:url(data:font/woff2;base64,%s) format('woff2')}" % b64(FDIR/"KMR-Apparat-Heavy.woff2"),
 "@font-face{font-family:'Apparat';font-weight:900;src:url(data:font/woff2;base64,%s) format('woff2')}" % b64(FDIR/"KMR-Apparat-Black.woff2"),
])
ISOURI = "data:image/png;base64," + b64(ISO)

EDS = [
 ("Latest", "The week experiential went pro",
  "Tyler Perry's virtual production volume, Xreal's Aura glasses, and Southwest on the beach.", "signal-20.html"),
 ("Edition 19", "Presence",
  "Real Madrid, LED volumes, and the growing backlash against AI.", "signal-19.html"),
 ("Edition 18", "Real time",
  "NVIDIA, Unreal, and the Gamescom floor.", "signal-18.html"),
 ("Edition 17", "Immersive",
  "The Sphere, teamLab, and Snap's new Specs.", "signal-17.html"),
]

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--ink:#1C1956;--body:#0B0F0F;--mut:#787878;--paper:#E8F1FA;--lav:#E4E4EF;--white:#FFF}
body{font-family:'Apparat','Helvetica Neue',Arial,sans-serif;background:
  radial-gradient(60% 50% at 12% 0%, rgba(50,191,252,.12), transparent 60%),
  radial-gradient(60% 50% at 92% 4%, rgba(181,92,183,.12), transparent 60%),
  #E8F1FA;color:var(--body);-webkit-font-smoothing:antialiased;min-height:100vh}
.wrap{max-width:1040px;margin:0 auto;padding:0 24px}
header{display:flex;align-items:center;justify-content:space-between;padding:30px 0 10px}
.brand{display:flex;align-items:center;gap:9px}
.brand img{height:30px;width:auto}
.brand b{font-weight:800;font-size:22px;letter-spacing:-.01em;color:var(--ink)}
.mast{font-weight:700;font-size:12px;letter-spacing:.14em;color:var(--mut)}
.hero{padding:40px 0 30px;max-width:760px}
.kick{font-weight:700;font-size:13px;letter-spacing:.14em;color:var(--mut);margin-bottom:14px}
h1{font-weight:900;font-size:clamp(40px,7vw,72px);line-height:1.0;letter-spacing:-.03em;color:var(--ink)}
h1 .g{background:linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.sub{margin-top:18px;font-weight:500;font-size:clamp(16px,2vw,20px);line-height:1.55;color:var(--mut);max-width:56ch}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px;padding:14px 0 10px}
@media(max-width:720px){.grid{grid-template-columns:1fr}}
.card{position:relative;background:var(--white);border-radius:18px;padding:30px 30px 26px;overflow:hidden;
  box-shadow:0 18px 50px rgba(28,25,86,.10);text-decoration:none;display:block;transition:transform .25s ease,box-shadow .25s ease}
.card:hover{transform:translateY(-3px);box-shadow:0 26px 64px rgba(28,25,86,.16)}
.card .bar{position:absolute;left:0;top:0;bottom:0;width:6px;background:linear-gradient(180deg,#32BFFC,#3D76E8,#6060BE,#B55CB7)}
.ck{display:inline-block;font-weight:800;font-size:11px;letter-spacing:.06em;color:var(--ink);
  background:var(--lav);border-radius:999px;padding:6px 12px;margin-bottom:16px}
.ck.latest{color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7)}
.card h2{font-weight:900;font-size:30px;line-height:1.08;letter-spacing:-.02em;color:var(--ink)}
.card p{margin-top:10px;font-weight:500;font-size:15px;line-height:1.55;color:var(--body)}
.card .read{margin-top:16px;font-weight:800;font-size:14px;color:var(--ink)}
.foot{border-top:1px solid var(--lav);margin-top:36px;padding:28px 0 50px;color:var(--mut);font-size:13px;line-height:1.8}
.foot b{color:var(--ink);font-weight:800;font-size:16px}
.foot a{color:var(--ink);text-decoration:none}
"""

cards = ""
for kick, title, summ, href in EDS:
    latest = " latest" if kick == "Latest" else ""
    cards += (
      '<a class="card" href="%s"><span class="bar"></span>'
      '<span class="ck%s">%s</span>'
      '<h2>%s</h2><p>%s</p><div class="read">Read the edition &#8594;</div></a>' % (href, latest, kick, title, summ))

HTML = (
 '<!doctype html><html lang="en"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 '<meta name="color-scheme" content="light only"><title>The Signal, by SensaLab</title>'
 '<style>' + FONT + CSS + '</style></head><body><div class="wrap">'
 '<header><div class="brand"><img src="' + ISOURI + '" alt="SensaLab"><b>SensaLab</b></div>'
 '<div class="mast">The Signal</div></header>'
 '<section class="hero"><div class="kick">Rendering imagination</div>'
 '<h1>The <span class="g">Signal</span></h1>'
 '<p class="sub">The signals in experiential worth your week. Three real moves in immersive and real time experiences, with the why it matters for your work. From SensaLab, in Los Angeles.</p></section>'
 '<section class="grid">' + cards + '</section>'
 '<footer class="foot"><p><b>SensaLab</b></p>'
 '<p>Rendering Experiences is the principle that guides everything we do. We turn ideas into emotional, immersive and measurable realities.</p>'
 '<p style="margin-top:10px"><a href="https://instagram.com/sensalab">Instagram</a> &middot; <a href="https://www.linkedin.com/company/sensalab">LinkedIn</a> &middot; <a href="https://youtube.com/@sensalab">Youtube</a></p>'
 '<p style="margin-top:8px">&#169; 2026 SensaLab, Inc. &middot; Los Angeles, CA, USA &middot; <a href="mailto:hello@sensalab.io">hello@sensalab.io</a></p>'
 '</footer></div></body></html>'
)

BLOG.mkdir(parents=True, exist_ok=True)
(BLOG/"index.html").write_text(HTML, encoding="utf-8")
print("wrote", BLOG/"index.html", len(HTML)//1024, "KB")
