# 04 — Segmentación macro: agencia productora vs marca creativa

> Metodología: `product-marketing` (personas B2B, jobs-to-be-done por rol) + `revops`
> (fit scoring). Principio rector: **una sola edición, acentos segmentados** — con una lista
> <500 y un equipo de una persona, bifurcar contenido es prematuro y caro.

## 1. Los dos segmentos (del ICP SL-26)

| | **Agencia experiencial** (segmento primario) | **Marca creativa** (segmento secundario) |
|---|---|---|
| Quién | Exec/Senior Creative Producer, Creative Director, Head of Creative Production (las 78 agencias scoreadas; 29 Strong, 15 Good) | VP Innovation, brand experience leads (Sony, Apple, Amazon, HBO, Netflix, lululemon, SKIMS, Fender, Microsoft, SEPHORA…) |
| Su job-to-be-done | **Ganar el pitch** y entregar sin reventar el presupuesto ni el cronograma | **Vender la idea adentro** y justificar la inversión (ROI, contenido, earned media) |
| Su miedo | Prometer un espectáculo que no puede construir; que el partner técnico lo deje mal frente al cliente | Firmar algo que se vea barato o que nadie recuerde; gastar sin métricas |
| Qué es SensaLab para él | La capa white-label que mete BAJO SU MARCA en la activación | El estándar de craft para exigirle más a sus agencias |
| Lectura que necesita | Feasibility + craft: "¿cómo se hizo?, ¿qué costaría?, ¿qué me puedo robar para mi próximo brief?" | Impacto + tendencia: "¿por qué funcionó?, ¿qué esperó el público?, ¿cómo se convirtió en content engine?" |
| Conversión esperada | Reply → coffee → RFP/brief con SensaLab como capa técnica | Reply → intro → SensaLab recomendado/exigido en el brief a sus agencias |

**Prioridad: agencia 70 / marca 30.** La agencia es el comprador directo del hueco white-label
y donde el pipeline SL-26 ya tiene densidad (81 agencias LA). La marca es amplificador: crea
demanda pull ("pídanle esto a su agencia") y eleva el estatus del newsletter.

## 2. Qué cambia por segmento (y qué NO)

**No cambia:** la edición semanal (una sola), los formatos, la cadencia, la voz, la web.

**Cambia (v1, barato de operar):**

| Palanca | Agencia | Marca |
|---|---|---|
| Etiqueta en `subscribers.json` | `segment: agency` (capturada en welcome email 3) | `segment: brand` |
| P.S. del email-slim | Ángulo pitch/producción: "steal this for your next pitch" | Ángulo estándar/encargo: "worth showing your agency" |
| CTA de negocio (1 de cada 4) | "Scoping an activation that needs a real-time layer? hit reply" | "Want a second pair of eyes on an immersive brief? hit reply" |
| Follow-up 1:1 de Jon a warm fuertes | Habla de feasibility, white-label, integración con su producción | Habla de estándar de craft, qué exigir, referencias de mercado |
| "Why it matters" (cuando el motor lo permita) | Cierra con implicación de producción | Cierra con implicación de marca/presupuesto |

**Regla dura para ambos:** el guardarriel legal no cambia por segmento. A la marca NUNCA se le
insinúa cartera previa; a la agencia NUNCA se le nombran otras agencias como clientes.

## 3. Dentro de "agencia": sub-priorización operativa (no editorial)

Para el orden de invitaciones y follow-ups 1:1 (no cambia el contenido):

1. **Strong fit (29)** — dedicadas a experiencial, sin 3D real-time in-house, immersive-minded,
   presupuestos de gran marca, cómodas con white-label → invitación personal de Jon, primera ola.
2. **Good fit (15)** — segunda ola, semana 3-4.
3. Resto de las 78 + los 118 leads con email → olas siguientes según capacidad de follow-up.

Un reply de un Strong fit vale más que 10 suscriptores nuevos: el lunes, la revisión de warm
readers (doc 01 §4) se ordena por fit score.

## 4. Cuándo bifurcar de verdad (criterio de salida de v1)

Bifurcar contenido (dos versiones del email, o secciones condicionales) SOLO cuando se cumplan
las tres: (a) lista >500 ICP, (b) ≥60% de suscriptores con segmento capturado, (c) evidencia
en `tracking.py` de que los clics de agencia y marca divergen por tipo de historia. Antes de
eso, la segmentación vive en los acentos de arriba y en el 1:1 de Jon.
