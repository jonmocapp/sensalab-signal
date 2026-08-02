# 03 — Cadencia y estructura de la relación

> Metodología: `emails` (welcome/nurture/re-engagement sequences, timing, subject lines,
> one email one job) adaptada a un newsletter B2B de lista pequeña y curada.

## 1. Cadencia core

- **Semanal, sin excepción.** La fiabilidad es parte del producto: un briefing que a veces
  llega no fabrica hábito ni disponibilidad mental.
- **Día/hora: martes 8:30am PT.** Público LA/US, B2B — martes evita el lunes de inbox lleno
  y deja la semana para que el contenido circule en pitches. Miércoles es el backup si un
  momento editorial (tentpole) lo justifica. Nunca viernes/fin de semana.
- **Regla de calidad sobre calendario**: si una semana el pool de historias es débil, el
  cerebro cae a formato Signal con menos items — pero SE ENVÍA. Saltarse semanas mata el hábito.
- Volumen total por suscriptor: 1 edición/semana + secuencias (welcome o re-engagement).
  Nunca dos emails el mismo día; la welcome pausa hasta el día siguiente si choca con la edición.

## 2. Cómo encajan The Signal y Teardown (los dos formatos del motor)

| | The Signal | Teardown |
|---|---|---|
| **Qué es** | Tarjetas de insight + "Why it matters" | Un caso destripado con lente de craft |
| **Trabajo en el funnel** | Fabrica **hábito y breadth**: suscriptor → warm (clics recurrentes) | Fabrica **autoridad y profundidad**: warm → conversación (replies, forwards) |
| **Frecuencia esperada** | Default (~3 de cada 4 semanas) | Cuando `talkability` lo dispara (~1 de cada 3-4 semanas) |
| **CTA típico** | "Read the full signal →" (clic a web) | Prompt de reply ("what would you have done?") |
| **Riesgo si se abusa** | Se vuelve digest genérico y olvidable | Se vuelve cínico/negativo; fatiga la crítica |

El selector por talkability de `build_edition.py` ya implementa este balance — la estrategia
lo ratifica: **no forzar Teardowns por calendario**; se ganan con material que lo amerite. Un
Teardown flojo daña más autoridad de la que 3 Signals construyen.

## 3. Welcome sequence (3 emails, listos para pegar — inglés, sentence case)

Trigger: opt-in confirmado. Exit: termina la secuencia o reply (un reply saca de toda
automatización → conversación humana). Objetivo: fijar la promesa, provocar el primer clic,
y capturar el segmento (agencia vs marca).

### Email 1 — inmediato: la promesa

- **Subject:** `welcome to Inmersivo — here's the deal`
- **Preview:** `one briefing a week, no pitch. this is what to expect.`

```
You're in.

Every Tuesday you'll get one short briefing on what's actually working
in immersive experiences — and why. Real-time 3D, projection, AR,
interactive. Read with a producer's eye: budget, build, brief.

Two rules we hold ourselves to:

1. Everything has to be useful in your next pitch. If it isn't
   ammunition, inspiration, or a talking point, it doesn't go in.
2. No sales pitch. This is a briefing, not a funnel.

Start with our latest edition:

[Read the latest edition →]

— SensaLab
The real luxury is presence
```

- **CTA:** botón a la última edición web. Un email, un trabajo: primer clic.

### Email 2 — día 2-3: la lente (por qué existe esto)

- **Subject:** `why we read experiences the way we do`
- **Preview:** `the gap between a spectacle and an expensive screen.`

```
Quick one.

The gap between an experience people line up for and an expensive
screen nobody remembers is rarely budget. It's craft: presence,
real-time response, interaction that feels alive.

That craft can be read. That's what Inmersivo does every week —
decode the pieces everyone's talking about, in production terms:
what moved the bar, what fell flat, and what it means for the
next brief on your desk.

If there's a piece you'd like us to put under the lens, hit reply
and name it. We read everything.

— SensaLab
```

- **CTA:** reply prompt suave. Siembra la conducta más valiosa (reply) desde el día 3.

### Email 3 — día 7: segmentación conversacional

- **Subject:** `one question so we get this right`
- **Preview:** `agency side or brand side?`

```
One question, ten seconds:

Are you reading from the agency side (you produce experiences for
clients) or the brand side (you commission them)?

[I'm agency side]   [I'm brand side]

Same briefing either way — but it helps us choose angles that are
actually useful to you.

— SensaLab
```

- **CTA:** dos links con UTM distinta → escriben el segmento en el perfil del suscriptor
  (`data/subscribers.json`). Cero fricción, cero form.

## 4. Ritmo permanente (la edición semanal)

Anatomía del email-slim (el vehículo — ya construido en `signal_email.py`):
- Asunto: sentence case, específico, 40-60 caracteres, gancho de la historia líder — nunca
  "Inmersivo #12" (el número no es un beneficio).
- Cuerpo: hook de 1-2 líneas + 1 botón a la edición web. El email gana el clic, la web
  entrega el valor. El clic va a NUESTRO sitio (data first-party, `tracking.py`).
- P.S. rotativo (máx 1 de cada 4 semanas el CTA suave de negocio; las otras: reply prompt,
  forward ask, o nada).

## 5. Re-engagement (dormidos)

Trigger: 0 puntos de engagement en 8 semanas (por clics, no solo opens — MPP infla opens).
Secuencia de 3 emails en 2 semanas; exit inmediato con cualquier clic o reply.

1. **Check-in** — subject `still useful?` — "We noticed you haven't opened Inmersivo in a
   while. One line: is it still useful to you? Reply 'keep' and we'll keep them coming."
2. **Lo mejor del trimestre** (día 5) — subject `the 3 editions worth your time` — los 3 links
   más clickeados del trimestre. Que el mejor contenido re-venda la suscripción.
3. **Última** (día 14) — subject `should we stop?` — "If we don't hear from you, we'll pause
   your subscription next week. One click keeps you in: [keep me in]." Sin clic → sunset
  (status paused, no delete). Lista pequeña y limpia > lista grande y muerta: protege
  deliverability y hace honesto el WEIR.

## 6. Higiene y deliverability (condición de todo lo anterior)

- Dominio: autenticar SPF + DKIM + DMARC en sensalab.io ANTES del primer envío (Brevo lo guía).
  Considerar subdominio de envío (news.sensalab.io) para aislar reputación.
- Warm-up: las primeras 2-3 semanas enviar a la lista semilla pequeña (mayor engagement =
  mejor reputación inicial). No volcar los 118 leads el día 1.
- Reply-to: hello@sensalab.io, monitoreado a diario — el reply es el evento de conversión #1.
- List-unsubscribe header activo (Brevo) y link de unsub visible. Gmail/Yahoo lo exigen.
- Los invitados 1:1 que no aceptan NO se suscriben. Solo opt-in real entra a la lista.
