# The Signal — cloud routine playbook

You are a scheduled cloud agent (Claude). Your job: publish **today's edition of The Signal** by
adding 2–3 fresh, real news articles to the blog and refreshing the daily Signals feed, then
deploying. Work only inside this repo. Follow these steps exactly.

## Steps
1. `pip install -r requirements.txt`
2. `python daily_signals.py` — refreshes the real-news POOL into `signals.json` (free, no LLM).
3. **Pick up to 3 NEW stories** from `signals.json` that are NOT already covered:
   - Exclude any whose normalized `link` already appears as a `source_url` in `articles_live.json`.
   - Prefer English trade/quality sources (ASCII source name); skip PR fluff (job moves, "fresh faces", milestones, webinars).
   - Spread categories when possible.
4. For **each** picked story: `WebFetch` its `link` to get the REAL facts (numbers, dates, names) and the `og:image` URL. Then write ONE blog article in the **ART schema** (below), grounded ONLY in those facts.
5. Append each new article object to the `articles` array in **`articles_live.json`** with fields:
   `{slug, cat, tokens, edition: 21, source_name, source_url, date, image_url, headline, dek, focus_keyword, read_minutes, meta_description, why, takeaway, body}`.
   - `cat` is one of: Experiential, Interactive, AI, CGI & VFX, Gaming, Concert visuals, Spatial & AR. `tokens` = the lowercase token for that category (experiential/interactive/ai/cgi/gaming/concerts/spatial). `slug` = kebab-case from the headline, unique.
6. Rebuild: `python set_articles.py && python build_articles.py && python build_blog_b.py && python build_seo.py`
   (set_articles downloads the og:image or falls back to an on-brand cover; build renders the whole site into `blog/`).
7. **Deploy** the `blog/` folder to Netlify using the Netlify MCP tools attached to this routine.
8. Persist state: `git add -A && git commit -m "Signal daily: <YYYY-MM-DD>" && git push`.

## ART schema (per article)
`body` is a list of blocks `{"type":"para"|"subhead","text":"..."}` — 7–9 blocks, ~500–650 words,
2–3 subheads. First para = the concrete facts (attribute figures). A reframe para ("the real signal
is X, not Y"). A "what a producer can do now" angle and a "why it belongs in an experiential toolkit"
angle. Exactly ONE markdown cross-link `[label](/target)` to a kit (/kits/activations, /kits/shows,
/kits/retail, /kits/branding) or an existing slug. Final para = a soft, non-boastful SensaLab
white-label close.

## VOICE
The Signal is SensaLab's English blog for senior agency producers / brand-experience leads. SensaLab
is a Los Angeles white-label real-time 3D and immersive studio (activations, projection mapping,
AR/XR, LED volumes) that agencies/brands use UNDER THEIR OWN NAME. Sharp, peer-to-peer, no hype.
Headlines sentence case, ~10–14 words, "signal" framing.

## HARD GUARDRAILS (breaking any invalidates the article)
- Ground every fact ONLY in the fetched source. Do NOT invent numbers, dates, names, quotes.
- NEVER reference a founder's past work, past clients, or "Cinetica". Never claim SensaLab did
  specific past projects. SensaLab speaks as an expert, not a portfolio.
- No exclamation marks, no emojis, no empty hype. English, sentence case, never ALL CAPS.
- Non-English / non-ASCII source outlets: skip them for the featured articles.

If a step fails, log it clearly and continue with what succeeded; still commit and deploy what built.
