#!/usr/bin/env python3
"""Prépare Slide Notes pour un deck.
Usage : python3 prepare.py <dossier_des_png> <dossier_cible> [préfixe=a]
Copie les slides (a1.png, a2.png…) en JPG légers + slides.json + page + serveur dans <dossier_cible>.
Les notes déjà présentes (notes.json) sont gardées."""
import json, os, re, shutil, sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
pre = sys.argv[3] if len(sys.argv) > 3 else "a"
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(dst, "img"), exist_ok=True)
files = [f for f in os.listdir(src) if re.fullmatch(rf"{pre}\d+\.png", f)]
files.sort(key=lambda f: int(re.findall(r"\d+", f)[0]))
out = []
for f in files:
    sid = f[:-4]
    jpg = f"img/{sid}.jpg"
    Image.open(os.path.join(src, f)).convert("RGB").resize((1280, 720)).save(os.path.join(dst, jpg), quality=82)
    out.append({"id": sid, "img": jpg + f"?v={int(os.path.getmtime(os.path.join(src, f)))}"})
json.dump(out, open(os.path.join(dst, "slides.json"), "w"), indent=1)
for n in ("index.html", "server.py"):
    shutil.copy(os.path.join(here, n), os.path.join(dst, n))
print(len(out), "slides prêtes dans", dst)
