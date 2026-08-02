# BLOG-ROADMAP — de newsletter a blog propio (~1 mes)

Objetivo estratégico (plan §6): **dejar de mandar tráfico a terceros.** Cada edición de
INMERSIVO se publica como post en `sensalab.io/blog`; el email linkea a NUESTRO post
(canonical) y la fuente original queda como cita al pie. El tráfico llega a nosotros, el
tracking es first-party, y el archivo compone SEO semana tras semana.

Principio rector: **el blog es un renderer nuevo, no un sistema nuevo.** Todo sale de la
misma fuente única.

---

## 1. Fuente de verdad: `content/`

- `content_model.py` escribe **`content/edicion-<n>.json`** (schema versionado: number,
  slug, date, format_id, theme, subject, preview_text, intro, signoff, canonical_url,
  stories[{slug, headline, source_name, source_url, body, lens, angle, entities, image_ref}]).
- El sitio estático **lee `content/`** y genera las páginas. Nadie edita HTML generado a
  mano; corregir = corregir el JSON y regenerar.
- El mismo objeto renderiza a: email (`to_issue` → `templater.build_html`), post Markdown
  con front-matter (`to_markdown`) y página HTML simple (`to_web_html`, markup de
  referencia para el template del sitio).
- `content/` vive en el repo → cada edición queda versionada en git (historial editorial
  gratis).

## 2. Sitio estático sugerido

**Astro** (primera opción) o **11ty** (alternativa más ligera). Ambos leen `content/` sin
tocar el bot:

- **Astro**: content collection con loader de `content/*.json` (o `glob` sobre `.md`
  generados con `to_markdown`). Rutas: `src/pages/blog/[slug].astro`.
- **11ty**: `_data/ediciones.js` que lee el directorio + pagination para generar una página
  por edición.

Decisiones:
- **URL**: `sensalab.io/blog/inmersivo-<nn>-<tema>/` (= `Edition.slug`, estable porque es
  el canonical). Anclas por historia: `#<story.slug>` (el markdown ya emite `<a id=...>`).
- **Índice** `sensalab.io/blog/`: lista de ediciones (número, fecha, subject, preview_text).
- **Estética**: misma marca del email (navy `#1C1956`, gradiente lazo, Georgia/serif para
  titulares) pero layout de página, no de correo.
- **Deploy**: Netlify o Vercel conectado al repo; build automático en cada push. Cero
  servidores, cero costo en estos volúmenes.

## 3. Publicación de cada edición (pipeline v2)

Orden importa: **el post se publica ANTES de enviar el email** (el email linkea al post).

1. Bot genera la edición (igual que hoy): `issue = writer.write_issue(...)`.
2. `ed = from_issue(issue, number, date, format_id, theme, candidates=chosen)` —
   hereda `entities`/`angle` de los `Candidate` (tags del post gratis).
3. `save_edition(ed)` → `content/edicion-<n>.json` + commit/push (el GitHub Action del
   bot ya corre en el repo; añadir el push del JSON al workflow).
4. CI del sitio detecta el push → build → post live en `sensalab.io/blog/<slug>/`.
5. `set_canonical(ed); save_edition(ed)` → fija `canonical_url`.
6. `to_issue(ed, prefer_canonical=True)` → `templater.build_html` → enviar email.

Backfill: las ediciones ya enviadas se convierten una vez (`from_issue` sobre los JSON/HTML
guardados) para que el blog no nazca vacío.

## 4. Canonical + cita al pie (email v2)

- Hoy: `to_issue(ed)` mantiene `link = source_url` → email idéntico al actual, nada se rompe.
- Con sitio: `to_issue(ed, prefer_canonical=True)` pone
  `link = canonical_url#<story.slug>` (nuestro post) y agrega `source_url` como clave
  extra por historia (el templater v1 la ignora).
- **Templater v2** (cambio pequeño, cuando toque): "Leer el análisis →" apunta a `link`
  (nuestro post) y debajo una cita al pie "Vía <source_name>" apuntando a `source_url`.
  La fuente original siempre queda citada — nunca desaparece, solo deja de ser el destino.
- En el sitio: `<link rel="canonical">` self-referencial en cada post (ya lo emiten
  `to_markdown`/`to_web_html` cuando `canonical_url` existe).

## 5. Tracking first-party (conecta con plan §5 / tracking.py)

- Links del email hacia el blog con UTM propios:
  `utm_source=inmersivo&utm_medium=email&utm_campaign=issue-<n>&utm_content=<story-slug>`.
- Analytics ligera y sin cookies en el blog: **Plausible** (pago) o **Cloudflare Web
  Analytics** (gratis) — suficiente para saber qué historias/formatos traen lectura.
- Fase 2: endpoint de redirect `go.sensalab.io/c/<token>` (diseño en `tracking.py`) para
  clicks del email independientes del ESP; con el blog propio, la mayor parte del valor ya
  se captura en el dominio propio.
- Loop de aprendizaje: lecturas/clicks por `story.slug` y `format_id` → realimenta los
  pesos del scoring (§4 del plan). Con blog propio la data es nuestra, no de Brevo.

## 6. SEO básico (v1, sin obsesionarse)

- Front-matter ya trae lo esencial: `title`, `description` (preview_text), `date`, `slug`,
  `tags` (entities: venues, tech, brands, IP — vocabulario que el ICP busca).
- Por post: `<title>` + meta description + OG/Twitter card (imagen: hero de la edición o
  card de marca por defecto) + JSON-LD `Article`.
- Por sitio: `sitemap.xml` + `robots.txt` + **RSS del blog** (bonus: el newsletter se
  vuelve suscribible por feed) — Astro/11ty lo dan casi gratis.
- Interlinking: cada post linkea al índice y a 1-2 ediciones anteriores relacionadas (por
  tags compartidos). El archivo entero es contenido evergreen de "tech experiencial".
- Rendimiento: estático puro → Core Web Vitals verdes sin trabajo extra.

## 7. Timeline (~1 mes, 4 semanas)

| Semana | Entregable |
|---|---|
| **S1** | Scaffold Astro + layout de marca; loader de `content/`; índice `/blog`; deploy preview en Netlify/Vercel. |
| **S2** | Template de post (mismas piezas que `to_web_html`: kicker, h1, intro, secciones con lens y cita); backfill de ediciones existentes; dominio `sensalab.io/blog` live. |
| **S3** | Wiring del bot: push de `content/` en el workflow, `set_canonical`, `to_issue(prefer_canonical=True)`, templater v2 con cita al pie; analytics first-party. |
| **S4** | SEO (sitemap, OG, JSON-LD, RSS), QA cross-device, y primera edición enviada 100% "email → post propio". |

## 8. Guardarrieles

- Los mismos del plan §7: **NUNCA** trabajo pasado del fundador / clientes pasados /
  Cinética; no inventar datos. El post es el MISMO contenido curado y aprobado que el
  email — publicar en web no añade contenido nuevo sin pasar por los mismos filtros
  (`writer.scan_forbidden` aplica antes de `save_edition`).
- La fuente original siempre citada y linkeada (`rel="noopener noreferrer"`): somos
  curaduría con POV, no scraping.
