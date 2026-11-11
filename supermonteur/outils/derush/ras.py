"""Coupes au ras de la voix (06/11/2026, RUSH : « cut plus serré, grave dans le brain corrige »).

Mesure RUSH : derush.py (même en mode serré) laisse 0,08 à 0,22 s de blanc à CHAQUE coupe (moyenne 0,15 s) :
fin_du_mot +0,04 s, filet +0,03 s au-delà du fondu de 0,03 s, attaque -0,04 à -0,10 s, puis arrondi à l'image vers
l'extérieur. Et derush.py --plages remet ces marges par-dessus des plages plus courtes (testé : 92,7 s demandées -> 95,6 s).
Donc ce script ne passe pas par derush.py : il relit ses plages (cut.segments.json, secondes du rush), rapproche chaque
bord intérieur de la voix et fait LE rendu lui-même, depuis le rush (un seul encodage, image intouchable).
  - fin d'une plage  = fin réelle du mot (queue_mot.fin_du_mot, la définition du Gardien, qui inclut déjà 0,04 s de queue) ;
  - début d'une plage = 1re trame de voix (voisée au-dessus du calme + 12 dB, ou voix forte) - 0,012 s ;
  - bords calés sur l'image la plus proche, sans jamais passer dans le mot (fin - fondu >= f - 0,028 : le Gardien bloque sous f - 0,03 ; début <= attaque - 0,005) ;
  - fondu anti-clic de 12 ms en sortie et 8 ms en entrée (au lieu de 30 ms) ;
  - jamais de plage rallongée, sauf 0,15 s max pour reprendre une attaque où derush.py a posé son début ; tout début et toute fin du clip inchangés (marges d'entrée / sortie de derush.py).
Le calme (pour la fin du mot) = tout le rush, comme le Gardien : mesuré sur les plages gardées, il rognait la queue des mots.

  python3 ras.py <rush> <dossier>        (lit <dossier>/cut.segments.json + words.json du RUSH ;
                                          écrit <dossier>/ras.mp4, ras.segments.json, ras.words.json = mots en temps du clip)
"""
import json, math, os, subprocess, sys
import numpy as np

src, D = sys.argv[1], sys.argv[2]
P = lambda f: os.path.join(D, f)
FIN, DEBUT, FADE_OUT, FADE_IN = 0.0, 0.012, 0.012, 0.008   # 07/11 : FIN 0,02 -> 18 mots coupés au Gardien (il veut fin - fondu >= f - 0,03)
sys.path.insert(0, os.path.expanduser("~/.claude/skills/supermonteur/scripts"))
from queue_mot import fin_du_mot          # même définition que derush.py et gardien.py (lue, jamais modifiée ici)

segs = [list(s) for s in json.load(open(P("cut.segments.json")))]
W = json.load(open(P("words.json")))["words"]
fps_s = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                                 "-of", "csv=p=0", src]).decode().strip()
num, den = map(int, fps_s.split("/")); FPS = num / den
rng = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_range",
                               "-of", "csv=p=0", src]).decode().strip() or "tv"

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, np.float32); n = len(x) // 160 * 160
db = 20 * np.log10(np.sqrt((x[:n].reshape(-1, 160) ** 2).mean(1)) + 1e-9)
db = np.convolve(db, np.ones(3) / 3, "same")                       # lissé 30 ms, comme derush.py / gardien.py
q = float(np.percentile(db, 95)) - 21                              # seuil de parole
fl = float(np.percentile(db, 3))   # calme de la pièce sur TOUT le rush, comme derush.py et le Gardien (sur les seules plages gardées il monte de ~8 dB et la queue des mots serait rognée, testé 07/11)

def voisee(k):
    f = x[k * 160: k * 160 + 480].astype(np.float64); f = f - f.mean()
    if len(f) < 480 or (f * f).sum() <= 0: return False
    return max((f[:-l] * f[l:]).sum() / np.sqrt((f[:-l] ** 2).sum() * (f[l:] ** 2).sum() + 1e-12) for l in range(40, 200, 2)) > 0.55

def fin(a, b):          # -> (nouvelle fin, fin du mot f)
    k = min(int(b * 100), len(db) - 1); j = k
    while j > max(int(a * 100), k - 80) and db[j] < q + 6: j -= 1    # dernière trame de voix forte
    if db[j] < q + 6: return b, b
    f = min(b, fin_du_mot(db, voisee, q, fl, j / 100, b + 0.02))
    return min(b, f - FIN), f

def debut(a, b):        # -> (nouveau début, attaque)
    # 07/11 (Gardien, « t » de « Tu es coach ? » mangé) : derush.py pose parfois son début DANS l'attaque ; on cherche l'attaque
    # à partir de 0,05 s avant sa plage et on part DEBUT avant elle (la voix continue, au plus 0,15 s plus tôt que derush.py).
    # Puis on remonte la voix CONTINUE (au-dessus du calme + 12 dB) jusqu'à 0,15 s avant la plage (« Et » doux de 308,3 s).
    for k in range(int((a - 0.05) * 100), min(len(db), int(b * 100))):
        if db[k] >= q or (db[k] >= fl + 12 and voisee(k)):
            sourd = 0   # un souffle (sans note) n'est pas remonté ; 3 trames sourdes max = l'explosion d'un « t », « p », « k »
            while k - 1 >= int((a - 0.15) * 100) and db[k - 1] >= fl + 12:
                if not voisee(k - 1):
                    sourd += 1
                    if sourd > 3: break
                k -= 1
            return k / 100 - DEBUT, k / 100
    return a, a

grid = lambda t: round(t * FPS) / FPS
res = []
for i, (a, b) in enumerate(segs):
    na, att = debut(a, b) if i > 0 else (a, a)
    nb, f = fin(na, b) if i < len(segs) - 1 else (b, b)
    ga, gb = grid(na), grid(nb)
    if i > 0 and ga > att - 0.005: ga = math.floor(na * FPS) / FPS        # jamais dans l'attaque
    if i < len(segs) - 1 and gb - FADE_OUT < f - 0.028: gb = math.ceil(nb * FPS) / FPS   # jamais dans la queue du mot
    ga, gb = max(ga, math.floor(min(a, na) * FPS) / FPS), min(gb, math.ceil(b * FPS) / FPS)   # jamais rallongée (sauf pour reprendre une attaque)
    if gb - ga < 0.3: ga, gb = math.floor(a * FPS) / FPS, math.ceil(b * FPS) / FPS   # sécurité : jamais une plage vidée
    res.append([round(ga, 4), round(gb, 4)])

# rendu : une entrée par plage (saut 1 s avant, découpe exacte dans le filtre), un seul encodage, puce vidéo du Mac
inputs, f, chain = [], "", ""
for i, (a, b) in enumerate(res):
    pre = math.floor(min(1.0, a) * FPS) / FPS   # 07/11 : saut calé sur la grille des images, sinon chaque morceau prend une fraction d'image de trop (+0,17 s sur 23 morceaux, son décalé)
    inputs += ["-ss", f"{a - pre:.4f}", "-t", f"{b - a + pre + 0.2:.4f}", "-i", src]
    sf, nf = round(pre * FPS), round((b - a) * FPS); d = nf / FPS   # 07/11 : découpe à l'IMAGE près (trim par durée gardait parfois 1 image de trop -> silence ajouté par concat)
    f += (f"[{i}:v]trim=start_frame={sf}:end_frame={sf + nf},setpts=PTS-STARTPTS[v{i}];"
          f"[{i}:a]atrim=start={pre:.4f}:duration={d:.4f},asetpts=PTS-STARTPTS,"
          f"afade=t=in:d={FADE_IN if i else 0.03},afade=t=out:st={d - (FADE_OUT if i < len(res) - 1 else 0.03):.4f}:d={FADE_OUT if i < len(res) - 1 else 0.03}[a{i}];")
    chain += f"[v{i}][a{i}]"
f += chain + f"concat=n={len(res)}:v=1:a=1[vc][a];[vc]scale=out_range={rng},format=nv12[v]"   # comme derush.py : plage de couleurs gardée, nv12 pour la puce
subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", f, "-map", "[v]", "-map", "[a]",
                "-c:v", "h264_videotoolbox", "-q:v", "75", "-g", "60", "-color_range", rng,
                "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                "-c:a", "aac", "-b:a", "192k", P("ras.mp4")], check=True)

# mots en temps du clip (pour ecrans_hooks.py et la vérification)
out_w, t0 = [], 0.0
for a, b in res:
    for w in W:
        m = (w["start"] + w["end"]) / 2
        if a <= m < b: out_w.append({"text": w["text"], "start": round(max(a, w["start"]) - a + t0, 3), "end": round(min(b, w["end"]) - a + t0, 3)})
    t0 += b - a
json.dump({"words": out_w}, open(P("ras.words.json"), "w"), ensure_ascii=False)
json.dump(res, open(P("ras.segments.json"), "w"))
avant = sum(b - a for a, b in segs)
print(f"ras : {len(res)} plages, {avant:.2f} s -> {t0:.2f} s ({avant - t0:.2f} s de blanc retirés) -> {P('ras.mp4')}")
