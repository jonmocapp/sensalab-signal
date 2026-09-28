# La lista: qué salió del Tier A y qué no

## Primero, lo que no pude hacer

Pediste nombres de ex-empleados de tus agencias Tier A, con tenure y situación actual.
**No los puedo entregar verificados**, y prefiero decírtelo antes que entregarte una lista bonita.

- Ese dato vive en perfiles de LinkedIn detrás de login. No tengo acceso.
- Probé búsqueda web pública sobre NVE, MKG y Giant Spoon: devuelve vacantes y perfiles de empresa,
  no historiales de carrera de personas.
- Inventar los nombres rompería tu propia regla del BRIEF (*"no inventes datos"*) y sería
  **peor que no entregar nada**: mandarías un mensaje afirmando la carrera de una persona real,
  con datos falsos. Eso quema al candidato y te quema a ti en una industria de 200 personas que
  se conocen entre sí.

Lo que sí hice: correr un script reproducible (`detect_independents.py`) sobre tus 118 contactos
verificados, y convertir el Tier A en el motor de sourcing de `02`.

---

## El hallazgo: tu Tier A no contiene a esta gente, y tiene sentido

De 118 contactos verificados sale **un solo conector freelance confirmado**.

No es un defecto de la lista. La lista se construyó para encontrar **compradores**, entonces está
llena — por diseño — de gente con empleo fijo en agencias y marcas. Los independientes que sí
tiene son mayormente creativos (DREAMER) y brand-side, no conectores agency-side.

**El Tier A sirve, pero en otro rol:**

| Activo | Rol viejo | Rol nuevo para este encargo |
|---|---|---|
| 44 agencias scoreadas | lista de cuentas objetivo | **filtro `Past company`** en Sales Navigator |
| 21 contactos Tier A | leads de venta | **fuentes de referido** — saben quién salió |

Ese es el verdadero "partir del Tier A".

---

## Cómo leer las señales del script

| Señal | Qué significa | Peso |
|---|---|---|
| `INDEPENDIENTE-EXPLICITO` | el rol dice freelance / fractional / independent | Confirmado |
| `DOMINIO-PROPIO-NOMBRE` | el dominio del email lleva su nombre (`leila@leilababoi.com`) | **Fuerte** — registrar un dominio con tu nombre es lo que hace quien construye identidad propia |
| `DOMINIO-NO-COINCIDE` | el email no cuadra con la empresa declarada | Anomalía: puede ser transición **o dato sucio**. Verificar. |
| `FREEMAIL` | gmail / me.com | **Débil, casi ruido.** Suele significar solo que quien armó la lista encontró un correo personal. No es evidencia de nada. |

---

## Candidatos reales de tu dataset

Son pocos y lo honesto es decirlo. Ninguno es el arquetipo A de `01`. Ordenados por utilidad real.

### 1. Juliane Kringe — el único conector freelance confirmado
- **Dónde está hoy:** Freelance, *Global Brand & Marketing Consultant*. `hello@julianekringe.com`
- **En tu data:** `IN-COLD`, tier C, familia CONNECTOR, estado Email-only.
- **Por qué sirve:** es la única fila que cruza freelance confirmado + rol de conector. Dominio propio.
- **Qué NO sabes y tienes que verificar:** si su rolodex es de **productores de agencia** o
  brand-side. Un consultor de brand marketing global puede no tocar nunca a un EP de experiencial.
- **Score estimado:** sin verificar. Frescura y disponibilidad altas; proximidad al productor
  desconocida — esa dimensión decide si vale o no.

### 2. Storme Whitby-Grubb — fractional, ya vive de ingreso variable
- **Dónde está hoy:** Wild Duchess, *Fractional Chief Creative Officer & Founder*. `storme@wildduchess.com`
- **En tu data:** `BR-COLD`, tier B, familia DREAMER.
- **Por qué sirve:** "fractional" significa que ya se vende a sí misma por proyecto y tolera el
  modelo de comisión sin que haya que convencerla. Perfil de fundadora.
- **Contra:** DREAMER, no CONNECTOR. Vende visión creativa, no capacidad técnica white-label.
- **Uso más probable:** mejor fuente de referidos que agente. Conoce el circuito de independientes.

### 3. Ez Blaine — señal de transición en un puesto grande
- **Dónde está hoy:** figura como Chief Creative Officer en Huge, pero usa `ez@ezblaine.com`.
- **Por qué mirarlo:** un CCO de una agencia global operando desde su dominio personal es el patrón
  clásico de alguien que ya está construyendo lo que sigue. Verificar estatus actual antes de nada.
- **Contra:** si sigue en Huge, está fuera de alcance. Y un CCO rara vez acepta un rol de comisión.

### 4. Fundadores de shop propio — fuentes de referido, no agentes
Yulia Graham (`YULIA`), Haley Bergman (`Haley Bergman Creative`), Jody Friedericks
(fundadora, The Designtist Group). Ya tienen negocio propio: **no van a vender para ti**, pero
están en el circuito y refieren. Trátalos como red, no como candidatos.

### Descartados con motivo
- **Gabe Sanchez** (Independent, freelance): en tus notas está marcado como *cliente potencial* de
  motion graphics. Es demanda, no oferta.
- **Eddie J Brannan** (Independent, Freelance CD): email con typo (`gmal.com`), tier C, DREAMER.
- **Los 23 `FREEMAIL`:** señal demasiado débil para actuar. Tratarlos como candidatos sería
  inventar con pasos extra.

---

## Regla dura: a quién NO tocar

**No reclutes a nadie que hoy trabaje en una cuenta viva de tu pipeline.** Sacarle el VP de BD a
NVE te cuesta NVE como cliente, y una agencia Strong recurrente vale más que una contratación.

Marcados `PIPELINE-VIVO` en `data/senales-independencia.csv`. Los críticos:

| Persona | Cuenta | Por qué está bloqueado |
|---|---|---|
| **Neel Kar** | Petrol Advertising | HOT, NDA enviado, esperando pricing. **No lo toques ni para pedirle un referido** hasta que cierre. |
| **Catherine Cannon** | NVE Experience Agency | VP de BD de una Strong. Es exactamente el perfil que quieres — y por eso mismo es la contratación más cara que podrías hacer. |
| **Ben Kinnear** | Spacecube | BD Manager, respondió "all of the above". Cuenta viva. |
| **Leila Baboi** | Accenture Song | Tier A, warm, case studies enviados. Tiene dominio propio, pero es cuenta en curso. |
| **Amanda Azoroh** | Omnicom Production | Nota explícita: *"NO llamar; ella contacta"*. Respétalo. |
| **Joe McLaren, Dickson Au, Mikette Miller** | Wasserman / OBE / Team One | Cuentas warm activas. Sirven como **fuentes de referido**, no como candidatos. |
| **Danielle Oxford** | CAA | Declinó contacto explícitamente. Fuera de todo. |

---

## Protocolo de verificación (antes de escribirle a cualquiera)

Corre esto por candidato. Si falla 1 o 2, no escribas.

1. **Estatus actual** — ¿el perfil dice self-employed / freelance / consultant, o sigue con
   empleador? Si sigue empleado en una Strong, ¿es cuenta de tu pipeline? Si sí → fuera.
2. **Tenure** — ¿3+ años en UNA agencia Strong/Good? Anota fechas exactas del perfil.
3. **Fecha de salida** — ¿dentro de 24 meses? ¿En el punto dulce de 3–12?
4. **Prueba de proximidad al productor** — ¿su historial muestra que trabajó *con* EPs, o solo
   cerca de ellos? Busca créditos de activación compartidos.
5. **Base geográfica** — LA/SoCal, disponible en persona.
6. **Restricciones** — pregunta en la primera llamada si tiene non-solicit vigente con su ex-empleador.
   California anula ampliamente los non-competes (B&P §16600, reforzado por SB 699 / AB 1076 en 2024),
   pero las cláusulas de no-solicitación de clientes y los reclamos por secreto comercial tienen
   matices. **No es asesoría legal — valídalo con tu abogado antes de firmar.** Regla operativa
   simple: nunca le pidas que traiga listas ni archivos de su ex-empleador.
7. **Score 0–25** (`01`). Registra en `data/candidatos-tracker.csv`.

---

## Qué hacer el lunes

| # | Acción | Tiempo | Rendimiento esperado |
|---|---|---|---|
| 1 | Mensaje de referido a Patrick Justice y Joe McLaren (`04`) | 20 min | **El más alto.** Son warm y ya refirieron antes. |
| 2 | Línea de reclutamiento en el footer de INMERSIVO | 10 min | Continuo, costo cero |
| 3 | Un mes de Sales Navigator + el stack de filtros de `02` | 2 h | 15–40 nombres calificados |
| 4 | Verificar a Juliane Kringe y Ez Blaine | 30 min | 2 decisiones binarias |
| 5 | Diff de rosters It List / BizBash, las 29 Strong | 3 h | Tenure y salida verificables sin Sales Nav |

El punto 1 antes que el 3. El referido llega pre-calificado por alguien en quien el candidato ya
confía; el sourcing en frío te devuelve a tu problema original — que el outreach frío no funciona.
