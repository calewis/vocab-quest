#!/usr/bin/env python3
"""Final Boss candidate builder.
Corpus: every .txt in books/ (Gutenberg boilerplate stripped).
Pipeline: unique words -> real dictionary words (WordNet, drop proper nouns via
instance-synsets + a capitalization heuristic) -> drop words already in our DB
-> drop common words (wordfreq Zipf) -> keep only the rare, book-attested ones.
"""
import re, json, glob, sys
from collections import defaultdict
sys.path.insert(0, "build")
import build_wordlist as bw
from nltk.corpus import wordnet as wn
import wordfreq

TOKEN = re.compile(r"[A-Za-z]+")
ZIPF_MAX = 2.9          # rarer than the College floor -> genuinely hard
MIN_COUNT = 2           # must appear >=2x so we can pull a real sentence
CAP_RATIO_MAX = 0.85    # mostly-capitalised word = proper noun -> drop
MIN_LEN = 4

def strip_gutenberg(text):
    a = text.find("*** START OF")
    b = text.find("*** END OF")
    if a != -1:
        a = text.find("\n", a)
        return text[a:(b if b != -1 else len(text))]
    return text

# --- count words + capitalisation across the whole corpus ---
count = defaultdict(int)
cap = defaultdict(int)
files = [f for f in glob.glob("books/*.txt") if "list_of_pg_urls" not in f]
for f in files:
    text = strip_gutenberg(open(f, encoding="utf-8", errors="ignore").read())
    for tok in TOKEN.findall(text):
        low = tok.lower()
        count[low] += 1
        if tok[0].isupper():
            cap[low] += 1
print(f"corpus: {len(files)} books, {len(count):,} unique raw tokens")

# --- filter ---
existing = {it["w"] for items in json.load(open("build/final_words.json")).values() for it in items}
cands = []
for w, c in count.items():
    if c < MIN_COUNT or len(w) < MIN_LEN or not bw.WORD_RE.match(w):
        continue
    if w in existing or w in bw.BLOCK or w in bw.STOP:
        continue
    if cap[w] / c > CAP_RATIO_MAX:          # proper noun
        continue
    if wordfreq.zipf_frequency(w, "en") > ZIPF_MAX:   # too common
        continue
    s = bw.dominant_sense(w)
    if s is None or s.instance_hypernyms():           # no dict sense / proper noun
        continue
    pos = bw.POS_NAME.get(s.pos())
    if pos is None:
        continue
    mp = "a" if s.pos() in ("a", "s") else s.pos()
    base = wn.morphy(w, mp)
    if base and base != w:                            # inflected form
        continue
    d = s.definition()
    if not d or len(d) < 8 or len(d) > 160 or re.search(rf"\b{re.escape(w)}\b", d, re.I):
        continue
    cands.append({"w": w, "pos": pos, "def": d, "group": f"{s.pos()}{s.offset()}",
                  "zipf": round(wordfreq.zipf_frequency(w, "en"), 2), "count": c})

cands.sort(key=lambda x: -x["count"])   # book-attested first (easier to quote)
json.dump(cands, open("build/boss_candidates.json", "w"), ensure_ascii=False)
print(f"candidates after all filters: {len(cands)}")
print("sample (frequent-in-books, rare-in-english):")
for x in cands[:30]:
    print(f"  {x['w']:<16} zipf={x['zipf']:<4} books×{x['count']:<3} {x['def'][:55]}")
