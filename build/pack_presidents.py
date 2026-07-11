#!/usr/bin/env python3
"""Inject build/presidents.json into the PRES_DATA slot in index.html.
Run after build/presidents.py. Portraits are verified public domain."""
import json, re

data = json.load(open("build/presidents.json"))
raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = open("index.html").read()
new, n = re.subn(r'const PRES_DATA = .*?; /\*__PRES__\*/',
                 "const PRES_DATA = " + raw + "; /*__PRES__*/", html, count=1, flags=re.S)
if n != 1:
    raise SystemExit("ERROR: PRES_DATA placeholder not found in index.html")
open("index.html", "w").write(new)
print(f"injected {len(data)} presidents ({len(raw)//1024}KB) into index.html")
