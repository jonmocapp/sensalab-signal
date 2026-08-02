# Árbol de KPIs — INMERSIVO

Especialista 05 · Skills aplicados: `analytics` (medir para decidir, no por vanidad). Principio rector: con lista chica, **los números absolutos mandan sobre los porcentajes** (con 140 entregados, 1 persona = 0.7 puntos).

---

## 1. El árbol

```
                        LISTA (crecimiento neto/mes)
                          │
  ENTREGADOS ─────────────┤  salud de infraestructura (guardarraíl)
      │                   │
  ABIERTOS (únicos) ──────┤  interés en el sobre (asunto + remitente) — direccional, inflado por proxy opens
      │                   │
  CLICKS (únicos) ────────┤  interés en el contenido — LA métrica primaria del newsletter
      │                   │
  VISITAS WEB ────────────┤  el click llegó (sesiones GA4 con utm_source=inmersivo)
      │                   │
  LECTURAS (edition_read) ┤  profundidad — la edición web cumplió
      │                   │
  REPLIES ────────────────┤  la señal de oro B2B: alguien contestó el correo
      │                   │
  CONVERSACIONES ─────────┤  reply/DM que se vuelve intercambio real (≥2 turnos)
      │                   │
  BOOKED ─────────────────┘  llamada agendada atribuible al newsletter
```

Métricas guardarraíl (nunca deben empeorar): **hard bounces**, **unsubscribes**, **quejas de spam**.

El insight SL-26 ordena el árbol: *"the pitch converts, connection is the bottleneck"*. El newsletter no se mide por booked directo — se mide por **reach caliente** (clicks, lecturas, replies). Booked es lagging y llegará por outbound sobre suscriptores engaged (ver spec de scoring, doc 03).

## 2. Definiciones y fuente de cada nodo

| KPI | Fórmula | Fuente |
|---|---|---|
| Entregados | `delivered / sent` | Brevo `globalStats` (poll, ya normalizado en `normalize_campaign_stats()`) |
| Open rate | `uniqueViews / delivered` | Brevo. Descontar `proxy_open` cuando se mida por webhook (Apple MPP infla 10–20 pp) |
| CTR | `uniqueClicks / delivered` | Brevo + webhooks |
| CTOR | `uniqueClicks / uniqueViews` | derivado (ya en `click_to_open`) |
| Visitas web | sesiones con `utm_campaign=issue-NNN` | GA4 (o log del redirect first-party) |
| Lecturas | evento `edition_read` (scroll ≥75% o ≥60 s) | GA4 |
| Replies | correos entrantes a `hello@sensalab.io` en respuesta a la edición | manual: etiqueta Gmail `inmersivo-reply` + conteo semanal en `data/ops-log.csv` |
| Conversaciones | replies/DMs con ≥2 turnos reales | manual (mismo log) |
| Booked | llamadas agendadas cuya fuente declarada/inferida es el newsletter | manual (mismo log) |
| Bounce rate | `(soft + hard) / sent` | Brevo |
| Unsub rate | `unsubscriptions / delivered` | Brevo |
| Complaint rate | `complaints / delivered` | Brevo (límite duro Gmail/Yahoo: 0.3%; objetivo <0.1%) |

## 3. Benchmarks B2B realistas y metas por fase

Rangos típicos de email B2B (industria, órdenes de magnitud — no promesas): open 30–40% (inflado por MPP), CTR 1.5–3%, CTOR 8–12%, unsub <0.5%, bounce <2%. Un newsletter curado a lista chica y warm debe rendir POR ENCIMA de la media B2B; si rinde en la media, algo falla en la relevancia.

### Fase 0 — infraestructura (pre-issue 1)

Sin metas de engagement. Checklist: SPF/DKIM/DMARC verdes, seed list cargada (los 118 leads LA, 98% con email → ~100–150 suscriptores opt-in reales tras invitación), webhook Brevo registrado, GA4 activo, `utm_campaign` unificado.

### Fase 1 — baseline (issues 1–8, ~2 meses)

Medir sin tocar. Nada de tests: se necesita línea base limpia.

| KPI | Meta | Alarma |
|---|---|---|
| Entregabilidad | ≥ 98% | < 96% |
| Open rate | ≥ 40% | < 30% |
| CTR | ≥ 3% | < 1.5% |
| CTOR | ≥ 8% | < 6% |
| Visitas web / edición | ≥ 80% de unique clicks | — |
| Replies | ≥ 1 por edición (absoluto) | 0 en 4 ediciones seguidas |
| Unsub | < 0.7% por envío | > 1.5% |
| Quejas | 0 absoluto | ≥ 1 |

### Fase 2 — optimizar (issues 9–26)

Arranca el programa de A/B (doc 05) y el loop del cerebro (doc 03).

| KPI | Meta |
|---|---|
| Open rate | ≥ 45% |
| CTOR | ≥ 12% |
| Lecturas (`edition_read`) | ≥ 50% de las visitas |
| Replies | ≥ 2 por mes |
| Conversaciones | ≥ 2 por mes |
| Booked | ≥ 1 por mes atribuible |
| Crecimiento de lista | +10–20 netos/mes (referidos + LinkedIn + web) |

### Fase 3 — escalar (lista ≥ 500)

Los porcentajes se vuelven estadísticamente útiles; los tests de click ganan potencia.

| KPI | Meta |
|---|---|
| Open rate | ≥ 42% (cae un poco al crecer: normal, vigilar el absoluto) |
| CTR | ≥ 4% |
| Booked | ≥ 2 por mes |
| Engaged share (score ≥ 40) | ≥ 45% de la lista activa |

## 4. Reglas de lectura (para no engañarnos)

1. **Opens son direccionales, no verdad**: Apple MPP abre por proxy. La tendencia sirve; el valor absoluto no. La métrica primaria de contenido es el click.
2. **Una edición no es señal**: leer en ventanas de 4 ediciones (media móvil), como hace el propio bandit.
3. **Con n<200, contar personas, no puntos**: "3 replies este mes" > "reply rate 2.1%".
4. **Cada KPI tiene un dueño de decisión**: open→asunto/remitente; CTOR→curaduría/formato; lecturas→edición web; replies→voz e invitación. Si un KPI no cambia ninguna decisión, se deja de mirar.
