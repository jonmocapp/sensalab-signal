# 03 — Subject lines, preheaders & copy optimization

Especialista 03. Misión: maximizar open rate y engagement con copy en la voz SensaLab
(punchy, contrarian, "why it matters"), en inglés, sentence case.

## Qué entregué

| Archivo | Contenido |
|---------|-----------|
| `subjects-preheaders.md` | Banco de **25 subjects para The Signal** + **25 para Teardown** (cada uno con chars, ángulo psicológico y rationale), **25 preheaders** emparejados que complementan sin repetir, **5 pares A/B** (una sola variable por test, con hipótesis y qué hacer con el ganador), bloque plano copy-paste, y pairing recomendado para las dos ediciones sim. |
| `hook-formulas.md` | El patrón casa ("two-beat statement") + **10 fórmulas reutilizables** de opening/hook con plantilla, ejemplos vivos de las ediciones, y tabla de qué fórmula va en qué slot (hero Signal, hero Teardown, Field Notes, In the Lab, Craft, why, video). |
| `refined-editions.md` | Auditoría slot por slot de `sim/edicion-A.json` y `sim/edicion-B.json` (qué falla y por qué, qué NO se toca) + valores refinados **JSON-ready** de statements y "why it matters", cada fix con su verificación de veracidad contra las fuentes de la propia edición. |
| `voice-guide.md` | Guía do/don't lista para pegar en el prompt del escritor del motor + checklist pre-envío de 8 puntos + notas de integración. |

## Decisiones clave

1. **Contrato del motor respetado**: subject ≤ 60 chars y preheader ≤ 90 chars (límites
   que ya viven en `writer.py`). Los 50 subjects y 25 preheaders están validados por
   script: cero em dashes, cero exclamaciones, todo sentence case, todo dentro de límite.
2. **Cero cifras inventadas**: todos los números en subjects/preheaders (2 million, 400
   drones, 12 minutes, 87-foot, 40 matches, 12K, 3v3) salen de las ediciones sourceadas.
   Guardarriel intacto: ningún texto alude al pasado del fundador ni a Cinética.
3. **Refinado quirúrgico, no reescritura**: en las ediciones solo se tocó lo que fallaba
   (statements que duplicaban su headline, whys que copiaban el body verbatim, un em dash,
   jerga de categoría). Las 6 mejores líneas quedan intactas y ahora son el
   "calibration set" del prompt del escritor.
4. **A/B con disciplina de una variable**: cada par testea un solo eje (insight vs.
   utility, largo vs. corto, anticipación vs. hecho consumado, caso nombrado vs. curiosity
   gap, aforismo vs. consecuencia). Métrica primaria open rate 24h, guardrail click rate.
5. **El banco es también few-shot**: los subjects sirven de ejemplos rotables dentro del
   prompt del motor; anclan el tono mejor que cualquier lista de adjetivos.

## Skills usados (invocados con la herramienta Skill)

- **`copywriting`** — principios base: claridad sobre cleverness, especificidad sobre
  vaguedad, beneficio para el lector, sentence case, prohibición de buzzwords; estructura
  de subject/preheader como headline/subheadline.
- **`ad-creative`** — metodología de generación por ángulos (contrarian, utility,
  curiosity, identity, loss, specificity), validación contra límites de caracteres antes
  de entregar, variación real de ángulo (no solo sinónimos), y grounding: cada línea
  trazable a material fuente real, cero claims inventados.
- **`hook-generator`** — la estructura de dos líneas (opening + contrast, tensión y
  curiosity gap) se adoptó como el patrón casa "two-beat statement"; sus 6 ángulos
  (number-led, contrarian, authority steal, future shock…) están mapeados en el banco.
- **`copywriting-refiner`** — disciplina de auditoría: citar exactamente qué falla y por
  qué, arreglar SOLO lo que falla, reglas de subject (sentence case, sin clickbait, sin
  em dashes, curiosidad o dolor en vez de describir el contenido).

## Qué necesito de Jon

1. **Decisión de idioma en el motor**: `writer.py` (línea ~81) aún pide el subject
   "en espanol"; el brief fija inglés. Hay que actualizar esa instrucción al integrar
   (yo no toco .py). El bloque de `voice-guide.md` ya asume inglés.
2. **Aplicar los refinados**: los valores JSON-ready de `refined-editions.md` se pegan en
   `sim/edicion-A.json` / `sim/edicion-B.json` cuando Jon dé el visto bueno (elegir entre
   primary y alt en los dos slots que ofrecen alternativa).
3. **Confirmar el primer A/B**: recomiendo arrancar con el par 1 (S1 vs S2) en la primera
   edición Signal real; Brevo free permite el split manual (dos campañas 50/50) si el
   plan no incluye A/B nativo.
4. **Open rate baseline**: cuando existan 2-3 envíos reales, pasarme opens/clicks por
   subject para rebalancear el banco hacia la familia de ángulos ganadora (el banco está
   etiquetado por ángulo justamente para eso).
