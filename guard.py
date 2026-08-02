# -*- coding: utf-8 -*-
"""
GATE non-compete (I1). Lee strategy/08-compliance/forbidden-terms.txt, normaliza el texto
(lower + sin diacriticos + colapso de separadores) y escanea el esquema NUEVO de edicion
(hero/sections/teardown/video/invitation). Un hit = bloqueo (fail-closed).

Reemplaza al viejo writer.scan_forbidden (que leia el esquema 'stories' obsoleto y no se
llamaba desde build_edition).
"""
from __future__ import annotations
import os
import re
import unicodedata

_HERE = os.path.dirname(os.path.abspath(__file__))
_TERMS_FILE = os.path.join(_HERE, "strategy", "08-compliance", "forbidden-terms.txt")
# Fallback minimo si el archivo no esta (nunca dejar el gate vacio)
_FALLBACK_A = ["cinetica", "cinetika", "cynetica", "kinetica", "sinetica"]


class GuardBlocked(Exception):
    def __init__(self, hits):
        self.hits = hits
        super().__init__(f"Gate non-compete BLOQUEO: {hits}")


def _deaccent(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", _deaccent((s or "").lower())).strip()


def _squash(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _norm(s))


def _load_terms():
    literal, regex = [], []
    section = None
    try:
        lines = open(_TERMS_FILE, encoding="utf-8").read().splitlines()
    except OSError:
        return [(_norm(t), _squash(t), "A") for t in _FALLBACK_A], []
    for raw in lines:
        line = raw.split("#", 1)[0].strip()  # quita comentarios inline
        if not line:
            m = re.match(r"^\s*\[([A-E])\]", raw)
            if m:
                section = m.group(1)
            continue
        m = re.match(r"^\[([A-E])\]", line)
        if m:
            section = m.group(1)
            line = line[line.index("]") + 1:].strip()
            if not line:
                continue
        if section == "E":
            continue  # allowlist del detector difuso (no implementamos fuzzy en v1)
        if section == "D" or line.startswith("re:"):
            regex.append(line[3:] if line.startswith("re:") else line)
        elif section in ("A", "B", "C"):
            literal.append((_norm(line), _squash(line), section))
    return literal, regex


_LITERAL, _REGEX = _load_terms()


def scan_text(text: str):
    n = _norm(text)
    sq = _squash(text)
    hits = []
    for tn, ts, sec in _LITERAL:
        if sec == "A":
            if ts and ts in sq:
                hits.append((sec, tn))
        else:
            if tn and tn in n:
                hits.append((sec, tn))
    for pat in _REGEX:
        try:
            if re.search(pat, n):
                hits.append(("D", pat))
        except re.error:
            pass
    return hits


def _edition_text(ed: dict) -> str:
    parts = [ed.get("edition_title", "")]
    h = ed.get("hero", {})
    parts += [h.get("kicker", ""), h.get("headline", ""), h.get("statement", ""), h.get("sub", "")]
    for s in ed.get("sections", []):
        parts += [s.get("kicker", ""), s.get("headline", ""), s.get("statement", ""),
                  s.get("body", ""), s.get("cta", ""), s.get("why", "")]
    td = ed.get("teardown", {})
    if td:
        parts += [td.get("case", ""), td.get("statement", ""), td.get("verdict", ""),
                  td.get("flaw", ""), td.get("principle", ""), td.get("why", ""),
                  td.get("video_statement", ""), td.get("done_right", {}).get("text", "")]
    v = ed.get("video", {})
    parts += [v.get("kicker", ""), v.get("headline", ""), v.get("statement", ""), v.get("body", "")]
    inv = ed.get("invitation", {})
    parts += [inv.get("kicker", ""), inv.get("headline", ""), inv.get("body", ""), inv.get("button", "")]
    return " \n ".join(p for p in parts if p)


def scan_edition(edition: dict):
    """Devuelve lista de hits (vacia = limpio)."""
    return scan_text(_edition_text(edition))


def assert_clean(edition: dict):
    """Fail-closed: lanza GuardBlocked si hay cualquier hit."""
    hits = scan_edition(edition)
    if hits:
        raise GuardBlocked(hits)
    return True


if __name__ == "__main__":
    import json, sys
    ed = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else {}
    print(f"terminos cargados: {len(_LITERAL)} literales + {len(_REGEX)} regex")
    print("hits:", scan_edition(ed))
