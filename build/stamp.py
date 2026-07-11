#!/usr/bin/env python3
"""Stamp the current git short SHA + commit date into the version tag in
index.html. Run right before deploying:  python3 build/stamp.py

The stamped SHA is the commit the build is based on (HEAD at stamp time); the
follow-up "stamp version" commit itself only changes this one string."""
import subprocess, re, sys

def git(*args):
    return subprocess.check_output(["git", *args]).decode().strip()

sha  = git("rev-parse", "--short", "HEAD")
date = git("log", "-1", "--format=%cd", "--date=short")
ver  = f"v {sha} · {date}"

html = open("index.html").read()
new, n = re.subn(r'(<div class="version" id="version">).*?(</div>)',
                 lambda m: m.group(1) + ver + m.group(2), html, flags=re.S)
if n != 1:
    raise SystemExit("ERROR: version element not found in index.html")
open("index.html", "w").write(new)
print("stamped", ver)
