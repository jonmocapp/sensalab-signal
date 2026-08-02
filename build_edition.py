# -*- coding: utf-8 -*-
"""
build_edition — el cerebro 'AI sin AI' que decide FORMATO (The Signal por default;
Teardown cuando hay caso polarizante) y RENDERIZA web + email. Determinista, sin LLM.
Antes de renderizar corre el GATE non-compete (guard) fail-closed.
"""
from __future__ import annotations
import re

import guard
from render_signal import build_signal, DEFAULT_FONT
from render_teardown import build_teardown
from signal_email import build_signal_email

# Señales de talkability (palabras/frases COMPLETAS; se matchean con \b y se cuentan
# DISTINTAS, no repeticiones — así "called it fake" no dispara doble por "fake").
_TALK = ["backlash", "criticized", "criticism", "slop", "ai slop", "roasted", "mocked",
         "flop", "too smooth", "comments off", "switched off", "turn off comments",
         "called it fake", "torched", "disappointing", "disappointed", "controversy",
         "controversial", "dragged", "cringe", "went viral", "blocked the logo",
         "covered the logo"]
_TALK_RX = [re.compile(r"\b" + re.escape(k) + r"\b", re.IGNORECASE) for k in _TALK]


def talkability(edition) -> int:
    parts = []
    for s in edition.get("sections", []):
        parts += [s.get("headline", ""), s.get("statement", ""), s.get("body", "")]
    td = edition.get("teardown", {})
    parts += [td.get("verdict", ""), td.get("flaw", ""), td.get("statement", "")]
    blob = " ".join(parts)
    return sum(1 for rx in _TALK_RX if rx.search(blob))  # DISTINTAS, no .count


class EditionInvalid(ValueError):
    pass


def validate(edition: dict, fmt: str) -> None:
    """Falla claro (EditionInvalid) si la edicion no trae lo minimo para renderizar."""
    errs = []
    if not isinstance(edition, dict):
        raise EditionInvalid("la edicion debe ser un dict")
    if not str(edition.get("issue_no", "")).strip():
        errs.append("falta issue_no")
    hero = edition.get("hero") or {}
    if not (hero.get("statement") or hero.get("headline")):
        errs.append("hero sin statement/headline")
    if fmt == "teardown":
        td = edition.get("teardown") or {}
        for key in ("case", "statement", "verdict", "flaw", "principle", "why"):
            if not str(td.get(key, "")).strip():
                errs.append(f"teardown.{key} vacio")
    else:
        secs = edition.get("sections") or []
        if not secs:
            errs.append("signal sin sections")
        for i, s in enumerate(secs):
            if not s.get("role"):
                errs.append(f"section[{i}] sin role (rompe anchors/imagenes)")
            if not (s.get("statement") or s.get("headline")):
                errs.append(f"section[{i}] sin statement/headline")
    inv = edition.get("invitation") or {}
    if not inv.get("headline"):
        errs.append("invitation sin headline")
    if errs:
        raise EditionInvalid("Edicion invalida: " + "; ".join(errs))


def choose_format(edition) -> tuple[str, str]:
    """Devuelve (formato, razon). formato in {'signal','teardown'}."""
    override = (edition.get("format") or "").lower()
    if override in ("signal", "teardown"):
        return override, f"formato forzado por edicion (format={override})"
    t = talkability(edition)
    if edition.get("teardown") and t >= 2:
        return "teardown", f"caso polarizante (talkability={t}) + bloque teardown listo"
    return "signal", f"sin caso dominante (talkability={t}); digest de insights (The Signal)"


def compose(edition, media, *, issue_no, date, web_url="#",
            font_stack=DEFAULT_FONT, img_base="", logo="media/sensalab-logo.png",
            legal_name="SensaLab", legal_address="Los Angeles, CA, USA",
            unsub="{{ unsubscribe }}") -> dict:
    # GATE non-compete fail-closed: si aparece algo prohibido, no se renderiza nada.
    guard.assert_clean(edition)

    fmt, reason = choose_format(edition)
    validate(edition, fmt)  # falla claro antes de renderizar HTML roto
    if fmt == "teardown":
        web = build_teardown(edition, media, issue_no=issue_no, date=date, web_url=web_url,
                             font_stack=font_stack, img_base=img_base, logo=logo)
    else:
        web = build_signal(edition, media, issue_no=issue_no, date=date, web_url=web_url,
                           font_stack=font_stack, img_base=img_base, logo=logo)
    email = build_signal_email(edition, media, web_url=web_url, issue_no=issue_no, date=date,
                               unsub=unsub, legal_name=legal_name, legal_address=legal_address,
                               img_base=img_base, logo=logo,
                               format_label=("Teardown" if fmt == "teardown" else "The Signal"))
    return {"format": fmt, "reason": reason, "web": web, "email": email}
