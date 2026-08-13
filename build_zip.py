# -*- coding: utf-8 -*-
"""Zip blog/ with FORWARD-SLASH paths (real folders) so Netlify serves img/ and fonts/.
PowerShell Compress-Archive writes backslash entries that break subfolders; this fixes it."""
import zipfile, pathlib, shutil
BLOG = pathlib.Path(__file__).resolve().parent / "blog"
OUT = pathlib.Path(__file__).resolve().parent / "signal-site.zip"
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for p in BLOG.rglob("*"):
        if p.is_file():
            z.write(p, p.relative_to(BLOG).as_posix())
names = zipfile.ZipFile(OUT).namelist()
bs = sum(1 for n in names if "\\" in n)
print("entries:", len(names), "| MB:", OUT.stat().st_size // 1024 // 1024)
print("backslash entries (must be 0):", bs)
print("has fonts/:", any(n.startswith("fonts/") for n in names),
      "| has img/:", any(n.startswith("img/") for n in names),
      "| index at root:", "index.html" in names)
for t in [r"C:\Users\jonmo\Downloads\signal-site.zip",
          r"C:\Users\jonmo\Desktop\signal-site.zip",
          r"C:\Users\jonmo\OneDrive\Desktop\signal-site.zip"]:
    try:
        shutil.copyfile(OUT, t); print("copied ->", t)
    except Exception as e:
        print("skip", t, e)
