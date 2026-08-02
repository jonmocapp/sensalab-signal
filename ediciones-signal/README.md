# Cómo se autora una edición (INMERSIVO · The Signal / Teardown)

El pipeline lee **`ediciones-signal/next.json`** cada semana:

```bash
python strategy/09-ops/run_weekly.py build      # renderiza web + email de next.json
python strategy/09-ops/run_weekly.py send       # SEND_MODE=file por default (no envía)
```

Al enviar de verdad, `next.json` se archiva solo en `ediciones-signal/sent/NN.json`.
Si no hay `next.json`, el build dice "semana sin edición" y no hace nada (es seguro).

`compose()` corre **3 puertas** antes de renderizar. Si una falla, **no se genera nada**:
1. **Gate non-compete (`guard.py`, fail-closed):** nunca el estudio anterior, clientes pasados
   ni "Cinética" (79 términos, normaliza acentos/separadores). Ver `strategy/08-compliance/`.
2. **Validador de esquema:** exige los campos mínimos (abajo) o aborta con mensaje claro.
3. **Selector de formato:** decide `signal` vs `teardown` (ver §Formato).

Ejemplos listos para copiar en **`ejemplos/`**:
- `ejemplo-signal.json` — digest de insights (The Signal).
- `ejemplo-teardown.json` — disección de un caso polarizante (Teardown).

---

## Campos mínimos (los exige `validate()`)

```jsonc
{
  "issue_no": "07",                       // obligatorio
  "edition_title": "…",                   // opcional (fallback de subject)
  "subject": "…",                         // <=60 chars, INGLÉS, sentence case (no MAYÚSCULAS)
  "format": "signal",                     // opcional: fuerza "signal" | "teardown" (si no, se decide solo)

  "hero": {                               // obligatorio: statement O headline
    "kicker": "This week's signal",
    "statement": "…",                     // el titular grande (sentence case)
    "sub": "…"
  },

  "sections": [                           // SIGNAL: >=1; cada una necesita role + statement/headline
    {
      "role": "field-notes",             // id único → ancla #field-notes + slot de imagen
      "statement": "…",
      "body": "…",
      "why": "…",                        // caja "Why it matters"
      "cta": "Read more →",
      "alt": "…"                         // texto alt de la imagen (accesibilidad)
    }
  ],

  "teardown": {                           // SÓLO formato teardown: todos obligatorios
    "case": "…", "statement": "…", "verdict": "…",
    "flaw": "…", "principle": "…", "why": "…",
    "case_img_role": "craft",            // qué slot de media usa la imagen del caso
    "done_right": { "text": "…", "label": "…", "img_role": "field-notes" },
    "video_statement": "…"
  },

  "video": { "statement": "…", "body": "…", "duration": "1:20" },   // opcional
  "invitation": { "headline": "…", "body": "…", "button": "Touch it" },  // headline obligatorio

  "media_plan": {                         // mapea cada slot → índice de sources[]
    "hero": 0, "field-notes": 1, "in-the-lab": 3, "craft": 2,
    "video": { "poster_url": "https://…", "link": "https://…" }
  },
  "sources": [ "https://…", "https://…" ] // se baja el og:image de cada una
}
```

## Formato: cómo se elige
- `format: "teardown"` o `"signal"` **fuerza** el formato.
- Si no, hay teardown cuando existe el bloque `teardown` **y** la _talkability_ ≥ 2
  (palabras de controversia real: backlash, criticized, switched off, called it fake, ai slop…).
- Si no, **The Signal** (digest).

## Reglas de marca (no negociables)
- **Nunca** texto TODO EN MAYÚSCULAS — sentence case siempre. Wordmark = "SensaLab".
- Texto sólo en la paleta: `#0B0F0F #F4F3F3 #787878 #1C1956 #E4E4EF` (el gradiente sólo en la barra).
- **Nunca** referir el estudio/clientes pasados ni "Cinética" (lo bloquea el gate igual).

## Imágenes
- Van por `media_plan` → `sources[]` (og:image de cada fuente). Se bajan **email-safe**:
  webp→jpg, ancho ≤1280, peso ≤200KB (lo hace `fetch_media.download`).
- Un slot sin `og:image` no tumba la edición: esa tarjeta sale sin imagen.
- **Pendiente de Jon:** las imágenes de los ejemplos son de terceros. Para enviar de
  verdad hay que usar imágenes propias o licenciadas (ver `strategy/00-CONSOLIDADO.md §4`).

## Validar una edición antes de publicarla
```bash
python -c "import json,build_edition as b; ed=json.load(open('ediciones-signal/next.json',encoding='utf-8')); \
b.compose(ed, None, issue_no=ed['issue_no'], date=__import__('datetime').datetime(2026,1,1)); print('OK', b.choose_format(ed))"
```
Si imprime `OK …` pasa las 3 puertas. Si lanza `GuardBlocked` o `EditionInvalid`, dice qué corregir.
