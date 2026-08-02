"""
Contrato de datos compartido del CEREBRO INMERSIVO.
Todos los modulos del motor editorial usan Candidate (ver notes/CEREBRO-INMERSIVO.md).
Sin dependencias de otros modulos del proyecto: es la base comun.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit


def normalize_url(u: str) -> str:
    """Normaliza URL para dedup: quita query (utm_*), fragmento y slash final."""
    try:
        p = urlsplit((u or "").strip())
        return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), "", "")).lower()
    except Exception:
        return (u or "").strip().lower()


# Angulos editoriales validos (ver composer.py / formatos)
ANGLES = ("straight", "bar-moved", "steal-this", "teardown", "tech-unlock", "recap")

# Sub-scores que rellenan los distintos modulos (scoring.py combina en "total")
SCORE_KEYS = ("relevance", "b2b", "timeliness", "momentum", "novelty",
              "authority", "talkability", "angle", "geo", "total")


@dataclass
class Candidate:
    # --- ingesta ---
    headline: str
    source: str
    link: str
    summary: str = ""
    published: datetime | None = None
    tier: str = "query"           # core | rotate | query
    geo: bool = False

    # --- enriquecido por el cerebro ---
    entities: dict = field(default_factory=lambda: {
        "brands": [], "venues": [], "tech": [], "agencies": [], "ip": []})
    topic: str = ""               # tema/cluster normalizado (picos + anti-repeticion)
    scores: dict = field(default_factory=dict)   # ver SCORE_KEYS
    angle: str = "straight"       # uno de ANGLES
    moment: str | None = None     # id de tentpole/momento si aplica

    def key(self) -> str:
        return normalize_url(self.link) or self.headline.strip().lower()

    @property
    def total(self) -> float:
        return float(self.scores.get("total", 0.0))

    @classmethod
    def from_story(cls, story) -> "Candidate":
        """Convierte un sources.Story (bot v1) en Candidate (cerebro v2)."""
        return cls(
            headline=getattr(story, "headline", ""),
            source=getattr(story, "source", ""),
            link=getattr(story, "link", ""),
            summary=getattr(story, "summary", ""),
            published=getattr(story, "published", None),
            tier=getattr(story, "tier", "query"),
            geo=getattr(story, "geo", False),
        )

    def all_entities(self) -> list[str]:
        out = []
        for v in self.entities.values():
            out.extend(v)
        return out
