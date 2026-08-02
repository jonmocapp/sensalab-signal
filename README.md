# INMERSIVO — Bot de newsletter de SensaLab

Bot 100% en Python que arma y envia el newsletter semanal solo:

**RSS → filtro + anti-repeticion → escritura con la voz SensaLab (Claude) → HTML → envio (MailerLite)**

Corre gratis en la nube (GitHub Actions) cada lunes 8am CDMX. No necesitas tu PC prendida.

---

## Que hace cada archivo

| Archivo | Rol |
|---|---|
| `newsletter_bot.py` | Orquesta todo el pipeline |
| `sources.py` | Fuentes RSS + filtro de keywords + foco geografico + scoring |
| `select.py` | Seleccion + anti-repeticion (estado en `state.json`) |
| `writer.py` | Escribe la edicion con Claude (voz SensaLab + **Lens** obligatorio) |
| `templater.py` | Arma el HTML del correo (email-safe, colores de marca) |
| `sender.py` | Entrega via MailerLite (borrador o envio) |
| `config.py` | Toda la config por variables de entorno |
| `.env.example` | Plantilla de variables (copia a `.env`) |
| `.github/workflows/newsletter.yml` | El cron gratis en la nube |

---

## Prueba local en 3 pasos (sin conectar nada)

```powershell
cd C:\Dev\SensaLab-Newsletter-Bot
py -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 1) Ver que noticias trae y como las selecciona (NO llama a Claude, NO envia):
python newsletter_bot.py --dry-run

# 2) Generar una edicion real en HTML (necesita tu ANTHROPIC_API_KEY):
copy .env.example .env      # edita .env y pon tu key
python newsletter_bot.py    # SEND_MODE=file -> guarda el HTML en ediciones/
```

Abre el HTML de `ediciones/` en el navegador para ver como quedo.

---

## Modos de entrega (`SEND_MODE`)

- **`file`** (default) — solo guarda el HTML. Prueba sin conectar nada. 100% gratis.
- **`draft`** — crea la campana en el ESP como **borrador**; tu la revisas y le das *enviar*.
- **`send`** — crea y **envia** sola. El "1000% automatico".

Recomendacion: arranca en `draft` unas semanas (revisas antes de mandar), luego `send`.

## Proveedor de envio (`PROVIDER`) — LEE ESTO

> ⚠️ **El plan GRATIS de MailerLite NO permite enviar tu HTML propio por API** (eso
> requiere el plan **Advanced**, ~$18+ USD/mes). Todo el diseno de marca depende de mandar
> HTML propio, asi que para el camino gratis usamos **Brevo**.

- **`brevo`** (default, RECOMENDADO) — el plan gratis SI envia campanas HTML por API (300/dia).
- **`mailerlite`** — solo si ya pagas Advanced.

### Conectar Brevo (gratis)
1. Crea cuenta en brevo.com (plan gratis).
2. Verifica tu remitente/dominio (`hello@sensalab.io`).
3. Crea una **lista** y copia su **List ID** (numero).
4. SMTP & API → API Keys → genera una key (`xkeysib-...`).
5. Pon en `.env` (o Secrets de GitHub): `PROVIDER=brevo`, `BREVO_API_KEY`, `BREVO_LIST_ID`,
   `FROM_EMAIL`, `COMPANY_ADDRESS`, `SEND_MODE=draft`.

> Nota: el envio real (draft/send) por API todavia hay que probarlo con tu key —
> lo dejo listo y validado en codigo, pero no pude probar el POST real sin tus credenciales.

---

## Deploy gratis en la nube (GitHub Actions)

1. Sube esta carpeta a un repo **privado** de GitHub (no subas `.env`).
2. Repo → Settings → Secrets and variables → Actions → **New repository secret**. Agrega:
   `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `SEND_MODE`, `PROVIDER`, `BREVO_API_KEY`,
   `BREVO_LIST_ID`, `FROM_NAME`, `FROM_EMAIL`, `COMPANY_LEGAL_NAME`, `COMPANY_ADDRESS`.
   (Si usas MailerLite Advanced: `MAILERLITE_API_KEY`, `MAILERLITE_GROUP_ID`.)
3. Settings → Actions → General → Workflow permissions → **Read and write** (para que el bot
   pueda guardar `state.json`; el yml ya declara `permissions: contents: write`).
4. Listo. Corre solo los lunes. Dispáralo a mano en **Actions** → *Run workflow*.

> Los crons de GitHub son *best-effort* (pueden retrasarse minutos/horas en picos). "8am"
> es una ventana, no un reloj suizo. El commit semanal de `state.json` mantiene el repo
> "activo" y evita que GitHub deshabilite el cron por inactividad (60 dias).

> **Estado local vs nube:** `state.json` esta en `.gitignore`; el workflow lo commitea con
> `git add -f`. No corras `draft`/`send` en tu PC una vez que la nube este activa, o tendras
> dos estados divergentes. Local = solo para probar en modo `file`.

> El workflow hace commit de `state.json` y `ediciones/` para que la anti-repeticion persista
> entre semanas. Por eso el repo debe permitir que Actions escriba (Settings → Actions →
> Workflow permissions → **Read and write**).

Alternativa: Railway/Render con cron — mismo `python newsletter_bot.py`, mismas variables.

---

## Fuentes y reglas

- **Core** (cada edicion): Event Marketer, BizBash.
- **Rotate** (con filtro): Adweek, The Art Newspaper, Social Media Today.
- **Anti-repeticion:** max 5 historias, max 1 por fuente, EM/BizBash alternan el lead
  (EM semanas impares, BizBash pares), Sphere max 2 semanas seguidas, min 2 con foco geo,
  nunca repite una URL ya enviada.

## El Lens (obligatorio)

Cada historia lleva el comentario SensaLab que **siempre** empieza:
> "Para SensaLab, esto le importa a marcas, agencias y empresas porque ..."

Esta baked en el prompt y hay una salvaguarda en el codigo que lo fuerza.

## Guardarrail legal

El prompt prohibe mencionar el trabajo pasado del fundador, clientes pasados o "Cinetica",
y prohibe inventar datos o casos.
