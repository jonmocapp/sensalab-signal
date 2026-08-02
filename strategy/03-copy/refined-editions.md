# Refined copy — edicion-A.json & edicion-B.json

Method (copywriting-refiner discipline, adapted to newsletter statements): audit every
`statement` and `why`, quote what fails and why, fix **only** what fails. Everything
refined stays inside the facts already sourced in each edition — no new claims, no
invented numbers, guardrail intact. Em dashes removed from display copy (they read as
brochure, and several email clients render them inconsistently).

Verdict legend: **KEEP** (already sharp, do not touch) · **REFINE** (fix applied).

---

## Edition A — issue 05, The Signal ("Steal This World Cup")

### Audit

| Slot | Current | Verdict | Problem |
|------|---------|---------|---------|
| hero.statement | "The best of the World Cup happened outside the stadiums." | REFINE | Near-verbatim echo of the headline ("The World Cup's best experiences happened outside the stadiums") — the two render together, so the statement adds nothing. |
| field-notes.statement | "The activations people remembered didn't ask to be watched." | REFINE | Good bones, but "remembered" is soft and unverifiable; the body's own proof is the queue and the play. |
| field-notes.why | "Participation outlasts impressions." | REFINE (light) | True and short, but single-beat; the two-beat version hits harder in the card. |
| in-the-lab.statement | "A scoreboard in the sky is just a data pipeline with an audience." | KEEP | The edition's best line. |
| in-the-lab.why | "Any same-day feed can become sky-scale scenography." | REFINE | Repeats the body's final sentence verbatim; the why-slot should compress, not copy. |
| craft.statement | "The watch party grew up — it's a venue-grade product now." | REFINE | Em dash; "venue-grade product" is category jargon where concrete behavior exists (ticketed domes). |
| craft.why | "Capture built for the canvas beats repurposed broadcast." | REFINE | Near-verbatim of the body ("designed for the canvas beats repurposed broadcast"). |
| video.statement | "Sixty seconds, three stolen ideas." | KEEP | Compressed triad, on-voice. |

### Refined copy (JSON-ready values)

```json
{
  "hero": {
    "statement": "The best venue at the World Cup wasn't the stadium."
  },
  "sections": [
    {
      "role": "field-notes",
      "statement": "People didn't queue to watch. They queued to play.",
      "why": "Impressions expire. Participation doesn't."
    },
    {
      "role": "in-the-lab",
      "statement": "A scoreboard in the sky is just a data pipeline with an audience.",
      "why": "Live data is set design material now."
    },
    {
      "role": "craft",
      "statement": "The watch party grew up. It sells tickets now.",
      "why": "Shoot for the room, not the rectangle."
    }
  ]
}
```

### Why each fix holds up (veracity check)

- **hero**: pier club, drone scoreboard, dome watch parties, 2M-visitor fan fests are all
  venues in the edition; "wasn't the stadium" is the edition's literal argument. Stops
  echoing the headline and adds the venue ranking.
  - Alt (spicier, still true): `"Spain took the trophy. Producers should take the playbook."`
- **field-notes statement**: 3v3 tournaments and pier games are in the body; queueing is in
  the body. Behavior replaces the unverifiable "remembered".
- **field-notes why**: same claim as before, recut into the house two-beat.
- **in-the-lab why**: compresses "any same-day feed can become sky-scale scenography" into
  a material claim instead of repeating it; 7 words.
- **craft statement**: "ticketed dome watch parties" appear in the hero sub; "sells tickets"
  is the concrete proof that it's venue-grade — shows instead of labels.
- **craft why**: restates capture-for-the-canvas as a producer instruction; "the rectangle"
  = broadcast framing, straight from the body ("framed for the dome, not TV").

---

## Edition B — issue 06, Teardown ("The Audience Can Tell")

### Audit

| Slot | Current | Verdict | Problem |
|------|---------|---------|---------|
| hero.statement | "Your audience just became a craft critic." | REFINE | Identical to the headline, word for word. One of the two slots is wasted. |
| field-notes.statement | "Harry Potter didn't reopen a movie. It opened a room." | KEEP | House-best two-beat. |
| field-notes.why | "Catalog IP is experiential inventory now." | KEEP | Precise, B2B, 6 words. |
| in-the-lab.statement | "Photoreal capture walked out of the demo and into the pipeline." | KEEP | Clear movement, true to OpenUSD/Unreal facts. |
| in-the-lab.why | "Scan the venue, previz the activation, reuse the asset." | KEEP | Actionable triad; the most producer-useful line in the issue. |
| craft.statement | "They sanded the grime off Shrek. The audience called it fake." | KEEP | The reference two-beat for the whole voice. |
| craft.why | "Polish isn't finish." | KEEP | The house aphorism. Do not touch. |
| teardown.verdict | "The June teaser drew backlash sharp enough that comments got switched off. It wasn't nostalgia. It was texture." | REFINE (light) | First sentence duplicates the craft section body verbatim; the verdict slot should read like a ruling, not a recap. |
| teardown.statement / video / done_right | (various) | KEEP | Statement mirrors craft.statement by design (it is the case's title card); done_right text is sharp and true. |

### Refined copy (JSON-ready values)

```json
{
  "hero": {
    "statement": "Audiences clock the flaw before they can name it."
  },
  "teardown": {
    "verdict": "Backlash sharp enough to switch the comments off. Not nostalgia. Texture."
  }
}
```

### Why each fix holds up (veracity check)

- **hero statement**: supported by the edition's own arc — the backlash came first, the
  vocabulary ("AI slop") arrived after. Keeps the headline's promotion line intact and
  gives the statement its own job: the mechanism.
  - Alt (uses the sub's closing thesis): `"Surfaces are strategy now."` — only if the
    renderer doesn't show hero.sub and hero.statement together, since the sub already
    ends on that phrase.
- **teardown verdict**: same facts (backlash, comments off, nostalgia vs. texture), recut
  from a 19-word recap into a 12-word ruling. Three fragments read like a judge's stamp,
  which is the slot's role.

---

## What was deliberately NOT changed

Refiner rule: fix only what fails. These lines are the voice working at full strength and
rewriting them would be regression, not refinement:

- "A scoreboard in the sky is just a data pipeline with an audience."
- "Harry Potter didn't reopen a movie. It opened a room."
- "They sanded the grime off Shrek. The audience called it fake."
- "Polish isn't finish."
- "Scan the venue, previz the activation, reuse the asset."
- "Sixty seconds, three stolen ideas." / "Watch a room become a splat."

They are the calibration set: any future writer output should sound like these six.
