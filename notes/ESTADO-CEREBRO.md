# INMERSIVO — Estado del cerebro (handoff 2026-07-23, noche)

Resumen de la sesión nocturna: se construyó el **cerebro editorial "AI sin AI"** encima del
bot v1, se probó contra noticias reales, y se arreglaron todos los bugs del red-team.

## Qué corre HOY (un comando)

```powershell
cd C:\Dev\SensaLab-Newsletter-Bot
python newsletter_bot_v2.py --dry-run     # el cerebro arma el plan de la semana (NO llama LLM, NO envía)
```
Probado contra las noticias reales de esta semana: juntó **110 candidatas** (RSS + 10 queries
de Google News), **detectó solo** que el Mundial acabó, y eligió el formato **steal_this**
("las mejores ideas del Mundial") con 5 activaciones reales del Mundial. Cero intervención.

Para una edición REAL (necesita tu `ANTHROPIC_API_KEY`):
```powershell
copy .env.example .env      # pon tu key; SEND_MODE=file de default (no envía, solo genera HTML)
python newsletter_bot_v2.py
```

## Los dos bots

- `newsletter_bot.py` (v1): RSS → filtro → anti-repetición → writer → ESP. Simple, robusto.
- `newsletter_bot_v2.py` (v2, el cerebro): ingesta amplia → tag entidades → momentos →
  scoring multi-factor → **composer elige formato** → writer respeta formato/ángulo → ESP.

## El cerebro (módulos, todos probados)

| Módulo | Rol | Estado |
|---|---|---|
| `models.py` | contrato `Candidate` | ✅ |
| `ingest_news.py` | Google News RSS por query (reacciona a entidades/momentos) | ✅ |
| `lexicon.py` | léxico marcas/venues/tech/agencias/IP + tag/topic | ✅ |
| `calendar_events.py` | 14 tentpoles; ve Mundial *just-ended*, Comic-Con *live*, SIGGRAPH *upcoming* | ✅ |
| `b2b_fit.py` | scorer del ICP (SL-26): Nike immersive 0.96, Apple earnings 0.00 | ✅ 10 tests |
| `momentum.py` + `scoring.py` | picos + ranking ponderado | ✅ 45 tests |
| `composer.py` | 6 algoritmos de composición + meta-selector | ✅ |
| `tracking.py` | UTM + target_blank + Brevo stats/webhooks + engagement + token first-party | ✅ |
| `content_model.py` | mismo contenido → email HOY, **blog** mañana (markdown/web + canonical) | ✅ |
| `brain.py` | orquestador del cerebro (plan de edición) | ✅ |

## Los 6 algoritmos de composición (el cerebro elige uno según la semana)

- **Digest** — 5 items balanceados (default).
- **Momento/Temático** — momento activo o topic dominante caliente → 1 hero + ángulos del tema.
- **Teardown/Crítica** — algo polémico/craft-fail (el short de Shrek) → análisis con lente de craft.
- **Deep Dive** — semana floja + tema evergreen → explainer de un tema.
- **Steal-This** — tras evento grande (Mundial, Coachella) → "N ideas robables".
- **Tech-unlock** — release real de tool/modelo (Anthropic, Unreal) → "qué desbloquea".

## Data / tracking (respuestas a tus preguntas)

- **Clicks/aperturas**: Brevo trae stats + webhooks (`tracking.fetch_campaign_stats`, `parse_webhook`).
- **A dónde mandamos el click**: **nueva pestaña** (`target="_blank" rel="noopener noreferrer"`,
  correcto para B2B: el correo queda abierto). Cada link lleva UTM (`utm_source=inmersivo`…).
- **Tracking de usuario**: `data/subscribers.json` — engagement por suscriptor (recencia+frecuencia),
  segmentación engaged/dormant/new (`tracking.engagement_score`, `segment`).
- **First-party (rumbo a sitio propio)**: token HMAC + redirect `go.sensalab.io/c/<token>` diseñado
  (`make_click_token`/`verify_click_token`) para data de clicks independiente del ESP.

## Blog propio (~1 mes) — ya sembrado

`content_model.py` guarda cada edición como JSON estructurado (`content/`) del que salen DOS
renderers: email (hoy) y **markdown/web con front-matter + canonical** (blog). Cuando salga el
sitio (Astro/11ty sugerido), el email linkeará a NUESTROS posts (canonical) y la fuente queda como
cita — dejamos de mandar tráfico a terceros. Ver `notes/BLOG-ROADMAP.md`.

## Bugs arreglados (red-team v2, Fable)

- Preflight del ESP ANTES de gastar el LLM y comprometer estado (no quemar la semana si Brevo rechaza).
- Guarda de alineación de links en `writer` (aborta si el modelo devuelve # distinto de historias).
- `save_state` atómico + aviso (no reset silencioso) si el JSON se corrompe.
- Workflow que **falla ruidoso** (antes perdía el estado en silencio ante conflicto).
- Brevo: quitado el campo `type` inválido; `BREVO_LIST_ID` validado numérico.
- `config.validate` ya no mete el aviso de MailerLite como error bloqueante.
- Voz/Lens integrada al writer (test del ácido, few-shots, `[FOCO GEO]` explicado, anti-autobombo).

## Pendiente (siguiente sesión)

1. Correr una edición REAL con tu API key (validar la prosa por formato).
2. Tests de `composer`/`tracking`/`content_model` (los agentes Fable murieron antes de escribirlos).
3. Conectar Brevo real (cuenta + lista + remitente verificado) y probar el envío en `draft`.
4. Arrancar el blog (Astro/11ty) leyendo de `content/`.
5. Afinar pesos/umbrales del composer con datos reales de varias semanas.

## Nota sobre los agentes Fable

4 de 8 agentes Fable murieron con el stall conocido ("Response stalled mid-stream"); dejaron sus
archivos casi completos y Opus (el orquestador) los completó/verificó. `lexicon.py` se escribió
entero a mano por esa caída.
