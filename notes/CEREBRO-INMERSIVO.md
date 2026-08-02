# CEREBRO INMERSIVO — arquitectura del motor editorial "AI sin AI"

Plan maestro. El objetivo NO es "juntar noticias": es un **editor de máquina** que decide
QUÉ vale la pena y CÓMO enmarcarlo con POV de experto B2B, reaccionando a **momentos**
(terminó el Mundial → mejores ideas; salió el short de Shrek → por qué se vio feo; Harry
Potter en Cosm LA; SIGGRAPH; Anthropic sacó modelo). Toda la INTELIGENCIA vive en
heurísticas deterministas de Python (scoring, léxicos, calendario, detección de picos,
selección de formato). Un LLM sólo redacta las palabras finales — el juicio editorial es del
cerebro.

> Regla de oro (del reporte de ventas SL-26): *"the pitch converts, connection is the
> bottleneck."* El newsletter existe para ganar CONEXIÓN a escala y quedar top-of-mind. Cada
> edición debe pasar el **test del productor**: ¿esto le da munición, inspiración o un tema de
> conversación para su próximo pitch de marca? Si no, no va.

---

## 0. Quién lee (ICP, del SL-26)

- **Agencias experienciales** (81 en LA) + **marcas** (Sony, Apple, Amazon, HBO, Netflix,
  lululemon, SKIMS, Fender, Microsoft, SEPHORA, Workday…). Roles: VP Innovation, Exec/Senior
  Creative Producer, Creative Director, Head of Creative Production, Exec Producer.
- **STRONG fit** = dedicada a experiencial · fabrica/monta pero SIN 3D real-time/interactivo
  in-house · immersive-minded (projection, AR, touch, installations) · presupuestos de
  gran marca · cómoda poniendo tech de un partner bajo su propia marca (white-label).
- **Ángulo SensaLab** (repetido en el reporte): la capa white-label de 3D real-time /
  projection / AR / interactivo que la agencia mete en su activación; convierte activaciones
  en "content engines"; el "spectacle" digital bajo su marca.
- **Implicación editorial:** hacer que ESE productor se vea inteligente e inspirado. Mostrar
  qué se puede, qué está ganando, qué está fallando, y qué tech lo desbloquea — sin vender
  duro. SensaLab se posiciona por asociación, no por pitch.

---

## 1. Contrato de datos (todos los módulos usan esto)

`Candidate` (dataclass, extiende el `Story` actual). Campos:

```
headline, source, link, summary, published        # ingesta
tier, geo                                          # ya existe
entities: dict   # {"brands":[], "venues":[], "tech":[], "agencies":[], "ip":[]}
topic: str       # cluster/tema normalizado (para picos y anti-repeticion)
scores: dict     # {"relevance","b2b","timeliness","momentum","novelty","authority","talkability","angle","geo","total"}
angle: str       # "bar-moved" | "steal-this" | "teardown" | "tech-unlock" | "recap" | "straight"
moment: str|None # id de momento/tentpole si aplica (ej. "siggraph-2026")
```

Interfaz común: cada módulo expone funciones puras `def enrich(cands: list[Candidate]) -> None`
(mutan en sitio) o `def score(cand) -> float`. Sin estado global salvo stores en disco.

---

## 2. Módulos (archivos nuevos; el bot v1 queda como base)

| Archivo | Rol |
|---|---|
| `ingest_news.py` | Fuentes por QUERY (Google News RSS `news.google.com/rss/search?q=`) para reaccionar a entidades/momentos, además del RSS fijo. Registro de queries por entidad. |
| `calendar_events.py` | Calendario de tentpoles (SIGGRAPH, CES, Cannes Lions, Comic-Con, Super Bowl, Mundial, Coachella, Art Basel, GDC, Apple/Anthropic/OpenAI, aperturas Sphere/Cosm/Meow Wolf). Detecta "momento activo" por fecha. |
| `lexicon.py` | Diccionarios: brands, venues (Sphere, Cosm, Meow Wolf, teamLab), tech (Unreal, Unity, Notch, TouchDesigner, projection mapping, LED volume, gaussian splatting, AR glasses), **agencias del ICP** (de la lista SL-26), IP/franquicias (Harry Potter, Shrek, Barbie). Etiqueta entidades. |
| `b2b_fit.py` | Score de encaje B2B usando el ICP: sube activación de agencia/marca, gran presupuesto, white-label, tech-que-podrían-usar; baja fluff de consumer-tech. |
| `momentum.py` | Detección de picos: clusteriza candidatos por `topic`/entidad; marca un tema como "momento" si el cluster es grande o hay tentpole activo. |
| `composer.py` | **El centro.** Los formatos de edición (abajo) + el META-selector que elige el formato de la semana según el pool + calendario. |
| `scoring.py` | Combina los sub-scores en `total` con pesos configurables (y ganchos para el feedback de engagement). |
| `tracking.py` | UTM builder, `target=_blank rel=noopener`, ingesta de stats/webhooks de Brevo (open/click/bounce/unsub), store de engagement por suscriptor, diseño del endpoint de redirect first-party. |
| `content_model.py` | Modela edición+historias como JSON estructurado → renderiza a email HOY y a **blog** mañana (mismo contenido, dos renderers). |

---

## 3. Algoritmos de composición (el cerebro elige uno por semana)

Cada formato = su propia lógica de selección + arreglo. El META-selector puntúa el "fit" de
cada formato dado el pool de la semana y el calendario, y corre el ganador.

- **A. Digest** (default): 5 items balanceados, diversidad de fuente, min geo. (El actual.)
- **B. Momento / Temático** (event-driven): un tentpole activo (SIGGRAPH, Mundial, HP en Cosm)
  → 1 hero + 3-4 ángulos del mismo tema. Se dispara con momento activo o pico fuerte.
- **C. Teardown / Crítica** (POV): un objeto polarizante de craft (el short de Shrek, una
  activación fallida) → análisis crítico con la lente de craft de SensaLab ("por qué falló,
  cómo debió hacerse"). Se dispara con `talkability` alta.
- **D. Deep Dive** (explainer de un tema): un tema (gaussian splatting para eventos, LED
  volumes) con varias facetas. Se dispara en semana floja con tema evergreen fuerte.
- **E. Steal-This Playbook** (roundup de ideas): tras un evento cultural grande (Coachella,
  Mundial) → "N ideas que te puedes robar", táctico y list-driven.
- **F. Signal / Tech-unlock**: sale una herramienta/modelo (Anthropic, release de Unreal,
  gafas AR nuevas) → "qué desbloquea esto para experiencias". Se dispara con señal de release.

El META-selector es la decisión "tipo-editor": mira el pool, el calendario y los picos, y
escoge la forma de la edición como lo haría un editor. Esa es la magia "AI sin AI".

---

## 4. Scoring (juicio editorial, multi-factor)

`total = w1*relevance + w2*b2b + w3*timeliness + w4*momentum + w5*novelty + w6*authority +
w7*talkability + w8*angle_potential + w9*geo`

- `relevance`: fuerza de keywords experienciales (STRONG/INCLUDE, ya existe, con límites de palabra).
- `b2b`: encaje con el ICP (`b2b_fit.py`).
- `timeliness`: recencia + si toca un tentpole activo.
- `momentum`: qué tan "spike" está el tema esta semana (`momentum.py`).
- `novelty`: anti-repetición (no cubierto recientemente; por `topic`, no sólo URL).
- `authority`: peso de la fuente + mención de gran marca/venue.
- `talkability`: controversia/craft-fail (motor del formato Teardown).
- `angle_potential`: qué tan bien encaja en un ángulo fuerte.
- `geo`: boost LA/Miami/NY/Vegas.

Pesos en `config`/JSON, ajustables por el **feedback de engagement** (§5): un tema/formato que
rinde clicks sube su peso (bandit simple). El cerebro APRENDE de la data, sin LLM.

---

## 5. Tracking y medición (data → aprendizaje)

- **Links**: `target="_blank" rel="noopener noreferrer"` (nueva pestaña — correcto para B2B,
  el correo queda abierto) + **UTM** en cada link: `utm_source=inmersivo&utm_medium=email&
  utm_campaign=issue-<n>&utm_content=<story-slug>`.
- **Entrega/aperturas/clicks**: la API de stats + webhooks de Brevo (sent/delivered/opened/
  clicked/bounced/unsub). Ingesta a un store.
- **Por-usuario**: `data/subscribers.json` con opens/clicks por suscriptor a lo largo del
  tiempo → **engagement score** → segmentar (más a los enganchados, re-engage a dormidos).
- **First-party (rumbo a sitio propio)**: endpoint de redirect en nuestro dominio
  (`go.sensalab.io/c/<token>` → log → 302 al destino) para data de clicks independiente del ESP.
- **Loop de aprendizaje**: qué historias/formatos ganaron clicks → realimenta los pesos de §4.

---

## 6. Rumbo a blog propio (dejar de mandar tráfico a terceros)

- `content_model.py`: cada edición e historia como JSON estructurado → dos renderers:
  (a) email HTML (hoy), (b) post de blog / página web (cuando salga el sitio, ~1 mes).
- Al lanzar el sitio: cada edición se publica como post en `sensalab.io/blog` y el email
  linkea a NUESTROS posts (canónicos), no a terceros. La fuente original queda como cita al
  pie; el destino es nuestro análisis. Así el tráfico va a nosotros y el tracking es first-party.
- Sitio sugerido: estático (Astro/11ty/Next export) alimentado del mismo `content/` — el blog
  es un renderer nuevo, no un sistema nuevo. Se planea en `notes/BLOG-ROADMAP.md`.

---

## 7. Correctitud B2B (guardarriel de propuesta)

- Cada edición pasa el **test del productor** (§ regla de oro).
- Tono: value-first, sin vender duro; el lector es un productor senior ocupado; respeta su
  tiempo; dale munición para su próximo pitch.
- CTA suave y opcional ("¿quieres esta capa? responde"), no en cada historia.
- Cadencia semanal; listo para segmentar agencia vs marca.
- Guardarriel legal intacto: NUNCA trabajo pasado del fundador / clientes pasados / Cinética;
  no inventar datos ni casos.

---

## 8. Orden de construcción

1. Ingesta ampliada (`ingest_news.py`) + léxico (`lexicon.py`) + calendario (`calendar_events.py`).
2. Scorers (`b2b_fit.py`, `momentum.py`, `scoring.py`) sobre el `Candidate`.
3. `composer.py` (formatos + meta-selector) — el centro.
4. `tracking.py` + `content_model.py`.
5. Integración en `newsletter_bot.py` v2 (el writer LLM sólo redacta al final).
6. Tests + red-team de cada pieza (Fable).

Todo se construye con **Fable 5**. El bot v1 (RSS→filtro→anti-rep→writer→ESP) queda como base
funcional mientras el cerebro v2 crece a un lado y luego se integra.
