"""Vidéo 16:9 sous-titrée (RUSH : l’utilisateur « répare-le » = SuperMonteur doit monter seul un rush horizontal).
Recette validée sur RUSH et RUSH (juge 9/10) : rush dérushé en 1920x1080, sous-titres SF Pro 50 px,
blancs avec halo sombre, EN BAS de l'image (centre du texte y=975, 
voix intacte à -14 LUFS (mix_youtube.py), musique seulement si plan.json en a une.

  python3 soustitres169.py <dossier> (lit plan.json : cam, words, lignes facultatif, music facultatif ; écrit final.mp4)

plan.json :
  "format": "16:9", "cam": "clip.mp4", "words": "words.json",
  "lignes": ["félicitations, tu es bien inscrit", ...] facultatif : texte à l'écran, mot pour mot dans l'ordre (sinon découpe auto)
  "music": {"src": "...", "from": 12.0} facultatif
Découpe auto : une ligne <= 38 caractères, coupée en fin de phrase, sinon après une virgule, jamais un bloc < 0,6 s
(Œil : bloc trop bref = illisible). Minuscule en début de phrase, point final retiré (style validé).
"""
import json, os, re, subprocess, sys, unicodedata
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.abspath(sys.argv[1]); os.chdir(D)
W, H, FPS = 1920, 1080, 30
S = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(os.path.dirname(S), "fonts", "SF-Pro.ttf")
SIZE, POIDS, Y, MAXC, MIN_BLOC = 50, 500, 975, 38, 0.6

plan = json.load(open("plan.json"))
cam = plan.get("cam", "clip.mp4")
mots = json.load(open(plan.get("words", "words.json")))["words"]
txt = lambda m: m.get("text", m.get("word", "")).strip()
_n = lambda s: re.sub(r"[^\w']", "", unicodedata.normalize("NFD", s.lower().replace("’", "'")).encode("ascii", "ignore").decode())
FIN, VIRG = ".!?…", ",;:"


def nettoie(s):
    s = re.sub(r"[.,;:]+$", "", s.strip())               # point / virgule de fin retirés ; ? et ! gardés
    return s.replace("« ", "").replace(" »", "").replace('"', "")


# mots après lesquels une ligne ne finit jamais (« inscrit au | live », « découvrir mon | système » = refusé par l’utilisateur)
FAIBLES = set("au aux à de d' du des le la les l' un une mon ma mes ton ta tes son sa ses ce cet cette ces et ou en "
              "qui que qu' pour sur dans si je tu il on ne n' plus très avec par bien juste pas tout tous".split())
LIENS = set("et pour qui que qu' si ou parce mais dans sur avec en notamment pendant".split())


def debut_phrase(t):
    """Majuscule de début de phrase -> minuscule (style validé) ; « IA », « WhatsApp » restent tels quels."""
    return t[:1].lower() + t[1:] if t[:1].isupper() and t[1:] == t[1:].lower() else t


def coupe(ws):
    """Une phrase trop longue coupée au meilleur endroit : après une virgule ou avant un mot de liaison, jamais après un mot
    faible, parts équilibrées ; récursif jusqu'à des lignes de MAXC caractères au plus."""
    t = " ".join(ws)
    if len(t) <= MAXC or len(ws) < 2:
        return [ws]
    best, bk = None, 1
    for k in range(1, len(ws)):
        g, d = " ".join(ws[:k]), " ".join(ws[k:])
        cout = max(len(g), len(d)) + 0.3 * abs(len(g) - len(d))
        fin = ws[k - 1].lower().rstrip(",;:")
        if ws[k - 1][-1:] in VIRG: cout -= 14
        if ws[k].lower().rstrip(",") in LIENS: cout -= 8
        if fin in FAIBLES or fin.endswith("'"): cout += 60
        if k == 1 or k == len(ws) - 1: cout += 25           # jamais un mot seul sur sa ligne
        if best is None or cout < best: best, bk = cout, k
    return coupe(ws[:bk]) + coupe(ws[bk:])


def auto():
    """[(texte, nb de mots)] : une phrase = une ligne si elle tient, sinon coupée aux bons endroits."""
    phrases, cur = [], []
    for i, m in enumerate(mots):
        t = txt(m)
        if not cur: t = debut_phrase(t) if (i == 0 or txt(mots[i - 1])[-1:] in FIN) else t
        cur.append(t)
        if t[-1:] in FIN: phrases.append(cur); cur = []
    if cur: phrases.append(cur)
    return [(nettoie(" ".join(l)), len(l)) for ph in phrases for l in coupe(ph)]


if plan.get("lignes"):
    L = [(nettoie(t), len(t.split())) for t in plan["lignes"]]
    ecran = [_n(x) for t in plan["lignes"] for x in t.split()]
    assert len(ecran) == len(mots), f"plan.lignes : {len(ecran)} mots à l'écran pour {len(mots)} mots dits"
    for i, (x, m) in enumerate(zip(ecran, mots)):
        assert x == _n(txt(m)), f"plan.lignes : mot {i} « {x} » à l'écran, « {txt(m)} » dit"
else:
    L = auto()

fin = round(float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cam])) * FPS) / FPS
blocs, k = [], 0
for t, n in L:
    blocs.append([t, mots[k]["start"], mots[k + n - 1]["end"]]); k += n
# bloc trop bref : fusionné avec le suivant (ou le précédent pour le dernier)
# (temps AFFICHÉ = jusqu'au bloc suivant si le trou est < 0,5 s, sinon fin du mot + 0,2 s, comme au rendu)
affiche = lambda i: (blocs[i + 1][1] if i + 1 < len(blocs) and blocs[i + 1][1] - blocs[i][2] < 0.5 else blocs[i][2] + 0.2) - blocs[i][1]
i = 0
while i < len(blocs):
    if affiche(i) < MIN_BLOC and len(blocs) > 1:
        voisins = [j for j in (i + 1, i - 1) if 0 <= j < len(blocs)]
        j = min(voisins, key=lambda j: len(blocs[j][0]))
        x, y = sorted((i, j))
        blocs[x] = [blocs[x][0] + " " + blocs[y][0], blocs[x][1], blocs[y][2]]; del blocs[y]
        i = max(0, x - 1); continue
    i += 1
blocs[0][1] = 0.0                                          # texte présent dès la 1re image

f = ImageFont.truetype(FONT, SIZE)
f.set_variation_by_axes([POIDS if a["name"] in (b"Weight", "Weight") else a["default"] for a in f.get_variation_axes()])


def calque(t, p):
    masque = Image.new("L", (W, H), 0)
    ImageDraw.Draw(masque).text((W / 2, Y), t, font=f, fill=255, anchor="mm")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halo = masque.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(4)).point(lambda v: min(255, int(v * 2.2)))
    ombre = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ombre.putalpha(halo); img.alpha_composite(ombre, (0, 2))
    blanc = Image.new("RGBA", (W, H), (255, 255, 255, 0)); blanc.putalpha(masque); img.alpha_composite(blanc)
    img.save(p, compress_level=1)


os.makedirs("st", exist_ok=True)
for x in os.listdir("st"):
    if x.endswith(".png"): os.remove(os.path.join("st", x))
Image.new("RGBA", (W, H), (0, 0, 0, 0)).save("st/vide.png")
liste, cur, trop_large = [], 0.0, []
for i, (t, a, b) in enumerate(blocs):
    suite = blocs[i + 1][1] if i + 1 < len(blocs) else fin
    b = suite if suite - b < 0.5 else b + 0.2
    a, b = round(a * FPS) / FPS, round(min(b, fin) * FPS) / FPS
    if f.getlength(t) > W - 160: trop_large.append(t)
    if a > cur: liste.append(("vide.png", a - cur))
    p = f"s{i:03d}.png"; calque(t, "st/" + p); liste.append((p, b - a)); cur = b
if fin > cur: liste.append(("vide.png", fin - cur))
with open("st/calques.txt", "w") as o:
    for p, d in liste: o.write(f"file '{p}'\nduration {d:.4f}\n")
    o.write(f"file '{liste[-1][0]}'\n")
json.dump([{"texte": t, "start": round(a, 3), "end": round(b, 3)} for t, a, b in blocs], open("st/blocs.json", "w"), ensure_ascii=False, indent=0)
courts = [blocs[i][0] for i in range(len(blocs)) if affiche(i) < MIN_BLOC]
print(f"{len(blocs)} sous-titres · blocs < {MIN_BLOC} s : {courts or 'aucun'} · trop larges : {trop_large or 'aucun'}")
if trop_large: sys.exit(f"sous-titre plus large que l'image : {trop_large}")

subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", cam, "-f", "concat", "-safe", "0", "-i", "st/calques.txt",
    "-filter_complex", f"[1:v]fps={FPS},format=rgba[o];[0:v][o]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[sortie]", "-map", "[sortie]", "-an", "-r", str(FPS),
    "-c:v", "h264_videotoolbox", "-profile:v", "high", "-b:v", "14M", "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709",
    "-color_trc", "bt709", "-t", f"{fin:.3f}", "st/rendu.mp4"], check=True)
mix = ["python3", os.path.join(S, "mix_youtube.py"), "st/rendu.mp4", cam, "final.tmp.mp4"]
mu = plan.get("music") or {}
if mu.get("src"): mix += ["--musique", mu["src"], "--debut", str(mu.get("from", 0))]
subprocess.run(mix, check=True)
os.replace("final.tmp.mp4", "final.mp4")                  # nouveau fichier : une version liée (versions/vN.mp4) n'est jamais écrasée
