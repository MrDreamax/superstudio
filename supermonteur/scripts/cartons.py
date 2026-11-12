#!/usr/bin/env python3
"""Cartons d'arbitre au-dessus de la tête (RUSH, maquette C notée 9/10 par le juge). Variante du style Comparatif.

Une rangée de cases (une par élément) entre la zone morte du haut (270 px) et la tête. Cases vides en pointillé
(toutes blanches : la verte en vert « spoile la suite »). À chaque élément : son titre en gros (Outfit 800,
blanc, une ligne) à `at` ; le carton tombe dans sa case avec un ressort à `carte` (le mot « carton »). Le vert arrive
plus gros. Tout s'efface à `fin` (début du CTA).

plan.json :
  "cartons": {"top": 300, "fin": 52.1, "items": [
      {"couleur": "rouge", "titre": "MONTER TOI-MÊME", "at": 0.2, "carte": 3.1}, ...
      {"couleur": "vert", "titre": "TES PROPRES MOTS", "at": 40.0, "carte": 42.3}]}
Lancé par monte.sh juste après build.mjs (comme viral.py inject) : python3 cartons.py plan.json
"""
import json, sys

MARK = 'id="cartons"'
W, H, GAP = 150, 210, 28
ROUGE = "linear-gradient(150deg,#ef3b50 0%,#d7263d 45%,#9c1528 100%)"
VERT = "linear-gradient(150deg,#3fe07a 0%,#13b24c 45%,#0a7a32 100%)"


def fit(titre, size=84, maxw=950):
    """Une ligne, jamais coupée : taille réduite si le titre est long (Outfit 800 ≈ 0,62 em par lettre en majuscules)."""
    est = len(titre) * size * 0.62
    return int(size * min(1, maxw / est)) if est else size


def inject(plan_path):
    plan = json.load(open(plan_path))
    c = plan["cartons"]
    items, top = c["items"], c.get("top", 315)
    n = len(items)
    x0 = (1080 - (n * W + (n - 1) * GAP)) // 2
    if x0 < 65:
        sys.exit(f"{n} cartons ne tiennent pas dans la largeur sûre (marge {x0} px < 65)")
    html = open("index.html", encoding="utf8").read()
    if MARK in html:
        sys.exit("les cartons sont déjà dans index.html : relancer build.mjs d'abord")
    css = f"""
  #cartons{{position:absolute;inset:0;pointer-events:none;opacity:0}}
  #cartons .voile{{position:absolute;left:0;right:0;top:0;height:{top + H + 260}px;background:linear-gradient(#000c 0%,#0009 55%,#0000 100%)}}
  #cartons .cs{{position:absolute;top:{top}px;width:{W}px;height:{H}px;border-radius:12px;border:3px dashed #ffffff8c;background:#0006}}
  #cartons .cd{{position:absolute;top:{top}px;width:{W}px;height:{H}px;border-radius:16px;opacity:0;
     box-shadow:0 18px 40px #000a, inset 0 0 0 3px #fff3}}
  #cartons .cd::after{{content:"";position:absolute;inset:0;border-radius:16px;background:linear-gradient(120deg,#fff5 0%,#fff0 40%)}}
  #cartons .tt{{position:absolute;left:0;right:0;top:{top + H + 28}px;text-align:center;color:#fff;font-family:"Mont";
     font-weight:800;text-transform:uppercase;white-space:nowrap;text-shadow:0 4px 16px #000b;opacity:0}}
"""
    body = ['<div id="cartons"><div class="voile"></div>']
    js = []
    for i, it in enumerate(items):
        x = x0 + i * (W + GAP)
        vert = it["couleur"] == "vert"
        rot = -4 if (i % 2 or vert) else 4
        body.append(f'<div class="cs" style="left:{x}px"></div>')   #  l’utilisateur : case verte en pointillé vert = « ça spoile la suite » -> toutes blanches
        glow = ",0 0 18px #2fb87259" if vert else ""
        body.append(f'<div class="cd" id="cd{i}" style="left:{x}px;background:{VERT if vert else ROUGE};'
                    f'box-shadow:0 18px 40px #000a, inset 0 0 0 3px #fff3{glow}"></div>')
        body.append(f'<div class="tt" id="tt{i}" style="font-size:{fit(it["titre"])}px">{it["titre"]}</div>')
        # titre : entre à `at`, sort quand le suivant entre (ou à la fin)
        js.append(f'tl.fromTo("#tt{i}",{{opacity:0,y:14,filter:"blur(6px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:.3,ease:"power3.out",immediateRender:false}},{it["at"]:.2f});')
        if i + 1 < n:
            js.append(f'tl.to("#tt{i}",{{opacity:0,y:-10,filter:"blur(6px)",duration:.18,ease:"power2.in"}},{items[i + 1]["at"] - 0.18:.2f});')
        # carton : tombe d'en haut (20 px seulement : à -90 il passait dans la zone morte du haut), ressort, se pose légèrement penché
        sc = 1.06 if vert else 1
        js.append(f'tl.fromTo("#cd{i}",{{opacity:0,y:-20,rotation:{rot * -2},scale:{sc * 1.1:.2f}}},'
                  f'{{opacity:1,y:0,rotation:{rot},scale:{sc},duration:.42,ease:"back.out(2.2)",immediateRender:false}},{it["carte"]:.2f});')
        if vert:
            js.append(f'tl.fromTo("#cd{i}",{{filter:"brightness(1.8)"}},{{filter:"brightness(1)",duration:.5,ease:"power2.out",immediateRender:false}},{it["carte"] + 0.3:.2f});')
    body.append("</div>")
    t0, fin = max(items[0]["at"] - 0.25, 0), c.get("fin")
    js.insert(0, f'tl.fromTo("#cartons",{{opacity:0}},{{opacity:1,duration:.35,ease:"power2.out",immediateRender:false}},{t0:.2f});')
    if fin:
        js.append(f'tl.to("#cartons",{{opacity:0,duration:.4,ease:"power2.in"}},{fin - 0.4:.2f});')
    html = html.replace("</style>", css + "</style>", 1)
    i = html.rindex("  </div>\n  <script>")
    html = html[:i] + "    " + "".join(body) + "\n" + html[i:]
    anchor = "    tl.to({},{duration:DUR},0);"
    if anchor not in html:
        sys.exit("ancre de la timeline introuvable dans index.html (build.mjs a changé ?)")
    html = html.replace(anchor, "    " + "\n    ".join(js) + "\n" + anchor, 1)
    open("index.html", "w", encoding="utf8").write(html)
    print(f"cartons posés : {n} cases, marge {x0} px, haut {top} px")


if __name__ == "__main__":
    inject(sys.argv[1])
