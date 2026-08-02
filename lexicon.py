"""
Lexico de entidades del CEREBRO INMERSIVO: diccionarios curados + etiquetado.
Llena Candidate.entities (brands/venues/tech/agencies/ip) y deriva Candidate.topic.

Matching por LIMITES DE PALABRA. Los acronimos (AR, VR, LED...) van case-SENSITIVE
para no confundirlos con palabras comunes ("are", "revealed"); el resto case-insensitive.
Amplia las listas libremente: son la memoria de mundo del editor.
"""
from __future__ import annotations

import re

from models import Candidate

# --- Diccionarios (amplia con confianza) ---

BRANDS = [
    "Nike", "Adidas", "Puma", "Netflix", "Disney", "Disney+", "Google", "YouTube", "Amazon",
    "Apple", "Meta", "Facebook", "Instagram", "TikTok", "Snapchat", "Snap", "Coca-Cola", "Coke",
    "Pepsi", "LEGO", "Spotify", "Samsung", "BMW", "Mercedes", "Mercedes-Benz", "Audi", "HBO",
    "Sony", "PlayStation", "Xbox", "Nintendo", "lululemon", "SKIMS", "Fender", "Red Bull",
    "Heineken", "Corona", "Bud Light", "Warner Bros", "Universal", "Paramount", "McDonald's",
    "Gucci", "Louis Vuitton", "Prada", "Balenciaga", "Dior", "Chanel", "L'Oreal", "Sephora",
    "Ulta", "Microsoft", "Intel", "NVIDIA", "Verizon", "Salesforce", "Airbnb", "Uber", "Roblox",
    "Fortnite", "Epic Games", "Riot Games", "Ferrari", "Porsche", "Toyota", "Honda", "Ford",
    "Hyundai", "Kia", "Chevrolet", "Anthropic", "OpenAI", "Nvidia", "AMD", "Qualcomm",
]

VENUES = [
    "The Sphere", "Sphere", "Cosm", "Meow Wolf", "teamLab", "Illuminarium", "ARTECHOUSE",
    "Dreamscape", "Superblue", "Hall des Lumieres", "Outernet", "AREA15", "Area15",
    "Museum of Ice Cream", "Frameless", "Lightroom", "The Lume", "Atelier des Lumieres",
    "Wonderspaces", "Immersive Van Gogh", "Sphere Las Vegas", "Las Vegas Sphere",
]

TECH = [
    "Unreal Engine", "Unreal", "Unity", "Notch", "TouchDesigner", "projection mapping",
    "LED volume", "LED wall", "LED floor", "virtual production", "gaussian splatting",
    "NeRF", "volumetric capture", "volumetric", "spatial computing", "Vision Pro",
    "motion capture", "mocap", "real-time 3D", "real-time", "WebGL", "WebGPU", "WebAR",
    "WebXR", "generative", "holographic", "hologram", "Disguise", "MadMapper", "Resolume",
    "LiDAR", "photogrammetry", "digital twin", "MetaHuman", "drone show", "projection",
    "mapping", "immersive audio", "spatial audio", "haptics", "mixed reality",
    "augmented reality", "virtual reality", "extended reality",
    # acronimos (case-sensitive, ver ACRONYMS)
    "AR", "VR", "XR", "MR", "LED",
]

AGENCIES = [
    "Giant Spoon", "Jack Morton", "MKG", "Mirrored Media", "NVE", "BeCore",
    "Allied Experiential", "Alt Terrain", "Media.Monks", "MediaMonks", "Wasserman", "Superfly",
    "GPJ", "George P. Johnson", "Pico", "Imagination", "Momentum Worldwide", "Sparks",
    "Production Club", "INVNT", "Innovate Marketing Group", "2113 Labs", "Hatch",
    "Civic Entertainment", "Bureau Betak", "Villa Eugenie", "We Are Collider", "TH Experiential",
    "Jack Morton Worldwide", "Legacy", "MAS", "De-Yan",
]

IP = [
    "Harry Potter", "Wizarding World", "Shrek", "Barbie", "Star Wars", "Marvel", "Avengers",
    "Spider-Man", "Pokemon", "Pokemon", "Stranger Things", "Wicked", "Dune", "Avatar",
    "Squid Game", "Batman", "Lord of the Rings", "Game of Thrones", "Minecraft", "Super Mario",
    "Sonic", "Frozen", "Formula 1", "F1", "World Cup", "Olympics", "Super Bowl", "Comic-Con",
]

# Acronimos y siglas: match EXACTO en mayusculas (evita "are"/"revealed"/"mr.")
ACRONYMS = {"AR", "VR", "XR", "MR", "LED", "F1", "GPJ", "MKG", "NVE", "MAS", "NeRF",
            "WebGL", "WebGPU", "WebAR", "WebXR", "LiDAR"}

_CATEGORIES = {"brands": BRANDS, "venues": VENUES, "tech": TECH, "agencies": AGENCIES, "ip": IP}
# Prioridad para elegir el topic dominante
_TOPIC_PRIORITY = ("venues", "ip", "brands", "tech", "agencies")

_STOP = {"the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "with", "at", "by",
         "new", "unveils", "launches", "opens", "brings", "how", "why", "this", "that",
         "its", "into", "from", "as", "is", "are", "will", "las", "los"}


def _compile(term: str) -> re.Pattern:
    flags = 0 if term in ACRONYMS else re.IGNORECASE
    return re.compile(r"\b" + re.escape(term) + r"\b", flags)


_PATTERNS = {cat: [(t, _compile(t)) for t in terms] for cat, terms in _CATEGORIES.items()}


def _slug(text: str, max_words: int = 4) -> str:
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    words = [w for w in words if w not in _STOP][:max_words]
    return "-".join(words) if words else "sin-tema"


def tag(cand: Candidate) -> None:
    """Llena cand.entities buscando cada termino con limites de palabra."""
    blob = f" {cand.headline} {cand.summary} "
    for cat, pats in _PATTERNS.items():
        found = []
        for term, rx in pats:
            if rx.search(blob):
                found.append(term)
        # dedup preservando orden
        cand.entities[cat] = list(dict.fromkeys(found))


def derive_topic(cand: Candidate) -> str:
    """Deriva cand.topic: entidad dominante (venue>ip>brand>tech>agency) o slug del titular."""
    for cat in _TOPIC_PRIORITY:
        ents = cand.entities.get(cat) or []
        if ents:
            cand.topic = _slug(ents[0], max_words=4)
            return cand.topic
    cand.topic = _slug(cand.headline)
    return cand.topic


def tag_all(cands: list[Candidate]) -> None:
    for c in cands:
        tag(c)
        derive_topic(c)
