# 05 — Tracking, analytics y medición

Especialista 05 · INMERSIVO. Skills invocados y aplicados: **`analytics`** (taxonomía UTM, naming de eventos, árbol de medición para decisiones), **`analytics-dashboard`** (estructura del panel: tiles de titular → tendencias → detalle → análisis escrito), **`ab-testing`** (hipótesis, tamaño de muestra, anti-peeking, programa ICE) y **`dataviz`** (forma por trabajo del dato, un eje por gráfica, color por construcción) para el mock.

## Qué entregué

| Archivo | Contenido |
|---|---|
| `01-utm-taxonomy.md` | Taxonomía canónica de UTM (email, social, referral), semántica de utm_content por bloque, `utm_term` reservado para experimentos, conexión con GA4 y el redirect first-party, checklist de QA por edición |
| `02-kpi-tree.md` | Árbol entregados → abiertos → clicks → visitas → lecturas → replies → conversaciones → booked; definiciones, fuente y fórmula por nodo; benchmarks B2B y metas por fase (0 a 3); reglas de lectura para lista chica |
| `03-engagement-scoring.md` | Spec del score 0–100 (documenta el `engagement_score()` vigente), refinamientos (descuento de proxy opens, banda at-risk, sunset), export semanal a ventas (matriz engagement × ICP del SL-26) y formalización del bandit sin LLM (deltas por señal, multiplicadores por topic, log de auditoría, freno de emergencia) |
| `04-dashboard-spec.md` | Spec del panel: 6 fuentes de datos, layout de 7 filas, 10 paneles con forma/fuente/decisión, reglas visuales de marca, plantilla de análisis escrito |
| `05-ab-testing-roadmap.md` | Roadmap de tests: realidad estadística con n≈140 (tabla de tamaños de muestra), diseño pooled multi-edición, regla de decisión honesta, backlog ICE (asunto → día/hora → hero → CTA → densidad), secuencia por issues y plantilla de documentación |
| `mock-dashboard.html` | Mock estático del panel, autocontenido (cero librerías externas), solo los 5 hex de marca, sentence case, datos marcados como ejemplo |

## Decisiones clave

1. **El motor ya mide** — `tracking.py` implementa UTMs, poll de Brevo, webhooks, score y `performance_by_topic`; mis specs se anclan a ese código en vez de inventar otro sistema. Lo que falta son 3 piezas de pegamento (deltas por señal, export a ventas, descuento de proxy opens) y están especificadas, no programadas (regla: no tocar .py).
2. **Bug de taxonomía detectado**: `tracking.wrap_link()` emite `utm_campaign=issue-<n>` y `signal_email._url()` emite `signal-<n>` — la misma edición aparecería como dos campañas. Canónica propuesta: `issue-NNN` (cero-padded). Cambio de una línea al integrar.
3. **El click es la métrica primaria**, no el open (Apple MPP infla opens; `parse_webhook()` ya distingue `proxy_open`). Con lista chica, números absolutos sobre porcentajes.
4. **A/B con honestidad estadística**: con ~140 entregados no hay significancia por envío; el diseño es pooled multi-edición con split congelado, variantes valientes, una variable a la vez (coherente con el ritmo de iteración de la casa) y regla de decisión "directional + repeated" declarada como tal.
5. **El bandit y el A/B no se pisan**: formato Signal vs Teardown lo aprende el bandit (talkability + multiplicadores), no se somete a A/B.
6. **Mock 100% marca**: paleta de 5, intensidades por opacidad del azul, series separadas por estilo (sólido/punteado/textura 45°) — nunca hues nuevos. El validador de paleta del skill dataviz no pudo ejecutarse (no hay Node en la máquina); se mitigó evitando categorías multi-hue por diseño.

## Qué necesito de Jon

1. **Unificar `utm_campaign`** al integrar (`issue-NNN` en `signal_email.py` o en `wrap_link`, una línea).
2. **BREVO_API_KEY** y registro del webhook marketing (los eventos exactos ya están en `MARKETING_WEBHOOK_EVENTS` de `tracking.py`).
3. **Hosting de la edición web + GA4** (crear propiedad, pegar snippet; los eventos están en `01-utm-taxonomy.md` §3).
4. **2 minutos por semana**: contar replies/conversaciones/booked en `data/ops-log.csv` (etiqueta Gmail `inmersivo-reply`). Es el único dato manual del árbol y es la señal de oro.
5. **Decidir** si el redirect first-party `go.sensalab.io/c/` entra en fase 1 o 2 (los tokens HMAC ya existen en `tracking.py`; solo falta el endpoint).
