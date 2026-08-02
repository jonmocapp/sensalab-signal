"""
Configuracion central del bot de newsletter SensaLab.
Todo se controla con variables de entorno (.env en local, Secrets en GitHub/Railway).

IMPORTANTE (bug de secrets vacios): en GitHub Actions un secret no definido se
expande a "" y la env var SI queda seteada (vacia). Por eso usamos `getenv(x) or default`
en vez de `getenv(x, default)` -> asi un valor vacio tambien cae al default.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def env(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return v if (v is not None and v.strip() != "") else default


BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "state.json"
OUTPUT_DIR = BASE_DIR / "ediciones"

# --- Claude / Anthropic ---
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY")
# Modelo que ESCRIBE la edicion. Opus 4.8 ~ $0.05-0.08 USD por edicion (~$3-4 USD/ano).
# NO es gratis: Anthropic requiere creditos prepagados. Alternativas mas baratas:
# "claude-sonnet-5". Maxima calidad: "claude-fable-5".
ANTHROPIC_MODEL = env("ANTHROPIC_MODEL", "claude-opus-4-8")

# --- Entrega ---
# file  -> solo guarda el HTML en ediciones/ (default, 100% gratis, no envia)
# draft -> crea BORRADOR en el ESP (tu revisas y envias)
# send  -> crea y ENVIA solo
SEND_MODE = env("SEND_MODE", "file").lower()

# Proveedor de envio. IMPORTANTE:
#   brevo      -> plan GRATIS permite enviar campanas HTML por API (300/dia). RECOMENDADO.
#   mailerlite -> el plan GRATIS NO permite HTML propio por API (requiere plan Advanced de pago).
PROVIDER = env("PROVIDER", "brevo").lower()

# Brevo (api.brevo.com)
BREVO_API_KEY = env("BREVO_API_KEY")
BREVO_LIST_ID = env("BREVO_LIST_ID")

# MailerLite (connect.mailerlite.com) -- solo util con plan Advanced
MAILERLITE_API_KEY = env("MAILERLITE_API_KEY")
MAILERLITE_GROUP_ID = env("MAILERLITE_GROUP_ID")

FROM_NAME = env("FROM_NAME", "SensaLab")
FROM_EMAIL = env("FROM_EMAIL", "hello@sensalab.io")

# --- Datos legales del pie (CAN-SPAM / footer del ESP) ---
COMPANY_LEGAL_NAME = env("COMPANY_LEGAL_NAME", "SensaLab")
# Regla de marca: la ubicacion es SIEMPRE Los Angeles (nunca Mexico) y sin guiones.
COMPANY_ADDRESS = env("COMPANY_ADDRESS", "Los Angeles, CA, USA")

# --- Parametros editoriales ---
MAX_STORIES = int(env("MAX_STORIES", "5"))
MIN_STORIES = int(env("MIN_STORIES", "3"))
LOOKBACK_DAYS = int(env("LOOKBACK_DAYS", "10"))
MIN_GEO_STORIES = int(env("MIN_GEO_STORIES", "2"))

# --- Marca (para el template) ---
BRAND = {
    "name": "SensaLab",
    "tagline": "Rendering Imagination",
    "signature": "The real luxury is presence",
    "site": "https://sensalab.io",
    "navy": "#1C1956",
    "paper": "#FEFDFB",
    "ink": "#2A2740",
    "muted": "#6E6A85",
    "grad": ["#32BFFC", "#3D76E8", "#6060BE", "#B55CB7"],
}

# Placeholder de baja del ESP (cada proveedor usa el suyo).
UNSUB_TOKEN = {
    "brevo": "{{ unsubscribe }}",
    "mailerlite": "{$unsubscribe}",
}.get(PROVIDER, "{{ unsubscribe }}")


def validate(require_api: bool = True) -> list:
    """Devuelve lista de problemas de configuracion (vacia = todo bien)."""
    problems = []
    if require_api and not ANTHROPIC_API_KEY:
        problems.append("Falta ANTHROPIC_API_KEY (la key de Claude).")
    if SEND_MODE not in ("file", "draft", "send"):
        problems.append(f"SEND_MODE invalido: '{SEND_MODE}'. Usa file | draft | send.")
    if SEND_MODE in ("draft", "send"):
        if PROVIDER not in ("brevo", "mailerlite"):
            problems.append(f"PROVIDER invalido: '{PROVIDER}'. Usa brevo | mailerlite.")
        if PROVIDER == "brevo":
            if not BREVO_API_KEY:
                problems.append("PROVIDER=brevo requiere BREVO_API_KEY.")
            if not BREVO_LIST_ID:
                problems.append("PROVIDER=brevo requiere BREVO_LIST_ID.")
        elif PROVIDER == "mailerlite":
            if not MAILERLITE_API_KEY:
                problems.append("PROVIDER=mailerlite requiere MAILERLITE_API_KEY.")
            if not MAILERLITE_GROUP_ID:
                problems.append("PROVIDER=mailerlite requiere MAILERLITE_GROUP_ID.")
        if PROVIDER == "brevo" and BREVO_LIST_ID and not BREVO_LIST_ID.isdigit():
            problems.append(f"BREVO_LIST_ID debe ser numerico, no '{BREVO_LIST_ID}'.")
    return problems


def advisories() -> list:
    """Avisos informativos (NO bloquean el envio)."""
    notes = []
    if PROVIDER == "mailerlite":
        notes.append("MailerLite plan gratis NO envia HTML propio por API (requiere Advanced). "
                     "Considera PROVIDER=brevo.")
    return notes
