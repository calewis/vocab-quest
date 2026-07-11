#!/usr/bin/env python3
"""Concatenate the 4 candidate tier files, tag each with its source tier,
shuffle (seeded), and split into fixed-size chunk files for the agents."""
import json, os, random, glob, sys

CHUNK = int(sys.argv[1]) if len(sys.argv) > 1 else 125

items = []
for t in ("grade", "middle", "high", "college"):
    for it in json.load(open(f"build/candidates/tier_{t}.json")):
        it["tier"] = t
        items.append(it)

random.seed(42)
random.shuffle(items)

for f in glob.glob("build/chunks/chunk_*.json"):
    os.remove(f)
os.makedirs("build/chunks", exist_ok=True)
os.makedirs("build/out", exist_ok=True)

n = 0
for i in range(0, len(items), CHUNK):
    with open(f"build/chunks/chunk_{n:03d}.json", "w") as f:
        json.dump(items[i:i + CHUNK], f, ensure_ascii=False)
    n += 1

print(f"{len(items)} candidates -> {n} chunks of {CHUNK}")
