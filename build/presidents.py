#!/usr/bin/env python3
"""Fetch presidential portraits that are VERIFIED public domain, shrink them, and
write build/presidents.json ([[num, name, dataURI], ...]) plus a provenance file
build/presidents_credits.json (source + license per portrait).

Copyright safety: we take each president's Wikipedia lead portrait, then query the
Wikimedia Commons license metadata for that exact file and ONLY embed it if the
license is public domain. Anything not confirmed PD is skipped and reported, so a
human can substitute a known-PD federal/Library-of-Congress image. Portraits of US
presidents in the public domain are overwhelmingly federal works (White House / DoD
photographers) or old enough to be PD; their Commons source is usually the Library
of Congress or the National Archives, which we record.
"""
import json, subprocess, urllib.parse, urllib.request, tempfile, os, base64, sys, time

PRES = [
    (1,"George Washington","George Washington"),(2,"John Adams","John Adams"),
    (3,"Thomas Jefferson","Thomas Jefferson"),(4,"James Madison","James Madison"),
    (5,"James Monroe","James Monroe"),(6,"John Quincy Adams","John Quincy Adams"),
    (7,"Andrew Jackson","Andrew Jackson"),(8,"Martin Van Buren","Martin Van Buren"),
    (9,"William Henry Harrison","William Henry Harrison"),(10,"John Tyler","John Tyler"),
    (11,"James K. Polk","James K. Polk"),(12,"Zachary Taylor","Zachary Taylor"),
    (13,"Millard Fillmore","Millard Fillmore"),(14,"Franklin Pierce","Franklin Pierce"),
    (15,"James Buchanan","James Buchanan"),(16,"Abraham Lincoln","Abraham Lincoln"),
    (17,"Andrew Johnson","Andrew Johnson"),(18,"Ulysses S. Grant","Ulysses S. Grant"),
    (19,"Rutherford B. Hayes","Rutherford B. Hayes"),(20,"James A. Garfield","James A. Garfield"),
    (21,"Chester A. Arthur","Chester A. Arthur"),(22,"Grover Cleveland","Grover Cleveland"),
    (23,"Benjamin Harrison","Benjamin Harrison"),(24,"Grover Cleveland","Grover Cleveland"),
    (25,"William McKinley","William McKinley"),(26,"Theodore Roosevelt","Theodore Roosevelt"),
    (27,"William Howard Taft","William Howard Taft"),(28,"Woodrow Wilson","Woodrow Wilson"),
    (29,"Warren G. Harding","Warren G. Harding"),(30,"Calvin Coolidge","Calvin Coolidge"),
    (31,"Herbert Hoover","Herbert Hoover"),(32,"Franklin D. Roosevelt","Franklin D. Roosevelt"),
    (33,"Harry S. Truman","Harry S. Truman"),(34,"Dwight D. Eisenhower","Dwight D. Eisenhower"),
    (35,"John F. Kennedy","John F. Kennedy"),(36,"Lyndon B. Johnson","Lyndon B. Johnson"),
    (37,"Richard Nixon","Richard Nixon"),(38,"Gerald Ford","Gerald Ford"),
    (39,"Jimmy Carter","Jimmy Carter"),(40,"Ronald Reagan","Ronald Reagan"),
    (41,"George H. W. Bush","George H. W. Bush"),(42,"Bill Clinton","Bill Clinton"),
    (43,"George W. Bush","George W. Bush"),(44,"Barack Obama","Barack Obama"),
    (45,"Donald Trump","Donald Trump"),(46,"Joe Biden","Joe Biden"),
    (47,"Donald Trump","Donald Trump"),
]

UA = "VocabQuestPresidents/1.0 (educational; https://github.com/calewis/vocab-quest)"

# Where a president's Wikipedia lead image isn't public domain, pin a specific
# known-PD Commons file (federal / National Archives / Library of Congress).
OVERRIDE = {
    "Franklin D. Roosevelt": "Franklin D. Roosevelt portrait - NARA - 196689.jpg",
}

def api(host, params):
    params = {**params, "format": "json"}
    url = f"https://{host}/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=25))

def lead_filename(title):
    d = api("en.wikipedia.org", {"action":"query","titles":title,"prop":"pageimages","piprop":"name"})
    page = next(iter(d["query"]["pages"].values()))
    return page.get("pageimage")

def commons_info(filename):
    d = api("commons.wikimedia.org", {"action":"query","titles":"File:"+filename,
            "prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":260})
    page = next(iter(d["query"]["pages"].values()))
    ii = page.get("imageinfo")
    if not ii:
        return None
    return ii[0]

def val(em, key):
    return (em.get(key, {}) or {}).get("value", "") or ""

def is_public_domain(em):
    lic  = val(em, "LicenseShortName").lower()
    lf   = val(em, "License").lower()
    use  = val(em, "UsageTerms").lower()
    return ("public domain" in lic) or lf.startswith("pd") or ("public domain" in use)

def strip_html(s):
    import re
    return re.sub(r"<[^>]+>", "", s).replace("&amp;", "&").strip()

def shrink(raw, width=150, quality=62):
    with tempfile.TemporaryDirectory() as d:
        src, dst = os.path.join(d,"in"), os.path.join(d,"out.jpg")
        open(src,"wb").write(raw)
        subprocess.run(["sips","-s","format","jpeg","-s","formatOptions",str(quality),
                        "--resampleWidth",str(width),src,"--out",dst], check=True, capture_output=True)
        return open(dst,"rb").read()

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read()

def main():
    cache, out, credits, problems = {}, [], {}, []
    for num, name, title in PRES:
        if title not in cache:
            entry = {"img":"", "source":"", "license":"", "file":""}
            try:
                fn = OVERRIDE.get(title) or lead_filename(title)
                if not fn:
                    raise RuntimeError("no lead image")
                info = commons_info(fn)
                if not info:
                    raise RuntimeError("not on Commons (local file?)")
                em = info.get("extmetadata", {})
                if not is_public_domain(em):
                    problems.append((num, name, fn, val(em,"LicenseShortName") or "unknown"))
                    print(f"  !! {num} {name}: NOT PD -> {val(em,'LicenseShortName')!r} ({fn})", file=sys.stderr)
                else:
                    raw = fetch(info["thumburl"])
                    entry["img"]     = "data:image/jpeg;base64," + base64.b64encode(shrink(raw)).decode()
                    entry["license"] = strip_html(val(em,"LicenseShortName")) or "Public domain"
                    entry["source"]  = strip_html(val(em,"Credit"))[:120] or strip_html(val(em,"Artist"))[:120]
                    entry["file"]    = fn
                    print(f"  {num:>2} {name:<24} {len(entry['img'])//1365}KB  [{entry['license']}]")
                time.sleep(0.25)
            except Exception as e:
                problems.append((num, name, "", str(e)))
                print(f"  !! {num} {name}: {e}", file=sys.stderr)
            cache[title] = entry
        e = cache[title]
        out.append([num, name, e["img"]])
        credits[str(num)] = {"name":name, "file":e["file"], "license":e["license"], "source":e["source"]}

    json.dump(out, open("build/presidents.json","w"))
    json.dump(credits, open("build/presidents_credits.json","w"), indent=1)
    ok = sum(1 for r in out if r[2])
    kb = sum(len(r[2]) for r in out)//1024
    print(f"\nwrote build/presidents.json  ({ok}/{len(out)} with PD portraits, ~{kb}KB base64)")
    if problems:
        print(f"\n{len(problems)} need attention:")
        for p in problems: print("  ", p)

if __name__ == "__main__":
    main()
