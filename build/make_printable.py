#!/usr/bin/env python3
"""Printable word-list sheet (words only, labeled by tier, multi-column).
Usage: make_printable.py <tier> [<tier> ...] -> build/review/wordlists_printable.html"""
import json, sys, html

TIER_LABEL = {"grade": "Grade School (ages 6–10)", "middle": "Middle School (ages 11–13)",
              "high": "High School (ages 14–17)", "college": "College (advanced)"}

fw = json.load(open("build/final_words.json"))
tiers = [t for t in sys.argv[1:] if t in fw]

parts = ["""<!doctype html><html><head><meta charset="utf-8"><title>Vocab Quest — Word Lists</title>
<style>
  @page { margin: 0.5in; }
  body { font: 10px/1.35 -apple-system, Arial, sans-serif; color:#000; margin:0; }
  h1 { font-size: 16px; margin: 0 0 2px; }
  .sub { color:#555; font-size:10px; margin-bottom:10px; }
  section { break-before: page; }
  section:first-of-type { break-before: auto; }
  h2 { font-size: 13px; margin: 0 0 6px; padding:3px 6px; background:#eee;
       border-left: 4px solid #7c3aed; }
  .count { font-weight: normal; color:#666; font-size:10px; }
  ul { columns: 5; column-gap: 14px; list-style:none; margin:0; padding:0; }
  li { break-inside: avoid; padding: 1px 0; white-space: nowrap; }
  li::before { content: "\\2610  "; color:#bbb; }   /* empty checkbox to mark cuts */
  @media print { .noprint { display:none; } }
</style></head><body>
<h1>Vocab Quest — Word Lists for Review</h1>
<div class="sub noprint">Tip: print this page (Cmd/Ctrl-P). Check the box next to any word to cut it.</div>
"""]

for t in tiers:
    words = sorted(x["w"] for x in fw[t])
    parts.append(f'<section><h2>{TIER_LABEL.get(t,t)} <span class="count">— {len(words)} words</span></h2><ul>')
    parts.extend(f"<li>{html.escape(w)}</li>" for w in words)
    parts.append("</ul></section>")

parts.append("</body></html>")
open("build/review/wordlists_printable.html", "w").write("".join(parts))
print("wrote build/review/wordlists_printable.html for tiers:", ", ".join(tiers))
