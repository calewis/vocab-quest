#!/usr/bin/env python3
"""Merge the per-tier ambiguity clusters into final_words.json as a conflict-id
field 'c'. Two words sharing a non-empty 'c' never appear together as options.
Re-runnable: reads whatever conflicts_<tier>.json files exist."""
import json, os

fw = json.load(open("build/final_words.json"))
for items in fw.values():
    for it in items:
        it["c"] = ""   # reset each run

total = 0
for t in ("grade", "middle", "high", "college"):
    f = f"build/curate/conflicts_{t}.json"
    if not os.path.exists(f):
        print(f"  {t}: no conflict file yet — skipped")
        continue
    clusters = json.load(open(f))
    wmap = {it["w"]: it for it in fw[t]}
    for k, cluster in enumerate(clusters):
        cid = f"{t[0]}{k}"
        for w in cluster:
            it = wmap.get(str(w).lower())
            if it:
                it["c"] = cid
    covered = sum(1 for it in fw[t] if it["c"])
    total += covered
    print(f"  {t}: {len(clusters)} clusters, {covered} words tagged")

json.dump(fw, open("build/final_words.json", "w"), ensure_ascii=False)
print(f"total words tagged with a conflict id: {total}")
