# -*- coding: utf-8 -*-
"""
Media ingestion: para cada historia, encuentra la imagen real del POST (og:image de la
fuente citada) y el VIDEO (poster + link). Baja todo local a sim/out/media/ y escribe un
manifest. Esto es el "buscar posts y videos" del cerebro (por ahora vía og:image de las
fuentes que ya trae la edicion; extensible a image/video search).
"""
import json, os, re, requests
from io import BytesIO

try:
    from PIL import Image
    _PIL = True
except Exception:  # PIL ausente: se degrada a guardar crudo (ver download)
    _PIL = False

BASE = os.path.dirname(os.path.abspath(__file__))
OUTMEDIA = os.path.join(BASE, "sim", "out", "media")
os.makedirs(OUTMEDIA, exist_ok=True)
import time

# Reglas email-safe: nada de .webp (Outlook no lo renderiza), ancho tope y peso tope.
MAXW, MAXKB = 1280, 200
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept": "text/html,image/avif,image/webp,image/png,image/*,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9",
      "Referer": "https://www.google.com/"}


def _get(url, **kw):
    last = None
    for i in range(3):
        try:
            return requests.get(url, headers=UA, timeout=30, allow_redirects=True, **kw)
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise last

# Mapa slot -> indice en el arreglo sources[] de cada edicion + config de video.
PLAN = {
    "A": {"hero": 2, "field-notes": 0, "in-the-lab": 3, "craft": 6,
          "video_src_idx": 2,
          "video_link": "https://www.fox13seattle.com/video/fmc-tc4eswursuf4mz31"},
    "B": {"hero": 0, "field-notes": 0, "in-the-lab": 3, "craft": 8,
          "video_poster_url": "https://cdn.filmshrine.com/uploads/2026/06/shrek-5-teaser-trailer.jpg",
          "video_link": "https://www.youtube.com/results?search_query=Shrek+5+official+teaser+trailer"},
}


def og_image(page_url):
    r = _get(page_url)
    r.raise_for_status()
    for pat in [r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
                r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)']:
        m = re.search(pat, r.text, re.I)
        if m:
            return m.group(1)
    return None


def save_image(im, dest_noext):
    """Deja una imagen PIL ya abierta EMAIL-SAFE: limita ancho a MAXW, conserva PNG solo
    si trae transparencia (aplana a JPG si pesa), y comprime JPG a <=MAXKB. Devuelve basename."""
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    if has_alpha:
        path = dest_noext + ".png"
        im.save(path, "PNG", optimize=True)
        if os.path.getsize(path) > MAXKB * 1024:  # PNG opaco pesado -> aplana y pasa a JPG
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im.convert("RGBA"), mask=im.convert("RGBA").split()[-1])
            os.remove(path)
            path = dest_noext + ".jpg"
            im = bg
            has_alpha = False
    if not has_alpha:
        path = dest_noext + ".jpg"
        im = im.convert("RGB")
        q = 85
        im.save(path, "JPEG", quality=q, optimize=True, progressive=True)
        while os.path.getsize(path) > MAXKB * 1024 and q > 40:
            q -= 8
            im.save(path, "JPEG", quality=q, optimize=True, progressive=True)
    return os.path.basename(path)


def download(img_url, dest_noext):
    """Baja la imagen y la deja EMAIL-SAFE (via save_image). Devuelve el basename final."""
    r = _get(img_url)
    r.raise_for_status()
    data = r.content
    ct = r.headers.get("content-type", "").lower()

    if not _PIL:
        ext = ".png" if ("png" in ct or img_url.lower().endswith(".png")) else ".jpg"
        path = dest_noext + ext
        with open(path, "wb") as f:
            f.write(data)
        return os.path.basename(path)

    try:
        im = Image.open(BytesIO(data))
        im.load()
    except Exception:
        path = dest_noext + ".jpg"
        with open(path, "wb") as f:
            f.write(data)
        return os.path.basename(path)

    return save_image(im, dest_noext)


def resolve(ed_key):
    ed = json.load(open(os.path.join(BASE, "sim", f"edicion-{ed_key}.json"), encoding="utf-8"))
    srcs = ed["sources"]
    cfg = PLAN[ed_key]
    man = {"hero": None, "sections": {}, "video": {}}

    # imagenes de secciones + hero (og:image de la fuente)
    for slot in ("hero", "field-notes", "in-the-lab", "craft"):
        try:
            page = srcs[cfg[slot]]
            img = og_image(page)
            if img:
                fname = download(img, os.path.join(OUTMEDIA, f"{ed_key}-{slot}"))
                key = "hero" if slot == "hero" else None
                if key == "hero":
                    man["hero"] = f"media/{fname}"
                else:
                    man["sections"][slot] = f"media/{fname}"
                print(f"  {ed_key}/{slot}: {fname}")
            else:
                print(f"  {ed_key}/{slot}: sin og:image en {page[:50]}")
        except Exception as e:
            print(f"  {ed_key}/{slot}: ERROR {type(e).__name__}: {e}")

    # video: poster (url directa o og:image de la fuente) + link
    try:
        if cfg.get("video_poster_url"):
            poster = cfg["video_poster_url"]
        else:
            poster = og_image(srcs[cfg["video_src_idx"]])
        if poster:
            fname = download(poster, os.path.join(OUTMEDIA, f"{ed_key}-video"))
            man["video"] = {"poster": f"media/{fname}", "link": cfg["video_link"]}
            print(f"  {ed_key}/video: {fname}")
    except Exception as e:
        # Fallback: reusa la imagen de craft como poster del video (para no dejar el slot vacio)
        fallback = man["sections"].get("craft") or man.get("hero")
        if fallback:
            man["video"] = {"poster": fallback, "link": cfg["video_link"]}
            print(f"  {ed_key}/video: fallback -> {fallback} ({type(e).__name__})")
        else:
            print(f"  {ed_key}/video: ERROR {type(e).__name__}: {e}")

    return man


if __name__ == "__main__":
    manifest = {k: resolve(k) for k in ("A", "B")}
    mpath = os.path.join(OUTMEDIA, "manifest.json")
    json.dump(manifest, open(mpath, "w", encoding="utf-8"), indent=2)
    print(f"\nmanifest -> {mpath}")
    print(json.dumps(manifest, indent=2))
