#!/usr/bin/env python3
"""Embed final_words.json into index.html as a plain JSON object literal.
No gzip / base64 / DecompressionStream -> runs on any browser with JSON.
GitHub Pages still gzips it over the wire, so download size stays small."""
import json, re

POS_IDX = {"noun": 0, "verb": 1, "adjective": 2}

data = json.load(open("build/final_words.json"))
out = {}
for tier, items in data.items():
    out[tier] = [[it["w"], POS_IDX.get(it["pos"], 0), it["def"],
                  it["sentence"], it["form"], it["group"], it.get("c", "")] for it in items]

# minified, single line; escape </ so a stray "</script>" can't close the tag
raw = json.dumps(out, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
counts = {t: len(v) for t, v in out.items()}
print(f"words {sum(counts.values())} {counts}")
print(f"inline JSON bytes: {len(raw):,}")

html = open("index.html").read()
new, n = re.subn(r'const PACKED_DATA = .*;',
                 lambda m: "const PACKED_DATA = " + raw + ";", html, count=1)
if n != 1:
    raise SystemExit("ERROR: PACKED_DATA line not found in index.html")
open("index.html", "w").write(new)
print("injected plain JSON into index.html")
