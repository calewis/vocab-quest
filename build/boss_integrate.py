#!/usr/bin/env python3
"""Apply the safety removals and add the boss tier to final_words.json."""
import json, os

tier = json.load(open("build/curate/boss_tier.json"))
removals = set()
rf = "build/curate/boss_removals.json"
if os.path.exists(rf):
    removals = {r["w"] if isinstance(r, dict) else r for r in json.load(open(rf))}

clean = [e for e in tier if e["w"] not in removals]
fw = json.load(open("build/final_words.json"))
fw["boss"] = [{"w": e["w"], "pos": e["pos"], "def": e["def"], "tier": "boss",
               "sentence": e["sentence"], "form": e["form"], "group": e["group"],
               "c": e.get("c", "")} for e in clean]
json.dump(fw, open("build/final_words.json", "w"), ensure_ascii=False)
print(f"safety removals applied: {len(removals)}  ->  boss tier: {len(fw['boss'])} words")
