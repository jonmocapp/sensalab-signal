# Roadmap de A/B testing — INMERSIVO

Especialista 05 · Skills aplicados: `ab-testing` (hipótesis, tamaño de muestra, el problema del peeking, programa ICE), `analytics` (instrumentación de variantes vía `utm_term`).

---

## 1. La verdad incómoda primero: la potencia estadística

Con la lista de arranque (~100–150 entregados), el split clásico 50/50 por envío **no puede detectar casi nada**. Tamaños de muestra requeridos (α=0.05 bilateral, potencia 80%):

| Métrica base | Efecto a detectar | n por variante | ¿Viable hoy? |
|---|---|---|---|
| Open 40% | +15 pp (40→55) | ~170 | Casi — pooling de 3 ediciones |
| Open 40% | +10 pp (40→50) | ~390 | Pooling de 6 ediciones |
| Open 40% | +5 pp | ~1,560 | No hasta lista ≥ 3k |
| CTR 4% | +2 pp (4→6) | ~1,900 | No hasta lista ≥ 4k |
| CTOR 10% | +5 pp (10→15) | ~690 | Fase 3 |

Consecuencias de diseño (no opcionales):

1. **Un test = varias ediciones.** La unidad no es el envío sino el test: misma hipótesis, split repetido 3–6 ediciones consecutivas, resultados agrupados (pooled). El split se re-aleatoriza por suscriptor UNA vez al inicio del test y se mantiene fijo (mitad A / mitad B estables) — consistencia del skill ab-testing.
2. **Solo variantes valientes.** Con esta n, un matiz de wording es invisible. Se testean diferencias de enfoque, no de coma.
3. **Una variable a la vez, un test vivo a la vez.** (Coincide con el ritmo de iteración de una sola variable que ya es regla de la casa.)
4. **Regla de decisión honesta en fase 2** (pre-significancia): declarar ganadora una variante solo si (a) gana el pooled en ≥ 3 de 4 ediciones del test Y (b) el lift agrupado supera el umbral mínimo de la tabla de abajo Y (c) ningún guardarraíl empeoró (unsub, quejas, replies). Si no: inconclusivo → se queda el control y se anota el aprendizaje. Nada de p-hacking con n=140; esto es "directional + repeated", y se documenta como tal.
5. **Cero peeking**: la duración se fija ANTES (nº de ediciones); no se corta un test porque "ya se ve".

Mecánica en Brevo: el A/B nativo no está en el plan gratis → workaround sin coste: **dos campañas idénticas a dos mitades aleatorias de la lista** (listas A/B congeladas por test). Cada variante marca sus links con `utm_term=exp-<test>-<a|b>` para seguir el efecto río abajo (web, replies).

## 2. Backlog priorizado (ICE) — qué probar y en qué orden

| # | Test | Hipótesis (formato del skill) | Métrica primaria | I | C | E | ICE |
|---|---|---|---|---|---|---|---|
| 1 | **Estilo de asunto**: ángulo talkability ("the Sphere just changed the brief") vs beneficio directo ("3 ideas for your next activation") | Porque el ICP es creativo senior saturado de newsletters, creemos que el asunto-ángulo subirá opens ≥ 10 pp | open rate pooled (6 ediciones) | 9 | 6 | 9 | 8.0 |
| 2 | **Día/hora de envío**: martes 8 am PT vs jueves 8 am PT | Porque los productores planifican a inicio de semana, martes rendirá más opens y clicks | open rate (4+4 ediciones alternadas — aquí el split es temporal, no de lista) | 7 | 5 | 10 | 7.3 |
| 3 | **Hero del email slim**: imagen grande primero vs titular + texto primero | Porque el contenido es visual-first (3D/proyección), la imagen subirá CTOR ≥ 5 pp | CTOR pooled (6 ediciones) | 8 | 6 | 7 | 7.0 |
| 4 | **CTA de invitación**: "Touch it →" (actual) vs verbo de conversación ("Start the conversation →") | Porque el objetivo real es el reply/conversación, un CTA conversacional moverá clicks del botón + replies | clicks en `utm_content=invitation` + replies (6 ediciones) | 7 | 5 | 8 | 6.7 |
| 5 | **Densidad del slim**: 3 tarjetas vs 5 tarjetas | Porque menos opciones concentran el click, 3 tarjetas subirá clicks totales por lector | unique clicks/entregado | 6 | 5 | 7 | 6.0 |
| 6 | **Nombre de remitente**: "SensaLab" vs "nombre @ SensaLab" | El remitente humano sube opens y replies en B2B | open + reply | 6 | 6 | 9 | 7.0* |

\* El #6 es barato y de bajo riesgo: buen candidato a colarse temprano si el #2 (temporal) corre en paralelo sin conflicto de variable (remitente afecta open; día/hora también → NO se corren juntos; ver secuencia).

**Qué NO se A/B-testea**: el formato Signal vs Teardown. Esa decisión ya la toma el cerebro por talkability y la mide el bandit (doc 03) — someterla a A/B duplicaría el mecanismo de aprendizaje y partiría la muestra que el bandit necesita.

## 3. Secuencia (fase 2, arranca en el issue 9)

```
issues 1–8    fase 1: NADA. Solo baseline limpio (doc 02).
issues 9–14   test 1 — estilo de asunto (split de lista, 6 ediciones, pooled)
issues 15–22  test 2 — día de envío (alternancia por bloques de 2, sin split)
issues 23–28  test 3 — hero imagen vs texto
issues 29–34  test 4 — CTA de invitación
issues 35–40  test 5 o repesca del mejor inconclusivo (con la lista ya más grande)
```

Cadencia de programa (del skill ab-testing): revisión semanal de 15 min (guardarraíles del test vivo — parar solo si un guardarraíl empeora claro), cierre y decisión al terminar las ediciones fijadas, retro mensual del backlog con re-score ICE.

## 4. Plantilla de documentación (una por test, en `strategy/05-analytics/experiments/`)

```
## exp-<slug>
Fechas / issues: …          Split: lista A/B congelada (n=…/…) o temporal
Hipótesis: Porque [dato], creemos que [cambio] causará [efecto ≥ umbral] en [ICP].
Métrica primaria: …         Secundarias: …        Guardarraíles: unsub, quejas, replies
Duración fijada: N ediciones (decidida antes de lanzar — sin peeking)
Resultado pooled: A … vs B … (lift …, ediciones ganadas …/…)
Decisión: ganadora / control / inconclusivo
Patrón aprendido: [la frase reutilizable]
Aplicar a: [dónde más sirve: web, LinkedIn, outbound]
```

Con el tiempo esto se convierte en el playbook del programa: la biblioteca de patrones probados sobre ESTE ICP — más valiosa que cualquier benchmark de industria.

## 5. Cuándo se gradúa el programa

- **Lista ≥ 500**: los tests de open pasan a split por envío único (2–3 ediciones bastan para +10 pp).
- **Lista ≥ 2k**: entran tests de CTR/CTOR con significancia real; considerar plan de Brevo con A/B nativo si el manual pesa.
- **Siempre**: un test vivo, una variable, guardarraíles primero, y el bandit editorial corriendo por debajo sin interferencia.
