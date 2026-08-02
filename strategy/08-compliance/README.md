# 08 — Compliance, legal & brand safety

Especialista 08 del BRIEF MAESTRO. Misión: que INMERSIVO se pueda enviar sin riesgo legal ni
de marca. Todo auditado contra los archivos reales del motor (rutas y líneas citadas en cada
doc). **No edité ningún .py** — las integraciones al motor quedan especificadas para quien
lo opere.

## Skills usados
- **`careful`** — modo guardarriel activo durante toda la auditoría: cero operaciones
  destructivas, cero ediciones al motor, solo lectura del código y escritura en esta carpeta.
- **`safe-publish`** — su metodología de publicación (preview completo → validaciones →
  confirmación tipada explícita, nunca "yes" → verificación y reporte post-publish) está
  adaptada de Webflow a Brevo como el flujo humano del gate de pre-envío (doc 03 §3.4).
- **`review`** — marco de revisión con evidencia: cada hallazgo cita archivo:línea que lo
  motiva, y los claims de la copy se auditaron contra sus fuentes (doc 04 §2). Los huecos
  del gate se verificaron con grep, no por suposición.

## Entregables

| Archivo | Qué contiene |
|---|---|
| `01-checklist-can-spam-gdpr.md` | Checklist CAN-SPAM punto por punto con estado real ([OK]/[GAP]/[VERIFICAR]), cómo cumplir cada gap con Brevo, e higiene GDPR/CCPA/CASL. |
| `02-flujo-consentimiento-optin.md` | Decisión single vs double opt-in (DOI, con razones), setup Brevo, y el flujo para convertir los 118 leads SL-26 en suscriptores sin quemarlos ni violar los términos de Brevo. |
| `03-gate-noncompete.md` | Política non-compete en 3 clases (nombre / alusión / invento), los 4 huecos verificados del gate actual, y el spec completo del gate de pre-envío bloqueante (4 superficies, normalización anti-evasión, 3 detectores + 2 flags advisory, revisión humana tipada, auditoría). |
| `forbidden-terms.txt` | Lista prohibida versionable: términos exactos ES/EN, variantes de evasión, patrones regex de alusión, y allowlist del detector difuso con justificaciones. |
| `04-footer-claims-imagenes.md` | Revisión legal del footer (®, "Inc.", dirección), auditoría claim-por-claim de las ediciones A y B contra sus fuentes, y el análisis de riesgo de las imágenes og:image de terceros con la escalera de reemplazo. |
| `05-matriz-riesgos.md` | 13 riesgos con severidad, probabilidad actual, exposición y mitigación, ordenados por exposición real. |

## Decisiones clave

1. **Tres bloqueantes del primer envío:** (a) el gate non-compete hoy NO cubre el formato
   real — `build_edition.py` nunca llama a `scan_forbidden`, y `scan_forbidden` lee el esquema
   viejo, no `hero/sections/teardown` (verificado: writer.py:147-157, grep 0 matches en
   build_edition.py); (b) las imágenes actuales de `sim/out/media/` son og:images de
   Warner/DreamWorks/Fox/Cosm — no pueden salir en un email comercial; (c) el footer no tiene
   dirección postal física válida para CAN-SPAM (solo "Los Angeles, CA — USA").
2. **La lista es opt-in o no es.** Los 118 leads del SL-26 no se importan a Brevo jamás
   (términos de Brevo + deliverability + marca); se convierten vía invitación 1:1, LinkedIn
   y double opt-in. El contenido es público en la web — nadie necesita estar en la lista
   para recibir el link.
3. **Gate antes que draft.** Orden obligatorio: escaneo limpio → draft en Brevo → aprobación
   humana tipada (`PUBLICAR`) → sendNow del contenido con el mismo SHA-256 aprobado. El flujo
   actual crea el draft en Brevo aunque haya término prohibido (newsletter_bot_v2.py:81-86) —
   invertido en el spec.
4. **La copy actual está sana.** Auditoría claim-por-claim de A y B: todo hecho externo traza
   a `sources[]`, los hedges están bien puestos ("billed as a first", "roughly 40") y no hay
   una sola alusión a historial propio. El problema legal de las ediciones no es el texto:
   son las imágenes.

## Qué necesito de Jon (todo <1h salvo el mailbox)

1. **Mailbox CMRA en LA** (iPostal1/Anytime/UPS Store, ~$10-30/mes) → `COMPANY_ADDRESS` en
   `.env` + perfil de empresa en Brevo. Bloquea el primer envío.
2. **DNS de sensalab.io**: registros SPF/DKIM/DMARC que Brevo genere al autenticar el dominio.
3. **Confirmaciones de una vez**: ¿existe registro USPTO de "SensaLab" (si no → ™)? ¿existe
   "SensaLab, Inc." constituida (si no → "© 2026 SensaLab")? ¿los handles
   instagram.com/sensalab, linkedin.com/company/sensalab, youtube.com/@sensalab son nuestros?
   ¿algún lead del SL-26 es canadiense?
4. **Publicar `sensalab.io/privacy`** antes de abrir el formulario de alta.
5. **Decisión de assets**: aprobar que las ediciones #05/#06 se re-ilustren con assets
   propios/tipográficos antes del envío (doc 04 §3).
