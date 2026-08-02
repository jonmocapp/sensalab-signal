# -*- coding: utf-8 -*-
"""Individual article pages for The Signal. Rich editorial layout: kicker, H1, hero image, dek,
subheads + paragraphs (with resolved internal links), takeaway box, why-it-matters callout,
in-article email capture + category kit, hire band, next story. Reading chrome + SEO BlogPosting."""
import json, re, html, pathlib
from signal_content import BLOG, FONT, ISO, STORIES, BY_SLUG, DATE, KITS, COVERS2

DEST = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\Newsletter\blog")
BASE = "https://signal.sensalab.io"
def art(slug): return "article-%s.html" % slug
KIT_NAMES = {k[0] for k in KITS}
KIT_ID = {kid: name for name, cls, kid, title, blurb in KITS}   # k1->retail...
KITCAT = {"Experiential":"activations","AI":"activations","Interactive":"activations",
 "CGI & VFX":"shows","Gaming":"shows","Concert visuals":"shows","Spatial & AR":"retail"}
CATTOK = {"Experiential":"experiential","Spatial & AR":"spatial","CGI & VFX":"cgi","AI":"ai",
 "Gaming":"gaming","Interactive":"interactive","Concert visuals":"concerts"}
PLAUSIBLE = '<script defer data-domain="signal.sensalab.io" src="https://plausible.io/js/script.js"></script>'

def resolve(target):
    t = target.strip().lstrip("/")
    if t.startswith("signal/"): t = t[7:]
    if t.startswith("kits/"):
        name = t[5:].strip("/");  return "kit-%s.html" % name if name in KIT_NAMES else "index.html#kit"
    if t in KIT_ID: return "kit-%s.html" % KIT_ID[t]
    if t in KIT_NAMES: return "kit-%s.html" % t
    if t in BY_SLUG: return art(t)
    if t.startswith("#") or t.startswith("http"): return target
    return "index.html"

def linkify(text):
    # escape, then convert [label](target) markdown links to anchors
    def repl(m):
        label, tgt = m.group(1), m.group(2)
        return '<a href="%s">%s</a>' % (resolve(tgt), html.escape(label))
    parts = re.split(r'(\[[^\]]+\]\([^)]+\))', text)
    out = []
    for p in parts:
        m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', p)
        out.append(repl(m) if m else html.escape(p))
    return "".join(out)

CSS = r"""
*{margin:0;padding:0;box-sizing:border-box}
:root{--ink:#1C1956;--body:#0B0F0F;--paper:#F4F3F3;--lav:#E4E4EF;--mut:#787878;--glass:rgba(255,255,255,.58);--gline:rgba(255,255,255,.7)}
html{scroll-behavior:smooth}
body{font-family:'Apparat','Helvetica Neue',Arial,sans-serif;color:var(--body);background:#EEF1FB;-webkit-font-smoothing:antialiased;overflow-x:hidden}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%}
:focus-visible{outline:3px solid #3D76E8;outline-offset:2px;border-radius:6px}
.skip{position:absolute;left:-9999px;top:8px;z-index:1000;background:#1C1956;color:#F4F3F3;padding:10px 16px;border-radius:999px;font-weight:800;font-size:13px}
.skip:focus{left:16px}
.bg{position:fixed;inset:0;overflow:hidden;z-index:0;pointer-events:none}
.blob{position:absolute;border-radius:50%;filter:blur(72px);opacity:.4;pointer-events:none}
.b1{width:48vw;height:48vw;left:-16vw;top:-14vw;background:radial-gradient(circle,#32BFFC,transparent 62%)}
.b2{width:44vw;height:44vw;right:-14vw;top:10vw;background:radial-gradient(circle,#B55CB7,transparent 62%)}
main,footer{position:relative;z-index:1}
.prog{position:fixed;top:0;left:0;height:3px;width:0;z-index:99999;background:linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7)}
.chrome{position:fixed;top:16px;left:0;right:0;z-index:9999;display:flex;justify-content:space-between;padding:0 18px;pointer-events:none}
.chrome a{pointer-events:auto}
.sigback,.sigwork{font:800 13px/1 'Apparat',Arial,sans-serif;padding:11px 18px;border-radius:999px;transition:transform .2s;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.sigback{background:rgba(255,255,255,.78);color:#1C1956;border:1px solid rgba(255,255,255,.85);box-shadow:0 8px 24px rgba(28,25,86,.16)}
.sigwork{color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7);box-shadow:0 8px 24px rgba(96,96,190,.4)}
.sigback:hover,.sigwork:hover{transform:translateY(-2px)}
@media(max-width:600px){.sigback,.sigwork{font-size:12px;padding:9px 14px}}
.ahero{max-width:820px;margin:0 auto;padding:104px 22px 0}
.crumb{font-weight:700;font-size:12px;letter-spacing:.04em;color:var(--mut);margin-bottom:18px}
.crumb a{color:var(--ink)}.crumb a:hover{opacity:.7}
.kicker{display:inline-flex;align-items:center;gap:10px;font-weight:800;font-size:12px;letter-spacing:.14em;color:var(--ink);opacity:.78;margin-bottom:14px}
.kicker i{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#32BFFC,#B55CB7)}
h1.at{font-weight:900;font-size:clamp(28px,4.2vw,46px);line-height:1.07;letter-spacing:-.03em;color:var(--ink);max-width:20ch}
.ameta{margin-top:16px;font-weight:700;font-size:13px;letter-spacing:.03em;color:var(--ink);opacity:.85}
.ameta .sep{opacity:.4;margin:0 8px}
.aimg{max-width:980px;margin:28px auto 0;padding:0 22px}
.aimg img{width:100%;height:clamp(300px,44vw,480px);object-fit:cover;border-radius:24px;box-shadow:0 30px 74px rgba(28,25,86,.22)}
.abody{max-width:720px;margin:0 auto;padding:34px 22px 0}
.abody .dek{font-weight:700;font-size:clamp(19px,2.1vw,23px);line-height:1.5;color:var(--ink);margin-bottom:26px;letter-spacing:-.01em}
.abody h2{font-weight:900;font-size:clamp(21px,2.5vw,27px);line-height:1.2;letter-spacing:-.02em;color:var(--ink);margin:34px 0 14px}
.abody p{font-weight:500;font-size:17px;line-height:1.78;color:var(--body);margin-bottom:20px}
.abody a{color:#1C1956;font-weight:700;border-bottom:2px solid rgba(28,25,86,.22)}
.abody a:hover{border-color:#1C1956}
.aimg2{margin:30px 0}
.aimg2 img{width:100%;height:clamp(220px,32vw,340px);object-fit:cover;border-radius:18px;box-shadow:0 20px 50px rgba(28,25,86,.16)}
.takeaway{max-width:720px;margin:34px auto 0;padding:0 22px}
.takeaway .in{background:linear-gradient(120deg,#1C1956,#3D76E8 60%,#6060BE);color:#F4F3F3;border-radius:20px;padding:26px 30px}
.takeaway .k{display:block;font-weight:800;font-size:11px;letter-spacing:.14em;color:#E4E4EF;margin-bottom:8px}
.takeaway p{font-weight:800;font-size:19px;line-height:1.45;letter-spacing:-.01em;margin:0}
.callout{max-width:720px;margin:22px auto 0;padding:0 22px}
.callout .in{display:flex;gap:16px;padding:22px 24px;background:var(--glass);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid var(--gline);border-radius:18px;box-shadow:0 16px 44px rgba(28,25,86,.10)}
.callout .bar{width:5px;border-radius:3px;background:linear-gradient(180deg,#32BFFC,#B55CB7);flex:none}
.callout .k{font-weight:800;font-size:11px;letter-spacing:.12em;color:var(--mut);display:block;margin-bottom:6px}
.callout p{font-weight:800;font-size:17px;line-height:1.45;color:var(--ink);margin:0;letter-spacing:-.01em}
.src{max-width:720px;margin:24px auto 0;padding:0 22px;font-weight:600;font-size:14px;color:var(--mut)}
.src a{color:#1C1956;font-weight:800;border-bottom:2px solid rgba(28,25,86,.28)}
/* in-article capture */
.acap{max-width:820px;margin:44px auto 0;padding:0 22px}
.acap .in{background:var(--glass);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid var(--gline);border-radius:22px;box-shadow:0 18px 50px rgba(28,25,86,.10);padding:clamp(26px,4vw,38px);text-align:center}
.acap h3{font-weight:900;font-size:clamp(21px,2.6vw,28px);letter-spacing:-.02em;color:var(--ink);max-width:22ch;margin:0 auto}
.acap p.s{margin:12px auto 20px;font-weight:500;font-size:15px;color:var(--mut);max-width:44ch}
.aform{display:flex;gap:10px;justify-content:center;max-width:460px;margin:0 auto;flex-wrap:wrap}
.aform input[type=email]{flex:1;min-width:200px;border:1px solid rgba(28,25,86,.16);border-radius:999px;padding:14px 20px;font:500 15px 'Apparat',Arial,sans-serif;background:rgba(255,255,255,.75);outline:none}
.aform input[type=email]:focus{border-color:#6060BE;box-shadow:0 0 0 4px rgba(96,96,190,.16)}
.aform button{border:0;border-radius:999px;padding:14px 26px;font-weight:800;font-size:15px;color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7);cursor:pointer;transition:transform .2s}
.aform button:hover{transform:translateY(-2px)}
.hp{position:absolute;left:-5000px}
.okmsg{display:none;font-weight:800;font-size:16px;color:var(--ink);padding:6px 0}
.acap .kitline{margin-top:16px;font-weight:700;font-size:14px;color:var(--ink)}
.acap .kitline a{border-bottom:2px solid rgba(28,25,86,.28)}
/* hire */
.hire{max-width:1000px;margin:48px auto 0;padding:0 22px}
.hire .in{border-radius:28px;color:#F4F3F3;background:linear-gradient(120deg,#1C1956,#3D76E8 52%,#6060BE);padding:clamp(40px,5vw,62px) clamp(24px,4vw,52px);text-align:center}
.hire h2{font-weight:900;font-size:clamp(26px,3.4vw,40px);letter-spacing:-.025em;max-width:20ch;margin:0 auto}
.hire p{margin:14px auto 24px;font-weight:500;font-size:16px;color:#E4E4EF;max-width:48ch;line-height:1.55}
.hire a.cta{display:inline-block;background:#F4F3F3;color:#1C1956;font-weight:800;font-size:16px;padding:15px 32px;border-radius:999px;transition:transform .2s}
.hire a.cta:hover{transform:translateY(-2px)}
/* next */
.next{max-width:1000px;margin:22px auto 0;padding:0 22px}
.next a{display:flex;align-items:center;justify-content:space-between;gap:16px;background:var(--glass);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid var(--gline);border-radius:22px;padding:24px 30px;transition:transform .25s,box-shadow .25s}
.next a:hover{transform:translateY(-3px);box-shadow:0 26px 60px rgba(28,25,86,.16)}
.next .l{font-weight:700;font-size:12px;letter-spacing:.1em;color:var(--mut);display:block;margin-bottom:6px}
.next .t{font-weight:900;font-size:clamp(18px,2.1vw,23px);letter-spacing:-.02em;color:var(--ink);line-height:1.15}
.next .arrow{flex:none;font:800 26px/1 Arial;color:var(--ink)}
.foot{max-width:980px;margin:54px auto 0;padding:40px 22px 60px;color:var(--mut);font-size:13px;line-height:1.9}
.foot b{color:var(--ink);font-weight:800;font-size:16px}
.foot a{color:var(--ink)}.foot a:hover{opacity:.7}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
"""

JS = ("addEventListener('scroll',function(){var h=document.documentElement,d=(h.scrollHeight-h.clientHeight);"
 "var p=document.querySelector('.prog');if(p)p.style.width=(d>0?h.scrollTop/d*100:0)+'%';},{passive:true});"
 "function sigSubmit(form,done){var pre=location.protocol==='file:'||/^(localhost$|127\\.|192\\.168\\.)/.test(location.hostname);"
 "if(pre){done(true);return;}var data=new URLSearchParams(new FormData(form));"
 "fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:data.toString()})"
 ".then(function(r){done(r.ok);}).catch(function(){done(false);});}"
 "document.querySelectorAll('form.aform').forEach(function(f){f.addEventListener('submit',function(e){e.preventDefault();"
 "sigSubmit(f,function(ok){var box=f.parentElement;f.style.display='none';var m=box.querySelector('.okmsg');"
 "m.textContent=ok?\"You're in. Watch your inbox for the next edition.\":\"Something went wrong. Email hello@sensalab.io and we'll add you.\";m.style.display='block';});});});")

def render_body(blocks, midimg=None):
    out = []; sub = 0; placed = False
    fig = '<figure class="aimg2"><img src="%s" alt="" loading="lazy"></figure>' % midimg if midimg else ""
    for b in blocks:
        if b.get("type") == "subhead":
            sub += 1
            if sub == 2 and fig and not placed:
                out.append(fig); placed = True
            out.append("<h2>%s</h2>" % linkify(b["text"]))
        else:
            out.append("<p>%s</p>" % linkify(b["text"]))
    if fig and not placed:
        out.insert(max(1, len(out)-1), fig)
    return "".join(out)

def build(s, nxt):
    ed = s["edition"]; dlabel, diso = DATE[ed]
    url = "%s/%s" % (BASE, art(s["slug"]))
    aimg = "%s/%s" % (BASE, s["img"])      # this article's own cover, for OG/Twitter/schema
    tok = CATTOK.get(s["cat"], "")
    kitcat = KITCAT.get(s["cat"], "activations")
    wc = sum(len(b["text"].split()) for b in s["body"])
    # Atribución a la fuente real (solo notas del Carril 2; las 12 originales no traen source_url).
    src_prefix = ('Source: <a href="%s" target="_blank" rel="noopener">%s &#8599;</a> &middot; '
                  % (html.escape(s["source_url"]), html.escape(s.get("source_name") or "the original"))) if s.get("source_url") else ""
    org = {"@type":["Organization","ProfessionalService"],"@id":BASE+"/#org","name":"SensaLab",
     "alternateName":["Sensa Lab","SensaLab Los Angeles"],"url":"https://sensalab.io/","email":"hello@sensalab.io",
     "logo":"https://signal.sensalab.io/icon-192.png","slogan":"Rendering imagination",
     "address":{"@type":"PostalAddress","addressLocality":"Los Angeles","addressRegion":"CA","addressCountry":"US"},
     "sameAs":["https://instagram.com/sensalab","https://www.linkedin.com/company/sensalab","https://youtube.com/@sensalab"]}
    post = {"@type":"BlogPosting","@id":url+"#post","headline":s["headline"],"description":s["meta"],
     "datePublished":diso,"dateModified":diso,"inLanguage":"en","url":url,"mainEntityOfPage":url,
     "image":aimg,"articleSection":s["cat"],"keywords":s["focus_keyword"],
     "wordCount":wc,"timeRequired":"PT%dM"%s["read_minutes"],
     "author":{"@id":BASE+"/#org"},"publisher":{"@id":BASE+"/#org"},
     "isPartOf":{"@type":"Blog","@id":BASE+"/#blog","name":"The Signal"}}
    crumbs = {"@type":"BreadcrumbList","itemListElement":[
     {"@type":"ListItem","position":1,"name":"The Signal","item":BASE+"/"},
     {"@type":"ListItem","position":2,"name":s["headline"],"item":url}]}
    ld = json.dumps({"@context":"https://schema.org","@graph":[org,post,crumbs]}, ensure_ascii=False)

    head = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
     '<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light only">'
     '<title>%s | The Signal by SensaLab</title>' % html.escape(s["headline"])
     + '<meta name="description" content="%s">' % html.escape(s["meta"])
     + '<link rel="canonical" href="%s">' % url
     + '<meta name="robots" content="index,follow,max-image-preview:large">'
     + '<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png"><link rel="apple-touch-icon" href="apple-touch-icon.png">'
     + '<meta name="author" content="SensaLab"><meta name="publisher" content="SensaLab">'
     + '<meta name="geo.region" content="US-CA"><meta name="geo.placename" content="Los Angeles"><meta name="theme-color" content="#F4F3F3">'
     + '<meta name="keywords" content="%s">' % html.escape(s["focus_keyword"])
     + '<meta property="og:type" content="article"><meta property="og:site_name" content="The Signal by SensaLab">'
     + '<meta property="og:title" content="%s"><meta property="og:description" content="%s">' % (html.escape(s["headline"]), html.escape(s["meta"]))
     + '<meta property="og:url" content="%s"><meta property="og:image" content="%s">' % (url, aimg)
     + '<meta property="article:published_time" content="%s"><meta property="article:section" content="%s">' % (diso, html.escape(s["cat"]))
     + '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s">' % (html.escape(s["headline"]), html.escape(s["meta"]), aimg)
     + PLAUSIBLE
     + '<script type="application/ld+json">%s</script>' % ld
     + '<style>' + FONT + CSS + '</style></head>')

    body = "".join([
     '<body><a class="skip" href="#main">Skip to content</a><div class="prog"></div><div class="bg"><div class="blob b1"></div><div class="blob b2"></div></div>',
     '<div class="chrome"><a class="sigback" href="index.html#latest">&#8592; The Signal</a>',
     '<a class="sigwork" href="work.html">Work with us</a></div>',
     '<main id="main">',
     '<header class="ahero"><nav class="crumb"><a href="index.html">The Signal</a> &rsaquo; <a href="index.html?cat=', tok, '#latest">', s["cat"], '</a></nav>',
     '<span class="kicker"><i></i>', s["cat"], '</span>',
     '<h1 class="at">', html.escape(s["headline"]), '</h1>',
     '<div class="ameta">Edition ', str(ed), '<span class="sep">&middot;</span>', dlabel, '<span class="sep">&middot;</span>', str(s["read_minutes"]), ' min read</div></header>',
     '<div class="aimg"><img src="', s["img"], '" alt="', html.escape(s["headline"]), '"></div>',
     '<article class="abody"><p class="dek">', html.escape(s["dek"]), '</p>', render_body(s["body"], COVERS2.get(s["slug"])), '</article>',
     '<div class="takeaway"><div class="in"><span class="k">Your takeaway</span><p>', html.escape(s["takeaway"]), '</p></div></div>',
     '<div class="callout"><div class="in"><span class="bar"></span><div><span class="k">Why it matters</span><p>', html.escape(s["why"]), '</p></div></div></div>',
     '<p class="src">', src_prefix, 'First published in Edition ', str(ed), ' of The Signal. <a href="index.html#archive">Browse the archive &#8594;</a></p>',
     # in-article capture
     '<section class="acap"><div class="in"><h3>Get moves like this every two weeks</h3>',
     '<p class="s">Real developments in experiential and real time, with a clear read on why they matter. Free, no filler.</p>',
     '<form class="aform" name="signal-subscribe" method="POST" data-netlify="true" netlify-honeypot="bot-field">',
     '<input type="hidden" name="form-name" value="signal-subscribe"><p class="hp"><label>Do not fill <input name="bot-field"></label></p>',
     '<input type="email" name="email" required placeholder="you@studio.com" aria-label="Your email"><button type="submit">Get The Signal</button></form>',
     '<div class="okmsg" role="status"></div>',
     '<p class="kitline">Pitching soon? Grab the <a href="kit-', kitcat, '.html">free ', kitcat, ' idea kit &#8594;</a></p>',
     '</div></section>',
     # hire
     '<section class="hire"><div class="in"><h2>Put people inside your brand</h2>',
     '<p>We build responsive, real time, immersive experiences for agencies and brands, white label, under your name.</p>',
     '<a class="cta" href="work.html">Work with us &#8594;</a></div></section>',
     '<nav class="next"><a href="', art(nxt["slug"]), '"><div><span class="l">Keep reading</span><span class="t">', html.escape(nxt["headline"]), '</span></div><span class="arrow">&#8594;</span></a></nav>',
     '<footer class="foot"><p><b>SensaLab</b></p>',
     '<p>Rendering imagination is the principle that guides everything we do. From Los Angeles.</p>',
     '<p style="margin-top:8px"><a href="https://sensalab.io">sensalab.io</a> &middot; <a href="https://instagram.com/sensalab">Instagram</a> &middot; <a href="https://www.linkedin.com/company/sensalab">LinkedIn</a> &middot; <a href="https://youtube.com/@sensalab">YouTube</a></p>',
     '<p style="margin-top:8px">&#169; 2026 SensaLab &middot; Los Angeles, CA, USA &middot; <a href="mailto:hello@sensalab.io">hello@sensalab.io</a> &middot; <a href="privacy.html">Privacy</a></p></footer>',
     '</main><script>', JS, '</script></body></html>',
    ])
    return head + body

n = 0
for i, s in enumerate(STORIES):
    nxt = STORIES[(i+1) % len(STORIES)]
    htmlout = build(s, nxt)
    (BLOG/art(s["slug"])).write_text(htmlout, encoding="utf-8")
    try: (DEST/art(s["slug"])).write_text(htmlout, encoding="utf-8")
    except Exception: pass
    n += 1
    print("article ->", art(s["slug"]), "(%d KB, %d words)" % (len(htmlout)//1024, sum(len(b['text'].split()) for b in s['body'])))
print("done", n, "articles")
