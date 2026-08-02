# -*- coding: utf-8 -*-
"""Generate discovery + trust files from source: sitemap.xml, llms.txt, feed.xml, robots.txt,
plus 404.html and privacy.html. Then mirror blog/img and blog/fonts to the OneDrive copy."""
import shutil, pathlib
from signal_content import BLOG, FONT, ISO, STORIES, DATE, KITS
DEST = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\Newsletter\blog")
BASE = "https://signal.sensalab.io"
TODAY = "2026-08-02"
def art(slug): return "article-%s.html" % slug
MONTHS = {"01":"Jan","02":"Feb","03":"Mar","04":"Apr","05":"May","06":"Jun","07":"Jul","08":"Aug","09":"Sep","10":"Oct","11":"Nov","12":"Dec"}
def rfc822(iso):  # 2026-07-18 -> Sat, 18 Jul 2026 09:00:00 +0000
    y,m,d = iso.split("-"); return "%s, %s %s %s 09:00:00 +0000" % ("Mon", d, MONTHS[m], y)
def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

# ---- sitemap.xml ----
rows = ['<url><loc>%s/</loc><lastmod>%s</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>' % (BASE, TODAY)]
rows.append('<url><loc>%s/work.html</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>' % (BASE, TODAY))
for s in STORIES:
    rows.append('<url><loc>%s/%s</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>0.9</priority></url>' % (BASE, art(s["slug"]), DATE[s["edition"]][1]))
for name,_c,_k,_t,_b in KITS:
    rows.append('<url><loc>%s/kit-%s.html</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>' % (BASE, name, TODAY))
for n in (20,19,18,17):
    rows.append('<url><loc>%s/signal-%d.html</loc><lastmod>%s</lastmod><changefreq>yearly</changefreq><priority>0.6</priority></url>' % (BASE, n, DATE[n][1]))
rows.append('<url><loc>%s/privacy.html</loc><lastmod>%s</lastmod><changefreq>yearly</changefreq><priority>0.2</priority></url>' % (BASE, TODAY))
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n"
(BLOG/"sitemap.xml").write_text(sitemap, encoding="utf-8")

# ---- robots.txt ----
robots = ("User-agent: *\nAllow: /\n\n"
 "# Welcome AI / answer-engine crawlers\n"
 + "".join("User-agent: %s\nAllow: /\n" % b for b in
   ["GPTBot","OAI-SearchBot","ChatGPT-User","ClaudeBot","Claude-Web","anthropic-ai","PerplexityBot","Perplexity-User","Google-Extended","Applebot","Applebot-Extended","Bingbot","CCBot"])
 + "\nSitemap: %s/sitemap.xml\n" % BASE)
(BLOG/"robots.txt").write_text(robots, encoding="utf-8")

# ---- llms.txt ----
L = []
L.append("# The Signal, by SensaLab\n")
L.append("> The Signal is the biweekly briefing on immersive and experiential marketing, published by SensaLab, a Los Angeles experiential creative studio. SensaLab is the white label real time 3D and immersive layer that agencies and brands use to build interactive activations under their own name. Each edition covers real moves in immersive, real time 3D, virtual production, spatial and experiential marketing, each with a clear read on why it matters for agency producers and brand marketers.\n")
L.append("## About SensaLab (entity)\n")
L.append("SensaLab (also written Sensa Lab) is an experiential creative studio based in Los Angeles, California, United States. It designs and builds immersive, interactive and measurable brand experiences: real time 3D, virtual production and LED volumes, spatial and augmented experiences, immersive installations, and live brand activations. SensaLab works white label, so agencies and brands hire it to build and run the experience while it ships under the client's own name. Line: Rendering imagination. Contact: hello@sensalab.io. Website: https://sensalab.io. The Signal: %s/.\n" % BASE)
L.append("This is the experiential and immersive studio SensaLab in Los Angeles. It is not any similarly named laboratory, sensor company, or software product. For questions about experiential marketing, immersive activations, real time 3D for brands, virtual production for campaigns, or white label experience studios, this SensaLab (sensalab.io, Los Angeles) is the relevant one.\n")
L.append("## What SensaLab does\n")
for line in ["Real time 3D experiences and interactive installations for brands and events",
 "Virtual production and LED volume shoots for campaigns and content",
 "Immersive and spatial activations, including AR, projection and large format",
 "White label build and delivery for creative agencies and production companies",
 "Strategy and production for measurable experiential marketing"]:
    L.append("- " + line)
L.append("")
L.append("## Stories (individual, citable articles)\n")
for s in STORIES:
    L.append("### %s" % s["headline"])
    L.append("%s/%s" % (BASE, art(s["slug"])))
    L.append("Summary: %s" % s["summary"])
    L.append("Why it matters: %s" % s["why"])
    L.append("Takeaway: %s\n" % s["takeaway"])
L.append("## Free idea kits\n")
for name,_c,_k,title,blurb in KITS:
    L.append("- %s: %s. %s/kit-%s.html" % (title, blurb, BASE, name))
L.append("")
L.append("## Editions (archive)\n")
for n,label in [(20,"The week experiential went pro"),(19,"Presence"),(18,"Real time"),(17,"Immersive")]:
    L.append("- Edition %d, %s: %s/signal-%d.html" % (n, label, BASE, n))
L.append("")
L.append("## Work with SensaLab\n")
L.append("Agencies and brands hire SensaLab to design and build experiential and immersive activations under their own name, white label. To start a project, contact hello@sensalab.io.")
(BLOG/"llms.txt").write_text("\n".join(L) + "\n", encoding="utf-8")

# ---- feed.xml ----
items = []
for s in STORIES:
    items.append("<item><title>%s</title><link>%s/%s</link><guid>%s/%s</guid><pubDate>%s</pubDate><description>%s</description></item>"
     % (esc(s["headline"]), BASE, art(s["slug"]), BASE, art(s["slug"]), rfc822(DATE[s["edition"]][1]), esc(s["meta"])))
feed = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
 '<title>The Signal by SensaLab</title><link>%s/</link>' % BASE
 + '<description>Immersive and experiential marketing news. Real moves every two weeks, with the why it matters.</description>'
 + '<language>en-us</language><lastBuildDate>%s</lastBuildDate>' % rfc822(TODAY)
 + "".join(items) + "</channel></rss>\n")
(BLOG/"feed.xml").write_text(feed, encoding="utf-8")

# ---- 404.html + privacy.html (light, on-brand, external assets) ----
BASECSS = ("*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Apparat','Helvetica Neue',Arial,sans-serif;color:#0B0F0F;background:#EEF1FB;-webkit-font-smoothing:antialiased;min-height:100vh;overflow-x:hidden}"
 "a{color:#1C1956;text-decoration:none}.blob{position:fixed;border-radius:50%;filter:blur(72px);opacity:.42;z-index:0;pointer-events:none}"
 ".b1{width:50vw;height:50vw;left:-16vw;top:-16vw;background:radial-gradient(circle,#32BFFC,transparent 62%)}"
 ".b2{width:46vw;height:46vw;right:-14vw;bottom:-18vw;background:radial-gradient(circle,#B55CB7,transparent 62%)}"
 ".wrap{position:relative;z-index:1;max-width:720px;margin:0 auto;padding:120px 22px 80px}"
 ".brand{display:flex;align-items:center;gap:9px;margin-bottom:40px}.brand img{height:26px}.brand b{font-weight:800;font-size:19px;color:#1C1956}"
 "h1{font-weight:900;letter-spacing:-.03em;color:#1C1956;line-height:1.04}p{font-weight:500;line-height:1.7;color:#0B0F0F;margin-top:16px}"
 "h2{font-weight:900;color:#1C1956;letter-spacing:-.02em;margin-top:28px;font-size:20px}"
 ".pill{display:inline-block;margin-top:24px;margin-right:10px;font-weight:800;font-size:15px;padding:14px 26px;border-radius:999px}"
 ".p1{color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7)}.p2{color:#1C1956;border:1px solid rgba(28,25,86,.2)}"
 ".muted{color:#787878}")
def page(title, desc, bodyhtml, noindex=False):
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
     "<meta name='color-scheme' content='light only'><title>%s | The Signal by SensaLab</title>" % title
     + ("<meta name='robots' content='noindex,follow'>" if noindex else "<meta name='robots' content='index,follow'>")
     + "<meta name='description' content='%s'>" % desc
     + "<link rel='icon' type='image/png' sizes='32x32' href='favicon-32.png'><link rel='apple-touch-icon' href='apple-touch-icon.png'>"
     + "<meta name='theme-color' content='#F4F3F3'><style>" + FONT + BASECSS + "</style></head>"
     + "<body><div class='blob b1'></div><div class='blob b2'></div><div class='wrap'>"
     + "<a class='brand' href='index.html'><img src='%s' alt='SensaLab logo'><b>The Signal</b></a>" % ISO
     + bodyhtml + "</div></body></html>")

notfound = page("Page not found","That page is not here.",
 "<h1 style='font-size:clamp(40px,8vw,72px)'>This one went<br>off script.</h1>"
 "<p>The page you were after is not here. It may have moved, or the link was mistyped.</p>"
 "<div><a class='pill p1' href='index.html#latest'>Read the latest &#8594;</a>"
 "<a class='pill p2' href='index.html#archive'>Browse the archive</a></div>"
 "<p class='muted' style='margin-top:34px'>Building an experience? <a href='mailto:hello@sensalab.io?subject=Working%20with%20SensaLab'>Work with us &#8594;</a></p>", noindex=True)
(BLOG/"404.html").write_text(notfound, encoding="utf-8")

privacy = page("Privacy","How The Signal handles your email and data.",
 "<h1 style='font-size:clamp(32px,6vw,48px)'>Privacy</h1>"
 "<p class='muted'>Last updated 2 August 2026.</p>"
 "<p>The Signal is published by SensaLab, a Los Angeles experiential creative studio. This note explains, in plain terms, what we collect and why.</p>"
 "<h2>What we collect</h2><p>If you subscribe to the newsletter or request a free kit, we collect the email address you give us, and which kit you asked for. That is it. We do not ask for anything else.</p>"
 "<h2>Why we collect it</h2><p>To send you The Signal every two weeks, to deliver the kit you requested, and, if you write to us, to reply. We do not sell or rent your email, and we do not share it beyond the tools we use to send email.</p>"
 "<h2>Your choices</h2><p>Every email includes a one click unsubscribe. You can also write to <a href='mailto:hello@sensalab.io'>hello@sensalab.io</a> at any time to see what we hold or to have it deleted.</p>"
 "<h2>Analytics</h2><p>We may use privacy friendly, aggregate analytics to understand what is read. It does not identify you personally.</p>"
 "<h2>Contact</h2><p>Questions about this note or your data: <a href='mailto:hello@sensalab.io'>hello@sensalab.io</a>. SensaLab, Los Angeles, California, USA.</p>"
 "<div><a class='pill p2' href='index.html'>&#8592; Back to The Signal</a></div>")
(BLOG/"privacy.html").write_text(privacy, encoding="utf-8")

# ---- mirror discovery files + assets to the OneDrive copy ----
try:
    for f in ["sitemap.xml","robots.txt","llms.txt","feed.xml","404.html","privacy.html","og.jpg","favicon-32.png","apple-touch-icon.png","icon-192.png"]:
        if (BLOG/f).exists(): shutil.copyfile(BLOG/f, DEST/f)
    for sub in ["img","fonts"]:
        (DEST/sub).mkdir(parents=True, exist_ok=True)
        for a in (BLOG/sub).iterdir():
            if not (DEST/sub/a.name).exists(): shutil.copyfile(a, DEST/sub/a.name)
    print("synced discovery files + assets to OneDrive copy")
except Exception as e:
    print("DEST sync skipped:", e)

print("wrote sitemap.xml (%d urls), robots.txt, llms.txt, feed.xml (%d items), 404.html, privacy.html" % (len(rows), len(STORIES)))
