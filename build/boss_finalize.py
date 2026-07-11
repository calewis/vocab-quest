#!/usr/bin/env python3
"""Assemble the boss tier: word + def + group + real (shortened) sentence + form."""
import json, re

words = json.load(open("build/curate/boss_words.json"))
sents = json.load(open("build/curate/boss_sentences.json"))

def shorten(s, form):
    if len(s.split()) <= 30:
        return s
    for cl in re.split(r'[,;:—]| - ', s):
        if form.lower() in cl.lower() and 5 <= len(cl.split()) <= 30:
            cl = cl.strip()
            return cl if cl[:1].isupper() else "… " + cl
    w = s.split()
    idx = next((i for i, t in enumerate(w) if form.lower() in t.lower()), len(w)//2)
    a, b = max(0, idx-11), min(len(w), idx+12)
    return ("… " if a > 0 else "") + " ".join(w[a:b]) + (" …" if b < len(w) else "")

out = []
for it in words:
    sd = sents.get(it["w"])
    if not sd:
        continue
    sent = shorten(sd["s"], sd["form"])
    if sd["form"].lower() not in sent.lower():   # safety: keep the word visible
        continue
    out.append({"w": it["w"], "pos": it["pos"], "def": it["def"],
                "sentence": sent, "form": sd["form"], "group": it["group"], "c": ""})

json.dump(out, open("build/curate/boss_tier.json", "w"), ensure_ascii=False)
lens = [len(e["sentence"].split()) for e in out]
print(f"boss tier entries: {len(out)}")
print(f"sentence words: min {min(lens)}  median {sorted(lens)[len(lens)//2]}  max {max(lens)}")
