#!/usr/bin/env python3
"""Split the grade tier into K-3 (easiest) and Grades 4-5, and gather the ~200
most common non-function words (not already in the DB) as K-3 additions."""
import json, sys
sys.path.insert(0, "build")
import build_wordlist as bw
import wordfreq
from wordfreq import top_n_list

fw = json.load(open("build/final_words.json"))
existing = {it["w"] for items in fw.values() for it in items}
grade = fw["grade"]
for it in grade:
    it["_z"] = wordfreq.zipf_frequency(it["w"], "en")

zs = sorted(it["_z"] for it in grade)
q = lambda p: zs[int(len(zs)*p)]
print(f"grade zipf: min {zs[0]}  p25 {q(.25)}  median {q(.5)}  p70 {q(.70)}  max {zs[-1]}")

TH = 4.7   # grade words at/above this frequency are the "absolutely easiest" -> K-3
k3g = [it for it in grade if it["_z"] >= TH]
g45 = [it for it in grade if it["_z"] < TH]
print(f"threshold {TH}: k3-from-grade {len(k3g)}  |  grades4-5 {len(g45)}")

# The most common *content* words a K-3 child knows (concrete nouns, action
# verbs, simple adjectives, colors) — the high-frequency sight vocabulary,
# minus function words. Deduped against everything already in the DB.
COMMON = """
dog cat cow pig hen duck fish frog bird bee ant bug fox owl bear lion tiger goat sheep horse
pony mouse rabbit deer wolf snake turtle whale shark monkey elephant zebra giraffe penguin
mom dad baby boy girl kid brother sister friend family grandma grandpa aunt uncle
head hair eye ear nose mouth tooth arm hand finger leg foot toe knee tummy
milk egg bread apple banana grape orange cake candy cookie pizza soup rice bean corn meat
cheese butter honey jam juice water
sun moon star sky cloud rain snow wind storm tree leaf flower grass hill lake pond river sea
beach sand mud dirt fire ice
house home door window roof wall floor bed chair table couch cup plate bowl spoon fork pot
pan book pencil crayon paper ball toy box bag hat shoe sock shirt coat glove clock lamp key
map card kite drum bell brush comb soap towel
car bus truck train plane boat bike road bridge
desk crayon park zoo farm store barn
day night noon week month
run jump hop skip walk march crawl kneel sleep wake eat drink bite chew taste sing dance
paint cut glue throw catch kick roll bounce swim dive fall slip trip laugh smile frown hug
kiss wave clap wash cook bake sweep share hide seek watch listen smell touch hold carry push
pull lift fill spill pour ring knock build ride fly float sink dig plant grow melt burn
freeze count spell
red blue green yellow black white brown pink purple orange gray gold
tall wide fat thin fast slow hot cold warm cool wet dry soft rough smooth loud quiet bright
heavy empty mean rude glad scared lazy busy hungry thirsty sleepy sick sweet sour salty
""".split()

adds, seen = [], set()
for w in COMMON:
    if w in existing or w in seen or w in bw.BLOCK or len(w) < 2:
        continue
    seen.add(w)
    s = bw.dominant_sense(w)
    adds.append({"w": w, "pos": bw.POS_NAME.get(s.pos(), "noun") if s else "noun",
                 "def": s.definition() if s else ""})

for it in grade:
    it.pop("_z", None)
json.dump(k3g, open("build/curate/k3_from_grade.json", "w"), ensure_ascii=False)
json.dump(g45, open("build/curate/g45_from_grade.json", "w"), ensure_ascii=False)
json.dump(adds, open("build/curate/k3_additions.json", "w"), ensure_ascii=False)
print(f"additions: {len(adds)}")
print("first 40:", ", ".join(a["w"] for a in adds[:40]))
