# Runbook de operación — INMERSIVO / The Signal

Cómo correr, revisar, recuperar y apagar el loop semanal. Para Jon (y para el Claude de turno).

## 1. La semana normal (operación asistida, mientras no hay ingesta automática)

| Cuándo | Qué pasa | Quién |
|---|---|---|
| Jue–Dom | Se deja la edición de la semana en `ediciones-signal/next.json` (schema de `sim/edicion-A.json`, idealmente con `media_plan`) y se hace push | Jon / pipeline de contenido |
| Lun ~8:00 LA | El workflow corre solo: build → publica web → verifica 200 → campaña Brevo | GitHub Actions |
| Lun 8:05 | Con `SEND_MODE=draft`: llega el test interno; revisar checklist (abajo) y dar "Send" en Brevo | Jon |
| Lun 8:10 | Con `SEND_MODE=send`: ya salió solo; verificar en Brevo → Campaigns que el envío esté "Sent" | Jon (1 min) |

Sin `next.json` el lunes = semana sin edición: el workflow termina en verde con un aviso,
no manda nada y no toca estado. Es intencional (mejor callar que mandar relleno).

## 2. Cómo correr en local (setup de dev)

```powershell
cd C:\Dev\SensaLab-Newsletter-Bot
py -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env    # + agregar las vars de strategy/09-ops/env.additions.example

# Build de prueba con una edición real de muestra (no llama LLM, no envía):
python strategy\09-ops\run_weekly.py build --edition sim\edicion-A.json

# Previsualizar la edición web (las rutas de imagen son relativas, se ven bien):
python -m http.server 8000 -d site
# -> http://localhost:8000/01/   (y el archivo en http://localhost:8000/)

# El email queda en out-signal\email-01.html. OJO: sus imágenes son URLs absolutas
# a SIGNAL_PUBLIC_BASE — se verán rotas hasta que la web esté publicada. Es correcto.

# Ensayo de envío sin crear campaña (requiere web ya publicada + keys):
python strategy\09-ops\run_weekly.py send --dry-run
```

Reglas de higiene local (mismas que el bot v1):

- `SEND_MODE=file` en tu `.env` local SIEMPRE. `draft`/`send` solo la nube.
- No correr `send` local con el cron activo: divergirías `signal_state.json` (la numeración).
- `site/` y `out-signal/` son artefactos de runtime → agregarlos a `.gitignore` al integrar.
- En modo `file` el estado NO se toca: puedes correr `build` mil veces sin ensuciar nada.

## 3. Checklist de revisión del borrador (antes de "Send" en Brevo)

1. Remitente `SensaLab <hello@sensalab.io>`, asunto en sentence case (nada en MAYÚSCULAS).
2. Todas las imágenes cargan (logo del masthead incluido).
3. 2–3 links al azar: van a `https://signal.sensalab.io/<NN>/` con `utm_campaign=signal-<NN>`.
4. La edición web abre y se ve bien en móvil (ancho 680, sin scroll horizontal).
5. Guardarriel legal: nada de trabajo pasado del fundador, clientes pasados ni "Cinética"
   (el orquestador ya lo escanea y degrada a draft, pero el ojo humano confirma).
6. Footer: unsubscribe visible, © 2026 SensaLab, Inc., Los Angeles, CA — USA.
7. Solo entonces: Send. (Primeras 3–4 semanas en `draft`; graduar a `send` cuando
   dos ediciones seguidas pasen la checklist sin correcciones.)

## 4. Si algo falla (síntoma → causa probable → acción)

| Síntoma | Causa probable | Acción |
|---|---|---|
| El cron no corrió el lunes | Crons de GitHub son best-effort; o repo sin actividad 60 días (GitHub desactiva schedules) | Actions → "INMERSIVO - The Signal" → Run workflow (manual). El commit semanal de estado normalmente mantiene vivo el cron |
| Step "Construir edicion" rojo | `next.json` inválido (JSON malformado) | Ver el log del step; corregir el JSON y re-run all jobs |
| Muchos `[media] ... sin og:image` | Fuentes sin og:image o bloqueando scraping | No bloquea. Si la edición queda muy pelona: agregar `media_plan` con mejores índices o `poster_url` directo y re-run |
| Step "Publicar web" rojo (401/403) | `PAGES_DEPLOY_TOKEN` expirado o mal scope | Regenerar fine-grained PAT (contents: read+write SOLO en el repo público), actualizar el secret, re-run |
| `send` aborta: "la edicion no responde 200" | Pages aún construyendo, DNS/CNAME mal, `SIGNAL_PUBLIC_BASE` no coincide con el dominio real | Abrir la URL a mano; revisar Settings → Pages del repo público; corregir la variable; re-run all jobs (es seguro: el estado no se incrementó) |
| `[ESP] Brevo: API key invalida (401)` | Key rotada/mal pegada | Regenerar en Brevo → SMTP & API → actualizar secret `BREVO_API_KEY` |
| `[ESP] lista N no accesible` | `BREVO_LIST_ID` no es el ID numérico | Brevo → Contacts → Lists → copiar el ID (número), actualizar la variable |
| Campaña creada pero step murió antes de persistir estado | Ver Brevo ANTES de re-run: si la campaña ya existe, NO re-correr `send` (crearía duplicado). Actualizar `signal_state.json` a mano (issue_no + entrada en editions) y commitear | |
| Imágenes rotas en el email recibido | Se envió antes de que la web viviera (no debería: `wait_live` lo impide) o la imagen pesa demasiado y el cliente la corta | Arreglar la web (ver rollback): el email apunta allá, el fix llega a todos los clics futuros |
| Envío salió con error de contenido | — | Ver sección 5: el email no se puede des-enviar, la web sí se puede corregir |

Códigos de salida de `run_weekly.py`: 0 ok/no-op · 1 falta pieza (edición/meta) · 2 falla
externa (web no viva, ESP) · 3 excepción no manejada.

## 5. Rollback

- **Edición web**: cada edición es una carpeta inmutable en el repo público. Hotfix =
  corregir `site/<NN>/` y re-publicar (re-run del workflow o push directo al repo público).
  Quitar una edición = `git revert` del commit de deploy en el repo público (auditable).
  Como el email apunta a la web, corregir la web ES el rollback efectivo post-envío.
- **Email enviado**: no existe rollback. Mitigaciones por diseño: `draft` como default,
  test interno, `wait_live` antes de crear campaña, guardarriel non-compete. Si salió algo
  grave (legal / links rotos masivos): corregir la web primero; solo mandar fe de erratas
  si el error es legal o funcional — nunca por un typo.
- **Estado**: `git revert` del commit "The Signal: estado ..." en el repo del bot y, si la
  campaña no salió, mover `ediciones-signal/sent/<NN>.json` de vuelta a `next.json`.
- **Pausar el envío pero no el pipeline**: variable `SEND_MODE=file` (todo sigue
  construyéndose y publicándose, no se manda nada).
- **Apagar todo**: Actions → workflow → ⋯ → Disable workflow (o comentar el bloque
  `schedule:` del yml). Reversible en un click.

## 6. Incidente mayor — primeros 15 minutos

1. ¿Se envió algo a la lista? (Brevo → Campaigns → estado). Si no: disable workflow y
   arreglar con calma; nadie vio nada.
2. Si se envió con contenido roto: arreglar `site/<NN>/` (los clics futuros ya llegan bien),
   luego decidir fe de erratas con la sección 5.
3. Si es fuga de secret (key en un log, push accidental de `.env`): rotar la key en el
   proveedor (Brevo/Anthropic/GitHub PAT) ANTES de investigar; las keys viejas mueren primero.
4. Anotar qué pasó en `strategy/09-ops/incidents.md` (crearlo al primer incidente):
   fecha, síntoma, causa raíz, fix, prevención. Cinco líneas bastan.

## 7. Límites y mantenimiento

- **Brevo free**: 300 emails/día. Lista actual ~118 leads: OK. Al pasar de ~280 contactos,
  planear upgrade (Starter) o partir el envío en dos días.
- **Brevo**: verificar dominio remitente (SPF + DKIM en el DNS de sensalab.io) ANTES del
  primer envío real; sin eso, directo a spam.
- **GitHub Pages**: ~100 GB/mes de banda y ~1 GB de repo. Con 5–10 MB/edición hay años.
  TODO opcional: compresión de imágenes (Pillow) en el build.
- **PAT**: los fine-grained tokens expiran (máx 1 año). Poner recordatorio de calendario
  un mes antes; síntoma de expiración = step "Publicar web" rojo con 401.
- **Cron y DST**: GitHub no ajusta horario de verano; revisar el cron en noviembre/marzo
  si "8:00 LA exacto" importa.
- **Cada 3 meses**: abrir el archivo (`signal.sensalab.io`), clicar 2 ediciones viejas,
  confirmar que imágenes y links viven.
