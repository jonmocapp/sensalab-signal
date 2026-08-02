# Matriz de riesgos — INMERSIVO (legal / marca / reputación)

Especialista 08. Severidad = impacto si ocurre. Prob. = probabilidad con el sistema ACTUAL
(antes de aplicar las mitigaciones de los docs 01-04). Exposición = severidad × probabilidad,
que es lo que ordena la tabla.

| ID | Riesgo | Tipo | Sev. | Prob. actual | Exposición | Mitigación (doc) | Prob. residual |
|----|--------|------|------|--------------|------------|------------------|----------------|
| R1 | Violación del non-compete: "Cinética" o alusión a trabajo/clientes pasados llega a un envío. Consecuencia: acción legal contractual contra el fundador + munición permanente en manos del ex-empleador. | Legal + existencial | Crítica | Media (el gate actual NO escanea el formato real: huecos #1-#2 del doc 03) | **La más alta del proyecto** | Gate multicapa bloqueante + revisión humana tipada + auditoría (doc 03, forbidden-terms.txt) | Muy baja |
| R2 | Copyright de imágenes: og:images de Warner/DreamWorks/Fox/Getty-likes en un email comercial y hospedadas en sensalab.io. DMCA, demand letter, daños estatutarios. | Legal + reputación | Alta | Alta (los assets actuales de sim/out/media/ ya son de terceros) | Muy alta | Assets propios/licenciados + campo `license` en manifest + gate (doc 04 §3) | Baja |
| R3 | CAN-SPAM: envío sin dirección postal física válida (hoy solo "Los Angeles, CA — USA"). Hasta ~$53k por email teóricos; realista: complaints + flag del ESP. | Legal | Alta | Certeza si se envía hoy | Alta | Mailbox CMRA + slot en footer + checkbox del gate (doc 01 §1.4) | Nula (es binario) |
| R4 | Import de los 118 leads SL-26 a Brevo sin consentimiento: suspensión de cuenta Brevo (violación de sus términos), spam complaints de decision-makers del ICP — la audiencia exacta que no podemos quemar. | Contractual + marca | Alta | Media (la tentación operativa existe; hoy nada lo impide) | Alta | Política lista-solo-opt-in + flujo 1:1/LinkedIn/DOI (doc 02 §3) | Baja |
| R5 | "SensaLab®" sin registro USPTO y/o "SensaLab, Inc." sin constitución: false marking, representación societaria falsa; debilita reclamos futuros de marca. | Legal | Media | Desconocida (pendiente verificación de Jon) | Media | Verificar registro/acta; fallback ™ y "© 2026 SensaLab" (doc 04 §1) | Nula tras verificar |
| R6 | Claim fáctico inventado o sin fuente pasa a un envío (alucinación del writer): pérdida de la credibilidad que ES el producto; corrección pública. | Reputación | Media | Baja-media (writer.py:73-74 lo prohíbe; sin enforcement automático) | Media | Detector F1 números↔fuentes + regla de hedges atribuidos (docs 03 §3.3, 04 §2) | Baja |
| R7 | Teardown cruza de crítica de obra a ataque a personas/estudio (defamación): edición B critica el teaser de Shrek 5. | Legal + reputación | Media | Baja (la copy actual está bien encuadrada) | Baja-media | Reglas de fair comment: obra sí, personas no; hechos con fuente (doc 04 §2.1) | Baja |
| R8 | Deliverability/reputación de dominio: sensalab.io sin SPF/DKIM/DMARC alineados, o spam-rate >0.3% por lista fría → spam folder permanente para TODO correo de SensaLab (incluido el comercial 1:1). | Técnico + marca | Media | Media | Media | Autenticación en Brevo + DOI + lista limpia (docs 01 §1.1, 02) | Baja |
| R9 | CASL: algún lead SL-26 resulta canadiense y recibe email sin consentimiento expreso (multas hasta CAD $10M, régimen estricto). | Legal | Media | Baja (pipeline LA; no auditado por país) | Baja-media | Filtro por país; canadienses solo vía DOI (doc 01 §4) | Muy baja |
| R10 | Asociación implícita con marcas/eventos cubiertos (FIFA, Cosm, Warner): un lector u organizador entiende patrocinio u participación donde no la hay. | Marca | Media | Baja (copy actual es claramente editorial) | Baja | Prohibido logos/key art/“official/partner”; uso nominativo en texto solamente (doc 04 §2.3) | Muy baja |
| R11 | GDPR: suscriptor UE entra a la lista y pide borrado/queja. | Legal | Baja | Baja | Baja | DOI con log de consentimiento + DPA Brevo + proceso de borrado 30 días (doc 01 §2) | Muy baja |
| R12 | Handles sociales del footer (instagram.com/sensalab, etc.) no controlados por SensaLab: tráfico del newsletter aterrizando en cuenta ajena. | Marca | Baja | Desconocida | Baja | Verificación única de los 3 handles antes de la edición #05 (doc 04 §1) | Nula tras verificar |
| R13 | CCPA: petición de derechos de un contacto californiano. | Legal | Baja | Muy baja (bajo umbrales; ver doc 01 §3) | Muy baja | Privacy policy + honrar peticiones aunque no obligue | Muy baja |

## Lectura ejecutiva

- **Bloqueantes del primer envío (no negociables):** R1 (gate), R2 (imágenes), R3 (dirección).
  Los tres tienen fix concreto y barato; ninguno requiere abogado para resolverse, solo
  ejecución.
- **La regla que previene R4 cuesta $0:** los leads no se importan; se les invita. Está
  escrita en doc 02 §3 precisamente para el día en que haya prisa.
- **Verificaciones de una sola vez (Jon, <1h total):** R5 (registro/acta), R12 (handles),
  R9 (país de los 118), R13 (umbral de ingresos).
- **Riesgo aceptado conscientemente:** usar un frame mínimo del material criticado en
  teardowns bajo fair use (doc 04 §3.3) — defendible, documentado, y solo en ese contexto.
