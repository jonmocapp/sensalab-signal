# Sourcing de ex-empleados de ventas a volumen

Actualiza `03-lista-candidatos.md`. Ese doc concluía que el Tier A no contenía candidatos porque
se construyó para encontrar compradores. Los dos PDFs cambian la escala del problema: pasamos de
**44 agencias a 158**, y de 0 a **240 perfiles de LinkedIn** como red semilla.

---

## 1. El giro: el ex-vendedor vale doble

Tu frase — *"de ahí saldrán clientes"* — es la parte importante y conviene formalizarla, porque
cambia la economía del ejercicio.

Cada ex-empleado de ventas que encuentres cae en uno de dos estados, y **los dos sirven**:

| Estado | Qué es | Qué haces |
|---|---|---|
| **Libre / independiente** | salió y no volvió a entrar | **Candidato a agente.** Mensajes de `04`. |
| **Empleado en otra agencia** | salió y aterrizó en otra casa | **Puerta a un cliente nuevo.** Conoce el producto, conoce el hueco, y ahora tiene presupuesto. |

Eso convierte el sourcing en una operación con **rendimiento garantizado**: no hay nombre
desperdiciado. Si no lo contratas, lo vendes. Un ex-BD de NVE que hoy está en Giant Spoon es
exactamente la puerta caliente que el outreach frío nunca te iba a dar.

### La regla que no puedes romper

**El triage va antes del mensaje, no después.**

```
¿Dónde está hoy?
├─ Independiente / freelance / consultor / sin empleador
│     → mensaje de RECLUTAMIENTO (04)
├─ Empleado en una agencia que NO es cuenta viva tuya
│     → mensaje de VENTA. Nunca de reclutamiento.
└─ Empleado en una cuenta viva de tu pipeline
      → no lo tocas. Ni venta ni reclutamiento. (ver 03)
```

Mandar "vente a vender conmigo" a alguien empleado en una agencia objetivo es un intento de
poaching: quema la agencia como cliente y corre el chisme en una industria chica. El costo de
equivocarse aquí es mucho mayor que el de verificar 30 segundos.

---

## 2. El universo: 158 agencias

`data/universo-agencias.csv` — consolidado y deduplicado de cuatro fuentes:

| Fuente | Agencias | Qué aporta |
|---|---|---|
| `icp-agencies-wave3.csv` (repo) | 44 | fit SL-26 scoreado + LinkedIn de empresa |
| `seed-118.csv` (repo) | 74 | agencias con contacto humano ya hecho |
| PDF pipeline — Coachella, en persona | 13 | **las más valiosas: contacto cara a cara** |
| PDF pipeline — DM Instagram + scraping | 51 | cobertura ancha, sin contacto aún |

- 44 con fit SL-26 (29 STRONG / 15 GOOD)
- 34 con URL de empresa en LinkedIn
- 21 aparecen en 2+ fuentes → mayor confianza en que son reales y activas

---

## 3. El motor: 158 búsquedas ya construidas

`data/busquedas-ex-ventas.csv` tiene, **por agencia**, dos URLs listas para pegar en el navegador:

- `busqueda_linkedin` — búsqueda de personas con el nombre de la agencia + títulos de ventas
- `busqueda_google_xray` — X-ray de Google sobre perfiles públicos, acotado a Los Angeles

Títulos que cubren ambas: *business development · new business · account director · client partner
· partnerships · sales*.

### Prioridades

| Prioridad | Agencias | Criterio |
|---|---|---|
| **1** | 41 | fit STRONG, o conocidas en persona en Coachella |
| **2** | 23 | fit GOOD, o presentes en 2+ fuentes |
| **3** | 94 | cobertura ancha |

### El filtro que de verdad importa (hazlo en la UI, no por URL)

LinkedIn gratis **sí** tiene filtro `Past company` en la búsqueda de personas. Es el que aísla
ex-empleados, y no se puede pasar por URL — hay que ponerlo a mano:

> Buscar → **People** → **All filters** → `Past company` = [agencia] · `Locations` = Greater Los
> Angeles Area · `Title` = business development

Y quita de la lista a quien siga teniendo esa agencia como `Current company`. Eso te deja
**solo ex-empleados**, que es exactamente lo que pediste.

Sales Navigator (`02`) agrega lo que gratis no da: *"Changed jobs in the past 90 days"* y
`Years at past company 3+`. Un mes basta para barrer las 41 de prioridad 1.

---

## 4. Rendimiento esperado

Supuestos explícitos — ajústalos cuando tengas datos reales de las primeras 10 agencias:

| Etapa | Supuesto | Resultado |
|---|---|---|
| 158 agencias barridas | 2–5 ex-ventas visibles por agencia en LA | **300–600 nombres** |
| Filtro: salida <24 meses + título real de ventas | 15–25% sobrevive | **50–150 calificados** |
| Split por estado | ~⅓ libres, ~⅔ empleados en otra agencia | **~20–50 candidatos · ~35–100 puertas** |
| Respuesta a mensaje personalizado | 10–20% | **5–20 conversaciones** |
| Cierre | — | **2–3 agentes** + cartera de puertas calientes |

El número que importa no es el primero sino el último de la tercera fila: **35–100 puertas
calientes a agencias nuevas** es, por sí solo, más valor que la contratación. Esa es la parte
que tu instinto ya había visto.

---

## 5. La red semilla: 240 perfiles del Master List

`data/perfiles-semilla.csv` — 240 URLs únicas de LinkedIn extraídas del PDF Master List.

Úsalas de dos formas:
1. **Verificación directa:** abre el perfil, mira si sigue en la agencia o ya salió.
2. **Expansión del grafo:** "People also viewed" de cada perfil lista gente del mismo círculo
   — mismos empleadores, mismos roles. Es la ruta más rápida a nombres que la búsqueda por
   agencia no devuelve porque nunca pusieron el nombre completo de la casa en su perfil.

---

## 6. Qué NO es confiable de los PDFs (dicho explícitamente)

El Master List es una tabla de varias columnas y **no se linealiza bien** al extraer el texto.
Medí el pareo nombre ↔ URL contra el slug de cada perfil: **solo 42% de los pares coincide**.

Consecuencia práctica:

- ✅ **Confiable:** las 240 URLs de perfil. Cada slug identifica a su persona.
- ✅ **Confiable:** el nombre derivado del slug (`/in/taylor-sommer-b81732126` → Taylor Sommer).
- ❌ **NO confiable:** la asociación nombre ↔ rol ↔ agencia que salió del parseo de la tabla.

Por eso `perfiles-semilla.csv` trae las columnas `rol_verificado`, `agencia_verificada` y
`estatus_hoy` **vacías**: se llenan abriendo el perfil, no adivinando. Rellenarlas desde el
parseo habría metido 58% de datos falsos en tu CRM — y esos datos terminan dentro de un mensaje
dirigido a una persona real.

Los emails y agencias de la sección Coachella del PDF de pipeline **sí** son confiables: esa
sección es texto lineal, no tabla.

---

## 7. Cadencia operativa

10 agencias por semana, ~15 minutos cada una. Las 41 de prioridad 1 quedan barridas en un mes.

| Día | Acción |
|---|---|
| Lun | 10 filas de `busquedas-ex-ventas.csv` (prioridad 1 primero). Filtro `Past company` en la UI. |
| Mar | Triage de lo encontrado según el árbol de §1. Anota estado en `candidatos-tracker.csv`. |
| Mié | Verificación (protocolo de 7 pasos en `03`) de los que dieron libres. |
| Jue | Mensajes: reclutamiento (`04`) a libres · venta a puertas. Nunca mezclados. |
| Vie | Seguimientos según la secuencia de 3 toques de `04`. Marca `revisado` en el CSV. |

Registra `encontrados` por agencia en `busquedas-ex-ventas.csv`. Después de 10 agencias vas a
saber tu rendimiento real por agencia, y ahí se recalibra la tabla de §4 con datos tuyos en vez
de mis supuestos.
