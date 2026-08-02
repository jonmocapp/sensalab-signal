# Pilares de contenido de INMERSIVO

Política editorial del cerebro "AI sin AI". Metodología: skill `content-strategy` (pilares
product-led + audience-led, searchable/shareable) y skill `content-matrix` (matriz pilar ×
formato con ideas concretas por celda).

Regla de oro heredada del BRIEF: cada pieza pasa el **test del productor** — ¿le da munición,
inspiración o tema de conversación para su próximo pitch de marca? Si no, no va.

---

## Los 5 pilares

Los pilares son los ÁNGULOS editoriales del cerebro. Cuatro ya existen como valores de
`Candidate.angle` en el contrato de datos (`bar-moved`, `steal-this`, `teardown`,
`tech-unlock`); el quinto (`framework`) hay que añadirlo al contrato.

| # | Pilar | Qué es | Por qué el ICP lo lee | Tipo (skill content-strategy) |
|---|-------|--------|----------------------|-------------------------------|
| 1 | **Bar-moved** | Alguien subió el estándar: un venue, show o activación que resetea lo que el público espera (Sphere, Cosm, un booth que rompió internet). | Munición para justificar presupuesto: "esto es lo nuevo normal, tu marca no puede verse vieja". | Shareable (observación de tendencia) |
| 2 | **Steal-this** | Ideas tácticas y robables extraídas de tentpoles y activaciones, listas para adaptar a un pitch. | Material directo de pitch. El productor lo guarda y lo reenvía. | Shareable + guardable (listicle) |
| 3 | **Teardown** | Crítica de craft de un caso fallido o polarizante: qué falló, por qué, cómo debió hacerse. | Lo hace más filoso en la sala; conversación garantizada. Es el pilar con más personalidad de marca. | Shareable (contrarian/analytical) |
| 4 | **Tech-unlock** | Un release (engine, modelo, hardware AR) traducido a "qué desbloquea para experiencias en vivo". | El productor oye del release en todas partes; nosotros lo traducimos a SU mundo. Posiciona a SensaLab como el traductor técnico. | Searchable + shareable (analytical) |
| 5 | **Framework** | Modelos mentales evergreen: cómo especificar un domo LED vs pantalla plana, cómo brifear contenido real-time, bandas de presupuesto de una capa interactiva. | Los "keepers": se guardan, se reenvían, compounding authority. Es el pilar que más asocia a SensaLab con expertise. | Searchable (use-case / explainer) — clave para el blog futuro |

Nota de posicionamiento: los pilares 1–4 son reactivos (los dispara la semana); el 5 es de
inventario (se produce con calma y se publica en semanas valle). Guardarriel intacto en los
cinco: opinión de mercado sin autobombo, cero referencias a trabajos pasados del fundador.

---

## Mapeo pilar → formato de edición → renderer

Formatos de edición según `composer.py` (A–F) y renderers construidos hoy:

| Formato (composer) | Pilar dominante | Renderer hoy | Estado |
|---|---|---|---|
| A. digest | mezcla (cards con ángulo por historia) | `render_signal.py` (The Signal) | **Construido** |
| B. moment | bar-moved (hero) + mezcla | ninguno propio → cae en Signal genérico | **Falta** (`render_moment`: monográfico 1 hero + ángulos) |
| C. teardown | teardown | `render_teardown.py` | **Construido** |
| D. deep_dive | framework | ninguno → hoy imposible renderizar bien | **Falta** (`render_deep_dive`: explainer 1 tema, facetas) |
| E. steal_this | steal-this | ninguno → caería en Signal, pierde la forma de playbook numerado | **Falta** (`render_steal`: lista numerada, cada item cierra en "propón esto") |
| F. tech_unlock | tech-unlock | Signal funciona como aproximación (hero + cards) | **Falta variante** (`render_signal` con modo hero-focus; prioridad baja) |

**Orden recomendado de construcción de renderers** (según frecuencia en el calendario de 12
semanas, doc 03): 1) `render_steal` (4 semanas lo piden), 2) `render_moment` (3 semanas),
3) `render_deep_dive` (2 semanas), 4) variante hero de Signal para tech_unlock (2 semanas,
pero Signal actual es un sustituto digno).

Mientras no existan: el formato elegido por el cerebro se degrada a Signal con el ángulo
correcto por card, y se registra `renderer_gap` en la telemetría del plan (ver doc 02, regla F).

---

## Matriz pilar × formato (skill content-matrix, adaptada)

Adaptación declarada: la matriz canónica del skill usa 8 formatos de post social; aquí las
columnas son los formatos de edición reales del motor. Cada celda = un titular concreto en
inglés (sentence case), anclado a eventos reales y verificables de la ventana jul–oct 2026.

| Pilar ↓ / Formato → | The Signal (digest) | Teardown | Steal-this playbook | Moment (monográfico) | Deep dive (framework) |
|---|---|---|---|---|---|
| **Bar-moved** | "The week the dome went mainstream" (card hero sobre Cosm Detroit) | "The activation that raised the bar — and still missed" | "5 bar-raising moves from US Open fan week you can pitch at any scale" | "Sphere's first Latino residency: what Carín León weekend means for venues" | "From flat screen to shared reality: how venues reset audience expectations" |
| **Steal-this** | Card "steal this" semanal dentro del digest | "Everyone copied this Comic-Con stunt. Here's why the copies flopped" | "What the smartest booths at Comic-Con got right" | "Gamescom 2026: the booth ideas worth flying home with" | "The anatomy of a stealable activation: a 6-part checklist" |
| **Teardown** | Card crítica corta ("quick verdict") en digest | "Why that fan-fest AR moment felt fake — a craft autopsy" | "5 activation fails of the summer and the fix for each" | "When the tentpole flops: three misses from the same week" | "The uncanny valley of brand experiences: why almost-real reads as fake" |
| **Tech-unlock** | Card "signal" sobre un release menor | "The demo was magic. The install will not be. A reality check" | "6 things you can already do with gaussian splatting at an event" | "Meta Connect 2026: the producer's cut" | "Real-time engines for producers: what Unreal and Unity actually change on site" |
| **Framework** | Card "one framework" mensual en digest | "The brief was the failure: how bad specs killed a good idea" | "10 questions to ask before you sign an LED dome" | "SIGGRAPH week: the research that will hit your budgets in 2027" | "Domes vs screens: a producer's cheat sheet" |

Celda más fuerte de la matriz: **Tech-unlock × Moment ("Meta Connect 2026: the producer's
cut")** — está anclada a una fecha confirmada (23–24 sep), toca el hueco exacto de SensaLab
(capa AR/real-time white-label) y es la edición más fácil de reenviar dentro de una agencia.

---

## Cadencia objetivo por pilar (12 semanas)

Del calendario del doc 03: steal-this 4 · moment 3 · tech-unlock 2 · framework/deep-dive 2 ·
digest 1 (colchón). El teardown NO se agenda: es oportunista (lo dispara talkability) y puede
sustituir cualquier semana valle — presupuestar 1–2 por trimestre como expectativa realista.
