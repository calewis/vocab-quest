#!/usr/bin/env python3
"""Opus taste-curation for the MIDDLE tier. Operates on the WORKING set
(post-grade), removes dry/corporate/agent-noun/crude entries, builds vivid
replacement candidates for a Sonnet polish pass."""
import json, sys
sys.path.insert(0, "build")
import build_wordlist as bw

REMOVE = set("""
accountability adjustment advisory affiliate allowable allowance application appoint
assurance assured audit autonomous aviation behavioral boycott clearance completion
cellular con bust businessman commuter cleaner dieter fisher hairdresser investigator
investor listener observer porter prosecutor prosecution receiver receptionist striker
traveller visitor animator blogger bot reboot upload startup spreadsheet interface micro
indie temp offset output format install subscribe charger projector dispenser deficit
delegation detection digestion disposal effectiveness enforcement engagement extraction
geological incorporate isolation membrane nuclear orientation organizational presidency
prospective publishing quarantine succession surveillance taxation taxpayer tenure
therapeutic thermal tuition withdrawal willingness sensitivity stiffness sweetness
nervousness goodness ignorance abundance confirmation conjunction convention coordinate
criticism damages disapproval communication competition examination exhibition
inconvenience inspection interference introduction reference reflection reservation
selection process premise par factor medium effect ease exist enable arise react comply
intend implement dismiss disturb dissolve disappoint acknowledge vomit spit jerk grub
shotgun amazon android applicable comparable adequate
""".split())

ADD_POOL = """
brisk vivid somber dreary radiant frantic hesitant reluctant sincere gracious arrogant
humble bashful defiant awkward brittle coarse eerie glorious gruff jagged keen lush murky
quaint rugged scarce serene sly tranquil wary wicked wistful bleak dazzling dismal immense
jovial luminous mellow meager peculiar placid rickety savage sullen vibrant vigorous frail
gaunt dainty drab lofty stark dreadful ghastly gallant
linger sprint dart lunge hoist grasp seize shatter crumble wither flourish dwindle swell
plunge glide trudge sway quiver shudder wince scowl smirk whimper bellow mumble ponder peer
scan sketch scribble forge mold assemble demolish conceal reveal pursue prowl lurk dread
loom wrestle clench sever drape kindle smolder unravel meander
horizon ridge summit gorge glacier marsh swamp lagoon reef prairie tundra cavern tide gust
drizzle hail sleet mist haze ember cinder beacon anchor mast harbor voyage quest legend myth
riddle fable verse melody chorus canvas sculpture portrait mural quill parchment scroll
dagger shield armor banner fortress moat turret chariot stallion mare hound falcon raven
heron lynx antelope gazelle panther cobra mongoose
""".split()

fw = json.load(open("build/final_words.working.json"))
existing = {it["w"] for items in fw.values() for it in items}

middle = fw["middle"]
before = len(middle)
removed = [it["w"] for it in middle if it["w"] in REMOVE]
fw["middle"] = [it for it in middle if it["w"] not in REMOVE]
missing = sorted(REMOVE - set(removed))
need = before - len(fw["middle"])

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
                  "zipf": round(bw.wordfreq.zipf_frequency(w, "en"), 2), "tier": "middle"})

take = cands[:need]
json.dump(take, open("build/curate/middle_new_candidates.json", "w"), ensure_ascii=False)
json.dump(fw, open("build/final_words.working.json", "w"), ensure_ascii=False)
print(f"middle: before {before}, removed {len(removed)}, kept {len(fw['middle'])}, need {need}")
print(f"valid add candidates: {len(cands)}; using {len(take)}")
print(f"REMOVE entries not found in tier ({len(missing)}): {missing}")
if len(cands) < need:
    print(f"!! WARNING: only {len(cands)} adds, short by {need-len(cands)}")
