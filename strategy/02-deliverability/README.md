# 02 — Deliverability e infraestructura de envío

Especialista 02. Misión: que INMERSIVO llegue al inbox del ICP (VP Innovation, creative producers
en agencias/marcas LA), no a spam. Todo lo de esta carpeta es ejecutable tal cual; nada toca los
.py del motor.

## Entregables

| Archivo | Qué contiene |
|---------|--------------|
| `dns-records-sensalab.md` | Registros SPF/DKIM/DMARC listos para pegar (subdominio `news.sensalab.io` + raíz), explicación de cada uno, progresión DMARC none→quarantine→reject, y comandos de verificación |
| `brevo-setup.md` | Setup completo de Brevo: dominio autenticado, remitente verificado, decisión shared vs dedicated IP, envío por API de CAMPAÑAS (con PowerShell ejecutable), tracking server-side vía API/webhooks, letra chica del plan gratis |
| `warmup-y-lista.md` | Estrategia de consentimiento (permission pass), calendario de rampa semana a semana para la lista de 118, verificación previa, política de bounces/quejas/unsubs y flujo sunset de inactivos |
| `auditoria-spam.md` | Auditoría de `final-A/B.html` y `final-email-A/B.html`: 6 bloqueos con fix concreto, scan de copy (limpia), links, ratio texto/imagen, pesos reales medidos |
| `checklist-inbox.md` | Checklists (setup / por edición / post-envío / mensual), tabla de herramientas con costos, diagnóstico rápido |

## Decisiones clave (y por qué)

1. **Enviar desde `news.sensalab.io`, no desde el raíz.** Aísla la reputación del newsletter del
   buzón `hello@sensalab.io`. Reply-to al buzón real para que "Reply." funcione.
2. **Shared IP, no dedicada.** Una IP dedicada a ~500–2.000 emails/mes se enfría sola y daña más
   de lo que protege; el umbral es ~50k/mes.
3. **API de campañas, no transaccional.** Es lo que resuelve `{{ unsubscribe }}` y añade one-click
   unsubscribe (RFC 8058) que Gmail/Yahoo exigen. Enviar el HTML actual por la API transaccional
   rompería el unsubscribe → quejas → muerte del dominio.
4. **Permission pass antes de la edición 1.** La lista viene de outbound; con 118 contactos una
   sola queja ya supera el umbral de Gmail. Un 1:1 de Jon invitando a suscribirse convierte una
   lista fría indefendible en una lista chica pero blindada (y Brevo puede exigir prueba de opt-in).
5. **La copy no es el problema; la infra sí.** El tono editorial sentence case sin urgencia es
   perfil de inbox. Los bloqueos: imágenes con rutas relativas (llegarían rotas), 1,85 MB de
   imágenes en la edición A, WebP que Outlook no renderiza, falta dirección postal CAN-SPAM,
   falta versión texto plano, alts vacíos. Todos con fix puntual en `auditoria-spam.md`.
6. **Engagement = clics + respuestas, nunca aperturas** (Apple MPP las infla). Sunset a las 8
   ediciones sin engagement, con un email de re-enganche antes de suprimir.

## Skills usados (citación)

- **`sales-deliverability`** (invocado con la herramienta Skill): marco SPF/DKIM/DMARC, calendario
  de warmup, umbrales (bounce <3%, quejas <0,1%, DMARC progresivo), regla "no envíes bulk desde el
  dominio primario", higiene de lista. Incluidas sus referencias `references/platforms.md`
  (sección "In Brevo": autenticación, `include:spf.brevo.com`, IP dedicada, DMARC obligatorio
  Gmail/Yahoo 2024 y Microsoft 2025, pricing por volumen) y `references/learnings.md`.
- **`sales-brevo`** (skill de plataforma, leído vía el repo remoto del skill según el protocolo de
  `sales-deliverability`): confirmó el flujo Settings → Domains, `spf.brevo.com`, dedicated IP solo
  en pago con warmup gradual, y limpieza de inactivos 6+ meses.
- **`ads-server-side-tracking`**: evaluado y descartado como no aplicable (su alcance es medición
  de paid media — sGTM/CAPI/píxeles). En su lugar apliqué sus principios trasladables: tracking
  first-party (dominio de clics propio, redirects `/go/...` en dominio propio) y captura de eventos
  server-side vía webhooks/API de Brevo como fuente de verdad (§4 de `brevo-setup.md`).

## Qué necesito de Jon

1. **Acceso/confirmación del DNS de sensalab.io** (¿qué registrador/panel?) para pegar el bloque de
   `dns-records-sensalab.md`.
2. **¿Dónde vive `hello@sensalab.io`?** (¿Google Workspace?) — define el SPF/DKIM del dominio raíz.
3. **BREVO_API_KEY** (y crear la cuenta si no existe) + decisión de pasar a Starter antes del envío
   a lista completa (quita el branding de Brevo del footer).
4. **Dirección postal física** (calle/PO Box + ZIP) para el footer — requisito CAN-SPAM.
5. **Hosting de la edición web/media** (pendiente según BRIEF): sin URLs absolutas para las
   imágenes no se puede enviar nada.
6. **Luz verde a la estrategia de permiso** (permission pass §0 de `warmup-y-lista.md`) — es la
   decisión con más impacto de todo este documento.
7. Crear las **3 cuentas seed** (Gmail/Outlook/Yahoo) o pasarme accesos si ya existen.

## Orden de ejecución sugerido

DNS (48 h de propagación) → cuenta Brevo + autenticación + remitente → fixes de la auditoría →
mail-tester ≥9/10 → permission pass → semana 0 de warmup → edición #1 por lotes.
