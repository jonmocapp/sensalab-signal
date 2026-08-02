# Plan de warmup + política de higiene de lista

Contexto real (SL-26): 118 leads LA (98% con email), 78 agencias scoreadas (29 Strong, 15 Good).
Lista NUEVA y mayormente FRÍA, dominio de envío NUEVO (`news.sensalab.io`) = reputación cero.
Saltarse el warmup es la causa #1 de caer a spam (regla dura del skill).

## 0. El problema del consentimiento (resolver ANTES de la edición 1)

Estos contactos vienen de outbound, no se suscribieron. Eso implica: riesgo de quejas
(el umbral de Gmail es brutal: 0,3% = 1 queja en ~333 envíos; con 118 contactos UNA queja ya es 0,8%)
y riesgo de suspensión en Brevo (sus términos exigen consentimiento y pueden pedir prueba).

**Estrategia recomendada — "permission pass" (semana 0):**
1. Jon envía un email 1:1 real (desde su buzón normal, NO desde Brevo, sin HTML, sin tracking)
   a los 118: dos líneas presentando INMERSIVO + link al formulario de doble opt-in de Brevo.
2. Solo quienes se suscriben o responden entran a la lista INMERSIVO.
3. Resultado: lista más chica pero 100% defendible, quejas ~0, y esos 30–50 engaged son
   exactamente el combustible que el warmup necesita.

**Plan B (si Jon decide enviar sin permission pass):** solo tier Strong con interacción previa real
en la edición 1, línea visible de "por qué recibes esto", unsubscribe prominente, y abortar
(pausar todo) si aparece 1 queja o >2 bounces.

## 1. Calendario de rampa (newsletter semanal, dominio nuevo)

Regla general: nunca crecer más de ~50% de volumen semana a semana; respetar el orden
"más engaged primero".

| Semana | Edición | Destinatarios | Lotes | Quiénes |
|--------|---------|---------------|-------|---------|
| 0 | — | 10–15 | 3–5/día | Solo infra: DNS propagado 48h, mail-tester ≥9/10, tests a seeds propios (Gmail/Outlook/Yahoo) y a 3–5 colegas/amigos que abran y respondan. Nada de prospectos. |
| 1 | #1 | 25–30 | 2 lotes de ~15/día | Los más calientes: respondieron al outbound, warm del pipeline, opt-ins del permission pass. |
| 2 | #2 | 50–60 | ≤30/día | Semana 1 completa + Strong ICP opt-in restantes. |
| 3 | #3 | 90–118 | ≤40/día | Lista completa verificada. |
| 4+ | #4+ | Lista completa | 1–2 lotes | Cadencia semanal normal. |

- Cómo ejecutar los lotes: duplicar la campaña en Brevo con sub-listas por lote y `scheduledAt`
  escalonado (el cap de 300/día del plan gratis nunca se toca).
- **Incorporar listas nuevas** (p. ej. contactos de las 78 agencias scoreadas): siempre verificadas
  primero, en tandas ≤30% del volumen ya activo, mezcladas con la lista engaged — nunca una lista
  fría sola de golpe.
- **Semáforo durante la rampa** (medir 48 h después de cada lote):
  - Bounce >3% → PAUSA, limpiar y re-verificar antes de seguir.
  - Queja ≥1 (a este volumen) → PAUSA, revisar consentimiento del segmento.
  - Clics sanos y cero quejas → siguiente lote según calendario.
- No hace falta herramienta de warmup automatizado (Warmbox/Lemwarm etc.): esas son para cold
  outbound a escala de mailboxes; aquí el volumen es bajo y el pool compartido de Brevo ya está
  caliente. Lo que se calienta es el DOMINIO, con engagement real por lotes.

## 2. Verificación previa (obligatoria antes del primer import)

- Pasar los 118 emails por **ZeroBounce** (100 verificaciones/mes gratis + PAYG) o NeverBounce.
  Con 118 emails el costo es ~2 USD. Importar a Brevo SOLO los `valid`.
- `catch-all/accept_all` → marcar y enviar en último lote, vigilando bounces.
- `invalid`, `disposable`, `role` genéricos (info@, sales@) → fuera.
- Re-verificar toda la lista cada 3 meses (los emails B2B decaen ~25%/año — la gente cambia de
  agencia constantemente en este sector).
- Toda alta futura entra por doble opt-in de Brevo → no necesita verificación manual.

## 3. Política de higiene continua

| Evento | Acción | Cuándo |
|--------|--------|--------|
| Hard bounce | Supresión permanente (Brevo lo hace solo; no re-importar jamás) | Inmediato |
| Soft bounce ×3 consecutivos | Mover a suprimidos | Tras 3ª edición |
| Queja de spam | Supresión permanente + revisar qué segmento era | Inmediato |
| Unsubscribe | Automático vía `{{ unsubscribe }}` / one-click. NUNCA re-importar. Honrar en <48 h también los que respondan "sácame" por email | Inmediato |
| Sin clics ni respuestas en 8 ediciones (~2 meses) | Entra al flujo sunset | Mensual |

**Métrica de engagement = clics + respuestas, NO aperturas** (Apple MPP infla aperturas; los datos
del webhook/API de `brevo-setup.md` §4 son la fuente de verdad).

### Flujo sunset (inactivos)

1. **Edición 8 sin engagement** → el contacto pasa al segmento `dormido`.
2. **Email de re-enganche** (uno solo, tono de la casa, sin descuentos porque no vendemos nada):
   asunto tipo "Should we keep sending this?" + un solo CTA: "Keep me on the list".
3. **Sin clic en 14 días** → suprimir de INMERSIVO (no borrar el contacto: conservarlo marcado
   `sunset` para el CRM; sigue siendo un lead de outbound, solo deja de recibir el newsletter).
4. Efecto: el ratio de engagement de la lista sube → los ISP ven un remitente que la gente lee →
   más inbox para los que sí importan.

## 4. Umbrales de monitoreo permanentes

| Métrica | Objetivo | Acción si se excede |
|---------|----------|---------------------|
| Bounce rate | <2% (tope 3%) | Pausar, limpiar, re-verificar |
| Quejas | <0,1% (tope Gmail 0,3%) | Reducir volumen, revisar segmento/consentimiento |
| Unsubscribe | <1% por edición | Revisar relevancia/frecuencia |
| CTR (proxy de inbox) | Estable o creciente | Si cae >50% de golpe: test de placement (ver checklist) — probable caída a spam |
