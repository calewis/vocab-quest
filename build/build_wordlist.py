#!/usr/bin/env python3
"""
Stage 1: build a tiered candidate word list from WordNet + wordfreq.
No LLM here — purely free/local data. Output feeds the agent polish stage.

Per word we keep the DOMINANT sense only (most frequent per SemCor counts),
its definition, part of speech, and a synonym-group id (the synset), which
the game uses to keep two synonyms out of the same 12-tile round.

Difficulty tiers are assigned by word frequency (Zipf); the LLM agents will
later re-check age-appropriateness and re-bucket / drop as needed, so this
just has to be roughly right and slightly over-generated.
"""
import re, json, os
from nltk.corpus import wordnet as wn
import wordfreq

WORD_RE = re.compile(r"^[a-z]{3,}$")

# Offensive-word blocklist is kept OUT of version control (see .gitignore);
# it lives locally in build/blocklist.txt. Empty set if the file is absent.
BLOCK = set(open("build/blocklist.txt").read().split()) if os.path.exists("build/blocklist.txt") else set()

# function / structural words that make dull or misleading puzzle entries
STOP = set("""
the a an and or but nor for yet so as if then than that this these those
is are was were be been being am has have had do does did will would shall should
can could may might must ought
i you he she it we they me him her us them my your his its our their mine yours
to of in on at by from with without into onto upon over under above below
between among through during before after about against along around
not no yes very just only also too even still much many more most less least
who whom whose which what where when why how here there
one two three four five six seven eight nine ten
""".split())

POS_NAME = {"n": "noun", "v": "verb", "a": "adjective", "s": "adjective"}  # adverbs dropped

# over-feed, weighted toward harder bands (they lose the most to downward
# re-bucketing by the age-check); final targets are 600/550/450/400.
TARGET_KEEP = {"grade": 550, "middle": 600, "high": 650, "college": 700}

# Zipf bands -> tier.  Higher Zipf = more common = easier.
# Upper cap 5.6 sheds ultra-common function words; the LLM stage re-buckets.
def tier_for(zipf):
    if zipf > 5.6:   return None
    if zipf >= 4.2:  return "grade"
    if zipf >= 3.8:  return "middle"
    if zipf >= 3.4:  return "high"
    if zipf >= 2.9:  return "college"
    return None  # too rare for now (reserved for the future boss tier)

def dominant_sense(word):
    syns = wn.synsets(word)
    if not syns:
        return None
    best, best_count, best_idx = None, -1, 10**9
    for i, s in enumerate(syns):
        cnt = 0
        for l in s.lemmas():
            if l.name().lower() == word:
                cnt = l.count()
                break
        if cnt > best_count or (cnt == best_count and i < best_idx):
            best, best_count, best_idx = s, cnt, i
    return best

def main():
    seen = set()
    tiers = {"grade": [], "middle": [], "high": [], "college": []}
    for word in wn.all_lemma_names():
        word = word.lower()
        if word in seen or not WORD_RE.match(word) or word in BLOCK or word in STOP:
            continue
        seen.add(word)
        # block vulgar inflections via their base form (pissed -> piss)
        if {wn.morphy(word, p) for p in "nva"} & BLOCK:
            continue
        z = wordfreq.zipf_frequency(word, "en")
        tier = tier_for(z)
        if tier is None:
            continue
        s = dominant_sense(word)
        if s is None:
            continue
        # drop proper nouns (WordNet marks them as instances)
        if s.instance_hypernyms():
            continue
        pos = POS_NAME.get(s.pos())
        if pos is None:  # adverbs / unknown
            continue
        # drop inflected forms (plurals, participles): morphy reduces them to a
        # different base that also exists in WordNet -> "designed"->"design"
        mp = "a" if s.pos() in ("a", "s") else s.pos()
        base = wn.morphy(word, mp)
        if base and base != word:
            continue
        d = s.definition()
        if not d or len(d) < 8 or len(d) > 140:
            continue
        # drop circular definitions that contain the word itself
        if re.search(rf"\b{re.escape(word)}\b", d, re.I):
            continue
        if not re.search(r"[aeiou]", word):  # abbreviation-y oddities
            continue
        tiers[tier].append({
            "w": word,
            "pos": pos,
            "def": d,
            "group": f"{s.pos()}{s.offset()}",
            "zipf": round(z, 2),
        })

    os.makedirs("build/candidates", exist_ok=True)
    print(f"{'tier':8} {'raw':>6} {'kept':>6}   sample of kept words")
    print("-" * 78)
    for t, items in tiers.items():
        items.sort(key=lambda x: -x["zipf"])
        raw = len(items)
        keep = TARGET_KEEP[t]
        if raw > keep:  # evenly sample across the frequency band for variety
            step = raw / keep
            items = [items[int(i * step)] for i in range(keep)]
        with open(f"build/candidates/tier_{t}.json", "w") as f:
            json.dump(items, f, ensure_ascii=False, indent=0)
        sample = ", ".join(x["w"] for x in items[::max(1, len(items)//14)][:14])
        print(f"{t:8} {raw:>6} {len(items):>6}   {sample}")

    # small pilot for quality review before the full billable run
    pilot = {}
    for t, items in tiers.items():
        items = json.load(open(f"build/candidates/tier_{t}.json"))
        step = max(1, len(items) // 15)
        pilot[t] = items[::step][:15]
    with open("build/candidates/pilot.json", "w") as f:
        json.dump(pilot, f, ensure_ascii=False, indent=1)
    print("-" * 78)
    print("wrote build/candidates/pilot.json (15 words/tier for review)")

if __name__ == "__main__":
    main()
