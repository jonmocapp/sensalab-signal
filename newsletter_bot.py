"""
INMERSIVO — bot semanal de newsletter de SensaLab.

Pipeline:
  1. Descarga RSS de las fuentes  -> sources.fetch_all
  2. Filtra + anti-repeticion      -> select.choose
  3. Escribe con la voz SensaLab   -> writer.write_issue (Claude API)
  4. Arma el HTML del correo       -> templater.build_html
  5. Entrega                       -> file | draft | send (sender.deliver)
  6. Guarda el estado              -> select.commit

Uso:
  python newsletter_bot.py            # corrida real (segun SEND_MODE)
  python newsletter_bot.py --dry-run  # solo busca y selecciona, NO llama a Claude ni envia
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone

import config
import sources
import curation as selector
import templater
# writer (anthropic) y sender (requests para MailerLite) se importan lazy
# dentro de run(), para que --dry-run no requiera esas dependencias.


def log(msg: str) -> None:
    print(msg, flush=True)


def run(dry_run: bool = False) -> int:
    now = datetime.now(timezone.utc)
    log(f"\n=== INMERSIVO :: {now.date().isoformat()} :: modo={'DRY-RUN' if dry_run else config.SEND_MODE} ===")

    problems = config.validate(require_api=not dry_run)
    if problems:
        for p in problems:
            log(f"  [config] {p}")
        if not dry_run:
            return 2
    for a in config.advisories():
        log(f"  [aviso] {a}")

    # 1) Fuentes
    log("\n[1] Descargando fuentes...")
    candidates = sources.fetch_all(lookback_days=config.LOOKBACK_DAYS)
    log(f"    Total candidatas: {len(candidates)}")
    if not candidates:
        log("    Sin candidatas. No se genera edicion.")
        return 1

    # 2) Seleccion + anti-repeticion
    log("\n[2] Seleccionando (anti-repeticion)...")
    state = selector.load_state(config.STATE_FILE)
    chosen = selector.choose(candidates, state,
                             max_stories=config.MAX_STORIES,
                             min_geo=config.MIN_GEO_STORIES, now=now)
    if len(chosen) < config.MIN_STORIES:
        log(f"    Solo {len(chosen)} historias (< {config.MIN_STORIES}). No se envia esta semana.")
        return 1

    for i, s in enumerate(chosen, 1):
        geo = " [geo]" if s.geo else ""
        log(f"    {i}. [{s.source}]{geo} {s.headline[:70]}")

    short = selector.geo_shortfall(chosen, config.MIN_GEO_STORIES)
    if short:
        log(f"    [aviso] {short} historia(s) geo por debajo del minimo "
            f"({config.MIN_GEO_STORIES}); no habia mas con foco LA/Miami/NY/Vegas.")

    if dry_run:
        log("\n[DRY-RUN] Listo. No se llamo a Claude ni se envio nada.")
        return 0

    # Preflight del ESP ANTES de gastar Claude o comprometer estado: si el ESP va a
    # rechazar (401, cuenta no aprobada, lista inexistente), abortamos sin quemar la edicion.
    if config.SEND_MODE in ("draft", "send"):
        import sender
        pf = sender.preflight(provider=config.PROVIDER, brevo_api_key=config.BREVO_API_KEY,
                              brevo_list_id=config.BREVO_LIST_ID,
                              ml_api_key=config.MAILERLITE_API_KEY,
                              ml_group_id=config.MAILERLITE_GROUP_ID)
        if pf:
            for p in pf:
                log(f"  [ESP] {p}")
            log("    Abortando ANTES de escribir/enviar. Arregla el ESP y reintenta.")
            return 2
        log("  [ESP] preflight ok (cuenta + lista accesibles).")

    # 3) Escritura
    log("\n[3] Escribiendo con la voz SensaLab...")
    import writer  # lazy: solo aqui necesitamos anthropic
    issue = writer.write_issue(chosen, model=config.ANTHROPIC_MODEL,
                               api_key=config.ANTHROPIC_API_KEY or None)
    issue_number = state.get("issue_number", 0) + 1
    log(f"    Asunto: {issue.get('subject','')}")

    # Guardarrail non-compete: si aparece un termino prohibido, NUNCA se auto-envia.
    send_mode = config.SEND_MODE
    forbidden = writer.scan_forbidden(issue)
    if forbidden:
        log(f"    [!] ALERTA non-compete: aparecen terminos prohibidos {forbidden}.")
        if send_mode == "send":
            send_mode = "draft"
            log("    [!] Envio automatico BLOQUEADO. Se degrada a borrador para revision humana.")

    # 4) HTML
    log("\n[4] Armando HTML...")
    html_body = templater.build_html(issue, issue_number=issue_number, date=now,
                                     unsub=config.UNSUB_TOKEN,
                                     legal_name=config.COMPANY_LEGAL_NAME,
                                     legal_address=config.COMPANY_ADDRESS)

    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y-%m-%d")
    html_path = config.OUTPUT_DIR / f"inmersivo-{issue_number:02d}-{stamp}.html"
    html_path.write_text(html_body, encoding="utf-8")
    log(f"    Guardado: {html_path}")

    # 5) Guardar estado ANTES de entregar: si el envio falla o el runner muere entre
    #    el envio y el guardado, preferimos "perder" estas historias a re-enviarlas.
    log("\n[5] Guardando estado (antes de entregar)...")
    state = selector.commit(state, chosen, now=now)
    selector.save_state(config.STATE_FILE, state)
    log(f"    Edicion #{issue_number} registrada.")

    # 6) Entrega
    log(f"\n[6] Entrega (proveedor={config.PROVIDER}, modo={send_mode})...")
    if send_mode == "file":
        log("    Modo file: solo se guardo el HTML. (Configura un ESP para enviar.)")
    else:
        import sender  # lazy: solo aqui necesitamos requests/ESP
        res = sender.deliver(
            provider=config.PROVIDER,
            mode=send_mode,
            subject=issue.get("subject", "INMERSIVO"),
            from_name=config.FROM_NAME,
            from_email=config.FROM_EMAIL,
            html_body=html_body,
            name=f"INMERSIVO #{issue_number:02d} - {stamp}",
            brevo_api_key=config.BREVO_API_KEY,
            brevo_list_id=config.BREVO_LIST_ID,
            ml_api_key=config.MAILERLITE_API_KEY,
            ml_group_id=config.MAILERLITE_GROUP_ID,
        )
        if res["sent"]:
            log(f"    ENVIADO via {res['provider']}. Campana {res['campaign_id']}.")
        else:
            log(f"    BORRADOR creado via {res['provider']} (campana {res['campaign_id']}). Revisa y envia.")

    log("\n    Listo.\n")
    return 0


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv or "-n" in sys.argv
    try:
        sys.exit(run(dry_run=dry))
    except Exception as e:
        log(f"\n[ERROR] {type(e).__name__}: {e}")
        sys.exit(3)
