# 10-qa — QA, red-team & go-live (especialista 10)

## Qué entregué
- `reporte-qa-redteam.md` — auditoría priorizada (P0→P3) de rendering, marca, legal y motor,
  con evidencia archivo:línea verificada por ejecución.
- `go-live-checklist.md` — checklist definitivo con criterios de aceptación y responsable
  (Jon vs motor) para el primer envío real.

## Skills usados
`qa` (modo solo-reporte), `verification-before-completion` (cada hallazgo se verificó
ejecutando greps/md5/harness de edge-cases contra el motor real), `review`, `security-reviewer`.

## Veredicto
**NO-GO hoy.** Bloquean: imágenes con ruta relativa en el email (rotas en todo cliente),
WebP en email B (roto en Outlook), anclas muertas email→web, video de la edición B que
linkea a una búsqueda de YouTube, y clics de video que se fugan a terceros sin UTM.
Todo lo demás es P2/P3. Lo estructural (escape, paleta, sentence case, guardarriel legal,
peso <102KB) está PASS con evidencia.

## Decisiones clave
1. Auditoría 100% report-only: cero ediciones al motor y al repo (regla 1 del BRIEF).
2. Verifiqué dinámicamente (corrí el motor con entradas rotas desde un harness externo):
   crashes sin `hero`, crash con `date` string, `<img src="">` con media faltante,
   talkability disparable con UNA frase ("called it fake" = 2 por doble conteo de substrings).
3. El pipeline automatizado (`newsletter.yml` → `newsletter_bot.py`) aún NO invoca
   `build_edition.compose()`: los crashes P2 se vuelven "el lunes no salió el newsletter"
   en cuanto se integre — el validador de esquema debe entrar junto con la integración.

## Qué necesito de Jon
1. **Hosting**: publicar la edición web en `sensalab.io/inmersivo/NN` y las imágenes en URL
   pública (hoy los links del email dan 404 y las imágenes son rutas relativas).
2. **Dirección postal física** (CAN-SPAM) para el footer del email.
3. **Decisión de lista**: los 118 leads de outbound son lista fría; Brevo exige opt-in en sus
   ToS — riesgo real de suspensión de cuenta. Ver sección C del checklist.
4. **Keys**: BREVO_API_KEY, BREVO_LIST_ID, ANTHROPIC_API_KEY en GitHub Secrets;
   SEND_MODE=draft para las primeras 2 ediciones.
5. **Decisión de producto**: ¿los clics de video van a nuestra web con ancla o al tercero
   con UTM? (P1-3 del reporte).
