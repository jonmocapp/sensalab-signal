# -*- coding: utf-8 -*-
"""Repair the archive editions (signal-17..20): proper HTML skeleton + charset (kills mojibake and
quirks-mode white zones), and REMOVE the injected bottom reading-chrome band that renders faint/broken
(the top "back to The Signal" + "Work with us" pills already cover navigation). Idempotent."""
import re, pathlib
BLOG = pathlib.Path(r"C:\Dev\SensaLab-Newsletter-Bot\blog")
DEST = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\Newsletter\blog")
TITLES = {17:"Edition 17, Immersive",18:"Edition 18, Real time",19:"Edition 19, Presence",20:"Edition 20, The week experiential went pro"}
SKEL = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light only">'
 '<title>%s | The Signal by SensaLab</title></head><body>')

for n in (17,18,19,20):
    f = BLOG/("signal-%d.html"%n)
    t = f.read_text(encoding="utf-8", errors="replace")
    # proper skeleton (once)
    if not t.lstrip().lower().startswith("<!doctype"):
        t = (SKEL % TITLES[n]) + t
    # remove the faint/broken injected bottom band + its scoped style, and any leftover band-fix style
    t = re.sub(r"<section class=['\"]signext['\"][\s\S]*?</section>", "", t)
    t = re.sub(r"<style>[^<]*?\.signext\{[\s\S]*?</style>", "", t)   # scoped inject style (no attrs)
    t = re.sub(r'<style id="sig-band-fix">[\s\S]*?</style>', "", t)  # remove earlier band-fix attempt
    if "</body>" not in t.lower():
        t = t + "</body></html>"
    f.write_text(t, encoding="utf-8")
    try: (DEST/("signal-%d.html"%n)).write_text(t, encoding="utf-8")
    except Exception: pass
    print("repaired edition", n, "| signext removed:", "signext" not in t)
print("done")
