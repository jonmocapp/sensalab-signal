# 01 — Objetivos y north-star metric

> Metodología: `revops` (lifecycle stages, scoring, SLAs) + `marketing-plan` (north-star + leading indicators por etapa).

## 1. El problema que el newsletter resuelve (anclaje al insight)

Del SL-26: **"The pitch converts, connection is the bottleneck."** El 95% de los decision-makers
que enganchan se vuelven warm. El embudo NO se rompe en la conversión — se rompe en el REACH:
no hay suficientes personas del ICP en estado "warm" en un momento dado.

Implicación directa: el newsletter no es un canal de contenido, es una **máquina de fabricar
conexión warm a escala**. Cada decisión (métrica, formato, cadencia) se evalúa contra una sola
pregunta: *¿esto aumenta la cantidad de personas del ICP que están warm con SensaLab esta semana?*

## 2. North-star metric

**WEIR — weekly engaged ICP readers**: número de suscriptores verificados como ICP (agencia
experiencial o marca, rol decision-maker/producer) que abrieron o hicieron clic en al menos
1 de las últimas 4 ediciones.

Por qué esta y no otra:

| Candidata | Por qué NO es la north-star |
|---|---|
| Tamaño de lista | Vanidad. 1,000 suscriptores no-ICP = cero pipeline. |
| Open rate | Inflado por Apple MPP; no distingue ICP de curiosos. |
| Meetings booked | Es el resultado ($), pero es lagging y de bajo volumen — no sirve para dirigir decisiones semanales. |
| **WEIR** | Es exactamente "conexión warm a escala": ICP real × atención recurrente. Es leading respecto a conversaciones y accionable cada semana. |

**Métrica de dinero (lagging, se reporta mensual):** conversaciones iniciadas y meetings booked
atribuibles al newsletter (reply, clic en link de agenda, o mención "leo INMERSIVO" en un call).

## 3. Árbol de KPIs (qué mueve a qué)

```
Meetings booked (mensual)
└── Conversaciones iniciadas (replies, DMs, agenda-clicks)
    └── WEIR ← NORTH STAR (semanal)
        ├── Suscriptores ICP netos (crecimiento de lista calificada)
        │   ├── Invitaciones 1:1 aceptadas (outbound de los 118 leads / 78 agencias)
        │   ├── Referidos/forwards ("forward this to a producer")
        │   └── Suscripciones orgánicas (LinkedIn, web)
        └── Tasa de re-engagement (dormidos que vuelven)
```

## 4. Etapas del lifecycle (definiciones operativas)

Adaptación del framework de lifecycle de `revops` al funnel del brief
(suscriptor → warm → conversación → booked):

| Etapa | Criterio de entrada | Criterio de salida | Dueño | SLA |
|---|---|---|---|---|
| **Subscriber** | Opt-in confirmado (form, invitación aceptada) | Fit verificado contra ICP | Motor + Jon | Verificar fit en ≤7 días |
| **ICP subscriber** | Empresa = agencia experiencial o marca del perfil SL-26 Y rol = producer/CD/VP Innovation/Head of Production | ≥1 open o clic en las últimas 4 ediciones | Motor (`tracking.py`) | — |
| **Warm reader** | ≥1 interacción en últimas 4 ediciones; **warm fuerte** = ≥2 clics o 1 reply/forward | Reply, DM, o clic en link de agenda | Motor detecta, Jon actúa | Revisar lista warm cada lunes |
| **Conversation** | Reply al newsletter, DM de LinkedIn iniciado, o pregunta directa | Meeting agendado o recycled a warm | **Jon** (personal, nunca automatizado) | Responder replies en ≤24h hábiles |
| **Booked** | Meeting en calendario | Sale del scope del newsletter → pipeline de ventas SL-26 | Jon | — |

Reglas duras:
- **Un reply es oro.** Cada reply lo contesta Jon en persona, en ≤24h hábiles. Es el momento
  exacto en que "connection" deja de ser bottleneck para esa persona.
- **Nunca** pitch automatizado a un warm reader. El paso warm → conversation es 1:1 y humano;
  el newsletter solo fabrica el contexto para que ese 1:1 no sea frío.
- Un suscriptor no-ICP no cuenta para WEIR pero no se purga (puede ser influencer/referidor).

## 5. Scoring de engagement (para `tracking.py`, no editar .py — spec para integrar)

Puntos por suscriptor, ventana móvil de 4 ediciones:

| Señal | Puntos | Nota |
|---|---|---|
| Open | 1 | Poco fiable (MPP) — piso, no señal fuerte |
| Clic a la edición web | 3 | La señal de atención real del modelo email-slim → web |
| 2+ clics en una edición | +2 | Leyó a fondo |
| Reply | 10 | Dispara acción humana inmediata |
| Forward detectado / nuevo suscriptor referido | 8 | Advocacy |
| Unsub / bounce | reset | Sale del funnel |

Umbrales: **warm** ≥3 puntos · **warm fuerte** ≥8 · **dormido** = 0 puntos en 8 semanas.

## 6. Objetivos a 90 días (números)

Base real: 118 leads LA con email (98%), 78 agencias ICP scoreadas (29 Strong, 15 Good).
El techo inicial de lista calificada es ~150-300 personas — y está bien: es una lista de
francotirador, no de volumen.

| Métrica | Semana 4 | Semana 8 | Semana 12 |
|---|---|---|---|
| Suscriptores ICP | 60 | 120 | 200 |
| **WEIR (north star)** | 30 | 65 | 110 |
| Click-to-web rate por edición | ≥4% | ≥5% | ≥6% |
| Replies acumulados | 2 | 6 | 12 |
| Conversaciones iniciadas | 1 | 4 | 8 |
| Meetings booked | 0 | 1 | 3 |

Benchmark de sanidad (B2B lista curada pequeña): open 45-60%, CTR 3-6%. Si a la semana 8 el
click-to-web está <3%, el problema es contenido/asunto, no lista — activar el plan del doc 06.
