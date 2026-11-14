#!/usr/bin/env python3
"""Verrou du Monteur (14/11/2026, audit vitesse : 2 montages en même temps sur un Mac de 8 Go = rendus 2 à 4 fois plus lents,
Mac endormi pendant un rendu = 2 h 49 d'attente pour 5 min de travail).
  python3 verrou.py -- <commande de rendu...>      (express.py et monte.sh s'y relancent tout seuls)
- UN seul rendu à la fois : un 2e attend son tour (15 min max, puis part quand même en le disant).
  Le verrou tient au processus : un rendu qui plante le libère tout seul, il ne reste jamais coincé.
- Mac gardé éveillé pendant le rendu (caffeinate -i).
- Outils vérifiés en 1 s avant de rendre (ffmpeg, ffprobe, node, place sur le disque).
- Durée réelle notée (~/.cache/supermonteur/durees.jsonl) et durée habituelle annoncée au départ.
Tout couper : SUPERMONTEUR_VERROU=0 (la commande part directement, comme avant).
"""
import fcntl, json, os, shutil, statistics, subprocess, sys, time

cmd = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not cmd: sys.exit("usage : verrou.py -- <commande>")
env = dict(os.environ, SUPERMONTEUR_VERROU_TENU="1")
if os.environ.get("SUPERMONTEUR_VERROU") == "0":
    sys.exit(subprocess.call(cmd, env=env))

C = os.path.expanduser("~/.cache/supermonteur"); os.makedirs(C, exist_ok=True)
nom = os.path.basename(cmd[1] if len(cmd) > 1 else cmd[0])
dossier = os.path.basename(os.path.abspath(cmd[2] if len(cmd) > 2 else "."))

# 1. outils (1 s)
manque = [o for o in ("ffmpeg", "ffprobe", "node") if not shutil.which(o)]
if manque: sys.exit(f"⛔ outil introuvable : {', '.join(manque)} (lancer setup.sh)")
libre = shutil.disk_usage(os.getcwd()).free / 1e9
if libre < 2: sys.exit(f"⛔ disque presque plein ({libre:.1f} Go libres) : faire de la place avant de rendre")

# 2. un seul rendu à la fois
f = open(os.path.join(C, "rendu.lock"), "a+")
t0 = time.time(); dit = False
while True:
    try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB); break
    except BlockingIOError:
        if not dit:
            f.seek(0); qui = f.read().strip() or "?"
            print(f"⏳ un autre montage tourne ({qui}) : j'attends mon tour (Mac 8 Go, 2 rendus ensemble = 2 fois plus lents)", flush=True); dit = True
        if time.time() - t0 > 900:
            print("⚠️ attente > 15 min : je pars quand même", flush=True); break
        time.sleep(2)
f.seek(0); f.truncate(); f.write(f"{dossier} · {nom} · depuis {time.strftime('%H:%M:%S')}"); f.flush()

# 3. durée habituelle
J = os.path.join(C, "durees.jsonl")
passe = []
try:
    for l in open(J):
        d = json.loads(l)
        if d.get("outil") == nom and d.get("ok"): passe.append(d["s"])
except (OSError, ValueError): pass
if passe[-10:]: print(f"⏱ durée habituelle de {nom} : ~{statistics.median(passe[-10:]):.0f} s (mesurée sur {len(passe[-10:])} rendus)", flush=True)

# 4. rendu, Mac éveillé
t1 = time.time()
r = subprocess.call((["caffeinate", "-i"] if shutil.which("caffeinate") else []) + cmd, env=env)
s = time.time() - t1
_saute = os.path.join(C, "saute")
if os.path.exists(_saute):   # rendu évité (rien n'avait changé) : pas une vraie durée de rendu
    os.remove(_saute); print(f"⏱ aucun rendu ({s:.0f} s)", flush=True); sys.exit(r)
try:
    with open(J, "a") as o: o.write(json.dumps({"outil": nom, "reel": dossier, "s": round(s, 1), "ok": r == 0, "quand": time.strftime("%Y-%m-%d %H:%M")}) + "\n")
except OSError: pass
print(f"⏱ {nom} : {s:.0f} s réelles" + (f" (attente du tour : {t1 - t0:.0f} s)" if t1 - t0 > 3 else ""), flush=True)
sys.exit(r)
