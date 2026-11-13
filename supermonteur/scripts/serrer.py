"""Resserre un clip déjà dérushé au ras de la voix (RUSH : « cut plus serré (tu fais souvent l'erreur) »).

Mesure sur RUSH : derush.py laissait 0,2 à 0,4 s de blanc à CHAQUE raccord (marge après le mot + départ calé avant la
voix), et ses filets remettent ces marges si on lui passe des plages plus courtes. Donc on resserre APRÈS lui, sur le clip :
  - chaque blanc >= BLANC s (son mesuré, 12 dB au-dessus du calme de la pièce) est réduit à 2 x GARDE s ;
  - jamais dans un mot (temps des mots) ;
  - un blanc posé sur un raccord existant ne crée aucune coupe en plus ; ailleurs, la nouvelle coupe doit laisser des plans
    >= 2 s (règle « plan >= 2 s ») et tomber après un mot qui finit par . , ! ? ; : (jamais en milieu de phrase).
Écrit clip.mp4 resserré, words.json + cut.segments.json recalés, serrer.log ; coupe la queue muette finale.

  python3 serrer.py <dossier du reel>      (lit clip.mp4, words.json, cut.segments.json)
"""
import json, os, subprocess, sys
import numpy as np

D = sys.argv[1]
GARDE, BLANC, MINSHOT, PONCT, PAUSE, RESPI = 0.05, 0.10, 2.0, ".,!?…;:", 0.40, 0.22   # RUSH (« cut plus serré entre les phrases, il ne faut pas de blanc », « mais il ne faut pas couper les mots ») : blanc dès 0,10 s
P = lambda f: os.path.join(D, f)
clip = P("clip.mp4")
wj = json.load(open(P("words.json"))); W = wj["words"]
segs = json.load(open(P("cut.segments.json")))

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     capture_output=True).stdout
x = np.frombuffer(raw, np.float32); n = len(x) // 160 * 160
db = 20 * np.log10(np.sqrt((x[:n].reshape(-1, 160) ** 2).mean(1)) + 1e-9)
# RUSH : silence = sous le bruit de la pièce + 25 % de l'écart bruit -> voix (avant : bruit + 12 dB, qui prenait les fins
# de mots douces pour du calme et obligeait à se caler sur les temps de mots, qui débordent : 0,15 s de blanc restait par phrase)
_bruit, _voix = np.percentile(db, 10), np.percentile(db, 70)
calme = db < _bruit + 0.25 * (_voix - _bruit)
total = n / 16000

joints, t = [], 0.0
for a, b in segs: t += b - a; joints.append(t)
joints = joints[:-1]

blancs, run = [], 0
for i, v in enumerate(np.append(calme, False)):
    if v: run += 1
    else:
        if run / 100 >= BLANC: blancs.append(((i - run) / 100, i / 100))
        run = 0

coupes = list(joints)                    # coupes visibles (pour la règle des 2 s)
retire = []
for s0, s1 in blancs:
    if s0 < 0.2 or s1 > total - 0.2: continue                 # début / fin : gérés par le dérush
    avant = [w for w in W if w["start"] < s0]
    apres = [w for w in W if w["end"] > s1]
    # sans reprise et en parlant de manière fluide, on garde les blancs et respirations entre phrases ; on coupe serré seulement
    # sur une grande pause ou une reprise.
    #  - raccord entre deux prises (joint du dérush) : au ras de la voix, queue 0,04 s, attaque 0,03 s, aucun blanc ;
    #  - dans une prise fluide : on ne touche qu'une vraie pause (>= PAUSE), ramenée à une respiration naturelle (RESPI).
    sur_joint = any(s0 - 0.1 <= j <= s1 + 0.1 for j in joints)
    if sur_joint:
        a, b = s0 + 0.04, s1 - 0.03
    else:
        if s1 - s0 < PAUSE: continue
        a, b = s0 + RESPI / 2, s1 - RESPI / 2
    # le seuil strict (bruit + 25 %) garde déjà les fins et attaques douces (f, s, ch) dans la voix ; les temps de mots ne
    # servent plus que de garde-fou grossier (un temps qui déborde de plus de 0,15 s dans le blanc = faux, ignoré)
    # aux raccords les temps de mots débordent de 0,1 s dans le blanc : seul le son décide, queue 0,05 s, attaque 0,04 s
    if sur_joint:
        a, b = s0 + 0.05, s1 - 0.04
    else:
        if avant and s0 < avant[-1]["end"] < s0 + 0.15: a = max(a, avant[-1]["end"] + 0.02)
        if apres and s1 - 0.15 < apres[0]["start"] < s1: b = min(b, apres[0]["start"] - 0.01)
    if b - a < 0.05: continue
    if not sur_joint:
        # (studio Super, « Pas le temps de filmer » : coupe posée à 2,09 s du raccord suivant, puis le blanc retiré (0,25 s)
        # raccourcit le plan à 1,84 s -> Gardien « Plans >= 2 s » bloque) : la longueur se mesure APRÈS retrait du blanc, début et fin
        # du clip compris, avec 0,15 s de marge pour les autres blancs retirés dans le même plan.
        if any((c < a and a - c < MINSHOT + 0.15) or (c >= a and c - b < MINSHOT + 0.15) for c in coupes + [0.0, total]): continue
        coupes.append(a)
    retire.append((round(a, 3), round(b, 3)))

# fin : la voix s'éteint, on garde 0,15 s (sinon le Gardien voit un « trou de son » dans la queue muette, RUSH v1)
on = np.where(~calme)[0]
fin = min(total, on[-1] / 100 + 0.15) if len(on) else total
if fin < total - 0.1: retire.append((round(fin, 3), round(total, 3)))
if not retire:
    print("serrer : rien à resserrer"); sys.exit(0)

garde, t = [], 0.0
for a, b in retire: garde.append((t, a)); t = b
garde.append((t, total))
f = "".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];"
            for i, (a, b) in enumerate(garde))
f += "".join(f"[v{i}][a{i}]" for i in range(len(garde))) + f"concat=n={len(garde)}:v=1:a=1[v][a]"
tmp = P("clip.serre.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", clip, "-filter_complex", f, "-map", "[v]", "-map", "[a]",
                "-c:v", "h264_videotoolbox", "-q:v", "75", "-g", "60", "-c:a", "aac", "-b:a", "192k", tmp], check=True)

def recale(t):
    d = 0.0
    for a, b in retire:
        if t >= b: d += b - a
        elif t > a: return a - d
    return t - d
for w in W: w["start"], w["end"] = round(recale(w["start"]), 3), round(recale(w["end"]), 3)
os.replace(tmp, clip)
# cut.segments.json (secondes du RUSH) suit le clip : le Gardien y lit les coupes (plans >= 2 s, micro-coupures)
def moins(segs, retire):
    res, t = [], 0.0
    for a, b in segs:
        c0, c1 = t, t + (b - a); t = c1; morceaux = [[a, b]]
        for r0, r1 in retire:
            if r1 <= c0 or r0 >= c1: continue
            x0, x1 = a + max(r0, c0) - c0, a + min(r1, c1) - c0
            nouv = []
            for m0, m1 in morceaux:
                if x1 <= m0 or x0 >= m1: nouv.append([m0, m1]); continue
                if x0 > m0: nouv.append([m0, x0])
                if x1 < m1: nouv.append([x1, m1])
            morceaux = nouv
        res += [[round(m0, 3), round(m1, 3)] for m0, m1 in morceaux if m1 - m0 > 0.01]
    return res
json.dump(moins(segs, retire), open(P("cut.segments.json"), "w"))
if os.path.exists(P("cut.mp4")): os.remove(P("cut.mp4"))      # le Gardien lit cut.mp4 en priorité : c'était l'ancienne coupe
json.dump(wj, open(P("words.json"), "w"), ensure_ascii=False)
gain = sum(b - a for a, b in retire)
with open(P("serrer.log"), "w") as fo: fo.write(json.dumps({"retire": retire, "gain": gain}))
print(f"serrer : {len(retire)} blancs resserrés, {gain:.2f} s retirés, {len(coupes) - len(joints)} coupe(s) en plus -> {total - gain:.2f} s")
