# Estrategia de CTA — Inmersivo (por sección y por formato)

> Especialista 07 · Skills aplicados: `cro` (jerarquía, una acción primaria), `cta-designer` (PVP,
> rotación de secuencia, fricción). Todo el copy pegable está en inglés y en sentence case.

---

## 1. Principio rector

**Una edición = una acción primaria.** El SL-26 dice: *"the pitch converts, connection is the
bottleneck"*. Por lo tanto la conversión que importa NO es un click — es **una respuesta humana**
(reply). Todo lo demás (leer la web, bajar un PDF) son pasos que calientan esa respuesta.

Regla de oro heredada de `cta-designer`: **nunca pedimos calendario en el email**. "Book a call"
no existe en Inmersivo. El book vive solo en la landing, debajo de la opción de reply, para quien
ya decidió.

## 2. El modelo de dos capas (email slim → web)

Cada pieza tiene UN trabajo:

| Pieza | Trabajo | CTA primario | CTA secundario |
|---|---|---|---|
| **Email slim** | llevar el click a NUESTRA web | leer la edición web (hero + tarjetas) | invitation block ("Touch it" → reply) |
| **Edición web** | convertir lectura en conversación | invitation block ("Touch it" → /touch) | suscribirse (visitantes no suscritos) + compartir |

Nota de integración (NO toqué los .py): hoy `signal_email.py` manda el botón del invitation a
`web_url#invitation`. Recomendado: en el **email** ese botón debe ser `mailto:` (ver
`02-touch-it-flow.md`); en la **web** sí va a la página `/touch`. Es un cambio de una línea que
integra Jon.

## 3. Jerarquía de CTAs dentro de cada formato

### Formato The Signal (email slim)

| Posición | Elemento | Acción | Tono |
|---|---|---|---|
| 1 | Tarjetas (field-notes / in-the-lab / craft) — "Steal the playbook →" etc. | click a la web | curiosidad, verbo + objeto específico, ≤4 palabras |
| 2 | Video — "▶ Watch · 01:00" | click a la web | ídem |
| 3 | **Invitation block** (único bloque con botón) | reply / touch | invitación abierta, cero presión |
| 4 | Footer (socials) | ambiente | nunca compite |

Las tarjetas son **la misma acción repetida** (leer la web) con framings distintos — eso está bien
(`cro`: repetir el CTA en puntos de decisión no es competir). El único CTA *distinto* de la
edición es el invitation. Por eso es el único con botón.

### Formato Teardown (email slim)

Igual jerarquía, con un matiz: el Teardown demuestra criterio técnico, así que su invitation
rinde más con un **Resource CTA** (las build notes del caso) que con la pregunta abierta.
Ver rotación abajo.

### Edición web (ambos formatos)

- **Primario:** invitation block al final → `/touch` (el lector ya consumió; es el momento).
- **Secundario:** bloque de suscripción email-only ("One email a week. Unsubscribe anytime.") —
  hoy NO existe en `render_signal.py` / `render_teardown.py`; recomendado agregarlo para
  visitantes que llegan por LinkedIn/compartido. Un solo campo (skill `signup`).
- Los CTAs de tarjeta desaparecen como links salientes: en la web la tarjeta ES el contenido.

## 4. Reglas de copy para CTAs (paleta verbal)

1. Sentence case siempre. Flecha `→` al final de links de texto, nunca en botones.
2. Links de tarjeta: verbo + objeto concreto ("See it fly →", "Inside the dome →"). Prohibido
   "Learn more", "Click here", "Read more" a secas.
3. Botón del invitation: **"Touch it" está reservado para pedir conversación.** Es firma de marca
   (eco del sitio SensaLab). Si el invitation de la semana ofrece un recurso, el botón cambia de
   verbo ("Send me the notes") para no diluir el significado de "Touch it".
4. Siempre una línea de escape sin fricción bajo el botón del email:
   `Or just hit reply — it lands with a human.`
5. Nada de urgencia falsa, contadores, "last chance" (skill `offers`, vocabulario prohibido).

## 5. Banco de invitations PVP (pegables, rotan semana a semana)

Metodología `cta-designer`: cada invitation es una **permissionless value promise** — útil aunque
nunca compren, sin mencionar producto, respondible en una línea.

### V1 — Diagnostic question · 🟢 fricción baja · *default de The Signal*
```json
"invitation": {
  "kicker": "An open invitation",
  "headline": "Have something impossible in mind?",
  "body": "What's the one brief on your desk this quarter that everyone loves and nobody knows how to build? Reply with two lines — we'll tell you what it would actually take.",
  "button": "Touch it"
}
```
**Por qué funciona:** los pone a pensar en SU brief atascado; la respuesta ES la conversación.

### V2 — Resource (build notes) · 🟢 · *default del Teardown*
```json
"invitation": {
  "kicker": "For your next pitch",
  "headline": "Want the build notes?",
  "body": "We wrote up the production anatomy behind this teardown — the pipeline, the gear class, the failure points, and the questions we'd ask before quoting it. Reply with the word notes and we'll send the PDF.",
  "button": "Send me the notes"
}
```
**Por qué funciona:** activo concreto y nombrado (skill `lead-magnets`, M3), cero obligación,
la respuesta de una palabra rompe el hielo.

### V3 — Insight / lista viva · 🟢
```json
"invitation": {
  "kicker": "An open invitation",
  "headline": "We keep a running list of what made people queue this year",
  "body": "Every activation in this newsletter goes into a swipe file — the idea, why it worked, and what it would take to pull off. Reply with the word list and the current cut is yours.",
  "button": "Send me the list"
}
```
**Por qué funciona:** benchmark suave sin datos inventados; "the current cut" da sensación de
documento vivo (guardarriel intacto: solo referencia lo publicado en el propio newsletter).

### V4 — Trigger estacional · 🟡 fricción media
```json
"invitation": {
  "kicker": "Pitch season is close",
  "headline": "Is there a slide in your deck that needs to become real?",
  "body": "If a pitch this fall leans on a real-time moment — a reactive room, a live-data show, a dome — send us that one slide. We'll reply with what it takes to build it, before you promise it.",
  "button": "Touch it"
}
```
**Por qué funciona:** timing real (temporada de pitches), la promesa protege SU pitch — valor
aunque no contraten.

### V5 — The impossible brief review (la oferta, franqueza total) · 🟡 · *máx. 1 de cada 6 ediciones*
```json
"invitation": {
  "kicker": "The impossible brief review",
  "headline": "Send the brief. Get a straight answer in 48 hours.",
  "body": "Once in a while we say this plainly: if a brief needs real-time 3D, projection or AR under your own brand, send it over. Within 48 hours you get a feasibility read — buildable or not, the risks, and the one decision that makes it cheaper. No deck, no pitch, no obligation.",
  "button": "Touch it"
}
```
**Por qué funciona:** es la oferta desnuda (ver `05-offer-framing.md`) pero sigue siendo PVP: el
feasibility read es útil aunque construyan con otro. ⚠️ El SLA de 48 h lo confirma Jon.

## 6. Rotación (regla de secuencia de `cta-designer`: nunca el mismo tipo dos veces seguidas)

Ciclo de 6 ediciones, se repite:

| Edición | Formato probable | Invitation | Acción pedida |
|---|---|---|---|
| n | Signal | V1 diagnostic | reply (2 líneas) |
| n+1 | Teardown | V2 build notes | reply "notes" |
| n+2 | Signal | V3 swipe file | reply "list" |
| n+3 | Teardown | V2 build notes (del nuevo caso) | reply "notes" |
| n+4 | Signal | V4 trigger (si hay temporada) o V1 | reply (1 slide / 2 líneas) |
| n+5 | cualquiera | V5 la oferta directa | reply con el brief |

Si `build_edition.py` cambia el formato de la semana, la invitation sigue la tabla por TIPO, no
por número: Teardown → V2; Signal → la siguiente de {V1, V3, V4} que no se usó la edición pasada.

## 7. Medición (skill `cro`)

- **Métrica norte:** replies por 1.000 entregados (no open rate).
- Email: CTR al sitio web; CTR del invitation por variante (UTM ya existente:
  `utm_content=invitation`); replies etiquetadas por palabra clave (notes / list / brief).
- Web: conversión del invitation → `/touch`; conversión del bloque suscripción.
- Test A/B inicial sugerido (una variable): headline del invitation V1
  ("Have something impossible in mind?" vs "What's the brief nobody knows how to build?").
