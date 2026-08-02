# 05 — Plan de 90 días (semana a semana)

> Metodología: `marketing-plan` (roadmap 90 días en fases Unblock → Foundation → Velocity →
> Compound, con dueños y criterios de éxito). Dueño de todo: Jon (+ el motor). Presupuesto: $0
> (Brevo free + hosting estático). Los números de meta vienen del doc 01 §6.

## Fase 1 — Unblock (semanas 1-2): quitar los bloqueos de envío

| Semana | Acciones | Criterio de éxito |
|---|---|---|
| **1** | · Autenticar dominio: SPF, DKIM, DMARC (subdominio de envío news.sensalab.io) en Brevo · Configurar BREVO_API_KEY y sender · Decidir hosting de la edición web (estático; ver BLOG-ROADMAP) y publicar las 2 ediciones sim (A y B) como páginas reales · Página de suscripción mínima (form → Brevo double opt-in) | Un email de prueba llega a inbox (no spam) en Gmail y Outlook; las ediciones A/B tienen URL pública |
| **2** | · Cargar lista semilla: contactos personales + los aliados más cercanos (10-20) · Escribir welcome sequence en Brevo (copy listo en doc 03 §3) · Dry-run completo del pipeline: build → render → send a lista semilla · Checklist legal pre-envío (doc 02 §5) como paso fijo del proceso | Pipeline end-to-end funciona; welcome sequence dispara al opt-in |

## Fase 2 — Foundation (semanas 3-4): lanzar y sembrar la lista

| Semana | Acciones | Criterio de éxito |
|---|---|---|
| **3** | · **Edición #1 real (The Signal)** a la lista semilla · Primera ola de invitaciones 1:1: las 29 agencias Strong fit — email personal de Jon (no masivo): 2-3 líneas + link a la edición #1 publicada ("thought this might be useful — one a week, no pitch") · Mirror en LinkedIn: post con el insight líder + link | Edición #1 enviada un martes 8:30am PT; ≥15 invitaciones personales salieron |
| **4** | · Edición #2 · Segunda ola: 15 Good fit + primeros leads de los 118 · Medir baseline: open, click-to-web, replies · Ajustar asunto/hook según lo aprendido | **≥60 suscriptores ICP, WEIR ≥30**, ≥1 reply |

## Fase 3 — Velocity (semanas 5-8): ritmo + crecimiento de lista

| Semana | Acciones | Criterio de éxito |
|---|---|---|
| **5** | · Edición #3 · Tercera ola de invitaciones (resto de leads 118, por lotes de ~20 con nota personal) · Activar forward ask en el P.S. ("know a producer who'd use this? forward it") | Cadencia intacta; primeras suscripciones no invitadas |
| **6** | · Edición #4 — **primer Teardown si el material lo amerita** (no forzar) · Primer CTA suave de negocio en P.S. (1 de cada 4, doc 02 §6) | Teardown genera ≥2 replies o forwards |
| **7** | · Edición #5 · Revisión de warm readers (lunes, ya como rutina): follow-up 1:1 de Jon a los 5 warm más fuertes ordenados por fit — nota personal referenciando SU actividad (qué clickearon), sin pitch | ≥2 conversaciones 1:1 vivas |
| **8** | · Edición #6 · **Retro de mitad de camino**: WEIR vs meta (65), click-to-web vs 5%, replies vs 6 · Decidir: ¿qué formato/historias ganan clics? → alimentar pesos del cerebro | **≥120 suscriptores ICP, WEIR ≥65, ≥1 meeting booked** |

## Fase 4 — Compound (semanas 9-12): primeras conversiones sistemáticas

| Semana | Acciones | Criterio de éxito |
|---|---|---|
| **9** | · Edición #7 · Lanzar re-engagement para dormidos de la primera ola (doc 03 §5) · LinkedIn: pedir a 3-5 lectores warm que compartan/comenten la edición | Re-engagement recupera ≥15% de dormidos |
| **10** | · Edición #8 · Follow-up 1:1 ronda 2 (siguientes 5 warm fuertes) · Capturar segmento faltante: mini-campaña "one question" a suscriptores sin etiqueta (email 3 de welcome, doc 03 §3) | ≥60% de la lista con segmento capturado |
| **11** | · Edición #9 (segundo Teardown probable) · Preparar "best of quarter" (los 3 links más clickeados) como asset de invitación para olas nuevas y re-engagement | Asset publicado en la web |
| **12** | · Edición #10 · **Retro de trimestre**: funnel completo (suscriptor→warm→conversación→booked), qué olas de invitación convirtieron mejor, qué formato movió warm→conversación · Plan del trimestre 2 (¿ampliar geo? ¿marcas? ¿bifurcar segmentos? — criterios en doc 04 §4) | **≥200 suscriptores ICP, WEIR ≥110, ≥8 conversaciones, ≥3 meetings booked** |

## Reglas de operación del plan

- **La cadencia es sagrada**: ante cualquier conflicto de tiempo, se recorta el alcance de la
  edición (menos items), nunca la fecha.
- **Invitaciones siempre 1:1 y opt-in**: nadie entra a la lista sin aceptar. El volumen de
  invitaciones se ajusta a la capacidad real de Jon de personalizarlas (~15-20/semana).
- **El lunes es de funnel**: 30 min — revisar warm readers, responder pendientes, elegir
  follow-ups de la semana. El martes es de envío. El resto lo hace el motor.
- Cada retro (semanas 8 y 12) alimenta los pesos del cerebro (scoring/formatos) — el loop de
  aprendizaje del motor es parte del plan, no un extra.
