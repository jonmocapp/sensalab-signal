# Pipelines para encontrar ex-vendedores

Dos, ordenados por lo que puedes correr hoy. **El primero es gratis, sin llave y sin
LinkedIn.** El segundo da más cobertura pero necesita plan de pago.

Ninguno de los dos raspa LinkedIn. Eso viola su contrato de usuario y la sanción normal es
restricción o cierre de cuenta — y tu LinkedIn *es* el activo del que depende todo este
plan. No vale el intercambio.

---

## 1. Diff del Internet Archive — el que sí puedes correr hoy

### La idea

Las agencias publican su equipo en su propia web. El Internet Archive guarda versiones
viejas de esas páginas. **Quien estaba en la página de equipo de 2023 y no está en la de
hoy, se fue.** Si además su cargo era comercial, es exactamente la persona que buscas.

```
105 agencias con dominio
    ↓  CDX del Internet Archive: snapshots de /team, /about, /people, /leadership
  una foto del equipo por año, 2019 → hoy
    ↓  extrae nombre + cargo de cada ficha
    ↓  diff: estaba antes, no está ahora
  SALIDAS  →  filtra cargos comerciales  →  salidas-detectadas.csv
```

### Por qué este está limpio

- Datos públicos: páginas de marketing que las agencias publican a propósito.
- El Internet Archive tiene API documentada (CDX), abierta y gratuita. **Sin llave.**
- Cada nombre sale con **evidencia**: link al snapshot y fecha. Todo verificable.
- No rodea ningún bloqueo. Es una biblioteca pública consultada como se consulta.

### Correrlo

```bash
pip install requests beautifulsoup4        # bs4 es opcional, pero mejora el parseo

cd strategy/11-reclutamiento-ventas
python pipeline_wayback.py --probar        # autoprueba del extractor, sin red
python pipeline_wayback.py --solo-strong   # las 29 STRONG
python pipeline_wayback.py                 # las 105 con dominio
```

`--probar` corre una autoprueba con HTML de muestra y no toca la red. Ya la dejé pasando
en los dos modos (con y sin bs4): extrae 3 personas de una página de ejemplo, descarta
"Los Angeles" como falso nombre y marca los 2 cargos comerciales. Córrela primero para
confirmar que tu entorno está bien.

### Qué esperar, sin adornos

El extractor es heurístico: busca un nombre propio seguido de algo que parece cargo, que
es como están maquetadas casi todas estas páginas. **No va a funcionar en todas.** Muchos
shops chicos no publican equipo, y algunos sitios montan el equipo con JavaScript, que el
archivo no siempre captura.

Por eso el script escribe **`cobertura-equipos.csv`**: dice agencia por agencia si hubo
historial útil o no. Esperaría señal buena en las agencias medianas y grandes — Jack
Morton, MKTG, Giant Spoon, Allied, Pico, Sparks, BeCore — y poco en los shops de 5
personas. Con que funcione en las grandes ya tienes nombres con fecha de salida, que es
el dato que Apollo *no* te da bien.

### Salidas

| Archivo | Qué trae |
|---|---|
| `data/salidas-detectadas.csv` | nombre, cargo en la agencia, agencia, último año visto, ausente desde, **link al snapshot** |
| `data/cobertura-equipos.csv` | dónde funcionó y dónde no, por agencia |

El cache en `.cache_wayback/` guarda los snapshots: re-correr no vuelve a pedir nada.

---

## 2. Apollo — más cobertura, requiere plan de pago

Ya lo usas: **"Apollo" es la columna de origen de tu Master List** (56 menciones). Su
filtro `q_organization_domains_list` acepta empleador **actual o previo**, que es
literalmente "gente que trabajó en esta agencia".

```bash
export APOLLO_API_KEY=...
python pipeline_ex_ventas.py --probe          # valida con UNA agencia
python pipeline_ex_ventas.py --solo-strong
```

**Corre `--probe` primero.** apollo.io está bloqueado por el proxy de red de mi sesión, así
que no pude validar la API contra tu cuenta. El probe imprime la respuesta cruda con los
nombres de campo; si no coinciden con lo que el script asume, me la pasas y ajusto. También
te dice cuál de las dos rutas de búsqueda responde en tu plan, y si tu cuenta es gratuita
sale un 403 ahí mismo — la búsqueda de personas por API es de pago.

---

## Cómo se complementan

| | Internet Archive | Apollo |
|---|---|---|
| Costo | gratis | plan de pago |
| Llave | no | sí |
| Cobertura | agencias que publican equipo | cualquiera con dominio |
| **Fecha de salida** | **sí, fechada** | no confiable |
| Email / LinkedIn | no | sí |

Se complementan bien: el archivo te dice **quién se fue y cuándo**, Apollo te da **cómo
contactarlo**. Corre el archivo primero porque no cuesta nada, y usa Apollo para
enriquecer los nombres que salgan.

## Las 53 agencias sin dominio

Ninguno de los dos pipelines las cubre. Resuelve sus dominios una vez (están en su
Instagram) y ponlos en la columna `dominio` de `data/universo-agencias.csv`: los dos
scripts los toman solos.

## Después

Los dos dejan las columnas `verificado` y `contactado` vacías a propósito. Abre la
evidencia, confirma, y pásame el CSV: con nombres reales hago el scoring de
`01-perfil-ideal.md` y los mensajes a medida de `04-mensajes.md`.
