# The Signal — motor autónomo (local, puro Python, sin n8n)

Busca noticias reales, las acomoda, las redacta con voz SensaLab, les consigue imagen, las mete a
**Latest stories** y publica el sitio. Solo. Sin n8n: Python ya orquesta todo el flujo.

## El loop
```
daily_signals.py   → POOL de noticias reales (RSS + Google News, puntuadas)   [gratis, sin LLM]
      ↓
pipeline.py        → elige las mejores nuevas del pool
      ↓  fetch_source.py     baja la fuente: hechos reales + og:image
      ↓  article_writer.py   redacta la nota (Claude API) anclada a esos hechos + guardarraíl
      ↓  set_articles.py     la mete a articles_live.json, consigue/optimiza la imagen
      ↓  build_articles/build_blog_b/build_seo   reconstruye Latest stories + el sitio
      ↓
deploy.py          → publica blog/ en Netlify por API        [opcional]
published.json     → recuerda qué ya publicó (nunca repite)
```
`autopilot.py` encadena pipeline + deploy, una pasada o en bucle.

## Correr
```bash
python autopilot.py --once            # una pasada completa (buscar→redactar→publicar)
python autopilot.py --every 12        # demonio: corre ya y cada 12 h
python autopilot.py --once --mock     # prueba la plomería sin LLM ni publicar
python pipeline.py --dry --limit 3    # ver qué elegiría, sin escribir
```

## Dejarlo 100% autónomo en la PC (sin proceso vivo)
```powershell
powershell -ExecutionPolicy Bypass -File setup_autopilot.ps1
```
Registra una tarea que corre `autopilot.py --once` **diario a las 7am**, aunque reinicies.

## Configuración (.env, una vez)
| Variable | Para qué | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | **Necesaria** para redactar las notas | — |
| `PIPELINE_MODEL` | Modelo que redacta | `claude-sonnet-5` (barato) |
| `PIPELINE_MAX_NEW` | Notas nuevas por corrida | `3` |
| `NETLIFY_AUTH_TOKEN` + `NETLIFY_SITE_ID` | Publicar en vivo (si faltan, solo construye local) | — |

## Costo
Solo el paso de redacción usa la API. Con Sonnet, ~pocos centavos por nota; a 3/día son unos
dólares al mes. El pool, el scoring, las imágenes y el build son gratis. Sube a `claude-opus-4-8`
en `PIPELINE_MODEL` si quieres máxima calidad por más costo.

## Guardarraíles (siempre activos)
- Cada nota se ancla SOLO en el texto real de la fuente (no inventa datos).
- Se **rechaza** cualquier nota que mencione a Cinética / trabajo previo / autobombo (non-compete).
- Fuentes no latinas y PR de bajo valor (perfiles, nombramientos) se descartan para deep-dive.
