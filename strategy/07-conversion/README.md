# 07 — Conversión, CTA & lead capture

Especialista 07 · Misión: convertir lectores en conversaciones sin vender duro.

## Qué entregué

| Archivo | Contenido |
|---|---|
| `01-cta-strategy.md` | Jerarquía de CTAs por pieza (email slim vs web) y por formato (Signal vs Teardown); regla "una acción primaria por edición"; banco de 5 invitations PVP pegables (JSON listo para las ediciones); rotación de 6 semanas; reglas de copy; métricas |
| `02-touch-it-flow.md` | El flujo completo "Have something impossible in mind? → Touch it": mailto prefilled en email (reply-first), página `/touch` con copy completo, post-submit, esqueleto de la primera respuesta humana de Jon, métricas |
| `03-landing-work-with-us-spec.md` | Spec sección por sección de la landing ligera con copy final pegable: hero, 3 capabilities, cómo funciona, confianza sin clientes, FAQ, #touch, captura de newsletter, footer real |
| `landing-sample.html` (+ `media/sensalab-logo.png`) | Muestra funcional de la landing: paleta exacta (#0B0F0F/#F4F3F3/#787878/#1C1956/#E4E4EF), gradiente solo como barra de marca, sentence case, logo y footer reales, responsive, form #touch funcional vía mailto (sin backend), firma "The real luxury is presence" |
| `04-lead-magnets.md` | Portafolio de 4 magnets mapeados a etapa del funnel: swipe file (crecer lista), build notes (calificar), one-pager existente (colateral sin gate), impossible brief review (la oferta como magnet); gating, delivery, distribución LinkedIn/outbound, tags Brevo |
| `05-offer-framing.md` | La capa white-label como oferta: escalera feature→outcome, one-liners, value prop, full offer, value equation, anatomía de 6 componentes, el ask por canal, vocabulario del sistema y prohibido |

## Skills usados (los 6 pedidos)

- **`cro`** — jerarquía de CTAs, una acción primaria por edición, framework de landing (hero /
  prueba / objeciones / fricción), manejo de objeciones en FAQ, experimentos de una variable.
- **`cta-designer`** — metodología PVP para las invitations (valor sin permiso, cero calendario,
  reply de una palabra), tipología (diagnostic/resource/insight/trigger), regla de secuencia
  "nunca el mismo tipo dos veces seguidas", niveles de fricción.
- **`offers`** — value equation (diagnóstico: perceived likelihood es la palanca débil por el
  guardarriel → el newsletter la compensa), anatomía de 6 componentes, garantías no-reembolso
  (honestidad + invisibilidad), scarcity solo real, vocabulario prohibido.
- **`offer-definer`** — escalera feature→outcome, los 3 niveles de oferta (one-liner / value
  prop / full offer), líneas por canal, checklist de errores.
- **`signup`** — forms de campos mínimos (2 en #touch, 1 en suscripción), quitar incertidumbre
  ("what happens next"), microcopy y errores, post-submit/thank-you, mobile.
- **`lead-magnets`** — matching de formato a buyer stage, estrategia de gating (email-only vs
  sin gate vs reply-como-captura), content upgrades (build notes = upgrade del Teardown),
  delivery, benchmarks y distribución.

## Decisiones clave (y por qué)

1. **Reply-first, no landing-first.** La conversión que importa es la conversación (SL-26: "the
   pitch converts, connection is the bottleneck"). En el email, "Touch it" = mailto prefilled +
   "or just hit reply"; la landing es para tráfico web/frío. Bonus: las replies suben la
   reputación del sender.
2. **"Touch it" queda reservado para pedir conversación.** Cuando la invitation ofrece un
   recurso, el botón cambia de verbo ("Send me the notes") para no diluir la firma.
3. **Nunca "book a call" en el email.** El calendario aparece recién en el segundo intercambio
   humano. Una acción primaria por edición; los magnets solo ocupan el slot del invitation.
4. **Prueba social sin clientes** (guardarriel): compromisos verificables (your brand on
   everything / NDA / respuesta franca) + el newsletter como criterio público. Nada inventado.
5. **Dentro del email los magnets se piden por reply con una palabra** (`notes`, `list`) — a un
   suscriptor no se le pide un form. Los gates con form son solo para tráfico externo.
6. **El one-pager existente NO se gatea**: es colateral de cierre (adjunto de la primera
   respuesta + link en la landing).
7. En docs uso "Inmersivo" (no INMERSIVO) en todo copy público por la regla de sentence case.

## Qué necesito de Jon

1. **Confirmar el SLA del feasibility read: ¿48 h es sostenible?** Si no, definir el número real
   (72 h / two business days) — está impreso en invitation V5, /touch, landing y first-reply.
2. **Confirmar que el feasibility read no se cobra** (el copy de la FAQ lo implica: "costs you
   two lines of email").
3. **Scarcity honesta:** ¿hay un límite real de builds simultáneos por trimestre que se pueda
   publicar? Si no hay número honesto, no publicamos scarcity (así está escrito).
4. **Envío desde hello@sensalab.io** (o reply-to) en Brevo — el modelo reply-first depende de
   eso — + crear tags: `swipe-file`, `build-notes`, `brief-sent`, `newsletter-only`.
5. **Hosting**: dónde vivirán `/work-with-us` y `/touch` (la muestra HTML está lista para
   adaptar); conectar el form de suscripción a Brevo (double opt-in) — está marcado con
   `data-todo="brevo"` en el HTML.
6. **Aprobar la línea de bio de LinkedIn** propuesta en `05-offer-framing.md` §5.

## Nota de integración (yo NO toqué los .py)

- `signal_email.py` hoy manda el botón del invitation a `web_url#invitation`. Recomendado: en el
  email ese botón → mailto prefilled (URL exacta en `02-touch-it-flow.md` §2) + línea "Or just
  hit reply — it lands with a human." debajo.
- `render_signal.py` / `render_teardown.py`: el botón del invitation en la web → `/touch`
  (o `/work-with-us#touch`); agregar bloque de suscripción email-only antes del footer para
  visitantes no suscritos.
- Las 5 invitations del banco (`01-cta-strategy.md` §5) son JSON con las mismas claves que ya
  usan `edicion-A.json` / `edicion-B.json` — se pegan directo en las ediciones.
