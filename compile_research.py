# -*- coding: utf-8 -*-
"""Compila research/*.json (lo que trajeron los scouts) -> (1) añade metadata por slug a
articles_meta.json (categoría, tokens, fuente, imagen, fecha) y (2) escribe drafts_todo.json
con {slug, cat, headline_real, source_name, facts} para armar los prompts de los redactores.
Dedup por slug; no pisa lo ya existente (las 12 curadas siguen)."""
import glob
import json
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parent
RESEARCH = BASE / "research"
META_FILE = BASE / "articles_meta.json"
TODO_FILE = BASE / "drafts_todo.json"
EDITION = 21

TOKENS = {"Experiential": "experiential", "Spatial & AR": "spatial", "CGI & VFX": "cgi",
          "AI": "ai", "Gaming": "gaming", "Interactive": "interactive",
          "Concert visuals": "concerts"}
VALID = set(TOKENS)

_STOP = {"the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "with", "at", "by",
         "its", "into", "from", "as", "is", "are", "will", "new", "how", "that", "this",
         "becomes", "opens", "launch", "launches", "unveils", "announce", "announces", "most"}


def slugify(text: str, taken: set) -> str:
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    words = [w for w in words if w not in _STOP][:6]
    base = "-".join(words) or "story"
    slug, i = base, 2
    while slug in taken:
        slug = f"{base}-{i}"; i += 1
    return slug


def main() -> int:
    meta = json.loads(META_FILE.read_text(encoding="utf-8")) if META_FILE.exists() else {}
    taken = set(meta.keys())
    todo, added, skipped = [], 0, 0

    for f in sorted(glob.glob(str(RESEARCH / "*.json"))):
        for s in json.loads(pathlib.Path(f).read_text(encoding="utf-8")):
            cat = s.get("category", "").strip()
            if cat not in VALID:
                print(f"  [!] categoría inválida '{cat}' en {pathlib.Path(f).name}; se salta.")
                skipped += 1
                continue
            slug = slugify(s["headline_real"], taken)
            taken.add(slug)
            meta[slug] = {
                "cat": cat, "tokens": TOKENS[cat], "edition": EDITION,
                "source_name": s.get("source_name", ""), "source_url": s.get("source_url", ""),
                "date": s.get("date", ""), "image_url": s.get("image_url"),
            }
            todo.append({"slug": slug, "cat": cat, "headline_real": s["headline_real"],
                         "source_name": s.get("source_name", ""), "facts": s.get("facts", [])})
            added += 1

    META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    TODO_FILE.write_text(json.dumps(todo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"compilado: +{added} notas ({skipped} saltadas) -> articles_meta.json ({len(meta)} total)")
    print(f"drafts_todo.json listo con {len(todo)} historias para redactar.")
    # reparto sugerido en 8 grupos
    for gi in range(0, len(todo), 4):
        grp = todo[gi:gi + 4]
        print(f"  grupo {gi//4+1}: " + " | ".join(t["slug"][:28] for t in grp))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
