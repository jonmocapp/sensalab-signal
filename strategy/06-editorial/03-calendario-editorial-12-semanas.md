# Calendario editorial — 12 semanas (27 jul → 18 oct 2026)

Anclado a tentpoles REALES verificados con web search el 27-jul-2026 (fuentes en
`tentpole-calendar.json`). Formatos = ids de `composer.py`. Los subjects de ejemplo van en
inglés y sentence case (regla de marca). Recomendación de envío: **miércoles** — la mayoría
de los tentpoles cierran domingo, y el miércoles el cerebro ya tiene el pool del lunes-martes
con las mejores piezas de recap.

Regla transversal: el teardown NO se agenda — si en cualquier semana aparece un caso con
talkability fuerte (doc 02, regla A), desplaza al formato sugerido de esa semana. Las semanas
marcadas "teardown-friendly" son donde históricamente más aparecen casos (post-tentpole).

| Sem | Fechas 2026 | Momento (fase) | Formato sugerido | Pilar / ángulo | Qué le importa al productor | Subject de ejemplo |
|-----|------------|----------------|------------------|----------------|------------------------------|--------------------|
| 1 | jul 27 – ago 2 | SDCC terminó jul 26 (just-ended, fresquísimo); SIGGRAPH LA terminó jul 23; tail del Mundial (final jul 19) sigue vivo | **steal_this** (post-SDCC) | steal-this: activaciones del Gaslamp robables a cualquier escala | Material de pitch para briefs de entertainment/IP de Q4, que se están escribiendo YA | "What the smartest booths at Comic-Con got right" |
| 2 | ago 3 – 9 | Tail SIGGRAPH (papers/demos siguen rebotando); tail Mundial. Teardown-friendly (las críticas post-tentpole salen esta semana) | **tech_unlock** (cosecha SIGGRAPH) | tech-unlock: real-time, splatting, lo que baja de la academia al show floor | Qué pedirle a su partner técnico en los próximos 12 meses; sonar informado en la sala | "SIGGRAPH's quiet gift to live events" |
| 3 | ago 10 – 16 | Valle. Última semana útil del tail del Mundial (30 días → ~ago 18) | **deep_dive** (framework) | framework: domos y shared reality, percha = Cosm Detroit abre en otoño | Un keeper: cómo especificar domo vs pantalla; se guarda y se reenvía | "Domes vs screens: a producer's cheat sheet" |
| 4 | ago 17 – 23 | US Open Fan Week arranca ago 23 (upcoming/live); gamescom ONL ago 25 (upcoming) | **digest** (con ángulo preview) | mezcla; card hero = radar de las 6 semanas más densas del año | Agenda: qué mirar entre fin de agosto y octubre para no llegar tarde a ninguna conversación | "Six loud weeks are coming — here's your radar" |
| 5 | ago 24 – 30 | gamescom LIVE (ONL ago 25; feria ago 26–30); US Open Fan Week (ago 23–29, gratis); Burning Man arranca ago 30 | **moment** (gamescom) | bar-moved + tech-unlock: booths, engines, anuncios de Unreal/Unity | El booth como brand experience: qué está haciendo el gaming que el retail copiará en 6 meses | "Gamescom just showed where booths are going" |
| 6 | ago 31 – sep 6 | US Open main draw; Burning Man (hasta sep 6/7); Venice Immersive abre sep 2 (10º aniversario, 68 proyectos XR); HHN Hollywood abre sep 3 | **steal_this** (post-gamescom + fan week) | steal-this: fan zones, colas convertidas en experiencia, booth craft | Playbook de fan experience aplicable a activaciones de sponsor; HHN = benchmark LA de scenic+media | "The fan-zone playbook from a very loud week" |
| 7 | sep 7 – 13 | NFL kickoff sep 9 (miércoles: primero en 75 años); NYFW sep 10–15; Sphere: Carín León sep 11–13 (primer residente latino, fin de semana patrio mexicano); probable evento de Apple (sin anunciar) | **moment** (NYFW + semana bar-moved) | bar-moved: lo que las marcas hicieron en NY y Vegas esa semana | Munición "esto es lo nuevo normal" para justificar presupuesto; multicultural marketing con craft | "Fashion week moved the bar again" |
| 8 | sep 14 – 20 | Dreamforce sep 15–17 (Moscone); NYFW cierra sep 15; Venice Immersive cerró sep 12 (just-ended). Teardown-friendly (autopsias post-NYFW) | **steal_this** (Venice Immersive) | steal-this + tech-unlock: XR narrativo curado, listo para traducir a activación | 68 proyectos XR de 26 países ya filtrados por la Biennale: inspiración de nivel premio para pitches | "Venice just curated the best of XR for you" |
| 9 | sep 21 – 27 | Meta Connect sep 23–24 (gafas nuevas teaseadas + Quest + AI) | **tech_unlock** (Connect) | tech-unlock: hardware AR traducido a activaciones | Qué significa el nuevo hardware para briefs 2027; qué proponer el lunes siguiente | "Meta's new glasses, translated for producers" |
| 10 | sep 28 – oct 4 | Valle relativo; tail de Connect; watch: apertura de Cosm Detroit (otoño, fecha por anunciar) | **deep_dive** (framework) | framework: brifear contenido real-time / la capa interactiva white-label como línea de presupuesto | Cómo escribir el brief técnico sin tener al técnico en nómina — el hueco exacto del ICP | "How to brief real-time content (without a CTO)" |
| 11 | oct 5 – 11 | Advertising Week NY oct 5–8 (Penn District) + NYCC oct 8–11 (Javits, 20º aniversario) — industria y fandom en la misma ciudad | **moment** ("NY week") | bar-moved + steal-this: el estado del experiential dicho por la industria + activaciones NYCC en vivo | Citas frescas de AWNY para decks; qué activaron los studios en NYCC | "New York owned experiential this week" |
| 12 | oct 12 – 18 | NYCC y AWNY just-ended; preview F1 Austin (oct 23–25); HHN rumbo a Halloween (hasta nov 1) | **steal_this** (post-NYCC) + card preview F1 | steal-this: activaciones del 20º aniversario de NYCC; Halloween como percha retail | Ideas para los huecos de presupuesto de fin de año (Q4 use-it-or-lose-it) + radar F1/Vegas | "NYCC's 20th: the activations worth copying" |

## Notas de diseño del calendario

- **Distribución resultante**: steal_this 4 · moment 3 · tech_unlock 2 · deep_dive 2 ·
  digest 1 · teardown 0 agendados (oportunista, 1–2 esperables en semanas 2 y 8).
  Coincide con la cadencia objetivo del doc 01 y con las prioridades del meta-selector
  de composer.py (steal > moment > teardown > tech > deep_dive > digest).
- **Las semanas 3 y 10 son de inventario**: los deep dives se pueden escribir con
  anticipación (evergreen) y guardarse; si la semana valle resulta no ser valle, el
  deep dive espera sin caducar. Es el colchón anti-"semana floja".
- **La semana 7 es la más disputada** (NFL + NYFW + Sphere + posible Apple): el cerebro
  decidirá por dominancia de cluster; el calendario solo predice el empate más probable.
  Si Apple anuncia hardware relevante para AR/spatial, tech_unlock desplaza a moment.
- **Ecos de un mismo tentpole**: gamescom aparece en sem 5 (moment, live) y 6
  (steal_this, just-ended) con pilares distintos — es deliberado: cobertura live = qué
  pasó; recap = qué te robas. El anti-repetición por topic de composer exime a C y E,
  y las dos ediciones usan ángulos distintos.
- **Después de la semana 12** (para continuidad): F1 Austin oct 23–25 → steal_this sem 13;
  Adobe MAX nov 10–12 (Miami Beach — OJO: muchas fuentes viejas dicen octubre/LA, el sitio
  oficial dice Miami) → tech_unlock; Art Basel Miami (dic, verificar fechas exactas) →
  moment con geo Miami.
