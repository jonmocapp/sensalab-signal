"""
Seleccion de historias + anti-repeticion (estado persistente en state.json).

Reglas:
  - Hasta MAX_STORIES slots. Diversidad de fuente primero (1 por fuente); si no se
    alcanza el minimo, se permite hasta 2 por fuente (asi no muere una semana floja).
  - Event Marketer y BizBash alternan el LEAD: EM semanas impares, BizBash pares (ISO week).
  - "The Sphere" maximo 2 semanas seguidas.
  - Se intenta un minimo de historias con foco geografico (best-effort; se avisa si no).
  - Nunca repetir una URL ya usada (normalizada, sin utm_).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from sources import Story

DEFAULT_STATE = {
    "issue_number": 0,
    "used_keys": [],
    "last_lead_source": "",
    "sphere_streak": 0,
    "history": [],
}


def load_state(path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in DEFAULT_STATE.items():
            data.setdefault(k, v)
        return data
    except FileNotFoundError:
        return dict(DEFAULT_STATE)  # primera corrida: normal, sin aviso
    except (json.JSONDecodeError, OSError) as e:
        # Estado corrupto: NO reseteamos en silencio (perderiamos la anti-repeticion).
        # Respaldamos el archivo malo y avisamos fuerte.
        try:
            bad = f"{path}.corrupto"
            os.replace(path, bad)
            print(f"  [ALERTA] state.json corrupto ({e}); respaldado en {bad}. "
                  "Se arranca de cero SOLO esta vez; revisa el respaldo.")
        except OSError:
            print(f"  [ALERTA] state.json corrupto ({e}) y no se pudo respaldar.")
        return dict(DEFAULT_STATE)


def save_state(path, state: dict) -> None:
    state["used_keys"] = state["used_keys"][-400:]
    # Escritura atomica: temp + os.replace para no dejar el archivo a medias si crashea.
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _iso_week(dt: datetime) -> int:
    return dt.isocalendar()[1]


def _mentions_sphere(st: Story) -> bool:
    import re
    return bool(re.search(r"\bthe sphere\b|\bsphere\b",
                          f"{st.headline} {st.summary}", re.IGNORECASE))


def choose(candidates: list[Story], state: dict, *,
           max_stories: int, min_geo: int, now: datetime | None = None) -> list[Story]:
    now = now or datetime.now(timezone.utc)
    used = set(state.get("used_keys", []))
    week = _iso_week(now)

    pool = [s for s in candidates if s.key() not in used]

    if state.get("sphere_streak", 0) >= 2:
        pool = [s for s in pool if not _mentions_sphere(s)]

    lead_source = "Event Marketer" if week % 2 == 1 else "BizBash"
    alt_source = "BizBash" if lead_source == "Event Marketer" else "Event Marketer"

    selected: list[Story] = []
    per_source: dict[str, int] = {}

    def take(story: Story):
        selected.append(story)
        per_source[story.source] = per_source.get(story.source, 0) + 1

    # 1) LEAD (fuente designada -> otra core -> mejor del pool)
    lead = (next((s for s in pool if s.source == lead_source), None)
            or next((s for s in pool if s.source == alt_source), None)
            or (pool[0] if pool else None))
    if lead:
        take(lead)

    # 2) Relleno: diversidad primero (cap 1/fuente), luego profundidad (cap 2/fuente)
    for cap in (1, 2):
        for s in pool:
            if len(selected) >= max_stories:
                break
            if s in selected:
                continue
            if per_source.get(s.source, 0) >= cap:
                continue
            take(s)

    # 3) Minimo geo (best-effort, re-filtrando cada iteracion para respetar caps)
    def geo_count():
        return sum(1 for s in selected if s.geo)

    while geo_count() < min_geo:
        # Elige primero la victima (no-geo, no el lead); luego un candidato geo que quepa
        # CONSIDERANDO el slot que libera la victima (asi no se pierde un swap valido cuando
        # candidato y victima comparten fuente).
        victim = next((s for s in reversed(selected[1:]) if not s.geo), None)
        if victim is None:
            break
        freed = victim.source
        cand = next((s for s in pool if s.geo and s not in selected
                     and per_source.get(s.source, 0) - (1 if s.source == freed else 0) < 2), None)
        if cand is None:
            break  # no hay mas geo disponibles -> se avisa afuera
        selected.remove(victim)
        per_source[victim.source] -= 1
        take(cand)

    return selected[:max_stories]


def geo_shortfall(selected: list[Story], min_geo: int) -> int:
    got = sum(1 for s in selected if s.geo)
    return max(0, min_geo - got)


def commit(state: dict, selected: list[Story], *, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    state["issue_number"] = state.get("issue_number", 0) + 1
    state["used_keys"].extend(s.key() for s in selected)
    if selected:
        state["last_lead_source"] = selected[0].source
    state["sphere_streak"] = (state.get("sphere_streak", 0) + 1
                              if any(_mentions_sphere(s) for s in selected) else 0)
    state["history"].append({
        "issue": state["issue_number"],
        "date": now.date().isoformat(),
        "sources": [s.source for s in selected],
        "headlines": [s.headline for s in selected],
    })
    state["history"] = state["history"][-52:]
    return state
