# Plan de construcción de lista — de 118 leads a suscriptores con opt-in limpio

Metodología: skills `list-builder` (lista chica y targeteada > lista grande), `prospecting`
(fases 1–5 + guardarraíles de compliance) y `lead-magnets` (concepto aplicado al one-pager).

## Principios no negociables

1. **Nunca se compra una lista. Nunca se importa a nadie como "suscrito" sin su opt-in.**
   Los 118 del SL-26 son prospects de ventas con lineage legítimo (LeBook, Apollo, Coachella) —
   perfectamente contactables 1:1 bajo CAN-SPAM (B2B, con opt-out), pero NO son suscriptores.
   Se les INVITA; solo entra a Brevo quien dice sí o se registra solo.
2. **Double opt-in en Brevo** para todo el que llegue por formulario. Para el sí explícito por
   email/reply, basta single opt-in con el reply guardado como evidencia (guardar fecha + fuente
   en el atributo `SOURCE` — lineage GDPR/CAN-SPAM del skill `prospecting`).
3. **Quality bar del `list-builder`:** el objetivo NO es volumen. 80–120 personas correctas del
   circuito experiencial de LA valen más que 5,000 genéricas (6–50 leads → 5.3% reply vs 1.1%
   en 1,000+). Cada nombre debe pasar el test: "¿ventas querría llamarlo?"
4. **Guardarriel legal:** ninguna pieza de invitación menciona trabajo pasado del fundador,
   clientes pasados ni Cinética. Cero datos inventados.

---

## Fase 0 — Pre-lanzamiento (semana 1)

- [ ] Corregir los 6 bad data del SL-26: Lizzy Lehn (buscar email), Gary Fischer (línea muerta),
      Noelle Whitmore (tel NIS), Eddie Brannan (typo gmal.com → probar gmail.com), Mindy Benner
      (sin email), Temoc González (email de otra persona). Herramienta: LinkedIn + verificación
      manual; si no se resuelve, quedan fuera.
- [ ] Excluir de invitaciones: CAA / Danielle Oxford (declinó).
- [ ] Brevo: crear lista "INMERSIVO", atributos (`03-segmentacion.md`), formulario double opt-in,
      página de signup en sensalab.io (o subdominio), y autenticación del dominio de envío
      (SPF + DKIM + DMARC — idealmente `news.sensalab.io` para proteger el dominio raíz).
- [ ] Página de archivo web de ediciones (el modelo ya es web-rica + email-slim: la web edition
      pública es el mejor argumento de suscripción — "see the latest edition" convierte más que
      prometer).

## Fase 1 — Wave 1: los 21 warm+ (semana 1–2)

Invitación 1:1 personal de Jon, referenciando el hilo existente. NO es un blast: 21 emails
escritos a mano (o semi-templated). Expectativa realista: 40–60% opt-in → **8–13 suscriptores
fundadores** que además son los leads más calientes del pipeline.

Copy base (inglés, sentence case, adaptar 1 línea por persona):

> Subject: Starting something — thought of you
>
> Hi [name] — following up on our thread from [context: LeBook / our call / your reply].
>
> We're starting INMERSIVO: a short weekly read on real-time 3D, projection and interactive
> tech in brand experiences — what got built, how, and why it matters. No pitch, just the
> stuff we'd want to read ourselves.
>
> Want in? Just reply "yes" and you're on the list. One email a week, unsubscribe anytime.
>
> [firma Jon]
> The real luxury is presence.

Registrar cada "yes" con fecha en Brevo (`SOURCE = sl26-invite`).

## Fase 2 — Wave 2: los 90 cold conocidos (semana 2–5)

Los 44 attempted + 46 email-only entran en la secuencia email+LinkedIn que el propio SL-26
recomienda ("sequence before you dial", "dial the 46 email-only tail — already warmed").
El newsletter es el REGALO del touch 1, no el pitch:

> Subject: One good reason to hear from us weekly
>
> Hi [name] — I reached out a while back about SensaLab's white-label interactive layer for
> experiential work. Different note today: we just launched INMERSIVO, a weekly breakdown of
> the best immersive brand experiences — how they're built, rough cost logic, and what's
> coming next. Here's the latest edition: [link a la web edition].
>
> If it's useful, one click subscribes you. If not, no hard feelings — this is the only
> invite I'll send.
>
> [firma]

Reglas: 1 invitación + 1 recordatorio máximo (a los 10 días, solo a quien abrió sin clickear).
Después, el que no entró queda como prospect de ventas normal, no se le vuelve a invitar por
email (LinkedIn puede recordárselo orgánicamente). Cadencia de envío: 15–20/día para proteger
reputación del dominio.

Expectativa: 10–18% opt-in → **9–16 suscriptores**.

## Fase 3 — Wave 3: las 78 agencias ICP (semana 3–8, continuo)

Fuente: la lista scoreada del SL-26. Orden de ataque: 29 Strong → 15 Good (las 13 Possible solo
si sobra capacidad; las 21 screened-out jamás). 4 ya están en pipeline (OBE, NVE, MKG, Mirrored
Media) — esas van por wave 1/2.

Proceso por agencia (skill `prospecting`, branch B2B, con sus guardarraíles):
1. Identificar a la persona correcta en LinkedIn (manual, sin scraping): buscar títulos MAKER
   primero (EP / head of production / senior creative producer), founder/ECD en boutiques.
2. Connect request corto + al aceptar, DM con la última web edition + link de signup:

> Loved what [agency] did at [something public and recent they posted]. We write INMERSIVO —
> a weekly teardown of immersive brand experiences (build, cost logic, why it matters).
> Producers at LA shops read it for pitch ammunition. Latest edition: [link]. If it's your
> thing, signup is one click.

3. Email solo si está publicado en el sitio de la agencia (canal público) o si responde el DM.
4. Registrar `SOURCE = linkedin` + fecha.

Ritmo sostenible: 8–10 agencias/semana (regla "steady beats bursty" del SL-26).
Expectativa: 30–40% de las 44 Strong+Good aportan al menos 1 suscriptor → **15–25 suscriptores**.

## Motores de crecimiento continuo (después de las waves)

| Motor | Mecánica | Nota |
|---|---|---|
| **LinkedIn orgánico** | Jon publica 1 destacado de cada edición (la imagen/insight más fuerte) con link a la web edition; CTA de signup en el perfil y página de empresa | El canal donde ya hay 72% de los leads |
| **Eventos (LeBook, Coachella-style scouting)** | El follow-up post-evento cambia de "nice to meet you" a "join INMERSIVO" — CTA concreto y de bajo compromiso; QR del signup en el iPad/one-pager del booth | LeBook produjo el 76% de la lista actual: es EL canal |
| **Sitio web** | Signup en home + cada web edition pública termina en un bloque de suscripción ("get next week's edition") | Las web editions son SEO/AI-visibility a largo plazo |
| **Lead magnet: el one-pager "ideas"** | El SL-26 prueba que el book de 100 ideas jala replies. Versión gateada: un sampler tipo "10 interactive ideas for your next activation" (PDF corto) a cambio del opt-in; el book completo sigue siendo colateral de ventas 1:1 | No quemar el asset completo en el gate |
| **Referral loop** | Footer de cada email: "Forwarded by someone great? Get your own copy → [link]" + pedir el forward explícito 1 vez al mes ("know a producer who'd use this? forward it") | Gratis y compuesto; los referrals ya funcionan (4 en el SL-26) |

## Meta a 90 días (honesta, sin inflar)

| Fuente | Suscriptores esperados |
|---|---|
| Wave 1 (21 warm+) | 8–13 |
| Wave 2 (90 cold) | 9–16 |
| Wave 3 (44 Strong+Good) | 15–25 |
| Motores continuos (LinkedIn, web, referral, evento si cae) | 10–20 |
| **Total 90 días** | **~45–75 suscriptores ICP-puros** |

Con 95% de conversión on-reach documentada, 50–70 decision-makers leyéndote semanalmente es un
activo de pipeline enorme — no medir este newsletter en miles.

## Higiene y deliverability (checklist permanente)

- [ ] Double opt-in activo en formularios; evidencia de opt-in guardada para invitaciones.
- [ ] SPF/DKIM/DMARC verificados en Brevo antes del primer envío.
- [ ] Baja de 1 click + dirección física en el footer (CAN-SPAM).
- [ ] Bounces duros se eliminan tras la primera edición; sunset de dormants (ver `03-segmentacion.md`).
- [ ] Nunca superar el límite diario del plan Brevo (300/día) — con esta lista no es problema.
- [ ] Cada contacto conserva `SOURCE` + fecha (lineage de compliance del skill `prospecting`).
