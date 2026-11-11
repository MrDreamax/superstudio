"""Retirer (09/11/2026, RUSH) : coupe des bouts précis dans cut.mp4 APRÈS le dérush, quand derush.py remet le bout
(sa butée « vraie attaque » recule le bord jusqu'au euh ou au mot doublé collé au mot suivant : « le le marché », « parce que euh le GPS »).

    python3 retirer.py <t0> <t1> [<t0> <t1> ...]      # dans le dossier du reel, temps de cut.mp4 (avant teaser)
Met à jour cut.mp4, cut.words.json (mots dans les bouts retirés supprimés, suite décalée) et cut.segments.json (segment coupé en deux :
les numéros de coupe {"coupe": n} des B-rolls après ce point prennent +1). Garde une copie avant-retrait.*.
Un bout coupé en pleine phrase crée un plan court : le cacher sous un B-roll (Gardien : plans >= 2 s).
"""
import json, shutil, subprocess, sys

v = [float(x) for x in sys.argv[1:]]
cuts = sorted(zip(v[0::2], v[1::2]))
_seg = json.load(open("cut.segments.json")); _b, _c = [0.0], 0.0
for s0, s1 in _seg: _c += s1 - s0; _b.append(_c)
# un bord à moins de 0,08 s d'une coupe du dérush s'y colle (sinon il reste un bout de 1 image : Gardien « micro-coupe »)
cuts = [(min(_b, key=lambda x: abs(x - a)) if min(abs(x - a) for x in _b) < 0.08 else a,
         min(_b, key=lambda x: abs(x - b)) if min(abs(x - b) for x in _b) < 0.08 else b) for a, b in cuts]
for f in ("cut.mp4", "cut.words.json", "cut.segments.json"):
    shutil.copy2(f, "avant-retrait." + f)
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "cut.mp4"]))
keep, p = [], 0.0
for a, b in cuts:
    keep.append((p, a)); p = b
keep.append((p, dur))
fc = ""
for n, (a, b) in enumerate(keep):
    fc += f"[0:v]trim={a:.4f}:{b:.4f},setpts=PTS-STARTPTS[v{n}];[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS[a{n}];"
fc += "".join(f"[v{n}][a{n}]" for n in range(len(keep))) + f"concat=n={len(keep)}:v=1:a=1[v][a]"
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", "avant-retrait.cut.mp4", "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                "-r", "30", "-c:v", "h264_videotoolbox", "-b:v", "40M", "-c:a", "aac", "-b:a", "320k", "cut.mp4"], check=True)


def shift(x):
    return x - sum(b - a for a, b in cuts if x >= b)


w = json.load(open("avant-retrait.cut.words.json"))["words"]
nw = [dict(x, start=shift(x["start"]), end=shift(x["end"])) for x in w if not any(a <= (x["start"] + x["end"]) / 2 < b for a, b in cuts)]
json.dump({"words": nw}, open("cut.words.json", "w"), ensure_ascii=False)
seg = json.load(open("avant-retrait.cut.segments.json"))
new, c = [], 0.0
for s0, s1 in seg:
    parts = [(c, c + s1 - s0)]
    for a, b in cuts:
        q = []
        for x, y in parts:
            if b <= x or a >= y: q.append((x, y))
            else:
                if a > x: q.append((x, a))
                if b < y: q.append((b, y))
        parts = q
    new += [[round(s0 + x - c, 4), round(s0 + y - c, 4)] for x, y in parts if y - x > 1e-3]
    c += s1 - s0
json.dump(new, open("cut.segments.json", "w"))
print(f"retiré {sum(b - a for a, b in cuts):.2f} s · {len(w) - len(nw)} mot(s) · segments : {new}")
