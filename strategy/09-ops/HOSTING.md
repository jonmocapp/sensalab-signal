# Plan de hosting — ediciones web + imágenes de INMERSIVO

Especialista 09 — automatización, hosting & deploy. Estado: listo para ejecutar, costo $0.

## Decisión: GitHub Pages con repo público separado

El bot ya vive en GitHub (repo privado + Actions + estado commiteado). La opción con menos
piezas nuevas es servir la web desde **GitHub Pages de un segundo repo, público, que solo
recibe HTML renderizado + imágenes** (nunca el motor, ni estrategia, ni estado).

| Criterio | GitHub Pages (elegido) | Netlify | Cloudflare Pages |
|---|---|---|---|
| Costo | $0 | $0 (100 GB/mes) | $0 (ancho de banda sin límite práctico) |
| Cuentas nuevas | 0 (solo un PAT) | 1 + token | 1 + token |
| Deploy desde Actions | git push (acción `peaceiris/actions-gh-pages`) | CLI `netlify deploy` | CLI `wrangler pages deploy` |
| Repo privado como fuente | Sí (el público solo recibe el build) | Sí | Sí |
| Dominio propio + HTTPS | Sí (CNAME + cert automático) | Sí | Sí |
| Rollback | `git revert` en el repo público (auditable) | Redeploy de un deploy anterior | Redeploy de un deploy anterior |

Cambiar de host después es barato: la salida del build es una carpeta `site/` estática;
solo se reemplaza el paso de deploy del workflow. Si algún día el DNS de sensalab.io se
mueve a Cloudflare, Cloudflare Pages se vuelve la alternativa natural.

## Estructura de carpetas y URLs resultantes

El orquestador (`run_weekly.py build`) escribe en el repo del bot una carpeta `site/` que
se publica tal cual al repo público (`keep_files: true` conserva ediciones anteriores):

```
repo público: <org>/sensalab-signal   (branch main → Pages)
├── CNAME                       # "signal.sensalab.io" (lo crea GitHub al configurar dominio)
├── index.html                  # archivo del canal (lista de ediciones, lo genera el build)
├── 05/
│   ├── index.html              # edición #05 (The Signal o Teardown, según el cerebro)
│   └── media/
│       ├── sensalab-logo.png   # copiado de assets/ en cada edición (autocontenida)
│       ├── field-notes.jpg     # og:image bajadas por el pipeline de media
│       ├── in-the-lab.jpg
│       ├── craft.png
│       └── video.jpg
└── 06/
    └── ...
```

URLs resultantes:

| Qué | URL final (con DNS) | URL interina (sin DNS) |
|---|---|---|
| Edición #05 | `https://signal.sensalab.io/05/` | `https://<org>.github.io/sensalab-signal/05/` |
| Imagen | `https://signal.sensalab.io/05/media/craft.png` | `https://<org>.github.io/sensalab-signal/05/media/craft.png` |
| Archivo | `https://signal.sensalab.io/` | `https://<org>.github.io/sensalab-signal/` |

Decisiones de URL:

- **Subdominio `signal.sensalab.io`** (recomendado) en vez de `sensalab.io/signal/05`:
  el path en el apex obligaría a proxear desde el host del sitio principal (el proyecto 3D),
  acoplando el newsletter al deploy de la landing. El subdominio es cero acoplamiento.
- **Ediciones inmutables** en `/NN/`: cada carpeta se escribe una vez y no se vuelve a tocar
  (salvo hotfix). Los links de emails viejos nunca se rompen.
- Cuando se configura el dominio propio, GitHub **redirige** las URLs `github.io` viejas al
  dominio nuevo, así que empezar con la URL interina no rompe nada. Aun así: configurar el
  DNS **antes del primer envío real** para que los emails salgan ya con la URL bonita.

## Cómo suben las imágenes (hoy locales) y quedan en URL pública

Hoy: `fetch_media.py` baja las og:image a `sim/out/media/` (local). En producción el flujo
es el mismo mecanismo, con destino distinto:

1. `run_weekly.py build` reutiliza `og_image()` y `download()` de `fetch_media.py` (sin
   editar el motor) y baja cada imagen a `site/<NN>/media/` según el `media_plan` de la
   edición JSON (slot → índice de `sources[]`).
2. Copia `assets/sensalab-logo.png` a `site/<NN>/media/` (cada edición autocontenida).
3. El paso de deploy publica `site/` al repo público → GitHub Pages las sirve por HTTPS.
4. Resultado: `media/craft.png` local se vuelve `https://signal.sensalab.io/05/media/craft.png`.

Rutas en el HTML (clave):

- **Web** (`site/NN/index.html`): se renderiza con `img_base=""` → las rutas quedan
  relativas (`media/craft.png`). Funciona en Pages y también abriendo el archivo local
  o con `python -m http.server` para preview.
- **Email**: los clientes de correo NO resuelven rutas relativas → se renderiza con
  `img_base=f"https://signal.sensalab.io/{NN}/"`, que el motor ya soporta (`_img()` en
  `signal_email.py`).
- **Hallazgo del motor** (sin editarlo): en `build_signal_email()` el parámetro `logo` NO
  pasa por `img_base` (línea `<img src="{_e(logo)}"`), y `compose()` de `build_edition.py`
  no expone `logo`. Si se usara `compose()` tal cual, el logo del email saldría roto.
  Solución del orquestador: llama `choose_format()` + los renderers directamente y pasa
  `logo=f"{web_url}media/sensalab-logo.png"` absoluto al email. Cero cambios al motor.

Peso: las og:image pueden venir de 1–3 MB. Aceptable para la web; para el email es mucho.
TODO opcional (post-lanzamiento): paso de compresión con Pillow (max 1200 px de ancho,
JPEG q80) antes de publicar. Anotado en el runbook.

## Cómo el email apunta a la web

Ya está resuelto en el motor: `signal_email.py` construye cada CTA con
`_url(web_url, issue, slug)` → `https://signal.sensalab.io/05/?utm_source=inmersivo&utm_medium=email&utm_campaign=signal-05&utm_content=<slug>#<slug>`.
El botón de invitación y las tarjetas apuntan todos a NUESTRA edición (regla del brief:
el clic va a nuestro sitio, no a terceros). El orquestador solo tiene que pasar el
`web_url` correcto ANTES de que la página exista — es posible porque la URL es
determinista (`{base}/{NN}/`), y el paso `send` verifica que responda 200 antes de crear
la campaña.

## Configuración una sola vez (checklist para Jon)

1. Crear repo **público** `sensalab-signal` (vacío, branch `main`).
2. Settings → Pages → Source: deploy from branch `main`, carpeta `/ (root)`.
3. Fine-grained PAT (ver README, sección secrets) → secret `PAGES_DEPLOY_TOKEN` en el repo del bot.
4. DNS del dominio: registro `CNAME signal → <org>.github.io.` En el repo público:
   Settings → Pages → Custom domain: `signal.sensalab.io` → esperar el check → activar
   **Enforce HTTPS**.
5. En el repo del bot, variable `SIGNAL_PUBLIC_BASE=https://signal.sensalab.io` y
   `SIGNAL_SITE_REPO=<org>/sensalab-signal`.

Límites del plan gratis (holgados para este uso): repo ~1 GB recomendado, ~100 GB de ancho
de banda/mes, 10 builds/hora. Con ~5 imágenes por semana (~5–10 MB/edición) hay años de
margen; si el repo engorda en unos años, se archivan ediciones viejas.
