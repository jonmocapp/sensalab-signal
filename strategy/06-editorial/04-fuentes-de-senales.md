# Fuentes de señales — cómo detectar el "momento" de la semana

Además del RSS fijo actual (`sources.py`: Event Marketer y BizBash como core; Adweek, The Art
Newspaper y Social Media Today como rotate). Cuatro capas de señal, de más automatizable a
menos.

## Capa 1 — RSS adicionales (candidatos a `sources.py`)

Verificar cada URL de feed con `doctor.py` antes de añadir (algunas cambian o requieren UA).

| Fuente | Feed (verificar) | Tier sugerido | Qué aporta |
|---|---|---|---|
| Blooloop | blooloop.com/feed/ | core-candidato | location-based entertainment, venues, aperturas (Cosm, Sphere, museos) — el hueco de venues del pool actual |
| InPark Magazine | inparkmagazine.com/feed/ | rotate | themed entertainment + expos |
| Event Industry News | eventindustrynews.com/feed/ | rotate | tech de eventos (proveedores, casos) |
| Dezeen | dezeen.com/feed/ | rotate (filtro estricto) | instalaciones y diseño espacial de nivel premio |
| designboom | designboom.com/feed/ | rotate (filtro estricto) | arte/instalación; bueno para bar-moved visual |
| Road to VR | roadtovr.com/feed/ | rotate | XR serio, hardware AR |
| UploadVR | uploadvr.com/feed/ | rotate | XR consumer, Quest/Connect |
| befores & afters | beforesandafters.com/feed/ | rotate | virtual production, LED volumes |
| fxguide | fxguide.com/feed/ | rotate | craft de VFX/real-time |
| 80.lv | 80.lv (feed por verificar) | rotate | real-time art, Unreal/Unity en producción |
| Unreal Engine blog | unrealengine.com (feed por verificar) | query/rotate | releases del engine (señal directa del formato F) |
| Unity blog | unity.com/blog (feed por verificar) | query/rotate | idem |
| Little Black Book | lbbonline.com (feed por verificar) | rotate | trabajo de agencias, craft de campañas |
| The Drum | thedrum.com (feed por verificar) | rotate | industria creativa/experiential |

Criterio de admisión: misma regla que hoy — CORE entra con INCLUDE; ROTATE exige STRONG.
Dezeen/designboom necesitan el filtro estricto o inundan el pool con sillas y lámparas.

## Capa 2 — Google News RSS por query (ya en la arquitectura, `ingest_news.py`)

Queries fijas de entidad (el "radar permanente"):

- Venues: `"Sphere Las Vegas"`, `Cosm venue`, `"Meow Wolf"`, `teamLab`, `AREA15`,
  `Superblue`, `"Lightroom London"`, `Outernet`
- Craft/técnica: `"projection mapping"`, `"drone show"`, `"anamorphic billboard"`,
  `"LED volume"`, `"virtual production" stage`, `"gaussian splatting"`, `hologram concert`
- Mercado: `"brand activation"`, `"experiential marketing"`, `"immersive experience" opening`,
  `"pop-up" brand Los Angeles`
- Tech-unlock: `"Unreal Engine" event OR live`, `Unity real-time live`, `"AR glasses"`,
  `TouchDesigner`, `Notch VFX`

**Queries dinámicas por tentpole**: durante lead/live/tail de cada evento de
`tentpole-calendar.json`, añadir sus `keywords` como queries temporales. El calendario
alimenta la ingesta — así el pool "se calienta" solo cuando toca (ej. semana 4: se activan
`gamescom`, `opening night live`, `us open fan week`).

## Capa 3 — Ciclos de premios y listas (señal lenta, oro para steal-this y frameworks)

| Qué | Cuándo (aprox) | Uso editorial |
|---|---|---|
| Cannes Lions (Brand Experience & Activation, shortlists y Lions) | junio | banco de casos con pedigrí para todo el año |
| Event Marketer Ex Awards + It List | verano | quién está haciendo el mejor trabajo experiential en US |
| Clio Experience | otoño | segundo banco de casos |
| TEA Thea Awards (themed entertainment) | anuncio ~nov | venues y atracciones premiadas |
| Webby / FWA / Awwwards (interactive) | continuo/primavera | craft digital-físico |

No son noticias: son inventario. Alimentan deep dives y celdas de la matriz en semanas valle.

## Capa 4 — Señales sociales y manuales (10 min/semana de Jon, no automatizables gratis)

- LinkedIn: hashtags #experientialmarketing #brandactivation #immersive — qué comparten los
  productores del pipeline (la señal más cercana al ICP real).
- TikTok/IG: videos virales de activaciones (el motor de teardowns: ahí nacen los "se veía
  fake" y los "comments off").
- Reddit: r/virtualproduction, r/augmentedreality, r/vfx — detección temprana de
  controversias de craft.
- YouTube: canales de Sphere, Cosm, colectivos de projection mapping; los vídeos de recap
  de tentpoles concentran los mejores casos.

## Cómo se combina todo en "el momento de la semana"

Señal compuesta (todo determinista, sin LLM):

1. **Calendario**: fase live/just-ended en `tentpole-calendar.json` (vía `calendar_events.py`).
2. **Pico de pool**: cluster >= 4 historias del mismo topic en la semana (`momentum.py`).
3. **Pico de query**: mejora describible para `momentum.py` — contar items nuevos por query
   de Capa 2 vs su media móvil de 4 semanas; ratio >= 2x = spike (detecta momentos que NO
   están en el calendario, ej. un flop viral).
4. **Engagement retro**: clicks por topic desde Brevo (`tracking.py`) reponderan los pesos
   (`scoring.py`, bandit) — el lector vota qué pilares pesan más.

Si 1 y 2 coinciden → moment/steal_this casi seguro. Si solo 3 dispara → candidato a
teardown/tech_unlock según léxico. Si nada dispara → semana valle: deep dive de inventario.
