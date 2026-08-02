# Setup de Brevo para INMERSIVO (envío por API)

Estado según BRIEF: plan gratis de Brevo elegido como ESP; falta `BREVO_API_KEY`.
Volumen real: ~118 leads hoy, semanal, creciendo hacia unos cientos. El plan gratis
(300 emails/día, contactos ilimitados, precio por volumen no por contactos) sobra para 2026.

## 1. Orden exacto de setup (una sola vez)

1. **Cuenta**: crear/entrar con `hello@sensalab.io`. Completar el perfil de empresa completo
   (SensaLab, Inc., Los Angeles) — cuentas incompletas disparan la revisión antifraude de Brevo.
2. **Autenticar dominio**: Settings → *Senders, domains & dedicated IPs* → *Domains* →
   `news.sensalab.io` → pegar los registros de `dns-records-sensalab.md` (Brevo ofrece Entri para
   configurarlo automático si el DNS está en un registrador compatible; manual también sirve).
3. **Remitente verificado**: Settings → *Senders* → añadir:
   - From: `Inmersivo by SensaLab <hello@news.sensalab.io>` (sentence case, regla de marca)
   - Reply-to: `hello@sensalab.io` — las respuestas ("Reply." es el CTA de la edición B) caen en el
     buzón real de Jon. Crear el alias `hello@news.sensalab.io` o un forward para que exista el buzón
     (los ISP penalizan remitentes que rebotan).
4. **API key**: Settings → *SMTP & API* → *API keys* → generar → guardar como variable de entorno
   `BREVO_API_KEY` (nunca en el repo).
5. **Lista y atributos**: crear lista `INMERSIVO` + atributos `FIRSTNAME`, `COMPANY`, `ROLE`,
   `ICP_TIER` (Strong/Good — viene del SL-26). Importar SOLO contactos verificados
   (ver `warmup-y-lista.md`).
6. **Doble opt-in para altas nuevas**: crear el formulario de suscripción de Brevo con
   confirmación — todo suscriptor futuro entra con consentimiento probado.

## 2. Dedicated IP vs shared IP — decisión para este volumen

**Shared IP. Rotundo.**

- Una IP dedicada solo se recomienda a partir de **~50.000 emails/mes sostenidos** (regla del skill
  y de la propia Brevo). INMERSIVO enviará ~500–2.000/mes.
- Con volumen bajo una IP dedicada es CONTRAPRODUCENTE: no genera tráfico suficiente para
  mantenerse "caliente" y su reputación se degrada sola.
- En el pool compartido, Brevo gestiona la reputación de la IP; la tuya se juega a nivel de
  DOMINIO (por eso DKIM/DMARC alineados importan tanto).
- Revisar la decisión solo si algún día se superan 50k/mes consistentes; entonces: IP dedicada
  asociada exclusivamente al subdominio `news.sensalab.io` + warmup de IP de 4–6 semanas.

## 3. Cómo enviar: API de CAMPAÑAS, no la transaccional

Regla: el newsletter se envía como **campaña** (`POST /v3/emailCampaigns`), NO por
`POST /v3/smtp/email` (transaccional). Motivos de deliverability:

- Las campañas inyectan automáticamente `List-Unsubscribe` + `List-Unsubscribe-Post` (one-click,
  RFC 8058) que Gmail/Yahoo exigen a los bulk senders — por la vía transaccional habría que
  construirlo a mano.
- El tag `{{ unsubscribe }}` que ya está en `final-email-*.html` **solo se resuelve en campañas**.
  Enviado como transaccional saldría el placeholder literal → reporte de spam instantáneo.
- Separación de reputación marketing/transaccional dentro de Brevo.

### Crear campaña (PowerShell, ejecutable)

```powershell
$body = @{
  name        = "INMERSIVO 05 - The Signal"
  subject     = "The best of the World Cup happened outside the stadiums"
  previewText = "Fan festivals at two-million scale, a drone scoreboard, dome watch parties."
  sender      = @{ name = "Inmersivo by SensaLab"; email = "hello@news.sensalab.io" }
  replyTo     = "hello@sensalab.io"
  htmlContent = (Get-Content "C:\Dev\SensaLab-Newsletter-Bot\sim\out\final-email-A.html" -Raw)
  recipients  = @{ listIds = @(2) }   # id real de la lista INMERSIVO
  inlineImageActivation = $false       # imágenes SIEMPRE hosteadas, nunca adjuntas/inline
} | ConvertTo-Json -Depth 6

Invoke-RestMethod -Method Post -Uri "https://api.brevo.com/v3/emailCampaigns" `
  -Headers @{ "api-key" = $env:BREVO_API_KEY; "accept" = "application/json" } `
  -ContentType "application/json" -Body $body
```

### Test a seeds antes de cada envío real

```powershell
Invoke-RestMethod -Method Post -Uri "https://api.brevo.com/v3/emailCampaigns/{id}/sendTest" `
  -Headers @{ "api-key" = $env:BREVO_API_KEY } -ContentType "application/json" `
  -Body (@{ emailTo = @("seed.gmail@gmail.com","seed.outlook@outlook.com","seed.yahoo@yahoo.com") } | ConvertTo-Json)
```

### Enviar / programar

```powershell
# ahora:
Invoke-RestMethod -Method Post -Uri "https://api.brevo.com/v3/emailCampaigns/{id}/sendNow" -Headers @{ "api-key" = $env:BREVO_API_KEY }
# programado (para los lotes del warmup):
# PUT /v3/emailCampaigns/{id} con "scheduledAt": "2026-08-04T17:00:00.000Z"
```

## 4. Tracking server-side (sin depender del pixel de apertura)

Apple Mail Privacy Protection infla las aperturas — la verdad operativa son **clics, respuestas y
quejas**. Dos niveles, de simple a completo:

1. **Hoy (sin servidor):** tirar de estadísticas por API después de cada edición y guardarlas
   (el motor ya es determinista; esto es solo lectura, no toca los .py):
   ```powershell
   Invoke-RestMethod -Uri "https://api.brevo.com/v3/emailCampaigns/{id}?statistics=globalStats" `
     -Headers @{ "api-key" = $env:BREVO_API_KEY }
   ```
   Registrar por edición: delivered, uniqueClicks, hardBounces, softBounces, unsubscriptions, complaints.
2. **Cuando exista hosting web:** webhook de Brevo (Settings → Webhooks → marketing events:
   `delivered`, `click`, `hardBounce`, `softBounce`, `spam`, `unsubscribed`) apuntando a un endpoint
   propio → base de engagement first-party por contacto. Eso alimenta la política de sunset
   (ver `warmup-y-lista.md`) con datos reales en vez de aperturas fantasma.
3. Los UTM ya presentes en los links (`utm_source=inmersivo&utm_medium=email&utm_campaign=signal-XX`)
   están bien construidos — mantenerlos idénticos en todas las ediciones para series limpias en
   analytics del sitio.

## 5. Límites y letra chica del plan gratis

- **300 emails/día**: suficiente e incluso útil — fuerza los lotes del warmup.
- **Branding de Brevo en el footer** de campañas en plan gratis. Para quitarlo: plan Starter
  (el tier pago más bajo). Recomendación: arrancar el warmup en gratis y pasar a Starter antes del
  envío a lista completa — el logo de un ESP gratuito resta señal de remitente serio ante un
  VP Innovation de Sony.
- Brevo **exige consentimiento** en sus términos para email marketing y puede pedir prueba de
  opt-in si llegan quejas. Con lista fría de outbound: seguir la estrategia de permiso de
  `warmup-y-lista.md` al pie de la letra — una cuenta suspendida en la semana 2 cuesta más que
  cualquier atajo.
