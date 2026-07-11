#!/usr/bin/env python3
"""Replace the grade tier with k3 (easiest grade words + common additions) and
g45 (the rest of grade). Run after the Haiku additions are polished."""
import json, re, sys
sys.path.insert(0, "build")
import build_wordlist as bw

VALID = {"noun", "verb", "adjective"}
fw = json.load(open("build/final_words.json"))
k3g = json.load(open("build/curate/k3_from_grade.json"))
g45 = json.load(open("build/curate/g45_from_grade.json"))
for it in k3g: it["tier"] = "k3"
for it in g45: it["tier"] = "g45"

adds, seen = [], set()
for f in ("build/curate/k3_add_out_0.json", "build/curate/k3_add_out_1.json"):
    for it in json.load(open(f)):
        if "drop" in it:
            continue
        w = str(it.get("w", "")).lower().strip()
        if not w or it.get("pos") not in VALID or not it.get("def") or not it.get("sentence") or not it.get("form"):
            continue
        if it["form"].lower() not in it["sentence"].lower():
            continue
        if re.search(rf"\b{re.escape(w)}\b", it["def"], re.I) or w in seen:
            continue
        seen.add(w)
        s = bw.dominant_sense(w)
        adds.append({"w": w, "pos": it["pos"], "def": it["def"], "tier": "k3",
                     "sentence": it["sentence"], "form": it["form"],
                     "group": f"{s.pos()}{s.offset()}" if s else "", "c": ""})

new = {"k3": k3g + adds, "g45": g45}
for t in ("middle", "high", "college", "boss"):
    new[t] = fw[t]
json.dump(new, open("build/final_words.json", "w"), ensure_ascii=False)
print(f"k3: {len(new['k3'])} (grade-easy {len(k3g)} + additions {len(adds)})   g45: {len(new['g45'])}")
