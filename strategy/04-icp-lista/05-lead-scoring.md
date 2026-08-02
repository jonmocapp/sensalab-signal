# Modelo de lead scoring — fit + engagement para priorizar ventas

Metodología: skill `sales-lead-score` (modelo 4 dimensiones con pesos por motion, decay,
scoring negativo, umbrales calibrados y backtest). Motion de SensaLab: **outbound-led** con el
newsletter como capa de engagement — pesos ajustados a esa realidad.

## Pesos (escala 0–100)

| Dimensión | Peso | Por qué |
|---|---|---|
| Fit de rol (demographic) | 25 | El buyer correcto es la mitad del deal |
| Fit de empresa (firmographic) | 25 | Los 5 criterios Strong del SL-26 ya demostraron predecir |
| Engagement (behavioral) | 35 | Es la señal viva que el newsletter añade al sistema |
| Timing | 15 | Ventanas observables (temporada, vacantes, cuentas nuevas) |

(El default outbound del skill es 25/30/20/25; subimos behavioral porque el propósito del
newsletter es justamente generar señal de comportamiento semanal que antes no existía.)

## 1. Fit de rol — 0–25

| Caso | Puntos |
|---|---|
| Título ICP exacto: EP, senior/exec creative producer, head of production, founder/ECD/CCO de shop experiencial, VP innovation | 25 |
| Adyacente con influencia: CD in-house, VP brand creative, head of creative production, experiential director, BD/account director en agencia fit | 15 |
| Periférico: art director, copywriter, coordinator, marketing manager | 8 |
| Sin relevancia | 0 |

## 2. Fit de empresa — 0–25

| Caso | Puntos |
|---|---|
| Agencia Strong (5/5 criterios SL-26) o equivalente look-alike | 25 |
| Agencia Good (4/5) · marca con calendario experiencial activo y presupuesto gran-marca | 18 |
| Possible (3/5) · marca con actividad experiencial ocasional | 10 |
| Independiente/consultor con red en el circuito | 8 |
| Fuera de ICP (screened-out) | 0 |

**FIT_TIER para Brevo** (suma de 1+2): A = 40–50 · B = 25–39 · C = <25.

## 3. Engagement — 0–35 (con decay)

| Señal | Puntos | Decay |
|---|---|---|
| Reply al newsletter o a cualquier email | 15 | Sin decay 90 días, luego −50% |
| Pidió reunión / calendario | 20 (cap de dimensión) | Sin decay |
| Click en link de una edición | 8 por edición (cap 16) | −50% a 30 días |
| Refirió o reenvió a alguien (referral detectado) | 10 | −50% a 60 días |
| Se suscribió por decisión propia (form/lead magnet vs invitación) | 5 una vez | Sin decay |
| Interacción LinkedIn (comment/DM sustantivo) | 6 | −50% a 30 días |
| Open de email | 1 (cap 3) | −100% a 30 días |

**Nota dura sobre opens:** Apple Mail Privacy Protection infla opens — son señal débil por diseño.
Los clicks y replies son la moneda real. Nunca despertar a ventas por opens solos.

## 4. Timing — 0–15

| Señal | Puntos | Decay |
|---|---|---|
| La agencia publica vacante 3D/interactive/spatial | 6 | −50% a 30 días |
| Cuenta nueva ganada / activación anunciada | 6 | −50% a 60 días |
| Cambio de rol del contacto (<90 días) | 5 | 0 a 180 días |
| Ventana de temporada (pre-CES/Coachella/SXSW/holiday para su vertical) | 4 | Expira con la ventana |

## Scoring negativo

| Señal | Puntos |
|---|---|
| Unsubscribe del newsletter | −20 y fuera de envíos (pero sigue siendo prospect 1:1 legítimo) |
| Hard bounce | −15 hasta corregir email |
| Declinó explícitamente (ej. CAA) | −25 y fuera de invitaciones |
| Empleado de estudio competidor (3D real-time in-house) | −50 o descalificar |
| Dato roto sin corregir (los 6 FIX) | Congelado en 0 hasta arreglo |

**Desviación deliberada del default del skill:** NO se penaliza email personal (gmail). En este
mercado los decision-makers brand-side usan gmail personal de forma rutinaria — el SL-26 lo
demuestra (contactos de Amazon, Apple, HBO, lululemon, Microsoft… con gmail). Penalizarlo
mataría señal buena.

## Umbrales y acciones

| Banda | Score | Nombre | Acción |
|---|---|---|---|
| 0–39 | Nurture | Sigue recibiendo el newsletter; nada más | — |
| 40–64 | Warm watch | Touch ligero: like/comment en LinkedIn, sin email extra | Revisión quincenal |
| 65–79 | Sales-ready (el "MQL") | Email personal de Jon en <48h referenciando el contenido clickeado ("saw you read the [X] teardown — working on something similar?") | Semanal |
| 80+ | Hot lane | Pedir llamada/reunión esta semana; si hay NDA/pricing pendiente, cerrar | Inmediato |

Calibración inicial por backtest (paso 3 del skill, con los datos reales del SL-26):

| Contacto real (stage SL-26) | Fit rol | Fit empresa | Engagement seed | Timing | Total | Banda |
|---|---|---|---|---|---|---|
| VP Innovation, agencia Strong, NDA en mesa (Hot) | 25 | 25 | 20 (reunión/NDA) | 4 | ~94 | Hot lane ✓ |
| Senior creative producer, agencia grande, replied + referral | 25 | 18 | 15+10 (cap 35)→33 | 0 | ~76 | Sales-ready ✓ |
| Copywriter, agencia integrada, email-only sin señal | 8 | 10 | 0 | 0 | 18 | Nurture ✓ |

El modelo reproduce el orden del pipeline real → sano para arrancar.

## Operación (sin CRM, con lo que hay)

1. **Semanal (lunes, 20 min):** exportar de Brevo los clicks/replies de la última edición →
   actualizar la hoja de scoring (columna por dimensión, el seed vive en `data/seed-118.csv`) →
   Jon trabaja la banda 80+ ese día y la 65–79 en la semana.
2. **Mensual:** aplicar decay (regla simple: señales de >30 días valen mitad), revisar
   distribución (si "todo el mundo" es sales-ready, subir umbral; si nadie llega, revisar pesos
   — tabla de fallas del skill).
3. **Trimestral:** backtest contra deals reales avanzados; recalibrar pesos con lo aprendido.
4. Cuando haya CRM (o Airtable), migrar la hoja tal cual: las dimensiones ya son columnas.

## La conexión newsletter → ventas (el porqué de todo esto)

El SL-26 dice: 95% de los ALCANZADOS convierten a warm. El scoring convierte cada click en un
"alcanzado" barato: un click en un teardown es una mano levantada que la llamada en frío nunca
logró (29% reach). El seguimiento sales-ready referencia el contenido leído — el email deja de
ser frío por definición. Ese es el bucle: contenido → señal → score → toque personal → pipeline.
