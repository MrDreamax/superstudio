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
# RUSH (flash de 0,04 s au raccord) : la somme des plages en secondes ≠ la vraie coupe dans clip.mp4 (le dérush coupe
# à l'image, 30 i/s ; l'écart grandit jusqu'à 0,2 s en fin de clip). On MESURE chaque raccord : le plus gros saut d'image à ±0,3 s.
_img = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-vf", "scale=64:114,format=gray", "-f", "rawvideo", "-"],
                      capture_output=True).stdout
_fps = 30.0
try:
    _r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", clip],
                        capture_output=True, text=True).stdout.strip().split("/")
    _fps = float(_r[0]) / float(_r[1] if len(_r) > 1 else 1)
except Exception: pass
_fr = np.frombuffer(_img, np.uint8)
if len(_fr) >= 2 * 64 * 114:
    _fr = _fr[: len(_fr) // (64 * 114) * 64 * 114].reshape(-1, 64 * 114).astype(np.float32)
    _saut = np.abs(np.diff(_fr, axis=0)).mean(1)          # _saut[i] = changement entre l'image i et i+1 -> coupe à (i+1)/fps
    def _vrai(j):
        i0, i1 = max(0, int((j - 0.3) * _fps)), min(len(_saut), int((j + 0.3) * _fps) + 1)
        return round((i0 + int(np.argmax(_saut[i0:i1])) + 1) / _fps, 3) if i1 > i0 else j
    joints = [_vrai(j) for j in joints]

blancs, run = [], 0
for i, v in enumerate(np.append(calme, False)):
    if v: run += 1
    else:
        if run / 100 >= BLANC: blancs.append(((i - run) / 100, i / 100))
        run = 0

coupes = list(joints)                    # coupes visibles (pour la règle des 2 s)
retire = []
_fin = lambda w: w["text"].rstrip(" »\"'").endswith((".", "?", "!", "…", ":", ","))
# RUSH (Gardien « respiration en début de phrase » 0,23 s sur un raccord) : au début de chaque plage, le souffle
# avant la 1re note de voix (même détection que gardien.py 2 ter) est retiré, attaque gardée 0,03 s.
_xx = x.astype(np.float64); _p95 = np.percentile(db, 95)
def _trame(k):
    f = _xx[k * 160: k * 160 + 480]
    if len(f) < 480: return -120, 0
    f = f - f.mean(); e = 10 * np.log10((f * f).mean() + 1e-12)
    r = max((f[:-l] * f[l:]).sum() / np.sqrt((f[:-l] ** 2).sum() * (f[l:] ** 2).sum() + 1e-12) for l in range(40, 200, 4))
    return e, r
souffle = []
for j in joints:
    n, voix = 0, None
    for k in range(int(j * 100), int(min(j + 1.0, total) * 100)):
        e, r = _trame(k)
        if e > _p95 - 11 and r > 0.55: voix = k / 100; break
        if e > _p95 - 30 and r < 0.45: n += 1
    # j = raccord MESURÉ dans l'image : on part pile dessus (rien de la prise d'avant mangé, aucune image de la suivante laissée)
    # départ 0,4 image AVANT : j arrondi au millième (38,667) > vraie image (38,6667) gardait la 1re image de la prise suivante = flash
    if voix and n >= 12 and voix - 0.03 - j > 0.05: souffle.append((round(j - 0.4 / _fps, 3), round(voix - 0.03, 3)))
for s0, s1 in blancs:
    if s0 < 0.2 or s1 > total - 0.2: continue                 # début / fin : gérés par le dérush
    avant = [w for w in W if w["start"] < s0]
    apres = [w for w in W if w["end"] > s1]
    # RUSH : « s'il n'y a pas de reprise et que je parle de manière fluide, tu peux laisser certains blancs ou
    # respirations entre les phrases, on cut serré que quand il y a une grande pause et que je cherche mes pensées, ou quand je me reprends ».
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
    # aux raccords les temps de mots débordent de 0,1 s dans le blanc (RUSH) : seul le son décide, queue 0,05 s, attaque 0,04 s
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
        # RUSH (3 blancs de 0,5-0,7 s gardés -> Gardien « Silences entendus » bloquait le moteur) : un plan
        # court passe s'il contient une phrase ENTIÈRE (même règle que gardien.py, « pas une règle absolue »).
        def _court_ok(t0, t1):
            dans = [k for k, w in enumerate(W) if t0 - 0.1 <= w["start"] < t1 - 0.05]
            return bool(dans) and (dans[0] == 0 or _fin(W[dans[0] - 1])) and _fin(W[dans[-1]])
        bords = sorted(coupes + [0.0, total])
        av = max([c for c in bords if c < a], default=0.0); ap = min([c for c in bords if c >= b], default=total)
        if (a - av < MINSHOT + 0.15 and not _court_ok(av, a)) or (ap - b < MINSHOT + 0.15 and not _court_ok(b, ap)): continue
        coupes.append(a)
    retire.append((round(a, 3), round(b, 3)))

for s0, s1 in souffle:        # fusionné avec un blanc déjà retiré au même raccord
    hit = [r for r in retire if r[0] - 0.05 <= s1 and s0 <= r[1] + 0.05]
    for r in hit: retire.remove(r)
    retire.append((min([s0] + [r[0] for r in hit]), max([s1] + [r[1] for r in hit])))
retire.sort()
# fin : la voix s'éteint, on garde 0,15 s (sinon le Gardien voit un « trou de son » dans la queue muette, RUSH)
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
        # un bout < 0,08 s = écart d'arrondi à l'image entre le raccord compté et le raccord mesuré, pas un vrai plan
        res += [[round(m0, 3), round(m1, 3)] for m0, m1 in morceaux if m1 - m0 > 0.08]
    return res
json.dump(moins(segs, retire), open(P("cut.segments.json"), "w"))
if os.path.exists(P("cut.mp4")): os.remove(P("cut.mp4"))      # le Gardien lit cut.mp4 en priorité : c'était l'ancienne coupe
json.dump(wj, open(P("words.json"), "w"), ensure_ascii=False)
gain = sum(b - a for a, b in retire)
with open(P("serrer.log"), "w") as fo: fo.write(json.dumps({"retire": retire, "gain": gain}))
print(f"serrer : {len(retire)} blancs resserrés, {gain:.2f} s retirés, {len(coupes) - len(joints)} coupe(s) en plus -> {total - gain:.2f} s")
