# Checklist CAN-SPAM + GDPR/CCPA/CASL — INMERSIVO

Especialista 08 — Compliance, legal & brand safety. Estado auditado contra los archivos reales
del motor (rutas citadas). Objetivo: que la edición #05/#06 se pueda enviar por Brevo sin
exposición legal.

Leyenda: [OK] cumple hoy · [GAP] falta y bloquea · [VERIFICAR] Jon debe confirmar un hecho.

---

## 1. CAN-SPAM (ley aplicable: remitente USA, audiencia LA/US)

CAN-SPAM es régimen de **opt-out**: no exige consentimiento previo, pero exige 7 cosas por
email comercial. Multa estatutaria: hasta ~$53,000 USD **por email individual** (cifra FTC
ajustada 2025). Con 118 leads, un solo envío defectuoso = exposición teórica de 7 cifras.
Por eso el gate de pre-envío trata estos puntos como bloqueantes.

### 1.1 Remitente identificable y veraz — [OK con condición]
- `FROM_NAME=SensaLab`, `FROM_EMAIL=hello@sensalab.io` (config.py:52-53, .env.example). Correcto:
  el "From" identifica al iniciador real.
- **Condición técnica**: autenticar `sensalab.io` en Brevo (Senders & Domains → Authenticate):
  SPF (include de Brevo), DKIM 2048, DMARC (`p=none` el primer mes, luego `p=quarantine`).
  Sin esto, Gmail/Yahoo tratan el correo como no alineado y el "remitente identificable"
  se degrada en la práctica. Es checkbox del gate de pre-envío.

### 1.2 Subject no engañoso — [OK]
- "Steal This World Cup" / "The Audience Can Tell" son editoriales, no engañosos: el contenido
  entrega lo que el subject promete. Mantener la regla del writer ("sin clickbait", writer.py:81).
- Regla permanente: el subject nunca promete algo que el cuerpo no contiene, nunca simula
  respuesta ("Re:") ni transacción ("Your invoice").

### 1.3 Identificación como publicidad — [OK si la lista es 100% opt-in]
- CAN-SPAM exime de rotular "advertisement" cuando hay **consentimiento afirmativo previo**.
- Decisión de política: la lista de INMERSIVO es **solo opt-in confirmado** (ver doc 02).
  Mientras eso sea verdad, no hace falta rótulo. Si alguna vez se enviara a no-suscritos por
  ESP, habría que rotular — y no lo vamos a hacer.

### 1.4 Dirección postal física válida — [GAP — BLOQUEA EL PRIMER ENVÍO]
- Hoy el footer dice solo `Los Angeles, CA — USA` (brand_footer.py:10; final-email-A.html:69).
  Ciudad + estado **no** satisface CAN-SPAM: se exige street address actual, PO Box registrado
  en USPS, o private mailbox en un CMRA (UPS Store, iPostal1, Anytime Mailbox, Stable, etc.).
- Inconsistencia adicional: config.py:57 tiene default `"Ciudad de Mexico, Mexico"` y
  .env.example deja `COMPANY_ADDRESS=Tu direccion fisica, Ciudad, Pais` sin llenar. El footer
  nuevo (brand_footer.py) ni siquiera tiene slot para la dirección de calle.
- **Cómo cumplir con Brevo**:
  1. Jon contrata un virtual mailbox CMRA en Los Angeles (~$10-30/mes; iPostal1 o Anytime
     Mailbox tienen direcciones en LA) o usa la dirección del registered agent si el agente
     lo permite por escrito para correo comercial.
  2. Poner la dirección completa en `COMPANY_ADDRESS` del `.env` **y** en el perfil de empresa
     de Brevo (Settings → Company profile — Brevo la exige y la usa en su footer por defecto).
  3. Integración (para quien toque el motor después; yo no edito .py): `brand_footer.py`
     necesita un campo de dirección postal en `email_footer()` — línea del `fmeta`, formato
     `SensaLab · 1234 Example St #567 · Los Angeles, CA 90210 · USA`.
  4. El gate de pre-envío verifica con regex que el HTML final contenga una dirección con
     número de calle + ZIP antes de permitir crear la campaña (spec en doc 03).

### 1.5 Mecanismo de baja visible y funcional — [OK vía Brevo]
- `{{ unsubscribe }}` presente en el email final (final-email-A.html:71, final-email-B.html:71)
  y es el merge tag correcto de Brevo (config.py:79-82). Brevo lo sustituye por un enlace de
  baja de un clic hospedado por ellos, activo más de 30 días.
- Mejoras Brevo (config, no código):
  - Brevo agrega automáticamente header `List-Unsubscribe` + RFC 8058 (one-click) en campañas.
    Con <5,000 emails/día no es obligatorio por Gmail/Yahoo, pero lo tenemos gratis.
  - No ocultar el link: hoy va en gris subrayado 11px — aceptable ("clear and conspicuous");
    no reducirlo más ni bajar el contraste.
- Regla: el link de baja **nunca** se elimina del template. Es checkbox del gate.

### 1.6 Honrar bajas en ≤10 días hábiles — [OK vía Brevo, con disciplina]
- Brevo suprime al contacto de inmediato y globalmente. No requiere acción.
- Disciplina que sí depende de nosotros:
  - Nunca exportar la lista y reimportarla (revive bajas por error).
  - Si alguien responde "sácame" por email a hello@ en vez de usar el link: blocklist manual
    en Brevo (Contacts → añadir a suppression) el mismo día.
  - Prohibido condicionar la baja a login, formulario largo o "motivo obligatorio".

### 1.7 Responsabilidad por lo enviado "en tu nombre" — [OK con el gate]
- El bot escribe y envía en nombre de SensaLab; CAN-SPAM hace responsable a SensaLab aunque
  el contenido lo genere una máquina. Mitigación: gate de pre-envío + aprobación humana
  registrada (doc 03). Nunca `SEND_MODE=send` directo a producción; siempre draft → revisión
  → envío (sender.py ya soporta ambos modos).

---

## 2. GDPR (exposición baja, higiene igual)

Aplica solo si hay destinatarios en la UE. El ICP es LA/US (BRIEF), así que la exposición es
marginal — pero la higiene GDPR es barata y sirve de prueba de diligencia:

- **Base legal**: consentimiento (art. 6.1.a) capturado por double opt-in de Brevo, que
  registra timestamp + IP + fuente. No usar "interés legítimo" para newsletter B2B a fríos:
  complica todo y no lo necesitamos con lista opt-in.
- **Procesador**: Brevo es empresa francesa; su DPA (Data Processing Agreement) es parte de
  sus términos — guardar una copia PDF en el drive legal. No hay que firmar nada extra.
- **Minimización**: la lista guarda solo email, nombre, empresa, rol, fuente/fecha de
  consentimiento. Nada más.
- **Derechos**: la baja cubre oposición; para borrado (art. 17), cualquier petición a
  hello@sensalab.io se ejecuta en Brevo (delete contact) en ≤30 días. Anotar en un log simple.
- **Privacy policy**: publicar `sensalab.io/privacy` antes de abrir el formulario de alta
  (qué datos, para qué, procesador Brevo, cómo darse de baja/borrarse, contacto). El
  formulario de Brevo debe linkearla.

## 3. CCPA/CPRA (California)

- SensaLab casi seguro está **debajo de los umbrales** (≥$26M ingresos anuales, o datos de
  ≥100k consumidores CA, o ≥50% de ingresos por venta de datos) → la ley no obliga.
  [VERIFICAR con Jon: ingresos < umbral → confirmado no sujeto.]
- Aun así, buenas prácticas que cuestan cero: la privacy policy declara "we do not sell or
  share personal information", notice at collection en el formulario, y se honran peticiones
  de acceso/borrado por hello@.

## 4. CASL (Canadá) — trampa silenciosa

- CASL es régimen de **opt-in** (consentimiento expreso previo) con multas hasta CAD $10M.
- El SL-26 es pipeline de LA, pero si algún lead resulta canadiense (agencia con oficina en
  Toronto/Vancouver, dominio .ca), **no** se le puede enviar sin consentimiento expreso.
- Acción: filtrar la lista por país antes de cualquier import; los canadienses solo entran
  por el formulario DOI.

---

## 5. Resumen: qué falta exactamente y quién lo hace

| # | Acción | Quién | Bloquea envío |
|---|--------|-------|:---:|
| 1 | Contratar mailbox CMRA en LA y ponerla en `.env` + Brevo company profile | Jon | Sí |
| 2 | Slot de dirección postal en `email_footer()` (integración al motor) | Jon/Opus (motor) | Sí |
| 3 | Autenticar sensalab.io en Brevo (SPF/DKIM/DMARC) | Jon (DNS) | Sí |
| 4 | Publicar sensalab.io/privacy y linkearla en el form de alta | Jon | Antes de captar altas |
| 5 | Crear form Brevo con double opt-in (doc 02) | Jon | Antes de captar altas |
| 6 | Política lista-solo-opt-in adoptada por escrito (doc 02) | Jon | Sí (política) |
| 7 | Gate de pre-envío implementado (spec doc 03) | Opus (motor) | Sí |
| 8 | Verificar ® y "Inc." del footer (doc 04) | Jon | No, pero corregir en ed. #05 |
