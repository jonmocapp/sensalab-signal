# -*- coding: utf-8 -*-
"""Inject reading chrome into each edition: back to menu, progress bar, persistent Work with us, and a next/hire band."""
import re, pathlib
BLOG = pathlib.Path(r"C:\Dev\SensaLab-Newsletter-Bot\blog")
DEST = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\Newsletter\blog")

NEXT = {17:("signal-18.html","Real time","Edition 18"),
        18:("signal-19.html","Presence","Edition 19"),
        19:("signal-20.html","The week experiential went pro","Edition 20"),
        20:("index.html","Browse every edition of The Signal","The archive")}

TOP = ("<div class='sigprog'></div>"
 "<a class='sigback' href='index.html'>&#8592; The Signal</a>"
 "<a class='sigwork' href='mailto:hello@sensalab.io?subject=Working%20with%20SensaLab'>Work with us</a>"
 "<style>"
 ".sigprog{position:fixed;top:0;left:0;height:3px;width:0;z-index:99999;background:linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7)}"
 ".sigback,.sigwork{position:fixed;top:16px;z-index:99999;font:800 13px/1 'Helvetica Neue',Arial,sans-serif;"
 "padding:11px 18px;border-radius:999px;text-decoration:none;transition:transform .2s;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}"
 ".sigback{left:18px;background:rgba(255,255,255,.72);color:#1C1956;border:1px solid rgba(255,255,255,.85);box-shadow:0 8px 24px rgba(28,25,86,.16)}"
 ".sigwork{right:18px;color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7);box-shadow:0 8px 24px rgba(96,96,190,.4)}"
 ".sigback:hover,.sigwork:hover{transform:translateY(-2px)}"
 "@media(max-width:600px){.sigback,.sigwork{font-size:12px;padding:9px 14px}}"
 "</style>"
 "<script>addEventListener('scroll',function(){var h=document.documentElement,d=(h.scrollHeight-h.clientHeight);"
 "document.querySelector('.sigprog').style.width=(d>0?h.scrollTop/d*100:0)+'%'},{passive:true});</script>")

def bottom(nhref, ntitle, nlabel):
    return ("<section class='signext'><div class='signx-in'>"
      "<div class='col'><span class='k'>Keep reading</span>"
      "<a class='nx' href='%s'><span class='nl'>%s</span><span class='nt'>%s &#8594;</span></a></div>"
      "<div class='col hire'><span class='k'>Ready to build one, under your name?</span>"
      "<a class='wk' href='mailto:hello@sensalab.io?subject=Working%%20with%%20SensaLab'>Work with us &#8594;</a></div>"
      "</div></section>"
      "<style>"
      ".signext{background:linear-gradient(120deg,#1C1956,#3D76E8 55%%,#6060BE);color:#F4F3F3;padding:56px 22px;font-family:'Helvetica Neue',Arial,sans-serif}"
      ".signx-in{max-width:920px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:26px}"
      "@media(max-width:720px){.signx-in{grid-template-columns:1fr}}"
      ".signext .col{background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.2);border-radius:18px;padding:26px 28px;backdrop-filter:blur(10px)}"
      ".signext .k{display:block;font-weight:700;font-size:12px;letter-spacing:.1em;color:#E4E4EF;opacity:.85;margin-bottom:12px}"
      ".signext .nl{display:block;font-weight:700;font-size:12px;color:#E4E4EF;opacity:.8}"
      ".signext .nt{display:block;font-weight:900;font-size:24px;letter-spacing:-.02em;color:#F4F3F3;margin-top:4px}"
      ".signext .wk{display:inline-block;margin-top:6px;background:#F4F3F3;color:#1C1956;font-weight:800;font-size:15px;padding:14px 28px;border-radius:999px;text-decoration:none}"
      ".signext a{text-decoration:none}"
      "</style>") % (nhref, nlabel, ntitle, )

for n,(nh,nt,nl) in NEXT.items():
    f = BLOG/("signal-%d.html"%n)
    if not f.exists(): print(n,"MISSING"); continue
    t = f.read_text(encoding="utf-8", errors="replace")
    if "sigback" in t:  # already injected, strip old chrome first
        t = re.sub(r"<div class='sigprog'>.*?</script>", "", t, flags=re.S)
        t = re.sub(r"<section class='signext'>.*?</style>", "", t, flags=re.S)
    if re.search(r"<body[^>]*>", t, re.I):
        t = re.sub(r"(<body[^>]*>)", lambda m: m.group(1)+TOP, t, count=1, flags=re.I)
    else:
        t = TOP + t
    b = bottom(nh, nt, nl)
    if "</body>" in t.lower():
        i = t.lower().rfind("</body>"); t = t[:i] + b + t[i:]
    else:
        t = t + b
    f.write_text(t, encoding="utf-8")
    (DEST/("signal-%d.html"%n)).write_text(t, encoding="utf-8")
    print("chrome ->", f.name, "next:", nh)
