#!/usr/bin/env python3
"""Generate extra grade + college candidates (the short tiers) that were NOT
already sent to agents, and write them as new chunk files (chunk_020+)."""
import json, re, glob, random, sys
from nltk.corpus import wordnet as wn
import wordfreq
sys.path.insert(0, "build")
import build_wordlist as bw

sent = set()
for f in glob.glob("build/chunks/chunk_*.json"):
    for it in json.load(open(f)):
        sent.add(it["w"])

extra = {"grade": [], "college": []}
seen = set()
for word in wn.all_lemma_names():
    word = word.lower()
    if word in seen or not bw.WORD_RE.match(word) or word in bw.BLOCK or word in bw.STOP:
        continue
    seen.add(word)
    if word in sent:
        continue
    if {wn.morphy(word, p) for p in "nva"} & bw.BLOCK:
        continue
    z = wordfreq.zipf_frequency(word, "en")
    tier = bw.tier_for(z)
    if tier not in ("grade", "college"):
        continue
    s = bw.dominant_sense(word)
    if s is None or s.instance_hypernyms():
        continue
    pos = bw.POS_NAME.get(s.pos())
    if pos is None:
        continue
    mp = "a" if s.pos() in ("a", "s") else s.pos()
    base = wn.morphy(word, mp)
    if base and base != word:
        continue
    d = s.definition()
    if not d or len(d) < 8 or len(d) > 140:
        continue
    if re.search(rf"\b{re.escape(word)}\b", d, re.I):
        continue
    if not re.search(r"[aeiou]", word):
        continue
    extra[tier].append({"w": word, "pos": pos, "def": d,
                        "group": f"{s.pos()}{s.offset()}", "zipf": round(z, 2), "tier": tier})

random.seed(7)
random.shuffle(extra["grade"]); random.shuffle(extra["college"])
backfill = extra["grade"][:375] + extra["college"][:125]
random.shuffle(backfill)

CHUNK, start = 125, 20
n = 0
for i in range(0, len(backfill), CHUNK):
    with open(f"build/chunks/chunk_{start+n:03d}.json", "w") as f:
        json.dump(backfill[i:i + CHUNK], f, ensure_ascii=False)
    n += 1
print(f"fresh grade avail {len(extra['grade'])}, college avail {len(extra['college'])}")
print(f"backfill {len(backfill)} words -> chunks {start:03d}..{start+n-1:03d}")
