# -*- coding: utf-8 -*-
"""
run_weekly.py — BORRADOR (especialista 09) del orquestador del loop semanal de INMERSIVO.

Pipeline:  edicion JSON -> media -> compose (web + email) -> hospedar -> verificar -> Brevo -> estado

Fases (subcomandos), pensadas para que el workflow pueda reintentar cada una por separado:

  build   Lee la edicion JSON (schema de sim/edicion-*.json), baja las imagenes reales
          (og:image de las fuentes) a site/<NN>/media/, decide formato con el cerebro
          (choose_format), renderiza la edicion web (site/<NN>/index.html, rutas relativas)
          y el email (out-signal/email-<NN>.html, URLs ABSOLUTAS), y regenera el indice
          del archivo (site/index.html). No toca el estado.

  deploy  NO lo hace este script: lo hace el workflow (peaceiris/actions-gh-pages ->
          repo publico servido por GitHub Pages). En local puedes previsualizar con
          `python -m http.server 8000 -d site`.

  send    Espera a que la edicion este VIVA (GET 200 a la URL publica y al logo),
          corre el preflight del ESP (sender.preflight), crea la campana en Brevo
          (draft|send segun SEND_MODE), opcionalmente manda un test interno, y SOLO
          entonces persiste signal_state.json y archiva la edicion consumida.

Uso:
  python strategy/09-ops/run_weekly.py build --edition ediciones-signal/next.json
  python strategy/09-ops/run_weekly.py send [--dry-run] [--test-to hello@sensalab.io]
  python strategy/09-ops/run_weekly.py all --edition sim/edicion-A.json   # prueba local

Reglas que respeta:
  - NO edita ningun .py del motor: importa config/build_edition/render_*/signal_email/
    sender/fetch_media tal cual. Al integrar se puede mover este archivo a la raiz.
  - Estado PROPIO (signal_state.json), separado del state.json del bot v1 para no
    corromper la anti-repeticion de ese pipeline.
  - Guardarriel non-compete: si aparece un termino prohibido, el envio se degrada a draft.
  - SEND_MODE=file no toca estado (modo prueba); draft/send si lo persisten.

TODOs (piezas que faltan, marcados tambien inline):
  - TODO(ingesta): hoy la edicion JSON llega "a mano" en ediciones-signal/next.json.
    El paso automatico (ingest_news + writer emitiendo ESTE schema) es de los
    especialistas de contenido; cuando exista, se enchufa en cmd_ingest().
  - TODO(keys): BREVO_API_KEY / BREVO_LIST_ID / PAGES_DEPLOY_TOKEN de Jon.
  - TODO(dominio): SIGNAL_PUBLIC_BASE definitivo (signal.sensalab.io) o la URL interina
    https://<org>.github.io/sensalab-signal mientras no haya DNS.
  - TODO(media): compresion de imagenes (Pillow) antes de publicar; og:image pesa 1-3 MB.
"""
from __future__ import annotations

import argparse
import html as _h
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

OPS = Path(__file__).resolve().parent
ROOT = OPS.parent.parent  # strategy/09-ops -> raiz del repo del bot
sys.path.insert(0, str(ROOT))

import requests  # noqa: E402

import config  # noqa: E402  (motor — solo lectura)
import sender  # noqa: E402
import guard  # noqa: E402  (GATE non-compete real: 79 terminos normalizados, fail-closed)
from build_edition import compose, EditionInvalid  # noqa: E402  (motor unico)
from render_signal import build_signal  # noqa: E402
from render_teardown import build_teardown  # noqa: E402
from signal_email import build_signal_email  # noqa: E402
# Nota: importar fetch_media crea sim/out/media/ (makedirs a nivel de modulo). Inofensivo.
from fetch_media import download, og_image  # noqa: E402

# ---------------- rutas y constantes del LOOP (no del motor) ----------------
SITE = ROOT / "site"                     # lo que se publica al host estatico
OUTS = ROOT / "out-signal"               # email + meta (NO se publica)
STATE_FILE = ROOT / "signal_state.json"  # estado propio del loop Signal
ASSETS = ROOT / "assets"                 # logo real de marca
EDITIONS_IN = ROOT / "ediciones-signal"  # bandeja de entrada: next.json
SENT_DIR = EDITIONS_IN / "sent"

# TODO(dominio): interina -> https://<org>.github.io/sensalab-signal ; final -> signal.sensalab.io
PUBLIC_BASE = config.env("SIGNAL_PUBLIC_BASE", "https://signal.sensalab.io").rstrip("/")

# Guardarriel legal non-compete (BRIEF): nunca el estudio anterior ni clientes pasados.
# La lista real vive en guard.py (strategy/08-compliance/forbidden-terms.txt, 79 terminos).


def log(m: str) -> None:
    print(m, flush=True)


# ------------------------------- estado -------------------------------------
def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"issue_no": 0, "editions": []}


def save_state(st: dict) -> None:
    STATE_FILE.write_text(json.dumps(st, indent=2, ensure_ascii=False), encoding="utf-8")


def forbidden_hits(edition: dict) -> list[str]:
    # Delega en el GATE real (guard.py: 79 terminos normalizados, no substring naive).
    # Devuelve strings "seccion:termino" para registrar en el meta y en la red del send.
    return [f"{sec}:{term}" for sec, term in guard.scan_edition(edition)]


# ------------------------------- media --------------------------------------
def resolve_media(edition: dict, media_dir: Path) -> dict:
    """Baja la imagen real (og:image) de la fuente de cada slot a media_dir.
    Mapa slot->indice de sources[]: edition["media_plan"] (recomendado);
    fallback: fuentes en orden. Reusa og_image()/download() del motor.
    Tolerante a fallo por slot: una imagen caida NO tumba la edicion (la tarjeta
    sale sin imagen en el email; en la web queda el frame vacio -> ver runbook)."""
    media_dir.mkdir(parents=True, exist_ok=True)
    plan = edition.get("media_plan") or {}
    srcs = edition.get("sources") or []
    man = {"hero": None, "sections": {}, "video": {}}

    roles = ["hero"] + [s.get("role", f"s{i}") for i, s in enumerate(edition.get("sections", []))]
    for i, role in enumerate(roles):
        try:
            idx = plan.get(role, i if i < len(srcs) else None)
            if idx is None or not (0 <= int(idx) < len(srcs)):
                log(f"  [media] {role}: sin fuente asignada (TODO: media_plan en la edicion)")
                continue
            img = og_image(srcs[int(idx)])
            if not img:
                log(f"  [media] {role}: sin og:image en {srcs[int(idx)][:60]}")
                continue
            fname = download(img, str(media_dir / role))
            if role == "hero":
                man["hero"] = f"media/{fname}"
            else:
                man["sections"][role] = f"media/{fname}"
            log(f"  [media] {role}: {fname}")
        except Exception as e:
            log(f"  [media] {role}: ERROR {type(e).__name__}: {e} (sigue sin imagen)")

    # video: poster directo, og:image de una fuente, o fallback a una imagen ya bajada
    vp = plan.get("video") or {}
    try:
        poster = vp.get("poster_url")
        if not poster and "src_idx" in vp and 0 <= int(vp["src_idx"]) < len(srcs):
            poster = og_image(srcs[int(vp["src_idx"])])
        if poster:
            fname = download(poster, str(media_dir / "video"))
            man["video"] = {"poster": f"media/{fname}", "link": vp.get("link", "")}
            log(f"  [media] video: {fname}")
        elif vp.get("link") and man["sections"]:
            man["video"] = {"poster": next(iter(man["sections"].values())), "link": vp["link"]}
            log("  [media] video: fallback -> reusa imagen de seccion como poster")
    except Exception as e:
        log(f"  [media] video: ERROR {type(e).__name__}: {e} (edicion sale sin bloque video)")
    return man


def copy_brand_assets(media_dir: Path) -> None:
    src = ASSETS / "sensalab-logo.png"
    if src.exists():
        shutil.copy2(src, media_dir / "sensalab-logo.png")
    else:
        log(f"  [assets] FALTA {src} — el masthead saldra roto (TODO: verificar assets/)")


# --------------------------- indice del archivo ------------------------------
def write_archive_index(st: dict, extra: dict | None = None) -> None:
    """Regenera site/index.html (archivo del canal) desde el estado + la edicion en curso."""
    items = {str(e.get("no")): e for e in st.get("editions", [])}
    if extra:
        items[str(extra["issue_no"])] = {"no": extra["issue_no"], "title": extra["subject"],
                                         "date": extra["date"], "url": extra["web_url"]}
    rows = "".join(
        f'<li><a href="{_h.escape(it.get("url", "#"))}"><span class="no">#{_h.escape(str(it.get("no")))}</span> '
        f'{_h.escape(str(it.get("title", "")))}</a><span class="d">{_h.escape(str(it.get("date", "")))}</span></li>'
        for it in sorted(items.values(), key=lambda x: str(x.get("no")), reverse=True))
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "index.html").write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>The Signal — SensaLab</title>
<style>
 body{{background:#F4F3F3;color:#0B0F0F;font-family:'Helvetica Neue',Arial,system-ui,sans-serif;margin:0}}
 .bar{{height:4px;background:linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7)}}
 .wrap{{max-width:680px;margin:0 auto;padding:34px 20px 60px}}
 h1{{color:#1C1956;font-size:30px;letter-spacing:-.02em;margin:0 0 6px}}
 .sub{{color:#787878;font-size:15px;margin:0 0 30px}}
 ul{{list-style:none;padding:0;margin:0}} li{{display:flex;justify-content:space-between;gap:14px;
 border-bottom:1px solid rgba(28,25,86,.14);padding:15px 2px}}
 a{{color:#1C1956;text-decoration:none;font-weight:700}} .no{{color:#787878;margin-right:8px}}
 .d{{color:#787878;font-size:13px;white-space:nowrap}}
 .foot{{margin-top:44px;color:#787878;font-size:12px}}
</style></head><body><div class="bar"></div><div class="wrap">
<h1>The Signal</h1><p class="sub">Weekly signals for experiential producers, from SensaLab.</p>
<ul>{rows}</ul>
<p class="foot">© 2026 SensaLab, Inc. · Los Angeles, CA, USA · hello@sensalab.io</p>
</div></body></html>""", encoding="utf-8")


# ------------------------------- build --------------------------------------
def cmd_build(args) -> int:
    for p in config.validate(require_api=False):
        log(f"  [config] {p}")

    ed_path = Path(args.edition or config.env("SIGNAL_EDITION_JSON",
                                              str(EDITIONS_IN / "next.json")))
    if not ed_path.exists():
        log(f"[build] no hay edicion en {ed_path} — semana sin edicion. "
            f"(TODO(ingesta): aqui se enchufa la generacion automatica del JSON)")
        return 1
    edition = json.loads(ed_path.read_text(encoding="utf-8"))

    st = load_state()
    nn = int(st.get("issue_no", 0)) + 1
    nn2 = f"{nn:02d}"
    now = datetime.now(timezone.utc)
    web_url = f"{PUBLIC_BASE}/{nn2}/"
    ed_dir = SITE / nn2
    media_dir = ed_dir / "media"
    ed_dir.mkdir(parents=True, exist_ok=True)

    log(f"[build] edicion #{nn2} -> {web_url}")
    man = resolve_media(edition, media_dir)
    copy_brand_assets(media_dir)

    # MOTOR UNICO: compose() decide formato, corre el GATE non-compete (fail-closed),
    # valida el esquema y renderiza web + email con logo/img_base absolutos y correctos.
    # URLs absolutas (web_url) para que las imagenes y el logo carguen desde el host.
    try:
        out = compose(edition, man, issue_no=nn2, date=now, web_url=web_url,
                      img_base=web_url, logo=f"{web_url}media/sensalab-logo.png",
                      legal_name=config.COMPANY_LEGAL_NAME,
                      legal_address=config.COMPANY_ADDRESS,
                      unsub=config.UNSUB_TOKEN)
    except guard.GuardBlocked as e:
        log(f"  [x] GATE non-compete BLOQUEO: {e.hits}")
        log("  [x] build ABORTADO — no se genera edicion (revision humana obligatoria).")
        return 2
    except EditionInvalid as e:
        log(f"  [x] edicion invalida: {e} — build ABORTADO.")
        return 2
    fmt, reason = out["format"], out["reason"]
    log(f"[build] formato: {fmt} ({reason})")
    (ed_dir / "index.html").write_text(out["web"], encoding="utf-8")
    OUTS.mkdir(parents=True, exist_ok=True)
    email_path = OUTS / f"email-{nn2}.html"
    email_path.write_text(out["email"], encoding="utf-8")

    # Red de seguridad extra para el meta/send: siempre [] porque compose() ya habria abortado.
    hits = forbidden_hits(edition)

    # TODO(asunto): el especialista de copy define la regla final del subject.
    subject = (edition.get("subject") or edition.get("edition_title")
               or edition.get("hero", {}).get("statement", "The Signal"))
    meta = {"issue_no": nn2, "date": now.strftime("%Y-%m-%d"), "subject": subject,
            "web_url": web_url, "format": fmt, "forbidden_hits": hits,
            "email_file": str(email_path), "edition_file": str(ed_path)}
    (OUTS / "meta-latest.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False),
                                           encoding="utf-8")
    write_archive_index(st, meta)
    log(f"[build] web:   {ed_dir / 'index.html'}")
    log(f"[build] email: {email_path}")
    log("[build] listo. Siguiente paso: deploy de site/ y luego `send`.")
    return 0


# -------------------------------- send --------------------------------------
def wait_live(url: str, tries: int = 20, pause: int = 15) -> bool:
    """Espera a que la URL publica responda 200 (GitHub Pages tarda ~1 min en publicar)."""
    for i in range(1, tries + 1):
        try:
            r = requests.get(url, timeout=20, headers={"Cache-Control": "no-cache"})
            if r.status_code == 200:
                log(f"  [web] viva: {url}")
                return True
            log(f"  [web] {url} -> {r.status_code} (intento {i}/{tries})")
        except Exception as e:
            log(f"  [web] {type(e).__name__}: {e} (intento {i}/{tries})")
        time.sleep(pause)
    return False


def brevo_send_test(campaign_id, email: str) -> None:
    """Test interno de una campana en borrador. Nota Brevo: el destinatario debe existir
    como contacto de la cuenta (agrega hello@sensalab.io a una lista de prueba)."""
    r = requests.post(f"{sender.BREVO_API}/emailCampaigns/{campaign_id}/sendTest",
                      json={"emailTo": [email]},
                      headers={"api-key": config.BREVO_API_KEY,
                               "content-type": "application/json"}, timeout=30)
    if r.status_code >= 300:
        log(f"  [test] sendTest fallo ({r.status_code}): {r.text[:200]}")
    else:
        log(f"  [test] test interno enviado a {email}")


def finalize_state(meta: dict, res: dict | None, mode: str) -> None:
    st = load_state()
    st["issue_no"] = int(meta["issue_no"])
    entry = {"no": meta["issue_no"], "title": meta["subject"], "date": meta["date"],
             "url": meta["web_url"], "format": meta["format"], "mode": mode,
             "campaign_id": (res or {}).get("campaign_id")}
    st["editions"] = [e for e in st.get("editions", []) if str(e.get("no")) != meta["issue_no"]]
    st["editions"].append(entry)
    save_state(st)
    write_archive_index(st)

    # archiva la edicion consumida para que la proxima semana no se re-use
    src = Path(meta.get("edition_file", ""))
    if src.exists() and src.name == "next.json":
        SENT_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(SENT_DIR / f"{meta['issue_no']}.json"))
        log(f"  [estado] {src.name} -> ediciones-signal/sent/{meta['issue_no']}.json")
    log(f"  [estado] signal_state.json -> issue_no={st['issue_no']}")


def cmd_send(args) -> int:
    meta_path = OUTS / "meta-latest.json"
    if not meta_path.exists():
        log("[send] no hay out-signal/meta-latest.json — corre `build` primero.")
        return 1
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    mode = (config.SEND_MODE or "file").lower()
    if meta.get("forbidden_hits") and mode == "send":
        mode = "draft"
        log("[send] guardarriel non-compete: envio degradado a draft (revision humana)")

    if mode == "file":
        log("[send] SEND_MODE=file — modo prueba: no se envia y NO se toca el estado.")
        return 0

    # 1) la web tiene que estar viva ANTES de mandar un solo email
    if not wait_live(meta["web_url"]):
        log("[send] la edicion no responde 200 — NO se envia. Ver runbook (deploy/DNS).")
        return 2
    if not wait_live(meta["web_url"] + "media/sensalab-logo.png", tries=4, pause=10):
        log("[send] aviso: el logo no responde — el email saldria con imagen rota. Abortando.")
        return 2

    # 2) preflight del ESP (mismo criterio que newsletter_bot_v2: fallar ANTES de comprometer)
    pf = sender.preflight(provider=config.PROVIDER, brevo_api_key=config.BREVO_API_KEY,
                          brevo_list_id=config.BREVO_LIST_ID,
                          ml_api_key=config.MAILERLITE_API_KEY,
                          ml_group_id=config.MAILERLITE_GROUP_ID)
    if pf:
        for p in pf:
            log(f"  [ESP] {p}")
        log("[send] preflight fallo — no se crea campana. (TODO(keys): BREVO_API_KEY/LIST_ID)")
        return 2
    log("  [ESP] preflight ok.")

    if args.dry_run:
        log("[send] dry-run: web viva + ESP ok. No se creo campana ni se toco estado.")
        return 0

    # 3) crear (y opcionalmente enviar) la campana
    html_body = Path(meta["email_file"]).read_text(encoding="utf-8")
    res = sender.deliver(provider=config.PROVIDER, mode=mode, subject=meta["subject"],
                         from_name=config.FROM_NAME, from_email=config.FROM_EMAIL,
                         html_body=html_body,
                         name=f"INMERSIVO The Signal #{meta['issue_no']} - {meta['date']}",
                         brevo_api_key=config.BREVO_API_KEY, brevo_list_id=config.BREVO_LIST_ID,
                         ml_api_key=config.MAILERLITE_API_KEY,
                         ml_group_id=config.MAILERLITE_GROUP_ID)
    log(f"[send] {'ENVIADA' if res['sent'] else 'BORRADOR creado'} via {res['provider']} "
        f"(campana {res['campaign_id']}).")

    # 4) test interno (solo util cuando quedo en borrador)
    if args.test_to and config.PROVIDER == "brevo" and not res["sent"]:
        brevo_send_test(res["campaign_id"], args.test_to)

    # 5) estado al final: si algo fallo antes, re-correr es seguro (mismo numero de edicion)
    finalize_state(meta, res, mode)
    log("[send] listo.")
    return 0


# --------------------------------- cli --------------------------------------
def cmd_all(args) -> int:
    rc = cmd_build(args)
    if rc:
        return rc
    log("\n[all] build ok. Deploy: publica site/ (workflow) o previsualiza local:")
    log("      python -m http.server 8000 -d site   ->  http://localhost:8000/<NN>/")
    log("[all] despues corre:  python strategy/09-ops/run_weekly.py send")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Orquestador semanal INMERSIVO (borrador 09)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="renderiza web + email de la edicion de la semana")
    b.add_argument("--edition", help="ruta al JSON de edicion (default: ediciones-signal/next.json)")
    b.set_defaults(fn=cmd_build)

    s = sub.add_parser("send", help="verifica web viva + crea campana en el ESP")
    s.add_argument("--dry-run", action="store_true", help="checks sin crear campana")
    s.add_argument("--test-to", help="email para test interno del borrador (Brevo sendTest)")
    s.set_defaults(fn=cmd_send)

    a = sub.add_parser("all", help="build + instrucciones de deploy/send (uso local)")
    a.add_argument("--edition")
    a.set_defaults(fn=cmd_all)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log(f"\n[ERROR] {type(e).__name__}: {e}")
        sys.exit(3)
