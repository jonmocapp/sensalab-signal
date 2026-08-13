# -*- coding: utf-8 -*-
"""Shared content for The Signal: fonts, logo, hero, the 12 stories (copy from the editorial
workflow, merged with curated images), kits, archive. Imported by build_blog_b.py, build_articles.py, build_kits.py, build_seo.py."""
import re, base64, pathlib
from io import BytesIO
from PIL import Image
from signal_articles import ART   # auto-generated editorial copy (5 Opus agents)
from signal_covers import COVERS, COVERS2  # on-brand abstract covers (no third-party image IP)
# Carril 2: notas reales que Opus investigó/redactó y set_articles.py 'seteó' (opcional).
try:
    from articles_live import (ART_LIVE, TAX_LIVE, COVERS_LIVE, COVERS2_LIVE, META_LIVE,
                               EDITION as _ED_LIVE, EDITION_DATE as _ED_DATE)
except Exception:
    ART_LIVE, TAX_LIVE, COVERS_LIVE, COVERS2_LIVE, META_LIVE = {}, [], {}, {}, {}
    _ED_LIVE, _ED_DATE = 21, ("02 Aug 2026", "2026-08-02")
ART = {**ART, **ART_LIVE}
COVERS = {**COVERS, **COVERS_LIVE}
COVERS2 = {**COVERS2, **COVERS2_LIVE}

_REPO = pathlib.Path(__file__).resolve().parent          # repo root (cloud-safe, works on GitHub Actions)
_ASSETS = _REPO / "assets"                                # vendored fonts + logo (no OneDrive needed in cloud)
BLOG = _REPO / "blog"
FDIR = (_ASSETS / "fonts") if (_ASSETS / "fonts").exists() else pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\02-Marca\KMR Apparat\KMR Apparat\WEB\WOFF2")
MED  = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\Newsletter\ediciones\2026-08-Signal\substack")
_ISO_SRC = (_ASSETS / "isotipo.png") if (_ASSETS / "isotipo.png").exists() else (MED / "isotipo.png")

import hashlib, shutil
IMGDIR = BLOG/"img"; IMGDIR.mkdir(parents=True, exist_ok=True)
FONTDIR = BLOG/"fonts"; FONTDIR.mkdir(parents=True, exist_ok=True)

def b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()
def _save(data, ext):                       # write once, dedupe by content hash, return relative path
    h = hashlib.md5(data).hexdigest()[:12]
    name = "%s.%s" % (h, ext); p = IMGDIR/name
    if not p.exists(): p.write_bytes(data)
    return "img/" + name
def uri(p):                                 # externalize an asset file as-is
    return _save(pathlib.Path(p).read_bytes(), pathlib.Path(p).suffix.lower().lstrip("."))
def _enc(im, q):
    out = BytesIO(); im.save(out, "JPEG", quality=q, optimize=True)
    return _save(out.getvalue(), "jpg")
def opt_file(p, maxw, q=76):
    im = Image.open(p).convert("RGB")
    if im.width > maxw: im = im.resize((maxw, round(im.height*maxw/im.width)), Image.LANCZOS)
    return _enc(im, q)
def opt_uri(datauri, maxw, q=74):
    raw = base64.b64decode(datauri.split(",",1)[1])
    im = Image.open(BytesIO(raw)).convert("RGB")
    if im.width > maxw: im = im.resize((maxw, round(im.height*maxw/im.width)), Image.LANCZOS)
    return _enc(im, q)
def ed_imgs(n, k=3, maxw=900, q=74):
    t = (BLOG/("signal-%d.html"%n)).read_text(encoding="utf-8", errors="replace")
    u = re.findall(r"data:image/[a-zA-Z0-9.+-]+;base64,[A-Za-z0-9+/=]+", t)
    top = sorted(set(u), key=len, reverse=True)[:k]
    out = []
    for d in top:
        try: out.append(opt_uri(d, maxw, q))
        except Exception: pass
    while len(out) < k and out: out.append(out[-1])
    return out

WEIGHTS = [(500,"KMR-Apparat-Medium.woff2"),(700,"KMR-Apparat-Bold.woff2"),(800,"KMR-Apparat-Heavy.woff2"),(900,"KMR-Apparat-Black.woff2")]
for _w,_f in WEIGHTS:
    if not (FONTDIR/_f).exists(): shutil.copyfile(FDIR/_f, FONTDIR/_f)
FONT = "".join(
 "@font-face{font-family:'Apparat';font-style:normal;font-weight:%d;font-display:swap;src:url(fonts/%s) format('woff2')}" % (w, f)
 for w,f in WEIGHTS)
ISO  = uri(_ISO_SRC)

DATE = {20:("01 Aug 2026","2026-08-01"),19:("18 Jul 2026","2026-07-18"),18:("04 Jul 2026","2026-07-04"),17:("20 Jun 2026","2026-06-20")}
DATE[_ED_LIVE] = _ED_DATE   # fecha de la tanda curada (Carril 2)

# on-brand abstract cover per story (no third-party press photos / watermarks)
IMGMAP = dict(COVERS)

# per-story taxonomy (category label + filter tokens + edition)
TAX = [
 ("hollywood-studio-virtual-production","Experiential","experiential cgi",20),
 ("consumer-ar-glasses-reservations","Spatial & AR","spatial",20),
 ("airline-turned-beach-into-brand","Experiential","experiential concerts",20),
 ("stadium-year-round-attraction","Experiential","experiential",19),
 ("led-volumes-brand-stages","CGI & VFX","cgi",19),
 ("backlash-against-ai-presence","AI","ai",19),
 ("nvidia-real-time-rendering","AI","ai",18),
 ("unreal-engine-gamescom-floor","Gaming","gaming cgi",18),
 ("game-engines-interactive-worlds","Interactive","interactive gaming",18),
 ("sphere-live-venue","Concert visuals","concerts experiential",17),
 ("teamlab-interactive-art","Interactive","interactive experiential",17),
 ("snap-specs-everyday-ar","Spatial & AR","spatial",17),
]
TAX = TAX + TAX_LIVE   # + notas reales curadas (Carril 2)

def _card_summary(dek):
    first = dek.split(". ")[0].strip()
    if not first.endswith("."): first += "."
    return first

def _meta(m):                              # word-aware trim so meta never ends mid-word
    m = m.strip()
    if len(m) <= 158: return m
    cut = m[:158]
    cut = cut[:cut.rfind(" ")].rstrip(" ,.;:")
    return cut + "."

STORIES = []
for slug, cat, tokens, ed in TAX:
    a = ART[slug]
    STORIES.append(dict(
        slug=slug, cat=cat, tokens=tokens, edition=ed, img=IMGMAP[slug],
        headline=a["headline"], dek=a["dek"], summary=_card_summary(a["dek"]),
        body=a["body"], why=a["why"], takeaway=a["takeaway"],
        meta=_meta(a["meta_description"]),
        focus_keyword=a["focus_keyword"], read_minutes=a["read_minutes"],
        source_url=META_LIVE.get(slug, {}).get("source_url", ""),
        source_name=META_LIVE.get(slug, {}).get("source_name", "")))
BY_SLUG = {s["slug"]: s for s in STORIES}

FILTERS = [("All",""),("Experiential","experiential"),("Interactive","interactive"),("AI","ai"),
 ("CGI & VFX","cgi"),("Gaming","gaming"),("Concert visuals","concerts"),("Spatial & AR","spatial")]

# Featured carousel: SOLO notas con FOTO REAL de la fuente (nada de portadas abstractas vacías).
CAROUSEL = [BY_SLUG[s] for s in
 ["tomorrowland-consciencia-ambitious-mainstage-ever","vivid-sydney-2026-expands-day-night",
  "dataland-museum-ai-art-la","world-cup-2026-brand-activations","meow-wolf-phenomenomaly-live"]
 if s in BY_SLUG]

# (name, css class, kit-id, card title, blurb)
KITS = [
 ("retail","k1","k1","10 ideas for retail","Turn a store into a reason to visit, not just a place to buy."),
 ("branding","k2","k2","10 ideas for branding","Make the brand something people can stand inside."),
 ("activations","k3","k3","10 ideas for activations","Launch moments people actually talk about afterward."),
 ("shows","k4","k4","10 ideas for shows","Stage visuals that become the main act, not the backdrop."),
]

FAQ=[("What does SensaLab actually do?","We are a Los Angeles creative lab that designs and builds immersive, interactive experiences for BTL activations, conventions, launches, and corporate events. We combine custom games, sensor based interaction, hybrid installations, and creative content into experiences people take part in and remember."),
 ("What does white label mean for us as an agency?","It means we work invisibly behind your brand. We deliver the concept, the build, and the on-site operation, and you present it all as your own. The client relationship, the credit, and the spotlight stay entirely yours."),
 ("Do you only design, or do you build and run it too?","Both, end to end. We take a project from objective and concept through engineering, build, and live operation on-site. One team owns the experience, so nothing gets lost in a handoff and it holds up under real event conditions."),
 ("Can an experience be reused across multiple events or cities?","Yes. We build replicable systems by default. An experience created for one activation can be adapted and redeployed across other events, cities, and campaigns, so your investment keeps working long after the first show."),
 ("What kind of technology do you use?","Computer vision, real time systems, custom interactive games, CGI, avatars, animation, and motion capture, combined with screens and hardware. We choose the technology to serve the emotion and the goal, so the experience is what people feel."),
 ("How fast can you turn a project around?","Speed and flexibility are part of how we work. We move quickly, adapt to tight timelines and shifting briefs, and we can deliver pitch-ready concepts to help you win the work before full production begins."),
 ("How do we start working with you?","Tell us the objective, the audience, and the moment you need to create. We will shape a concept around it and show you what is possible. Reach out through Work with us, or subscribe to The Signal to see how we think.")]

# services content adapted from the SensaLab one-pager (light site, sentence case, no dashes)
SERVICES = [
 ("what-we-do","What we do",
  "SensaLab is a creative lab designing immersive experiences and interactive dynamics for BTL activations, conventions, and corporate events. Your brand gets attention, but attention is not enough. We turn it into a moment people step into, feel, and remember.",
  [("Custom interactive games","Purpose-built play for activations, launches, and events that pulls people in and keeps them engaged with your brand."),
   ("Sensor based interactions","Computer vision and real time systems that let the audience shape the experience with their body, movement, and presence."),
   ("Hybrid installations","Screens, hardware, and digital content composed into one physical space that reads as a single, coherent experience."),
   ("Creative integrations","CGI, avatars, animation, and motion capture woven into the activation to give your brand a living, responsive presence."),
   ("Pitch-ready concepts","Fully realized ideas you can present, defend, and win with, built to move from concept to floor without losing the vision.")]),
 ("what-makes-us-different","What makes us different",
  "The reasons agencies and brands bring us in, and keep coming back.",
  [("White label by design","We work behind your brand. The credit, the relationship, and the spotlight stay yours."),
   ("Technology in service of emotion","We never lead with the gadget. The tech disappears, and the feeling is what lands."),
   ("Active participation","People do, not just watch. Involvement is what turns a booth into a memory."),
   ("Replicable systems","We build once and redeploy across cities and campaigns, so your investment keeps paying off."),
   ("End to end execution","Concept, build, and on-site operation from one team, with nothing lost in the handoff."),
   ("Speed and flexibility","We move fast and adapt to tight timelines, changing briefs, and real-world constraints.")]),
 ("who-it-is-for","Who it is for",
  "We plug into the teams already shaping the experience, as the interactive layer they can rely on.",
  [("BTL and ATL agencies","The white label technology partner you present as your own, ready to deliver on the floor."),
   ("Brands at conventions and launches","A reason for people to stop, take part, and remember you long after the event."),
   ("Creative teams integrating technology","The build partner who turns ambitious concepts into working, reliable installations."),
   ("HR and internal teams","Immersive internal experiences that make culture, onboarding, and events actually felt."),
   ("Sensory, participatory campaigns","Activations that invite the audience in and reward them for taking part.")]),
]
HOWWEWORK = [("01","Objective","We start with the result you need, so every decision earns its place."),
 ("02","Audience","We map who you want to move and what actually captures them."),
 ("03","Emotion","We define the feeling to spark, because emotion is what gets remembered."),
 ("04","Narrative","We give the experience a story, so participation has meaning."),
 ("05","Interaction","We design how people take part, from first touch to final beat."),
 ("06","Aesthetic","We craft the look and feel to match your brand and the space."),
 ("07","Build","We engineer the tech, hardware, and content into one reliable system."),
 ("08","Operate","We run it on-site and keep it steady, so the experience never breaks.")]
RESULTS = ["Experiences people remember","Real time brand conversation","Reusable content for future campaigns",
 "Longer dwell time and deeper engagement","Voluntary, meaningful interaction","Organic social traction"]

ARCH=[(20,"The week experiential went pro","Tyler Perry's volume, Xreal's Aura, and Southwest on the beach.","signal-20.html",COVERS["hollywood-studio-virtual-production"]),
 (19,"Presence","Real Madrid, LED volumes, and the growing backlash against AI.","signal-19.html",COVERS["stadium-year-round-attraction"]),
 (18,"Real time","NVIDIA, Unreal, and the Gamescom floor.","signal-18.html",COVERS["nvidia-real-time-rendering"]),
 (17,"Immersive","The Sphere, teamLab, and Snap's new Specs.","signal-17.html",COVERS["sphere-live-venue"])]
