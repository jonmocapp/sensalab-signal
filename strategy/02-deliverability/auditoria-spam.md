# Auditoría de spam — copy y HTML actuales

Archivos auditados (24–27 jul 2026):
- `sim\out\final-email-A.html` (11,1 KB) y `final-email-B.html` (11,2 KB) — **los emails que se
  envían por Brevo**: peso principal de la auditoría.
- `sim\out\final-A.html` (9,2 KB) y `final-B.html` (7,9 KB) — ediciones web de destino.
- `sim\out\media\*` — pesos reales de imágenes.

## Veredicto

**La copy es limpia — el riesgo está en la infraestructura del HTML.** El texto editorial en
sentence case, sin mayúsculas, sin urgencia falsa ni vocabulario de venta es exactamente el perfil
que los filtros dejan pasar. Los bloqueos reales son 6 y todos tienen fix concreto.

Scorecard (email slim, que es lo que filtran los ISP):

| Área | Estado |
|------|--------|
| Palabras/patrones de spam en copy | OK — riesgo bajo |
| Estructura HTML (tablas, inline CSS, 600px) | OK — bien construido para email |
| Peso del HTML (11 KB < 102 KB de clipping de Gmail) | OK |
| Imágenes: rutas | **BLOQUEO** — relativas, rotas al enviar |
| Imágenes: peso y formato | **BLOQUEO** — 1,85 MB en A; WebP en B |
| Unsubscribe | **BLOQUEO CONDICIONAL** — solo funciona vía API de campañas |
| CAN-SPAM: dirección postal | **BLOQUEO LEGAL** — falta dirección física completa |
| Versión texto plano | Falta |
| Alt text en imágenes de contenido | Falta |
| Links | 2 fixes menores |

## Bloqueos (arreglar antes del primer envío)

### 1. Rutas de imagen relativas
Todas las imágenes usan `src="media/..."`. En el buzón del destinatario eso es una imagen rota —
y un email que llega como bloques rotos multiplica quejas. **Fix:** al integrar, reescribir a URLs
absolutas HTTPS en dominio propio (`https://sensalab.io/inmersivo/media/A-field-notes.jpg`).
Mismo dominio que los links = señal de coherencia para los filtros. No usar `inlineImageActivation`
de Brevo (emails inflados y peor placement).

### 2. Peso y formato de imágenes
Pesos reales actuales:

| Archivo | Peso | Objetivo |
|---------|------|----------|
| A-in-the-lab.jpg | 913 KB | ≤120 KB |
| A-video.jpg | 597 KB | ≤120 KB |
| A-field-notes.jpg | 196 KB | ≤120 KB |
| A-craft.png | 157 KB | ≤120 KB (pasar a JPG) |
| B-field-notes.webp | 493 KB | ≤120 KB **y convertir a JPG** |
| B-craft.jpg | 125 KB | OK ajustado |
| B-video.jpg | 130 KB | OK ajustado |
| B-in-the-lab.png | 36 KB | OK |

- Total email A: **~1,85 MB** de imágenes; email B: ~0,8 MB. Objetivo: **<500 KB por email**.
- Receta: redimensionar a 1072 px de ancho (2× los 536 px renderizados), JPG calidad 75–80.
- **WebP no renderiza en Outlook de escritorio (Windows)** — el ICP vive en Outlook corporativo
  (Sony, Microsoft, Amazon…). Convertir `B-field-notes.webp` a JPG. PNG solo para el logo.

### 3. `{{ unsubscribe }}` depende del método de envío
El tag de las líneas de footer solo lo resuelve la **API de campañas**. Enviado por la API
transaccional saldría el texto literal `{{ unsubscribe }}` sin link funcional → violación
CAN-SPAM + quejas. **Fix:** enviar como campaña (ya documentado en `brevo-setup.md` §3). Las
campañas añaden además `List-Unsubscribe-Post` (one-click RFC 8058) que Gmail/Yahoo exigen.

### 4. Falta dirección postal física (CAN-SPAM)
El footer dice "Los Angeles, CA — USA": no basta. CAN-SPAM exige dirección postal válida
(calle o PO Box o agente registrado). **Fix:** una línea en `brand_footer` (la integra Jon, no
tocamos .py): `SensaLab, Inc. · [calle y número / PO Box], Los Angeles, CA [ZIP], USA`.

### 5. Sin versión texto plano
Emails solo-HTML puntúan peor en SpamAssassin y colegas. **Fix:** en la campaña Brevo activar la
generación automática de texto plano o pasar un resumen de ~10 líneas (titular + 3 bullets + link
a la edición web + unsubscribe).

### 6. Alt text vacío en imágenes de contenido
`alt=""` en las 4 imágenes editoriales (el logo sí tiene alt). Con imágenes bloqueadas por defecto
(Outlook corporativo otra vez) el email queda mudo, y los filtros valoran alt presente.
**Fix:** alt descriptivo corto en sentence case, p. ej. `alt="Drone scoreboard over Seattle"`,
`alt="Cosm dome watch party"`, `alt="Shrek 5 teaser still"`.

## Copy — scan de palabras y patrones

Resultado del scan sobre A y B (email + web):

| Hallazgo | Dónde | Riesgo | Acción |
|----------|-------|--------|--------|
| "free" ×1 ("free Home of Soccer hubs") | email/web A | Bajo — uso editorial, no promocional | Dejar |
| "impossible" ("Have something impossible in mind?") | A y B | Nulo | Dejar |
| Flecha `→` y `▶` en CTAs | A y B | Nulo (unicode inofensivo) | Dejar |
| Sin ALL CAPS, sin `!`, sin `$`, sin "act now / limited / guarantee / click here / winner" | — | — | Perfil ideal, mantener como estándar editorial |

Los asuntos aún no existen en los archivos. Recomendación spam-safe: usar el H1 como asunto
(<60 caracteres, sentence case, cero clickbait):
- A: `The best of the World Cup happened outside the stadiums`
- B: `Your audience just became a craft critic`
Preheader ya implementado con hack `&zwnj;` correcto en ambos. Bien.

## Links

Email A: 12 links → 8 a `sensalab.io` (con UTM correctos), 2 a `fox13seattle.com`, socials + mailto.
Email B: 12 links → 8 a `sensalab.io`, 2 a `youtube.com/results?...`, socials + mailto.

1. **`youtube.com/results?search_query=Shrek+5...` (email B, ×2):** una URL de resultados de
   búsqueda con query string parece link de spam para los filtros y es frágil (el resultado #1
   puede cambiar). **Fix:** linkear al video exacto o, mejor, a un redirect propio
   `https://sensalab.io/go/shrek-teaser` — coherente con la regla del BRIEF ("el clic va a NUESTRO
   sitio") y deja el email mono-dominio.
2. **`fox13seattle.com` (email A, ×2):** mismo tratamiento — `https://sensalab.io/go/seattle-drones`.
   Objetivo: TODOS los clics del email en un solo dominio (sensalab.io) + tracking alineado.
3. `target="_blank"` y `rel="noopener"` en email son inertes (los clientes los ignoran/quitan) —
   no dañan; pueden quedarse.
4. Ratio links/texto: ~12 links por ~380 palabras es razonable para un newsletter; no añadir más.

## Ratio texto/imagen y tamaño

- ~380 palabras reales por email + 5 imágenes: dentro de lo sano (regla 60/40 aproximada) SIEMPRE
  que las imágenes lleven alt. El texto vive en HTML real (no en imágenes) — correcto.
- HTML 11 KB: sin riesgo de clipping de Gmail (102 KB). Mantenerse bajo ese techo cuando se
  añadan módulos.

## Las ediciones web (`final-A.html`, `final-B.html`)

- Correctas para su rol de página destino. **Nunca enviarlas como email**: usan `:root` vars,
  flexbox, `aspect-ratio`, `position:absolute`, `<style>` en head — todo eso muere en Outlook y
  varios webmails. La separación edición-web / email-slim del motor es exactamente la correcta.
- Único ajuste: cuando se publiquen, servir sus imágenes desde las mismas URLs absolutas que el
  email (una sola fuente de media).

## Orden de ejecución de los fixes

1. Hosting de media con URL absoluta (bloquea todo lo demás) — depende del hosting web pendiente.
2. Comprimir/convertir imágenes (tabla §2).
3. Dirección postal en footer.
4. Alt text.
5. Redirects `sensalab.io/go/...` para los 2 links externos.
6. Confirmar envío por API de campañas + texto plano activado.
7. Test mail-tester ≥9/10 y seeds — recién entonces, warmup semana 1.
