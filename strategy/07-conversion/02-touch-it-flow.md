# El flujo "Touch it" — de newsletter a conversación

> Especialista 07 · Skills aplicados: `cta-designer` (reply-first, cero calendario),
> `signup` (mínimos campos, quitar incertidumbre, post-submit), `cro` (fricción).

---

## 1. Mapa del flujo (decisión clave: reply-first)

```
EMAIL (suscriptor, warm)                    WEB (visitante, puede ser frío)
┌──────────────────────────┐               ┌──────────────────────────┐
│ invitation block         │               │ invitation block          │
│ "Have something          │               │ (misma copy)              │
│  impossible in mind?"    │               │                           │
│ [Touch it] ──────────────┼─→ mailto:     │ [Touch it] ───────────────┼─→ /touch
│ "Or just hit reply…"     │   prefilled   │                           │   (micro-landing)
└──────────────────────────┘               └──────────────────────────┘
            │                                          │
            ▼                                          ▼
   reply llega a hello@sensalab.io  ◄──── form de 2 campos o mailto
            │
            ▼
   primera respuesta humana < 48 h (SLA a confirmar por Jon)
   + one-pager adjunto (02-Marca/one_pager_sensalab_EN_2.pdf)
            │
            ▼
   si hay brief real → feasibility read → walkthrough de 20 min (recién AQUÍ aparece calendario)
```

**Por qué reply-first y no landing-first en el email** (skills `cta-designer` + `signup`):
1. Cero campos, cero páginas: la fricción más baja posible para un suscriptor warm.
2. Las replies son la conversación misma — el objetivo del SL-26 — no un proxy.
3. Bonus de entregabilidad: replies al remitente son la señal de engagement más fuerte para
   Gmail/Outlook; suben la reputación de hello@sensalab.io con cada edición.
4. Requisito: el email se envía **desde hello@sensalab.io** (o reply-to a esa casilla) — a
   configurar en Brevo.

## 2. El botón del email: mailto prefilled

El botón "Touch it" del email-slim debe apuntar a (cambio a integrar en `signal_email.py`,
yo no toqué el .py):

```
mailto:hello@sensalab.io?subject=An%20impossible%20brief&body=The%20brief%20(two%20lines%20is%20plenty)%3A%0A%0AWhere%20it%20happens%3A%0A%0AWhen%20it%20needs%20to%20be%20real%3A
```

Legible:

```
to:      hello@sensalab.io
subject: An impossible brief
body:    The brief (two lines is plenty):

         Where it happens:

         When it needs to be real:
```

Debajo del botón, siempre esta línea (13px, #787878):

```
Or just hit reply — it lands with a human.
```

Variantes del mailto por tipo de invitation (ver rotación en `01-cta-strategy.md`):

| Invitation | subject prefilled |
|---|---|
| V1 diagnostic / V4 trigger / V5 oferta | `An impossible brief` |
| V2 build notes | `Notes` |
| V3 swipe file | `List` |

Para V2/V3 el body va vacío — una palabra basta, esa es la gracia.

## 3. La página /touch (micro-landing, un solo propósito)

Destino del invitation en la **edición web** y link estable para bio de LinkedIn. NO es la
"work with us" (esa es más larga, ver `03-landing-work-with-us-spec.md`); /touch es el pasillo
más corto entre "leí algo" y "hablemos".

### Estructura y copy completo (pegable, sentence case)

```
[barra gradiente de marca, 4px]
[logo SensaLab]

kicker:   An open invitation
h1:       Have something impossible in mind?
sub:      A dome, a live-data show, a room that reacts — if the brief sounds
          unbuildable, that's our favorite kind. Tell us in two lines.

FORM (2 campos, skill signup: mínimo absoluto)
  label:       Work email
  placeholder: you@agency.com
  label:       The brief, in two lines
  placeholder: e.g. a 30-foot wall that reacts to every fan walking past — live, in June
  botón:       Send it
  microcopy:   A human reads every note. No newsletter signup hidden in here.

alternativa bajo el form:
  Prefer email? Write to hello@sensalab.io  [copy address]

QUÉ PASA DESPUÉS (quita incertidumbre — signup skill)
  1. Your note lands with a producer, not a bot.
  2. You get a feasibility read within 48 hours — buildable or not, and why.
  3. If it's worth a build, we scope it under your brand.

CONFIANZA (una línea, sin logos de clientes — guardarriel)
  White-label by default. NDA before details, if you prefer. Your brand on everything.

[footer real de marca]
```

### Post-submit (thank-you state)

```
h2:   Got it.
body: A human reads every brief — you'll hear from us within 48 hours.
      Meanwhile, the latest edition of Inmersivo is here →
```
(El link cierra el loop de vuelta al contenido; skill `lead-magnets`: nunca desperdiciar el
thank-you.)

### Reglas de implementación (skill signup)

- 2 campos máximo. Nombre, empresa y rol se infieren del dominio del email o se preguntan en la
  respuesta humana. Cada campo extra cuesta conversión.
- Sin CAPTCHA visible; honeypot oculto si hace falta.
- Mobile: inputs ≥44px de alto, teclado `type=email`.
- Errores inline, no limpiar el form.
- Sin backend todavía: el form puede construir un mailto (así está resuelto en
  `landing-sample.html`); cuando haya hosting, un endpoint que reenvíe a hello@sensalab.io.

## 4. La primera respuesta humana (el momento que convierte)

Esqueleto para Jon (inglés, sentence case, adjuntar el one-pager):

```
Subject: Re: An impossible brief

Hi [name] — thanks for sending this.

Short version: [buildable / buildable with one caveat / not as written — here's why, one line].
The thing that decides cost here is [the one variable].

Two questions before I give you a proper read:
1. [pregunta específica del brief]
2. When would it need to be standing?

Attached is a one-pager on how the white-label layer works — your brand on
everything, we stay invisible.

[firma]
The real luxury is presence
```

Reglas: responder < 48 h; nunca pedir call en el primer reply — el walkthrough de 20 min se
ofrece en el segundo intercambio, cuando ya hay brief concreto (secuencia de `cta-designer`:
el ask directo llega después de construir confianza).

## 5. Métricas del flujo

| Punto | Métrica | Señal de salud |
|---|---|---|
| Email | replies / 1.000 entregados | tendencia ↑ edición a edición |
| /touch | envíos de form / visitas | >10% (tráfico warm desde la edición web) |
| Respuesta | tiempo a primera respuesta humana | < 48 h siempre |
| Conversación | % de replies que llegan a feasibility read | la métrica de calificación real |
