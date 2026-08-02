# -*- coding: utf-8 -*-
"""Free-kit deliverable pages for The Signal. Each kit = 10 concrete, pitchable ideas
(concept + enabling real-time/immersive tech + rough footprint). Self-contained, light, on-brand,
with reading chrome, subscribe capture, hire band and ItemList schema."""
import json, html, pathlib
from signal_content import BLOG, FONT, ISO
DEST = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\Newsletter\blog")
BASE = "https://signal.sensalab.io"

KIT = {
 "retail": dict(title="10 ideas for retail", kw="experiential retail ideas",
   intro="Ten ways to turn a store into a reason to visit, not just a place to buy. Each one pairs a concept with the real time or immersive tech that makes it work, and a rough footprint you can pitch.",
   ideas=[
    ("Endless aisle portal","A feature wall becomes any world the product lives in, so shoppers step inside the brand instead of scanning a shelf. Real time 3D on an LED wall. Footprint: one wall."),
    ("A mirror that dresses you","A smart mirror layers products, colorways and scenes onto the shopper in real time. AR plus body tracking. Footprint: a fitting nook."),
    ("Product origin table","Lift a product and a projection maps the story of how it was made onto the surface. Object recognition plus projection mapping. Footprint: a central table."),
    ("Scent and scene room","A small room where light, sound and real time visuals shift to match a fragrance or a collection. Footprint: a three by three metre room."),
    ("A window that reacts","A storefront scene that notices passers by and reacts, pulling foot traffic through the door. Real time 3D plus presence detection. Footprint: the window."),
    ("Configurator wall","Customers build a product on a giant touch wall and watch it render photoreal in real time. Real time 3D configurator. Footprint: a touch wall."),
    ("Loyalty portal","Members scan in and a personal real time visual greets them and unlocks a moment. App or RFID plus real time graphics. Footprint: the entrance."),
    ("Miniature brand world","A physical diorama that phones reveal in animated AR layers. AR plus a physical set. Footprint: a plinth."),
    ("A photo moment that travels","A designed set with real time generative backdrops, so every shopper leaves with something worth posting. Footprint: a corner."),
    ("Signage that stays alive","Screens whose real time visuals shift with time of day, weather or stock, so nothing ever looks static. Real time 3D plus live data. Footprint: your existing screens."),
   ]),
 "branding": dict(title="10 ideas for branding", kw="immersive brand experience ideas",
   intro="Ten ways to make a brand something people can stand inside, not a logo on a wall. Each pairs a concept with the tech that delivers it.",
   ideas=[
    ("The brand world room","A walk in real time 3D environment that is the brand's universe. LED volume or projection room."),
    ("Origin story tunnel","A corridor of projection mapped scenes that tells the brand story as you walk it. Projection mapping."),
    ("Manifesto in motion","The brand's values as a generative, ever changing installation of light and type. Real time generative visuals."),
    ("A founder's eye AR layer","Point a phone at the space and see the brand's vision overlaid on the real room. AR."),
    ("A sensory signature","A repeatable signature of light, sound and motion the brand can deploy at any event. Real time toolkit."),
    ("Interactive values wall","Visitors choose a value and the wall answers with a tailored scene. Touch plus real time 3D."),
    ("The living logo","The identity rendered as a real time 3D object that reacts to people and sound. Real time 3D."),
    ("Portal between products","A room that transitions seamlessly between product worlds on an LED volume. LED volume."),
    ("A co creation canvas","Visitors add to a shared generative artwork that becomes brand owned content. Generative and multi user."),
    ("A lobby that performs","An arrival installation that greets, informs and impresses. Real time 3D plus presence."),
   ]),
 "activations": dict(title="10 ideas for activations", kw="brand activation ideas",
   intro="Ten launch and event ideas people actually talk about afterward. Each pairs a concept with the tech and the moment it creates.",
   ideas=[
    ("Step inside the teaser","A portable LED volume drops the audience inside the product world at launch. LED volume."),
    ("A reactive floor","A projection or LED floor that responds to where the crowd moves. Sensors plus real time."),
    ("Shoot the hero shot live","Capture the campaign hero shot in a volume, live, in front of the crowd. Virtual production."),
    ("A generative gift","Every attendee leaves with a unique, real time generated piece of content or art. Generative."),
    ("A crowd powered visual","The visuals build from the crowd's phones, movement or votes. Multi user real time."),
    ("An AR scavenger layer","An AR layer across the venue that rewards exploration. AR."),
    ("The mirror moment","A signature capture set with a real time backdrop engineered to be shared. Real time backdrop."),
    ("A portal drop","A doorway that teleports guests from the street into the brand world. LED tunnel."),
    ("A data sculpture","Live event data rendered as a growing real time sculpture on screen. Real time data."),
    ("A second screen companion","A web AR or real time layer so remote audiences join the moment. WebAR."),
   ]),
 "shows": dict(title="10 ideas for shows", kw="concert and show visual ideas",
   intro="Ten ways to make stage visuals the main act, not the backdrop. Each pairs a concept with the tech behind it.",
   ideas=[
    ("A wraparound world","A real time 3D world on the LED wall that shifts with the set. LED wall plus real time."),
    ("A reactive stage","Visuals that respond to music, lighting or performer position in real time. Real time plus tracking."),
    ("A volumetric performer","Capture or extend a performer into the digital world, live. Volumetric plus real time."),
    ("A generative act","A segment where the visuals are generated live and never repeat. Generative."),
    ("An audience lit finale","The crowd's phones or wearables become part of the show's lighting. Networked lighting."),
    ("Camera aware content","Visuals composed for the broadcast and stream camera as much as the room. Virtual production."),
    ("Scene teleports","Instant world changes between songs or segments on the LED volume. Real time 3D."),
    ("An AR extension","An app or WebAR layer that adds a dimension only phones can see. AR."),
    ("Data driven visuals","Set visuals that pull from live inputs, tour data or socials, to feel current. Real time data."),
    ("A pre show world","An immersive lobby world that primes the audience before doors. Projection or LED."),
   ]),
}

CSS = r"""
*{margin:0;padding:0;box-sizing:border-box}
:root{--ink:#1C1956;--body:#0B0F0F;--paper:#F4F3F3;--lav:#E4E4EF;--mut:#787878;--glass:rgba(255,255,255,.58);--gline:rgba(255,255,255,.7)}
html{scroll-behavior:smooth}
body{font-family:'Apparat','Helvetica Neue',Arial,sans-serif;color:var(--body);background:#EEF1FB;-webkit-font-smoothing:antialiased;overflow-x:hidden}
a{color:inherit;text-decoration:none}img{display:block;max-width:100%}
:focus-visible{outline:3px solid #3D76E8;outline-offset:2px;border-radius:6px}
.skip{position:absolute;left:-9999px;top:8px;z-index:1000;background:#1C1956;color:#F4F3F3;padding:10px 16px;border-radius:999px;font-weight:800;font-size:13px}
.skip:focus{left:16px}
.bg{position:fixed;inset:0;overflow:hidden;z-index:0;pointer-events:none}
.blob{position:absolute;border-radius:50%;filter:blur(72px);opacity:.42;pointer-events:none}
.b1{width:50vw;height:50vw;left:-16vw;top:-16vw;background:radial-gradient(circle,#32BFFC,transparent 62%)}
.b2{width:46vw;height:46vw;right:-14vw;bottom:-18vw;background:radial-gradient(circle,#B55CB7,transparent 62%)}
main,footer{position:relative;z-index:1}
.prog{position:fixed;top:0;left:0;height:3px;width:0;z-index:99999;background:linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7)}
.chrome{position:fixed;top:16px;left:0;right:0;z-index:9999;display:flex;justify-content:space-between;padding:0 18px;pointer-events:none}
.chrome a{pointer-events:auto}
.sigback,.sigwork{font:800 13px/1 'Apparat',Arial,sans-serif;padding:11px 18px;border-radius:999px;transition:transform .2s;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.sigback{background:rgba(255,255,255,.78);color:#1C1956;border:1px solid rgba(255,255,255,.85);box-shadow:0 8px 24px rgba(28,25,86,.16)}
.sigwork{color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7);box-shadow:0 8px 24px rgba(96,96,190,.4)}
.sigback:hover,.sigwork:hover{transform:translateY(-2px)}
.wrap{max-width:900px;margin:0 auto;padding-left:22px;padding-right:22px}
.khero{padding:112px 0 0}
.kicker{display:inline-flex;align-items:center;gap:10px;font-weight:800;font-size:12px;letter-spacing:.14em;color:var(--ink);opacity:.78;margin-bottom:14px}
.kicker i{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#32BFFC,#B55CB7)}
h1.kt{font-weight:900;font-size:clamp(34px,6vw,64px);line-height:1;letter-spacing:-.035em;color:var(--ink)}
h1.kt .g{background:linear-gradient(90deg,#3D76E8,#6060BE,#B55CB7);-webkit-background-clip:text;background-clip:text;color:transparent}
.kintro{margin-top:18px;font-weight:500;font-size:clamp(16px,1.8vw,19px);line-height:1.6;color:var(--mut);max-width:60ch}
.ideas{margin:40px 0 0;display:grid;gap:16px}
.idea{display:grid;grid-template-columns:64px 1fr;gap:20px;align-items:start;background:var(--glass);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid var(--gline);border-radius:20px;padding:24px 26px;box-shadow:0 14px 40px rgba(28,25,86,.08)}
.idea .n{font-weight:900;font-size:34px;line-height:1;letter-spacing:-.03em;background:linear-gradient(135deg,#3D76E8,#B55CB7);-webkit-background-clip:text;background-clip:text;color:transparent}
.idea h3{font-weight:900;font-size:20px;letter-spacing:-.01em;color:var(--ink);margin-bottom:6px}
.idea p{font-weight:500;font-size:15px;line-height:1.6;color:var(--body)}
@media(max-width:560px){.idea{grid-template-columns:1fr;gap:6px}.idea .n{font-size:28px}}
.cap{margin:44px 0 0;text-align:center;background:var(--glass);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid var(--gline);border-radius:24px;padding:clamp(30px,4vw,44px);box-shadow:0 18px 50px rgba(28,25,86,.10)}
.cap h2{font-weight:900;font-size:clamp(24px,3vw,34px);letter-spacing:-.02em;color:var(--ink);max-width:20ch;margin:0 auto}
.cap p{margin:12px auto 20px;font-weight:500;font-size:15px;color:var(--mut);max-width:46ch}
.form{display:flex;gap:10px;justify-content:center;max-width:460px;margin:0 auto;flex-wrap:wrap}
.form input[type=email]{flex:1;min-width:200px;border:1px solid rgba(28,25,86,.16);border-radius:999px;padding:14px 20px;font:500 15px 'Apparat',Arial,sans-serif;background:rgba(255,255,255,.75);outline:none}
.form input[type=email]:focus{border-color:#6060BE;box-shadow:0 0 0 4px rgba(96,96,190,.16)}
.form button{border:0;border-radius:999px;padding:14px 26px;font-weight:800;font-size:15px;color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7);cursor:pointer;transition:transform .2s}
.form button:hover{transform:translateY(-2px)}
.hp{position:absolute;left:-5000px}.okmsg{display:none;font-weight:800;font-size:16px;color:var(--ink)}
.hire{margin:22px 0 0;border-radius:26px;color:#F4F3F3;background:linear-gradient(120deg,#1C1956,#3D76E8 52%,#6060BE);padding:clamp(38px,5vw,58px) clamp(24px,4vw,48px);text-align:center}
.hire h2{font-weight:900;font-size:clamp(24px,3.2vw,38px);letter-spacing:-.025em;max-width:20ch;margin:0 auto}
.hire p{margin:14px auto 22px;font-weight:500;font-size:16px;color:#E4E4EF;max-width:46ch;line-height:1.5}
.hire a{display:inline-block;background:#F4F3F3;color:#1C1956;font-weight:800;font-size:16px;padding:15px 32px;border-radius:999px;transition:transform .2s}
.hire a:hover{transform:translateY(-2px)}
.other{margin:26px 0 0;text-align:center;font-weight:700;font-size:14px;color:var(--ink)}
.other a{border-bottom:2px solid rgba(28,25,86,.26);margin:0 6px;display:inline-block}
.foot{margin-top:20px;padding:40px 0 60px;color:var(--mut);font-size:13px;line-height:1.9}
.foot b{color:var(--ink);font-weight:800;font-size:16px}.foot a{color:var(--ink)}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
"""
JS = ("addEventListener('scroll',function(){var h=document.documentElement,d=(h.scrollHeight-h.clientHeight);"
 "var p=document.querySelector('.prog');if(p)p.style.width=(d>0?h.scrollTop/d*100:0)+'%';},{passive:true});"
 "function sigSubmit(form,done){var pre=location.protocol==='file:'||/^(localhost$|127\\.|192\\.168\\.)/.test(location.hostname);"
 "if(pre){done(true);return;}var data=new URLSearchParams(new FormData(form));"
 "fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:data.toString()})"
 ".then(function(r){done(r.ok);}).catch(function(){done(false);});}"
 "document.querySelectorAll('form.form').forEach(function(f){f.addEventListener('submit',function(e){e.preventDefault();"
 "sigSubmit(f,function(ok){f.style.display='none';var m=f.parentElement.querySelector('.okmsg');"
 "m.textContent=ok?'You are in. The next edition lands in your inbox.':'Something went wrong. Email hello@sensalab.io.';m.style.display='block';});});});")

def build(name, d):
    url = "%s/kit-%s.html" % (BASE, name)
    ideas_html = "".join(
     '<div class="idea"><div class="n">%02d</div><div><h3>%s</h3><p>%s</p></div></div>' % (i+1, html.escape(t), html.escape(desc))
     for i,(t,desc) in enumerate(d["ideas"]))
    others = [(n2, KIT[n2]["title"]) for n2 in KIT if n2 != name]
    other_html = "".join('<a href="kit-%s.html">%s</a>' % (n2, html.escape(t)) for n2,t in others)
    itemlist = {"@context":"https://schema.org","@type":"ItemList","name":d["title"],"url":url,
     "itemListElement":[{"@type":"ListItem","position":i+1,"name":t} for i,(t,_) in enumerate(d["ideas"])]}
    meta = d["intro"][:155].rstrip(" ,.;:") + "."
    head = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
     '<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light only">'
     '<title>%s | The Signal by SensaLab</title>' % html.escape(d["title"])
     + '<meta name="description" content="%s">' % html.escape(meta)
     + '<link rel="canonical" href="%s">' % url
     + '<meta name="robots" content="index,follow,max-image-preview:large">'
     + '<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png"><link rel="apple-touch-icon" href="apple-touch-icon.png">'
     + '<meta name="author" content="SensaLab"><meta name="theme-color" content="#F4F3F3">'
     + '<meta name="keywords" content="%s">' % html.escape(d["kw"])
     + '<meta property="og:type" content="website"><meta property="og:site_name" content="The Signal by SensaLab">'
     + '<meta property="og:title" content="%s"><meta property="og:description" content="%s">' % (html.escape(d["title"]), html.escape(meta))
     + '<meta property="og:url" content="%s"><meta property="og:image" content="%s/og.jpg">' % (url, BASE)
     + '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="%s/og.jpg">' % BASE
     + '<script defer data-domain="signal.sensalab.io" src="https://plausible.io/js/script.js"></script>'
     + '<script type="application/ld+json">%s</script>' % json.dumps(itemlist, ensure_ascii=False)
     + '<style>' + FONT + CSS + '</style></head>')
    body = "".join([
     '<body><a class="skip" href="#main">Skip to content</a><div class="prog"></div><div class="bg"><div class="blob b1"></div><div class="blob b2"></div></div>',
     '<div class="chrome"><a class="sigback" href="index.html#kit">&#8592; The Signal</a>',
     '<a class="sigwork" href="work.html">Work with us</a></div>',
     '<main id="main"><section class="wrap khero"><span class="kicker"><i></i>Free kit</span>',
     '<h1 class="kt">', d["title"].split(" ",1)[0], ' <span class="g">', d["title"].split(" ",1)[1], '</span></h1>',
     '<p class="kintro">', html.escape(d["intro"]), '</p>',
     '<div class="ideas">', ideas_html, '</div>',
     '<div class="cap"><h2>Get the next kit and the newsletter</h2>',
     '<p>Real moves in experiential and real time, every two weeks, plus new idea kits as we publish them.</p>',
     '<form class="form" name="signal-kit" method="POST" data-netlify="true" netlify-honeypot="bot-field">',
     '<input type="hidden" name="form-name" value="signal-kit"><input type="hidden" name="kit" value="', name, '">',
     '<p class="hp"><label>Do not fill <input name="bot-field"></label></p>',
     '<input type="email" name="email" required placeholder="you@studio.com" aria-label="Your email"><button type="submit">Get The Signal</button></form>',
     '<div class="okmsg" role="status"></div></div>',
     '<div class="other">More kits: ', other_html, '</div>',
     '<div class="hire"><h2>Want one of these built, under your name?</h2>',
     '<p>SensaLab is the white label real time 3D and immersive layer agencies and brands use to build activations under their own brand.</p>',
     '<a href="work.html">Work with us &#8594;</a></div>',
     '<footer class="foot"><p><b>SensaLab</b></p><p>Rendering imagination. From Los Angeles.</p>',
     '<p style="margin-top:8px"><a href="https://sensalab.io">sensalab.io</a> &middot; <a href="index.html">The Signal</a> &middot; <a href="privacy.html">Privacy</a></p>',
     '<p style="margin-top:8px">&#169; 2026 SensaLab &middot; Los Angeles, CA, USA &middot; <a href="mailto:hello@sensalab.io">hello@sensalab.io</a></p></footer>',
     '</section></main><script>', JS, '</script></body></html>',
    ])
    return head + body

for name, d in KIT.items():
    out = build(name, d)
    (BLOG/("kit-%s.html"%name)).write_text(out, encoding="utf-8")
    try: (DEST/("kit-%s.html"%name)).write_text(out, encoding="utf-8")
    except Exception: pass
    print("kit ->", "kit-%s.html"%name, "(%d KB, %d ideas)" % (len(out)//1024, len(d["ideas"])))
print("done kits")
