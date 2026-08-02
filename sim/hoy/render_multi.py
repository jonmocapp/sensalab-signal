# -*- coding: utf-8 -*-
"""
Renderiza ediciones en OTROS templates claros (b1, b4, c4), reusando toda la maquinaria de
render_pearl (portadas, adapt, logo, sentence case). Generaliza el post-proceso para el
masthead de cada template (a.brand y a.sl-brand), el número de issue y la ubicación.
Para templates con masthead oscuro (c4) usa el logo en blanco.
"""
import base64
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from bs4 import BeautifulSoup                       # noqa: E402
from PIL import Image                               # noqa: E402
from render_sim import fill                         # noqa: E402
import render_pearl as rp                           # noqa: E402

DESIGNS = r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\designs"

# edición -> (archivo de template, masthead oscuro?). Solo templates CLAROS: a1 (Pearl) y b1.
PLAN = {
    "17": ("design-b1.html", False),
    "18": ("design-a1.html", False),   # Pearl
    "19": ("design-b1.html", False),
    "20": ("design-b1.html", False),   # edición de hoy
}


ISOTIPO = os.path.join(HERE, "_brand", "isotipo-color.png")


def isotipo_uri():
    with open(ISOTIPO, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def white_logo_uri():
    """Versión del logo en blanco (paper) para mastheads oscuros: recolorea los píxeles
    opacos a #F4F3F3 conservando el alfa."""
    im = Image.open(rp.LOGO).convert("RGBA")
    alpha = im.split()[-1]
    white = Image.new("RGBA", im.size, (244, 243, 243, 0))
    white.putalpha(alpha)
    buf = io.BytesIO()
    white.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


_SENTENCE_CASE = [("Field Notes", "Field notes"), ("In the Lab", "In the lab"),
                  ("One take, no cuts", "one take, no cuts"), ("The Lazo", "the lazo")]


def post_process(html, ed, issue, dark):
    soup = BeautifulSoup(html, "html.parser")
    # ISOTIPO: Jon quiere solo el lazo (isotipo), NO el lockup con wordmark. El template ya
    # trae el isotipo como SVG (lazo con el gradiente de marca) -> conservamos el SVG y
    # quitamos el texto del wordmark.
    # MASTHEAD = logo COMPLETO: isotipo (gradiente) + wordmark "SensaLab" (sentence case, navy)
    brand = soup.find("a", attrs={"aria-label": "SensaLab"})
    if brand:
        for c in list(brand.children):
            c.extract()
        img = soup.new_tag("img", src=isotipo_uri())
        img["alt"] = "SensaLab"
        img["style"] = "height:28px;width:auto;display:block;"
        wm = soup.new_tag("span")
        wm.string = "SensaLab"
        wm["style"] = ("font-family:'Helvetica Neue','Aeonik',Arial,system-ui,sans-serif;"
                       "font-weight:800;font-size:21px;letter-spacing:-.01em;color:#1C1956;line-height:1;")
        brand.append(img)
        brand.append(wm)
    # FOOTER: elimina el ícono del lazo (Jon: "elimina este icono")
    for svg in soup.select("footer svg"):
        svg.decompose()
    # índice del template (b1: <a href="#item-N"><span class="t">mini titular</span>): usa MIS titulares
    idx = soup.select('a[href^="#item-"] span.t')
    secs = ed.get("sections", [])
    for i, el in enumerate(idx):
        if i < len(secs):
            el.string = secs[i].get("statement") or secs[i].get("headline", "")
    for meta in soup.find_all(string=lambda s: s and "Mexico City" in s):
        meta.replace_with(meta.replace("Mexico City", "Los Angeles"))
    # figcredit del template trae em dash ("Fig. 01 — ..."): regla de marca = sin guiones en copy
    for fc in soup.select("figcaption"):
        for node in fc.find_all(string=lambda s: s and "—" in s):
            node.replace_with(node.replace(" — ", " · ").replace("—", "·"))
    html = str(soup)
    html = html.replace("ISSUE 01 · JUL 2026", f"Issue {issue} · Jul 2026")
    html = re.sub(r"Issue 0\d\b", f"Issue {issue}", html)
    html = rp.ensure_viewport(html)  # web real: sin viewport un telefono renderiza a ~980px
    for a, b in _SENTENCE_CASE:
        html = html.replace(a, b)
    return html


def main():
    for issue, (tpl_name, dark) in PLAN.items():
        ed_file = next(f for f in os.listdir(HERE)
                       if f.startswith(f"ed{issue}-") and f.endswith(".json"))
        ed = json.load(open(os.path.join(HERE, ed_file), encoding="utf-8"))
        tpl = open(os.path.join(DESIGNS, tpl_name), encoding="utf-8").read()
        tpl = tpl.replace("text-transform:uppercase", "text-transform:none")
        media = rp.build_media(issue)
        html, report = fill(rp.adapt(ed), tpl, media=media)
        html = post_process(html, ed, issue, dark)
        out = os.path.join(HERE, f"multi-{issue}.html")
        open(out, "w", encoding="utf-8").write(html)
        print(f"  #{issue} [{tpl_name}] -> multi-{issue}.html  "
              f"(H{report['headlines_filled']}/{report['headlines_in_template']} "
              f"B{report['bodies_filled']}/{report['bodies_in_template']})")


if __name__ == "__main__":
    main()
