# Especialista 01 — Estrategia & posicionamiento

Estrategia maestra de INMERSIVO como sistema de demand-gen B2B, anclada al insight del SL-26:
**"the pitch converts, connection is the bottleneck"** — el newsletter existe para fabricar
conexión warm a escala con el ICP real.

## Qué se entregó

| Doc | Contenido |
|---|---|
| [01-objetivos-north-star.md](01-objetivos-north-star.md) | North-star **WEIR** (weekly engaged ICP readers), árbol de KPIs, lifecycle operativo suscriptor → warm → conversación → booked con criterios/SLAs, spec de engagement scoring para `tracking.py`, metas numéricas a 90 días |
| [02-posicionamiento-narrativa.md](02-posicionamiento-narrativa.md) | Posicionamiento en una frase, la cadena de asociación (utilidad → lente → identidad → disponibilidad mental), message house con 4 pilares, voz, guardarriel legal operativo, escalera de CTAs que mueve al lector por el funnel |
| [03-cadencia-y-relacion.md](03-cadencia-y-relacion.md) | Cadencia (martes 8:30am PT, sagrada), rol de The Signal (hábito) vs Teardown (autoridad), **welcome sequence de 3 emails con copy en inglés listo para pegar**, re-engagement de 3 emails, higiene de deliverability |
| [04-segmentacion.md](04-segmentacion.md) | Agencia (70) vs marca (30): jobs, miedos, qué cambia por segmento (P.S., CTA, follow-up 1:1) y qué no (una sola edición); sub-priorización Strong → Good fit; criterio para bifurcar contenido (no antes de 500 ICP) |
| [05-plan-90-dias.md](05-plan-90-dias.md) | Plan semana a semana en 4 fases (Unblock → Foundation → Velocity → Compound), con criterios de éxito por semana y metas: S4 = 60 ICP/WEIR 30 · S8 = 120/65 + 1 booked · S12 = 200/110 + 3 booked |
| [06-riesgos.md](06-riesgos.md) | 11 riesgos con probabilidad/impacto/mitigación/señal de alerta; los 3 letales: deliverability, guardarriel legal, cadencia |

## Decisiones clave (y por qué)

1. **North-star = WEIR, no tamaño de lista ni meetings.** Es la traducción medible de
   "connection a escala": ICP real × atención recurrente. Leading, semanal, accionable.
2. **La autoridad se construye con análisis, no con portafolio.** El Teardown es el sustituto
   estructural del case study — resuelve el guardarriel legal sin sacrificar credibilidad.
3. **El reply es el evento de conversión #1** y siempre lo contesta Jon en persona (≤24h).
   El newsletter fabrica contexto; el paso warm → conversación es humano, nunca automatizado.
4. **Venta dura prohibida; CTA de negocio solo como P.S. suave, máx 1 de cada 4 ediciones.**
   La promesa "briefing, no funnel" ES el posicionamiento (y se declara en el welcome email).
5. **Una sola edición con acentos por segmento** (agencia/marca capturado en la welcome).
   Bifurcar contenido solo con >500 ICP + evidencia de divergencia en clics.
6. **Lista de francotirador, no de volumen**: el techo inicial (~200-300 ICP de los 118 leads +
   78 agencias) es el diseño, no una debilidad. Invitaciones 1:1 opt-in, nunca blast.
7. **La cadencia es sagrada**: se recorta alcance de la edición, nunca la fecha.

## Skills usados

- **`emails`** — welcome/re-engagement sequences (estructura, timing, subject lines, "one email
  one job"), copy guidelines del email-slim, higiene de deliverability (doc 03).
- **`product-marketing`** — posicionamiento, personas B2B, switching dynamics (push/pull/
  habit/anxiety), customer language, message house (docs 02 y 04).
- **`marketing-plan`** — estructura del plan 90 días (Unblock/Foundation/Velocity/Compound),
  north-star + leading indicators, honestidad operativa en riesgos (docs 01, 05, 06).
- **`revops`** — lifecycle stages con entry/exit/owner/SLA, modelo de engagement scoring,
  SLA de respuesta a replies, higiene de lista (docs 01 y 03).

## Qué necesito de Jon

1. **Keys**: BREVO_API_KEY (bloquea semana 1) y acceso DNS de sensalab.io para SPF/DKIM/DMARC.
2. **Decisión de hosting** de la edición web (estático; sin URL pública el modelo email-slim → web
   se cae). Plan B en doc 06 #6.
3. **Confirmar el compromiso operativo mínimo**: lunes 30 min (revisión warm + follow-ups) +
   responder replies en ≤24h. El plan entero asume esto.
4. **La lista SL-26** (118 leads / 78 agencias con fit score) en formato importable, para
   ordenar las olas de invitación 1:1 de las semanas 3-5.
5. **Validar la meta de S12** (200 ICP, 3 meetings booked) contra su lectura del pipeline real.

## Guardarrieles respetados

Sin mención ni alusión a trabajo pasado del fundador, clientes pasados ni Cinética; cero datos
inventados (todas las cifras vienen del BRIEF/SL-26 o son metas marcadas como tales); sentence
case en todo el copy en inglés; ICP literal del SL-26. No se tocó ningún .py del motor — la
spec de scoring (doc 01 §5) es para que quien integre la aplique en `tracking.py`.
