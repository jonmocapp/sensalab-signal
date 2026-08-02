# Flujo de consentimiento / opt-in B2B — y qué hacer con los leads del SL-26

Especialista 08 — Compliance, legal & brand safety.

Principio rector: **el contenido es público, la lista es opt-in.** El modelo del motor ya lo
permite: la edición rica vive en la web (`sensalab.io/inmersivo/NN`) y el email slim solo es
el vehículo (BRIEF, "Producto ya construido"). Eso significa que nunca necesitamos meter a un
lead frío en Brevo para que vea el contenido — le mandamos el link y que él decida suscribirse.

---

## 1. Single vs double opt-in — decisión

**Recomendación: double opt-in (DOI) vía formulario nativo de Brevo.**

| Criterio | Single | Double |
|---|---|---|
| Mínimo legal US (CAN-SPAM) | Suficiente | Suficiente |
| Prueba de consentimiento (GDPR/CASL/disputas) | Débil | Fuerte: Brevo registra timestamp + IP + fuente |
| Deliverability (spam-rate <0.3% que exigen Gmail/Yahoo) | Riesgo de typos/bots | Lista limpia desde el día 1 |
| Fricción | Ninguna | ~20-30% no confirma |

Con un universo pequeño y de alto valor (productores senior), la calidad de la lista importa
más que el volumen: un spam complaint de un VP pesa muchísimo en una lista de 100. DOI.

Mitigación de la fricción: el email de confirmación DOI debe ser de marca (logo lazo, sentence
case, paleta) y de una sola acción: "Confirm and you're in. One email a week, unsubscribe
anytime." **Ojo Brevo**: el email de DOI no puede llevar contenido comercial extra — es solo
confirmación.

Base legal por régimen:
- **US (CAN-SPAM)**: opt-out; el DOI nos da además la exención de rotular "advertisement".
- **GDPR (si cae un suscriptor UE)**: consentimiento art. 6.1.a, probado por el log DOI.
- **CASL (si cae un canadiense)**: consentimiento expreso — el DOI lo satisface.

## 2. Setup en Brevo (todo en plan gratis)

1. Lista única `INMERSIVO` (el `BREVO_LIST_ID` del `.env`). No fragmentar en listas paralelas:
   las bajas se gestionan globalmente y una sola lista evita reenvíos a des-suscritos.
2. Atributos del contacto: `FIRSTNAME`, `COMPANY`, `ROLE`, `CONSENT_SOURCE`
   (`web-form` / `event` / `1to1-invite`), `CONSENT_DATE`. IP y timestamp los guarda Brevo solo.
3. Formulario (Contacts → Forms): checkbox NO premarcado, texto exacto sugerido:
   > *"Send me INMERSIVO — one email a week on immersive production. Unsubscribe anytime.
   > See our [privacy policy]."*
4. Activar double opt-in en el form; personalizar el email de confirmación con la marca.
5. Colocación del form: página del newsletter (`sensalab.io/inmersivo`), footer del sitio, y
   como link (Brevo hospeda el form con URL propia) para LinkedIn/firmas de email.
6. Suppression: nunca importar por encima; cualquier "sácame" por reply se agrega a blocklist
   el mismo día.

## 3. Los leads del SL-26 — sin quemarlos y sin violar reglas

Datos (BRIEF): 118 leads LA (98% email, 72% LinkedIn), 78 agencias ICP, 29 Strong.

**Regla dura: los 118 NO se importan a Brevo.** Tres razones independientes:
1. **Términos de Brevo**: prohíben listas compradas/recolectadas sin consentimiento. Un import
   frío arriesga la suspensión de la cuenta — perderíamos el canal entero por 118 contactos.
2. **Deliverability**: contactos que no esperan el email = complaints y bounces sobre un
   dominio (sensalab.io) que apenas empieza a construir reputación. Irreversible.
3. **Marca**: el newsletter posiciona por generosidad ("da munición, no vende duro"). Llegar
   sin permiso contradice la tesis del producto.

CAN-SPAM permitiría el envío frío con opt-out; el bloqueo aquí es contractual (Brevo),
técnico (reputación) y de marca — conviene decirlo así de claro para que la regla no parezca
arbitraria cuando haya prisa por "activar la lista".

### El flujo que sí (conversión de lead frío → suscriptor con consentimiento)

**Canal 1 — invitación 1:1 personal (los 29 Strong primero).**
Email individual desde el buzón normal de Jon (no ESP, no bulk, no plantilla masiva), tono
de colega compartiendo una pieza:
> Subject: `the world cup off-pitch playbook`
> "Hey {Name} — we just published a teardown of the World Cup activations that actually
> worked (drone scoreboard as a data pipeline, Cosm's venue-grade watch parties). Thought
> of {Agency} because of your experiential work. It's here: sensalab.io/inmersivo/05.
> We publish one of these a week — if it's useful you can get it by email here: {link al
> form DOI}. Either way, curious what you thought of the dome capture approach."
- Es correo real de relación (comparte contenido público, invita, pregunta), enviado 1:1.
  Aun así conserva higiene CAN-SPAM: identidad real y si alguien dice "no me escribas más",
  se respeta y se anota.
- Ritmo: 5-8/día máximo (protege la reputación del buzón personal), Strong → Good → resto.
- El lead NUNCA entra a la lista por esta vía: entra solo si él mismo completa el DOI.
  `CONSENT_SOURCE=1to1-invite` para medir conversión del pipeline SL-26.

**Canal 2 — LinkedIn (72% de los leads).**
Post de cada edición desde el perfil/página + DM a los Strong con el link a la edición web.
LinkedIn DMs no son email (CAN-SPAM no aplica); las normas son las de la plataforma. Mismo
principio: se comparte el contenido público, el form DOI hace la conversión.

**Canal 3 — eventos/llamadas.** Invitación verbal → "te mando el link para apuntarte" → DOI.
Nunca apuntar a nadie a mano "porque dijo que sí en un evento": el form es el registro.

### Qué NO hacer (lista negra operativa)
- No importar CSV del SL-26 a Brevo "solo como draft" — el riesgo es el import, no el envío.
- No BCC masivo desde Gmail (mata el buzón personal y es bulk de facto).
- No pre-marcar checkboxes ni esconder la suscripción dentro de otra cosa.
- No "te suscribí, avísame si no quieres" — inversión de consentimiento prohibida en CASL
  y tóxica de marca.
- No comprar listas para acelerar. Nunca.

## 4. Métrica honesta

Con DOI + invitación 1:1, esperar 10-25% de conversión de los Strong en 60 días (~5-8
suscriptores del núcleo) más el goteo web/LinkedIn. Es lento y correcto: el insight del SL-26
es que el pitch convierte cuando hay conexión — la lista pequeña y consentida ES la conexión.
El número que cuida este flujo no es el tamaño de la lista: es spam complaints = 0 y
open rate >50% en un nicho de 100 personas.
