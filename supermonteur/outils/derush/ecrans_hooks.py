"""Écrans noirs HOOK 1 / HOOK 2 / HOOK 3 / BODY entre les parties d'un dérush de pub (06/11/2026, RUSH).

l’utilisateur : « pour chaque montage y'a 2 ou 3 hooks, est-ce que tu peux les conserver dans un même rush et les séparer par un
écran noir avec écrit : hook 1, hook 2, hook 3, body ».
Une seule vidéo par script : [HOOK 1] hook 1 [HOOK 2] hook 2 ([HOOK 3] hook 3) [BODY] corps.
Écran = fond noir, texte blanc centré en MAJUSCULES, police Outfit SemiBold, 1 s, silence. Image du rush intouchable
(aucun étalonnage), mêmes taille / cadence / plage de couleurs que le clip.

  python3 ecrans_hooks.py <clip dérushé.mp4> <words.json du clip> <sortie.mp4> --parts "début hook 1|début hook 2|...|début body"
  python3 ecrans_hooks.py <clip> <words.json> <sortie.mp4> --temps 0,8.0,14.4,21.3

--parts : les premiers mots de chaque partie (dans l'ordre, la DERNIÈRE = le body), cherchés dans words.json (sans accents,
majuscules ni ponctuation). --temps : secondes du clip où commence chaque partie. Chaque coupe tombe au creux du son
entre le dernier mot d'une partie et le premier de la suivante (jamais dans un mot). --duree 1 = durée d'un écran.
Écrit aussi <sortie>.reperes.json (où commence chaque écran et chaque partie).
"""
import json, os, re, subprocess, sys, unicodedata
import numpy as np
from PIL import Image, ImageDraw, ImageFont

clip, words_p, out = sys.argv[1:4]
arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
DUREE = float(arg("--duree", 1.0))
FONT = os.path.expanduser("~/.claude/skills/supermonteur/fonts/Outfit.ttf")
W = json.load(open(words_p))["words"]

def probe(entries, stream=None):
    sel = ["-select_streams", stream] if stream else []
    r = subprocess.run(["ffprobe", "-v", "error", *sel, "-show_entries", entries, "-of", "json", clip],
                       capture_output=True, text=True).stdout
    return json.loads(r)
v = probe("stream=width,height,r_frame_rate,color_range", "v:0")["streams"][0]
WID, HEI, FPS_S, RNG = v["width"], v["height"], v["r_frame_rate"], v.get("color_range", "tv")
num, den = map(int, FPS_S.split("/")); FPS = num / den
SR = int(probe("stream=sample_rate", "a:0")["streams"][0]["sample_rate"])
TOTAL = float(probe("format=duration")["format"]["duration"])

norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()).split()

# 1) indice du 1er mot de chaque partie
if "--parts" in sys.argv:
    flat, owner = [], []
    for i, w in enumerate(W):
        for t in norm(w["text"]): flat.append(t); owner.append(i)
    debuts, pos = [], 0
    for p in arg("--parts").split("|"):
        q = norm(p)
        hit = next((k for k in range(pos, len(flat) - len(q) + 1) if flat[k:k + len(q)] == q), None)
        if hit is None: sys.exit(f"partie introuvable dans words.json : « {p} »")
        debuts.append(owner[hit]); pos = hit + len(q)
elif "--temps" in sys.argv:
    debuts = [min(range(len(W)), key=lambda i: abs(W[i]["start"] - float(t))) for t in arg("--temps").split(",")]
else:
    sys.exit("donne --parts ou --temps")
if len(debuts) < 2: sys.exit("il faut au moins 2 parties (1 hook + le body)")

# 2) point de coupe = creux du son entre le mot d'avant et le 1er mot de la partie (énergie par 10 ms)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, np.float32); n = len(x) // 160 * 160
db = 20 * np.log10(np.sqrt((x[:n].reshape(-1, 160) ** 2).mean(1)) + 1e-9)
def creux(i):
    lo, hi = max(0, int((W[i - 1]["end"] - 0.05) * 100)), min(len(db) - 1, int((W[i]["start"] + 0.05) * 100))
    if hi <= lo: return (W[i - 1]["end"] + W[i]["start"]) / 2
    return (lo + int(np.argmin(db[lo:hi + 1]))) / 100 + 0.005
cuts = [0.0] + [round(creux(i) * FPS) / FPS for i in debuts[1:]] + [TOTAL]   # grille des images : image et son de même durée
labels = [f"HOOK {k + 1}" for k in range(len(debuts) - 1)] + ["BODY"]

# 3) écrans (PNG) : fond noir, texte blanc centré, Outfit SemiBold
tmpdir = os.path.join(os.path.dirname(os.path.abspath(out)), "_ecrans"); os.makedirs(tmpdir, exist_ok=True)
font = ImageFont.truetype(FONT, int(HEI * 0.085))
try: font.set_variation_by_name("SemiBold")
except Exception: pass
pngs = []
for lab in labels:
    im = Image.new("RGB", (WID, HEI), (0, 0, 0)); d = ImageDraw.Draw(im)
    l, t, r, b = d.textbbox((0, 0), lab, font=font)
    d.text(((WID - (r - l)) / 2 - l, (HEI - (b - t)) / 2 - t), lab, font=font, fill=(255, 255, 255))
    p = os.path.join(tmpdir, lab.replace(" ", "_") + ".png"); im.save(p); pngs.append(p)

# 4) montage : écran, partie, écran, partie... (un seul encodage, puce vidéo du Mac)
L = len(labels)
inputs = ["-i", clip]
for p in pngs: inputs += ["-loop", "1", "-framerate", FPS_S, "-t", f"{DUREE}", "-i", p]          # entrées 1..L
for _ in labels: inputs += ["-f", "lavfi", "-t", f"{DUREE}", "-i", f"anullsrc=r={SR}:cl=stereo"]   # entrées L+1..2L
f, chain = "", ""
for k in range(L):
    a, b = cuts[k], cuts[k + 1]
    f += (f"[{k + 1}:v]scale={WID}:{HEI}:out_range={'pc' if RNG == 'pc' else 'tv'},setsar=1,fps={FPS_S}[e{k}];"
          f"[{L + 1 + k}:a]anull[s{k}];"
          f"[0:v]trim={a:.4f}:{b:.4f},setpts=PTS-STARTPTS,setsar=1[v{k}];"
          f"[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,aformat=sample_rates={SR}:channel_layouts=stereo[a{k}];")
    chain += f"[e{k}][s{k}][v{k}][a{k}]"
f += chain + f"concat=n={2 * L}:v=1:a=1[vc][a];[vc]scale=out_range={'pc' if RNG == 'pc' else 'tv'},format=nv12[v]"
subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", f, "-map", "[v]", "-map", "[a]",
                "-c:v", "h264_videotoolbox", "-q:v", "75", "-g", "60", "-color_range", RNG,
                "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                "-c:a", "aac", "-b:a", "192k", out], check=True)

# 5) repères
t, rep = 0.0, []
for k, lab in enumerate(labels):
    rep.append({"ecran": lab, "ecran_a": round(t, 2), "partie_a": round(t + DUREE, 2),
                "texte": " ".join(w["text"] for w in W if cuts[k] <= (w["start"] + w["end"]) / 2 < cuts[k + 1])[:80]})
    t += DUREE + cuts[k + 1] - cuts[k]
json.dump(rep, open(os.path.splitext(out)[0] + ".reperes.json", "w"), ensure_ascii=False, indent=1)
for r in rep: print(f"{r['ecran_a']:6.2f} s  {r['ecran']:7s} -> {r['texte']}")
print(f"-> {out} ({t:.1f} s)")
