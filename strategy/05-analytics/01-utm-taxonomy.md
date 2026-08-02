# Taxonomía de UTM — INMERSIVO

Especialista 05 · Tracking, analytics y medición. Skills aplicados: `analytics` (convenciones UTM + event naming), alineado con el código real de `tracking.py` y `signal_email.py`.

---

## 1. Estado actual del motor (leído, no editado)

El motor YA emite UTMs, pero con **dos convenciones distintas**:

| Módulo | utm_source | utm_medium | utm_campaign | utm_content |
|---|---|---|---|---|
| `tracking.py` → `wrap_link()` | `inmersivo` | `email` | `issue-<n>` | slug de la historia (`slugify()`, max 60) |
| `signal_email.py` → `_url()` | `inmersivo` | `email` | `signal-<n>` | **rol del bloque** (`hero`, `invitation`…) + `#<slug>` |

**Bug de taxonomía a resolver en la integración:** `issue-12` y `signal-12` son la misma edición pero en analytics aparecerán como dos campañas distintas. Hay que unificar (abajo la canónica). No edité los .py — es un cambio de una línea que integra Jon.

---

## 2. Taxonomía canónica (la regla)

### Formato general

```
utm_source  = quién envía el tráfico      (inmersivo | linkedin | instagram | youtube | partner)
utm_medium  = el canal                    (email | social | referral | qr)
utm_campaign= la edición                  (issue-NNN, cero-padded: issue-012)
utm_content = el link exacto dentro de la pieza   (<bloque>--<slug-historia>)
utm_term    = RESERVADO para experimentos (exp-<test>-<variante>, ej. exp-subject-b)
```

Reglas duras (del skill `analytics`):
- **Todo en minúsculas**, solo `[a-z0-9-]`, separador `-` (ya lo garantiza `slugify()`).
- **Nunca** UTMs en links internos del sitio (edición web → otra página de sensalab.io va limpia; los UTM solo cruzan de un canal externo hacia el sitio). UTMs en links internos rompen la atribución de la sesión.
- Los UTM nuestros **ganan** sobre los del publisher (ya implementado en `wrap_link()`: strip de `utm_*` ajenos).
- Documentar cada campaña nueva en `data/utm-log.csv` (columnas: fecha, url final, source, medium, campaign, content, term, dónde se usó).

### utm_campaign — identidad de la edición

- Canónica: `issue-NNN` con **cero-padding a 3 dígitos** (`issue-001` … `issue-052`). Ordena bien en cualquier tabla y aguanta años de ediciones.
- El **formato** (Signal vs Teardown) NO va en el campaign: es metadato de la edición y se junta en análisis vía el log de ediciones (`issue → formato`). Meterlo duplicaría campañas.
- Envíos especiales fuera de cadencia: `special-<slug>` (ej. `special-welcome`).

### utm_content — el link exacto

Convención de dos partes: `<bloque>--<slug>`; si el bloque no apunta a una historia, solo `<bloque>`.

| Link en el email slim | utm_content |
|---|---|
| Imagen/título del hero | `hero--<slug-historia>` |
| Tarjeta de insight n | `card-1--<slug>`, `card-2--<slug>`… |
| Bloque de video | `video--<slug>` |
| Botón de invitación (CTA final) | `invitation` |
| Logo del header | `logo` |
| Link del footer (web/socials) | `footer-web`, `footer-linkedin`… |

Así un mismo destino con dos links (hero y CTA) se distingue → sabemos si convierte la historia o el botón. El ancla `#<slug>` que ya añade `signal_email.py` se conserva (lleva al lector directo a su tarjeta en la edición web).

### utm_source / utm_medium por canal

| Contexto | source | medium |
|---|---|---|
| Email slim → edición web | `inmersivo` | `email` |
| Post LinkedIn que comparte la edición | `linkedin` | `social` |
| Instagram (bio o stories) | `instagram` | `social` |
| YouTube (descripción) | `youtube` | `social` |
| Newsletter de un tercero que nos linkea (co-marketing) | `partner-<nombre>` | `referral` |
| QR en un evento/activación | `evento-<slug>` | `qr` |

---

## 3. Conexión con analytics del sitio (rumbo al blog propio)

La edición web ES el embrión del blog (`notes/BLOG-ROADMAP.md`). El día uno del hosting:

1. **Herramienta:** GA4 (gratis, lee UTMs nativo, sin coste que romper el presupuesto). Alternativa ligera si se prefiere sin cookies: Cloudflare Web Analytics (gratis) — pero pierde el detalle por utm_content; recomendación: GA4.
2. **Eventos del sitio** (naming `objeto_accion` del skill analytics):

| Evento | Cuándo dispara | Propiedades |
|---|---|---|
| `edition_viewed` | pageview de una edición | `issue`, `format` |
| `edition_read` | scroll ≥ 75% o ≥ 60 s | `issue`, `format` |
| `story_outbound_clicked` | click a la fuente original | `issue`, `slug` |
| `contact_cta_clicked` | click en el CTA de conversación | `issue`, `location` |
| `subscribe_submitted` | alta a la lista desde la web | `source_page` |

   Conversiones marcadas en GA4: `contact_cta_clicked` y `subscribe_submitted`.
3. **La verdad de los clicks es first-party:** `tracking.py` ya trae los tokens HMAC para `go.sensalab.io/c/<token>` (§5 del módulo). Cuando el redirect exista, el email linkea al redirect → 302 al destino **con los UTM ya puestos**. Brevo y GA4 se vuelven verificación cruzada; el log del redirect es nuestro dato dueño, independiente del ESP.
4. **Cadena completa por lector:** webhook Brevo (`click` + `utm_content`) → sesión GA4 (`utm_campaign=issue-NNN`) → evento `edition_read` → `contact_cta_clicked`. El eslabón email→web casa por utm; el eslabón lector→persona vive en `data/subscribers.json` (email + slug clickeado, ya implementado en `record_event()`).

---

## 4. Checklist de QA por edición (antes de enviar)

- [ ] Todos los `<a>` del email llevan los 4 UTM y `target="_blank" rel="noopener noreferrer"` (ya lo da `link_attrs()`).
- [ ] `utm_campaign` idéntico en todos los links de la edición (un solo valor, `issue-NNN`).
- [ ] Ningún `utm_content` duplicado apuntando a bloques distintos.
- [ ] Links internos de la edición web SIN utm.
- [ ] Si hay experimento activo: `utm_term=exp-…` solo en la variante correspondiente.
- [ ] Fila añadida a `data/utm-log.csv`.
