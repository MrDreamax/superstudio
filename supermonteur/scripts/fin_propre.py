"""Fin propre du plan : aucun bout minuscule de face cam en fin de vidéo, aucun plein écran après la fin.

  python3 fin_propre.py plan.json        (lancé par monte.sh AVANT les B-rolls, donc avant le Gardien)

Pourquoi : (studio Super, « Pas le temps de filmer » v4), un B-roll prolongé « jusqu'à la toute fin » finissait à
17,79 s sur une vidéo de 17,3 s, et le Gardien a bloqué la version : « Plans >= 2 s : [(17.68, 0.11)] ». Aucun humain ni
Claude ne doit calculer la fin au centième près : c'est le moteur qui la cale.

Règles (même durée que build.mjs : min(plan.duration, durée de la face cam - 0,04 s)) :
 0. cut.segments.json dont la dernière plage finit après la fin réelle du rush (ancien dérush) : ramenée à cette fin.
 1. Un plein écran (B-roll, carton, liste, preuve) ou une capture incrustée qui commence dans les 0,3 dernières secondes = retiré.
 2. Un plein écran qui finit après la fin de la vidéo = coupé à la fin.
 3. Si le dernier plein écran laisse moins de 2 s de face cam en fin de vidéo, il est prolongé jusqu'à la fin (fusion dans
    le plan voisin). Sauf si ce bout contient une phrase entière (la règle du Gardien l'accepte, ).
Le Gardien n'est pas touché : il contrôle toujours tout, le plan lui arrive juste propre.
"""
import json, os, subprocess, sys

p = sys.argv[1]
D = os.path.dirname(os.path.abspath(p))
plan = json.load(open(p))
cam = plan.get("cam", "clip.mp4")
cam = cam if os.path.isabs(cam) else os.path.join(D, cam)
if not os.path.exists(cam) or plan.get("famille") == "broll-texte":
    sys.exit(0)
cam_dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cam],
                               capture_output=True, text=True).stdout.strip() or 0)
if not cam_dur:
    sys.exit(0)
dur = round(min(plan.get("duration") or cam_dur, cam_dur - 0.04), 3)

# 0 : cut.segments.json (ce que le Gardien lit pour les coupes) dont la dernière plage finit APRÈS la fin réelle du rush :
# ancien derush.py qui ajoutait sa traîne sans regarder la fin du rush. La vidéo (clip) est juste, seul le
# fichier ment : on ramène cette fin à la fin réelle du rush (image ET son). Rien d'autre n'est touché ; un autre écart reste
# au Gardien (« Coupes à jour »), qui bloque.
sp, vp = os.path.join(D, "cut.segments.json"), os.path.join(D, "cut.voice.json")
def _fin_flux(f, k):
    try: return float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", f"{k}:0", "-show_entries", "stream=duration",
                                      "-of", "csv=p=0", f], capture_output=True, text=True).stdout.split()[0])
    except Exception: return None
if os.path.exists(sp) and os.path.exists(vp):
    segs = json.load(open(sp)); rush = (json.load(open(vp)) or {}).get("src")
    if segs and rush and os.path.exists(rush) and sum(b - a for a, b in segs) - cam_dur > 0.02:
        fins = [x for x in (_fin_flux(rush, "v"), _fin_flux(rush, "a")) if x]
        if fins:
            fin_rush = int(min(fins) * 30 + 1e-6) / 30
            if segs[-1][1] > fin_rush + 0.005 and fin_rush - segs[-1][0] > 0.1:
                print(f"fin propre : cut.segments.json, dernière plage {segs[-1][1]} -> {fin_rush:.3f} s (fin réelle du rush)")
                segs[-1][1] = round(fin_rush, 3)
                json.dump(segs, open(sp, "w"))

CLES = ("brolls", "lists", "proofs", "inserts")
elems = [(k, x) for k in CLES for x in (plan.get(k) or [])]   # inserts : seulement ramenés dans la vidéo (règles 1-2), jamais allongés
elems += [("mini", m) for m in (plan.get("mini") or []) if m.get("type") == "card"]
log, change = [], False

# 1 + 2 : rien après la fin
for k, x in elems:
    if "start" not in x or "end" not in x:
        continue
    if x["start"] >= dur - 0.3:
        x["_retire"] = True
        log.append(f"{k} {x['start']}-{x['end']} retiré : commence après la fin de la vidéo ({dur} s)")
    elif x["end"] > dur:
        log.append(f"{k} {x['start']}-{x['end']} : fin ramenée à {dur} s (fin réelle de la vidéo)")
        x["end"] = dur
        change = True
for k in CLES + ("mini",):
    if plan.get(k) and any(x.get("_retire") for x in plan[k]):
        plan[k] = [x for x in plan[k] if not x.get("_retire")]
        change = True
elems = [(k, x) for k, x in elems if not x.get("_retire") and "start" in x and "end" in x and k != "inserts"]   # 3 : pleins écrans seuls

# 3 : bout de face cam < 2 s en fin
if elems:
    u1 = max(x["end"] for k, x in elems)
    reste = round(dur - u1, 3)
    W = []
    wp = plan.get("words", "words.json")
    wp = wp if os.path.isabs(wp) else os.path.join(D, wp)
    try:
        W = json.load(open(wp)).get("words") or []
    except Exception:
        pass
    fin = lambda w: w["text"].rstrip(" »\"'").endswith((".", "?", "!", "…", ":", ","))
    dans = [i for i, w in enumerate(W) if u1 - 0.1 <= w["start"] < dur - 0.05]
    phrase = bool(dans) and (dans[0] == 0 or fin(W[dans[0] - 1])) and fin(W[dans[-1]])
    if 0.02 < reste < 2.0 and not phrase:
        for k, x in elems:
            if abs(x["end"] - u1) < 0.011:
                log.append(f"{k} {x['start']}-{x['end']} prolongé jusqu'à la fin ({dur} s) : il restait {reste} s de face cam (plan < 2 s)")
                x["end"] = dur
                change = True

if change:
    json.dump(plan, open(p, "w"), ensure_ascii=False, indent=1)
for l in log:
    print("fin propre :", l)
