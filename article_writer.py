# -*- coding: utf-8 -*-
"""Redactor AUTOMÁTICO de notas del blog (Claude API). Toma un ítem del pool + el texto real de
la fuente y devuelve una entrada ART (mismo esquema que signal_articles.py) para 'Latest stories'.

Es la versión de máquina de lo que hicieron los redactores en sesión: misma voz, mismos
guardarraíles duros, pero llamando a la API para poder correr solo en la nube. Ancla en el texto
de la fuente (no inventa) y rechaza cualquier salida que toque el non-compete."""
from __future__ import annotations

from writer import FORBIDDEN   # única fuente de verdad del guardarraíl non-compete

SYSTEM_PROMPT = """\
You are the editor of The Signal, SensaLab's English-language blog. SensaLab is a Los Angeles
white-label real-time 3D and immersive studio: the layer agencies and brands use to design and
build interactive activations, projection mapping, AR/XR, LED-volume and immersive installations
UNDER THEIR OWN NAME. Reader = a senior agency producer / brand-experience lead: sharp, busy,
allergic to hype. Write peer-to-peer.

You receive a story headline and the SOURCE ARTICLE TEXT. Write one blog article via the emit_article
tool. Structure the body as 7-9 blocks (para/subhead), ~500-650 words, 2-3 subheads:
1) First para = the concrete facts (what/who/where + hard numbers/dates), using ONLY the source text;
   attribute figures ("according to the venue", "the report found").
2) A reframe para: "the real signal is [scale / a new default / a shifted cost], not [the surface thing]".
3) 2-3 subheads; include a "what a producer can actually do now" angle and a "why this belongs in an
   experiential toolkit" angle.
4) Final para = a soft, non-boastful SensaLab white-label close (1-2 sentences), spirit: "That is the
   layer we build. SensaLab is the white-label real-time 3D and immersive layer agencies and brands
   use to design and run experiences under their own name. [one line tying to this story]."

HARD GUARDRAILS (violating any invalidates the article):
- Ground every fact ONLY in the source text provided. Do NOT invent numbers, dates, names, quotes or
  outcomes. If a detail is not in the source text, do not write it.
- NEVER reference a founder's past work, past clients, or "Cinetica". Never claim SensaLab did specific
  past projects ("as we've done", "our clients"). SensaLab speaks as an expert, not a portfolio.
- No exclamation marks, no emojis, no empty hype ("revolutionary", "game-changer"). No superlatives
  without a cited number.
- English, sentence case, never ALL CAPS. Keep proper nouns and settled tech terms in English.

Call emit_article with everything. Do not write text outside the tool."""

TOOL = {
    "name": "emit_article",
    "description": "Return one complete blog article in the ART schema.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "headline": {"type": "string", "description": "editorial hook ~10-14 words, sentence case"},
            "dek": {"type": "string", "description": "1-2 sentences, the thesis"},
            "focus_keyword": {"type": "string"},
            "read_minutes": {"type": "integer"},
            "meta_description": {"type": "string", "description": "<=155 chars"},
            "why": {"type": "string", "description": "one sentence, why it matters"},
            "takeaway": {"type": "string", "description": "1-2 sentences, actionable"},
            "body": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "type": {"type": "string", "enum": ["para", "subhead"]},
                        "text": {"type": "string"},
                    },
                    "required": ["type", "text"],
                },
            },
        },
        "required": ["headline", "dek", "focus_keyword", "read_minutes",
                     "meta_description", "why", "takeaway", "body"],
    },
}


def _scan_forbidden(art: dict) -> list[str]:
    import unicodedata
    blob = " ".join([
        art.get("headline", ""), art.get("dek", ""), art.get("why", ""),
        art.get("takeaway", ""), art.get("meta_description", ""),
        *[b.get("text", "") for b in art.get("body", [])],
    ]).lower()
    blob = unicodedata.normalize("NFC", blob)
    return [t for t in FORBIDDEN if unicodedata.normalize("NFC", t) in blob]


def write_article(headline: str, source_name: str, source_url: str, source_text: str,
                  *, model: str, api_key: str | None = None) -> dict | None:
    """Devuelve una entrada ART (dict) o None si el modelo rechazó, no ancló, o tocó el guardarraíl."""
    from anthropic import Anthropic

    if not (source_text or "").strip():
        return None
    user = (
        f"HEADLINE: {headline}\nSOURCE: {source_name}\nLINK: {source_url}\n\n"
        f"SOURCE ARTICLE TEXT (the only facts you may use):\n\"\"\"\n{source_text[:6000]}\n\"\"\"\n\n"
        "Write the article now. Ground every fact in the source text above."
    )
    client = Anthropic(api_key=api_key) if api_key else Anthropic()
    try:
        resp = client.messages.create(
            model=model, max_tokens=4000, system=SYSTEM_PROMPT, tools=[TOOL],
            tool_choice={"type": "tool", "name": "emit_article"},
            messages=[{"role": "user", "content": user}],
        )
    except Exception as e:
        print(f"  [writer] API error: {e}")
        return None
    if getattr(resp, "stop_reason", None) in ("refusal", "max_tokens"):
        print(f"  [writer] descartada (stop_reason={resp.stop_reason})")
        return None

    art = None
    for block in resp.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "emit_article":
            art = block.input
            break
    if not art:
        return None

    hits = _scan_forbidden(art)
    if hits:
        print(f"  [writer] RECHAZADA por guardarraíl non-compete: {hits}")
        return None
    if not art.get("body") or len(art["body"]) < 4:
        return None
    art.setdefault("read_minutes", 3)
    return art
