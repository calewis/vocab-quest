#!/usr/bin/env python3
"""Write plain-text review files: one per tier (word | pos | definition) plus
a list of suggested alternative words not currently used anywhere.
Usage: review_files.py <tier> [<tier> ...]"""
import json, os, sys
sys.path.insert(0, "build")
import build_wordlist as bw

os.makedirs("build/review", exist_ok=True)
fw = json.load(open("build/final_words.working.json"))

def dump(tier):
    items = sorted(fw[tier], key=lambda x: x["w"])
    with open(f"build/review/{tier}_words.txt", "w") as f:
        f.write(f"# {tier.upper()} TIER — {len(items)} words\n")
        f.write("# Mark cuts with an 'x' at the start of the line; jot notes anywhere.\n")
        f.write("# word            pos        definition\n\n")
        for it in items:
            f.write(f"  {it['w']:<16} {it['pos']:<10} {it['def']}\n")
    print("wrote", f"build/review/{tier}_words.txt", len(items))

for t in sys.argv[1:]:
    if t in fw:
        dump(t)

# ---- suggested alternative words (not already used in any tier) ----
POOL = """
zany quirky nifty spry dapper sleek prim jaunty plucky chipper dour sulky moody testy cranky
witty shrewd cunning crafty devious sneaky rascal scamp rogue
gleaming glinting glistening twinkling flickering blazing scorching sweltering frigid balmy
muggy arid barren fertile whimsical eccentric bizarre outlandish majestic regal stately grand
modest lowly hectic turbulent tumultuous fidgety jittery peaceful courageous valiant heroic
fearless cowardly generous stingy thrifty frugal lavish extravagant diligent idle sluggish
lethargic listless elegant gawky ungainly
bolt saunter amble trek plod roam rove whittle chisel knead fashion craft grumble growl snarl
hiss squawk chirp cackle bray neigh whinny bleat cluck honk gallop scamper waddle slither
scuttle clamber vault hurdle
knoll dell glade grove thicket bramble hedge meadow manor mansion palace citadel cloak cape
shawl sash inkwell ledger tome torch spyglass sextant hearth mantel rafter cobweb burrow
warren thicket lagoon fjord cove inlet estuary bay reef marsh moor heath glen ravine gully
plume talon fang antler hoof bristle
""".split()

existing = {it["w"] for items in fw.values() for it in items}
sug, seen = [], set()
for w in POOL:
    w = w.lower()
    if w in existing or w in seen:
        continue
    seen.add(w)
    s = bw.dominant_sense(w)
    if s is None or s.instance_hypernyms():
        continue
    pos = bw.POS_NAME.get(s.pos())
    if pos is None:
        continue
    sug.append((w, pos, s.definition()))

sug = sug[:110]
with open("build/review/swap_suggestions.txt", "w") as f:
    f.write(f"# ~{len(sug)} SUGGESTED ALTERNATIVES — none currently used in any tier\n")
    f.write("# Circle/mark any you want swapped in, and tell me which tier.\n")
    f.write("# word            pos        (WordNet gloss; sentence gets written later)\n\n")
    for w, p, d in sug:
        f.write(f"  {w:<16} {p:<10} {d}\n")
print("wrote build/review/swap_suggestions.txt", len(sug))
