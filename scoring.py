"""
scoring.py — juicio editorial multi-factor del CEREBRO INMERSIVO (§4) + loop de
aprendizaje (§5).

Combina los sub-scores de Candidate.scores (SCORE_KEYS) en un "total" ponderado,
rellena con helpers deterministas los sub-scores que ningun otro modulo llena
(timeliness/authority/novelty) y expone el loop de aprendizaje: pesos en JSON
(data/weights.json) que el engagement ajusta con un bandit sencillo.

Convencion: todos los sub-scores viven en 0..1; el total tambien (los pesos se
normalizan al combinar). Sin LLM, sin APIs: heuristica pura y reproducible.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from models import Candidate, SCORE_KEYS

# ---------------------------------------------------------------------------
# Pesos default (§4). Suman 1.0. Racional de cada uno:
#
#   relevance   0.20  La puerta base: ¿es experiencial/inmersivo de verdad?
#                     Sin relevancia nada mas importa (keywords STRONG/INCLUDE).
#   b2b         0.18  La regla de oro del SL-26: el test del productor. Casi tan
#                     pesado como relevance porque el newsletter existe para el ICP.
#   timeliness  0.12  Cadencia semanal: lo fresco (y lo que toca tentpole) manda.
#   momentum    0.12  El diferenciador "editor de maquina": reaccionar a picos y
#                     momentos (mismo peso que timeliness — juntos son el "ahora").
#   novelty     0.10  Anti-repeticion por topic: castiga recalentar temas ya usados.
#   authority   0.08  Peso de la fuente + gran marca/venue: credibilidad, no criterio
#                     principal (una nota chica con gran angulo puede ganar).
#   talkability 0.08  Motor del formato Teardown: controversia/craft-fail vende
#                     conversacion, pero no debe dominar un digest normal.
#   angle       0.07  Que tan bien encaja en un angulo fuerte (bar-moved, steal-this).
#   geo         0.05  Boost LA/Miami/NY/Vegas: nice-to-have, ya hay MIN_GEO en curation.
# ---------------------------------------------------------------------------
WEIGHTS: dict[str, float] = {
    "relevance":   0.20,
    "b2b":         0.18,
    "timeliness":  0.12,
    "momentum":    0.12,
    "novelty":     0.10,
    "authority":   0.08,
    "talkability": 0.08,
    "angle":       0.07,
    "geo":         0.05,
}

# Sanity: WEIGHTS cubre exactamente los sub-scores (SCORE_KEYS sin "total").
assert set(WEIGHTS) == set(SCORE_KEYS) - {"total"}, "WEIGHTS desincronizado de SCORE_KEYS"

# Donde vive el loop de aprendizaje (§5): el engagement ajusta y persiste aqui.
DEFAULT_WEIGHTS_PATH = Path(__file__).resolve().parent / "data" / "weights.json"

# --- Parametros de los helpers deterministas ---
TIMELINESS_WINDOW_DAYS = 10.0   # = LOOKBACK_DAYS default: 0 dias -> 1.0, >=10 dias -> 0.0
TIMELINESS_UNKNOWN = 0.4        # sin fecha: ni fresco ni muerto (por debajo de la media)
TIMELINESS_MOMENT_BONUS = 0.2   # §4: "recencia + si toca un tentpole activo"

TIER_AUTHORITY = {"core": 0.8, "rotate": 0.55, "query": 0.35}  # confianza editorial por tier
AUTHORITY_ENTITY_BONUS = 0.2    # menciona gran marca O venue (Sphere, Cosm...) en entities

NOVELTY_FRESH = 1.0             # topic nunca usado
NOVELTY_UNKNOWN = 0.7           # sin topic: beneficio de la duda, pero menos que fresco
NOVELTY_REPEATED = 0.2          # topic ya cubierto recientemente (castigo fuerte, no veto)

# --- Bandit sencillo (§5) ---
LEARNING_RATE = 0.10            # paso pequeno: el loop corre cada semana, sin bandazos
MIN_WEIGHT = 0.02               # ninguna senal muere del todo (sigue explorando)
MAX_WEIGHT = 0.40               # ninguna senal secuestra el total


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


# ---------------------------------------------------------------------------
# Combinar y rankear
# ---------------------------------------------------------------------------

def combine(cand: Candidate, weights: dict[str, float] | None = None) -> None:
    """
    Escribe cand.scores["total"] = suma ponderada de los sub-scores presentes.
    Sub-score ausente cuenta como 0 (castigo natural a lo no-enriquecido).
    Se normaliza entre la suma de pesos, asi el total queda en la escala de los
    sub-scores (0..1) aunque los pesos custom no sumen 1.
    """
    w = weights if weights is not None else WEIGHTS
    keys = [k for k in w if k != "total"]
    denom = sum(float(w[k]) for k in keys)
    if denom <= 0:
        cand.scores["total"] = 0.0
        return
    num = sum(float(w[k]) * float(cand.scores.get(k, 0.0)) for k in keys)
    cand.scores["total"] = round(num / denom, 4)


def rank(cands: list[Candidate]) -> list[Candidate]:
    """Ordena por total desc (estable: empates conservan el orden de llegada)."""
    return sorted(cands, key=lambda c: -c.total)


# ---------------------------------------------------------------------------
# Helpers deterministas (rellenan sub-scores que ningun otro modulo llena)
# ---------------------------------------------------------------------------

def timeliness(cand: Candidate, now: datetime | None = None) -> float:
    """
    Recencia por fecha (0..1): 1.0 hoy, decae lineal a 0.0 en TIMELINESS_WINDOW_DAYS.
    Sin fecha -> TIMELINESS_UNKNOWN. Tentpole activo (cand.moment) suma un bonus
    (§4: "recencia + si toca un tentpole activo"). Escribe cand.scores["timeliness"].
    """
    now = now or datetime.now(timezone.utc)
    pub = cand.published
    if pub is None:
        score = TIMELINESS_UNKNOWN
    else:
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        age_days = max(0.0, (now - pub).total_seconds() / 86400.0)
        score = _clamp(1.0 - age_days / TIMELINESS_WINDOW_DAYS)
    if cand.moment:
        score = _clamp(score + TIMELINESS_MOMENT_BONUS)
    cand.scores["timeliness"] = round(score, 4)
    return cand.scores["timeliness"]


def authority(cand: Candidate) -> float:
    """
    Peso de la fuente (tier core > rotate > query) + bonus si la nota menciona
    gran marca o venue en entities (§4). Escribe cand.scores["authority"].
    """
    score = TIER_AUTHORITY.get((cand.tier or "").lower(), TIER_AUTHORITY["query"])
    ents = cand.entities or {}
    if ents.get("brands") or ents.get("venues"):
        score += AUTHORITY_ENTITY_BONUS
    cand.scores["authority"] = round(_clamp(score), 4)
    return cand.scores["authority"]


def novelty(cand: Candidate, used_topics) -> float:
    """
    Anti-repeticion por topic (no solo URL, §4): fresco 1.0, ya usado 0.2,
    sin topic 0.7. used_topics = topics de ediciones recientes (cualquier iterable).
    Escribe cand.scores["novelty"].
    """
    topic = (cand.topic or "").strip().lower()
    used = {(t or "").strip().lower() for t in (used_topics or ())}
    if not topic:
        score = NOVELTY_UNKNOWN
    elif topic in used:
        score = NOVELTY_REPEATED
    else:
        score = NOVELTY_FRESH
    cand.scores["novelty"] = score
    return score


# ---------------------------------------------------------------------------
# Loop de aprendizaje (§5): engagement -> pesos
# ---------------------------------------------------------------------------

def load_weights(path=DEFAULT_WEIGHTS_PATH) -> dict[str, float]:
    """
    Carga pesos desde JSON. Si el archivo no existe o esta corrupto, regresa una
    COPIA de WEIGHTS. Lo cargado se mezcla sobre los defaults (si manana agregamos
    una senal nueva, un weights.json viejo no la borra).
    """
    weights = dict(WEIGHTS)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for k, v in data.items():
                if k in weights and isinstance(v, (int, float)):
                    weights[k] = float(v)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return weights


def save_weights(path, weights: dict[str, float]) -> None:
    """Persiste pesos en JSON (crea data/ si hace falta)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump({k: round(float(v), 6) for k, v in sorted(weights.items())},
                  f, ensure_ascii=False, indent=2)


def adjust_weights(weights: dict[str, float], performance: dict) -> dict[str, float]:
    """
    Bandit sencillo (§5): sube el peso de las senales cuyas historias rindieron
    clicks; baja el de las que no. NO muta el dict de entrada.

    performance: {senal: rendimiento relativo en -1..1}. Ej.: si las historias con
    momentum alto ganaron clicks esta edicion, {"momentum": +0.6, "geo": -0.3}.
    (tracking.py calcula esos deltas a partir de los stats de Brevo.)

    Regla: w *= 1 + LEARNING_RATE * clamp(perf, -1, 1); luego se acota a
    [MIN_WEIGHT, MAX_WEIGHT] (nada muere, nada secuestra) y se renormaliza a
    suma 1.0 para que el total conserve escala entre semanas.
    """
    out = dict(weights)
    for key, perf in (performance or {}).items():
        if key in out and isinstance(perf, (int, float)):
            out[key] = float(out[key]) * (1.0 + LEARNING_RATE * _clamp(float(perf), -1.0, 1.0))
    out = {k: _clamp(float(v), MIN_WEIGHT, MAX_WEIGHT) for k, v in out.items()}
    total = sum(out.values())
    if total > 0:
        out = {k: v / total for k, v in out.items()}
    return out
