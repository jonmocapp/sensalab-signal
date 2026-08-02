# Spec — landing "work with us" (ligera)

> Especialista 07 · Skills aplicados: `cro` (framework completo de landing), `offers` /
> `offer-definer` (el copy expresa la oferta, no features), `signup` (form y captura).
> Muestra funcional: `landing-sample.html` en esta carpeta (paleta, logo y footer reales).

---

## Rol de la página

Para el visitante que NO viene del newsletter (LinkedIn, firma de email, boca a boca) o que
quiere contexto antes de escribir. **Una sola conversión primaria: enviar el brief** (sección
#touch). Conversión secundaria para los que no están listos: suscribirse a Inmersivo (email-only).
Sin navegación que compita (skill `cro`: landing = argumento completo en una página, un CTA).

URL sugerida: `sensalab.io/work-with-us` (y `/touch` puede ser esta misma página anclada a #touch
si se quiere mantener una sola pieza de hosting al inicio).

## Reglas duras aplicadas

- Paleta de texto solo: `#0B0F0F` `#F4F3F3` `#787878` `#1C1956` `#E4E4EF`. Gradiente de marca
  únicamente como barra superior de 4px (mismo uso que el email-slim).
- Sentence case en todo. Logo real (`media/sensalab-logo.png`). Footer real + firma
  "The real luxury is presence".
- Guardarriel: cero clientes pasados, cero Cinética, cero métricas inventadas. La prueba social
  se construye con **compromisos de proceso + pensamiento público** (ver sección 5).
- Tipografía: producción con KMR Apparat self-hosted (`02-Marca/KMR Apparat/`); la muestra usa
  stack Helvetica/Arial para no depender de licencias en un HTML suelto.

## Estructura sección por sección (copy final pegable)

### 0. Barra de marca + header
Barra gradiente 4px. Logo a la izquierda. Un solo link a la derecha: `Touch it` → #touch.

### 1. Hero
```
kicker:  For experiential producers
h1:      Say yes to the unbuildable brief
sub:     SensaLab is a white-label technical layer for experiential agencies —
         real-time 3D, projection and AR, built under your brand. You keep the
         client, the credit and the stage. We keep it running.
CTA 1:   Touch it            → #touch (botón, #1C1956 sobre #F4F3F3)
CTA 2:   Read the newsletter → edición web de Inmersivo (link de texto)
```
Racional (`cro`): headline de outcome, no de categoría; el sub responde "qué es, para quién,
qué gano" en 5 segundos; jerarquía de dos CTAs sin competencia.

### 2. Qué construimos (3 tarjetas capability → outcome)
```
h2: What we build

Real-time 3D
Venue-scale scenes that respond to live data — scores, votes, crowds, weather.
So the room changes when the moment does.

Projection
Mapping designed for the surface it lives on, not repurposed from a screen.
So the architecture becomes the medium.

AR and interactive
Rooms, walls and objects that react to the person in front of them.
So the audience gets a role, not a view.
```
Cada tarjeta: capability (1 línea) + outcome (línea "so…"). Escalera feature→outcome de
`offer-definer`.

### 3. Cómo funciona (3 pasos — baja el effort percibido, skill `offers`)
```
h2: How it works

1 · Send the brief
Two lines is plenty. The scary version, not the safe one.

2 · Feasibility read in 48 hours
Buildable or not, the real risks, and the one decision that makes it cheaper.
Before you promise anything to a client.

3 · We build under your brand
Your deck, your files, your name on-site. We stay invisible — that's the job.
```
⚠️ "48 hours" y el alcance del feasibility read los confirma Jon (ver README).

### 4. Por qué white-label (framing de oferta, sin fricción)
```
h2: Built to disappear

The layer is white-label because the work is yours. We don't compete for your
client — agencies and producers are who we work for. The tech carries your
brand into the pitch, through production, and onto the floor.
```

### 5. Confianza sin nombrar clientes (guardarriel → prueba por compromisos)
```
h2: What you can hold us to

· Your brand on everything — decks, files, credits, on-site shirts if it comes to that.
· NDA before details, if you prefer. Standard, not special.
· A straight answer in the feasibility read — if it isn't buildable, we say so
  before you pitch it, not after.
· Our thinking is public. Every week Inmersivo tears down what worked in
  experiential and why — judge the lens before you ever send a brief.
```
Racional: el skill `cro` pide social proof cerca del CTA; el guardarriel prohíbe logos y casos.
Sustituto legítimo: compromisos verificables + el newsletter como prueba de criterio
(pensamiento público = proof of craft). Nada inventado.

### 6. FAQ (manejo de objeciones, skill `cro`)
```
h2: Fair questions

Who gets the credit?
You do. That's what white-label means here — publicly, the work is your agency's.

Do you work directly with brands?
Our home is behind agencies and producers. When a brand comes to us directly,
the answer usually starts with "who's producing it?"

We're not sure it's even possible. Should we still write?
That's the exact right moment. The feasibility read exists so you know what's
real before the client hears a promise.

What does it cost?
Every build is scoped to the brief — there's no rate card that survives contact
with a dome. The feasibility read costs you two lines of email.
```
⚠️ La última respuesta implica que el feasibility read no se cobra — decisión de negocio que
confirma Jon.

### 7. #touch — el ask (idéntico al de `02-touch-it-flow.md`)
```
kicker: An open invitation
h2:     Have something impossible in mind?
body:   A dome, a live-data show, a room that reacts — if the brief sounds
        unbuildable, that's our favorite kind. Tell us in two lines.

form:   [Work email] [The brief, in two lines] → botón "Send it"
micro:  A human reads every note. No newsletter signup hidden in here.
alt:    Prefer email? Write to hello@sensalab.io
```

### 8. Captura secundaria — Inmersivo (para los no-listos; skill `lead-magnets` + `signup`)
```
h2:    Not pitching anything yet?
body:  Inmersivo is our weekly read on experiential — what worked, why it
       worked, and what it would take to build. One email a week, written for
       producers.
form:  [Work email] → botón "Subscribe"
micro: One email a week. No spam, no sequences. Unsubscribe anytime.
```
Email-only (un campo). Este bloque queda ARRIBA del footer y DEBAJO de #touch: nunca compite
con la acción primaria.

### 9. Footer real
Principle completo, socials Instagram/LinkedIn/Youtube, © 2026 SensaLab, Inc., Los Angeles,
CA — USA, hello@sensalab.io, sensalab.io. Cierre con la firma:
```
The real luxury is presence
```

## Detalles de implementación de la muestra (`landing-sample.html`)

- Sin dependencias externas (fuentes del sistema, sin CDNs); responsive (grid → 1 columna en
  móvil); botones pill como el email-slim.
- El form #touch construye un `mailto:` a hello@sensalab.io con los dos campos (funciona sin
  backend); el form de suscripción es placeholder marcado con `data-todo="brevo"` para conectar
  a Brevo (lista + double opt-in) cuando estén las keys.
- Anclas: `#touch` y `#newsletter` estables para que emails y bio de LinkedIn puedan apuntar
  directo.

## Experimentos sugeridos cuando haya tráfico (skill `cro`, una variable por vez)

1. Hero headline: "Say yes to the unbuildable brief" vs "The technical layer your pitch is missing".
2. Orden de secciones: FAQ antes vs después de #touch.
3. Form de 2 campos vs mailto-only en #touch.
