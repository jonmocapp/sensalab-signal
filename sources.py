"""
Fuentes RSS + filtro de keywords + deteccion geografica + scoring.

Fuentes decididas (ver Fuentes-RSS-y-veredicto.md):
  CORE   (cada edicion): Event Marketer, BizBash
  ROTATE (filtro estricto): Adweek, The Art Newspaper, Social Media Today

Matching por LIMITES DE PALABRA (regex) para evitar falsos positivos como
" ar " dentro de otra palabra o "led" dentro de "balloons".
"""
from __future__ import annotations

import html
import re
import socket
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from urllib.parse import urlsplit, urlunsplit

import feedparser
import requests

# Red de seguridad: si el fallback usa el fetch interno de feedparser (sin timeout
# propio), este default evita que un feed colgado congele el job de CI.
socket.setdefaulttimeout(30)

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

SOURCES = [
    {"name": "Event Marketer",     "url": "https://www.eventmarketer.com/feed/",         "tier": "core"},
    {"name": "BizBash",            "url": "https://www.bizbash.com/rss.xml",             "tier": "core"},
    {"name": "Adweek",             "url": "https://www.adweek.com/feed/",                "tier": "rotate"},
    {"name": "The Art Newspaper",  "url": "https://www.theartnewspaper.com/rss.xml",     "tier": "rotate"},
    {"name": "Social Media Today", "url": "https://www.socialmediatoday.com/feeds/news/","tier": "rotate"},
]

# STRONG = senal alta de experiencial/inmersivo. Una fuente ROTATE debe tener >=1 de estas.
STRONG = [
    "experiential", "immersive", "immersion", "projection mapping", "activation",
    "brand experience", "installation", "augmented reality", "mixed reality",
    "virtual reality", "extended reality", "spatial computing", "hologram",
    "holographic", "the sphere", "led volume", "virtual production", "generative art",
    "digital art", "multisensory", "sensory", "pop-up", "popup", "fan experience",
    "flagship experience", "metaverse", r"\b(ar|vr|xr)\b", r"\bled\b",
]

# INCLUDE = senal media (vocabulario de la industria de eventos/experiencias).
# Basta con >=1 para una fuente CORE (EM/BizBash ya vienen curadas al sector).
INCLUDE = [
    "experience", "event", "events", "exhibit", "exhibition", "retail", "stunt",
    "wearable", "real-time", "unreal", "unity", "3d", "interactive", "interactivity",
    "brand", "campaign", "launch", "showcase", "spectacle", "gala", "conference",
    "summit", "trade show", "expo", "sponsor", "sponsorship", "venue", "attendee",
    "guests", "party", "festival", "booth", "stage", "production", "display",
    "projection", "concert", "tour", "premiere", "spatial", "design",
]

# EXCLUDE = ruido puro (finanzas, ad-tech, corporativo). Mata la nota aunque tenga keyword.
# Nota: solo terminos claramente NO-experienciales, para no matar notas legitimas.
EXCLUDE = [
    "capex", "earnings", "guidance", "quarterly", "ipo", "valuation", "funding round",
    "layoffs", "job cuts", "lawsuit", "antitrust", "tariff", "obituary", "op-ed",
    "opinion:", "horoscope", "recipe", "gift guide", "coupon", "deal of the day",
    "conversion rate", "conversions", "click-through", "cpm", "algorithm update",
    "privacy policy", "subscription price", "ad spend", "ad revenue", "stock price",
    "how to save",
]

# GEO (eventos): LA / Miami / NY / Vegas. Global permitido para tech cool.
GEO = [
    "los angeles", "hollywood", "santa monica", "culver city", r"\bl\.a\.\b",
    "miami", "wynwood", "miami beach", "brickell",
    "new york", r"\bnyc\b", r"\bn\.y\.\b", "manhattan", "brooklyn", "times square",
    "las vegas", r"\bvegas\b", "the strip", r"\bsphere\b",
]


def _compile(terms: list[str]) -> list[re.Pattern]:
    pats = []
    for t in terms:
        # Si ya trae \b lo usamos tal cual; si no, envolvemos en limites de palabra.
        rx = t if "\\b" in t else r"\b" + re.escape(t) + r"\b"
        pats.append(re.compile(rx, re.IGNORECASE))
    return pats


_STRONG_RX = _compile(STRONG)
_INCLUDE_RX = _compile(INCLUDE)
_EXCLUDE_RX = _compile(EXCLUDE)
_GEO_RX = _compile(GEO)


@dataclass
class Story:
    headline: str
    source: str
    link: str
    summary: str
    published: datetime | None
    tier: str
    score: int = 0
    geo: bool = False
    tags: list = field(default_factory=list)

    def key(self) -> str:
        return _norm_url(self.link) or self.headline.strip().lower()


def _norm_url(u: str) -> str:
    """Normaliza la URL para dedup: quita query (utm_*), fragmento y slash final."""
    try:
        p = urlsplit((u or "").strip())
        return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), "", "")).lower()
    except Exception:
        return (u or "").strip().lower()


def _get_feed(url: str):
    """Descarga con requests (mas robusto que el fetch interno de feedparser) y parsea bytes."""
    try:
        r = requests.get(url, headers={"User-Agent": _UA,
                         "Accept": "application/rss+xml, application/xml, text/xml, */*"},
                         timeout=25, allow_redirects=True)
        r.raise_for_status()
        return feedparser.parse(r.content)
    except Exception:
        return feedparser.parse(url, agent=_UA)


def _parse_date(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime.fromtimestamp(time.mktime(val), tz=timezone.utc)
            except Exception:
                pass
    return None


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)  # decodifica &#8217; &amp; etc. (no dejar basura tipografica)
    return re.sub(r"\s+", " ", text).strip()


def _count(pats: list[re.Pattern], text: str) -> int:
    return sum(1 for p in pats if p.search(text))


def fetch_all(lookback_days: int = 10, verbose: bool = True) -> list[Story]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    out: list[Story] = []
    seen_keys: set[str] = set()  # dedup dentro de la misma corrida
    core_health: dict[str, int] = {}

    for src in SOURCES:
        try:
            feed = _get_feed(src["url"])
        except Exception as e:
            if verbose:
                print(f"  [!] {src['name']}: error de red ({e})")
            if src["tier"] == "core":
                core_health[src["name"]] = 0
            continue

        if getattr(feed, "bozo", 0) and not feed.entries:
            if verbose:
                print(f"  [!] {src['name']}: feed vacio o ilegible")
            if src["tier"] == "core":
                core_health[src["name"]] = 0
            continue

        kept = 0
        for entry in feed.entries:
            title = _clean(getattr(entry, "title", ""))
            summary = _clean(getattr(entry, "summary", "") or getattr(entry, "description", ""))
            link = getattr(entry, "link", "")
            if not title:
                continue

            pub = _parse_date(entry)
            if pub and pub < cutoff:
                continue

            blob = f" {title} {summary} "

            # EXCLUDE mata cualquier nota (ruido finanzas/adtech/corporativo)
            if _count(_EXCLUDE_RX, blob):
                continue

            strong = _count(_STRONG_RX, blob)
            inc = _count(_INCLUDE_RX, blob)

            # Puerta de calidad:
            #   ROTATE necesita >=1 keyword FUERTE (si no, es ruido tipo "Google Capex").
            #   CORE (EM/BizBash, ya curadas) pasa con >=1 fuerte O >=2 medias.
            if src["tier"] == "rotate":
                if strong < 1:
                    continue
            else:
                if strong < 1 and inc < 2:
                    continue

            score = strong * 15 + inc * 6
            if src["tier"] == "core":
                score += 5

            key = _norm_url(link) or title.lower()
            if key in seen_keys:
                continue
            seen_keys.add(key)

            geo = _count(_GEO_RX, blob) > 0
            if geo:
                score += 12

            out.append(Story(headline=title, source=src["name"], link=link, summary=summary,
                             published=pub, tier=src["tier"], score=score, geo=geo,
                             tags=[]))
            kept += 1

        if src["tier"] == "core":
            core_health[src["name"]] = kept
        if verbose:
            print(f"  [ok] {src['name']}: {kept} candidatas")

    # Alerta ruidosa si una fuente CORE viene vacia (la espina dorsal editorial)
    dead_core = [n for n, k in core_health.items() if k == 0]
    if dead_core and verbose:
        print(f"  [ALERTA] Fuente(s) CORE sin material: {', '.join(dead_core)}. "
              f"Revisa el feed (puede estar caido o haber cambiado de URL).")

    out.sort(key=lambda s: (s.score, s.published or datetime.min.replace(tzinfo=timezone.utc)),
             reverse=True)
    return out
