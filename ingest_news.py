"""
Ingesta por QUERY del CEREBRO INMERSIVO (ver notes/CEREBRO-INMERSIVO.md, modulo ingest_news).

El bot v1 (sources.py) lee feeds FIJOS. Este modulo agrega la otra pata: busqueda por
query en Google News RSS para reaccionar a ENTIDADES y MOMENTOS ("The Sphere", SIGGRAPH,
activaciones del Mundial...) ademas del RSS fijo.

Patron de red identico a sources._get_feed: requests (timeout + User-Agent de navegador)
y feedparser parseando BYTES (mas robusto que el fetch interno de feedparser).

Expone:
  - STANDING_QUERIES                  registro de queries permanentes (experiencial B2B)
  - search_news(query, ...)           una query -> list[Candidate] (tier="query")
  - queries_for_entities(entities)    entidades/momentos -> queries listas para buscar
  - gather(queries=None, ...)         corre varias queries, junta + dedup + ordena por fecha
  - resolve_link(url)                 best-effort: sigue el redirect de Google News

NOTA sobre links: Google News devuelve links redirect (news.google.com/rss/articles/...)
que resuelven al articulo real al hacer click en un navegador. Sirven tal cual en el
email (el click llega al destino). resolve_link() intenta obtener la URL final por HTTP,
pero Google a veces responde con una pagina intermedia (JS/consent) en vez de un 30x,
asi que la resolucion es best-effort y tolerante a fallo (regresa la URL original).

Sin estado global mutable: solo constantes de configuracion a nivel de modulo.
"""
from __future__ import annotations

import html
import re
import socket
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus, urlsplit

import feedparser
import requests

from models import Candidate

# Red de seguridad (mismo criterio que sources.py): si el fallback usa el fetch interno
# de feedparser (sin timeout propio), esto evita que un feed colgado congele el job.
socket.setdefaulttimeout(30)

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

_TIMEOUT = 25          # seg, para el fetch del feed
_RESOLVE_TIMEOUT = 6   # seg, para resolve_link (corto: es opcional/best-effort)
_PAUSE_BETWEEN_QUERIES = 0.4  # cortesia con Google News al correr varias queries

_GNEWS_SEARCH = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


# ---------------------------------------------------------------------------
# REGISTRO de queries permanentes — experiencial/inmersivo con lente B2B (ICP SL-26).
# Se corren cada edicion ademas del RSS fijo. Frases entre comillas = match exacto.
# ---------------------------------------------------------------------------
STANDING_QUERIES = [
    '"immersive brand activation"',
    '"projection mapping"',
    '"The Sphere" Las Vegas',
    '"experiential marketing"',
    '"AR activation"',
    '"LED volume" virtual production',
    '"immersive art" installation',
    '"brand experience" pop-up',
    '"immersive experience" brand',
    '"interactive installation" brand',
]

# Contexto que ancla una entidad/momento al terreno experiencial (para no traer
# resultados genericos de la entidad: "Nike" solo -> finanzas; "Nike" + contexto -> activaciones).
_ENTITY_CONTEXT = '(immersive OR experiential OR activation OR installation OR "brand experience")'


# ---------------------------------------------------------------------------
# Helpers (mismos criterios que sources.py; duplicados a proposito para mantener
# el modulo autocontenido — sources.py es del bot v1 y no queremos acoplarnos).
# ---------------------------------------------------------------------------
def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_date(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime.fromtimestamp(time.mktime(val), tz=timezone.utc)
            except Exception:
                pass
    return None


def _get_feed(url: str):
    """Descarga con requests (UA navegador, timeout) y parsea bytes; fallback al fetch
    interno de feedparser; None si todo falla. Mismo patron que sources._get_feed."""
    try:
        r = requests.get(url, headers={"User-Agent": _UA,
                         "Accept": "application/rss+xml, application/xml, text/xml, */*"},
                         timeout=_TIMEOUT, allow_redirects=True)
        r.raise_for_status()
        return feedparser.parse(r.content)
    except Exception:
        try:
            return feedparser.parse(url, agent=_UA)
        except Exception:
            return None


def build_search_url(query: str, lookback_days: int | None = None) -> str:
    """URL del RSS de busqueda de Google News. Si lookback_days > 0 agrega el operador
    de recencia `when:Nd` al query (salvo que el query ya traiga un when:)."""
    q = (query or "").strip()
    if lookback_days and lookback_days > 0 and "when:" not in q:
        q = f"{q} when:{int(lookback_days)}d"
    return _GNEWS_SEARCH.format(q=quote_plus(q))


def _split_source(entry) -> tuple[str, str]:
    """Google News titula como 'Headline - Publisher' y ademas manda <source>.
    Regresa (headline_limpio, publisher)."""
    title = _clean(getattr(entry, "title", ""))
    src = getattr(entry, "source", None)
    publisher = _clean(getattr(src, "title", "") or "") if src is not None else ""
    if publisher and title.lower().endswith(" - " + publisher.lower()):
        title = title[: -(len(publisher) + 3)].rstrip()
    elif not publisher and " - " in title:
        # Fallback: sin <source>, el publisher es el ultimo segmento tras ' - '.
        title, publisher = title.rsplit(" - ", 1)
        title, publisher = title.rstrip(), publisher.strip()
    return title, publisher


# ---------------------------------------------------------------------------
# API principal
# ---------------------------------------------------------------------------
def search_news(query: str, lookback_days: int = 7, limit: int = 20) -> list[Candidate]:
    """Busca una query en Google News RSS y regresa Candidates (tier="query").

    - Recencia: `when:{lookback_days}d` en el query + corte local por fecha publicada.
    - Dedup dentro de la query por Candidate.key() (URL normalizada).
    - Conserva el orden del feed (mezcla relevancia/fecha de Google); gather() ya
      reordena por fecha al juntar varias queries.
    - Tolerante a fallo: red caida / feed ilegible -> lista vacia, nunca excepcion.
    """
    if not (query or "").strip():
        return []
    feed = _get_feed(build_search_url(query, lookback_days))
    if feed is None or (getattr(feed, "bozo", 0) and not feed.entries):
        return []

    cutoff = None
    if lookback_days and lookback_days > 0:
        # Media hora de gracia para no tirar notas justo en el borde por drift de reloj.
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days, minutes=30)

    out: list[Candidate] = []
    seen: set[str] = set()
    for entry in feed.entries:
        headline, publisher = _split_source(entry)
        link = getattr(entry, "link", "") or ""
        if not headline or not link:
            continue

        published = _parse_date(entry)
        if cutoff and published and published < cutoff:
            continue

        summary = _clean(getattr(entry, "summary", "") or getattr(entry, "description", ""))
        cand = Candidate(
            headline=headline,
            source=publisher or "Google News",
            link=link,   # redirect de Google News; resuelve al hacer click (ver resolve_link)
            summary=summary,
            published=published,
            tier="query",
        )
        k = cand.key()
        if k in seen:
            continue
        seen.add(k)
        out.append(cand)
        if len(out) >= limit:
            break
    return out


def queries_for_entities(entities: list[str]) -> list[str]:
    """Arma queries de busqueda desde entidades/momentos (ej. ["SIGGRAPH",
    "World Cup activations"]) anclandolas al contexto experiencial para que Google
    no regrese la entidad en cualquier contexto (finanzas, deportes, etc.)."""
    out: list[str] = []
    seen: set[str] = set()
    for ent in entities or []:
        e = _clean(str(ent or ""))
        if not e:
            continue
        base = e if '"' in e else (f'"{e}"' if " " in e else e)
        q = f"{base} {_ENTITY_CONTEXT}"
        key = q.lower()
        if key not in seen:
            seen.add(key)
            out.append(q)
    return out


def gather(queries: list[str] | None = None, lookback_days: int = 7,
           per_query: int = 12, verbose: bool = True) -> list[Candidate]:
    """Corre varias queries (STANDING_QUERIES si queries es None), junta los resultados,
    dedup global por Candidate.key() y ordena por fecha de publicacion (recientes primero,
    sin fecha al final). Una query caida no tumba a las demas."""
    qs = list(queries) if queries is not None else list(STANDING_QUERIES)
    out: list[Candidate] = []
    seen: set[str] = set()
    for i, q in enumerate(qs):
        try:
            cands = search_news(q, lookback_days=lookback_days, limit=per_query)
        except Exception as e:  # search_news ya es tolerante; esto es el doble cinturon
            if verbose:
                print(f"  [!] query {q!r}: error ({e})")
            cands = []
        kept = 0
        for c in cands:
            k = c.key()
            if k in seen:
                continue
            seen.add(k)
            out.append(c)
            kept += 1
        if verbose:
            print(f"  [ok] query {q!r}: {kept} candidatas nuevas ({len(cands)} traidas)")
        if i < len(qs) - 1 and _PAUSE_BETWEEN_QUERIES:
            time.sleep(_PAUSE_BETWEEN_QUERIES)

    out.sort(key=lambda c: c.published or datetime.min.replace(tzinfo=timezone.utc),
             reverse=True)
    return out


def resolve_link(url: str, timeout: float = _RESOLVE_TIMEOUT) -> str:
    """OPCIONAL, best-effort: intenta seguir el redirect de un link de Google News
    (news.google.com/rss/articles/...) y regresar la URL final del articulo.

    Google no siempre responde con un 30x server-side (a veces sirve una pagina
    intermedia con JS/consent), asi que esto puede regresar la URL original. Nunca
    lanza excepcion: cualquier fallo de red -> regresa la URL de entrada tal cual.
    Intenta HEAD primero (barato) y luego GET en streaming (sin bajar el cuerpo).
    """
    if not url:
        return url
    headers = {"User-Agent": _UA}

    def _final_ok(u: str) -> bool:
        try:
            return bool(u) and "news.google.com" not in urlsplit(u).netloc.lower()
        except Exception:
            return False

    try:
        r = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        if _final_ok(r.url):
            return r.url
    except requests.RequestException:
        pass
    try:
        r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True,
                         stream=True)
        final = r.url
        r.close()
        if _final_ok(final):
            return final
    except requests.RequestException:
        pass
    return url


if __name__ == "__main__":
    # Corrida manual de humo: python ingest_news.py
    cands = gather(per_query=5)
    print(f"\n{len(cands)} candidatas unicas:")
    for c in cands[:15]:
        when = c.published.strftime("%Y-%m-%d") if c.published else "s/f"
        print(f"  [{when}] {c.headline}  — {c.source}")
