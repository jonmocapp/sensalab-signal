# Spec — panel de medición INMERSIVO

Especialista 05 · Skills aplicados: `analytics-dashboard` (estructura de panel: tiles de titular → tendencia → detalle → análisis escrito), `dataviz` (forma según el trabajo del dato, color computado, una sola escala por eje). Mock navegable en `mock-dashboard.html` (misma carpeta).

---

## 1. Fuentes de datos (todas ya previstas por el motor)

| Fuente | Qué da | Cadencia | Módulo |
|---|---|---|---|
| Brevo stats (poll) | sent/delivered/opens/clicks/bounces/unsubs + clicks por link (`linksStats`) | 1–2×/día (rate limit ~100 req/h en endpoints misc) | `fetch_campaign_stats()` |
| Brevo webhooks | eventos por suscriptor en tiempo real (delivered/open/click/bounce/unsub/spam) | push | `parse_webhook()` → `record_event()` |
| `data/subscribers.json` | score y segmento por suscriptor | derivado | `engagement_score()`, `segment()` |
| GA4 (sitio) | sesiones por `utm_campaign`, `edition_read`, `contact_cta_clicked` | diario | export/API GA4 |
| `data/weights.json` + `weights-history.jsonl` | pesos del cerebro y sus ajustes | por edición | `scoring.py` |
| `data/ops-log.csv` | replies, conversaciones, booked (manual semanal) | semanal | Jon (2 min/semana) |

Implementación v1 sin servidor: un script `build_dashboard.py` (futuro, lo integra Jon) junta las fuentes y renderiza un HTML estático a `sim/out/dashboard.html` después de cada edición. Cero infra, cero coste — mismo espíritu que el resto del motor.

## 2. Layout (de titular a detalle, orden de lectura)

```
┌────────────────────────────────────────────────────────────────┐
│ Inmersivo — panel de medición        edición NNN · fecha       │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────────────┤
│entreg│ open │ CTR  │ CTOR │visits│lectur│replies│ booked (mes) │  fila 1: tiles
├──────┴──────┴──────┴──────┴──────┴──────┴──────┴───────────────┤
│ Embudo de la edición: entregados → … → booked (barras h.)      │  fila 2
├───────────────────────────────┬────────────────────────────────┤
│ Tendencia por edición         │ Clicks por historia (edición)  │  fila 3
│ (open % y click %, líneas)    │ (barras h., por utm_content)   │
├───────────────────────────────┼────────────────────────────────┤
│ Rendimiento por topic         │ Formato: Signal vs Teardown    │  fila 4
│ (clicks por historia, barras) │ (clicks/historia, 4 ediciones) │
├───────────────────────────────┼────────────────────────────────┤
│ Salud de la lista             │ Pesos del cerebro + deltas     │  fila 5
│ (segmentos, barra apilada)    │ (9 barras + flecha de ajuste)  │
├───────────────────────────────┴────────────────────────────────┤
│ Experimento activo (hipótesis, variantes, n, estado, decisión) │  fila 6
├────────────────────────────────────────────────────────────────┤
│ Guardarraíles: bounces · unsubs · quejas (verde/alarma)        │  fila 7
└────────────────────────────────────────────────────────────────┘
```

## 3. Cada gráfica: forma, fuente, decisión que informa

| # | Panel | Forma (dataviz) | Fuente | Decisión que informa |
|---|---|---|---|---|
| 1 | Tiles de titular | número héroe + delta vs media 4 ediciones | Brevo + GA4 + ops-log | ¿esta edición fue normal o anomalía? |
| 2 | Embudo | barras horizontales, misma escala, valores absolutos | todas | ¿dónde se rompe la cadena? (el peor salto es el foco de la semana) |
| 3 | Tendencia | 2 líneas (open, click) — misma unidad (%), un solo eje; puntos por edición | Brevo | trayectoria; detecta fatiga o mejora del programa |
| 4 | Clicks por historia | barras horizontales ordenadas, etiqueta = `utm_content` | linksStats / webhooks | curaduría: qué historia ganó; alimenta el retro editorial |
| 5 | Por topic | barras (clicks por historia, ventana 8 ediciones) | `performance_by_topic()` | qué temas suben de peso (espejo humano del bandit) |
| 6 | Por formato | 2 barras: Signal vs Teardown (sólido vs textura, no dos hues) | idem | validar la decisión de formato por talkability |
| 7 | Salud de lista | barra apilada 100%: engaged/at-risk/new/dormant/lost | `segment()` | cuándo correr re-engage; tamaño real de la audiencia núcleo |
| 8 | Pesos del cerebro | barras + delta del último ajuste; link al history | weights.json | auditar el bandit de un vistazo; freno de emergencia |
| 9 | Experimento | tarjeta de texto: hipótesis, n acumulado/objetivo, estado | doc 05 | continuar/parar/decidir el test |
| 10 | Guardarraíles | 3 tiles con umbral (ok / alarma) | Brevo | proteger entregabilidad — si hay alarma, TODO lo demás espera |

## 4. Reglas visuales (del skill dataviz + marca)

- **Solo la paleta de marca**: fondo `#F4F3F3`, tinta `#0B0F0F`, secundario `#787878`, dato `#1C1956`, superficie de panel `#E4E4EF`. Sin hexes nuevos; los pasos de intensidad se hacen con **opacidad de `#1C1956`** sobre el fondo, y la separación de series con **estilo** (sólido vs punteado vs textura 45°), nunca con hues fuera de marca. Nota honesta: el validador de paleta del skill no pudo correrse en esta máquina (no hay Node); se mitigó por construcción evitando categorías multi-hue por completo.
- **Sentence case** en todo rótulo. Números formateados (`1.2k`, `46%`). Texto siempre en tinta/secundario, nunca del color de la serie.
- **Un solo eje por gráfica** — nunca doble escala. Open% y click% comparten unidad; si un día se quiere clicks absolutos vs %, son dos gráficas.
- Grid y ejes recesivos (`#E4E4EF`), marcas finas, etiquetas directas selectivas (no un número en cada punto).
- Tooltips por marca al hover en la versión real; el mock usa `<title>` nativo de SVG.
- Cada panel lleva su fuente al pie ("Brevo · poll diario", "GA4", "manual") — que nadie confunda dato duro con dato manual.

## 5. Análisis escrito (bajo el panel, por edición)

Plantilla de 5 líneas que el script rellena con datos y Jon completa con criterio:

1. **Titular**: la edición vs la media móvil de 4 (mejor/igual/peor y en qué nodo).
2. **Historia ganadora** y su topic; ¿confirma o contradice el peso actual del cerebro?
3. **Eslabón más débil del embudo** esta semana y la acción única que lo ataca.
4. **Señales de venta**: engaged nuevos en cuentas ICP Strong (lista corta, con slug clickeado).
5. **Guardarraíles**: ok / alarma.
