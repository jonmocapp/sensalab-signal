# Pipeline local: sacar ex-vendedores a volumen

## Primero, sobre raspar LinkedIn

Se puede técnicamente. No te conviene, y la razón es tuya, no mía: **el costo del error
lo pagas tú.** El scraping viola el contrato de usuario de LinkedIn, y la sanción normal
es restricción o cierre de cuenta. En una industria de relaciones donde tu LinkedIn *es*
el activo —y donde el plan completo depende de que productores y ex-vendedores te
contesten— perder la cuenta cuesta más que todo lo que el scraper te ahorraría.

Además es innecesario, porque ya pagas la herramienta que hace justo esto.

## El camino que sí: Apollo

En tu Master List, **"Apollo" es la columna de origen** — así encontraste a Lindsay Hall,
Judi Sanders, Peter Matkiwsky y decenas más. Ya lo usas.

Lo que lo vuelve la herramienta correcta para este encargo: el filtro
`q_organization_domains_list` de Apollo acepta **empleador actual o previo**. Eso es
exactamente "gente que trabajó en esta agencia". El pipeline lo aprovecha así:

```
158 agencias (105 con dominio)
    ↓  Apollo: dominio + títulos comerciales + Los Angeles
  personas ligadas a esa agencia (actuales y pasadas)
    ↓  descarta a quien sigue ahí
  EX-VENDEDORES  →  score 0–25  →  ex-vendedores.csv
```

## Puesta en marcha

```bash
pip install requests
export APOLLO_API_KEY=...            # Windows: set APOLLO_API_KEY=...

cd strategy/11-reclutamiento-ventas
python pipeline_ex_ventas.py --probe          # 1. valida con UNA agencia
python pipeline_ex_ventas.py --solo-strong    # 2. las 29 STRONG
python pipeline_ex_ventas.py                  # 3. las 105 con dominio
```

**Empieza por `--probe`, no te lo saltes.** apollo.io está bloqueado por el proxy de red
de la sesión de Claude, así que **no pude probar la API contra tu cuenta**. El probe
consulta una sola agencia e imprime la respuesta cruda con los nombres de campo.
Si no coinciden con lo que el script asume (`name`, `title`, `organization`,
`linkedin_url`), pásame esa salida y ajusto `empleador_actual()` y `puntua()` en un minuto.

Dos detalles que el probe también resuelve: Apollo ha servido la búsqueda de personas en
`/mixed_people/search` y en `/mixed_people/api_search` según plan — el script prueba las
dos y se queda con la que responda. Y la búsqueda de personas por API requiere plan de
pago; si tu cuenta es gratuita, el probe te lo va a decir con un HTTP 403.

## Lo que cuesta y lo que devuelve

- **Créditos:** las respuestas se guardan en `.cache_apollo/`, así que re-correr no vuelve
  a cobrar. Ajusta el ritmo con `--pausa` si topas el límite de tasa.
- **Cobertura:** 105 de 158 agencias tienen dominio, incluidas **28 de las 29 STRONG**.
  Los dominios los reconstruí de los emails de `seed-118` y del PDF de pipeline.
- **Salida:** `data/ex-vendedores.csv` con score, nombre, título en la agencia, dónde está
  hoy, LinkedIn, email y ciudad — ordenado por score, con columnas vacías para que marques
  `verificado` y `contactado`.

## Las 53 agencias sin dominio

Para esas va el camino manual que ya está en `02-donde-buscar.md`: LinkedIn →
**All filters → Past company** = la agencia, **Locations** = Greater Los Angeles Area.
Es el mismo filtro que usa el pipeline, hecho a mano. Sales Navigator agrega
*"Changed jobs in the past 90 days"*, que es literalmente "salió hace poco".

Si quieres cerrar esas 53, la vía barata es resolver sus dominios una vez (están en sus
Instagram o en una búsqueda) y meterlos en la columna `dominio` de
`data/universo-agencias.csv`. El pipeline los toma solo.

## Después del barrido

Lo que Apollo **no** te da con confianza es la fecha de salida ni los años de casa —
las dos dimensiones que más pesan en el score de `01-perfil-ideal.md`. Por eso el script
asigna un valor neutro en frescura y deja `verificado` vacío: eso se confirma abriendo el
perfil, y son segundos por persona cuando ya tienes la lista corta.

Pásame el CSV cuando corra y hago el scoring fino y los mensajes a medida por persona.
