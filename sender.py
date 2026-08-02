"""
Entrega multi-proveedor.

  brevo      -> api.brevo.com/v3/emailCampaigns  (plan GRATIS envia HTML por API, 300/dia)
  mailerlite -> connect.mailerlite.com/api/campaigns  (HTML propio por API = plan Advanced)

Modos: draft (crea borrador) | send (crea y envia). file se maneja en el orquestador.
"""
from __future__ import annotations

import requests

# ------------------------- Brevo -------------------------
BREVO_API = "https://api.brevo.com/v3"


def _int_list_id(list_id) -> int:
    try:
        return int(str(list_id).strip())
    except (TypeError, ValueError):
        raise RuntimeError(f"BREVO_LIST_ID debe ser un numero; recibi '{list_id}'.")


def _brevo_deliver(*, mode, api_key, list_id, subject, from_name, from_email,
                   html_body, name) -> dict:
    headers = {"api-key": api_key, "content-type": "application/json", "accept": "application/json"}
    payload = {
        "name": name,
        "subject": subject,
        "sender": {"name": from_name, "email": from_email},
        "htmlContent": html_body,
        "recipients": {"listIds": [_int_list_id(list_id)]},
    }
    r = requests.post(f"{BREVO_API}/emailCampaigns", json=payload, headers=headers, timeout=45)
    if r.status_code >= 300:
        raise RuntimeError(f"Brevo create ({r.status_code}): {r.text[:500]}")
    cid = r.json().get("id")
    result = {"provider": "brevo", "campaign_id": cid, "mode": mode, "sent": False}
    if mode == "send":
        s = requests.post(f"{BREVO_API}/emailCampaigns/{cid}/sendNow", headers=headers, timeout=45)
        if s.status_code >= 300:
            raise RuntimeError(f"Brevo sendNow ({s.status_code}): {s.text[:500]}")
        result["sent"] = True
    return result


# ---------------------- MailerLite -----------------------
ML_API = "https://connect.mailerlite.com/api"


def _ml_deliver(*, mode, api_key, group_id, subject, from_name, from_email,
                html_body, name) -> dict:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
               "Accept": "application/json"}
    payload = {
        "name": name,
        "type": "regular",
        "groups": [str(group_id)],
        "emails": [{"subject": subject, "from_name": from_name, "from": from_email,
                    "content": html_body}],
    }
    r = requests.post(f"{ML_API}/campaigns", json=payload, headers=headers, timeout=45)
    if r.status_code >= 300:
        raise RuntimeError(f"MailerLite create ({r.status_code}): {r.text[:500]} "
                           f"(recuerda: HTML propio por API requiere plan Advanced)")
    cid = r.json()["data"]["id"]
    result = {"provider": "mailerlite", "campaign_id": cid, "mode": mode, "sent": False}
    if mode == "send":
        s = requests.post(f"{ML_API}/campaigns/{cid}/schedule", json={"delivery": "instant"},
                          headers=headers, timeout=45)
        if s.status_code >= 300:
            raise RuntimeError(f"MailerLite schedule ({s.status_code}): {s.text[:500]}")
        result["sent"] = True
    return result


# ----------------------- Preflight -----------------------
def preflight(*, provider, brevo_api_key="", brevo_list_id="", ml_api_key="",
              ml_group_id="") -> list[str]:
    """Verifica cuenta + lista del ESP SIN enviar. Devuelve lista de problemas (vacia = ok).
    Se corre ANTES de llamar a Claude y de comprometer estado, para no quemar la semana
    si el ESP va a rechazar (401, cuenta no aprobada, lista inexistente)."""
    problems = []
    try:
        if provider == "brevo":
            h = {"api-key": brevo_api_key, "accept": "application/json"}
            a = requests.get(f"{BREVO_API}/account", headers=h, timeout=20)
            if a.status_code == 401:
                return ["Brevo: API key invalida (401)."]
            if a.status_code >= 300:
                return [f"Brevo: /account devolvio {a.status_code}: {a.text[:200]}"]
            lid = _int_list_id(brevo_list_id)
            l = requests.get(f"{BREVO_API}/contacts/lists/{lid}", headers=h, timeout=20)
            if l.status_code >= 300:
                problems.append(f"Brevo: lista {lid} no accesible ({l.status_code}).")
        elif provider == "mailerlite":
            h = {"Authorization": f"Bearer {ml_api_key}", "Accept": "application/json"}
            a = requests.get(f"{ML_API}/groups/{ml_group_id}", headers=h, timeout=20)
            if a.status_code == 401:
                return ["MailerLite: API key invalida (401)."]
            if a.status_code >= 300:
                problems.append(f"MailerLite: grupo {ml_group_id} no accesible ({a.status_code}).")
    except Exception as e:
        problems.append(f"Preflight del ESP fallo: {type(e).__name__}: {e}")
    return problems


# ----------------------- Dispatch ------------------------
def deliver(*, provider, mode, subject, from_name, from_email, html_body, name,
            brevo_api_key="", brevo_list_id="", ml_api_key="", ml_group_id="") -> dict:
    if provider == "brevo":
        return _brevo_deliver(mode=mode, api_key=brevo_api_key, list_id=brevo_list_id,
                              subject=subject, from_name=from_name, from_email=from_email,
                              html_body=html_body, name=name)
    if provider == "mailerlite":
        return _ml_deliver(mode=mode, api_key=ml_api_key, group_id=ml_group_id,
                           subject=subject, from_name=from_name, from_email=from_email,
                           html_body=html_body, name=name)
    raise ValueError(f"Proveedor desconocido: {provider}")
