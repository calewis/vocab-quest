#!/usr/bin/env python3
"""Merge agent outputs -> validated, tiered final word set.
Runs on whatever build/out/chunk_*.json files exist so far."""
import json, glob, re
from collections import defaultdict

TARGETS = {"grade": 600, "middle": 550, "high": 450, "college": 400}
VALID_POS = {"noun", "verb", "adjective"}

# word -> synonym group (synset id) from the candidate stage
group_map = {}
for t in TARGETS:
    for it in json.load(open(f"build/candidates/tier_{t}.json")):
        group_map[it["w"]] = it["group"]

keeps, drops, bad = {}, 0, []
files = sorted(glob.glob("build/out/chunk_*.json"))
for f in files:
    try:
        arr = json.load(open(f))
    except Exception as e:
        print("BAD JSON FILE:", f, e); continue
    for it in arr:
        if "drop" in it:
            drops += 1; continue
        w = str(it.get("w", "")).lower().strip()
        if not w or it.get("tier") not in TARGETS or it.get("pos") not in VALID_POS:
            bad.append((w, "fields")); continue
        if not it.get("def") or not it.get("sentence") or not it.get("form"):
            bad.append((w, "missing")); continue
        if re.search(rf"\b{re.escape(w)}\b", it["def"], re.I):
            bad.append((w, "circular-def")); continue
        if it["form"].lower() not in it["sentence"].lower():
            bad.append((w, "form-not-in-sentence")); continue
        if w in keeps:
            continue
        it["w"] = w
        it["group"] = group_map.get(w, "")
        keeps[w] = it

by_tier = defaultdict(list)
for it in keeps.values():
    by_tier[it["tier"]].append(it)

print(f"chunks merged: {len(files)}")
print(f"keeps: {len(keeps)}   drops: {drops}   invalid: {len(bad)}")
for w, r in bad[:25]:
    print("   bad:", w, r)
print("by tier :", {t: len(by_tier[t]) for t in TARGETS})
print("targets :", TARGETS)

final = {t: by_tier[t][:TARGETS[t]] for t in TARGETS}
json.dump(final, open("build/final_words.json", "w"), ensure_ascii=False)
print("wrote build/final_words.json ->", {t: len(v) for t, v in final.items()})
