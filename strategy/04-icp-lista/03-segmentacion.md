# Modelo de segmentación — una lista, tres ejes, ángulos distintos

Metodología: skills `icp-definer` + `prospecting` (fase 4: score & prioritize) aplicados a la
estructura real del pipeline SL-26. Implementable 100% en Brevo free (atributos de contacto +
segmentos dinámicos).

## Los tres ejes

### Eje 1 — Tipo (¿quién es?)
| Código | Segmento | En el seed SL-26 |
|---|---|---|
| AG | Agencia experiencial / production shop | 81 contactos |
| BR | Marca (in-house creative/production) | 34 contactos |
| IN | Independiente / consultor | 3 contactos |

### Eje 2 — Calor de relación (¿qué tan cerca está?)
Derivado directo del pipeline stage del SL-26 al arrancar; después lo actualiza el engagement.

| Código | Definición | Stages SL-26 | Personas |
|---|---|---|---|
| HOT | Conversación viva o NDA | Hot, Replied | 4 |
| WARM | Contacto humano logrado, interés declarado | Warm, Referral, Nurture | 17 |
| COLD | Conocido pero sin conversación (email enviado o solo dato) | Attempted, Email-only | 90 |
| FIX | Dato roto — arreglar antes de tocar | Bad data | 6 |
| EXCL | Declinó — fuera de invitaciones | Declined | 1 |

### Eje 3 — Familia de rol (¿qué le importa?)
| Código | Familia | Títulos típicos | Lente |
|---|---|---|---|
| MAKER | Producción | EP, senior creative producer, head of production, experiential director | Craft, costos, plazos |
| DREAMER | Creativo/marca | CD, ECD, CCO, VP brand creative, art director | Idea, cultura, novedad |
| CONNECTOR | Negocio | BD, account director, VP innovation, founder-as-seller | Pipeline, diferenciación, modelo |

## Los segmentos accionables (cruce de ejes)

| Segmento | Quiénes | Formato/ángulo que recibe | Movimiento esperado |
|---|---|---|---|
| **AG-HOT/WARM** (21 − brands/indep = 14) | Producers y founders ya warm | Invitación personal 1:1; teardown-first; respuestas van directo a ventas | Suscriben esta semana; primeros reply del newsletter |
| **AG-COLD** (62) | Agencias contactadas sin conversación | Invitación value-first dentro de la secuencia email+LinkedIn que el SL-26 ya recomienda ("sequence before you dial") | El newsletter ES el touch 1 de valor; warm antes del dial |
| **BR-HOT/WARM** (6) | Brand-side con hilo vivo | Invitación personal; ángulo Signal ("ammunition for your next brief") | Suscriben; nurture largo |
| **BR-COLD** (27) | Brand-side sin conversación | Invitación suave, énfasis en inspiración/tendencia, cero pitch | Opt-in lento pero de alto valor |
| **IN** (2 activos) | Freelance/consultores | Misma edición, sin prioridad de ventas | Reenvíos y referrals |
| **ICP-78** (wave 3) | Las 78 agencias scoreadas (29 Strong, 15 Good primero) | Prospecting LinkedIn → persona correcta → invitación con lead magnet | 15–25 suscriptores nuevos en 60 días |

Nota: el motor manda UNA edición para todos (v1). La segmentación NO fragmenta el contenido:
ordena (a) el tono de la invitación, (b) qué subject line se prueba con quién, y (c) cómo lee
ventas el engagement. Cuando la lista pase de ~150, evaluar sends por segmento en Brevo.

## Mapeo formato ↔ segmento (para el A/B de subject lines)

El motor elige formato por talkability; el ángulo del subject se adapta al segmento dominante:

| Edición | Ángulo para AG (makers) | Ángulo para BR (dreamers) |
|---|---|---|
| The Signal | "Three signals your next client will ask about" | "What audiences are actually responding to" |
| Teardown | "How that [X] activation was actually built" | "Steal this idea for your next launch" |

(Subject lines en inglés, sentence case, sin mayúsculas completas — regla de marca.)

## Lifecycle post-lanzamiento (se recalcula cada 4 ediciones)

| Tier | Regla | Acción |
|---|---|---|
| Engaged | Click en ≥1 de las últimas 4 ediciones, o reply | Alimenta lead scoring; ventas revisa semanal |
| Passive | Abre pero no clickea (ojo: opens inflados por Apple MPP — señal débil) | Nada; contenido sigue |
| Dormant | 0 opens/clicks en 8 ediciones | Email de re-engagement 1:1; si nada en 2 más, sunset (limpia deliverability) |

## Implementación en Brevo (atributos de contacto)

Crear estos atributos al importar los opt-ins:
- `TYPE` (AG / BR / IN)
- `WARMTH` (HOT / WARM / COLD) — seed del SL-26, se actualiza manual/mensual
- `ROLE_FAM` (MAKER / DREAMER / CONNECTOR)
- `FIT_TIER` (A / B / C) — ver `05-lead-scoring.md`
- `SOURCE` (sl26-invite / linkedin / event / website / referral / leadmagnet)
- `COMPANY`

Con eso, los segmentos dinámicos de Brevo (`TYPE = AG AND FIT_TIER = A AND clicked last campaign`)
dan la lista de seguimiento de ventas sin ninguna herramienta extra.
