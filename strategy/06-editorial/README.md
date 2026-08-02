# 06 — Calendario editorial & pipeline de contenido

Especialista 06. Política editorial del cerebro "AI sin AI" de INMERSIVO.
Fecha de trabajo: 2026-07-27. Guardarriel legal respetado en todos los entregables
(cero referencias a trabajo pasado del fundador/clientes/Cinética; cero datos inventados;
todas las fechas verificadas contra fuentes públicas).

## Qué entregué

| Archivo | Contenido |
|---|---|
| `01-pilares-de-contenido.md` | Los 5 pilares (bar-moved, steal-this, teardown, tech-unlock, framework), mapeo pilar → formato → renderer (qué está construido y qué falta), matriz pilar × formato con titulares concretos, cadencia objetivo. |
| `02-reglas-de-seleccion-de-formato.md` | Diagnóstico del `choose_format()` actual de `build_edition.py` y reglas afinadas: talkability v2 (niveles, concentración, frescura), señales de calendario, anti-fatiga, prioridades de empate y ruta de integración con `composer.py`. Solo descripción — **no toqué ningún .py**. |
| `03-calendario-editorial-12-semanas.md` | Semana a semana (27 jul → 18 oct 2026): momento probable, formato sugerido, pilar/ángulo, qué le importa al productor y subject de ejemplo en inglés. |
| `tentpole-calendar.json` | 17 eventos con fecha verificada + 6 watch items (fecha flotante/probable). Schema pensado para que `calendar_events.py` lo cargue y `ingest_news.py` genere queries dinámicas por tentpole. Validado (parsea). |
| `04-fuentes-de-senales.md` | 4 capas de señal más allá del RSS actual: feeds candidatos, queries de Google News (fijas + dinámicas desde el JSON), ciclos de premios, y señales sociales manuales; cómo se combinan en "el momento de la semana". |

## Skills usados

- **`content-strategy`**: metodología de pilares (product-led + audience-led),
  searchable/shareable, y priorización por impacto en el cliente — aplicada a los 5 pilares
  y su racional por ICP.
- **`content-matrix`**: metodología de matriz pilar × formato con una idea concreta por
  celda. Adaptación declarada: las columnas son los formatos reales del motor (Signal,
  Teardown, Steal-this, Moment, Deep dive) en lugar de los 8 formatos de post social del
  skill, y los inputs (pilares, "quién soy") vienen del BRIEF en vez de entrevista
  interactiva — esta sesión corre sin usuario en vivo.

## Decisiones clave

1. **`framework` como 5º pilar** (no existe hoy como `Candidate.angle`): es el pilar de
   inventario que resuelve las semanas valle y el que más compone autoridad para el blog
   futuro. Los otros 4 ya existen en el contrato de datos.
2. **Prioridad de renderers por datos del calendario**: `render_steal` primero (4 semanas
   de 12 lo piden), luego `render_moment` (3), luego `render_deep_dive` (2). Mientras
   tanto, degradación controlada a Signal con telemetría `renderer_gap`.
3. **El teardown no se agenda**: es oportunista (talkability) y desplaza a cualquier
   formato semanal. El calendario marca las semanas teardown-friendly (2 y 8).
4. **El calendario alimenta la ingesta**: los `keywords` de cada tentpole se convierten en
   queries de Google News solo durante sus ventanas lead/live/tail.
5. **Envío recomendado: miércoles** — los tentpoles cierran domingo y el pool de recaps
   madura lunes-martes.

## Hallazgos importantes (correcciones de datos)

- **`calendar_events.py` tiene SIGGRAPH mal para 2026**: ventana `(8,9)-(8,13)`, pero
  SIGGRAPH 2026 real fue **19–23 de julio** en LA (s2026.siggraph.org). Con la ventana
  actual el motor se habría perdido el momento por 3 semanas. Los eventos que cambian de
  mes entre años deben anclarse con `"year"` (el módulo ya lo soporta) o cargarse del JSON.
- **Adobe MAX 2026 es 10–12 nov en Miami Beach** (max.adobe.com); muchas fuentes siguen
  reportando octubre/LA. Anotado en el JSON.
- La semana 1 del calendario (esta semana) tiene TRES just-ended reales: SDCC (26 jul),
  SIGGRAPH (23 jul) y el tail del Mundial (final 19 jul) — coincide con la edición B de
  muestra (`sim/edicion-B.json`).

## Qué necesito de Jon

1. **Confirmar el día de envío** (recomiendo miércoles) — fija el corte del pool.
2. **Green light al orden de renderers** (`render_steal` → `render_moment` →
   `render_deep_dive`) antes de que nadie escriba código.
3. **Decidir integración**: adoptar `composer.choose_format()` como cerebro único y dejar
   `build_edition.py` como capa de render (doc 02, regla F), o mantener los dos caminos.
4. **Verificar feeds de Capa 1** con `doctor.py` antes de tocar `sources.py` (yo no edité
   ningún .py, regla del BRIEF).
5. **Watch items**: encargar a quien corresponda re-verificar Cosm Detroit (fecha de
   apertura), Snap Specs y Art Basel Miami 2026 cuando se anuncien fechas oficiales —
   están marcados `status: expected/probable` en el JSON, nunca usarlos sin re-verificar.
