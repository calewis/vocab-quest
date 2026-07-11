#!/usr/bin/env python3
import json, re
from collections import Counter

files = ["build/pilot_low.json", "build/pilot_high.json"]
keeps, drops = [], []
for f in files:
    data = json.load(open(f))
    for tier, items in data.items():
        for it in items:
            (drops if "drop" in it else keeps).append(it)

def sentence_has_word(word, sent):
    stem = re.escape(word[:-1] if word.endswith("e") else word)
    return re.search(rf"\b{re.escape(word)}|{stem}\w*", sent, re.I) is not None

print(f"KEEP: {len(keeps)}   DROP: {len(drops)}")
print("\ndrops:", ", ".join(f"{d['w']}" for d in drops))

# integrity checks
bad_sent, bad_def, missing = [], [], []
for k in keeps:
    if not all(x in k for x in ("w", "pos", "def", "tier", "sentence")):
        missing.append(k.get("w")); continue
    if not sentence_has_word(k["w"], k["sentence"]):
        bad_sent.append(k["w"])
    if re.search(rf"\b{re.escape(k['w'])}\b", k["def"], re.I):
        bad_def.append(k["w"])

print("\nsentence missing its word:", bad_sent or "none")
print("definition contains its word:", bad_def or "none")
print("missing fields:", missing or "none")

# tier redistribution (where the agents moved words)
print("\ntier after age-check:", dict(Counter(k["tier"] for k in keeps)))
