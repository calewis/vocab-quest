#!/usr/bin/env python3
"""Merge Fable's boss picks -> validated word list with synonym groups."""
import json, glob, re, sys
sys.path.insert(0, "build")
import build_wordlist as bw

VALID_POS = {"noun", "verb", "adjective"}
groupmap = {c["w"]: c["group"] for c in json.load(open("build/boss_candidates.json"))}
existing = {it["w"] for items in json.load(open("build/final_words.json")).values() for it in items}

seen, out, bad = set(), [], []
for f in sorted(glob.glob("build/curate/boss_pick_*.json")):
    for it in json.load(open(f)):
        w = str(it.get("w", "")).lower().strip()
        if not w or it.get("pos") not in VALID_POS or not it.get("def"):
            bad.append((w, "fields")); continue
        if re.search(rf"\b{re.escape(w)}\b", it["def"], re.I):
            bad.append((w, "circular")); continue
        if w in seen or w in existing:
            continue
        seen.add(w)
        g = groupmap.get(w)
        if not g:
            s = bw.dominant_sense(w)
            g = f"{s.pos()}{s.offset()}" if s else ""
        out.append({"w": w, "pos": it["pos"], "def": it["def"], "group": g})

json.dump(out, open("build/curate/boss_words.json", "w"), ensure_ascii=False)
print(f"merged boss words: {len(out)}  (invalid {len(bad)})")
