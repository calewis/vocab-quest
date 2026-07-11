#!/usr/bin/env python3
"""Generic tier curation. Reads the WORKING word set, removes the words listed
in <remove_file>, and builds WordNet replacement candidates from <addpool_file>.
Usage: curate_tier.py <tier> <remove_file> <addpool_file>"""
import json, sys
sys.path.insert(0, "build")
import build_wordlist as bw

tier, remove_file, addpool_file = sys.argv[1], sys.argv[2], sys.argv[3]
REMOVE = set(open(remove_file).read().split())
ADD_POOL = open(addpool_file).read().split()

fw = json.load(open("build/final_words.working.json"))
existing = {it["w"] for items in fw.values() for it in items}

col = fw[tier]
before = len(col)
removed = [it["w"] for it in col if it["w"] in REMOVE]
fw[tier] = [it for it in col if it["w"] not in REMOVE]
missing = sorted(REMOVE - set(removed))
need = before - len(fw[tier])

cands, seen = [], set()
for w in ADD_POOL:
    w = w.lower()
    if w in existing or w in seen or w in REMOVE:
        continue
    seen.add(w)
    s = bw.dominant_sense(w)
    if s is None or s.instance_hypernyms():
        continue
    pos = bw.POS_NAME.get(s.pos())
    if pos is None:
        continue
    cands.append({"w": w, "pos": pos, "def": s.definition(),
                  "group": f"{s.pos()}{s.offset()}",
                  "zipf": round(bw.wordfreq.zipf_frequency(w, "en"), 2), "tier": tier})

take = cands[:need]
json.dump(take, open(f"build/curate/{tier}_new_candidates.json", "w"), ensure_ascii=False)
json.dump(fw, open("build/final_words.working.json", "w"), ensure_ascii=False)
print(f"{tier}: before {before}, removed {len(removed)}, kept {len(fw[tier])}, need {need}")
print(f"valid add candidates: {len(cands)}; using {len(take)}")
print(f"REMOVE not found ({len(missing)}): {missing}")
if len(cands) < need:
    print(f"!! only {len(cands)} adds, short {need-len(cands)}")
