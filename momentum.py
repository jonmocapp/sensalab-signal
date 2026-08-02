"""
momentum.py — deteccion de picos/temas del CEREBRO INMERSIVO (§4 momentum, §2 modulos).

Clusteriza candidatos por `topic` (o entidad dominante si el topic viene vacio) y
escribe cand.scores["momentum"] en 0..1: un tema con muchos candidatos esta semana
(cluster grande) esta "en pico"; un tentpole activo (cand.moment) tambien empuja.

Puro conteo/heuristica determinista. Sin APIs externas, sin estado en disco.
Interfaz del cerebro (§1): funciones puras que mutan la lista en sitio.
"""
from __future__ import annotations

from collections import Counter

from models import Candidate

# --- Parametros de la heuristica (documentados para poder tunearlos) ---

# Tamano de cluster al que el momentum por volumen SATURA en 1.0.
# Con 5 candidatos del mismo tema en una semana, el tema claramente domina el pool
# (una edicion son ~5 historias): (size-1)/(SATURATION_SIZE-1) -> 1.0 en size>=5.
SATURATION_SIZE = 5

# Bonus por tentpole activo (cand.moment seteado por calendar_events.py).
# 0.5 = un candidato SOLO pero dentro de un momento (SIGGRAPH, Mundial) ya arranca
# a media escala, sin necesitar volumen; con algo de volumen llega al tope rapido.
MOMENT_BONUS = 0.5


def _norm(text: str) -> str:
    return (text or "").strip().lower()


def _entity_counts(cands: list[Candidate]) -> Counter:
    """Frecuencia global de cada entidad (normalizada) en el pool."""
    counts: Counter = Counter()
    for c in cands:
        for ent in c.all_entities():
            e = _norm(ent)
            if e:
                counts[e] += 1
    return counts


def _cluster_key(cand: Candidate, entity_counts: Counter) -> str:
    """
    Llave de cluster de un candidato:
      1) su `topic` normalizado, si existe;
      2) si no, su entidad DOMINANTE: la entidad del candidato mas frecuente en el
         pool completo (asi dos notas sin topic pero sobre "sphere" caen juntas).
         Empates se rompen alfabeticamente (determinista);
      3) si tampoco hay entidades, su key() (URL normalizada) -> cluster singleton.
    """
    topic = _norm(cand.topic)
    if topic:
        return topic
    ents = sorted({_norm(e) for e in cand.all_entities() if _norm(e)})
    if ents:
        return sorted(ents, key=lambda e: (-entity_counts[e], e))[0]
    return cand.key()


def cluster(cands: list[Candidate]) -> dict[str, list[Candidate]]:
    """Agrupa candidatos por tema (topic o entidad dominante). Orden estable."""
    counts = _entity_counts(cands)
    out: dict[str, list[Candidate]] = {}
    for c in cands:
        out.setdefault(_cluster_key(c, counts), []).append(c)
    return out


def score_momentum(cands: list[Candidate]) -> None:
    """
    Escribe cand.scores["momentum"] (0..1) para cada candidato:

      volumen = min(1, (tamano_cluster - 1) / (SATURATION_SIZE - 1))
                (singleton = 0.0; crece linealmente; satura en SATURATION_SIZE)
      momentum = min(1, volumen + MOMENT_BONUS si cand.moment esta seteado)
    """
    clusters = cluster(cands)
    size_by_id = {id(c): len(members) for members in clusters.values() for c in members}
    for c in cands:
        size = size_by_id.get(id(c), 1)
        volume = min(1.0, max(0.0, (size - 1) / (SATURATION_SIZE - 1)))
        bonus = MOMENT_BONUS if c.moment else 0.0
        c.scores["momentum"] = round(min(1.0, volume + bonus), 4)


def dominant_topic(cands: list[Candidate]) -> tuple[str, int] | None:
    """
    El tema con mas candidatos esta semana y su tamano — insumo del META-selector
    para decidir una edicion tematica (formato B). None si el pool viene vacio.
    Empates se rompen alfabeticamente por llave (determinista).
    """
    clusters = cluster(cands)
    if not clusters:
        return None
    key = sorted(clusters, key=lambda k: (-len(clusters[k]), k))[0]
    return key, len(clusters[key])
