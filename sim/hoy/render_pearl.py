# -*- coding: utf-8 -*-
"""
Mete las 4 ediciones de hoy DENTRO del template aprobado a1 (Pearl), usando el inyector
real (render_sim.fill). Baja imagenes reales (og:image, email-safe) y las EMBEBE como data
URI -> paginas self-contained (para publicar como Artifact). Slot sin imagen = placeholder
elegante del template (garabato del lazo). NO reinventa diseno.
"""
import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)

from bs4 import BeautifulSoup                     # noqa: E402
from render_sim import fill                      # noqa: E402
from fetch_media import og_image, download       # noqa: E402
import cover_image                                # noqa: E402  (pipeline robusto de portada)

PEARL = r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\designs\design-a1.html"
LOGO = os.path.join(ROOT, "sim", "out", "media", "sensalab-logo.png")
TMP = os.path.join(HERE, "_img")
os.makedirs(TMP, exist_ok=True)


def logo_data_uri():
    with open(LOGO, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def post_process(html):
    """Mete el logo REAL de Jon en el masthead (reemplaza el SVG+wordmark del template)
    y cambia la ubicacion del footer a Los Angeles."""
    soup = BeautifulSoup(html, "html.parser")
    brand = soup.select_one("a.brand")
    if brand:
        for c in list(brand.children):
            c.extract()
        img = soup.new_tag("img", src=logo_data_uri())
        img["alt"] = "SensaLab"
        img["style"] = "height:30px;width:auto;display:block;"
        brand.append(img)
    # FOOTER: sin el icono del lazo (regla de marca: el lazo solo va en el masthead)
    for svg in soup.select("footer svg"):
        svg.decompose()
    # footer: Mexico City -> Los Angeles (todo es LA)
    for meta in soup.select("p.meta"):
        for node in meta.find_all(string=lambda s: s and "Mexico City" in s):
            node.replace_with(node.replace("Mexico City", "Los Angeles"))
    return str(soup)


VIEWPORT = '<meta name="viewport" content="width=device-width,initial-scale=1">'


def ensure_viewport(html):
    """Los templates son fragmentos (sin <head>): en un telefono real, sin viewport meta
    el navegador cae al viewport legacy de ~980px (pagina diminuta). La inyectamos junto
    al charset; si la pagina se publica envuelta (Artifact), es inofensiva/duplicada."""
    if 'name="viewport"' in html:
        return html
    for charset in ('<meta charset="utf-8"/>', '<meta charset="utf-8">'):
        if charset in html:
            return html.replace(charset, charset + "\n" + VIEWPORT, 1)
    return VIEWPORT + "\n" + html

# Candidatas de portada por slot (LISTAS = fallback). El pipeline (cover_image) prueba en
# orden, rechaza logos/gráficos con el filtro de calidad, y hace dedup entre slots.
SOURCES = {
    "07": {
        "hero": ["https://overclock3d.net/news/software/nvidia-releases-their-zorah-neural-rendering-tech-demo/",
                 "https://blogs.nvidia.com/blog/siggraph-news-2026/"],
        "field-notes": ["https://blogs.nvidia.com/blog/racer-rtx-demo/",
                        "https://www.awn.com/news/nvidia-neural-rendering-world-models-and-simulation-keynote-set-siggraph-2026"],
        "in-the-lab": ["https://blogs.nvidia.com/blog/rtxdi-demo/",
                       "https://www.techtimes.com/articles/320990/20260719/siggraph-2026-opens-la-first-games-summit-neural-rendering-bets-chinese-ai-keynote.htm"],
        "craft": ["https://s2026.siggraph.org/about-the-conference/",
                  "https://www.techtimes.com/articles/320990/20260719/siggraph-2026-opens-la-first-games-summit-neural-rendering-bets-chinese-ai-keynote.htm"],
    },
    "08": {
        "hero": ["https://www.nippon.com/en/guide-to-japan/gu900322/",
                 "https://blooloop.com/immersive/news/teamlab-borderless-azabudai-hills-opening/"],
        "field-notes": ["https://www.globenewswire.com/news-release/2026/07/15/3327794/0/en/Wevr-s-Year-of-Global-Firsts-Five-Immersive-Experiences-Three-Continents-One-Million-Audiences-Reached.html"],
        "in-the-lab": ["https://www.fox5vegas.com/2026/01/19/sphere-announces-plans-second-us-venue-east-coast/",
                       "https://www.newsweek.com/second-las-vegas-style-sphere-to-cost-1-7-billion-11965912"],
        "craft": ["https://variety.com/2026/music/news/ar-rahman-arr-immersive-app-apple-vision-pro-1236816469/"],
    },
    "09": {
        "hero": ["https://www.eventmarketer.com/article/world-cup-2026-experiential-10-soccer-activations-beyond-stadiums/",
                 "https://www.promotoss.com/10-interactive-brand-activation-ideas-for-july-2026"],
        "field-notes": ["https://www.eventmarketer.com/article/world-cup-2026-experiential-10-soccer-activations-beyond-stadiums/",
                        "https://www.promotoss.com/10-interactive-brand-activation-ideas-for-july-2026"],
        "in-the-lab": ["https://www.promotoss.com/10-interactive-brand-activation-ideas-for-july-2026",
                       "https://rentforevent.com/blog/event-branding-inspiration/60-brand-activation-ideas-for-2026-ultimate-experiential-guide/"],
        "craft": ["https://rentforevent.com/blog/event-branding-inspiration/60-brand-activation-ideas-for-2026-ultimate-experiential-guide/",
                  "https://www.promotoss.com/10-interactive-brand-activation-ideas-for-july-2026"],
    },
    "10": {
        "hero": ["https://blog.studiovity.com/virtual-production-stages-explained-complete-guide-2026/",
                 "https://trivisionstudios.com/virtual-production-led-wall-how-the-technology-actually-works/"],
        "field-notes": ["https://trivisionstudios.com/virtual-production-led-wall-how-the-technology-actually-works/",
                        "https://beverlyboy.com/film-technology/the-rise-of-virtual-production-how-led-wall-stages-are-changing-filmmaking/"],
        "in-the-lab": ["https://www.npr.org/2026/06/19/nx-s1-5863068/snap-specs-ar-glasses-2195-smartphones",
                       "https://memeburn.com/snap-specs-ar-glasses-2026-2195-price-tag-and-a-big-bet-against-your-smartphone/",
                       "https://www.viture.com/blog/viture-unveils-helix-the-first-ai-safety-glasses-built-on-nvidia-s-xr-ai-solution-at-awe-2026"],
        "craft": ["https://skarredghost.com/2026/07/27/ai-pc-vr-mods-samsung/"],
    },
    "11": {
        "hero": ["https://www.npr.org/2026/06/19/nx-s1-5863068/snap-specs-ar-glasses-2195-smartphones",
                 "https://www.tomsguide.com/news/live/snap-specs-launch-live-latest-updates"],
        "field-notes": ["https://www.tomsguide.com/news/live/snap-specs-launch-live-latest-updates",
                        "https://www.npr.org/2026/06/19/nx-s1-5863068/snap-specs-ar-glasses-2195-smartphones"],
        "in-the-lab": ["https://skarredghost.com/2026/07/27/ai-pc-vr-mods-samsung/",
                       "https://www.viture.com/blog/viture-unveils-helix-the-first-ai-safety-glasses-built-on-nvidia-s-xr-ai-solution-at-awe-2026"],
        "craft": ["https://www.digitalcameraworld.com/tech/extended-reality/snaps-new-ar-camera-glasses-look-incredible-but-will-people-actually-use-them",
                  "https://www.tomsguide.com/news/live/snap-specs-launch-live-latest-updates"],
    },
    "12": {
        "hero": ["https://www.fox5vegas.com/2026/01/19/sphere-announces-plans-second-us-venue-east-coast/",
                 "https://www.newsweek.com/second-las-vegas-style-sphere-to-cost-1-7-billion-11965912"],
        "field-notes": ["https://www.newsweek.com/second-las-vegas-style-sphere-to-cost-1-7-billion-11965912",
                        "https://www.fox5vegas.com/2026/01/19/sphere-announces-plans-second-us-venue-east-coast/"],
        "in-the-lab": ["https://www.costar.com/article/769645513/sony-backs-domed-theaters-as-developers-chase-next-generation-anchors",
                       "https://news.northeastern.edu/2026/01/27/sphere-slated-for-maryland/",
                       "https://www.axios.com/local/atlanta/2024/07/23/cosm-centennial-yards-downtown-sphere"],
        "craft": ["https://eandt.theiet.org/2026/01/26/second-high-tech-entertainment-sphere-coming-us",
                  "https://www.costar.com/article/1059579434/sphere-entertainment-looks-to-follow-las-vegas-performance-with-global-expansion"],
    },
    "13": {
        "hero": ["https://blooloop.com/immersive/news/teamlab-borderless-azabudai-hills-opening/",
                 "https://hypebeast.com/2025/6/ubs-digital-art-museum-teamlab-borderless-hamburg-opening"],
        "field-notes": ["https://blooloop.com/immersive/news/teamlab-borderless-azabudai-hills-opening/",
                        "https://www.gotokyo.org/en/spot/1742/index.html"],
        "in-the-lab": ["https://www.designboom.com/art/ubs-digital-art-museum-2026-europe-largest-teamlab-show-hamburg-06-20-2025/",
                       "https://hypebeast.com/2025/6/ubs-digital-art-museum-teamlab-borderless-hamburg-opening"],
        "craft": ["https://tokyocheapo.com/entertainment/museums-and-exhibitions/mori-building-digital-art-museum-teamlab-borderless/",
                  "https://www.gotokyo.org/en/spot/1742/index.html"],
    },
    "14": {
        "hero": ["https://digiday.com/media/after-an-oversaturation-of-ai-generated-content-creators-authenticity-and-messiness-are-in-high-demand/",
                 "https://www.breef.com/breefingroom/articles/the-ai-marketing-backlash-why-ai-first-brands-are-starting-to-fall-flat"],
        "field-notes": ["https://digiday.com/media/after-an-oversaturation-of-ai-generated-content-creators-authenticity-and-messiness-are-in-high-demand/",
                        "https://thebrandleader.com/authenticity-vs-ai-in-social/"],
        "in-the-lab": ["https://www.breef.com/breefingroom/articles/the-ai-marketing-backlash-why-ai-first-brands-are-starting-to-fall-flat",
                       "https://blog.thewitslab.com/the-ai-content-flood-of-2026-why-brands-are-running-back-to-authentic-human-voices"],
        "craft": ["https://thebrandleader.com/authenticity-vs-ai-in-social/",
                  "https://digiday.com/media/after-an-oversaturation-of-ai-generated-content-creators-authenticity-and-messiness-are-in-high-demand/"],
    },
    "15": {
        "hero": ["https://wnhub.io/news/other/item-51522",
                 "https://www.invenglobal.com/articles/22886/a-vision-for-the-next-generation-game-engine-unreal-fest-2026-chicago-kicks-off"],
        "field-notes": ["https://wnhub.io/news/other/item-51522",
                        "https://games.gg/news/payop-unveils-new-brand-identity-at-gamescom-2026/"],
        "in-the-lab": ["https://www.unrealengine.com/news/state-of-unreal-2026-top-news-from-the-show",
                       "https://www.techtimes.com/articles/318511/20260616/unreal-engine-58-previewed-unreal-fest-chicago-mesh-terrain-faster-lumen-games-film.htm"],
        "craft": ["https://www.invenglobal.com/articles/22886/a-vision-for-the-next-generation-game-engine-unreal-fest-2026-chicago-kicks-off",
                  "https://www.techtimes.com/articles/318511/20260616/unreal-engine-58-previewed-unreal-fest-chicago-mesh-terrain-faster-lumen-games-film.htm"],
    },
    "16": {
        "hero": ["https://www.yankodesign.com/2025/11/20/apple-vision-pro-expands-its-immersive-universe-new-content-and-award-winning-apps-redefine-spatial-computing/",
                 "https://www.apple.com/newsroom/2025/06/visionos-26-introduces-powerful-new-spatial-experiences-for-apple-vision-pro/"],
        "field-notes": ["https://www.yankodesign.com/2025/11/20/apple-vision-pro-expands-its-immersive-universe-new-content-and-award-winning-apps-redefine-spatial-computing/",
                        "https://www.apple.com/newsroom/2025/06/visionos-26-introduces-powerful-new-spatial-experiences-for-apple-vision-pro/"],
        "in-the-lab": ["https://www.apple.com/newsroom/2025/06/visionos-26-introduces-powerful-new-spatial-experiences-for-apple-vision-pro/",
                       "https://www.yankodesign.com/2025/11/20/apple-vision-pro-expands-its-immersive-universe-new-content-and-award-winning-apps-redefine-spatial-computing/"],
        "craft": ["https://www.apple.com/newsroom/2024/04/apple-vision-pro-brings-a-new-era-of-spatial-computing-to-business/",
                  "https://www.yankodesign.com/2025/11/20/apple-vision-pro-expands-its-immersive-universe-new-content-and-award-winning-apps-redefine-spatial-computing/"],
    },
    "17": {
        "hero": ["https://www.newsweek.com/second-las-vegas-style-sphere-to-cost-1-7-billion-11965912",
                 "https://www.fox5vegas.com/2026/01/19/sphere-announces-plans-second-us-venue-east-coast/"],
        "field-notes": ["https://www.fox5vegas.com/2026/01/19/sphere-announces-plans-second-us-venue-east-coast/",
                        "https://www.newsweek.com/second-las-vegas-style-sphere-to-cost-1-7-billion-11965912"],
        "in-the-lab": ["https://blooloop.com/immersive/news/teamlab-borderless-azabudai-hills-opening/",
                       "https://hypebeast.com/2025/6/ubs-digital-art-museum-teamlab-borderless-hamburg-opening"],
        "craft": ["https://www.npr.org/2026/06/19/nx-s1-5863068/snap-specs-ar-glasses-2195-smartphones",
                  "https://www.tomsguide.com/news/live/snap-specs-launch-live-latest-updates"],
    },
    "18": {
        "hero": ["https://blogs.nvidia.com/blog/racer-rtx-demo/",
                 "https://overclock3d.net/news/software/nvidia-releases-their-zorah-neural-rendering-tech-demo/"],
        "field-notes": ["https://overclock3d.net/news/software/nvidia-releases-their-zorah-neural-rendering-tech-demo/",
                        "https://blogs.nvidia.com/blog/rtxdi-demo/"],
        "in-the-lab": ["https://www.unrealengine.com/news/state-of-unreal-2026-top-news-from-the-show",
                       "https://www.techtimes.com/articles/318511/20260616/unreal-engine-58-previewed-unreal-fest-chicago-mesh-terrain-faster-lumen-games-film.htm"],
        "craft": ["https://wnhub.io/news/other/item-51522",
                  "https://www.invenglobal.com/articles/22886/a-vision-for-the-next-generation-game-engine-unreal-fest-2026-chicago-kicks-off"],
    },
    "19": {
        "hero": ["https://www.yankodesign.com/2025/11/20/apple-vision-pro-expands-its-immersive-universe-new-content-and-award-winning-apps-redefine-spatial-computing/",
                 "https://www.apple.com/newsroom/2025/06/visionos-26-introduces-powerful-new-spatial-experiences-for-apple-vision-pro/"],
        "field-notes": ["https://www.apple.com/newsroom/2025/06/visionos-26-introduces-powerful-new-spatial-experiences-for-apple-vision-pro/",
                        "https://www.yankodesign.com/2025/11/20/apple-vision-pro-expands-its-immersive-universe-new-content-and-award-winning-apps-redefine-spatial-computing/"],
        "in-the-lab": ["https://blog.studiovity.com/virtual-production-stages-explained-complete-guide-2026/",
                       "https://trivisionstudios.com/virtual-production-led-wall-how-the-technology-actually-works/"],
        "craft": ["https://digiday.com/media/after-an-oversaturation-of-ai-generated-content-creators-authenticity-and-messiness-are-in-high-demand/",
                  "https://www.breef.com/breefingroom/articles/the-ai-marketing-backlash-why-ai-first-brands-are-starting-to-fall-flat"],
    },
    "20": {
        "hero": ["https://deadline.com/2026/07/tyler-perry-studios-virtual-production-soundstage-synapse-1236983768/",
                 "https://www.cbsnews.com/atlanta/news/tyler-perry-studios-synapse-partner-on-new-virtual-production-soundstage-in-atlanta/"],
        "field-notes": ["https://trivisionstudios.com/virtual-production-led-wall-how-the-technology-actually-works/",
                        "https://blog.studiovity.com/virtual-production-stages-explained-complete-guide-2026/"],
        "in-the-lab": ["https://glassalmanac.com/7-ar-devices-revealed-in-july-2026-that-show-what-changes-next/",
                       "https://www.awexr.com/blog/awe-usa-2026-major-product-launches-new-immersive-experiences-and-industry-announcements"],
        "craft": ["https://www.bizbash.com/experiential-marketing/soak-up-the-sun-summer-themed-brand-activations-we-loved-this-year",
                  "https://www.adweek.com/category/experiential/"],
    },
}

# Bloque video sintetizado por edicion (Pearl tiene slot de video; el motor necesita texto).
VIDEO = {
    "07": {"headline": "Sixty seconds of real time, no render wait", "body": "The through line from the show floor: light that used to bake overnight now moves live. Watch before your next brief."},
    "08": {"headline": "One room, a thousand people, one story", "body": "The clip that stuck: shared immersive is not a demo, it is a venue. Watch with your next activation open."},
    "09": {"headline": "Spectacle you watch versus an experience that answers", "body": "Sixty seconds on the difference between reach and participation. Watch before you sign the next backdrop."},
    "10": {"headline": "Ten locations, one stage, zero flights", "body": "The volume in motion, a brand shoot that never left the room. Watch what the stack makes possible."},
    "11": {"headline": "Two people, one layer, no phones", "body": "The clip that stuck: shared AR by eye contact. Watch before your next activation brief."},
    "12": {"headline": "Standing inside the image", "body": "Sixty seconds of what a wraparound room does to an audience. Watch before you design the next stage."},
    "13": {"headline": "Walk in, and the art moves with you", "body": "The room that reacts to your body, not the wall you look at. Watch with your next brief open."},
    "14": {"headline": "The thing a model cannot flood", "body": "Sixty seconds on why real beats synthetic right now. Watch before you sign the next AI first campaign."},
    "15": {"headline": "One engine, game to activation", "body": "The real time toolset crossing from games into brand work. Watch what it unlocks."},
    "16": {"headline": "A story you stand inside", "body": "Premium content shot for the headset, not the rectangle. Watch what spatial actually feels like."},
    "17": {"headline": "Standing inside the image", "body": "Sixty seconds of what a wraparound room does to an audience. Watch before you design the next stage."},
    "18": {"headline": "One engine, game to activation", "body": "The real time toolset crossing from games into brand work. Watch what it unlocks."},
    "19": {"headline": "A story you stand inside", "body": "Premium content shot for the headset, not the rectangle. Watch what presence feels like."},
    "20": {"headline": "The week the pros moved", "body": "Sixty seconds on a studio, a pair of glasses, and a beach. Watch before your next brief."},
}


def adapt(ed):
    """Convierte el esquema The Signal/Teardown al que espera render_sim (headline+video)."""
    hero = ed["hero"]
    out = {
        "issue_no": ed["issue_no"],
        "hero": {"kicker": hero.get("kicker", ""),
                 "headline": hero.get("statement") or hero.get("headline", ""),
                 "sub": hero.get("sub", "")},
        "video": VIDEO.get(str(ed["issue_no"]), {"headline": "Watch", "body": ""}),
        "invitation": {"headline": ed["invitation"]["headline"], "body": ed["invitation"]["body"]},
    }
    secs = ed.get("sections", [])
    if len(secs) < 3 and ed.get("teardown"):
        td = ed["teardown"]; dr = td.get("done_right", {})
        secs = [
            {"role": "field-notes", "headline": "Record spend, thin interaction",
             "body": td.get("flaw", ""), "cta": "Read the teardown ›"},
            {"role": "in-the-lab", "headline": "The activations that convert answer back",
             "body": td.get("principle", ""), "cta": "See the principle ›"},
            {"role": "craft", "headline": "Meanwhile, done right",
             "body": dr.get("text", ""), "cta": "Inside it ›"},
        ]
    out["sections"] = [{"role": s["role"],
                        "headline": s.get("statement") or s.get("headline", ""),
                        "body": s.get("body", ""),
                        "cta": s.get("cta", "Read more ›")} for s in secs[:3]]
    return out


def data_uri(path):
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def build_media(issue):
    """Portada de cada slot vía el pipeline robusto (cover_image.best_cover): prueba
    candidatas, rechaza logos/gráficos, dedup. Los slots sin portada fresca se rellenan
    del POOL de fotos ya conseguidas en esta edición (reparte y alterna, evita repetir
    adyacente) antes que dejar un placeholder. Devuelve manifest self-contained."""
    src = SOURCES.get(issue, {})
    slots = list(src.keys())
    avoid = set()
    got = {}  # slot -> data URI o None
    for slot in slots:
        dest = os.path.join(TMP, f"{issue}-{slot}")
        cached = [f for f in os.listdir(TMP) if f.startswith(f"{issue}-{slot}.")]
        if cached:
            got[slot] = data_uri(os.path.join(TMP, cached[0]))
            print(f"    {issue}/{slot}: cache")
            continue
        fname, img_url, page = cover_image.best_cover(src[slot], dest, avoid)
        if fname:
            got[slot] = data_uri(os.path.join(TMP, fname))
            print(f"    {issue}/{slot}: {img_url[:58]}")
        else:
            got[slot] = None
            print(f"    {issue}/{slot}: sin portada fresca (se rellena del pool)")

    # pool de fotos únicas conseguidas, en orden
    pool = []
    for slot in slots:
        if got[slot] and got[slot] not in pool:
            pool.append(got[slot])
    # rellena los None ciclando el pool, evitando igualar a los VECINOS (el anterior y el
    # siguiente ya resuelto): antes solo se miraba el anterior, y un primer slot vacio
    # podia quedar identico al slot siguiente ya lleno.
    if pool:
        pi = 0
        for k, slot in enumerate(slots):
            if got[slot] is not None:
                continue
            prev_img = got[slots[k - 1]] if k > 0 else None
            next_img = got[slots[k + 1]] if k + 1 < len(slots) else None
            choice = pool[pi % len(pool)]
            for _ in range(len(pool)):  # acotado: da la vuelta al pool una vez
                if choice != prev_img and choice != next_img:
                    break
                pi += 1
                choice = pool[pi % len(pool)]
            got[slot] = choice
            pi += 1

    media = {"hero": None, "sections": {}, "video": {}}
    for slot in slots:
        if got.get(slot):
            if slot == "hero":
                media["hero"] = got[slot]
            else:
                media["sections"][slot] = got[slot]
    # THUMBNAIL de video: usa el hero como poster del reel (arriba/abajo = máxima separación).
    poster = media["hero"] or media["sections"].get("field-notes")
    if poster:
        media["video"] = {"poster": poster, "link": "#"}
    return media


# Labels del template en title case -> sentence case (Jon: todo normal, sin mayus).
_SENTENCE_CASE = [
    ("Field Notes", "Field notes"),
    ("In the Lab", "In the lab"),
    ("One take, no cuts", "one take, no cuts"),
]


def main():
    tpl = open(PEARL, encoding="utf-8").read()
    tpl = tpl.replace("text-transform:uppercase", "text-transform:none")  # sin MAYUS en labels
    files = sorted(f for f in os.listdir(HERE) if f.startswith("ed") and f.endswith(".json"))
    outs = []
    for f in files:
        ed = json.load(open(os.path.join(HERE, f), encoding="utf-8"))
        issue = str(ed["issue_no"])
        print(f"  edicion #{issue} ({f}):")
        media = build_media(issue)
        adapted = adapt(ed)
        html, report = fill(adapted, tpl, media=media)
        html = html.replace("ISSUE 01 · JUL 2026", f"Issue {issue} · Jul 2026")  # numero real, sentence case
        html = post_process(html)  # logo real + Los Angeles
        html = ensure_viewport(html)  # web real: sin esto un telefono renderiza a ~980px
        for a, b in _SENTENCE_CASE:
            html = html.replace(a, b)
        out = os.path.join(HERE, f"pearl-{issue}.html")
        open(out, "w", encoding="utf-8").write(html)
        outs.append(out)
        print(f"    -> pearl-{issue}.html  (H{report['headlines_filled']}/{report['headlines_in_template']} "
              f"B{report['bodies_filled']}/{report['bodies_in_template']})")
    print("\nlisto:", ", ".join(os.path.basename(o) for o in outs))


if __name__ == "__main__":
    main()
