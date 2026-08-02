# -*- coding: utf-8 -*-
"""Carga signals.json (el feed diario que produce daily_signals.py) y lo deja listo para el
build del blog: asigna una portada abstracta de marca por categoría (sin IP) y ordena por
calidad. Expone SIGNALS. Importado por build_blog_b.py.

Las tarjetas de Señales linkean SIEMPRE a la fuente original (atribución); no generan página
interna. Son el Carril 1: noticias reales, frescas, actualizadas a diario."""
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parent
SIGNALS_JSON = BASE / "signals.json"

# Categoría -> portada abstracta ya existente en blog/img (reuso, sin generar 24 nuevas).
CAT_COVER = {
    "Experiential":    "img/cover-airline-turned-beach-into-brand.jpg",
    "Spatial & AR":    "img/cover-consumer-ar-glasses-reservations.jpg",
    "CGI & VFX":       "img/cover-led-volumes-brand-stages.jpg",
    "AI":              "img/cover-nvidia-real-time-rendering.jpg",
    "Gaming":          "img/cover-unreal-engine-gamescom-floor.jpg",
    "Interactive":     "img/cover-teamlab-interactive-art.jpg",
    "Concert visuals": "img/cover-sphere-live-venue.jpg",
}
_DEFAULT_COVER = "img/cover-stadium-year-round-attraction.jpg"

# Cuántas señales se muestran en la home (2 filas de 3). El feed guarda más para rotación.
DISPLAY_COUNT = 6


_TIER_RANK = {"core": 0, "rotate": 1, "query": 2}


def load(limit: int = DISPLAY_COUNT) -> list[dict]:
    try:
        data = json.load(open(SIGNALS_JSON, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []
    sig = data.get("signals", []) if isinstance(data, dict) else list(data)
    # Gate de calidad para la home: solo señales con titular, link Y un 'take' real (frase de la
    # fuente, no un duplicado del titular). Orden: fuentes curadas (core/rotate) antes que query,
    # luego score. La frescura la garantiza que el feed se regenere a diario.
    # Gate de calidad para la home: titular + link + 'take' real, y FUENTE en ASCII (los medios
    # trade en inglés lo son; descarta medios extranjeros con nombre en otro alfabeto). El orden
    # prioriza fuentes curadas (core/rotate) antes que las de Google News (query).
    def _ascii(s):
        return all(ord(c) < 128 for c in (s or ""))
    sig = [s for s in sig
           if s.get("headline") and s.get("link") and (s.get("take") or "").strip()
           and _ascii(s.get("source", ""))]
    sig.sort(key=lambda s: (_TIER_RANK.get(s.get("tier", "query"), 2), -s.get("score", 0)))
    out, seen_series = [], set()
    for s in sig:
        # Dedup por serie: no apilar varias del mismo formato recurrente ("Fresh Faces: X/Y/Z").
        series = s["headline"].split(":")[0].strip().lower()
        if series in seen_series:
            continue
        seen_series.add(series)
        out.append({
            "headline": s["headline"],
            "link": s["link"],
            "take": s.get("take", ""),
            "cat": s.get("cat", "Experiential"),
            "token": s.get("token", "experiential"),
            "source": s.get("source", ""),
            "img": CAT_COVER.get(s.get("cat", ""), _DEFAULT_COVER),
        })
        if len(out) >= limit:
            break
    return out


SIGNALS = load()
