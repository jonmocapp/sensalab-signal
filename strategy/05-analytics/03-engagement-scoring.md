# Spec — engagement scoring por suscriptor y loop del cerebro

Especialista 05 · Skills aplicados: `analytics` (event tracking por usuario), `ab-testing` (rigor del loop de aprendizaje). Todo determinista — **bandit simple, sin LLM**, coherente con "AI sin AI".

Estado real: `tracking.py` YA implementa el 80% de esto (`record_event`, `engagement_score`, `segment`, `performance_by_topic`) y `scoring.py` trae `adjust_weights` (bandit con LEARNING_RATE=0.10, clamp [0.02, 0.40], renormaliza a suma 1). Este doc **documenta el contrato, fija parámetros y especifica las 3 piezas que faltan** (descuento de proxy opens, deltas por señal, y el export a ventas). No edité los .py.

---

## 1. El score (0–100) — contrato vigente

```
score = 100 · (0.6 · recencia + 0.4 · frecuencia)

recencia   = exp(−días_desde_última_actividad / 45)      # media vida ≈ 31 días
frecuencia = min(1, (opens_90d + 3·clicks_90d) / 12)      # click pesa ×3
unsubscribed o hard bounce → score = 0 (compliance, no re-engage)
```

Por qué está bien así: recencia domina (60%) porque en B2B el valor es estar **top-of-mind ahora**; el click pesa ×3 porque el open miente (proxy) y el click es intención; la ventana de 90 días ≈ 12 ediciones semanales, que es justo el denominador del cap.

### Refinamiento 1 (para integrar): descuento de proxy opens

`parse_webhook()` ya marca `machine_open=True` para `proxy_open` (Apple MPP), pero `record_event()` lo cuenta como open completo y actualiza `last_open`. Spec:

```
frecuencia = min(1, (opens_reales_90d + 0.25·proxy_opens_90d + 3·clicks_90d) / 12)
recencia: un proxy_open NO actualiza last_open (solo opens reales y clicks)
```

Los eventos ya guardan el flag en `sub["events"]` → el cambio es solo en el cálculo, no en el almacenamiento. Sin esto, un iPhone dormido parece un lector fiel.

## 2. Segmentos y qué hace cada uno

`segment()` vigente: `engaged` (score ≥ 40) · `new` (< 21 días de alta, sin juzgar) · `dormant` (resto) · `lost` (unsub/hard bounce — NO contactar).

Refinamiento 2 — banda de vigilancia dentro de dormant:

| Segmento | Regla | Acción |
|---|---|---|
| engaged | score ≥ 40 | audiencia núcleo; candidatos a outbound (abajo) |
| at-risk | 15 ≤ score < 40 | siguen recibiendo; si 8 ediciones sin click → mover a re-engage |
| dormant | score < 15 y > 21 días | secuencia re-engage (1 correo "¿seguimos?"); sin respuesta en 2 envíos → sunset (dejar de enviar, proteger reputación) |
| new | alta < 21 días | no juzgar; el welcome hace su trabajo |
| lost | unsub / hard bounce / spam | fuera, para siempre |

El sunset no es cosmético: complaint rate y bounces son lo que Gmail mira; enviar a dormidos eternos cuesta entregabilidad de TODA la lista.

## 3. Alimenta al lead scoring de ventas

El puente con el SL-26: cruzar **engagement × fit ICP** (78 agencias ya scoreadas: 29 Strong, 15 Good).

**Export semanal** (pieza nueva, `data/sales-feed.json`, lo genera un script que lee `subscribers.json`):

```json
{ "email": "…", "score": 87.5, "segment": "engaged",
  "last_click": "2026-07-20", "clicked_slugs_90d": ["cosm-…", "siggraph-…"],
  "clicked_topics_90d": ["venues-domos", "realtime-3d"] }
```

**Matriz de prioridad para outbound:**

| | ICP Strong | ICP Good | Resto |
|---|---|---|---|
| **engaged** | P1 — contactar esta semana, citando el tema que clickeó | P2 | P3 |
| **at-risk** | P2 — tocar antes de que se enfríe | P3 | — |
| **new** | esperar 3 ediciones | esperar | — |

Señales de intención fuertes (suben una prioridad): click en una historia de **tecnología adyacente a la capa SensaLab** (real-time 3D, proyección, AR interactivo) · 2+ clicks en la misma edición · reply de cualquier tipo. El opener de outbound sale del `clicked_slugs_90d`: "vi que el caso X te interesó…" — sin autobombo y sin mencionar trabajo pasado (guardarraíl legal intacto: hablamos del mercado, no de nosotros).

## 4. Alimenta los pesos del cerebro — el bandit, formalizado

### Pieza existente

- `performance_by_topic(store, editions)` → `{topics: {t: clicks_per_story, share}, formats: {...}, stories: {slug: clicks}}`.
- `scoring.adjust_weights(weights, performance)` → `w *= 1 + 0.10·clamp(perf, −1, 1)`, clamp [0.02, 0.40], renormaliza. El floor 0.02 ES la exploración del bandit: ninguna señal muere, todo sigue teniendo chance de resurgir.

### Pieza que falta (spec): calcular `perf` por señal

Después de cada edición con datos (ver regla de muestra mínima):

```
para cada señal s en {relevance, b2b, timeliness, momentum, novelty,
                      authority, talkability, angle, geo}:

  clicked   = historias de la edición con ≥1 click (de performance_by_topic.stories)
  published = todas las historias publicadas en la edición

  perf[s] = clamp( ( media_s(clicked) − media_s(published) ) / 0.25 , −1, +1 )
```

Lectura: si las historias clickeadas tenían `momentum` medio 0.8 y las publicadas 0.55, `perf["momentum"] = +1.0` → su peso sube 10% esa semana. Determinista, auditable, sin LLM. Los sub-scores por historia ya existen (los produce `combine()` al armar la edición; hay que persistirlos en el log de la edición para poder mirarlos después — una línea en el JSON de edición).

### Reglas de seguridad del loop

1. **Muestra mínima**: si `total_clicks < 5` en la edición → NO ajustar (carry de pesos). Con 3 clicks, el ruido manda.
2. **Ventana**: los deltas se calculan con la edición recién medida, pero se aplica el ajuste **cada edición** con LEARNING_RATE 0.10 — a ese paso, mover un peso al doble tarda ~7 ediciones consecutivas de señal positiva. Correcto: sin bandazos.
3. **Topics y formatos** (además de señales): multiplicador editorial `m_t` por topic, inicial 1.0, actualizado `m_t ← clamp( m_t · (1 + 0.10 · perf_t), 0.85, 1.15 )` con `perf_t = clamp((cps_t − cps_medio) / cps_medio, −1, 1)` donde `cps` = clicks_per_story. Decae hacia 1.0 a razón de 2% por edición sin datos del topic (nada queda castigado/premiado para siempre). Mismo esquema para formato (Signal vs Teardown) — pero el formato ya lo decide talkability; el multiplicador solo matiza.
4. **Log de auditoría**: cada ajuste escribe una fila en `data/weights-history.jsonl`: `{issue, perf, weights_antes, weights_después}`. Si el newsletter "cambia de gusto", se puede ver exactamente qué click lo causó. Esto también alimenta el panel (doc 04).
5. **Freno de emergencia**: si CTOR cae < 6% dos ediciones seguidas tras una racha de ajustes → restaurar `WEIGHTS` default de `scoring.py` y reanudar el loop desde ahí (los defaults son el prior editorial sano).
