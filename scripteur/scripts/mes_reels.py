#!/usr/bin/env python3
"""Sort le texte vraiment dit dans les derniers reels montés. Usage : mes_reels.py [nombre, défaut 5]"""
import glob, json, os, re, sys

BASE = os.path.expanduser("~/Documents/SuperApps/supermonteur/reels")
nombre = int(sys.argv[1]) if len(sys.argv) > 1 else 5
vus, sortis = set(), 0
for d in sorted(glob.glob(BASE + "/*"), key=os.path.getmtime, reverse=True):
    if "test" in os.path.basename(d):
        continue
    for n in ("cut.words.json", "words.json"):
        p = os.path.join(d, n)
        if not os.path.exists(p):
            continue
        w = json.load(open(p, encoding="utf8"))
        if isinstance(w, dict):
            w = w.get("words") or w.get("segments") or []
        t = " ".join((x.get("word") or x.get("text") or "").strip() for x in w if isinstance(x, dict))
        t = re.sub(r"\s+'\s*", "'", t)
        if 100 < len(t.split()) < 320 and t[:60] not in vus:
            vus.add(t[:60])
            print(f"## {os.path.basename(d)}\n{t}\n")
            sortis += 1
        break
    if sortis >= nombre:
        break
