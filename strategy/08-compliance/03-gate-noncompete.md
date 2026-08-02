# Política non-compete operacionalizada + spec del gate de pre-envío

Especialista 08 — Compliance, legal & brand safety. Este doc amplía `scan_forbidden`
**conceptualmente** (no toco los .py; la integración la hace quien opera el motor).

---

## 1. La política, en 3 clases de prohibición

Fuente: guardarriel del BRIEF ("NUNCA menciones ni aludas al trabajo pasado del fundador,
clientes pasados, ni Cinética. No inventes datos, cifras ni casos.") y writer.py:70-78.

- **P1 — El nombre.** "Cinética" y toda variante, en cualquier idioma, campo, URL, filename,
  alt text o metadato. Sin excepciones, sin contexto atenuante. Un hit = edición inválida.
- **P2 — La alusión.** Cualquier afirmación en primera persona sobre historial: trabajo
  pasado, clientes pasados, proyectos previos, "años haciendo esto para X", portafolio,
  casos de éxito propios. Incluye la forma indirecta ("we've done this before for a global
  sneaker brand" alude sin nombrar — igual de prohibido). SensaLab opina como experto del
  mercado; no presume historial. Las marcas del ICP (Sony, Apple, Netflix…) solo pueden
  aparecer como **sujetos de noticias de terceros con fuente**, jamás como objetos de un verbo
  en primera persona ("we built/delivered/produced for…").
- **P3 — El invento.** Datos, cifras, fechas o casos no presentes en las fuentes de la
  edición. Un número sin fuente es un número inventado (writer.py:73-74).

## 2. Estado actual del gate — 3 huecos verificados

| # | Hueco | Evidencia | Gravedad |
|---|-------|-----------|----------|
| 1 | El pipeline nuevo NO escanea. `build_edition.py` (el cerebro que produce las ediciones reales sim/edicion-A/B → final-*.html) no llama a `scan_forbidden` en ningún punto. | grep `scan_forbidden` en build_edition.py: 0 matches; solo newsletter_bot.py:102 y newsletter_bot_v2.py:81 (pipeline viejo) lo usan | Crítica |
| 2 | El escáner lee el esquema viejo. `scan_forbidden` (writer.py:147-157) concatena `subject/preview_text/intro/signoff/theme/stories[]`; las ediciones reales usan `hero/sections/video/invitation/teardown/edition_title/sources`. Contra edicion-A.json el escaneo efectivo es de cadena vacía. | writer.py:149-153 vs sim/edicion-A.json:1-63 | Crítica |
| 3 | Con hit, igual sube el contenido al ESP. newsletter_bot_v2.py:81-86 degrada `send`→`draft`, pero el draft **con el término prohibido** se crea en Brevo (sale de nuestra infraestructura). | newsletter_bot_v2.py:84-86 + sender.py:34 (`POST /emailCampaigns` se ejecuta igual en modo draft) | Alta |
| 4 | Lista corta y solo literal. `FORBIDDEN` (writer.py:140-144) tiene 7 entradas literales; no cubre variantes con guiones, homoglifos, inglés ("our past clients"), ni alusiones sin keyword. | writer.py:140-144 | Alta |

## 3. Spec del gate de pre-envío (bloqueante)

### 3.1 Dónde corre y qué escanea (cobertura total, no por campos)

El gate corre como **último paso antes de cualquier llamada al ESP** y como paso de CI si el
envío sale de GitHub Actions (.github/workflows/newsletter.yml). Escanea **cuatro superficies**:

1. **JSON de la edición — recorrido recursivo.** Walk de TODO string en el dict, sin lista de
   campos (a prueba de cambios de esquema; mata el hueco #2). Incluye campos "internos"
   (`theme`, `angle`): si un interno está sucio, la edición se revisa igual — lo interno de
   hoy es copy de mañana.
2. **HTML final renderizado**, email y web (`final-*.html`, `final-email-*.html`): atrapa lo
   que inyectan templates, footer, alt text, títulos, comentarios HTML.
3. **Metadatos del envío**: subject, preview text, nombre de campaña, from_name — todo lo que
   viaja en el payload de sender.py.
4. **Rutas y URLs**: filenames de media/, URLs de sources y CTAs, parámetros UTM (una URL
   `utm_content=cinetica-style` también es un hit).

### 3.2 Pipeline de normalización (anti-evasión)

Antes de comparar, cada superficie pasa por:

```
lower() → NFKD → strip diacríticos (cinética→cinetica) → mapa homoglifos
(і/е/а/о/с cirílicas → latinas) → mapa leet (1→i, 3→e, 0→o, @→a, $→s) →
colapsar separadores (c-i.n_e t i c a → cinetica)
```

Y se evalúan **tres detectores** en orden:
- **D1 exacto**: substring contra la lista de términos normalizados (forbidden-terms.txt §A-C).
- **D2 patrones**: regex de alusión EN/ES (forbidden-terms.txt §D). Cazan la estructura
  "primera persona + verbo de entrega + pasado/cliente" sin depender de keywords.
- **D3 difuso**: Levenshtein ≤1 de cada token del texto contra `cinetica` (caza `cinetika`,
  `sinetica`, `cinetika`), con allowlist explícita (§E) para el vocabulario legítimo del
  dominio: `cinematic`, `cinematica`, `cinematography`, `kinetic`, `kinetics`, `cinema`.
  Un match difuso que no esté en la allowlist = hit.

### 3.3 Lógica de decisión (dos niveles)

- **HARD BLOCK (D1, D2, D3):** exit code ≠ 0. **No se crea ni el draft** en Brevo (cierra el
  hueco #3): el orden correcto es gate → (si limpio) draft → aprobación humana → send, nunca
  draft → gate. El reporte imprime término, superficie, contexto (±80 chars) y detector.
- **SOFT FLAG (advisory, no bloquea solo):**
  - **F1 números huérfanos**: todo numeral de la copy debe existir en el material de las
    fuentes de `sources[]` (política P3). Numeral sin respaldo → flag para el revisor.
  - **F2 juez LLM (opcional, ~$0.001/edición con Haiku):** prompt con la política de §1 y el
    texto plano; devuelve PASS o lista de alusiones sospechosas. Es red de seguridad
    semántica para alusiones sin keyword ("back when we lit up a stadium…"). Advisory:
    señal para el humano, nunca autoridad para aprobar.

### 3.4 Revisión humana (metodología safe-publish, adaptada de Webflow a Brevo)

Todo envío pasa por un humano con esta secuencia — igual que safe-publish exige preview +
confirmación tipada + verificación posterior:

1. **Preview**: gate limpio → se genera el reporte de pre-envío:
   - hits = 0 (con conteo de superficies y detectores corridos),
   - checklist CAN-SPAM automática: `{{ unsubscribe }}` presente, dirección postal (regex
     calle+ZIP) presente, from = hello@sensalab.io, subject ≤ 60 chars,
   - checklist de marca: sin MAYÚSCULAS completas, paleta de texto (5 hex del BRIEF),
   - **SHA-256 del htmlContent exacto** que se mandaría a la API.
2. **Draft**: solo entonces se crea la campaña en Brevo en modo draft. Jon la ve en Brevo
   (test send a hello@sensalab.io incluido).
3. **Confirmación tipada**: para disparar `sendNow`, el operador escribe la palabra exacta
   `PUBLICAR` (no "sí", no "ok", no "dale" — regla anti-confirmación-accidental de
   safe-publish). Cualquier otra respuesta = no envía.
4. **Sello**: antes de `sendNow` se re-verifica que el SHA-256 del contenido de la campaña
   sea el aprobado (lo aprobado = lo enviado, sin ventana de edición intermedia).
5. **Auditoría**: se agrega una línea JSON a `logs/send-approvals.jsonl`:
   `{ts, issue_no, sha256, gate:"clean", approver, action:"sent"}`. Si el gate bloqueó:
   `{ts, issue_no, term, surface, action:"blocked"}`. Este log es la prueba de "monitoreo
   de lo que se envía en tu nombre" (CAN-SPAM §1.7 del doc 01).

### 3.5 Protocolo de falso positivo

El gate va a bloquear algún día una frase legítima (p.ej. un festival real llamado "Kinetika").
Protocolo: (a) primera opción, reescribir la frase — casi siempre es lo más barato; (b) si el
término es legítimamente necesario, se agrega a la allowlist §E **con línea de justificación
y fecha**, y queda en el historial del repo. Prohibido: saltarse el gate con flag de entorno,
editar el reporte, o aprobar "solo por esta vez" sin tocar la allowlist. El gate sin
excepciones documentadas es la defensa; con excepciones silenciosas es teatro.

### 3.6 Mantenimiento de la lista

- `forbidden-terms.txt` es la fuente de verdad (versionada en git). El código la carga; los
  términos no viven hardcodeados en .py (hoy FORBIDDEN está en writer.py:140-144 — migrar).
- Revisión trimestral: nuevas variantes vistas en drafts bloqueados, nuevos patrones de
  alusión que el juez LLM haya flaggeado.
- La lista es en sí información sensible de segundo orden (revela qué se protege): el repo
  debe seguir privado.
