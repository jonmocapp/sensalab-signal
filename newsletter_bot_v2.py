"""
INMERSIVO v2 — orquestador del CEREBRO.

  cerebro (brain) -> plan de edicion -> redaccion (writer) -> UTM (tracking)
  -> HTML (templater) -> guarda edicion para blog (content_model) -> envio (sender)

Uso:
  python newsletter_bot_v2.py --dry-run   # arma el plan de la semana, NO llama LLM ni envia
  python newsletter_bot_v2.py             # edicion real (segun SEND_MODE), necesita ANTHROPIC_API_KEY
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone

import config
import brain
import templater
import curation as selector


def log(m: str) -> None:
    print(m, flush=True)


def run(dry_run: bool = False) -> int:
    now = datetime.now(timezone.utc)
    log(f"\n=== INMERSIVO v2 (cerebro) :: {now.date()} :: "
        f"{'DRY-RUN' if dry_run else config.SEND_MODE} ===")

    problems = config.validate(require_api=not dry_run)
    if problems:
        for p in problems:
            log(f"  [config] {p}")
        if not dry_run:
            return 2
    for a in config.advisories():
        log(f"  [aviso] {a}")

    # 1) CEREBRO: arma el plan de edicion de la semana
    log("\n[1] Cerebro: ingesta + scoring + composicion...")
    state = selector.load_state(config.STATE_FILE)
    state.setdefault("used_topics", [])
    plan, cands = brain.build_edition_plan(date=now, state=state,
                                           lookback_days=config.LOOKBACK_DAYS, verbose=True)
    if plan is None or len(plan.stories) < config.MIN_STORIES:
        n = 0 if plan is None else len(plan.stories)
        log(f"    Solo {n} historias (< {config.MIN_STORIES}). No se envia esta semana.")
        return 1

    brain._print_plan(plan, cands, now)

    if dry_run:
        log("\n[DRY-RUN] Plan listo. No se llamo al LLM ni se envio nada.")
        return 0

    # 2) Preflight del ESP ANTES de gastar el LLM o comprometer estado
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
        log("  [ESP] preflight ok.")

    # 3) Redaccion (respeta formato + angulo + theme del cerebro)
    log("\n[2] Redaccion con la voz SensaLab (formato + angulo del cerebro)...")
    import writer
    issue = writer.write_edition(plan, model=config.ANTHROPIC_MODEL,
                                 api_key=config.ANTHROPIC_API_KEY or None)
    issue_number = state.get("issue_number", 0) + 1
    log(f"    Formato={plan.format_id} | Asunto: {issue.get('subject','')}")

    # Guardarrail non-compete: bloquea auto-envio si aparece termino prohibido
    send_mode = config.SEND_MODE
    forbidden = writer.scan_forbidden(issue)
    if forbidden:
        log(f"    [!] ALERTA non-compete: {forbidden}.")
        if send_mode == "send":
            send_mode = "draft"
            log("    [!] Envio automatico BLOQUEADO -> borrador para revision humana.")

    # 4) Instrumentar links con UTM (tracking)
    try:
        import tracking
        for s in issue.get("stories", []):
            slug = tracking.slugify(s.get("headline", ""))
            s["link"] = tracking.wrap_link(s["link"], issue_number, slug)
    except Exception as e:
        log(f"    [tracking] no se pudo instrumentar UTM: {e}")

    # 5) HTML
    log("\n[3] Armando HTML...")
    stamp = now.strftime("%Y-%m-%d")
    html = templater.build_html(issue, issue_number=issue_number, date=now,
                                unsub=config.UNSUB_TOKEN,
                                legal_name=config.COMPANY_LEGAL_NAME,
                                legal_address=config.COMPANY_ADDRESS)
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    html_path = config.OUTPUT_DIR / f"inmersivo-{issue_number:02d}-{stamp}.html"
    html_path.write_text(html, encoding="utf-8")
    log(f"    Guardado: {html_path}")

    # 6) Guardar edicion estructurada (fuente para el blog futuro)
    try:
        import content_model
        ed = content_model.from_issue(issue, number=issue_number, date=now.date(),
                                      format_id=plan.format_id, theme=issue.get("theme", ""))
        content_model.save_edition(ed)
        log("    Edicion estructurada guardada (content/ — lista para el blog).")
    except Exception as e:
        log(f"    [content] no se pudo guardar la edicion estructurada: {e}")

    # 7) Estado ANTES de entregar (no re-enviar si el ESP falla)
    log("\n[4] Guardando estado...")
    selector.commit(state, plan.stories, now=now)
    state["used_topics"] = (state.get("used_topics", []) + [c.topic for c in plan.stories])[-200:]
    state["last_format"] = plan.format_id
    selector.save_state(config.STATE_FILE, state)
    log(f"    Edicion #{issue_number} registrada (formato {plan.format_id}).")

    # 8) Entrega
    log(f"\n[5] Entrega (proveedor={config.PROVIDER}, modo={send_mode})...")
    if send_mode == "file":
        log("    Modo file: solo se guardo el HTML.")
    else:
        import sender
        res = sender.deliver(
            provider=config.PROVIDER, mode=send_mode,
            subject=issue.get("subject", "INMERSIVO"),
            from_name=config.FROM_NAME, from_email=config.FROM_EMAIL,
            html_body=html, name=f"INMERSIVO #{issue_number:02d} - {stamp}",
            brevo_api_key=config.BREVO_API_KEY, brevo_list_id=config.BREVO_LIST_ID,
            ml_api_key=config.MAILERLITE_API_KEY, ml_group_id=config.MAILERLITE_GROUP_ID,
        )
        log(f"    {'ENVIADO' if res['sent'] else 'BORRADOR'} via {res['provider']} "
            f"(campana {res['campaign_id']}).")

    log("\n    Listo.\n")
    return 0


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv or "-n" in sys.argv
    try:
        sys.exit(run(dry_run=dry))
    except Exception as e:
        log(f"\n[ERROR] {type(e).__name__}: {e}")
        sys.exit(3)
