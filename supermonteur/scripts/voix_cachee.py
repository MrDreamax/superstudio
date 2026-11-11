"""Voix cachée (09/11/2026, l’utilisateur : « je dis deux fois Tony Robbins », « un mot répété en double », « quelques euh ») :
ElevenLabs gomme les euh, faux départs et mots doublés. Ce script cherche la voix DANS les blancs entre deux mots transcrits.

    python3 voix_cachee.py <video ou rush> <words.json> [--de s --a s]
Chaque ligne = un bout de voix non transcrit (euh, mot doublé, faux départ) à couper dans plages.json.
"""
import json, os, subprocess, sys, tempfile
import numpy as np, librosa

video, wj = sys.argv[1], sys.argv[2]
de = float(sys.argv[sys.argv.index("--de") + 1]) if "--de" in sys.argv else 0
a_ = float(sys.argv[sys.argv.index("--a") + 1]) if "--a" in sys.argv else 1e9
w = json.load(open(wj)); w = w.get("words", w) if isinstance(w, dict) else w
w = [x for x in w if de <= x["start"] <= a_]
if not w: sys.exit("aucun mot dans la plage")
a, b = w[0]["start"], w[-1]["end"]
with tempfile.TemporaryDirectory() as d:
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", video, "-vn", "-ac", "1", "-ar", "16000", f"{d}/x.wav"], check=True)
    y, _ = librosa.load(f"{d}/x.wav", sr=16000)
f0, voise, _ = librosa.pyin(y, fmin=70, fmax=350, sr=16000, frame_length=1024, hop_length=160)   # un euh est VOISÉ (hauteur stable), un souffle non
voise = np.nan_to_num(voise).astype(bool)
db = 20 * np.log10(librosa.feature.rms(y=y, frame_length=400, hop_length=160)[0] + 1e-9)
seuil = np.percentile(db, 10) + 0.4 * (np.percentile(db, 90) - np.percentile(db, 10))
t = np.arange(len(db)) * 0.01 + a
n = 0
for x, z in zip(w, w[1:]):
    g0, g1 = x["end"] + 0.03, z["start"] - 0.03
    if g1 - g0 < 0.08: continue
    m = (t >= g0) & (t <= g1)
    k = min(len(voise), len(db))
    mm = m[:k] & (db[:k] > seuil) & voise[:k]
    v = mm.sum() * 0.01
    if v > 0.12:   # un euh ou une syllabe doublée dure > 0,15 s ; en dessous = queue de mot ou souffle
        n += 1
        tv = t[:k][mm]
        print(f"voix {v:.2f} s de {tv[0]:.2f} à {tv[-1]:.2f} entre « {x['text'].strip()} » et « {z['text'].strip()} »")
print(f"{n} bout(s) de voix non transcrite" if n else "✅ aucune voix cachée (euh, mot doublé)")
