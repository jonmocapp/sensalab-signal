# Registros DNS listos — sensalab.io (envío con Brevo)

Objetivo: SPF + DKIM + DMARC alineados para que INMERSIVO llegue a inbox, sin arriesgar el correo
normal de `hello@sensalab.io`.

**Decisión de arquitectura (recomendada): enviar el newsletter desde el subdominio `news.sensalab.io`**
(remitente `hello@news.sensalab.io`, reply-to `hello@sensalab.io`). Si el subdominio quemara
reputación, el dominio raíz y el buzón principal quedan intactos. Es la práctica estándar
("no envíes bulk desde tu dominio primario").

> Los valores marcados `<-- DASHBOARD` los genera Brevo al autenticar el dominio
> (Settings → Senders, domains & dedicated IPs → Domains → Authenticate). Copia los del dashboard;
> aquí está el formato exacto esperado para que sepas qué vas a pegar y por qué.

---

## Bloque A — subdominio de envío `news.sensalab.io` (recomendado)

| # | Host (nombre) | Tipo | Valor | TTL | Qué hace |
|---|---------------|------|-------|-----|----------|
| 1 | `news.sensalab.io` | TXT | `brevo-code:xxxxxxxxxxxxxxxxxxxx` `<-- DASHBOARD` | 3600 | Prueba de propiedad del dominio ante Brevo. Sin esto no puedes autenticar. |
| 2 | `b1._domainkey.news.sensalab.io` | CNAME | `b1.news-sensalab-io.dkim.brevo.com` `<-- DASHBOARD` | 3600 | DKIM llave 1. Firma criptográfica: prueba que el email salió autorizado por ti y no fue alterado. |
| 3 | `b2._domainkey.news.sensalab.io` | CNAME | `b2.news-sensalab-io.dkim.brevo.com` `<-- DASHBOARD` | 3600 | DKIM llave 2 (Brevo usa doble llave para rotación). |
| 4 | `news.sensalab.io` | TXT | `v=spf1 include:spf.brevo.com -all` | 3600 | SPF: declara que SOLO Brevo puede enviar como `@news.sensalab.io`. `-all` (hard fail) es seguro aquí porque nadie más envía desde este subdominio. |

Notas:
- Si el wizard de Brevo te muestra el formato legado en lugar de b1/b2, será:
  `mail._domainkey.news.sensalab.io` TXT `k=rsa;p=MIGfMA0GCSqGSIb3...` `<-- DASHBOARD`. Es equivalente; pega el que te dé.
- Solo puede existir **un** registro SPF por host. Si ya hubiera un TXT `v=spf1...` en `news`, se fusiona, no se duplica.

## Bloque B — DMARC en el dominio raíz (cubre también los subdominios)

| # | Host (nombre) | Tipo | Valor | TTL | Qué hace |
|---|---------------|------|-------|-----|----------|
| 5 | `_dmarc.sensalab.io` | TXT | `v=DMARC1; p=none; rua=mailto:dmarc@sensalab.io; fo=1; adkim=r; aspf=r` | 3600 | DMARC en modo monitor: no bloquea nada todavía, pero te manda reportes agregados de quién envía usando tu dominio. Gmail/Yahoo lo exigen desde feb 2024 y Microsoft desde may 2025. |

Progresión (no saltarse pasos — el skill lo marca como error #1):
1. **Semanas 1–4:** `p=none` — solo observar reportes.
2. **Cuando 2–4 semanas de reportes salgan limpios:** subir a `p=quarantine; pct=100`.
3. **Tras 4 semanas más limpias:** `p=reject`.
- Regla dura: **un solo registro DMARC** con tag `rua`. Si Brevo te sugiere añadir su propio buzón de
  monitoreo, se agrega al MISMO registro: `rua=mailto:dmarc@sensalab.io,mailto:rua@dmarc.brevo.com`.
- Crea el alias `dmarc@sensalab.io` (o usa el digest semanal gratis de Postmark:
  registrarse en `dmarc.postmarkapp.com` y usar el `rua` que te den).

## Bloque C — dominio raíz `sensalab.io` (protege el buzón hello@)

| # | Host (nombre) | Tipo | Valor | TTL | Qué hace |
|---|---------------|------|-------|-----|----------|
| 6 | `sensalab.io` | TXT | `v=spf1 include:_spf.google.com ~all` *(si hello@ está en Google Workspace — CONFIRMAR con Jon)* | 3600 | SPF del dominio raíz para el correo normal. Sin esto, hasta las respuestas 1:1 de Jon pueden caer a spam. |
| 7 | DKIM del proveedor del buzón | TXT/CNAME | El que genere Google Workspace (Admin → Apps → Gmail → Authenticate email) u otro proveedor | 3600 | Firma DKIM del correo cotidiano. |

- Si `hello@sensalab.io` NO está en Google Workspace, sustituir el include por el del proveedor real
  (Zoho: `include:zohomail.com`, Microsoft 365: `include:spf.protection.outlook.com`).
- NO añadir `include:spf.brevo.com` al raíz si el newsletter sale del subdominio — mantiene los
  lookups bajos (límite: 10) y las reputaciones separadas.

## Bloque D — tracking de clics con marca propia (cuando haya plan de pago)

| # | Host (nombre) | Tipo | Valor | TTL | Qué hace |
|---|---------------|------|-------|-----|----------|
| 8 | `links.news.sensalab.io` | CNAME | el destino que indique Brevo al activar custom tracking `<-- DASHBOARD` | 3600 | Los links trackeados se reescriben con TU dominio en vez del dominio compartido de Brevo (los dominios de tracking compartidos heredan la reputación de otros remitentes). |

En plan gratis Brevo usa su dominio compartido de tracking: aceptable para el arranque con
volumen bajo; migrar a custom tracking al pasar a plan pago.

---

## Cómo verificar (después de 15 min – 48 h de propagación)

Desde PowerShell:

```powershell
nslookup -type=TXT news.sensalab.io          # debe mostrar brevo-code y v=spf1 include:spf.brevo.com
nslookup -type=CNAME b1._domainkey.news.sensalab.io
nslookup -type=CNAME b2._domainkey.news.sensalab.io
nslookup -type=TXT _dmarc.sensalab.io        # debe mostrar v=DMARC1; p=none...
nslookup -type=TXT sensalab.io               # un solo v=spf1
```

Online:
- MXToolbox: `mxtoolbox.com/SuperTool.aspx` → pestañas SPF / DKIM / DMARC / blacklist.
- En Brevo: botón **Authenticate** del dominio debe quedar en verde (Brevo re-chequea solo).
- Prueba final integral: enviar un test a `mail-tester.com` → objetivo **≥ 9/10** y ver
  SPF `pass`, DKIM `pass`, DMARC `pass` con dominio alineado.

## Errores comunes que evitar (del skill)

- Dos registros SPF en el mismo host → solo se lee uno y falla la validación. Fusionar siempre.
- Pasar DMARC directo a `p=reject` sin monitorear → bloqueas tu propio correo legítimo.
- Más de 10 lookups DNS en el SPF → SPF permerror. Por eso raíz y subdominio van separados.
- Olvidar el DKIM de un proveedor: cada plataforma que envía por ti necesita SU DKIM.
