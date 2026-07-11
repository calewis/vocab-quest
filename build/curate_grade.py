#!/usr/bin/env python3
"""Opus taste-curation for the GRADE tier: drop words that aren't real
1st-5th-grade vocab, build WordNet candidates for vivid replacements.
Replacements get polished (def + literary sentence) by a Sonnet agent next."""
import json, os, sys
sys.path.insert(0, "build")
import build_wordlist as bw

REMOVE = set("""
holder maker owner employer manager monitor reporter inspector
base matter form set unit section term terms mass core item element point line mark
agency alliance asset collective component funding profit retail regime treaty resource
resistance network operation occasion importance recognition popularity presence
preparation presentation comparison expression connection protection purpose unity
production difficulty confidence behavior
maximum minimum moderate various several few zero plus ninth addition degree limit depth
efficient technical historical international educational medical previous distinct broad
actual basic overall supreme local major current proper regular
demonstrate determine obtain provide transfer register display capture boost
weapon bomb bullet gun arsenal violence invasion revenge threat defeat flesh sue illegal
tum aunty gran sake okay felt spoke due self whole top low near middle true chaos
repeated threatened cheating dedicated retired
advantage academy action brand draft stroke logo concrete asset
""".split())

# Rich, teachable, concrete/vivid grade-level vocab. Over-supplied; the script
# validates against WordNet + existing words and takes what it needs.
ADD_POOL = """
brave gentle clumsy grumpy enormous gigantic fragile cheerful weary drowsy sturdy cozy
fluffy fuzzy prickly slippery sticky jolly greedy timid eager polite rude honest loyal
stubborn marvelous magnificent dizzy filthy ancient mighty fierce silent nervous proud
lonely silly bold swift graceful delicate damp crisp snug plump wobbly bumpy gloomy chilly
frosty breezy glossy dull spotless scruffy soggy crunchy tender juicy tangled hollow ragged
feeble restless nimble sleepy speckled
whisper gobble nibble munch stumble stagger wander scurry dash scamper giggle chuckle shiver
tremble sniff sneeze yawn stretch squeeze snatch toss fling explore discover scatter sprinkle
splash drip shimmer sparkle glow rumble roar buzz creak rustle blossom sprout drift soar dive
pounce gallop wriggle squirm clutch cling tug murmur mutter gaze peek glare frown grin weep
invent stack chase scrub sweep carve weave knit dig
meadow pebble puddle boulder cliff valley stream brook pond shore burrow nest lantern candle
blanket quilt mitten scarf sled kite marble bubble feather whisker claw beak mane herd flock
swarm orchard barn cottage cabin chimney attic cellar porch fence gate trail tower castle
treasure compass telescope magnet acorn pinecone petal thorn vine moss fern seashell dune
volcano comet galaxy rainbow thunder lightning blizzard breeze frost icicle ripple waterfall
otter beaver badger hedgehog squirrel chipmunk raccoon moose walrus dolphin octopus jellyfish
starfish crab lobster flamingo peacock ostrich parrot sparrow robin hawk owl hamster lizard
gecko turtle tortoise frog toad beetle ladybug dragonfly grasshopper caterpillar moth firefly
snail worm spider kitten puppy foal piglet lamb tadpole
""".split()

fw = json.load(open("build/final_words.json"))
os.makedirs("build/curate", exist_ok=True)
if not os.path.exists("build/final_words.backup.json"):
    json.dump(fw, open("build/final_words.backup.json", "w"), ensure_ascii=False)

existing = {it["w"] for items in fw.values() for it in items}

grade = fw["grade"]
before = len(grade)
removed = [it["w"] for it in grade if it["w"] in REMOVE]
fw["grade"] = [it for it in grade if it["w"] not in REMOVE]
missing = sorted(REMOVE - set(removed))
need = before - len(fw["grade"])

cands, skipped, seen = [], [], set()
for w in ADD_POOL:
    w = w.lower()
    if w in existing or w in seen or w in REMOVE:
        skipped.append(w); continue
    seen.add(w)
    s = bw.dominant_sense(w)
    if s is None or s.instance_hypernyms():
        skipped.append(w); continue
    pos = bw.POS_NAME.get(s.pos())
    if pos is None:
        skipped.append(w); continue
    cands.append({"w": w, "pos": pos, "def": s.definition(),
                  "group": f"{s.pos()}{s.offset()}",
                  "zipf": round(bw.wordfreq.zipf_frequency(w, "en"), 2), "tier": "grade"})

take = cands[:need]
json.dump(take, open("build/curate/grade_new_candidates.json", "w"), ensure_ascii=False)
json.dump(fw, open("build/final_words.working.json", "w"), ensure_ascii=False)
print(f"grade: before {before}, removed {len(removed)}, kept {len(fw['grade'])}, need {need}")
print(f"valid add candidates: {len(cands)} (pool {len(ADD_POOL)}); using {len(take)}")
print(f"REMOVE entries not found in tier ({len(missing)}): {missing}")
if len(cands) < need:
    print(f"!! WARNING: only {len(cands)} adds available, short by {need-len(cands)}")
