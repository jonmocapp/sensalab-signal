# BRIEF MAESTRO — INMERSIVO (newsletter B2B de SensaLab)

Contexto compartido para los 10 especialistas. Léelo completo antes de tu misión.

## Qué es el proyecto
**INMERSIVO** = newsletter semanal de thought-leadership B2B de **SensaLab** (estudio; capa
técnica **white-label** de 3D real-time / proyección / AR / interactivo que agencias y marcas
meten en sus activaciones experienciales). El newsletter posiciona a SensaLab como experto **por
asociación** — da munición e inspiración a productores, NO vende duro.

## El insight que lo justifica (del reporte de ventas SL-26)
*"The pitch converts, connection is the bottleneck."* 95% de los decision-makers que enganchan
se vuelven warm. El cuello de botella es el REACH. El newsletter ataca ese cuello: estar
top-of-mind y ser tan valioso que cuando el productor necesite la capa técnica, el nombre sea
SensaLab.

## A quién le hablamos (ICP, del SL-26)
- **Agencias experienciales** (81 en LA en el pipeline) + **marcas** (Sony, Apple, Amazon, HBO,
  Netflix, lululemon, SKIMS, Fender, Microsoft, SEPHORA…). Roles: VP Innovation, Exec/Senior
  Creative Producer, Creative Director, Head of Creative Production.
- **STRONG fit** = dedicada a experiencial · fabrica/monta pero SIN 3D real-time/interactivo
  in-house (el hueco white-label) · immersive-minded · presupuestos de gran marca · cómoda
  poniendo tech de un partner bajo su propia marca.
- Datos de outbound reales: 118 leads LA (98% con email, 72% LinkedIn), 78 agencias ICP scoreadas
  (29 Strong, 15 Good). Fuente: `OneDrive\Desktop\SensaLab\06-Web-y-Dev\SensaLab_SL-26_Sales_Intelligence_2026.pdf`.

## Producto ya construido (en C:\Dev\SensaLab-Newsletter-Bot\)
- **Motor "AI sin AI"**: `build_edition.py` (cerebro determinista que elige formato por talkability),
  `render_signal.py` (formato The Signal: tarjetas de insight + "Why it matters"),
  `render_teardown.py` (formato Teardown: caso destripado con lente de craft),
  `signal_email.py` (email-slim que linkea a la web), `brand_footer.py`.
- Ediciones reales de muestra: `sim/edicion-A.json` (Mundial → Signal), `sim/edicion-B.json`
  (Cosm/SIGGRAPH/Shrek → Teardown). Media real en `sim/out/media/`. Salidas en `sim/out/final-*.html`.
- Modelo: **edición web (rica, el destino/blog)** + **email slim (el vehículo que linkea a la web)**.
  El clic va a NUESTRO sitio, no a terceros.

## Marca (reglas duras)
- Logo real: `sim/out/media/sensalab-logo.png` (isotipo lazo + wordmark). Fuente: **KMR Apparat**
  (en `OneDrive\Desktop\SensaLab\02-Marca\KMR Apparat\`).
- **Paleta de TEXTO (solo estos 5):** `#0B0F0F` `#F4F3F3` `#787878` `#1C1956` `#E4E4EF`.
- **Sentence case SIEMPRE** — nada en MAYÚSCULAS completas.
- Footer real: principle "Rendering Experiences…", socials Instagram/LinkedIn/Youtube,
  © 2026 SensaLab, Inc., **Los Angeles, CA — USA**, hello@sensalab.io, sensalab.io.
- Firma: "The real luxury is presence".

## Guardarriel legal (CRÍTICO, no negociable)
NUNCA menciones ni aludas al trabajo pasado del fundador, clientes pasados, ni **"Cinética"**.
No inventes datos, cifras ni casos. Opina del mercado sin autobombo.

## Entrega / infra (estado)
Se planeó Brevo (plan gratis envía HTML por API) como ESP; hosting web pendiente; envío pendiente
de las keys de Jon (BREVO_API_KEY, ANTHROPIC_API_KEY). Idioma del newsletter: **inglés** (público LA/US).

## Reglas para TODOS los especialistas
1. Escribe TODOS tus entregables SOLO dentro de tu carpeta `strategy/<tu-numero>-<slug>/`. NO edites
   los .py existentes del motor (yo integro después). Puedes crear archivos de datos/borradores en tu carpeta.
2. Usa los SKILLS relevantes de tu dominio (invócalos con la herramienta Skill si está disponible;
   si no, aplica la metodología igual). Cita qué skills usaste.
3. Todo debe respetar el guardarriel legal, la paleta, sentence case, y el ICP real.
4. Sé concreto y accionable (no genérico). Entregables listos para ejecutar/pegar.
5. Cierra con un `README.md` en tu carpeta: qué entregaste, decisiones clave, y qué necesitas de Jon.
