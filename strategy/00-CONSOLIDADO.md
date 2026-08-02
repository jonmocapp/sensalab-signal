# INMERSIVO — Plan de operación consolidado
### Síntesis de los 10 especialistas B2B (2026-07-27)

Este documento une los 10 frentes en UNA hoja de ruta. Detalle en cada carpeta `strategy/NN-*/`.

---

## 1. Qué es la operación
Newsletter semanal B2B de SensaLab que ataca el cuello de botella de ventas (**"the pitch
converts, connection is the bottleneck"**): estar top-of-mind con productores de agencia y
marcas hasta que necesiten la capa técnica white-label.
- **2 formatos, el motor elige** (AI sin AI): **The Signal** (hábito, suscriptor→warm) ·
  **Teardown** (autoridad, warm→conversación; sustituye al case study y esquiva el non-compete).
- **North-star: WEIR** — weekly engaged ICP readers (ICP con ≥1 interacción en 4 ediciones).
- **Modelo de conversión: el REPLY** (siempre humano, ≤24h). CTA "Touch it" = pedir un brief,
  nunca "book a call". Web pública = destino; email slim = vehículo con UTM.
- **Lista de francotirador** (~200–300 ICP opt-in), NO los 118 en frío. Cadencia semanal fija.

## 2. El GATE de go-live (del QA) — hoy NO-GO, camino claro
Lo estructural PASA (paleta, sentence case, copy legal, peso <102KB). Bloqueadores por orden:

**Rojos (nadie envía sin esto):**
1. 🔴 Guardarriel legal INACTIVO — `scan_forbidden` lee esquema viejo y nunca se llama. `[motor]`
2. 🔴 Derechos de imágenes — HP/Cosm/Shrek/Fox sin licencia; #05/#06 no salen así. `[Jon: assets]`
3. 🔴 Email técnico — imágenes con ruta relativa (rotas), `.webp` en Outlook, anclas muertas,
   video B copy↔link incoherente. `[motor]`

**Naranjas (antes de escalar):** dirección postal CAN-SPAM, versión texto-plano, alt, dark mode,
UTM unificado (issue-N vs signal-N), crashes por esquema (hero/date), talkability con
word-boundaries, SIGGRAPH mal en calendar_events.py, imágenes ≤200KB.

## 3. Backlog de INTEGRACIÓN (código — lo hace Opus con GREEN LIGHT)
**ESTADO 2026-07-27: I1–I12 INTEGRADOS y verificados (101/101 tests verdes). Motor único = `build_edition.compose()` con gate fail-closed. Falta lo humano (§4).**

| # | Fix | Estado | Archivos |
|---|---|---|---|
| I1 | Gate non-compete reconectado al esquema nuevo + llamado en compose (fail-closed) | ✅ `guard.py` (79 términos) verificado: bloquea "Cinética" | guard.py, build_edition |
| I2 | `img_base` para imágenes absolutas + `logo` expuesto en compose | ✅ logo pasa por `_img(logo,img_base)` en los 3 renderers | signal_email, build_edition, render_* |
| I3 | `.webp`→JPG para email + comprimir ≤200KB | ✅ 0 webp; todo ≤200KB | media/ (script PIL) |
| I4 | Anclas `id=` en secciones web (email→sección) | ✅ signal: 5 anclas; teardown: #invitation | render_signal, render_teardown |
| I5 | Unificar UTM a `utm_campaign=issue-<n>` | ✅ signal_email alineado a tracking.py | tracking, signal_email |
| I6 | `alt` descriptivo en imágenes | ✅ signal + teardown case img | render_signal, render_teardown |
| I7 | Validador de esquema de edición | ✅ `validate()` en compose; aborta claro | build_edition |
| I8 | Talkability `\b` + distinct + override `edition["format"]` | ✅ B=5 → teardown, A=0 → signal | build_edition |
| I9 | Subject/edición en inglés (writer.py decía "en espanol") | ✅ prompt v1 → inglés + sentence case | writer |
| I10 | Corregir SIGGRAPH | ✅ **19–23 jul, LA** (fuente oficial s2026.siggraph.org); estaba en 9–13 ago. Adobe MAX: no existe entrada (no se inventó) | calendar_events |
| I11 | Dirección postal + label format-aware | ✅ email dice "Teardown"/"The Signal"; `legal_address` default corregido. **Falta la dirección postal real de Jon** | brand_footer, signal_email |
| I12 | Cablear `compose()` al pipeline + pausar v1 | ✅ `run_weekly.py` usa compose (gate fuerte fail-closed, no el débil de 2 términos) | run_weekly |

## 4. Lista de acción de JON (bloqueadores humanos) — por orden
1. **Keys/infra:** BREVO_API_KEY + BREVO_LIST_ID + ANTHROPIC_API_KEY (GitHub Secrets).
2. **DNS + remitente:** autenticar `news.sensalab.io` en Brevo (SPF/DKIM/DMARC) + buzón `hello@`.
3. **Hosting:** repo público `sensalab-signal` + Pages + CNAME `signal.sensalab.io` (guía en 09-ops).
4. **Imágenes propias/licenciadas** para reemplazar las de terceros.
5. **Dirección postal física** (PO Box/CMRA) para el footer.
6. **Decisión de lista:** opt-in 1:1 (29 Strong primero), nunca importar los 118.
7. **Compromiso operativo:** ~30 min/lunes + contestar replies ≤24h.
8. **Verificar marca:** "SensaLab®" (¿USPTO? si no ™) y "SensaLab, Inc." (¿constituida?).

## 5. Secuencia sugerida a primer envío
1. Opus integra I1–I12 (con green light) → `SEND_MODE=file`, todo verde en QA.
2. Jon: keys + DNS + hosting + imágenes propias + dirección.
3. Sembrar lista opt-in (wave 1: 21 warm+ con invitación 1:1; ver 04-icp-lista).
4. Generar edición real → `SEND_MODE=draft` → test de inbox (Gmail/Outlook/Apple + dark).
5. Envío #1 a ≤50, aprobado a ojo por Jon. Medir a 72h (CTR, quejas).
6. Graduar a `send` + activar cron (pausando el v1).
