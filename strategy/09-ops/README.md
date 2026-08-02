# 09 — Automatización, hosting & deploy

Especialista 09. Misión: llevar INMERSIVO a producción, corriendo solo, con costo $0.
Nada del motor fue editado; todo lo nuevo vive en esta carpeta.

## Qué entregué

| Archivo | Qué es |
|---|---|
| `HOSTING.md` | Plan de hosting: GitHub Pages con repo público separado, estructura de carpetas, URLs (`signal.sensalab.io/05/`), cómo las imágenes locales quedan en URL pública, y cómo el email apunta ahí |
| `run_weekly.py` | Borrador FUNCIONAL del orquestador semanal: edición JSON → media → web + email → verificación → campaña Brevo → estado. Subcomandos `build` / `send` / `all`, con TODOs claros donde faltan piezas/keys |
| `signal-weekly.yml` | Workflow de GitHub Actions (lunes 8:00 LA): build → artifact de revisión → deploy a Pages → verificación + Brevo → persistencia de estado. Para copiar a `.github/workflows/` |
| `RUNBOOK.md` | Operación: semana normal, correr local, checklist pre-envío, tabla síntoma→acción, rollback, incidente mayor, límites |
| `env.additions.example` | Variables nuevas para el `.env` local y para GitHub (Secrets/Variables) |

## El flujo end-to-end (Brevo por API)

```
ediciones-signal/next.json            (hoy: a mano · TODO: ingesta automática)
        │
        ▼
run_weekly.py build                   elige formato (choose_format del motor),
  ├─ site/<NN>/index.html             baja og:images a site/<NN>/media/,
  ├─ site/<NN>/media/*                renderiza web (rutas relativas) y
  ├─ site/index.html                  email (URLs absolutas + logo absoluto)
  └─ out-signal/email-<NN>.html + meta-latest.json
        │
        ▼
peaceiris/actions-gh-pages            publica site/ → repo público → GitHub Pages
        │                             → https://signal.sensalab.io/<NN>/
        ▼
run_weekly.py send                    espera 200 de la edición y del logo,
  ├─ sender.preflight (Brevo)         preflight del ESP,
  ├─ sender.deliver (draft|send)      crea la campaña con el HTML del email,
  ├─ sendTest opcional                test interno al borrador,
  └─ signal_state.json                y SOLO al final persiste numeración + archivo
```

## Decisiones clave

1. **GitHub Pages, repo público separado** (`sensalab-signal`): cero cuentas nuevas, deploy
   auditable por git, rollback = `git revert`. El repo público solo recibe HTML + imágenes
   (nunca motor/estrategia/estado). Netlify y Cloudflare Pages quedan documentadas como
   alternativas de un solo step si Jon prefiere no tener repo público (`HOSTING.md`).
2. **Subdominio `signal.sensalab.io` con ediciones inmutables `/NN/`**: cero acoplamiento
   con la landing 3D; los links de emails viejos no se rompen jamás.
3. **Hallazgo del motor (resuelto sin editarlo)**: en `signal_email.py` el `logo` no pasa
   por `img_base`, y `compose()` no expone `logo` → con `compose()` el logo del email
   saldría roto en producción. `run_weekly.py` llama `choose_format()` + renderers
   directamente y pasa el logo como URL absoluta.
4. **Tres fases separadas (build / deploy / send)** para que un fallo se reintente limpio:
   el email NUNCA se manda sin que la web (y el logo) respondan 200, y el estado solo se
   persiste al final → re-correr el workflow tras un fallo es seguro (misma numeración).
5. **Estado propio (`signal_state.json`)**, separado del `state.json` del bot v1, para no
   corromper la anti-repetición de ese pipeline. Persistido con el mismo patrón
   commit+rebase-retry del workflow v1.
6. **Gate semanal**: sin `ediciones-signal/next.json` no hay edición — el loop calla en vez
   de mandar relleno. Ese archivo es hoy el punto de entrada manual y mañana el output de
   la ingesta automática (mismo contrato).
7. **Secrets con mínimo privilegio**: keys solo en el step que las usa; lo no-sensible va
   en Variables de GitHub, no en Secrets; PAT fine-grained limitado al repo público.
   `config.py` ya maneja el bug de secrets vacíos de Actions (`env() or default`).
8. **`SEND_MODE` con default seguro**: `draft` si nadie dice lo contrario; degradación
   automática a `draft` si el guardarriel non-compete detecta un término prohibido.

## Manejo de secrets y variables (resumen)

| Nombre | Dónde | Para qué |
|---|---|---|
| `BREVO_API_KEY` | Secret | Crear/enviar campañas por API |
| `PAGES_DEPLOY_TOKEN` | Secret | Fine-grained PAT: contents read+write SOLO en `sensalab-signal`; expiración ≤1 año + recordatorio |
| `ANTHROPIC_API_KEY` | Secret | Solo cuando se active la ingesta automática (hoy el loop no llama LLM) |
| `SIGNAL_PUBLIC_BASE` | Variable | `https://signal.sensalab.io` (o la URL interina github.io) |
| `SIGNAL_SITE_REPO` | Variable | `<org>/sensalab-signal` |
| `SEND_MODE` | Variable | `file` → `draft` (semanas 1–4) → `send` |
| `PROVIDER`, `BREVO_LIST_ID`, `FROM_NAME`, `FROM_EMAIL`, `COMPANY_LEGAL_NAME`, `COMPANY_ADDRESS` | Variables | Config no sensible del envío |

Reglas: `.env` jamás a git (ya está en `.gitignore`); rotar cualquier key que toque un log;
GitHub enmascara secrets en logs pero no los pongas en `run:` echo; ante sospecha de fuga,
rotar primero e investigar después (runbook §6).

## Skills que usé (citados)

- **`devops-engineer`** — la columna vertebral: diseño del pipeline CI/CD por fases,
  secrets fuera del código y con mínimo privilegio, procedimiento de rollback documentado
  ANTES de activar, runbook de incidentes, y el patrón "validate → deploy → smoke test
  post-deploy" (aquí: `wait_live` + preflight antes de crear campaña).
- **`deploy-guide`** — su metodología de deploy (pre-flight checks → auth por token en
  CI → deploy → verificación → next steps) aplicada a hosting estático + Brevo; de ahí
  también el patrón de token de CI en secret y la advertencia de expiración/regeneración.
  (El skill es de Webflow; usé su método, no su target.)
- **`local-dev-setup`** — el flujo "assess → init → config → verify" del setup local:
  venv + `.env` desde ejemplo + `env.additions.example` + preview con `http.server` +
  checks de validación (runbook §2). (Ídem: método, no target.)

## Qué funciona HOY vs qué falta

Funciona ya (probado en frío, sin keys): `run_weekly.py build --edition sim/edicion-A.json`
renderiza web + email + archivo con imágenes reales, y `send --dry-run` valida el circuito
hasta antes de crear campaña.

## Qué necesito de Jon

1. **Repo público** `sensalab-signal` + Pages activado (branch `main`, root) — 5 min.
2. **PAT fine-grained** (contents read+write solo sobre ese repo) → secret `PAGES_DEPLOY_TOKEN`.
3. **Brevo**: cuenta free, verificar `hello@sensalab.io` + SPF/DKIM del dominio, crear la
   lista (importar los 118 leads del SL-26 cuando toque) → `BREVO_API_KEY` (secret) y
   `BREVO_LIST_ID` (variable).
4. **DNS**: `CNAME signal → <org>.github.io` — antes del primer envío real (interina
   github.io funciona mientras).
5. Copiar `signal-weekly.yml` a `.github/workflows/` y **pausar el `newsletter.yml` v1**
   (si no, dos correos cada lunes). Agregar `site/` y `out-signal/` al `.gitignore`.
6. Decidir la hora definitiva del cron (hoy: lunes 8:00 LA de verano).
7. **GREEN LIGHT** explícito para cada graduación: `file` → `draft` → `send`.
8. `ANTHROPIC_API_KEY` solo cuando los especialistas de contenido entreguen la ingesta
   automática (TODO(ingesta) en `run_weekly.py`).
