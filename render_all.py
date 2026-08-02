# -*- coding: utf-8 -*-
"""
Renderiza las ediciones reales en los 10 templates -> sim/out/<ED>-<template>.html
y arma un indice navegable. NO toca los diseños originales ni los slots de media.
"""
import glob, json, os
from render_sim import fill

BASE = os.path.dirname(os.path.abspath(__file__))
DESIGNS = r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\designs"
OUT = os.path.join(BASE, "sim", "out")
os.makedirs(OUT, exist_ok=True)

EDITIONS = {
    "A": ("Steal This World Cup", os.path.join(BASE, "sim", "edicion-A.json")),
    "B": ("The Audience Can Tell", os.path.join(BASE, "sim", "edicion-B.json")),
}

templates = sorted(glob.glob(os.path.join(DESIGNS, "design-*.html")))
rows = []

# manifest de media (imagenes reales + video) por edicion
mpath = os.path.join(OUT, "media", "manifest.json")
manifest = json.load(open(mpath, encoding="utf-8")) if os.path.exists(mpath) else {}

for edkey, (edtitle, edpath) in EDITIONS.items():
    edition = json.load(open(edpath, encoding="utf-8"))
    media = manifest.get(edkey)
    for tpl in templates:
        tname = os.path.splitext(os.path.basename(tpl))[0]  # design-a1
        html = open(tpl, encoding="utf-8").read()
        out_html, report = fill(edition, html, media=media)
        outname = f"{edkey}-{tname}.html"
        open(os.path.join(OUT, outname), "w", encoding="utf-8").write(out_html)
        rows.append((edkey, edtitle, tname, outname, report))
        print(f"  {outname}: H{report['headlines_filled']}/{report['headlines_in_template']} "
              f"B{report['bodies_filled']}/{report['bodies_in_template']} C{report['ctas_in_template']}")

# indice
cards = {"A": [], "B": []}
for edkey, edtitle, tname, outname, rep in rows:
    warn = "" if (rep["headlines_filled"] >= 5 and rep["bodies_filled"] >= 5) else " ⚠"
    cards[edkey].append(
        f'<a href="{outname}" style="display:block;padding:14px 18px;margin:6px 0;'
        f'background:#12102b;border:1px solid #2a2748;border-radius:10px;color:#EDEBFF;'
        f'text-decoration:none;font:600 15px/1.3 system-ui;">{tname}{warn}'
        f'<span style="display:block;font:400 12px/1.4 system-ui;color:#8b86b8;margin-top:3px;">'
        f'{rep["headlines_filled"]} titulares · {rep["bodies_filled"]} bodies · {rep["ctas_in_template"]} CTAs</span></a>')

idx = f"""<!doctype html><meta charset=utf-8><title>INMERSIVO — simulaciones</title>
<body style="margin:0;background:#0a0918;color:#EDEBFF;font-family:system-ui;padding:32px;">
<h1 style="font:700 26px/1.2 Georgia,serif;">INMERSIVO · simulaciones reales</h1>
<p style="color:#8b86b8;max-width:640px;">Cada diseño lleno con contenido REAL. 2 ediciones × 10 templates.
Los slots de media (hero/news/video) quedan como placeholders — los llena el carril de arte.</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:28px;max-width:920px;margin-top:24px;">
<div><h2 style="font:700 18px/1.2 Georgia,serif;">Edición A · Steal This World Cup</h2>{''.join(cards['A'])}</div>
<div><h2 style="font:700 18px/1.2 Georgia,serif;">Edición B · The Audience Can Tell</h2>{''.join(cards['B'])}</div>
</div></body>"""
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(idx)
print(f"\nOK -> {os.path.join(OUT, 'index.html')} ({len(rows)} simulaciones)")
