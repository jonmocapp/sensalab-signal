# Reporte QA + red-team — INMERSIVO (especialista 10)

Fecha: 2026-07-27 · Alcance: `build_edition.py`, `render_signal.py`, `render_teardown.py`,
`signal_email.py`, `brand_footer.py`, `sim/out/final-{A,B}.html`, `sim/out/final-email-{A,B}.html`
+ infra (`sender.py`, `.github/workflows/newsletter.yml`) como contexto. **Solo auditoría.**

Método: lectura completa + verificación ejecutada (greps sobre salidas reales, md5 de media,
harness de edge-cases que corrió el motor con entradas rotas). Prioridades: **P0** bloquea el
primer envío · **P1** lo daña · **P2** arreglar pronto · **P3** pulido.

Conteo: **2 P0 · 3 P1 · 9 P2 · 10 P3 · 7 PASS verificados.**

---

## P0 — bloquean el primer envío

### P0-1 · Imágenes del email con ruta relativa `media/...` → rotas en TODOS los clientes
- Evidencia: `final-email-A.html:12,24,33,42,52` (`src="media/..."`). Origen:
  `signal_email.py:28-31` (`_img`) y `:61` (default `logo="media/sensalab-logo.png"`),
  generado con `img_base=""`.
- Impacto: en el inbox no existe `media/`; Gmail/Outlook/Apple muestran 5 cuadros rotos.
- Fix (motor+Jon): hospedar `sim/out/media/*` en URL pública y generar con
  `compose(..., img_base="https://sensalab.io/inmersivo/media/")` + logo absoluto.
  Aceptación: `grep 'src="media/' final-email-*.html` = 0.

### P0-2 · WebP en el email B → imagen rota en Outlook de escritorio
- Evidencia: `final-email-B.html:24` usa `B-field-notes.webp` (`manifest.json:17`).
  El motor Word de Outlook no renderiza WebP.
- Fix (motor): transcodificar a JPG/PNG todo lo que entre al email (WebP solo web).
  Aceptación: cero `.webp` en `final-email-*.html`.

## P1 — integridad de links y promesa del modelo

### P1-1 · Las 4 anclas de cada email apuntan a IDs que NO existen en la web
- Evidencia: `signal_email.py:22-26` añade `#field-notes/#in-the-lab/#craft/#invitation`;
  verificado `grep -c 'id="' final-A.html final-B.html` = **0 y 0**; los fragmentos están en
  `final-email-A.html:28,37,46,62`.
- Impacto: cada clic aterriza arriba de la página; se pierde la continuidad email→sección.
- Fix (motor): `render_signal._card` → `<div class="card" id="{role}">`, invite →
  `id="invitation"`; equivalentes en `render_teardown`. Aceptación: cada fragmento tiene su `id=`.

### P1-2 · Email B: la copy del video promete splats, el link va a una BÚSQUEDA de YouTube del Shrek
- Evidencia: `final-email-B.html:53-55` — "Watch a room become a splat" + "▶ Watch · 01:00"
  con href `youtube.com/results?search_query=Shrek+5...` (`manifest.json:23`). Causa: el email
  usa `edition["video"]` (splats, `edicion-B.json:40-45`) pero link/poster salen de
  `media["video"]` (Shrek). La web teardown sí es coherente (`render_teardown.py:63`).
- Fix (motor+Jon): validar coherencia edition.video ↔ media.video en `compose()`; rechazar
  URLs `youtube.com/results` como link de video en preflight.

### P1-3 · Los clics de video se fugan a terceros sin UTM, contra el modelo "el clic va a NUESTRO sitio"
- Evidencia: `final-email-A.html:52,55` → fox13seattle.com directo; `signal_email.py:72,75`
  usa `vm.get('link')` crudo sin `_url()`. BRIEF fija el modelo del clic a nuestra web.
- Fix (decisión Jon + motor): video en la edición web con ancla `#video` y el email linkea ahí
  con UTM, o al menos envolver el link externo con UTM.

## P2 — arreglar antes de escalar

1. **`alt=""` vacío en todas las imágenes del email** (`signal_email.py:30`). Con imágenes
   bloqueadas (default Gmail para remitentes nuevos) el email queda casi vacío; falla a11y.
   Fix: alt descriptivo (del `statement`) + bgcolor de respaldo.
2. **Dark mode sin blindaje** (`signal_email.py:79`): solo `color-scheme: light`; falta
   `supported-color-schemes`; Gmail Android/Outlook dark invierten igual. Fix: ambas metas +
   logo dark-safe + matriz de pruebas.
3. **Sin versión texto plano** (`sender.py:31` solo `htmlContent`). Fix: generar `textContent`.
4. **CAN-SPAM: falta dirección postal física** (`brand_footer.py:10` solo "Los Angeles, CA —
   USA"; `COMPANY_ADDRESS` de `.env.example:35` nunca se renderiza). Fix: línea de dirección
   en `email_footer()`; Jon provee PO Box.
5. **Crash con edición sin `hero`** — verificado: `KeyError: 'hero'` (`render_signal.py:65`,
   `signal_email.py:63`). Sin validación de esquema, el cron del lunes muere. Fix: validador.
6. **Crash si `date` es string** — verificado: `AttributeError` en `signal_email.py:65`.
   Nota: `build_signal` recibe `date` y nunca lo usa (parámetro muerto).
7. **Rol de media faltante → `<img src="">` en la web** — verificado: 3 src vacíos en signal,
   2 en teardown (`render_signal.py:54`, `render_teardown.py:99`). Fix: omitir img o placeholder.
8. **Talkability con falsos positivos** — verificado: UNA frase "They called it fake" da
   talkability=2 (substring cuenta "fake" + "called it fake") y dispara Teardown; `"mock"`
   matchea "mockup", `"fake"` matchea "fakery" (`build_edition.py:15-18,28`). Fix:
   word-boundaries + dedupe de keywords solapados + override explícito `edition["format"]`.
9. **Peso de imágenes edición A ≈1.8MB** (`A-in-the-lab.jpg` 896KB, `A-hero/video.jpg` 584KB).
   Comprimir a ≤200KB c/u (resize 1072px, q~80).

## P3 — pulido

1. `font:` shorthand en todo el email: Outlook/Word maltrata el line-height → longhand en h1/body.
2. Bordes `rgba()` en email (`signal_email.py:43`,`:101`): Outlook los ignora; 123,77,255 es un
   morado fuera de sistema (el resto usa navy 28,25,86).
3. Fondo `#F7F5FD` del invite en email (`signal_email.py:101`) fuera de paleta (web usa #fff).
4. Preheader sin `mso-hide:all` (`signal_email.py:82`).
5. Sin helpers MSO/DPI; border-radius cuadrado en Outlook (aceptable).
6. Fecha "27.07.2026" (`%d.%m.%Y`) — formato europeo para audiencia US; sugerido "Jul 27, 2026".
7. Email de una edición Teardown se titula "The Signal" (`signal_email.py:80,90`): web dice
   "Teardown · #06", email "The Signal · #06". Decidir etiqueta neutral o format-aware.
8. Fragmento sin URL-encode (`signal_email.py:25` `#{slug}` crudo). Usar `quote(slug)`.
9. Params muertos: `legal_name/legal_address` no usados (`signal_email.py:59-60`); `compose()`
   defaultea `legal_address="CDMX, Mexico"` (`build_edition.py:41`) contra la marca LA.
10. Misceláneos verificados: video huérfano (poster sin `video` → tarjeta con statement vacío);
    `issue_no` int → "#7" vs "#05"; `A-video.jpg` byte-idéntico a `A-hero.jpg` y `B-hero.webp` a
    `B-field-notes.webp` (¿reuso intencional?); el `hero` del manifest nunca se renderiza en el
    signal web; kickers del JSON en title case ("Field Notes") hoy no se renderizan.

## PASS verificados (con evidencia)
- Guardarriel legal ✅ (`grep -rniE "cin[eé]tica"` → solo dentro del propio guardarraíl; cero en copy).
- Paleta de TEXTO ✅ (todos los `color:` ∈ {#0B0F0F,#F4F3F3,#787878,#1C1956,#E4E4EF}).
- Sentence case ✅ (únicos all-caps: ULTRA, FIFA, SIGGRAPH — nombres propios/acrónimos).
- Peso HTML <102KB ✅ (email-A = 11,129 bytes; B = 11,163).
- `aspect-ratio`/`backdrop-filter` en email ✅ (grep = 0; solo en web).
- Seguridad del render ✅ (`html.escape(quote=True)` en todo; sin eval/shell; sin secretos).
- Claims ✅ sin inventos (cifras trazan a `sources` de los JSON; fact-check humano por edición).

## Nota de integración
`newsletter.yml` → `newsletter_bot.py` **no invoca** `build_edition.compose()` todavía; el motor
auditado solo corre desde scripts de simulación. Integrar junto con el validador de esquema
(P2-5/6) o el cron del lunes fallará en silencio la primera edición malformada.
