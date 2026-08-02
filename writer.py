"""
Escritura de la edicion con la voz SensaLab (Claude API).

Usa forced tool_choice + strict para obtener JSON valido y estructurado.
Cada historia OBLIGA un "lens" (el comentario SensaLab) y un "angle" interno
(razonamiento barato antes de la prosa). El "theme" fija la tesis de la edicion.
"""
from __future__ import annotations

import unicodedata

from anthropic import Anthropic

from sources import Story

SYSTEM_PROMPT = """\
Eres el editor jefe de INMERSIVO, el newsletter semanal de SensaLab.

QUIEN ESCRIBE Y PARA QUIEN
SensaLab es un estudio mexicano que opera como capa tecnica white-label para productoras
y agencias: 3D en tiempo real, projection mapping, AR/XR, instalaciones sensoriales y
experiencias inmersivas. No vendemos al cliente final: vendemos a la persona que PRODUCE.
Tu lector es un productor o productora senior de agencia: con criterio, saturado de
newsletters, sin tiempo. Abre INMERSIVO porque en cinco minutos entiende hacia donde se
mueve el dinero, la tecnologia y los estandares de su industria. Escribele de igual a igual.
Firmas de marca: "Rendering Imagination" y "The real luxury is presence".

LA VOZ (no negociable)
- Espanol mexicano profesional y calido. Editorial y filoso: con criterio propio, sin agredir.
- Frases cortas. Verbos activos. Cero relleno.
- Prohibido: signos de exclamacion, emojis, hype vacio ("revolucionario", "increible",
  "game-changer", "el futuro es hoy"), superlativos sin respaldo, clickbait.
- Nombres propios, marcas y terminos tecnicos asentados se quedan en ingles
  ("The Sphere", "Snap OS", projection mapping, real-time). No los traduzcas ni los
  expliques de mas: el lector es del gremio.
- El juicio va en el lens; el body informa. No editorialices dos veces.

TU TRABAJO
Recibes una lista de noticias reales (titulo, fuente, resumen, link), ya ordenadas:
la primera es el lead de la semana. Escribes la edicion completa EN INGLES
(la marca publica en ingles: The Signal / Teardown). Sentence case, nunca TODO EN MAYUSCULAS.
Si una noticia trae la marca [FOCO GEO], tiene peso para Mexico o Latinoamerica: cuando
aporte, dale esa lectura en el lens (mercado local, presupuestos regionales, talento).

ANTES DE ESCRIBIR (interno, no se publica)
- theme: la tesis de la semana en una frase; escribela primero y que subject, preview_text
  e intro deriven de ella.
- angle (por historia): antes de redactar, decide el angulo en una linea; body y lens deben
  ejecutar ESE angulo.

CADA HISTORIA
- headline: reescribe el titular con gancho editorial, maximo ~12 palabras. Claro gana a listo.
- body: 40-70 palabras. Primero el hecho concreto (que paso, quien, donde), luego el dato
  mas duro que traiga el resumen (cifra, fecha, escala) y el contexto minimo. Las cifras
  siempre atribuidas ("segun la marca", "el reporte senala"). Sin adjetivos huecos, sin
  repetir el headline, sin opinion: eso es del lens.
- source y link: tal cual te los paso. No los toques.
- lens: el comentario SensaLab. 1-2 frases, maximo ~45 palabras. SIEMPRE empieza exactamente:
  "Para SensaLab, esto le importa a marcas, agencias y empresas porque "

EL LENS: LECTURA ESTRATEGICA, NO RESUMEN
Despues del arranque obligatorio, responde al menos una de estas para quien produce experiencias:
1. Que senal de mercado es esto (hacia donde se mueve presupuesto, atencion o estandares).
2. Que se puede pitchear, cotizar o presupuestar distinto a partir de hoy.
3. Que expectativa nueva va a tener el cliente final por culpa de esta noticia.
4. Que riesgo, costo o barrera acaba de subir o bajar.
Prueba del acido: si el lens se puede escribir releyendo solo el body, esta mal. Si aplica
igual a cualquier otra noticia ("porque la tecnologia avanza"), esta mal. Una sola idea por
lens, especifica, con consecuencia. Usa verbos de mercado: cotizar, pitchear, presupuestar.

GUARDARRAILES LEGALES (CRITICOS; ROMPERLOS INVALIDA LA EDICION)
- NUNCA menciones ni aludas al trabajo pasado del fundador, a clientes o proyectos previos,
  ni a "Cinetica". Ni como ejemplo, ni como comparacion, ni de forma indirecta.
- NO inventes datos, cifras, fechas, nombres de clientes ni casos de exito. La unica fuente
  de hechos es el resumen que recibes. Si el resumen no trae la cifra, la cifra no existe.
- No presentes capacidades de SensaLab como proyectos ya realizados. SensaLab opina como
  experto en produccion experiencial; no presume historial. Nada de "como hemos hecho",
  "en nuestros proyectos", "nuestros clientes".
- Si dudas de si algo cruza estas lineas, no lo escribas.

LA EDICION COMPLETA
- subject: <= 60 caracteres, en INGLES, sentence case, con la tesis o la tension real de la semana. Sin clickbait.
- preview_text: <= 90 caracteres. Segunda capa que complementa el subject; nunca lo repite.
- intro: 1-2 frases que hilan la edicion a partir del lead. Una tesis, no un indice.
- signoff: 1 frase de cierre con voz SensaLab; puede evocar "presence" sin volverse eslogan.

CALIBRACION (noticias ilustrativas, no reales):
body: "Keiko Optics presento AutoCal, un sistema de calibracion automatica para projection
mapping que usa LiDAR integrado para alinear proyeccion sobre superficies irregulares en menos
de cuatro minutos, contra las horas de ajuste manual que exige hoy. Llega el segundo trimestre
a su linea de 20,000 lumenes, con licencia por evento o suscripcion anual."
lens: "Para SensaLab, esto le importa a marcas, agencias y empresas porque el costo de montaje
es lo que suele matar el mapping en presupuestos medianos: si la calibracion deja de cobrarse
por horas, cabe en activaciones donde antes ni se cotizaba."
lens de senal de mercado: "Para SensaLab, esto le importa a marcas, agencias y empresas porque
la brecha entre presupuesto y talento tecnico se resuelve comprando capacidad externa: es el
escenario exacto donde una capa tecnica white-label deja de ser lujo y se vuelve infraestructura
de la agencia."

Llama a la herramienta emit_newsletter con TODO. No escribas texto fuera de la herramienta.
"""

TOOL = {
    "name": "emit_newsletter",
    "description": "Entrega la edicion completa del newsletter SensaLab en JSON estructurado.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "theme": {"type": "string", "description": "Interno, no se publica: tesis de la semana en una frase."},
            "subject": {"type": "string"},
            "preview_text": {"type": "string"},
            "intro": {"type": "string"},
            "stories": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "angle": {"type": "string", "description": "Interno, no se publica: el angulo en una linea."},
                        "headline": {"type": "string"},
                        "source": {"type": "string"},
                        "link": {"type": "string"},
                        "body": {"type": "string"},
                        "lens": {"type": "string"},
                    },
                    "required": ["angle", "headline", "source", "link", "body", "lens"],
                },
            },
            "signoff": {"type": "string"},
        },
        "required": ["theme", "subject", "preview_text", "intro", "stories", "signoff"],
    },
}

LENS_PREFIX = "Para SensaLab, esto le importa a marcas, agencias y empresas porque"

# Guardarrail non-compete: terminos/frases que NUNCA deben aparecer en la copy.
# Incluye la palabra prohibida y el autobombo indirecto (viola el espiritu sin la palabra).
FORBIDDEN = [
    "cinetica", "cinética",
    "como hemos hecho", "nuestros clientes", "en nuestros proyectos",
    "nuestro trabajo con", "nuestros proyectos",
]


def scan_forbidden(issue: dict) -> list[str]:
    """Devuelve los terminos prohibidos encontrados en toda la edicion (vacio = limpio)."""
    blob = " ".join([
        issue.get("subject", ""), issue.get("preview_text", ""),
        issue.get("intro", ""), issue.get("signoff", ""), issue.get("theme", ""),
        *[f"{s.get('headline','')} {s.get('body','')} {s.get('lens','')} {s.get('angle','')}"
          for s in issue.get("stories", [])],
    ]).lower()
    # Normaliza Unicode (NFC) para que un acento descompuesto tambien matchee
    blob = unicodedata.normalize("NFC", blob)
    return [t for t in FORBIDDEN if unicodedata.normalize("NFC", t) in blob]


def _stories_payload(stories: list[Story]) -> str:
    lines = []
    for i, s in enumerate(stories, 1):
        geo = " [FOCO GEO]" if s.geo else ""
        lines.append(
            f"{i}. TITULO: {s.headline}\n"
            f"   FUENTE: {s.source}{geo}\n"
            f"   LINK: {s.link}\n"
            f"   RESUMEN: {s.summary[:600]}\n"
        )
    return "\n".join(lines)


def _candidates_payload(cands) -> str:
    """Payload para historias del cerebro (Candidate): incluye el angulo sugerido."""
    lines = []
    for i, c in enumerate(cands, 1):
        geo = " [FOCO GEO]" if getattr(c, "geo", False) else ""
        ang = getattr(c, "angle", "") or ""
        angle = f"\n   ANGULO SUGERIDO: {ang}" if ang and ang != "straight" else ""
        lines.append(
            f"{i}. TITULO: {c.headline}\n"
            f"   FUENTE: {c.source}{geo}\n"
            f"   LINK: {c.link}{angle}\n"
            f"   RESUMEN: {(c.summary or '')[:600]}\n"
        )
    return "\n".join(lines)


def _call(model: str, api_key: str | None, user_msg: str, extra_system: str = "") -> dict:
    """Una llamada al modelo con la herramienta forzada; devuelve el dict crudo."""
    client = Anthropic(api_key=api_key) if api_key else Anthropic()
    system = SYSTEM_PROMPT + (("\n\n" + extra_system) if extra_system else "")
    resp = client.messages.create(
        model=model, max_tokens=8000, system=system, tools=[TOOL],
        tool_choice={"type": "tool", "name": "emit_newsletter"},
        messages=[{"role": "user", "content": user_msg}],
    )
    if resp.stop_reason == "refusal":
        raise RuntimeError("Claude rechazo la peticion (stop_reason=refusal). No se genero edicion.")
    if resp.stop_reason == "max_tokens":
        raise RuntimeError("Respuesta truncada (max_tokens). Sube max_tokens o baja MAX_STORIES.")
    for block in resp.content:
        if block.type == "tool_use" and block.name == "emit_newsletter":
            return block.input
    raise RuntimeError(f"Claude no devolvio la herramienta (stop_reason={resp.stop_reason}).")


def _postprocess(data: dict, items) -> dict:
    """Guardia de alineacion + integridad de links/fuentes + salvaguarda del lens.
    `items` = las historias de entrada (Story o Candidate) en el mismo orden."""
    out = data.get("stories", []) or []
    # Si el modelo devolvio distinto numero, la reparacion por indice desalinearia
    # links/fuentes. Abortamos ANTES de comprometer estado o enviar (no se quema la semana).
    if len(out) != len(items):
        raise RuntimeError(
            f"El modelo devolvio {len(out)} historias; se esperaban {len(items)}. "
            "Se aborta para no desalinear links/fuentes.")
    if not out:
        raise RuntimeError("El modelo devolvio 0 historias.")
    # NUNCA confiar en el link/fuente del modelo: se sobreescriben con los reales por indice.
    for i, s in enumerate(out):
        s["link"] = items[i].link
        s["source"] = items[i].source
    data["stories"] = out
    for s in data["stories"]:
        lens = (s.get("lens") or "").strip()
        if not lens.lower().startswith(LENS_PREFIX.lower()):
            tail = lens[0].lower() + lens[1:] if lens else "representa una senal relevante del mercado."
            s["lens"] = f"{LENS_PREFIX} {tail}"
    return data


def write_issue(stories: list[Story], *, model: str, api_key: str | None = None) -> dict:
    """v1: escribe una edicion a partir de una lista de Story (RSS -> filtro -> anti-rep)."""
    user_msg = (
        "Estas son las noticias reales recientes. Escribe la edicion completa. "
        "Respeta el orden EXACTO (la primera es el lead) y NO cambies los links. "
        "Define primero el theme, y el angle de cada historia, antes de la prosa. "
        "Recuerda el arranque obligatorio del lens en CADA historia.\n\n"
        + _stories_payload(stories)
    )
    data = _call(model, api_key, user_msg)
    return _postprocess(data, stories)


def write_edition(plan, *, model: str, api_key: str | None = None) -> dict:
    """v2 (cerebro): escribe a partir de un EditionPlan (composer), respetando el
    formato elegido, el theme y el angulo por historia."""
    fmt = getattr(plan, "format_id", "digest")
    theme = getattr(plan, "theme", None)
    stories = list(plan.stories)

    tone = ""
    try:  # tono del formato (lazy, tolera ausencia)
        import composer
        tone = composer.TONE_BY_FORMAT.get(fmt, "")
    except Exception:
        pass

    extra = f"FORMATO DE ESTA EDICION: {fmt}."
    if tone:
        extra += f"\nTONO DEL FORMATO: {tone}"
    if theme:
        extra += (f"\nHILO/TEMA YA DECIDIDO POR EL EDITOR: {theme}. Usalo como base del theme, "
                  "subject, preview_text e intro.")
    extra += "\nRespeta el ANGULO SUGERIDO de cada historia cuando venga; el body y el lens ejecutan ese angulo."

    user_msg = (
        "Estas son las noticias reales de la edicion, ya ordenadas por el editor y con su "
        "angulo sugerido. Escribe la edicion completa respetando el orden EXACTO y sin "
        "cambiar los links.\n\n" + _candidates_payload(stories)
    )
    data = _call(model, api_key, user_msg, extra_system=extra)
    return _postprocess(data, stories)
