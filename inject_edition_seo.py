# -*- coding: utf-8 -*-
"""Inject per-edition SEO/GEO into each edition head: title, description, canonical, OG, BlogPosting JSON-LD tied to the SensaLab entity. Idempotent (wrapped in <!--sigseo--> markers)."""
import re, json, pathlib
BLOG = pathlib.Path(r"C:\Dev\SensaLab-Newsletter-Bot\blog")
DEST = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\Newsletter\blog")
BASE = "https://signal.sensalab.io"

ED = {
 17:("Immersive","The Sphere, teamLab, and Snap's new Specs. Three moves that put people inside the brand.","2026-06-20"),
 18:("Real time","NVIDIA, Unreal, and the Gamescom floor. Real time 3D moves from the studio to the show.","2026-07-04"),
 19:("Presence","Real Madrid, LED volumes, and the backlash against AI. The week presence beat spectacle.","2026-07-18"),
 20:("The week experiential went pro","Tyler Perry's volume, Xreal's Aura, and Southwest on the beach. Different players, same bet: put people inside it.","2026-08-01"),
}

ORG = {"@type":["Organization","ProfessionalService"],"@id":BASE+"/#org","name":"SensaLab",
 "alternateName":["Sensa Lab","SensaLab Los Angeles"],"url":"https://sensalab.io/",
 "email":"hello@sensalab.io","logo":"https://sensalab.io/logo.png","slogan":"Rendering imagination",
 "address":{"@type":"PostalAddress","addressLocality":"Los Angeles","addressRegion":"CA","addressCountry":"US"},
 "sameAs":["https://instagram.com/sensalab","https://www.linkedin.com/company/sensalab","https://youtube.com/@sensalab"]}

def block(n):
    head, desc, date = ED[n]
    url = "%s/signal-%d.html" % (BASE, n)
    title = "%s | The Signal by SensaLab" % head
    post = {"@type":"BlogPosting","@id":url+"#post","headline":head,"description":desc,
     "datePublished":date,"dateModified":date,"inLanguage":"en","url":url,"mainEntityOfPage":url,
     "image":BASE+"/og.jpg","author":{"@id":BASE+"/#org"},"publisher":{"@id":BASE+"/#org"},
     "isPartOf":{"@type":"Blog","@id":BASE+"/#blog","name":"The Signal"},
     "about":["Experiential marketing","Immersive experiences","Real time 3D"]}
    ld = json.dumps({"@context":"https://schema.org","@graph":[ORG,post]}, ensure_ascii=False)
    return ("<!--sigseo-->"
      '<title>%s</title>' % title
      + '<meta name="description" content="%s">' % desc
      + '<link rel="canonical" href="%s">' % url
      + '<meta name="robots" content="index,follow,max-image-preview:large">'
      + '<meta name="author" content="SensaLab"><meta name="geo.region" content="US-CA"><meta name="geo.placename" content="Los Angeles">'
      + '<meta property="og:type" content="article"><meta property="og:site_name" content="The Signal by SensaLab">'
      + '<meta property="og:title" content="%s"><meta property="og:description" content="%s">' % (head, desc)
      + '<meta property="og:url" content="%s"><meta property="og:image" content="%s/og.jpg">' % (url, BASE)
      + '<meta property="article:published_time" content="%s"><meta property="article:publisher" content="https://sensalab.io/">' % date
      + '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s">' % (head, desc)
      + '<script type="application/ld+json">%s</script>' % ld
      + "<!--/sigseo-->")

for n in ED:
    f = BLOG/("signal-%d.html"%n)
    if not f.exists(): print(n,"MISSING"); continue
    t = f.read_text(encoding="utf-8", errors="replace")
    t = re.sub(r"<!--sigseo-->.*?<!--/sigseo-->", "", t, flags=re.S)   # strip prior
    t = re.sub(r"<title>.*?</title>", "", t, count=1, flags=re.S|re.I)  # drop original title (replaced)
    blk = block(n)
    if re.search(r"</head>", t, re.I):
        t = re.sub(r"</head>", blk+"</head>", t, count=1, flags=re.I)
    elif re.search(r"<head[^>]*>", t, re.I):
        t = re.sub(r"(<head[^>]*>)", lambda m: m.group(1)+blk, t, count=1, flags=re.I)
    else:  # no head at all, put after <html> or at top
        t = blk + t
    f.write_text(t, encoding="utf-8")
    (DEST/("signal-%d.html"%n)).write_text(t, encoding="utf-8")
    print("seo ->", f.name, "|", ED[n][0])
