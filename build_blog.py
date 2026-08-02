# -*- coding: utf-8 -*-
"""The Signal blog home: full scrollable news sheet (hero + this edition's stories + archive + subscribe)."""
import re, base64, pathlib

BLOG = pathlib.Path(r"C:\Dev\SensaLab-Newsletter-Bot\blog")
FDIR = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\02-Marca\KMR Apparat\KMR Apparat\WEB\WOFF2")
MED  = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\Newsletter\ediciones\2026-08-Signal\substack")

def b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()
def uri(p):
    ext = pathlib.Path(p).suffix.lower().lstrip(".").replace("jpg","jpeg")
    return "data:image/%s;base64,%s" % (ext, b64(p))
def largest_uri(fn):
    t = (BLOG/fn).read_text(encoding="utf-8", errors="replace")
    u = re.findall(r"data:image/[a-zA-Z0-9.+-]+;base64,[A-Za-z0-9+/=]+", t)
    return max(u, key=len) if u else ""

FONT = "".join([
 "@font-face{font-family:'Apparat';font-weight:500;src:url(data:font/woff2;base64,%s) format('woff2')}" % b64(FDIR/"KMR-Apparat-Medium.woff2"),
 "@font-face{font-family:'Apparat';font-weight:700;src:url(data:font/woff2;base64,%s) format('woff2')}" % b64(FDIR/"KMR-Apparat-Bold.woff2"),
 "@font-face{font-family:'Apparat';font-weight:800;src:url(data:font/woff2;base64,%s) format('woff2')}" % b64(FDIR/"KMR-Apparat-Heavy.woff2"),
 "@font-face{font-family:'Apparat';font-weight:900;src:url(data:font/woff2;base64,%s) format('woff2')}" % b64(FDIR/"KMR-Apparat-Black.woff2"),
])
ISO   = uri(MED/"isotipo.png")
HERO  = uri(MED/"hero-led.jpg")

STORIES = [
 ("Field notes","A Hollywood studio bet the lot on virtual production",
  "Tyler Perry Studios is building a virtual production volume with Synapse, LED wall, camera tracking and Unreal, ready by the end of 2026.", uri(MED/"1-tyler-perry-volume.jpg")),
 ("In the lab","Consumer AR glasses opened reservations",
  "Xreal opened paid reservations for the Aura, an Android first pair of XR glasses, with broader phone support later in 2026.", uri(MED/"2-xreal-glasses.jpg")),
 ("Craft","An airline turned a beach into a brand",
  "Southwest brought back Sunset on the Beach, a July event co branded with Coca Cola around America 250.", uri(MED/"3-southwest-beach.jpg")),
]

ARCHIVE = [
 (20,"Edition 20","The week experiential went pro","Tyler Perry's volume, Xreal's Aura, and Southwest on the beach.","signal-20.html"),
 (19,"Edition 19","Presence","Real Madrid, LED volumes, and the growing backlash against AI.","signal-19.html"),
 (18,"Edition 18","Real time","NVIDIA, Unreal, and the Gamescom floor.","signal-18.html"),
 (17,"Edition 17","Immersive","The Sphere, teamLab, and Snap's new Specs.","signal-17.html"),
]
ACOVERS = {n: largest_uri("signal-%d.html" % n) for n,_,_,_,_ in ARCHIVE}

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--ink:#1C1956;--body:#0B0F0F;--paper:#F4F3F3;--lav:#E4E4EF;--mut:#787878;--white:#FFF}
html{scroll-behavior:smooth}
body{font-family:'Apparat','Helvetica Neue',Arial,sans-serif;color:var(--body);background:var(--paper);-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:1120px;margin:0 auto;padding:0 clamp(20px,4vw,44px)}
/* nav */
.nav{position:sticky;top:0;z-index:20;background:rgba(244,243,243,.82);backdrop-filter:saturate(1.3) blur(14px);border-bottom:1px solid var(--lav)}
.nav .wrap{display:flex;align-items:center;justify-content:space-between;height:66px}
.brand{display:flex;align-items:center;gap:9px}
.brand img{height:28px;width:auto}
.brand b{font-weight:800;font-size:20px;letter-spacing:-.01em;color:var(--ink)}
.nav a.sub{background:var(--ink);color:var(--paper);font-weight:800;font-size:13px;padding:11px 20px;border-radius:999px}
/* hero */
.hero{position:relative;height:min(78vh,720px);min-height:460px;overflow:hidden;display:flex;align-items:flex-end}
.hero .bg{position:absolute;inset:0;background:url(__HERO__) center/cover;filter:saturate(1.05)}
.hero .tint{position:absolute;inset:0;mix-blend-mode:screen;opacity:.4;background:radial-gradient(46% 60% at 16% 18%,rgba(50,191,252,.9),transparent 60%),radial-gradient(44% 52% at 90% 12%,rgba(181,92,183,.9),transparent 60%)}
.hero .scrim{position:absolute;inset:0;background:linear-gradient(100deg,rgba(11,15,15,.82) 0%,rgba(11,15,15,.45) 45%,rgba(11,15,15,.15) 65%,rgba(11,15,15,.5) 100%)}
.hero .in{position:relative;z-index:2;padding-bottom:clamp(40px,6vw,64px);max-width:820px;color:var(--paper)}
.ey{display:flex;align-items:center;gap:12px;font-weight:700;font-size:13px;letter-spacing:.16em;color:var(--lav);margin-bottom:18px}
.ey i{width:30px;height:3px;border-radius:2px;background:linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7)}
.hero h1{font-weight:900;font-size:clamp(40px,6vw,84px);line-height:.99;letter-spacing:-.035em;text-shadow:0 6px 50px rgba(0,0,0,.5);max-width:15ch}
.hero p{margin-top:18px;font-weight:500;font-size:clamp(16px,1.6vw,19px);line-height:1.55;color:var(--lav);max-width:52ch}
.pill{display:inline-block;margin-top:26px;background:var(--paper);color:var(--ink);font-weight:800;font-size:15px;padding:14px 30px;border-radius:999px;transition:transform .25s}
.pill:hover{transform:translateY(-2px)}
/* sections */
section.blk{padding:clamp(52px,7vw,86px) 0}
.head{display:flex;align-items:baseline;gap:16px;margin-bottom:30px}
.head h2{font-weight:900;font-size:clamp(26px,3.4vw,40px);letter-spacing:-.02em;color:var(--ink)}
.head .n{font-weight:700;font-size:13px;letter-spacing:.14em;color:var(--mut)}
/* story grid */
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.g2{display:grid;grid-template-columns:repeat(2,1fr);gap:24px}
@media(max-width:860px){.g3{grid-template-columns:1fr}.g2{grid-template-columns:1fr}}
.card{background:var(--white);border-radius:18px;overflow:hidden;box-shadow:0 16px 44px rgba(28,25,86,.09);transition:transform .25s,box-shadow .25s;display:block}
.card:hover{transform:translateY(-4px);box-shadow:0 26px 64px rgba(28,25,86,.15)}
.card .img{height:190px;background-size:cover;background-position:center}
.card .pad{padding:22px 24px 26px}
.ck{display:inline-block;font-weight:800;font-size:11px;letter-spacing:.06em;color:var(--ink);background:var(--lav);border-radius:999px;padding:6px 12px;margin-bottom:14px}
.ck.g{color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7)}
.card h3{font-weight:900;font-size:22px;line-height:1.14;letter-spacing:-.01em;color:var(--ink)}
.card p{margin-top:10px;font-weight:500;font-size:14.5px;line-height:1.55;color:var(--body)}
.card .rd{margin-top:14px;font-weight:800;font-size:13px;color:var(--ink)}
.arch{background:linear-gradient(180deg,#EDECF6,#E8F1FA)}
.arch .card .img{height:150px}
/* subscribe */
.subs{background:#0B0F0F;background-image:linear-gradient(120deg,#1C1956,#3D76E8 55%,#6060BE);color:var(--paper);text-align:center;padding:clamp(56px,8vw,96px) 0}
.subs h2{font-weight:900;font-size:clamp(30px,5vw,52px);letter-spacing:-.025em;max-width:16ch;margin:0 auto}
.subs p{margin:16px auto 26px;font-weight:500;font-size:17px;color:var(--lav);max-width:48ch}
.form{display:flex;gap:10px;justify-content:center;max-width:460px;margin:0 auto;flex-wrap:wrap}
.form input{flex:1;min-width:220px;border:0;border-radius:999px;padding:15px 22px;font:500 15px 'Apparat',Arial,sans-serif}
.form button{border:0;border-radius:999px;padding:15px 28px;font-weight:800;font-size:15px;background:var(--paper);color:var(--ink);cursor:pointer}
/* footer */
.foot{background:var(--paper);padding:40px 0 60px;color:var(--mut);font-size:13px;line-height:1.85}
.foot b{color:var(--ink);font-weight:800;font-size:16px}
.foot a{color:var(--ink)}
"""

stories_html = ""
for ck, h, p, im in STORIES:
    stories_html += ('<a class="card" href="signal-20.html"><div class="img" style="background-image:url(%s)"></div>'
      '<div class="pad"><span class="ck">%s</span><h3>%s</h3><p>%s</p><div class="rd">Read in the edition &#8594;</div></div></a>' % (im, ck, h, p))

arch_html = ""
for n, lb, tt, summ, href in ARCHIVE:
    g = " g" if n == 20 else ""
    lbl = "Latest &middot; " + lb if n == 20 else lb
    arch_html += ('<a class="card" href="%s"><div class="img" style="background-image:url(%s)"></div>'
      '<div class="pad"><span class="ck%s">%s</span><h3>%s</h3><p>%s</p><div class="rd">Read the edition &#8594;</div></div></a>' % (href, ACOVERS[n], g, lbl, tt, summ))

HTML = (
 '<!doctype html><html lang="en"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 '<meta name="color-scheme" content="light only"><title>The Signal, by SensaLab</title>'
 '<style>' + FONT + CSS.replace("__HERO__", HERO) + '</style></head><body>'
 # nav
 '<nav class="nav"><div class="wrap"><a class="brand" href="#top"><img src="' + ISO + '" alt="SensaLab"><b>SensaLab</b></a>'
 '<a class="sub" href="#subscribe">Subscribe</a></div></nav>'
 # hero
 '<header class="hero" id="top"><div class="bg"></div><div class="tint"></div><div class="scrim"></div>'
 '<div class="wrap"><div class="in"><div class="ey"><i></i>The Signal &middot; Edition 20 &middot; Los Angeles</div>'
 '<h1>The week experiential went pro</h1>'
 '<p>A Hollywood studio built a volume, consumer AR glasses opened reservations, and a major airline turned a beach into a brand. Same bet: put people inside it.</p>'
 '<a class="pill" href="signal-20.html">Read the edition &#8594;</a></div></div></header>'
 # this edition
 '<section class="blk"><div class="wrap"><div class="head"><h2>In this edition</h2><span class="n">Three signals this week</span></div>'
 '<div class="g3">' + stories_html + '</div></div></section>'
 # archive
 '<section class="blk arch"><div class="wrap"><div class="head"><h2>The archive</h2><span class="n">Every edition of The Signal</span></div>'
 '<div class="g2">' + arch_html + '</div></div></section>'
 # subscribe
 '<section class="subs" id="subscribe"><div class="wrap"><h2>Put people inside the brand</h2>'
 '<p>The signals in experiential worth your week. Three real moves, every other week, with the why it matters for your work.</p>'
 '<form class="form" onsubmit="return false"><input type="email" placeholder="you@studio.com"><button>Subscribe</button></form></div></section>'
 # footer
 '<footer class="foot"><div class="wrap"><p><b>SensaLab</b></p>'
 '<p>Rendering Experiences is the principle that guides everything we do. We turn ideas into emotional, immersive and measurable realities. From Los Angeles.</p>'
 '<p style="margin-top:10px"><a href="https://instagram.com/sensalab">Instagram</a> &middot; <a href="https://www.linkedin.com/company/sensalab">LinkedIn</a> &middot; <a href="https://youtube.com/@sensalab">Youtube</a></p>'
 '<p style="margin-top:8px">&#169; 2026 SensaLab, Inc. &middot; Los Angeles, CA, USA &middot; <a href="mailto:hello@sensalab.io">hello@sensalab.io</a></p>'
 '</div></footer></body></html>'
)

BLOG.mkdir(parents=True, exist_ok=True)
(BLOG/"index.html").write_text(HTML, encoding="utf-8")
print("wrote", BLOG/"index.html", len(HTML)//1024, "KB")
