#!/usr/bin/env python3
"""Merge polished curated words back into the working word set.
Usage: curate_apply.py <tier> <candidates_file> <polished_out_file>
Reads/writes build/final_words.working.json."""
import json, re, sys

tier, cand_file, out_file = sys.argv[1], sys.argv[2], sys.argv[3]
VALID_POS = {"noun", "verb", "adjective"}

fw = json.load(open("build/final_words.working.json"))
groups = {c["w"]: c["group"] for c in json.load(open(cand_file))}
polished = json.load(open(out_file))
existing = {it["w"] for items in fw.values() for it in items}

added, dropped, bad = [], 0, []
for it in polished:
    if "drop" in it:
        dropped += 1; continue
    w = str(it.get("w", "")).lower().strip()
    if not w or it.get("pos") not in VALID_POS or not it.get("def") or not it.get("sentence") or not it.get("form"):
        bad.append((w, "fields")); continue
    if it["form"].lower() not in it["sentence"].lower():
        bad.append((w, "form")); continue
    if re.search(rf"\b{re.escape(w)}\b", it["def"], re.I):
        bad.append((w, "circular")); continue
    if w in existing:
        bad.append((w, "dup")); continue
    existing.add(w)
    added.append({"w": w, "pos": it["pos"], "def": it["def"], "tier": tier,
                  "sentence": it["sentence"], "form": it["form"], "group": groups.get(w, "")})

fw[tier].extend(added)
json.dump(fw, open("build/final_words.working.json", "w"), ensure_ascii=False)
print(f"{tier}: added {len(added)}, dropped {dropped}, invalid {len(bad)} -> tier now {len(fw[tier])}")
if bad:
    print("  invalid:", bad[:15])
