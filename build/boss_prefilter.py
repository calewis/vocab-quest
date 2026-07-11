#!/usr/bin/env python3
"""Cut the boss candidates down to the rare/long/attested set, shuffle, and
split into chunks for Fable to curate."""
import json, os, random, glob

c = json.load(open("build/boss_candidates.json"))
keep = [x for x in c if x["zipf"] <= 2.3 and len(x["w"]) >= 6 and x["count"] >= 3]
random.seed(11)
random.shuffle(keep)

for f in glob.glob("build/curate/boss_chunk_*.json"):
    os.remove(f)
os.makedirs("build/curate", exist_ok=True)
SIZE, n = 300, 0
for i in range(0, len(keep), SIZE):
    json.dump(keep[i:i+SIZE], open(f"build/curate/boss_chunk_{n:02d}.json", "w"), ensure_ascii=False)
    n += 1
print(f"pre-Fable candidates: {len(keep)} -> {n} chunks of {SIZE}")
