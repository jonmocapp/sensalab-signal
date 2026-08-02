"""
composer.py — EL CENTRO del Cerebro Inmersivo (ver notes/CEREBRO-INMERSIVO.md §3 y §4).

Algoritmos de composicion (6 formatos) + META-SELECTOR que elige el formato de la
semana como lo haria un editor. Todo determinista: cero LLM. Este modulo SOLO decide
estructura (que historias, en que orden, con que angulo); la prosa la escribe otro paso.

Formatos:
  A. digest       — 5 items balanceados, diversidad de fuente, min geo (default).
  B. moment       — momento activo o topic dominante fuerte → 1 hero + 3-4 angulos del mismo tema.
  C. teardown     — candidato con talkability alta (craft-fail/controversia) → 1 pieza + contexto.
  D. deep_dive    — semana floja + tema evergreen fuerte → 1 tema, varias facetas.
  E. steal_this   — momento cultural recien terminado → "N ideas que te puedes robar".
  F. tech_unlock  — señal de release de tool/modelo → "que desbloquea".

TABLA DE REGLAS DEL META-SELECTOR (gates duros + formula de fit + prioridad en empate):

  | Fmt | Gate duro                                                            | Fit                                        | Prio |
  |-----|----------------------------------------------------------------------|--------------------------------------------|------|
  | E   | momento "just-ended" con >= STEAL_CLUSTER_MIN (3) historias           | 0.70 + 0.20*min(1, n/5) [+0.10 cultural]    | 1    |
  | B   | momento activo con cluster >= MOMENT_CLUSTER_MIN (4), o topic fresco  | 0.60 + 0.25*dominancia [+0.10 tentpole]     | 2    |
  |     | dominante: cluster >= 4, ratio >= DOMINANCE_RATIO_MIN (0.45) y        |                                             |      |
  |     | "calor" (avg momentum o timeliness) >= DOMINANT_HEAT_MIN (0.50)       |                                             |      |
  | C   | max talkability >= TALKABILITY_MIN (0.70)                              | 0.45 + 0.50*max_talkability                 | 3    |
  | F   | candidato con entidad tech + (palabra de release o timeliness >= 0.70) | 0.50 + 0.35*señal                           | 4    |
  |     | y relevance >= 0.45 (o total >= 0.50)                                  | señal = 0.5*timeliness + 0.5*min(1,total)   |      |
  | D   | semana floja (max total < 0.60 y media < 0.45) + cluster evergreen     | 0.55 + 0.04*min(5, cluster)                 | 5    |
  |     | fresco >= 3 (avg timeliness <= 0.40, avg relevance >= 0.50)            |                                             |      |
  | A   | siempre elegible (fallback)                                            | 0.40 [+0.05 si pool rico: >=8 frescas y     | 6    |
  |     |                                                                        |  >=4 fuentes]                               |      |

  - Penalizacion anti-repeticion de formato: -FORMAT_REPEAT_PENALTY (0.15) si el formato
    no-digest fue el de la semana pasada (state["last_format"]).
  - El ganador no-digest debe superar MIN_FIT (0.55) Y el fit del digest; si no → Digest.
  - Pool < MIN_POOL (3) → Digest degradado directo (se indica en el plan).
  - Anti-repeticion por topic: state["used_topics"] excluye topics ya cubiertos del digest
    y de los temas de B/D; C y E quedan exentos (son event-driven, la noticia manda).

Imports perezosos: calendar_events (momentos activos/recien terminados) se usa si existe;
todo tolera su ausencia. Los sub-scores se leen con cand.scores.get(..., default).
"""
from __future__ import annotations

import importlib
from collections import Counter
from dataclasses import dataclass, field

from models import Candidate

# --------------------------------------------------------------------------
# Constantes / umbrales (comentados en la tabla del docstring)
# --------------------------------------------------------------------------

FORMAT_DIGEST = "digest"          # A
FORMAT_MOMENT = "moment"          # B
FORMAT_TEARDOWN = "teardown"      # C
FORMAT_DEEP_DIVE = "deep_dive"    # D
FORMAT_STEAL = "steal_this"       # E
FORMAT_TECH = "tech_unlock"       # F

FORMAT_LETTER = {
    FORMAT_DIGEST: "A", FORMAT_MOMENT: "B", FORMAT_TEARDOWN: "C",
    FORMAT_DEEP_DIVE: "D", FORMAT_STEAL: "E", FORMAT_TECH: "F",
}

# Prioridad en empate de fit (menor = gana). Orden editorial: lo mas raro y
# time-critical primero; digest siempre al final.
PRIORITY = {
    FORMAT_STEAL: 1, FORMAT_MOMENT: 2, FORMAT_TEARDOWN: 3,
    FORMAT_TECH: 4, FORMAT_DEEP_DIVE: 5, FORMAT_DIGEST: 6,
}

MIN_POOL = 3                  # < esto → digest degradado directo
DIGEST_TARGET = 5             # items del digest clasico
DIGEST_MIN_STORIES = 3        # < esto en el plan → degradado
MIN_FIT = 0.55                # un formato no-digest debe superar esto
DIGEST_BASE_FIT = 0.40        # fit baseline del digest (fallback)
DIGEST_RICH_BONUS = 0.05      # pool rico (>=8 frescas, >=4 fuentes)
FORMAT_REPEAT_PENALTY = 0.15  # mismo formato que la semana pasada

DOMINANCE_RATIO_MIN = 0.45    # B: fraccion del pool en el topic dominante
MOMENT_CLUSTER_MIN = 4        # B: hero + 3 minimo
DOMINANT_HEAT_MIN = 0.50      # B: el cluster debe estar "caliente" (spike), no evergreen
TALKABILITY_MIN = 0.70        # C: umbral de controversia/craft-fail
STEAL_CLUSTER_MIN = 3         # E: minimo de ideas robables
STEAL_CULTURAL_BONUS = 0.10   # E: bonus si el momento es tentpole cultural
WEAK_MAX_TOTAL = 0.60         # D: semana floja si max(total) < esto...
WEAK_MEAN_TOTAL = 0.45        # D: ...y media(total) < esto
EVERGREEN_CLUSTER_MIN = 3     # D: facetas minimas del tema
EVERGREEN_TIMELINESS_MAX = 0.40
EVERGREEN_RELEVANCE_MIN = 0.50
TECH_TIMELINESS_MIN = 0.70    # F: recencia que sustituye a la palabra de release
TECH_RELEVANCE_MIN = 0.45
TECH_TOTAL_MIN = 0.50
MIN_GEO_STORIES = 1           # digest: minimo de historias geo si el pool las tiene

# Señales lexicas de release (stems, en/es) para el formato F.
RELEASE_STEMS = (
    "launch", "releas", "unveil", "announc", "introduc", "ship", "debut",
    "drops", "rolls out", "now available", "beta", "sdk",
    "lanza", "lanzam", "anunci", "presenta", "estren", "ya disponible",
)

# Pistas de tentpole cultural (bonus del formato E).
CULTURAL_HINTS = (
    "mundial", "world-cup", "worldcup", "world cup", "coachella", "super-bowl",
    "superbowl", "super bowl", "olympic", "olimpi", "art-basel", "art basel",
    "comic-con", "comiccon", "grammy", "oscar", "cannes", "fifa", "f1",
)

PRODUCER_TEST = ("Test del productor: cada historia debe darle municion, inspiracion "
                 "o tema de conversacion para su proximo pitch de marca.")

# Instrucciones de tono para el writer (paso posterior; aqui solo estructura).
TONE_BY_FORMAT = {
    FORMAT_DIGEST: ("Agil y curado: 2-3 frases por item con POV de productor senior; "
                    "cero relleno; cada item cierra con el 'para que te sirve'."),
    FORMAT_MOMENT: ("Monografico: abre fuerte con el hero y trata cada historia como un "
                    "angulo distinto del MISMO tema; que se sienta cobertura de editor."),
    FORMAT_TEARDOWN: ("Critica de craft: que fallo, por que, y como se debio hacer. "
                      "Firme pero justo, sin burla; la leccion es accionable."),
    FORMAT_DEEP_DIVE: ("Explainer: un tema, varias facetas; enseña sin condescender; "
                       "ejemplos concretos y aplicables a activaciones."),
    FORMAT_STEAL: ("Playbook tactico y list-driven: N ideas robables numeradas; cada una "
                   "termina en algo que el lector puede proponer en su proximo pitch."),
    FORMAT_TECH: ("Señal: que salio, que desbloquea para experiencias en vivo, y que haria "
                  "un productor con esto el lunes."),
}


# --------------------------------------------------------------------------
# EditionPlan
# --------------------------------------------------------------------------

@dataclass
class EditionPlan:
    """Plan estructural de una edicion. La 1a historia de `stories` es el hero."""
    format_id: str                              # digest|moment|teardown|deep_dive|steal_this|tech_unlock
    theme: str | None                           # tema/momento de la edicion (None en digest)
    stories: list[Candidate]                    # en orden; stories[0] = hero
    angle_by_story: dict[str, str] = field(default_factory=dict)  # Candidate.key() -> angle
    rationale: str = ""                         # por que este formato y estas historias
    meta: dict = field(default_factory=dict)    # instrucciones para el writer + telemetria

    @property
    def hero(self) -> Candidate | None:
        return self.stories[0] if self.stories else None


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _lazy(name: str):
    """Import perezoso y tolerante: devuelve el modulo o None."""
    try:
        return importlib.import_module(name)
    except Exception:
        return None


def _total(c: Candidate) -> float:
    try:
        return float((c.scores or {}).get("total", 0.0))
    except Exception:
        return 0.0


def _s(c: Candidate, key: str, default: float = 0.0) -> float:
    try:
        return float((c.scores or {}).get(key, default))
    except Exception:
        return default


def _ents(c: Candidate, kind: str) -> list:
    return list((getattr(c, "entities", None) or {}).get(kind) or [])


def _clean(cands) -> list[Candidate]:
    """Dedup por key() conservando la version con mayor total; orden estable."""
    best: dict[str, Candidate] = {}
    for c in cands or []:
        if not (getattr(c, "headline", "") or "").strip():
            continue
        k = c.key()
        if k not in best or _total(c) > _total(best[k]):
            best[k] = c
    return list(best.values())


def _ranked(pool) -> list[Candidate]:
    """Orden determinista: total desc, luego headline (tie-break estable)."""
    return sorted(pool, key=lambda c: (-_total(c), (c.headline or "").lower()))


def _related(a: Candidate, b: Candidate) -> bool:
    """Mismo topic, mismo momento o entidades compartidas."""
    if a.topic and b.topic and a.topic.lower() == b.topic.lower():
        return True
    if a.moment and b.moment and a.moment == b.moment:
        return True
    ea = {e.lower() for e in a.all_entities()}
    eb = {e.lower() for e in b.all_entities()}
    return bool(ea & eb)


def _support_angle(c: Candidate, fallback: str) -> str:
    """Angulo de una historia de apoyo segun sus propias señales."""
    if _s(c, "talkability") >= TALKABILITY_MIN:
        return "teardown"
    if _ents(c, "tech"):
        return "tech-unlock"
    return fallback


def _has_release_word(c: Candidate) -> bool:
    text = ((c.headline or "") + " " + (c.summary or "")).lower()
    return any(stem in text for stem in RELEASE_STEMS)


def _is_cultural(moment_id: str) -> bool:
    m = (moment_id or "").lower()
    return any(h in m for h in CULTURAL_HINTS)


# --------------------------------------------------------------------------
# Señales del pool (todo lo que el meta-selector mira)
# --------------------------------------------------------------------------

def _signals(pool: list[Candidate], date, state: dict) -> dict:
    used = {str(t).lower() for t in (state.get("used_topics") or []) if t}

    # Anti-repeticion: "fresco" = topic no cubierto recientemente (o sin topic).
    fresh = [c for c in pool if not c.topic or c.topic.lower() not in used]

    # Clusters por topic (solo frescos, con topic).
    topic_counts = Counter(c.topic.lower() for c in fresh if c.topic)
    clusters = {t: [c for c in fresh if (c.topic or "").lower() == t] for t in topic_counts}

    dominant_topic, dominant_cluster, dominance, dom_heat = None, [], 0.0, 0.0
    if topic_counts:
        dominant_topic = max(topic_counts, key=lambda t: (topic_counts[t], t))
        dominant_cluster = clusters[dominant_topic]
        dominance = len(dominant_cluster) / max(1, len(pool))
        n = len(dominant_cluster)
        avg_mom = sum(_s(c, "momentum") for c in dominant_cluster) / n
        avg_tim = sum(_s(c, "timeliness") for c in dominant_cluster) / n
        dom_heat = max(avg_mom, avg_tim)

    # Momentos: estado explicito (state["moments"]) + calendar_events (perezoso)
    # + tags en candidatos (el tagger solo etiqueta momentos activos).
    status: dict[str, str] = {}
    for k, v in (state.get("moments") or {}).items():
        status[str(k)] = str(v)
    cal = _lazy("calendar_events")
    if cal is not None and date is not None:
        # calendar_events.active_moments(date) devuelve dicts con id/edition + phase
        # ("live"/"just-ended"/"upcoming"). (Antes se buscaban funciones inexistentes.)
        try:
            fn = getattr(cal, "active_moments", None)
            if callable(fn):
                for m in (fn(date) or []):
                    if isinstance(m, dict):
                        mid = m.get("edition") or m.get("id")
                        phase = str(m.get("phase") or "").lower()
                        if not mid:
                            continue
                        if phase == "just-ended":
                            status[str(mid)] = "just-ended"
                        elif phase in ("live", "active"):
                            status.setdefault(str(mid), "active")
                        # 'upcoming' no lo usa el meta-selector
                    elif m:
                        status.setdefault(str(m), "active")
        except Exception:
            pass
    if state.get("active_moment"):
        status.setdefault(str(state["active_moment"]), "active")
    for m in {c.moment for c in pool if c.moment}:
        status.setdefault(str(m), "active")

    def cluster_for_moment(mid: str) -> list[Candidate]:
        ml = mid.lower()
        return [c for c in pool
                if (c.moment or "").lower() == ml or (c.topic or "").lower() == ml]

    active_moment = None           # (id, cluster) del momento activo mas cubierto
    for m in sorted(m for m, s in status.items() if s == "active"):
        cl = cluster_for_moment(m)
        if len(cl) >= MOMENT_CLUSTER_MIN and (active_moment is None or len(cl) > len(active_moment[1])):
            active_moment = (m, cl)

    steal_moment = None            # (id, cluster) del momento recien terminado
    for m in sorted(m for m, s in status.items() if s == "just-ended"):
        cl = cluster_for_moment(m)
        if len(cl) >= STEAL_CLUSTER_MIN and (steal_moment is None or len(cl) > len(steal_moment[1])):
            steal_moment = (m, cl)

    # C: candidato mas "hablable".
    talk_hero = max(pool, key=lambda c: (_s(c, "talkability"), _total(c))) if pool else None

    # F: señal de release tech (primera en orden de ranking que cumpla el gate).
    tech_signal = None             # (cand, fuerza)
    for c in _ranked(pool):
        if not _ents(c, "tech"):
            continue
        if c.moment and _is_cultural(c.moment):
            continue  # pertenece a un momento cultural (Mundial, etc.), no es un release de tool
        if not _has_release_word(c):
            continue  # exige palabra de release REAL: no basta con ser fresca y tener tech
        if _s(c, "relevance") < TECH_RELEVANCE_MIN and _total(c) < TECH_TOTAL_MIN:
            continue
        tech_signal = (c, 0.5 * min(1.0, _s(c, "timeliness")) + 0.5 * min(1.0, _total(c)))
        break

    # D: semana floja + tema evergreen fresco.
    totals = [_total(c) for c in pool]
    weak_week = bool(totals) and max(totals) < WEAK_MAX_TOTAL and \
        (sum(totals) / len(totals)) < WEAK_MEAN_TOTAL
    hinted = {str(t).lower() for t in (state.get("evergreen_topics") or [])}
    evergreen = None               # (topic, cluster)
    for t, cl in sorted(clusters.items(),
                        key=lambda kv: (-len(kv[1]),
                                        -sum(_total(c) for c in kv[1]) / max(1, len(kv[1])),
                                        kv[0])):
        if len(cl) < EVERGREEN_CLUSTER_MIN:
            continue
        avg_tim = sum(_s(c, "timeliness") for c in cl) / len(cl)
        avg_rel = sum(_s(c, "relevance") for c in cl) / len(cl)
        if t in hinted or (avg_tim <= EVERGREEN_TIMELINESS_MAX and avg_rel >= EVERGREEN_RELEVANCE_MIN):
            evergreen = (t, cl)
            break

    return {
        "n": len(pool),
        "n_fresh": len(fresh),
        "n_sources": len({(c.source or "").lower() for c in pool}),
        "used": used,
        "fresh": fresh,
        "clusters": clusters,
        "dominant_topic": dominant_topic,
        "dominant_cluster": dominant_cluster,
        "dominance": dominance,
        "dominant_heat": dom_heat,
        "active_moment": active_moment,
        "steal_moment": steal_moment,
        "talk_hero": talk_hero,
        "tech_signal": tech_signal,
        "weak_week": weak_week,
        "evergreen": evergreen,
    }


# --------------------------------------------------------------------------
# META-SELECTOR
# --------------------------------------------------------------------------

def choose_format(cands, date=None, state=None) -> tuple[str, float, str]:
    """Puntua el fit de cada formato dado el pool y devuelve
    (formato_id, fit_score, razon). Determinista; fallback siempre a Digest."""
    state = state or {}
    pool = _clean(cands)
    if len(pool) < MIN_POOL:
        return (FORMAT_DIGEST, DIGEST_BASE_FIT,
                f"Pool insuficiente ({len(pool)} < {MIN_POOL}): Digest degradado.")

    sig = _signals(pool, date, state)
    fits: dict[str, tuple[float, str]] = {}

    # --- A. Digest: baseline, siempre elegible --------------------------------
    base = DIGEST_BASE_FIT
    if sig["n_fresh"] >= 8 and sig["n_sources"] >= 4:
        base += DIGEST_RICH_BONUS
    fits[FORMAT_DIGEST] = (base, "Default editorial: pool balanceado sin señal fuerte "
                                 "de otro formato → digest de 5 items.")

    # --- E. Steal-This: momento recien terminado ------------------------------
    if sig["steal_moment"]:
        m, cl = sig["steal_moment"]
        fit = 0.70 + 0.20 * min(1.0, len(cl) / 5.0)
        cultural = _is_cultural(m)
        if cultural:
            fit += STEAL_CULTURAL_BONUS
        fits[FORMAT_STEAL] = (min(fit, 1.0),
                              f"Momento '{m}' recien terminado con {len(cl)} historias"
                              + (" (tentpole cultural)" if cultural else "")
                              + " → playbook de ideas robables.")

    # --- B. Momento/Tematico: momento activo o topic dominante caliente -------
    b_fit, b_reason = 0.0, ""
    if sig["active_moment"]:
        m, cl = sig["active_moment"]
        b_fit = 0.60 + 0.25 * (len(cl) / max(1, sig["n"])) + 0.10  # +0.10 tentpole activo
        b_reason = (f"Momento activo '{m}' con {len(cl)} historias → "
                    "monografico 1 hero + angulos del mismo tema.")
    if (sig["dominant_topic"] and len(sig["dominant_cluster"]) >= MOMENT_CLUSTER_MIN
            and sig["dominance"] >= DOMINANCE_RATIO_MIN
            and sig["dominant_heat"] >= DOMINANT_HEAT_MIN):
        alt = 0.60 + 0.25 * sig["dominance"]
        if alt > b_fit:
            b_fit = alt
            b_reason = (f"Topic dominante fresco '{sig['dominant_topic']}' "
                        f"({len(sig['dominant_cluster'])}/{sig['n']} historias, "
                        f"calor {sig['dominant_heat']:.2f}) → edicion tematica.")
    if b_fit > 0:
        fits[FORMAT_MOMENT] = (min(b_fit, 1.0), b_reason)

    # --- C. Teardown: talkability alta -----------------------------------------
    th = sig["talk_hero"]
    if th is not None and _s(th, "talkability") >= TALKABILITY_MIN:
        talk = min(1.0, _s(th, "talkability"))
        fits[FORMAT_TEARDOWN] = (0.45 + 0.50 * talk,
                                 f"'{th.headline[:70]}' con talkability {talk:.2f} "
                                 "(craft-fail/controversia) → teardown con lente de craft.")

    # --- F. Tech-unlock: señal de release --------------------------------------
    if sig["tech_signal"]:
        c, strength = sig["tech_signal"]
        if not c.topic or c.topic.lower() not in sig["used"]:  # anti-repeticion de tema
            fits[FORMAT_TECH] = (0.50 + 0.35 * strength,
                                 f"Release detectado: '{c.headline[:70]}' "
                                 f"(tech: {', '.join(_ents(c, 'tech')[:3])}) → que desbloquea.")

    # --- D. Deep Dive: semana floja + evergreen fuerte --------------------------
    if sig["weak_week"] and sig["evergreen"]:
        t, cl = sig["evergreen"]
        fits[FORMAT_DEEP_DIVE] = (0.55 + 0.04 * min(5, len(cl)),
                                  f"Semana floja (sin picos) + tema evergreen '{t}' con "
                                  f"{len(cl)} facetas → deep dive.")

    # --- Penalizacion por repetir formato de la semana pasada -------------------
    last = state.get("last_format")
    if last and last in fits and last != FORMAT_DIGEST:
        f, r = fits[last]
        fits[last] = (f - FORMAT_REPEAT_PENALTY, r + " (penalizado: repite formato)")

    # --- Ganador: fit desc, prioridad editorial en empate ------------------------
    ordered = sorted(fits.items(), key=lambda kv: (-kv[1][0], PRIORITY[kv[0]]))
    fmt, (fit, reason) = ordered[0]
    digest_fit = fits[FORMAT_DIGEST][0]
    if fmt != FORMAT_DIGEST and (fit < MIN_FIT or fit <= digest_fit):
        return (FORMAT_DIGEST, digest_fit,
                f"Fallback a Digest: '{fmt}' no supero umbral "
                f"(fit {fit:.2f} vs MIN_FIT {MIN_FIT} / digest {digest_fit:.2f}).")
    return (fmt, round(fit, 3), reason)


# --------------------------------------------------------------------------
# Formatos (cada uno: pool scoreado + fecha + estado → EditionPlan | None)
# --------------------------------------------------------------------------

def compose_digest(cands, date=None, state=None, max_stories=DIGEST_TARGET) -> EditionPlan:
    """A. Digest: items balanceados; diversidad de fuente y topic; min geo.
    Nunca devuelve None (es el fallback universal)."""
    state = state or {}
    pool = _clean(cands)
    used = {str(t).lower() for t in (state.get("used_topics") or []) if t}
    ranked = _ranked(pool)
    target = max(1, max_stories)

    picks: list[Candidate] = []
    seen_src: set[str] = set()
    seen_topic: set[str] = set()

    def fresh_ok(c):  # anti-repeticion por topic
        return not c.topic or c.topic.lower() not in used

    # Pases de relajacion: 1) fresco + fuente y topic unicos; 2) fresco + topic
    # unico; 3) topic unico (permite topics usados); 4) lo que quede.
    passes = (
        lambda c: fresh_ok(c) and (c.source or "").lower() not in seen_src
                  and (not c.topic or c.topic.lower() not in seen_topic),
        lambda c: fresh_ok(c) and (not c.topic or c.topic.lower() not in seen_topic),
        lambda c: (not c.topic or c.topic.lower() not in seen_topic),
        lambda c: True,
    )
    relaxed_note = ""
    for i, ok in enumerate(passes):
        for c in ranked:
            if len(picks) >= target:
                break
            if c in picks or not ok(c):
                continue
            picks.append(c)
            seen_src.add((c.source or "").lower())
            if c.topic:
                seen_topic.add(c.topic.lower())
        if len(picks) >= target:
            if i >= 2:
                relaxed_note = " (relajado: se admitieron topics ya cubiertos)"
            break

    # Min geo: si el pool tiene historias geo y no quedo ninguna, mete la mejor
    # geo reemplazando la pick de menor total no-geo.
    geo_pool = [c for c in ranked if c.geo]
    if geo_pool and MIN_GEO_STORIES and not any(c.geo for c in picks):
        best_geo = next((c for c in geo_pool if c not in picks), None)
        if best_geo is not None:
            non_geo = [c for c in picks if not c.geo]
            if len(picks) >= target and non_geo:
                worst = min(non_geo, key=_total)
                picks[picks.index(worst)] = best_geo
            else:
                picks.append(best_geo)
    picks = _ranked(picks)  # hero = mayor total; orden final por total

    degraded = len(picks) < DIGEST_MIN_STORIES
    angles = {c.key(): (c.angle or "straight") for c in picks}
    rationale = (f"Digest de {len(picks)} items: balance de score, diversidad de fuente "
                 f"({len({(c.source or '').lower() for c in picks})} fuentes) y "
                 f"min {MIN_GEO_STORIES} geo{relaxed_note}.")
    if degraded:
        rationale = (f"EDICION DEGRADADA: solo {len(picks)} candidatas utilizables "
                     f"(< {DIGEST_MIN_STORIES}). " + rationale)
    return EditionPlan(
        format_id=FORMAT_DIGEST, theme=None, stories=picks, angle_by_story=angles,
        rationale=rationale,
        meta={"degraded": degraded,
              "min_geo_ok": any(c.geo for c in picks) or not geo_pool},
    )


def compose_moment(cands, date=None, state=None, max_stories=DIGEST_TARGET) -> EditionPlan | None:
    """B. Momento/Tematico: 1 hero + 3-4 angulos del MISMO tema."""
    state = state or {}
    pool = _clean(cands)
    sig = _signals(pool, date, state)

    if sig["active_moment"]:
        theme, cluster = sig["active_moment"]
        why = f"momento activo '{theme}'"
    elif (sig["dominant_topic"] and len(sig["dominant_cluster"]) >= MOMENT_CLUSTER_MIN
          and sig["dominance"] >= DOMINANCE_RATIO_MIN
          and sig["dominant_heat"] >= DOMINANT_HEAT_MIN):
        theme, cluster = sig["dominant_topic"], sig["dominant_cluster"]
        why = f"topic dominante '{theme}' ({len(cluster)}/{sig['n']} del pool)"
    else:
        return None

    ranked = _ranked(cluster)
    hero, rest = ranked[0], ranked[1:]
    n_support = min(4, max(1, max_stories) - 1)  # 3-4 angulos de apoyo

    # Apoyo con preferencia de fuentes distintas; luego rellena.
    support: list[Candidate] = []
    seen_src = {(hero.source or "").lower()}
    for c in rest:
        if len(support) >= n_support:
            break
        if (c.source or "").lower() not in seen_src:
            support.append(c)
            seen_src.add((c.source or "").lower())
    for c in rest:
        if len(support) >= n_support:
            break
        if c not in support:
            support.append(c)

    stories = [hero] + support
    cycle = ("straight", "steal-this", "recap")
    angles = {hero.key(): "bar-moved"}
    ci = 0
    for c in support:
        a = _support_angle(c, cycle[ci % len(cycle)])
        if a == cycle[ci % len(cycle)]:
            ci += 1
        angles[c.key()] = a
    return EditionPlan(
        format_id=FORMAT_MOMENT, theme=theme, stories=stories, angle_by_story=angles,
        rationale=(f"Edicion tematica por {why}: hero '{hero.headline[:70]}' + "
                   f"{len(support)} angulos del mismo tema."),
        meta={"why": why},
    )


def compose_teardown(cands, date=None, state=None, max_stories=DIGEST_TARGET) -> EditionPlan | None:
    """C. Teardown/Critica: la pieza mas 'hablable' + contexto."""
    state = state or {}
    pool = _clean(cands)
    if not pool:
        return None
    hero = max(pool, key=lambda c: (_s(c, "talkability"), _total(c)))
    if _s(hero, "talkability") < TALKABILITY_MIN:
        return None

    n_ctx = min(3, max(1, max_stories) - 1)
    related = _ranked([c for c in pool if c is not hero and _related(hero, c)])[:n_ctx]
    filler = [c for c in _ranked(pool) if c is not hero and c not in related]
    context = related + filler[:max(0, n_ctx - len(related))]

    stories = [hero] + context
    angles = {hero.key(): "teardown"}
    for c in context:
        angles[c.key()] = "recap" if c in related else "straight"
    return EditionPlan(
        format_id=FORMAT_TEARDOWN, theme=hero.topic or None, stories=stories,
        angle_by_story=angles,
        rationale=(f"Teardown de '{hero.headline[:70]}' "
                   f"(talkability {_s(hero, 'talkability'):.2f}) + {len(context)} piezas "
                   f"de contexto ({len(related)} relacionadas)."),
        meta={"related_context": len(related)},
    )


def compose_deep_dive(cands, date=None, state=None, max_stories=DIGEST_TARGET) -> EditionPlan | None:
    """D. Deep Dive: un tema evergreen, varias facetas (semana floja)."""
    state = state or {}
    pool = _clean(cands)
    sig = _signals(pool, date, state)
    if not sig["evergreen"]:
        return None
    theme, cluster = sig["evergreen"]
    stories = _ranked(cluster)[:max(1, max_stories)]
    if len(stories) < EVERGREEN_CLUSTER_MIN:
        return None
    cycle = ("steal-this", "recap", "straight")
    angles = {stories[0].key(): "straight"}  # hero = explainer central
    ci = 0
    for c in stories[1:]:
        a = _support_angle(c, cycle[ci % len(cycle)])
        if a == cycle[ci % len(cycle)]:
            ci += 1
        angles[c.key()] = a
    return EditionPlan(
        format_id=FORMAT_DEEP_DIVE, theme=theme, stories=stories, angle_by_story=angles,
        rationale=(f"Deep dive en '{theme}': semana floja, tema evergreen con "
                   f"{len(stories)} facetas."),
        meta={"weak_week": sig["weak_week"]},
    )


def compose_steal_this(cands, date=None, state=None, max_stories=DIGEST_TARGET) -> EditionPlan | None:
    """E. Steal-This Playbook: N ideas robables tras un momento recien terminado."""
    state = state or {}
    pool = _clean(cands)
    sig = _signals(pool, date, state)
    if not sig["steal_moment"]:
        return None
    theme, cluster = sig["steal_moment"]
    stories = _ranked(cluster)[:max(1, max_stories)]
    if len(stories) < STEAL_CLUSTER_MIN:
        return None
    angles = {c.key(): "steal-this" for c in stories}
    return EditionPlan(
        format_id=FORMAT_STEAL, theme=theme, stories=stories, angle_by_story=angles,
        rationale=(f"Playbook post-'{theme}': {len(stories)} ideas que te puedes robar, "
                   "ordenadas por score."),
        meta={"cultural": _is_cultural(theme)},
    )


def compose_tech_unlock(cands, date=None, state=None, max_stories=DIGEST_TARGET) -> EditionPlan | None:
    """F. Signal/Tech-unlock: release de tool/modelo → que desbloquea."""
    state = state or {}
    pool = _clean(cands)
    sig = _signals(pool, date, state)
    if not sig["tech_signal"]:
        return None
    hero, strength = sig["tech_signal"]
    hero_tech = {e.lower() for e in _ents(hero, "tech")}

    def shares_tech(c):
        return bool(hero_tech & {e.lower() for e in _ents(c, "tech")})

    related = _ranked([c for c in pool if c is not hero
                       and (shares_tech(c) or _related(hero, c))])
    support = related[:min(3, max(1, max_stories) - 1)]

    stories = [hero] + support
    angles = {hero.key(): "tech-unlock"}
    for c in support:
        # Con marca/venue/agencia = aplicacion robable; si no, contexto directo.
        applied = _ents(c, "brands") or _ents(c, "venues") or _ents(c, "agencies")
        angles[c.key()] = "steal-this" if applied else "straight"
    theme = (_ents(hero, "tech") or [hero.topic or None])[0]
    return EditionPlan(
        format_id=FORMAT_TECH, theme=theme, stories=stories, angle_by_story=angles,
        rationale=(f"Señal tech: '{hero.headline[:70]}' (fuerza {strength:.2f}) → "
                   f"que desbloquea para experiencias; {len(support)} piezas de apoyo."),
        meta={"signal_strength": round(strength, 3)},
    )


FORMAT_FUNCS = {
    FORMAT_DIGEST: compose_digest,
    FORMAT_MOMENT: compose_moment,
    FORMAT_TEARDOWN: compose_teardown,
    FORMAT_DEEP_DIVE: compose_deep_dive,
    FORMAT_STEAL: compose_steal_this,
    FORMAT_TECH: compose_tech_unlock,
}


# --------------------------------------------------------------------------
# Orquestador
# --------------------------------------------------------------------------

def compose(cands, date=None, state=None, max_stories=DIGEST_TARGET) -> EditionPlan:
    """Corre choose_format y la funcion del formato ganador. Setea cand.angle por
    historia. Robusto: pool corto o formato imposible → Digest (indicado en el plan)."""
    state = state or {}
    pool = _clean(cands)

    if len(pool) < MIN_POOL:
        plan = compose_digest(pool, date, state, max_stories)
        plan.meta["degraded"] = True
        plan.meta["fit_score"] = DIGEST_BASE_FIT
        plan.meta["selector_reason"] = (f"Pool insuficiente ({len(pool)} < {MIN_POOL}): "
                                        "Digest degradado.")
        if "DEGRADADA" not in plan.rationale:
            plan.rationale = (f"EDICION DEGRADADA: solo {len(pool)} candidatas "
                              f"(< {MIN_POOL}). " + plan.rationale)
        return _finalize(plan, pool, date)

    fmt, fit, reason = choose_format(pool, date, state)
    plan = FORMAT_FUNCS[fmt](pool, date, state, max_stories)
    if plan is None:  # defensa: el gate paso pero la composicion no alcanzo
        plan = compose_digest(pool, date, state, max_stories)
        reason += f" | Fallback a Digest: '{fmt}' no logro componer historias suficientes."
        fmt, fit = FORMAT_DIGEST, DIGEST_BASE_FIT
    plan.meta["fit_score"] = fit
    plan.meta["selector_reason"] = reason
    return _finalize(plan, pool, date)


def _finalize(plan: EditionPlan, pool: list[Candidate], date) -> EditionPlan:
    """Aplica angulos a los Candidates y completa meta para el writer."""
    for c in plan.stories:
        c.angle = plan.angle_by_story.get(c.key(), c.angle or "straight")
    plan.meta.setdefault("degraded", len(plan.stories) < DIGEST_MIN_STORIES)
    plan.meta.update({
        "format_letter": FORMAT_LETTER.get(plan.format_id, "?"),
        "tone": TONE_BY_FORMAT.get(plan.format_id, TONE_BY_FORMAT[FORMAT_DIGEST]),
        "producer_test": PRODUCER_TEST,
        "theme": plan.theme,
        "hero_key": plan.hero.key() if plan.hero else None,
        "n_pool": len(pool),
        "n_stories": len(plan.stories),
        "date": str(date) if date else None,
    })
    plan.meta.setdefault("min_geo_ok",
                         any(c.geo for c in plan.stories) or not any(c.geo for c in pool))
    return plan
