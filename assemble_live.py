# -*- coding: utf-8 -*-
"""Ensambla los borradores editoriales (drafts/*.json, escritos por los 4 redactores) con la
metadata fija (articles_meta.json: categoría, tokens, fuente, imagen real) -> articles_live.json,
que set_articles.py consume. Tolera fences ```json y valida que no falte ninguna nota."""
import glob
import json
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parent
DRAFTS = BASE / "drafts"
META = json.load(open(BASE / "articles_meta.json", encoding="utf-8"))

# Campos editoriales que deben venir del redactor
NEED = ("headline", "dek", "focus_keyword", "read_minutes", "meta_description", "why", "takeaway", "body")


def _load_json_loose(text: str):
    t = text.strip()
    t = re.sub(r"^```(?:json)?", "", t).strip()
    t = re.sub(r"```$", "", t).strip()
    # por si el agente antepuso prosa: recorta al primer [ ... ] o { ... }
    i, j = t.find("["), t.rfind("]")
    if i != -1 and j != -1 and j > i:
        t = t[i:j + 1]
    return json.loads(t)


def main() -> int:
    articles, seen, problems = [], set(), []
    files = sorted(glob.glob(str(DRAFTS / "*.json")))
    if not files:
        print("No hay drafts/*.json todavía."); return 1
    for f in files:
        try:
            arr = _load_json_loose(pathlib.Path(f).read_text(encoding="utf-8"))
        except Exception as e:
            problems.append(f"{pathlib.Path(f).name}: no parsea ({e})"); continue
        for a in (arr if isinstance(arr, list) else [arr]):
            slug = a.get("slug")
            if not slug or slug in seen:
                continue
            miss = [k for k in NEED if k not in a]
            if miss:
                problems.append(f"{slug}: faltan {miss}"); continue
            m = META.get(slug)
            if not m:
                problems.append(f"{slug}: sin metadata en articles_meta.json"); continue
            articles.append({**a, **m})   # editorial + metadata fija (cat/tokens/fuente/imagen)
            seen.add(slug)

    missing = [s for s in META if s not in seen]
    if missing:
        problems.append("Faltan notas por redactar: " + ", ".join(missing))

    json.dump({"articles": articles}, open(BASE / "articles_live.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"ensamblado: {len(articles)}/{len(META)} notas -> articles_live.json")
    for p in problems:
        print("  [!]", p)
    return 0 if not problems else 2


if __name__ == "__main__":
    raise SystemExit(main())
