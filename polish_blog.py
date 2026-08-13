# -*- coding: utf-8 -*-
"""polish_blog.py — las reglas duras de Jon, aplicadas al blog/ generado (post-procesador).
pipeline.py lo corre DESPUES de build_articles/build_blog_b/build_seo, para que la
automatizacion nunca regrese el blog al estado viejo. Idempotente (corre N veces sin danio).

Reglas (2026-08-13):
 1. Logo del nav = wordmark AVIF de la pagina web (mismo asset).
 2. LOCK DE PORTADAS: las portadas SIEMPRE son las imagenes de INTERNET de la
    fuente (og:image via set_articles USE_SOURCE_IMAGES=True). PROHIBIDO
    sustituirlas por assets propios de Jon (orden directa 2026-08-13).
    Ninguna noticia sin imagen: el salvavidas JS elimina la card si su imagen falla.
 3. Slide 1 del carrusel = poster "Welcome to The Signal." (placeholder de marca
    hasta que Jon entregue su imagen).
 4. CTA del kit = pill blanco grande (.kgo).
 5. FAQ oculto.
 6. Nav con "Return to website" (../ = raiz del sitio integrado), sin FAQ.
 7. Sin contador de stories; maximo 25 en el grid.
 8. Sin parrafo corporativo en el hero (el About del footer SI se queda).
 + fondo lavanda premium, links #archive -> #latest, noscript fallback.
"""
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parent
BLOG = BASE / "blog"

LOGO_AVIF = 'data:image/avif;base64,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'  # inyectado por tools: wordmark de la web como data URI
LAV = "linear-gradient(180deg,#F3F1F8,#EAE7F2) fixed"

WELCOME = (
    '<div class="slide on" aria-hidden="false">'
    '<div style="position:absolute;inset:0;background:linear-gradient(130deg,#1C1956 0%,#3D76E8 42%,#6060BE 68%,#B55CB7 100%)"></div>'
    '<div class="fscrim"></div><div class="fcard"><span class="fchip">SensaLab &middot; The Signal</span>'
    '<div class="fh">Welcome to The Signal.</div>'
    '<p>Our read on immersive, experiential and real time work. The moves worth your week, each with a clear why.</p>'
    '<a class="go" href="#latest">Browse the stories &#8594;</a></div></div>')

JONFIX = (
    '<style id="jonfix">#fcount{display:none!important}#faq{display:none!important}'
    '.kit .kgo{display:inline-flex;align-items:center;gap:8px;background:#F4F3F3;color:#1C1956;'
    'font-weight:800;font-size:15.5px;padding:13px 26px;border-radius:999px;margin-top:16px;'
    'align-self:flex-start;box-shadow:0 12px 28px rgba(11,15,15,.28);transition:transform .2s}'
    '.kit:hover .kgo{transform:translateX(5px) scale(1.05)}</style>')

GUARD = (
    '<script id="jonguard">(function(){'
    'document.querySelectorAll("#grid .card .ph").forEach(function(ph){'
    'var m=(ph.getAttribute("style")||"").match(/url\\(([^)]+)\\)/);if(!m)return;'
    'var im=new Image();im.onerror=function(){var c=ph.closest(".card");if(c)c.remove();};'
    'im.src=m[1].replace(/["\\x27]/g,"");});'
    'document.querySelectorAll(".slide img").forEach(function(g){'
    'g.addEventListener("error",function(){var s=g.closest(".slide");'
    'if(s&&!s.classList.contains("on"))s.remove();});});})();</script>')



def recolor_all():
    for p in BLOG.glob("*.html"):
        t = p.read_text(encoding="utf-8", errors="ignore")
        n = t.replace("background:#EEF1FB", "background:" + LAV)
        n = n.replace("index.html#archive", "index.html#latest")
        if n != t:
            p.write_text(n, encoding="utf-8")


def polish_index():
    p = BLOG / "index.html"
    if not p.exists():
        print("[polish] no hay blog/index.html"); return
    t = p.read_text(encoding="utf-8", errors="ignore")
    if LOGO_AVIF.startswith("data:"):
        t = re.sub(r'(<a class="brand" href="#top"><img src=")[^"]+(")',
                   lambda m: m.group(1) + LOGO_AVIF + m.group(2), t, count=1)
        t = t.replace('alt="SensaLab logo">', 'alt="SensaLab" style="height:20px;width:auto">', 1)
    t = t.replace('<a href="#faq">FAQ</a></nav>', '<a href="../">Return to website</a></nav>', 1)
    t = t.replace('<a href="#faq">FAQ</a><a href="#subscribe">',
                  '<a href="../">Return to website</a><a href="#subscribe">', 1)
    if "Welcome to The Signal." not in t:
        t = t.replace('<div class="slide on" aria-hidden="false">',
                      WELCOME + '<div class="slide" aria-hidden="true">', 1)
    t = re.sub(r'<p class="dek">(?:<b>)?SensaLab is a Los Angeles experiential creative studio.*?</p>',
               '', t, count=1, flags=re.S)
    cards = re.findall(r'<article class="card[^"]*".*?</article>', t, re.S)
    for c in cards[25:]:
        t = t.replace(c, "", 1)
    if 'id="jonfix"' not in t:
        t = t.replace("</head>", JONFIX + "</head>", 1)
    if "<noscript>" not in t:
        t = t.replace("</head>",
                      "<noscript><style>.rev{opacity:1!important;transform:none!important}</style></noscript></head>", 1)
    if 'id="jonguard"' not in t:
        t = t.replace("</body>", GUARD + "</body>", 1)
    p.write_text(t, encoding="utf-8")


def run():
    recolor_all()
    polish_index()
    n = len(re.findall(r'<article class="card[^"]*"',
                       (BLOG / "index.html").read_text(encoding="utf-8", errors="ignore")))
    print(f"[polish] listo: reglas de Jon aplicadas ({n} stories en grid, max 25)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
