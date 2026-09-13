# Orden 01 — Barrido de salidas en el Internet Archive

**Para:** quien tenga salida a internet (esta sesión de Claude no la tiene: el proxy bloquea archive.org).
**Pide:** Claude, llevando el pipeline de reclutamiento de SensaLab.
**Devuelve a:** Jon, que me lo pega de vuelta a mí.

---

## Qué hay que hacer

Correr un script que ya está escrito y probado. No hay que escribir código ni decidir nada.

```bash
git clone <repo> && cd sensalab-signal/strategy/11-reclutamiento-ventas
pip install requests beautifulsoup4
python pipeline_wayback.py --probar          # 1. autoprueba, sin red (~1 seg)
python pipeline_wayback.py --solo-strong     # 2. el barrido (~20-40 min)
```

## Criterio de éxito

1. **`--probar` imprime `extractor: OK`.** Si no, parar y reportar la salida completa.
2. **El barrido termina** e imprime una línea por agencia. Es normal que muchas digan
   "sin historial útil" — se registra, no es un fallo.
3. Quedan dos archivos en `data/`.

## Qué devolver

Los dos CSV, completos, sin editar:

- `data/salidas-detectadas.csv`
- `data/cobertura-equipos.csv`

Y si algo falló, el texto del error tal cual. **No arregles nada por tu cuenta y no
rellenes celdas vacías**: las columnas `verificado`, `contactado` y `notas` van vacías a
propósito.

## Qué NO hacer

- No tocar LinkedIn. Ni abrirlo, ni rasparlo. Este barrido no lo necesita.
- No inventar ni completar nombres que el script no haya extraído.
- No subir cambios al repo. Solo devolver los dos CSV.

## Contexto, por si ayuda

Las agencias publican su equipo en su web; el Internet Archive guarda versiones viejas.
Quien estaba en la página de equipo de 2023 y no está en la de hoy, se fue. Filtrado a
cargos comerciales, eso es la lista de ex-vendedores que buscamos. Cada fila sale con el
link al snapshot como evidencia.

Detalle completo en `../07-pipeline-local.md`.

---

## Cuando vuelva

Yo me encargo de: deduplicar, puntuar 0–25 según `01-perfil-ideal.md`, cruzar contra las
cuentas vivas del pipeline para marcar a los intocables, y escribir el mensaje a medida de
cada uno según `04-mensajes.md`.
