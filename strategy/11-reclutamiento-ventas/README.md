# 11 — Reclutamiento de agentes comerciales a comisión

Misión: contratar 2–3 agentes de ventas a comisión (15–20%) que ya tengan relación directa
con productores de agencias experienciales en LA. **Buscamos personas, no agencias.**

| Doc | Qué resuelve |
|---|---|
| **`EMPIEZA-AQUI.md`** | **El camino corto, sin código. Lee esto primero.** |
| `01-perfil-ideal.md` | Quién es exactamente la persona. 3 arquetipos, descalificadores, scoring 0–25. |
| `02-donde-buscar.md` | Dónde está y cómo sacarla. Filtros Sales Navigator, boolean, canales fuera de LinkedIn. |
| `03-lista-candidatos.md` | Qué salió del Tier A real + qué NO pude verificar y por qué. Protocolo de verificación. |
| `04-mensajes.md` | Mensajes de acercamiento: a candidatos reales, a fuentes de referido, y plantillas por arquetipo. |
| `05-estructura-comision.md` | Sobre qué se paga el 15–20%, cola, registro de cuenta, cuentas de la casa. |
| `07-pipeline-local.md` | **Corre en tu maquina.** Dos pipelines: diff del Internet Archive (gratis) y Apollo (de pago). |
| `06-sourcing-ex-ventas.md` | **Operación a volumen.** 158 agencias, 158 búsquedas listas, triage reclutar-vs-vender, rendimiento esperado. |
| `pipeline_wayback.py` | Diff de paginas de equipo archivadas: quien estaba antes y ya no. Gratis, sin llave. |
| `pipeline_ex_ventas.py` | El pipeline: consulta Apollo por agencia y deja solo a los que ya salieron. |
| `detect_independents.py` | Script reproducible: clasifica señales de independencia en `seed-118.csv`. |
| `data/senales-independencia.csv` | Output del script. 45 filas con señal. |
| `data/candidatos-tracker.csv` | Tracker vacío para el sourcing en vivo. |
| `data/universo-agencias.csv` | 158 agencias consolidadas de 4 fuentes (repo + los 2 PDFs). |
| `data/busquedas-ex-ventas.csv` | Una búsqueda LinkedIn + una X-ray por agencia, priorizadas. |
| `data/perfiles-semilla.csv` | 240 perfiles de LinkedIn del Master List, para verificar y expandir. |

## El hallazgo que cambia el plan

Tu Tier A **no contiene** a la gente que buscas, y no es un defecto de la lista: se construyó
para encontrar **compradores**, así que está llena de gente con empleo fijo. De 118 contactos
verificados, sale **un solo** conector freelance confirmado.

El Tier A sirve para esto, pero en otro rol:
1. Las **44 agencias** de `icp-agencies-wave3.csv` son tu filtro `Past company` en LinkedIn.
   Ese es el input de sourcing que casi nadie tiene y tú sí.
2. Los **21 contactos Tier A** son tus **fuentes de referido**. Ellos saben quién salió.

Ver `03` para el detalle y `02` para la ejecución.

## Regla dura

No reclutar a nadie que hoy trabaje en una cuenta viva de tu pipeline. Sacarle el VP de BD a
NVE te cuesta NVE como cliente — y NVE vale más como cuenta recurrente que como contratación.
Las cuentas bloqueadas están marcadas `PIPELINE-VIVO` en el CSV de señales.
