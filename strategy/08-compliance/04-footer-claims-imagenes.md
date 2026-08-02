# Revisión legal: footer, claims de la copy e imágenes

Especialista 08 — Compliance, legal & brand safety. Auditado contra sim/edicion-A.json,
sim/edicion-B.json, sim/out/final-A.html, final-B.html, final-email-A/B.html y brand_footer.py.

---

## 1. Footer (brand_footer.py + final-email-*.html:67-71)

| Elemento | Texto actual | Veredicto | Acción |
|---|---|---|---|
| Marca | `SensaLab®` | **[VERIFICAR]** El símbolo ® afirma registro federal en USPTO. Usarlo sin registro es "false marking" — debilita cualquier reclamo de marca futuro y es sancionable. | Jon confirma nº de registro USPTO. Si no existe (o está en trámite): usar `SensaLab™` (™ no requiere registro) en footer web y email. |
| Entidad | `© 2026 SensaLab, Inc. All rights reserved` | **[VERIFICAR]** ", Inc." afirma una corporación constituida con ese nombre exacto. Si la entidad es LLC, o aún no existe, es una representación falsa de forma societaria. | Jon confirma acta de constitución. Alternativas seguras mientras tanto: `© 2026 SensaLab` a secas (el copyright no exige forma societaria). |
| Dirección | `Los Angeles, CA — USA` | **[GAP]** Insuficiente para CAN-SPAM (ver doc 01 §1.4): se exige street address/PO Box/CMRA. | Mailbox CMRA + slot nuevo en `email_footer()`. En el footer **web** no es obligatorio (no es email), puede quedarse como está. |
| Baja | `{{ unsubscribe }}` (solo email) | [OK] Merge tag correcto de Brevo; footer web correctamente sin él. | Mantener; el gate verifica presencia. |
| Contacto | hello@sensalab.io + socials | [OK] Consistente con remitente. | **[VERIFICAR]** que las 3 URLs sociales existen y son de SensaLab (instagram.com/sensalab, linkedin.com/company/sensalab, youtube.com/@sensalab) — apuntar a un handle ajeno u ocupado es riesgo de marca tonto y evitable. |
| Principle | "Rendering Experiences… emotional, immersive and measurable realities" | [OK] Puffery clásico (aspiracional, no verificable, no cuantitativo) — legalmente seguro. "measurable" no promete una medición concreta a nadie. | Ninguna. |
| Falta | Línea de "por qué recibes esto" | Mejora, no requisito: reduce spam complaints. | Añadir sobre el link de baja: `You're getting INMERSIVO because you subscribed at sensalab.io.` |

## 2. Claims de la copy (ediciones A y B)

Metodología (skill `review`): todo claim fáctico debe citar la línea que lo motiva y su fuente,
o se marca. Resultado global: **la copy está bien construida** — cada afirmación externa traza
a `sources[]` (8-9 URLs por edición) y los hedges están donde deben.

Verificado, con evidencia:
- "Spain took the trophy at MetLife on July 19" (edicion-A.json:8) → cbsnews.com en sources:61. OK.
- "2,500-drone show" Michelob / "Home of Soccer" adidas (A:16) → eventmarketer.com sources:54. OK.
- "400-drone scoreboard… billed as a first" (A:25) → visitseattle.org + geekwire sources:56-57.
  El hedge "billed as a first" atribuye el claim de primicia a la fuente, no lo afirma SensaLab.
  Ese patrón es exactamente el correcto — conservarlo como regla de estilo.
- "roughly 40 matches… 87-foot 12K domes" (A:34) → cosm.com + avinteractive sources:58-59. El
  "roughly" hedgea bien. OK.
- "fan festivals at two-million scale" (A:8) → fifa.com sources:55. OK.
- "OpenUSD v26.03 now includes a Gaussian splat schema… 4,000 photos" (B:25) → blog.siggraph.org
  sources:57. OK.
- "comments got switched off" Shrek 5 (B:34,67) → thetab.com sources:60. OK.

Riesgos residuales y reglas:
1. **Teardown de trabajo ajeno (edición B).** Criticar el teaser de Shrek 5 es opinión sobre
   obra creativa pública = fair comment, protegido. Reglas para que siga siéndolo:
   critica la obra, nunca personas nombradas ("the redesign chased clean" ✔; "el director X
   arruinó…" ✘); los hechos que sostienen la opinión (backlash, comments off) siempre con
   fuente; el juicio siempre como lectura de craft, no como acusación de mala fe.
2. **"AI slop" entre comillas citando al internet** (B:34,68) — correcto: es cita de
   sentimiento público, no etiqueta propia de SensaLab contra un estudio. Mantener las comillas.
3. **Marcas de terceros en texto** (FIFA, World Cup, Cosm, Harry Potter, Shrek, Michelob,
   adidas): uso nominativo editorial — legal. Límite: no usar sus **logos**, key art oficial ni
   sugerir asociación ("official", "partner", "in collaboration with" están prohibidos salvo
   contrato). El título "Steal This World Cup" es editorial y claramente no patrocinado; OK,
   pero jamás en un contexto que sugiera que SensaLab participó en la Copa.
4. **Invitación** ("that's the layer we build", B:50) — claim de capacidad presente, no de
   historial: compatible con el guardarriel. Regla: capacidades siempre en presente ("we
   build"), jamás en pasado con beneficiario ("we built for").
5. **No verificado por mí**: la existencia real de los hechos noticiosos (soy gate de forma,
   no de hechos). El detector F1 del gate (números ↔ fuentes) y la disciplina del writer
   (writer.py:73-74) son la defensa. Ningún claim de la copy actual carece de fuente asociada.

## 3. Imágenes — el riesgo más alto de este bloque

**Hallazgo:** `fetch_media.py` descarga como assets los `og:image` de los artículos fuente
(comentario en fetch_media.py:75: "imagenes de secciones + hero (og:image de la fuente)").
El inventario actual (sim/out/media/manifest.json) incluye material casi seguro protegido:
- `B-hero.webp` / `B-field-notes.webp` — Harry Potter en Cosm (personajes y fotografía de
  Warner Bros. / material de prensa de Cosm).
- `B-craft.jpg` — frame del teaser de Shrek 5 (DreamWorks/Universal).
- `A-video.jpg` — still de Fox 13 Seattle; `A-*.jpg` — fotos editoriales de Event Marketer /
  Visit Seattle / Cosm.

Por qué es un problema real:
- Un newsletter comercial B2B **no** es uso editorial de prensa: es marketing de SensaLab.
  Reproducir y redistribuir (email + hosting en sensalab.io) fotos ajenas sin licencia es
  infracción directa de copyright. Para obras registradas en US, daños estatutarios de $750 a
  $30,000 por obra (hasta $150,000 si es dolosa), más el escenario realista: DMCA takedown o
  demand letter de Getty/AP/estudio — caro, público y en el peor momento.
- El argumento de fair use es débil: uso comercial, obra creativa, imagen completa, y
  sustituye al mercado de licencias. El teardown (comentario/crítica) da algo de cobertura a
  UN frame del teaser criticado, pero no a heros decorativos de Harry Potter.
- Riesgo agravado por marca: SensaLab vende craft visual; ser cazado usando imágenes ajenas
  es daño reputacional directo a la tesis del producto.

**Recomendación (en orden):**
1. **Assets propios como default.** Composiciones generadas/propias de SensaLab con la
   estética de marca para heros y secciones. Ventaja doble: cero riesgo + el newsletter LUCE
   SensaLab en vez de lucir como un clipping de prensa. Nunca generar personajes protegidos
   con IA (un Shrek "generado" sigue siendo obra derivada infractora).
2. **Press kits con términos explícitos.** Cosm, FIFA media portal, marcas: si el kit dice
   "for editorial/media use", documentar la URL de términos + fecha en manifest.json. Nota
   honesta: "media use" suele cubrir prensa, no marketing de terceros — leer los términos,
   no asumirlos.
3. **Screenshots mínimos SOLO en teardowns**: un frame reducido del material específicamente
   criticado, con crédito, dentro del análisis — el caso más defendible de fair use. No como
   hero, no decorativo.
4. **Tipografía como imagen.** Donde no haya asset legal, tarjeta tipográfica con el
   statement de la sección (el formato Signal ya vive de statements — sim/edicion-A.json
   trae `statement` por sección). Cero riesgo, on-brand.
5. **Linkear nunca es infringir**: el link al video de Fox/YouTube está bien; el problema es
   copiar el still como poster. Poster propio + link fuera.

**Cambio de proceso:** `manifest.json` debe crecer un campo `license` por asset
(`own | licensed:<url-términos> | press-kit:<url> | fair-use-teardown`). El gate de pre-envío
(doc 03) bloquea si algún asset referenciado en el HTML final carece de valor en `license`.
La edición #05/#06 **no debe salir con las imágenes actuales**.
