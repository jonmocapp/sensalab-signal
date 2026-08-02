# 04 — ICP, construcción de lista y segmentación

Especialista 04 · INMERSIVO · basado en el BRIEF maestro + extracción completa del
`SensaLab_SL-26_Sales_Intelligence_2026.pdf` (vía pdftotext — los 118 contactos, el funnel real
y las 78 agencias scoreadas están incorporados, no resumidos de memoria).

## Skills usados (invocados con la herramienta Skill)

| Skill | Dónde se aplicó |
|---|---|
| `icp-definer` | `01-icp-refinado.md` — ICPs trigger-based con scoring 4D (pain/budget/reach/timing) y test de list-building |
| `persona-definer` | `02-personas.md` — 3 personas con JTBD, dolores personales, KPIs, canal y scoring; mapeo precio→seniority |
| `list-builder` | `04-plan-de-lista.md` — principio "lista chica targeteada > lista grande" (dato: 6–50 leads → 5.3% reply vs 1.1% en 1,000+) |
| `sales-lead-score` | `05-lead-scoring.md` — modelo 4 dimensiones con pesos por motion, decay, scoring negativo, umbrales y backtest |
| `prospecting` | `03-segmentacion.md` y `04-plan-de-lista.md` — fases 1–5, guardarraíles de compliance (lineage, no scraping, no comprar listas) |

## Qué hay en esta carpeta

| Archivo | Contenido |
|---|---|
| `01-icp-refinado.md` | Quién SÍ va en la lista: ICP 1 agencia experiencial sin 3D in-house (18/20), ICP 2 brand-side (15/20), ICP 3 independientes; exclusiones duras (la plantilla es el "screened out 21" del SL-26) |
| `02-personas.md` | 3 personas: "producer under the gun" (18/20), "boutique founder" (17/20), "brand creative director" (14/20) — con qué formato mueve a cada una |
| `03-segmentacion.md` | 3 ejes (tipo × calor × familia de rol), 6 segmentos accionables, mapeo formato↔segmento, lifecycle tiers, atributos Brevo |
| `04-plan-de-lista.md` | Opt-in limpio en 3 waves + 5 motores de crecimiento + copy en inglés listo para pegar + meta honesta: ~45–75 suscriptores ICP-puros en 90 días |
| `05-lead-scoring.md` | Modelo 0–100: fit 50 (rol 25 + empresa 25) + engagement 35 + timing 15; umbrales nurture/warm-watch/sales-ready/hot-lane; backtest contra el pipeline real |
| `data/seed-118.csv` | Los 118 contactos del SL-26 con wave, segmento, calor, familia de rol, fit tier y notas — la hoja de trabajo de las waves 1–2 |
| `data/icp-agencies-wave3.csv` | Las 44 agencias Strong+Good (29+15) con ubicación, web, LinkedIn y el ángulo del SL-26 — la hoja de trabajo de la wave 3 |

## Decisiones clave

1. **Una lista, dos ICPs, un envío.** No dos newsletters: la segmentación ordena invitación,
   subject lines y lectura de ventas, no fragmenta el contenido. Los dos formatos del motor ya
   mapean: Teardown → producers/makers, Signal → brand-side/dreamers.
2. **Los 118 NO se importan como suscritos.** Son prospects con lineage legítimo; se les invita
   1:1 (wave 1: los 21 warm+; wave 2: los 90 cold, donde el newsletter es el regalo del touch 1
   que el propio SL-26 pide — "sequence before you dial"). Solo entra a Brevo quien dice sí.
3. **Meta chica a propósito:** 45–75 suscriptores ICP-puros en 90 días. Con el 95% de conversión
   on-reach documentada, 50–70 decision-makers leyéndote cada semana es pipeline, no vanidad.
4. **El clic es el nuevo "reached".** El cuello de botella del SL-26 era reach (29% al teléfono).
   Cada click en una edición es una mano levantada gratis: el scoring lo convierte en un
   seguimiento personal que referencia el contenido leído — nunca más un email frío.
5. **Opens = señal débil** (Apple MPP los infla): el modelo pesa clicks y replies. Y NO se
   penaliza el gmail personal — este mercado lo usa a nivel decision-maker (el SL-26 lo prueba).
6. **Lead magnet sin quemar el asset:** el book de 100 ideas ya demostró jalar replies; se gatea
   un sampler ("10 interactive ideas"), el book completo sigue siendo colateral de ventas 1:1.
7. **Guardarriel respetado:** ningún copy menciona trabajo pasado, clientes pasados ni Cinética;
   cero datos inventados — todos los números citados salen del SL-26 o del dato lemlist del skill.

## Qué necesito de Jon

1. **Corregir los 6 bad data** (están marcados FIX en `seed-118.csv`); 2 son solo teléfono roto y
   ya se pueden invitar por email (P+P, Persona Comms).
2. **Confirmar el subdominio de envío** (`news.sensalab.io` recomendado) y autenticar
   SPF/DKIM/DMARC en Brevo antes del primer send (necesita las keys pendientes del BRIEF).
3. **Decidir el gate del lead magnet:** ¿sampler de 10 ideas del book existente, o piezas nuevas?
   (Yo recomiendo sampler: cero producción nueva.)
4. **20 minutos los lunes** para el ritual de scoring (export de Brevo → hoja → trabajar banda 80+).
5. **Aprobar el copy en inglés** de las 3 invitaciones (`04-plan-de-lista.md`) — 1 línea de
   personalización por contacto en wave 1 la pone él, que conoce los hilos.
