# Go-live checklist — INMERSIVO #1 (definitivo)

Regla: **NO-GO mientras cualquier casilla A-D esté abierta.** E es deseable, no bloqueante.
Responsable: **[Jon]** = acción humana · **[motor]** = fix de código (integra tras GREEN LIGHT).

## A. Contenido y render — bloqueante
- [ ] **[motor]** P0-1: imágenes del email con URL absoluta hospedada.
      Aceptación: `grep 'src="media/' final-email-*.html` = 0 y draft de Brevo muestra todas las imágenes.
- [ ] **[motor]** P0-2: cero `.webp` en emails (transcodificar a JPG/PNG).
- [ ] **[motor]** P1-1: anclas `id="field-notes|in-the-lab|craft|invitation"` en la web; cada
      fragmento del email aterriza en su sección.
- [ ] **[Jon+motor]** P1-2: link de video real (nunca `youtube.com/results`), copy↔link coherentes.
- [ ] **[Jon]** P1-3 decisión: clic de video → nuestra web con ancla (recomendado) o tercero con UTM.
- [ ] **[motor]** alt descriptivo en todas las imágenes del email.
- [ ] **[Jon]** fact-check de cifras contra `sources[]` de la edición (10 min por edición).
- [ ] **[Jon]** pasada final de marca: sentence case, paleta, tono; scan Cinética/fundador = 0.
- [ ] **[Jon]** ⚠️ DERECHOS DE IMÁGENES: las ediciones #05/#06 usan Harry Potter/Cosm (Warner),
      frame de Shrek 5 y still de Fox — uso comercial sin licencia. NO enviar con esas imágenes;
      reemplazar por assets propios/licenciados antes del primer envío.

## B. Deliverability — bloqueante
- [ ] **[Jon]** SPF + DKIM + DMARC de sensalab.io autenticados en Brevo (subdominio news.sensalab.io).
      Aceptación: dominio "verificado" en Brevo y mail-tester.com ≥ 9/10.
- [ ] **[Jon]** From = hello@sensalab.io sobre dominio autenticado (nunca gmail).
- [ ] **[Jon]** ⚠️ Base de consentimiento de la lista. Los 118 leads de outbound son LISTA FRÍA:
      los ToS de Brevo exigen opt-in — importarlos en masa arriesga suspensión de la cuenta.
      Recomendado: sembrar con opt-ins reales (firma, LinkedIn, la web) y usar el newsletter como
      CTA en el outbound 1:1, no como import.
- [ ] **[Jon]** Primer envío a lista pequeña (≤50). Aceptación: bounces <2%, quejas <0.1%.
- [ ] **[Jon]** Test de inbox real con draft: Gmail web+app, Outlook desktop+web, Apple Mail,
      cada uno en dark mode. Aceptación: sin imágenes rotas, sin clipping, layout íntegro.
- [ ] **[motor]** Versión texto plano (`textContent`) en el payload.

## C. Legal — bloqueante
- [ ] **[Jon→motor]** Dirección postal física (calle o PO Box/CMRA) en el footer del email (CAN-SPAM).
- [ ] **[motor]** ⚠️ Gate non-compete real: `scan_forbidden` lee el esquema VIEJO y nunca se llama
      desde build_edition — hoy el guardarriel NO está activo en los formatos nuevos. Reconectar
      (escanear hero/sections/teardown) y bloquear envío si hay hit, antes de subir draft.
- [ ] **[Jon]** Verificar en el draft que `{{ unsubscribe }}` es link funcional (sintaxis de
      CAMPAÑAS Brevo — correcto; ya presente en ambos emails).
- [ ] **[Jon]** Click de unsubscribe probado de punta a punta.
- [ ] **[Jon]** Verificar marca: "SensaLab®" (¿registro USPTO? si no → ™) y "SensaLab, Inc."
      (¿constituida? si no → "© 2026 SensaLab").
- [ ] **[auto]** Scan de guardarriel = 0 hallazgos (correr por edición).

## D. Web y tracking — bloqueante
- [ ] **[Jon]** Edición web publicada en `sensalab.io/inmersivo/NN` ANTES del envío (hoy 404).
- [ ] **[Jon]** Analytics en la web (GA4 o Plausible) leyendo los UTM.
- [ ] **[motor]** Unificar `utm_campaign` (tracking.py dice `issue-N`, signal_email dice `signal-N`).
- [ ] **[Jon]** Verificar que el click-tracking de Brevo preserva los `#fragments`.
- [ ] **[Jon]** KPI del #1 definidos: CTR al sitio (>2.5%), replies, unsubscribes <0.5%.

## E. Infra y motor — muy recomendado (no bloquea el #1 si el envío es manual)
- [ ] **[Jon]** GitHub Secrets: BREVO_API_KEY, BREVO_LIST_ID, ANTHROPIC_API_KEY, FROM_*, COMPANY_ADDRESS.
- [ ] **[Jon]** `SEND_MODE=draft` las primeras 2 ediciones; humano aprieta enviar en Brevo.
- [ ] **[auto]** `sender.preflight()` devuelve `[]` antes de cada envío.
- [ ] **[motor]** Validador de esquema de edición (evita KeyError 'hero' / crash de date en el cron).
- [ ] **[motor]** Integrar `build_edition.compose()` al pipeline (hoy solo corre en simulación).
- [ ] **[motor]** Talkability con word-boundaries + override `edition["format"]`.
- [ ] **[motor]** Corregir SIGGRAPH en calendar_events.py (era ago; real jul 19–23).
- [ ] **[motor]** Compresión de imágenes ≤200KB c/u antes de hospedar.

## Gate final
GO cuando A, B, C y D estén 100% ✅. El draft del envío #1 lo aprueba Jon a ojo en los 3
clientes + dark mode. Primera medición a 72h: si CTR <1% o quejas >0.1%, pausar y revisar.
