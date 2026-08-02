# 06 — Riesgos y mitigaciones

> Metodología: `marketing-plan` (operational honesty: nombrar lo incómodo) + `emails`
> (deliverability) + `revops` (higiene de datos y funnel).

| # | Riesgo | Prob. | Impacto | Mitigación | Señal de alerta |
|---|---|---|---|---|---|
| 1 | **Deliverability**: dominio nuevo sin reputación → spam folder, todo lo demás es irrelevante | Alta | Crítico | SPF/DKIM/DMARC antes del envío #1; subdominio news.sensalab.io; warm-up con lista semilla engaged; email-slim (poco HTML, un link); list-unsubscribe header; nunca comprar listas | Open <25% en Gmail en las primeras 3 ediciones; bounces >2% |
| 2 | **Violación del guardarriel legal** (alusión a trabajo pasado/Cinética) en un descuido de copy | Media | Crítico (legal) | Checklist pre-envío fijo (doc 02 §5); la autoridad se construye con análisis, no portafolio (Teardown como sustituto del case study); revisar también los P.S. y welcome emails, no solo el cuerpo | Cualquier "we built/our clients/we've done" en un borrador |
| 3 | **Lista pequeña desanima** ("solo 80 suscriptores") y se abandona la cadencia | Media | Alto | Encuadre correcto desde el día 1: el techo inicial es ~200-300 ICP y ESO es el diseño (francotirador, no volumen). La north-star es WEIR y conversaciones, no tamaño. 80 ICP warm > 5,000 genéricos | Comparar la lista con benchmarks de newsletters de consumo |
| 4 | **Treadmill de contenido**: la edición semanal depende de una persona con más proyectos | Media | Alto | El motor ya existe para esto ("AI sin AI"): el cerebro elige y arma; regla de "se envía igual con menos items" (doc 03 §1); banco de 2-3 historias evergreen (deep dives) como reserva para semanas flojas | Dos martes seguidos en riesgo de no salir |
| 5 | **Opens no confiables** (Apple MPP infla aperturas) → decisiones sobre data falsa | Alta | Medio | El modelo email-slim → web ya lo resuelve: la métrica que manda es el clic a nuestra web (first-party, `tracking.py`); WEIR pondera clics/replies sobre opens (doc 01 §5) | Open rate >75% sostenido (sospechoso) con clics planos |
| 6 | **Sin hosting web al lanzar** → el email-slim no tiene destino y el modelo se cae | Media | Alto | Es EL bloqueo de la semana 1 (doc 05); plan B: publicar la edición como página estática en cualquier hosting gratuito (Netlify/GitHub Pages) con el dominio después — no retrasar el lanzamiento por el sitio "bonito" | Semana 2 sin URL pública de las ediciones A/B |
| 7 | **Invitados fríos marcan spam** (los 118 leads no pidieron el email) | Media | Alto | Invitación personal 1:1 (no blast), opt-in real para entrar a la lista, tono "thought this might be useful" con link a edición publicada — el newsletter se muestra, no se impone | Complaint rate >0.1% en Brevo |
| 8 | **Teardown mal calibrado**: crítica que se lee como ataque a una agencia/marca del propio ICP | Baja | Alto | Lente de craft, no de personas: se critica la ejecución técnica y decisiones de diseño, nunca al equipo; jamás nombrar a la agencia productora del ICP como culpable; equilibrar cada "qué falló" con "cómo se haría bien" | Un Teardown cuyo objeto es una de las 78 agencias del pipeline |
| 9 | **Dependencia de un solo canal** (email) | Media | Medio | Mirror semanal en LinkedIn (insight líder + link) desde la semana 3 — mismo contenido, cero costo marginal; los replies/DMs de LinkedIn cuentan como conversaciones en el funnel | Crecimiento de lista 100% dependiente de invitaciones |
| 10 | **Brevo free limits / lock-in del ESP** | Baja | Medio | Límite free (300/día) alcanza para lista <300 con envío escalonado; el redirect first-party (go.sensalab.io) planeado en `tracking.py` independiza la data de clicks del ESP; export mensual de subscribers | Lista >250 o necesidad de enviar en <1 hora |
| 11 | **Conversión warm→conversación no ocurre** (leen pero nadie contesta) | Media | Alto | No es fallo del contenido sino del puente: subir dosis de reply prompts genuinos, y follow-up 1:1 proactivo de Jon a warm fuertes (el newsletter fabrica el contexto, el 1:1 cierra la conexión — doc 01 §4) | Semana 8 con WEIR en meta pero 0 conversaciones |

## Los tres que pueden matar el proyecto (vigilancia semanal)

1. **#1 deliverability** — sin inbox no hay nada. Se resuelve una vez, bien, en semana 1.
2. **#2 guardarriel legal** — un solo desliz tiene costo legal. Checklist en cada envío, sin excepciones.
3. **#4 cadencia** — el activo es el hábito del lector; se destruye en 2-3 semanas de silencio.
