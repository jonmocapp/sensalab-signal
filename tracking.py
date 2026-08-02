"""
tracking.py — Módulo de MEDICIÓN del Cerebro Inmersivo (notes/CEREBRO-INMERSIVO.md §5).

Este módulo NO envía correos. Sólo instrumenta y mide:

  1. LINKS        wrap_link() añade UTM a cada link de historia; link_attrs() da el
                  fragmento target/rel correcto para B2B (nueva pestaña).
  2. BREVO STATS  fetch_campaign_stats() lee métricas por campaña de la API real de
                  Brevo (GET /v3/emailCampaigns/{id}; auth header "api-key").
  3. WEBHOOKS     parse_webhook() normaliza los eventos marketing de Brevo
                  (delivered / opened / click / soft_bounce / hard_bounce / unsubscribe).
  4. ENGAGEMENT   store JSON data/subscribers.json: record_event(), engagement_score(),
                  segment() -> engaged / dormant / new (+ lost).
  5. FIRST-PARTY  tokens HMAC para el redirect futuro go.sensalab.io/c/<token>
                  (make_click_token / verify_click_token / redirect_url).
  6. LOOP         performance_by_topic() agrega clicks por topic/formato para
                  realimentar scoring.adjust_weights (sólo produce el dict).

Endpoints de Brevo VERIFICADOS contra developers.brevo.com (2026-07):
  - GET  https://api.brevo.com/v3/emailCampaigns/{campaignId}
         query ?statistics= globalStats | linksStats | statsByDomain | statsByDevice
         | statsByBrowser. La respuesta incluye statistics.globalStats con: sent,
         delivered, deferred, softBounces, hardBounces, viewed, uniqueViews, clickers,
         uniqueClicks, complaints, unsubscriptions, trackableViews, estimatedViews.
  - GET  https://api.brevo.com/v3/emailCampaigns          (listar campañas)
  - POST https://api.brevo.com/v3/webhooks                (registrar webhook,
         type="marketing", events: delivered/opened/click/hardBounce/softBounce/
         unsubscribed/spam/listAddition)
  Rate limit: 429 al excederlo; endpoints "misc" (incl. stats) ~100 req/hora en el
  plan general -> poll de stats 1-2 veces al día, el resto por webhooks.

Ver notes/TRACKING.md para el cableado completo (Brevo config + redirect first-party).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

BREVO_API = "https://api.brevo.com/v3"

UTM_SOURCE = "inmersivo"
UTM_MEDIUM = "email"

DATA_DIR = Path(__file__).resolve().parent / "data"
SUBSCRIBERS_FILE = DATA_DIR / "subscribers.json"

REDIRECT_BASE = "https://go.sensalab.io/c"   # endpoint first-party (futuro)

# Máximo de eventos crudos guardados por suscriptor (recencia/frecuencia usan ~90 días).
EVENTS_CAP = 400

# Eventos que se piden al registrar el webhook MARKETING en Brevo (enum real del
# endpoint POST /v3/webhooks — ojo: difiere de los nombres que llegan en el payload).
MARKETING_WEBHOOK_EVENTS = (
    "delivered", "opened", "click", "softBounce", "hardBounce",
    "unsubscribed", "spam", "listAddition",
)

# Nombre de evento en el PAYLOAD del webhook marketing -> evento normalizado nuestro.
_EVENT_MAP = {
    "delivered": "delivered",
    "opened": "open",
    "proxy_open": "open",          # apertura por proxy (Apple MPP etc.) — se marca en meta
    "click": "click",
    "clicked": "click",
    "soft_bounce": "soft_bounce",
    "softbounce": "soft_bounce",
    "hard_bounce": "hard_bounce",
    "hardbounce": "hard_bounce",
    "unsubscribe": "unsubscribed",  # así llega en el payload marketing (singular)
    "unsubscribed": "unsubscribed",
    "spam": "spam",
    "complaint": "spam",
    "list_addition": "list_addition",
    # tipos normalizados nuestros (por si record_event recibe algo ya normalizado)
    "open": "open",
}

NORMALIZED_EVENTS = ("delivered", "open", "click", "soft_bounce", "hard_bounce",
                     "unsubscribed", "spam", "list_addition", "other")


# ---------------------------------------------------------------------------
# Helpers de tiempo
# ---------------------------------------------------------------------------

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_ts(value) -> datetime | None:
    """Acepta epoch (int/float), ISO 8601 o 'YYYY-MM-DD HH:MM:SS' de Brevo."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    s = str(value).strip()
    if re.fullmatch(r"\d{9,13}", s):                       # epoch como string
        ts = float(s) / (1000.0 if len(s) >= 13 else 1.0)
        return _parse_ts(ts)
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# 1. LINKS — UTM + atributos
# ---------------------------------------------------------------------------

def slugify(text: str, max_len: int = 60) -> str:
    """'Visión: Harry Potter en Cosm LA' -> 'vision-harry-potter-en-cosm-la'.

    Sin acentos, minúsculas, sólo [a-z0-9-]. Idempotente. Para utm_content.
    """
    s = unicodedata.normalize("NFKD", str(text or ""))
    s = s.encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
        # no cortar a media palabra si hay un guion razonablemente cerca
        if "-" in s and len(s) - s.rfind("-") < 12:
            s = s[:s.rfind("-")]
    return s


def wrap_link(url: str, issue_number: int, story_slug: str) -> str:
    """Añade los UTM del Cerebro Inmersivo preservando la query existente.

    utm_source=inmersivo & utm_medium=email & utm_campaign=issue-<n>
    & utm_content=<slug>. Si el URL ya trae utm_* (del publisher), los NUESTROS
    ganan (se reemplazan); el resto de la query y el #fragment se preservan.
    """
    url = (url or "").strip()
    if not url:
        return url
    parts = urlsplit(url)
    pairs = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.lower().startswith("utm_")]
    pairs += [
        ("utm_source", UTM_SOURCE),
        ("utm_medium", UTM_MEDIUM),
        ("utm_campaign", f"issue-{int(issue_number)}"),
        ("utm_content", slugify(story_slug) or "story"),
    ]
    return urlunsplit((parts.scheme, parts.netloc, parts.path,
                       urlencode(pairs), parts.fragment))


def link_attrs() -> str:
    """Atributos para cada <a> del email: nueva pestaña (correcto para B2B: el
    correo queda abierto) + noopener/noreferrer."""
    return 'target="_blank" rel="noopener noreferrer"'


# ---------------------------------------------------------------------------
# 2. BREVO STATS — lectura de métricas por campaña
# ---------------------------------------------------------------------------

class BrevoAPIError(RuntimeError):
    """Error de la API de Brevo (status >= 300 tras reintentos)."""

    def __init__(self, status: int, message: str):
        super().__init__(f"Brevo API ({status}): {message}")
        self.status = status


def _brevo_get(api_key: str, path: str, params: dict | None = None,
               retries: int = 2, timeout: int = 30) -> dict:
    """GET con auth 'api-key', manejo de 429 (Retry-After) y errores."""
    if not api_key:
        raise BrevoAPIError(0, "Falta BREVO_API_KEY.")
    headers = {"api-key": api_key, "accept": "application/json"}
    url = f"{BREVO_API}{path}"
    last = None
    for attempt in range(retries + 1):
        r = requests.get(url, headers=headers, params=params or {}, timeout=timeout)
        if r.status_code == 429 and attempt < retries:
            # Rate limit (plan general: ~100 req/h en endpoints misc). Backoff.
            wait = min(float(r.headers.get("Retry-After", 2 ** attempt)), 30.0)
            time.sleep(wait)
            last = r
            continue
        if r.status_code >= 300:
            raise BrevoAPIError(r.status_code, r.text[:500])
        return r.json()
    raise BrevoAPIError(last.status_code if last is not None else 429,
                        "Rate limit persistente (429).")


def normalize_campaign_stats(data: dict) -> dict:
    """Aplana la respuesta de GET /emailCampaigns/{id} a nuestro dict de métricas.

    Función pura (testeable sin red). Campos de Brevo: statistics.globalStats
    {sent, delivered, deferred, softBounces, hardBounces, viewed, uniqueViews,
    clickers, uniqueClicks, complaints, unsubscriptions, ...} y linksStats
    {url: clicks} si se pidió.
    """
    stats = (data.get("statistics") or {})
    g = stats.get("globalStats") or {}

    def n(key):  # métrica entera con default 0
        try:
            return int(g.get(key) or 0)
        except (TypeError, ValueError):
            return 0

    delivered = n("delivered")
    unique_views = n("uniqueViews")
    unique_clicks = n("uniqueClicks")
    out = {
        "campaign_id": data.get("id"),
        "name": data.get("name", ""),
        "subject": data.get("subject", ""),
        "status": data.get("status", ""),
        "sent_date": data.get("sentDate") or data.get("scheduledAt") or "",
        "sent": n("sent"),
        "delivered": delivered,
        "deferred": n("deferred"),
        "soft_bounces": n("softBounces"),
        "hard_bounces": n("hardBounces"),
        "opens": n("viewed"),
        "unique_opens": unique_views,
        "clicks": n("clickers"),
        "unique_clicks": unique_clicks,
        "complaints": n("complaints"),
        "unsubscriptions": n("unsubscriptions"),
        # tasas útiles para el loop (0.0 si no hay base)
        "open_rate": round(unique_views / delivered, 4) if delivered else 0.0,
        "click_rate": round(unique_clicks / delivered, 4) if delivered else 0.0,
        "click_to_open": round(unique_clicks / unique_views, 4) if unique_views else 0.0,
        "bounce_rate": round((n("softBounces") + n("hardBounces")) / n("sent"), 4)
                       if n("sent") else 0.0,
        # clicks por link: {url: clicks} — de aquí salen clicks por historia
        # (el utm_content del URL identifica el slug) si no hay webhooks.
        "links": stats.get("linksStats") or {},
    }
    return out


def fetch_campaign_stats(api_key: str, campaign_id: int) -> dict:
    """Métricas de UNA campaña. GET /v3/emailCampaigns/{id} (+linksStats).

    Devuelve el dict normalizado de normalize_campaign_stats(). Lanza
    BrevoAPIError si la API falla (404 campaña inexistente, 401 key mala, 429...).
    """
    data = _brevo_get(api_key, f"/emailCampaigns/{int(campaign_id)}",
                      params={"excludeHtmlContent": "true"})
    # linksStats llega junto a globalStats en la respuesta de detalle; si el plan
    # no lo incluyó, se pide explícito (segunda llamada, sólo si faltó).
    if not (data.get("statistics") or {}).get("linksStats"):
        try:
            extra = _brevo_get(api_key, f"/emailCampaigns/{int(campaign_id)}",
                               params={"statistics": "linksStats",
                                       "excludeHtmlContent": "true"})
            links = (extra.get("statistics") or {}).get("linksStats")
            if links:
                data.setdefault("statistics", {})["linksStats"] = links
        except BrevoAPIError:
            pass  # linksStats es un extra; las métricas globales ya están
    return normalize_campaign_stats(data)


def list_campaigns(api_key: str, limit: int = 20, offset: int = 0,
                   status: str | None = None) -> list[dict]:
    """Lista campañas (GET /v3/emailCampaigns) ya normalizadas — para mapear
    'issue-<n>' -> campaign_id y hacer polling de las últimas ediciones."""
    params = {"limit": limit, "offset": offset,
              "excludeHtmlContent": "true", "sort": "desc"}
    if status:
        params["status"] = status  # p.ej. "sent"
    data = _brevo_get(api_key, "/emailCampaigns", params=params)
    return [normalize_campaign_stats(c) for c in data.get("campaigns", [])]


# ---------------------------------------------------------------------------
# 3. WEBHOOKS — parser de eventos marketing de Brevo
# ---------------------------------------------------------------------------

def _utm_content_of(url: str) -> str:
    """Extrae el utm_content (slug de historia) de un URL clickeado."""
    try:
        for k, v in parse_qsl(urlsplit(url or "").query, keep_blank_values=True):
            if k.lower() == "utm_content":
                return v
    except ValueError:
        pass
    return ""


def parse_webhook(payload: dict) -> dict:
    """Normaliza un evento del webhook MARKETING de Brevo.

    Payload real de Brevo (verificado): {"event", "email", "id", "camp_id",
    "campaign name", "date_sent", "date_event", "ts_sent", "ts_event", "ts",
    "tag", "URL" (sólo click), "list_id" (unsub/list_addition), "reason" y
    "sending_ip" (bounces)}.

    Devuelve dict normalizado:
      {email, event, raw_event, campaign_id, campaign_name, timestamp (ISO UTC),
       link, story_slug, list_ids, reason, machine_open}
    Eventos desconocidos -> event="other" (el receptor decide ignorarlos);
    lanza ValueError sólo si el payload no trae ni email ni evento.
    """
    if not isinstance(payload, dict):
        raise ValueError("Payload de webhook no es un objeto JSON.")
    raw_event = str(payload.get("event") or "").strip().lower()
    email = str(payload.get("email") or "").strip().lower()
    if not raw_event and not email:
        raise ValueError("Webhook sin 'event' ni 'email' — no es un evento de Brevo.")

    event = _EVENT_MAP.get(raw_event, "other")
    ts = (_parse_ts(payload.get("ts_event")) or _parse_ts(payload.get("ts"))
          or _parse_ts(payload.get("date_event")) or _utcnow())
    link = payload.get("URL") or payload.get("url") or ""
    list_ids = payload.get("list_id") or []
    if isinstance(list_ids, (int, str)):
        list_ids = [list_ids]

    return {
        "email": email,
        "event": event,
        "raw_event": raw_event,
        "campaign_id": payload.get("camp_id"),
        "campaign_name": payload.get("campaign name") or payload.get("campaign_name") or "",
        "timestamp": _iso(ts),
        "link": link,
        "story_slug": _utm_content_of(link),
        "list_ids": list(list_ids),
        "reason": payload.get("reason") or "",
        "machine_open": raw_event == "proxy_open",
    }


# ---------------------------------------------------------------------------
# 4. ENGAGEMENT por suscriptor — store JSON data/subscribers.json
# ---------------------------------------------------------------------------

def _empty_store() -> dict:
    return {"version": 1, "updated": "", "subscribers": {}}


def load_store(path: Path | str = SUBSCRIBERS_FILE) -> dict:
    """Carga (o crea vacío) el store de engagement por suscriptor."""
    p = Path(path)
    if not p.exists():
        return _empty_store()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _empty_store()
    if not isinstance(data, dict) or "subscribers" not in data:
        return _empty_store()
    return data


def save_store(store: dict, path: Path | str = SUBSCRIBERS_FILE) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    store["updated"] = _iso(_utcnow())
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(p)


def _sub(store: dict, email: str) -> dict:
    email = (email or "").strip().lower()
    subs = store.setdefault("subscribers", {})
    if email not in subs:
        subs[email] = {
            "first_seen": _iso(_utcnow()),
            "last_open": None, "last_click": None, "last_delivered": None,
            "opens": 0, "clicks": 0, "deliveries": 0,
            "soft_bounces": 0, "hard_bounces": 0, "complaints": 0,
            "unsubscribed": False,
            "events": [],
        }
    return subs[email]


def record_event(store: dict, email: str, event: str, meta: dict | None = None) -> dict:
    """Registra un evento normalizado (o crudo de Brevo) para un suscriptor.

    meta opcional: {timestamp (ISO), campaign_id, campaign_name, link, story_slug,
    machine_open, reason}. Devuelve el registro del suscriptor (mutado en sitio;
    persistir con save_store()).
    """
    email = (email or "").strip().lower()
    if not email:
        raise ValueError("record_event: falta email.")
    ev = _EVENT_MAP.get(str(event or "").strip().lower(), "other")
    meta = meta or {}
    ts = meta.get("timestamp") or _iso(_utcnow())
    sub = _sub(store, email)

    if ev == "delivered":
        sub["deliveries"] += 1
        sub["last_delivered"] = ts
    elif ev == "open":
        sub["opens"] += 1
        sub["last_open"] = ts
    elif ev == "click":
        sub["clicks"] += 1
        sub["last_click"] = ts
    elif ev == "soft_bounce":
        sub["soft_bounces"] += 1
    elif ev == "hard_bounce":
        sub["hard_bounces"] += 1
    elif ev == "spam":
        sub["complaints"] += 1
    elif ev == "unsubscribed":
        sub["unsubscribed"] = True
    elif ev == "list_addition":
        pass  # first_seen ya cubre el alta

    entry = {"event": ev, "ts": ts}
    for k_src, k_dst in (("campaign_id", "campaign_id"), ("story_slug", "slug"),
                         ("link", "link"), ("machine_open", "machine_open")):
        if meta.get(k_src):
            entry[k_dst] = meta[k_src]
    sub["events"].append(entry)
    if len(sub["events"]) > EVENTS_CAP:
        sub["events"] = sub["events"][-EVENTS_CAP:]
    return sub


def record_webhook(store: dict, payload: dict) -> dict:
    """Atajo receptor: parse_webhook() + record_event() en un paso."""
    ev = parse_webhook(payload)
    return record_event(store, ev["email"], ev["event"], ev)


def engagement_score(store: dict, email: str, now: datetime | None = None) -> float:
    """Score 0-100: 60% recencia + 40% frecuencia de opens/clicks (90 días).

    - recencia: exp(-días_desde_última_actividad / 45) — media vida ~31 días.
    - frecuencia: (opens_90d + 3*clicks_90d) / 12, cap 1.0 (click pesa x3).
    - unsubscribed o hard bounce -> 0.0 (no re-engage: compliance).
    """
    email = (email or "").strip().lower()
    sub = (store.get("subscribers") or {}).get(email)
    if not sub:
        return 0.0
    if sub.get("unsubscribed") or sub.get("hard_bounces", 0) > 0:
        return 0.0
    now = now or _utcnow()

    last_ts = [t for t in (_parse_ts(sub.get("last_open")),
                           _parse_ts(sub.get("last_click"))) if t]
    if last_ts:
        days = max(0.0, (now - max(last_ts)).total_seconds() / 86400.0)
        recency = math.exp(-days / 45.0)
    else:
        recency = 0.0

    horizon = 90.0 * 86400.0
    opens90 = clicks90 = 0
    for e in sub.get("events", []):
        t = _parse_ts(e.get("ts"))
        if not t or (now - t).total_seconds() > horizon:
            continue
        if e.get("event") == "open":
            opens90 += 1
        elif e.get("event") == "click":
            clicks90 += 1
    freq = min(1.0, (opens90 + 3.0 * clicks90) / 12.0)

    return round(100.0 * (0.6 * recency + 0.4 * freq), 1)


def segment(store: dict, now: datetime | None = None,
            engaged_threshold: float = 40.0, new_days: int = 21) -> dict:
    """Segmenta suscriptores para el envío/re-engage.

      engaged : score >= engaged_threshold — la audiencia núcleo.
      new     : alta reciente (< new_days) y aún sin score — no juzgarlos todavía.
      dormant : el resto — candidatos a re-engage.
      lost    : unsubscribed o hard bounce — NO contactar (compliance).
    """
    now = now or _utcnow()
    out = {"engaged": [], "dormant": [], "new": [], "lost": []}
    for email, sub in (store.get("subscribers") or {}).items():
        if sub.get("unsubscribed") or sub.get("hard_bounces", 0) > 0:
            out["lost"].append(email)
            continue
        score = engagement_score(store, email, now=now)
        if score >= engaged_threshold:
            out["engaged"].append(email)
            continue
        first = _parse_ts(sub.get("first_seen"))
        if first and (now - first).total_seconds() < new_days * 86400.0:
            out["new"].append(email)
        else:
            out["dormant"].append(email)
    for k in out:
        out[k].sort()
    return out


# ---------------------------------------------------------------------------
# 5. FIRST-PARTY — tokens HMAC para go.sensalab.io/c/<token>
# ---------------------------------------------------------------------------
# Diseño completo en notes/TRACKING.md. Resumen: el email linkea a
# https://go.sensalab.io/c/<token>; el server (futuro) verifica el HMAC, loguea
# {email_hash?, slug, issue, ts} y responde 302 al destino. La data de clicks
# queda NUESTRA, independiente del ESP. Aquí vive la parte criptográfica.

_SIG_BYTES = 16  # HMAC-SHA256 truncado a 128 bits — suficiente para anti-forja de URL


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64u_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _sign(secret: str | bytes, body: bytes) -> str:
    key = secret.encode("utf-8") if isinstance(secret, str) else secret
    return _b64u(hmac.new(key, body, hashlib.sha256).digest()[:_SIG_BYTES])


def make_click_token(secret: str | bytes, url: str, issue_number: int | None = None,
                     story_slug: str | None = None, issued_at: int | None = None) -> str:
    """Genera el token firmado para el redirect first-party.

    Formato: <payload_b64url>.<hmac_b64url>  donde payload = JSON compacto
    {"u": url_destino, "i": issue, "s": slug, "t": epoch_emisión}.
    El secret vive en env (TRACKING_SECRET), nunca en el repo.
    """
    if not secret:
        raise ValueError("make_click_token: falta el secret (env TRACKING_SECRET).")
    if not (url or "").strip():
        raise ValueError("make_click_token: falta el URL destino.")
    payload = {"u": url.strip(), "t": int(issued_at if issued_at is not None else time.time())}
    if issue_number is not None:
        payload["i"] = int(issue_number)
    if story_slug:
        payload["s"] = slugify(story_slug)
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    b64 = _b64u(body)
    return f"{b64}.{_sign(secret, b64.encode('ascii'))}"


def verify_click_token(secret: str | bytes, token: str,
                       max_age_days: float | None = None,
                       now: datetime | None = None) -> dict:
    """Verifica firma (y edad opcional) del token. Devuelve
    {"url", "issue", "slug", "issued_at"} o lanza ValueError si es inválido.
    """
    if not secret:
        raise ValueError("verify_click_token: falta el secret.")
    parts = (token or "").split(".")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("Token con formato inválido.")
    b64, sig = parts
    expected = _sign(secret, b64.encode("ascii"))
    if not hmac.compare_digest(sig, expected):
        raise ValueError("Firma HMAC inválida (token alterado o secret incorrecto).")
    try:
        payload = json.loads(_b64u_decode(b64))
    except (ValueError, json.JSONDecodeError):
        raise ValueError("Payload del token ilegible.")
    issued = int(payload.get("t") or 0)
    if max_age_days is not None:
        now_ts = (now or _utcnow()).timestamp()
        if now_ts - issued > max_age_days * 86400.0:
            raise ValueError("Token expirado.")
    return {
        "url": payload.get("u", ""),
        "issue": payload.get("i"),
        "slug": payload.get("s", ""),
        "issued_at": issued,
    }


def redirect_url(token: str, base: str = REDIRECT_BASE) -> str:
    """URL final para el email: https://go.sensalab.io/c/<token>."""
    return f"{base.rstrip('/')}/{token}"


# ---------------------------------------------------------------------------
# 6. LOOP — clicks por topic/formato para realimentar scoring.adjust_weights
# ---------------------------------------------------------------------------

def performance_by_topic(store: dict, editions: list[dict]) -> dict:
    """Agrega clicks del store por topic y por formato de edición.

    editions: lo que produce el composer/content_model — lista de dicts:
      {"issue": 12, "format": "digest",
       "stories": [{"slug": "cosm-la-harry-potter", "topic": "venues-domos"}, ...]}
    (acepta "headline" en vez de "slug"; se sluggifica igual que wrap_link).

    Devuelve el dict que scoring.adjust_weights consumirá (NO lo llama):
      {"total_clicks": N,
       "topics":  {topic:  {"clicks", "stories", "clicks_per_story", "share"}},
       "formats": {formato: {"clicks", "stories", "clicks_per_story", "share"}},
       "stories": {slug: clicks}}
    Clicks cuyo slug no aparece en ninguna edición van al topic "(desconocido)".
    """
    slug_topic: dict[str, str] = {}
    slug_format: dict[str, str] = {}
    topics: dict[str, dict] = {}
    formats: dict[str, dict] = {}

    def bucket(d: dict, key: str) -> dict:
        return d.setdefault(key, {"clicks": 0, "stories": 0,
                                  "clicks_per_story": 0.0, "share": 0.0})

    for ed in editions or []:
        fmt = str(ed.get("format") or "digest")
        for st in ed.get("stories", []):
            slug = slugify(st.get("slug") or st.get("headline") or "")
            if not slug:
                continue
            topic = str(st.get("topic") or "(sin-topic)")
            slug_topic[slug] = topic
            slug_format[slug] = fmt
            bucket(topics, topic)["stories"] += 1
            bucket(formats, fmt)["stories"] += 1

    story_clicks: dict[str, int] = {}
    total = 0
    for sub in (store.get("subscribers") or {}).values():
        for e in sub.get("events", []):
            if e.get("event") != "click":
                continue
            slug = slugify(e.get("slug") or _utm_content_of(e.get("link", "")))
            if not slug:
                continue
            total += 1
            story_clicks[slug] = story_clicks.get(slug, 0) + 1
            topic = slug_topic.get(slug, "(desconocido)")
            bucket(topics, topic)["clicks"] += 1
            if slug in slug_format:
                bucket(formats, slug_format[slug])["clicks"] += 1

    for d in (topics, formats):
        for b in d.values():
            if b["stories"]:
                b["clicks_per_story"] = round(b["clicks"] / b["stories"], 3)
            if total:
                b["share"] = round(b["clicks"] / total, 3)

    return {"total_clicks": total, "topics": topics,
            "formats": formats, "stories": story_clicks}
