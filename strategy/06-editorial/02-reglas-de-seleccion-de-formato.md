# Reglas de selección de formato — mejoras para `build_edition.py`

Descripción de reglas para que Jon las integre después. **No se editó ningún .py.**

## Estado actual (diagnóstico)

`build_edition.choose_format()` hoy decide con una sola señal:
`talkability = suma de substrings _TALK en todo el texto` y regla
`teardown si (bloque teardown presente) y (talkability >= 2)`, si no → Signal.

Problemas concretos detectados en el código actual:

1. **Substring matching sin límites de palabra**: `blob.count("slop")` matchea "slope";
   `"fake"` matchea "fakery" (aceptable) pero también dentro de palabras. `sources.py` ya
   resuelve esto con `\b` regex — misma técnica aplica aquí.
2. **Cuenta repeticiones, no señales**: una sola palabra repetida 3 veces = 3 puntos. Un
   texto que dice "backlash" dos veces no es más polarizante que uno que dice "backlash"
   + "comments off" + "torched".
3. **Señales dispersas = falso positivo**: 5 secciones con 1 palabra tibia cada una suman
   igual que UN caso concentrado. El Teardown necesita UN objeto polarizante, no ruido
   repartido.
4. **Sin memoria de formato**: puede salir Teardown 4 semanas seguidas (fatiga; composer.py
   ya penaliza repetición con `FORMAT_REPEAT_PENALTY` — build_edition no).
5. **Ciego al calendario**: la semana post-Comic-Con con 4 historias del tema pide playbook
   (steal-this), no digest — build_edition no consulta `calendar_events.py`.
6. **Duplica el cerebro**: `composer.choose_format()` ya evalúa 6 formatos con gates + fit;
   build_edition reimplementa una versión pobre de la señal C.

## Reglas afinadas (señales concretas)

### A. Talkability v2 (para el gate del Teardown)

- **A1 — regex con límites de palabra**, reutilizando el patrón `_compile()` de `sources.py`.
- **A2 — contar términos DISTINTOS**, cap de 2 puntos por término (anti-spam de una palabra).
- **A3 — dos niveles de señal**:
  - STRONG (2 pts c/u): `backlash`, `torched`, `comments off` / `switched off` /
    `turn off comments`, `called it fake`, `dragged`, `roast`, `slop`, `flop`, `blocked`,
    `covered the logo`.
  - MILD (1 pt c/u): `disappoint`, `cringe`, `controvers`, `too smooth`, `went viral`,
    `mock`, `criticiz`, `fake`.
  - **Gate: >= 3 puntos con al menos 1 STRONG** (sustituye al `>= 2` actual).
- **A4 — concentración en el hero**: >= 60% de los puntos deben venir del bloque
  `teardown` (verdict/flaw/statement) o de UNA sola sección. Señales repartidas en 3+
  secciones sin bloque dominante → sigue siendo Signal. (Un teardown es una autopsia de UN
  caso.)
- **A5 — frescura del caso**: si la edición trae fecha del caso, exigir <= 10 días
  (`TIMELINESS_WINDOW_DAYS` de scoring.py). Controversia vieja leída tarde = daño de marca.

### B. Señales de calendario (nuevas; consultar `calendar_events.active_moments(date)`)

- **B1 — steal-this**: momento `just-ended` con `brand_activation: true` y >= 3 historias
  de la edición matcheando sus keywords → formato steal_this. Mientras no exista
  `render_steal`: renderizar con Signal forzando `angle="steal-this"` en todas las cards e
  intro numerada ("N ideas you can steal from ___").
- **B2 — moment**: momento `live` con >= 4 historias del tema → formato moment.
  Interim: Signal con el hero del cluster primero y las relacionadas juntas.
- **B3 — fuente de fechas**: las ventanas NO deben vivir hardcodeadas en 2 lugares.
  `tentpole-calendar.json` (en esta carpeta) es la fuente de datos; `calendar_events.py`
  debería poder cargarla (los eventos anclados a año como SIGGRAPH cambian de mes entre
  años — ver corrección abajo).

### C. Señal de release (tech-unlock)

- **C1**: entidad `tech` del lexicon presente + >= 1 stem de `RELEASE_STEMS` (composer.py)
  en headline+summary + el candidato NO pertenece a un momento cultural → framing
  tech-unlock ("what this unlocks"). Interim: Signal con hero-focus.

### D. Anti-fatiga de formato

- **D1**: persistir `state.json` con `last_formats` (últimas 4 ediciones). Reglas: no
  repetir teardown si hubo uno en las últimas 2 ediciones; máximo 2 teardowns por cada 4
  ediciones; espejo del `FORMAT_REPEAT_PENALTY` (0.15) de composer.py para los demás.

### E. Prioridad cuando compiten señales

Orden: **teardown fuerte** (>= 5 pts concentrados y caso <= 10 días) → **steal_this**
(just-ended brand_activation) → **moment** (live) → **tech_unlock** → **signal** (default).
Racional editorial: un craft-fail jugoso es más raro y genera más conversación que un recap
que toda la prensa del sector también va a hacer; pero un teardown tibio nunca le gana a un
tentpole caliente.

### F. Ruta de integración recomendada (la mejora estructural)

`build_edition.choose_format()` debería **delegar en `composer.choose_format(cands, date,
state)`** cuando la edición venga del pipeline v2, y quedarse solo con el mapeo
formato → renderer disponible:

```
teardown            → render_teardown
todo lo demás (A/B/D/E/F) → render_signal (con el framing del formato)
```

registrando `meta["renderer_gap"] = formato_elegido` cuando el formato ganador no tenga
renderer propio. Esa telemetría dice QUÉ renderer construir primero con datos reales
(la predicción del calendario: `render_steal`).

## Corrección de datos detectada (importante)

`calendar_events.py` define SIGGRAPH con ventana `(8, 9)–(8, 13)`. **SIGGRAPH 2026 real fue
19–23 de julio** (LA Convention Center, s2026.siggraph.org). La ventana recurrente mes/día
no sirve para eventos que cambian de mes entre años (SIGGRAPH 2025 fue en agosto, 2026 en
julio): esos deben anclarse por año con el campo `"year"` que el módulo ya soporta, o
cargarse desde `tentpole-calendar.json`. Con la ventana actual, el motor se habría perdido
el momento SIGGRAPH por 3 semanas.
