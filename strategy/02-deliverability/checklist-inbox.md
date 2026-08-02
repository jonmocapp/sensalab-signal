# Checklist de inbox placement + herramientas

## A. Una sola vez (antes de la edición #1)

- [ ] DNS: SPF, DKIM (b1/b2), DMARC `p=none` publicados y verdes en Brevo (ver `dns-records-sensalab.md`)
- [ ] MXToolbox: SPF pass / DKIM pass / DMARC pass / 0 blacklists (dominio y subdominio)
- [ ] Remitente `hello@news.sensalab.io` verificado en Brevo; el buzón existe (alias/forward) y NO rebota
- [ ] Reply-to `hello@sensalab.io` probado (responder a un test y confirmar que llega a Jon)
- [ ] mail-tester.com con el email real (imágenes absolutas incluidas): **≥ 9/10**
- [ ] Google Postmaster Tools: `sensalab.io` y `news.sensalab.io` verificados (dashboard de
      reputación de dominio y tasa de spam en Gmail — el ICP de agencias vive mucho en Workspace)
- [ ] DMARC digest activo (alias `dmarc@sensalab.io` o digest semanal gratis de Postmark)
- [ ] 3 cuentas seed propias creadas: Gmail, Outlook.com, Yahoo
- [ ] Lista verificada con ZeroBounce/NeverBounce; solo `valid` importados
- [ ] Estrategia de consentimiento ejecutada (permission pass — `warmup-y-lista.md` §0)
- [ ] Los 6 bloqueos de `auditoria-spam.md` cerrados

## B. Antes de CADA edición (5 minutos)

- [ ] `sendTest` a las 3 seeds → ¿inbox, promotions o spam? (en Gmail, Promotions es aceptable
      para un newsletter; spam no)
- [ ] Render OK en Outlook de escritorio (la seed de Outlook.com + un vistazo con imágenes
      bloqueadas: ¿se entiende el email solo con texto y alts?)
- [ ] Asunto <60 caracteres, sentence case, sin palabras de urgencia/venta
- [ ] Preheader presente y distinto del asunto
- [ ] Todos los links probados; todos a `sensalab.io` (externos vía `/go/...`); UTM correctos
- [ ] Unsubscribe visible y resolviendo (probar en el test: el link del footer debe abrir la
      página de baja de Brevo)
- [ ] Peso: HTML <102 KB; imágenes totales <500 KB
- [ ] Versión texto plano generada
- [ ] Lote según calendario de warmup (semanas 1–3) o lista completa (semana 4+)

## C. 48 h después de cada edición

- [ ] API `GET /v3/emailCampaigns/{id}?statistics=globalStats` → registrar delivered, clicks,
      bounces, unsubs, complaints
- [ ] Semáforo: bounce <3% · quejas 0 · unsub <1% — cualquier rojo pausa la rampa
- [ ] Postmaster Tools: spam rate <0,1% (nunca acercarse a 0,3%) y reputación de dominio ≥ "Medium"
- [ ] Respuestas en `hello@sensalab.io` contestadas <24 h (las respuestas son ORO para reputación:
      señal de conversación real, no bulk)

## D. Mensual

- [ ] Blacklist check: MXToolbox + multirbl.valli.org para `sensalab.io`, `news.sensalab.io` y
      las IP que muestre el header de un email real
- [ ] Reporte DMARC revisado: ¿algún remitente no autorizado usando el dominio?
- [ ] Segmento `dormido` procesado (flujo sunset de `warmup-y-lista.md` §3)
- [ ] Trimestral: re-verificar toda la lista (decay ~25%/año)
- [ ] Cuando DMARC lleve 4+ semanas limpio: subir `p=none` → `quarantine` → (4 semanas más) `reject`

## Herramientas — cuál, para qué, costo

| Herramienta | Para qué | Costo | Cuándo |
|-------------|----------|-------|--------|
| mail-tester.com | Score integral (auth + contenido + listas negras) | Gratis (3/día) | Setup + cuando cambie la plantilla |
| MXToolbox | Validar DNS y blacklists | Gratis | Setup + mensual |
| Google Postmaster Tools | Reputación de dominio y spam rate EN Gmail (dato real, no estimado) | Gratis | Continuo |
| GlockApps | Placement por ISP con lista seed grande (inbox/spam/promotions por proveedor) | Trial gratis; ~$85/mes después | Solo si las seeds propias muestran problemas o antes de escalar la lista fuerte |
| ZeroBounce | Verificación de lista + placement test (1 gratis/mes) + monitor de blacklist | 100 verificaciones/mes gratis | Setup + trimestral |
| Postmark DMARC digest | Reporte DMARC semanal legible por humanos | Gratis | Continuo |
| multirbl.valli.org | Chequeo masivo de blacklists | Gratis | Mensual |
| Seeds propias (Gmail/Outlook/Yahoo) | La prueba más honesta y rápida de placement | Gratis | Cada edición |

Nota del skill (aprendida de Instantly, aplica en general): **no confiar en scores sintéticos de
warmup/reputación — la verdad es dónde cae el email en cuentas reales**. Por eso el ritual de
seeds en cada edición es innegociable.

## Diagnóstico rápido si algo se rompe

| Síntoma | Causa probable | Primer paso |
|---------|----------------|-------------|
| Seeds en spam en Gmail | Auth rota o reputación de dominio | mail-tester + Postmaster Tools; verificar DKIM sigue `pass` |
| Seeds en spam solo en Outlook | Contenido/imágenes (Outlook es el más duro) | Revisar pesos, alts, versión texto |
| CTR cae >50% de golpe | Caída a spam silenciosa | Placement test (ZeroBounce/GlockApps) + blacklist check |
| Bounces suben | Lista envejecida | Pausar, re-verificar lista completa |
| Brevo pide prueba de opt-in | Queja de un contacto frío | Responder con el registro del permission pass / doble opt-in |
