# -*- coding: utf-8 -*-
"""
Inyector de contenido: mete una edicion estructurada (JSON) en cualquiera de los 10
templates de diseno, reemplazando titulares/bodies/CTAs por ROL (no por clase CSS,
que varia entre templates). Preserva todo el diseno; deja los slots de media intactos
(esos los llena el carril de arte).

Modelo de contenido compartido por los 10:
  hero(kicker,headline,sub) -> 3 secciones(kicker,headline,body,cta) -> video -> invitation

Uso:  python render_sim.py <edicion.json> <design.html> <salida.html>
"""
from __future__ import annotations

import sys
from bs4 import BeautifulSoup

# clases que son "mobiliario de marca" / footer -> NO tocar.
# OJO: aqui NO van clases de fuente/acento (ap, grad-txt) porque aparecen en titulares reales.
FURNITURE = {"meta", "legal", "fine", "where", "motto", "tag", "sl-fine", "wordmark",
             "lab", "sl-wordmark", "tnum", "num", "slot-tag", "sl-slot-tag",
             "duration", "runtime", "ph-dim", "ph-chip", "sl-num", "item-num", "playmeta",
             "dur", "label-motto"}
ACCENT = {"em", "grad-text", "grad-txt", "grad"}


def _cls(el) -> set:
    return set(el.get("class") or [])


def _is_furniture(el) -> bool:
    return bool(_cls(el) & FURNITURE)


def _edition_lists(ed: dict):
    heads = [ed["hero"]["headline"]] + [s["headline"] for s in ed["sections"]] \
        + [ed["video"]["headline"], ed["invitation"]["headline"]]
    bodies = [ed["hero"]["sub"]] + [s["body"] for s in ed["sections"]] \
        + [ed["video"]["body"], ed["invitation"]["body"]]
    ctas = [s.get("cta", "") for s in ed["sections"]]
    return heads, bodies, ctas


def _set_headline(el, text: str):
    """Reemplaza el texto del titular preservando una palabra-acento (span.em/grad)."""
    accents = [t for t in el.find_all(["span", "em", "b", "i"]) if _cls(t) & ACCENT]
    if accents:
        acc = accents[-1]
        words = text.split()
        if len(words) >= 4:
            lead, tail = " ".join(words[:-2]), " ".join(words[-2:])
        else:
            lead, tail = text, ""
        for c in list(el.children):
            c.extract()
        if lead:
            el.append(lead + " ")
        acc.string = tail
        el.append(acc)
    else:
        el.string = text


import re as _re

# clases de etiquetas-placeholder dentro de un slot de media (a ocultar al meter imagen)
_SLOT_LABELS = {"slot-tag", "sl-slot-tag", "ph-chip", "ph-dim", "sl-num", "playmeta",
                "dur", "media-fill", "runtime", "duration", "num"}
_DIM_RX = _re.compile(r"\d+\s*[×x]\s*\d+|newsletter-?ai|drop\s*<|poster\s*\+\s*play|loops?\s+muted",
                      _re.I)


def _slot_aspect(slot):
    """Aspect-ratio del slot: lo lee de su etiqueta de dimensiones (ej. 1200×760)."""
    m = _re.search(r"(\d{3,4})\s*[×x]\s*(\d{3,4})", slot.get_text(" ", strip=True))
    if m:
        return int(m.group(1)), int(m.group(2))
    name = (slot.get("data-slot") or "").lower()
    return {"hero": (1200, 760), "news-1": (900, 675), "news-2": (1400, 600),
            "news-3": (720, 900), "video": (1280, 720)}.get(name, (16, 9))


def _fill_slot(slot, nodes, w, h):
    st = slot.get("style", "") or ""
    slot["style"] = (st + f";position:relative;overflow:hidden;aspect-ratio:{w}/{h};").lstrip(";")
    for c in list(slot.children):
        c.extract()
    for n in nodes:
        slot.append(n)


def _img_tag(soup, src):
    img = soup.new_tag("img", src=src)
    img["style"] = "width:100%;height:100%;object-fit:cover;display:block;"
    img["loading"] = "lazy"
    return img


def _inject_image(soup, slot, src):
    w, h = _slot_aspect(slot)
    _fill_slot(slot, [_img_tag(soup, src)], w, h)


def _inject_video(soup, slot, poster, link):
    w, h = _slot_aspect(slot)
    a = soup.new_tag("a", href=link or "#")
    a["target"] = "_blank"
    a["rel"] = "noopener noreferrer"
    a["style"] = "position:absolute;inset:0;display:block;text-decoration:none;"
    a.append(_img_tag(soup, poster))
    play = soup.new_tag("span")
    play["style"] = ("position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);"
                     "width:72px;height:72px;border-radius:50%;background:rgba(10,9,24,.55);"
                     "border:2px solid rgba(255,255,255,.9);box-shadow:0 6px 24px rgba(0,0,0,.4);")
    tri = soup.new_tag("span")
    tri["style"] = ("position:absolute;top:50%;left:calc(50% + 3px);transform:translate(-50%,-50%);"
                    "width:0;height:0;border-left:20px solid #fff;border-top:13px solid transparent;"
                    "border-bottom:13px solid transparent;")
    a.append(play)
    a.append(tri)
    _fill_slot(slot, [a], w, h)


def _apply_media(soup, ed, media):
    news_imgs = [media.get("sections", {}).get(s["role"]) for s in ed["sections"]]
    ni = 0
    for slot in soup.select("[data-slot]"):
        name = (slot.get("data-slot") or "").lower()
        if name == "hero" and media.get("hero"):
            _inject_image(soup, slot, media["hero"])
        elif name.startswith("news"):
            img = news_imgs[ni] if ni < len(news_imgs) else None
            ni += 1
            if img:
                _inject_image(soup, slot, img)
        elif name == "video" and media.get("video", {}).get("poster"):
            _inject_video(soup, slot, media["video"]["poster"], media["video"].get("link", "#"))


def _set_text_keep_arrow(el, text: str):
    orig = el.get_text(strip=True)
    arrow = ""
    for a in ("›", "→", "»"):
        if orig.endswith(a):
            arrow = " " + a
            break
    base = text.rstrip(" ›→»")
    el.string = base + arrow


def _role_of(label: str):
    l = label.lower()
    if "lab" in l:
        return "in-the-lab"
    if "field" in l or "note" in l:
        return "field-notes"
    if any(k in l for k in ("craft", "veil", "technique", "white", "vanish", "seam")):
        return "craft"
    return None


def _preceding_kicker(node):
    """Texto de la etiqueta/kicker mas cercana ANTES de un titular (para saber su rol)."""
    prev = node
    for _ in range(12):
        prev = prev.find_previous(True)
        if prev is None:
            break
        if _is_furniture(prev):
            continue
        t = prev.get_text(" ", strip=True)
        if not t:
            continue
        if prev.name in ("span", "small", "p", "div", "b", "em", "h4", "h5", "h6") \
                and 1 <= len(t.split()) <= 7:
            return t
    return ""


def _reorder_sections(sections: list, section_heads: list) -> list:
    """Reordena MIS 3 secciones para empatar el orden de etiquetas del template."""
    detected = [_role_of(_preceding_kicker(h)) for h in section_heads]
    by_role = {s["role"]: s for s in sections}
    if all(d in by_role for d in detected) and len(set(detected)) == 3:
        return [by_role[d] for d in detected]
    return sections  # template sin etiquetas topicas -> orden por defecto


def fill(edition: dict, template_html: str, media: dict | None = None) -> tuple[str, dict]:
    soup = BeautifulSoup(template_html, "html.parser")

    # 1) TITULARES (h1-h4, sin footer)
    hl_nodes = [h for h in soup.find_all(["h1", "h2", "h3", "h4"]) if not _is_furniture(h)]

    # Reordenar mis secciones para que empaten las etiquetas del template (a4, etc.)
    ed = dict(edition)
    if len(hl_nodes) >= 4:
        ed = dict(edition)
        ed["sections"] = _reorder_sections(edition["sections"], hl_nodes[1:4])
    heads, bodies, ctas = _edition_lists(ed)

    for el, tx in zip(hl_nodes, heads):
        _set_headline(el, tx)

    # 2) BODIES (<p> con clase sub/body/body-copy, o parrafo largo; sin footer)
    def is_body(p):
        c = _cls(p)
        if c & FURNITURE:
            return False
        if c & {"sub", "body", "body-copy"}:
            return True
        return len(p.get_text(" ", strip=True).split()) >= 10
    body_nodes = [p for p in soup.find_all("p") if is_body(p)]
    for el, tx in zip(body_nodes, bodies):
        el.string = tx

    # 3) CTAs (<a> cuya clase contiene 'cta')
    cta_nodes = [a for a in soup.find_all("a") if "cta" in " ".join(a.get("class") or [])]
    if ctas:
        for i, a in enumerate(cta_nodes):
            _set_text_keep_arrow(a, ctas[i % len(ctas)])

    # 4) MEDIA (imagenes de posts + video poster/play en los data-slot)
    if media:
        _apply_media(soup, ed, media)

    report = {
        "headlines_in_template": len(hl_nodes), "headlines_filled": min(len(hl_nodes), len(heads)),
        "bodies_in_template": len(body_nodes), "bodies_filled": min(len(body_nodes), len(bodies)),
        "ctas_in_template": len(cta_nodes),
    }
    return str(soup), report


def main():
    ed_path, tpl_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    import json
    edition = json.load(open(ed_path, encoding="utf-8"))
    html = open(tpl_path, encoding="utf-8").read()
    out, report = fill(edition, html)
    open(out_path, "w", encoding="utf-8").write(out)
    print(f"  {tpl_path.split(chr(92))[-1]}: {report}")


if __name__ == "__main__":
    main()
