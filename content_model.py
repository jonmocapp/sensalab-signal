"""
content_model.py — FUENTE UNICA de contenido del CEREBRO INMERSIVO (plan §6).

Modela cada edicion e historia como CONTENIDO ESTRUCTURADO, independiente del canal.
El mismo objeto `Edition` se renderiza a:
  (a) email HTML — HOY, via to_issue() + templater.build_html (sin tocar el templater);
  (b) blog/web — MANANA, via to_markdown() (post con front-matter) o to_web_html().

FUENTE DE VERDAD: `content/edicion-<n>.json`
  - content_model escribe ahi (save_edition); NADIE edita los HTML generados a mano.
  - El generador de sitio estatico (Astro/11ty; ver notes/BLOG-ROADMAP.md) LEE `content/`
    y construye sensalab.io/blog. El blog es un renderer nuevo, no un sistema nuevo.

FLUJO v2 (cuando exista el sitio):
  issue = writer.write_issue(...)                      # igual que hoy
  ed    = from_issue(issue, number=n, date=now, format_id=fmt, theme=t, candidates=chosen)
  save_edition(ed)                                     # -> content/edicion-<n>.json
  ... CI publica el post en sensalab.io/blog ...       # ANTES de enviar el correo
  set_canonical(ed); save_edition(ed)                  # fija canonical_url
  html = templater.build_html(to_issue(ed, prefer_canonical=True), ...)

NOTA EMAIL V2 (canonical en vez de link de tercero):
  Hoy `to_issue(ed)` pone `link = source_url` (el tercero) — comportamiento identico al
  actual, el templater v1 no se entera. Cuando `canonical_url` exista,
  `to_issue(ed, prefer_canonical=True)` pone `link = <canonical_url>#<slug-historia>`
  (NUESTRO post, ancla por historia) y agrega `source_url` como clave extra en cada
  historia (el templater v1 la ignora). El templater v2 debera:
    - "Leer el analisis ->" apuntando a `link` (nuestro post), y
    - una cita al pie "Via <source>" apuntando a `source_url` (la fuente original).
  Asi el trafico llega a nosotros y el tracking es first-party (plan §5).
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date as date_t, datetime
from html import escape as _esc
from pathlib import Path

from models import normalize_url, ANGLES  # contrato comun del cerebro

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"

SCHEMA_VERSION = 1

# Mismas categorias de entidades que models.Candidate.entities
ENTITY_KEYS = ("brands", "venues", "tech", "agencies", "ip")

SITE_BASE = "https://sensalab.io"
BLOG_PATH = "blog"


# ---------------------------------------------------------------- utilidades

def slugify(text: str, max_len: int = 60) -> str:
    """'Harry Potter llegó a Cosm LA' -> 'harry-potter-llego-a-cosm-la'."""
    t = unicodedata.normalize("NFKD", text or "")
    t = t.encode("ascii", "ignore").decode("ascii").lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    if len(t) > max_len:
        t = t[:max_len].rsplit("-", 1)[0] or t[:max_len]
    return t or "historia"


def _coerce_date(d) -> date_t:
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date_t):
        return d
    if isinstance(d, str) and d:
        return datetime.fromisoformat(d).date()
    raise TypeError(f"Fecha invalida para Edition.date: {d!r}")


def _norm_entities(e: dict | None) -> dict:
    """Garantiza todas las claves de ENTITY_KEYS (listas), preservando extras."""
    out = {k: list((e or {}).get(k, []) or []) for k in ENTITY_KEYS}
    for k, v in (e or {}).items():
        if k not in out:
            out[k] = list(v or [])
    return out


def _yaml_str(s: str) -> str:
    """String escapado para front-matter YAML (comillas dobles)."""
    return '"' + (s or "").replace("\\", "\\\\").replace('"', '\\"') + '"'


# ------------------------------------------------------------------- modelos

@dataclass
class StoryContent:
    """Una historia, independiente del canal (email hoy, post de blog manana)."""
    slug: str
    headline: str
    source_name: str
    source_url: str
    body: str
    lens: str
    angle: str = "straight"            # uno de models.ANGLES
    entities: dict = field(default_factory=lambda: _norm_entities(None))
    image_ref: str | None = None       # data URI, URL o ruta de asset (opcional)

    def __post_init__(self):
        if not self.slug:
            self.slug = slugify(self.headline)
        if self.angle not in ANGLES:   # tolerante: no rompe el pipeline
            self.angle = "straight"
        self.entities = _norm_entities(self.entities)

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "headline": self.headline,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "body": self.body,
            "lens": self.lens,
            "angle": self.angle,
            "entities": self.entities,
            "image_ref": self.image_ref,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StoryContent":
        return cls(
            slug=d.get("slug", ""),
            headline=d.get("headline", ""),
            source_name=d.get("source_name", ""),
            source_url=d.get("source_url", ""),
            body=d.get("body", ""),
            lens=d.get("lens", ""),
            angle=d.get("angle", "straight"),
            entities=d.get("entities") or {},
            image_ref=d.get("image_ref") or None,
        )

    def tags(self) -> list[str]:
        """Entidades -> tags slug del post (dedupe preservando orden)."""
        seen, out = set(), []
        for k in self.entities:
            for name in self.entities[k]:
                t = slugify(str(name))
                if t and t not in seen:
                    seen.add(t)
                    out.append(t)
        return out


@dataclass
class Edition:
    """Una edicion completa de INMERSIVO (fuente unica email + blog)."""
    number: int
    date: date_t
    format_id: str                     # A-digest | B-momento | C-teardown | ... (plan §3)
    theme: str                         # tema/hilo de la semana
    subject: str
    preview_text: str
    intro: str
    signoff: str
    stories: list[StoryContent] = field(default_factory=list)
    canonical_url: str | None = None   # URL de NUESTRO post cuando exista el sitio

    def __post_init__(self):
        self.number = int(self.number)
        self.date = _coerce_date(self.date)

    @property
    def slug(self) -> str:
        """Slug del post: 'inmersivo-07-<tema>'. Estable: es la URL del canonical."""
        tail = slugify(self.theme or self.subject, max_len=48)
        return f"inmersivo-{self.number:02d}" + (f"-{tail}" if tail else "")

    def tags(self) -> list[str]:
        seen, out = set(), []
        for s in self.stories:
            for t in s.tags():
                if t not in seen:
                    seen.add(t)
                    out.append(t)
        return out

    def to_dict(self) -> dict:
        return {
            "schema": SCHEMA_VERSION,
            "number": self.number,
            "slug": self.slug,          # derivado; conveniencia para el generador
            "date": self.date.isoformat(),
            "format_id": self.format_id,
            "theme": self.theme,
            "subject": self.subject,
            "preview_text": self.preview_text,
            "intro": self.intro,
            "signoff": self.signoff,
            "canonical_url": self.canonical_url,
            "stories": [s.to_dict() for s in self.stories],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Edition":
        return cls(
            number=d["number"],
            date=d["date"],
            format_id=d.get("format_id", "A-digest"),
            theme=d.get("theme", ""),
            subject=d.get("subject", ""),
            preview_text=d.get("preview_text", ""),
            intro=d.get("intro", ""),
            signoff=d.get("signoff", ""),
            stories=[StoryContent.from_dict(s) for s in d.get("stories", [])],
            canonical_url=d.get("canonical_url") or None,
        )

    # conveniencia (alias de las funciones de modulo)
    def save(self, content_dir: Path | None = None) -> Path:
        return save_edition(self, content_dir)

    @classmethod
    def load(cls, number: int, content_dir: Path | None = None) -> "Edition":
        return load_edition(number, content_dir)


# --------------------------------------------------- persistencia (content/)

def content_path(number: int, content_dir: Path | None = None) -> Path:
    return (content_dir or CONTENT_DIR) / f"edicion-{int(number)}.json"


def save_edition(edition: Edition, content_dir: Path | None = None) -> Path:
    """Escribe content/edicion-<n>.json (fuente de verdad del blog)."""
    path = content_path(edition.number, content_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(edition.to_dict(), ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    return path


def load_edition(number: int, content_dir: Path | None = None) -> Edition:
    path = content_path(number, content_dir)
    return Edition.from_dict(json.loads(path.read_text(encoding="utf-8")))


def list_editions(content_dir: Path | None = None) -> list[int]:
    """Numeros de edicion disponibles en content/, ordenados."""
    d = content_dir or CONTENT_DIR
    out = []
    if d.is_dir():
        for p in d.glob("edicion-*.json"):
            m = re.fullmatch(r"edicion-(\d+)\.json", p.name)
            if m:
                out.append(int(m.group(1)))
    return sorted(out)


# ------------------------------------- interop con el email actual (issue <->)

def from_issue(issue: dict, number: int, date, format_id: str, theme: str,
               candidates: list | None = None) -> Edition:
    """
    Convierte el dict `issue` del writer/templater actual en una Edition.

    `candidates` (opcional): lista de models.Candidate del pool de la semana; si se
    pasa, cada historia hereda `entities` y `angle` del Candidate con el mismo link
    (match por models.normalize_url). Sin candidates, quedan los defaults.
    """
    by_link = {}
    for c in (candidates or []):
        by_link[normalize_url(getattr(c, "link", ""))] = c

    stories, used = [], set()
    for s in issue.get("stories", []):
        slug = slugify(s.get("headline", ""))
        base, i = slug, 2
        while slug in used:               # slugs unicos dentro de la edicion
            slug = f"{base}-{i}"
            i += 1
        used.add(slug)

        cand = by_link.get(normalize_url(s.get("link", "")))
        stories.append(StoryContent(
            slug=slug,
            headline=s.get("headline", ""),
            source_name=s.get("source", ""),
            source_url=s.get("link", ""),
            body=s.get("body", ""),
            lens=s.get("lens", ""),
            angle=getattr(cand, "angle", "straight") if cand else "straight",
            entities=getattr(cand, "entities", None) if cand else None,
            image_ref=s.get("image") or None,
        ))

    return Edition(
        number=number, date=date, format_id=format_id, theme=theme,
        subject=issue.get("subject", ""),
        preview_text=issue.get("preview_text", ""),
        intro=issue.get("intro", ""),
        signoff=issue.get("signoff", ""),
        stories=stories,
    )


def to_issue(edition: Edition, *, prefer_canonical: bool = False) -> dict:
    """
    Convierte una Edition al dict `issue` que consume templater.build_html HOY.

    - prefer_canonical=False (default): `link` = source_url -> email identico al actual.
    - prefer_canonical=True y canonical_url seteado: `link` = nuestro post (con ancla
      por historia) y se agrega `source_url` (clave extra que el templater v1 ignora;
      el v2 la usa para la cita al pie). Ver NOTA EMAIL V2 arriba.
    """
    use_canonical = prefer_canonical and bool(edition.canonical_url)
    stories = []
    for s in edition.stories:
        d = {
            "headline": s.headline,
            "source": s.source_name,
            "link": canonical_story_url(edition, s) if use_canonical else s.source_url,
            "body": s.body,
            "lens": s.lens,
        }
        if use_canonical:
            d["source_url"] = s.source_url   # cita al pie en el email v2
        if s.image_ref:
            d["image"] = s.image_ref
        stories.append(d)
    return {
        "subject": edition.subject,
        "preview_text": edition.preview_text,
        "intro": edition.intro,
        "stories": stories,
        "signoff": edition.signoff,
    }


# ------------------------------------------------------------------ canonical

def set_canonical(edition: Edition, site_base: str = SITE_BASE,
                  blog_path: str = BLOG_PATH) -> str:
    """Fija canonical_url = https://sensalab.io/blog/<slug>/ y lo devuelve."""
    edition.canonical_url = (
        f"{site_base.rstrip('/')}/{blog_path.strip('/')}/{edition.slug}/")
    return edition.canonical_url


def canonical_story_url(edition: Edition, story: StoryContent) -> str | None:
    """URL de la historia dentro de NUESTRO post (ancla #slug). None sin canonical."""
    if not edition.canonical_url:
        return None
    return f"{edition.canonical_url}#{story.slug}"


# -------------------------------------------------------------- renderer WEB

def to_markdown(edition: Edition) -> str:
    """
    Post de blog en Markdown con front-matter YAML (title, date, slug, tags de
    entities + extras utiles). Listo para content collections de Astro/11ty.
    Cada historia lleva un ancla HTML explicita (<a id="slug">) para que
    canonical_story_url() funcione igual en markdown que en to_web_html().
    """
    fm = [
        "---",
        f"title: {_yaml_str(edition.subject)}",
        f"date: {edition.date.isoformat()}",
        f"slug: {_yaml_str(edition.slug)}",
        f"tags: {json.dumps(edition.tags(), ensure_ascii=False)}",
        f"description: {_yaml_str(edition.preview_text)}",
        f"edition: {edition.number}",
        f"format: {_yaml_str(edition.format_id)}",
        f"theme: {_yaml_str(edition.theme)}",
    ]
    if edition.canonical_url:
        fm.append(f"canonical_url: {_yaml_str(edition.canonical_url)}")
    fm.append("---")

    parts = ["\n".join(fm), "", edition.intro, ""]
    for s in edition.stories:
        parts += [
            f'<a id="{s.slug}"></a>',
            "",
            f"## {s.headline}",
            "",
            s.body,
            "",
            f"> {s.lens}",
            "",
            f"Fuente: [{s.source_name}]({s.source_url})",
            "",
        ]
    parts += ["---", "", f"*{edition.signoff}*", ""]
    return "\n".join(parts)


def to_web_html(edition: Edition) -> str:
    """
    HTML simple de PAGINA (semantico, sin tablas ni CSS inline de email) — distinto
    del email. Es el renderer web interino y el markup de referencia para el
    template del sitio estatico; el sitio definitivo lee content/*.json.
    """
    d = edition.date
    head_canonical = (f'\n<link rel="canonical" href="{_esc(edition.canonical_url)}">'
                      if edition.canonical_url else "")
    secs = []
    for s in edition.stories:
        img = (f'\n    <img src="{_esc(s.image_ref)}" alt="" loading="lazy">'
               if s.image_ref else "")
        secs.append(f"""  <section id="{_esc(s.slug)}">{img}
    <h2>{_esc(s.headline)}</h2>
    <p>{_esc(s.body)}</p>
    <blockquote class="lens">{_esc(s.lens)}</blockquote>
    <p class="source">Fuente: <a href="{_esc(s.source_url)}" target="_blank"
       rel="noopener noreferrer">{_esc(s.source_name)}</a></p>
  </section>""")
    sections = "\n".join(secs)

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(edition.subject)}</title>
<meta name="description" content="{_esc(edition.preview_text)}">{head_canonical}
</head>
<body>
<article>
  <header>
    <p class="kicker">INMERSIVO &middot; #{edition.number:02d} &middot;
      <time datetime="{d.isoformat()}">{d.strftime('%d.%m.%Y')}</time></p>
    <h1>{_esc(edition.subject)}</h1>
    <p class="intro">{_esc(edition.intro)}</p>
  </header>
{sections}
  <footer>
    <p class="signoff"><em>{_esc(edition.signoff)}</em></p>
  </footer>
</article>
</body>
</html>
"""
