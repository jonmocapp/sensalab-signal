# -*- coding: utf-8 -*-
import os
HERE = os.path.dirname(os.path.abspath(__file__))
TPLS = [("a1","Editorial Pearl"),("a2","Cinematic Ink"),("a4","Deep Vitrine"),
        ("a5","Kinetic Signal"),("b1","Pearl refinado"),("b2","Darkroom Ink"),
        ("b4","Vitrine refinado"),("c4","The Fold"),("panel-1","Till Morning"),
        ("panel-3","Full Brightness")]

def cell(edkey, code):
    png = f"shots/{edkey}-design-{code}.png"
    html = f"{edkey}-design-{code}.html"
    tag = "Mundial" if edkey == "A" else "Cosm/SIGGRAPH/Shrek"
    return f'''<a href="{html}" style="text-decoration:none;color:#EDEBFF;">
      <div style="background:#14122e;border:1px solid #2a2748;border-radius:12px;overflow:hidden;">
        <div style="height:360px;overflow:hidden;background:#0a0918;">
          <img src="{png}" style="width:100%;display:block;" loading="lazy">
        </div>
        <div style="padding:9px 12px;font:600 12px/1.3 system-ui;">Versión {edkey} · {tag}</div>
      </div></a>'''

rows = ""
for code, title in TPLS:
    rows += f'''<div style="margin:30px 0 8px;font:700 17px/1.2 Georgia,serif;color:#fff;">{code.upper()} · {title}</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">{cell("A",code)}{cell("B",code)}</div>'''

doc = f'''<!doctype html><meta charset=utf-8><title>INMERSIVO — las 20 simulaciones</title>
<body style="margin:0;background:#0a0918;color:#EDEBFF;font-family:system-ui;padding:30px;max-width:820px;margin:0 auto;">
<h1 style="font:800 26px/1.2 Georgia,serif;">Las 20 simulaciones</h1>
<p style="color:#8b86b8;">Tus 10 diseños, cada uno con 2 newsletters reales. Haz click en cualquiera para abrirlo completo.
Las cajas grises dentro (hero, imágenes, video) son donde van las fotos/clips — eso lo pone tu carril de arte.</p>
{rows}
</body>'''
open(os.path.join(HERE, "galeria.html"), "w", encoding="utf-8").write(doc)
print("galeria.html listo")
