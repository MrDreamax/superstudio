"""Fin basse 

Mesure la mélodie de la voix (librosa pyin) sur la fin de chaque phrase : hauteur des 0,5 dernières secondes de voix
comparée à la hauteur médiane de la phrase. Chute >= 8 % = fin basse.

    python3 fin_basse.py <video> <words.json> # contrôle la FIN de la vidéo (code 1 si pas bonne)
    python3 fin_basse.py <video> <words.json> --candidats [--de s --a s] # liste toutes les fins de phrase possibles avec leur chute
words.json = {"words": [{"text", "start", "end"}]} dans les temps de la vidéo (cut.words.json, words.json du rush...).
"""
import json, subprocess, sys, tempfile, os
import numpy as np
import librosa

SEUIL = 0.92   # fin <= 92 % de la médiane de la phrase


def audio(video, a, b):
    with tempfile.TemporaryDirectory() as d:
        w = os.path.join(d, "x.wav")
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{max(0, a):.3f}", "-to", f"{b:.3f}", "-i", video,
                        "-ac", "1", "-ar", "16000", w], check=True)
        y, _ = librosa.load(w, sr=16000)
    return y


def chute(video, mots):
    """mots = la phrase entière. Rend (ratio fin / médiane, hauteur médiane, hauteur de fin)."""
    a, b = mots[0]["start"], mots[-1]["end"]
    y = audio(video, a, b + 0.05)
    f0, voix, _ = librosa.pyin(y, fmin=70, fmax=350, sr=16000, frame_length=1024, hop_length=160)
    t = np.arange(len(f0)) * 160 / 16000
    ok = voix & ~np.isnan(f0)
    if ok.sum() < 10:
        return None, None, None
    med = np.median(f0[ok])
    fin_v = t[ok][-1]
    fin = f0[ok & (t >= fin_v - 0.5)]
    if len(fin) < 3:
        return None, med, None
    f = np.median(fin[-max(3, len(fin) // 2):])   # la toute fin de la dernière syllabe voisée
    plancher = np.percentile(f0[ok], 20)
    # (« par le business », 98 Hz, phrase de 135 à 97 Hz) : une phrase qui DESCEND jusqu'à son plancher est une fin basse,
    # même si la chute finale est douce. Sinon chute >= 8 % sous la médiane.
    return (min(f / med, SEUIL) if f <= plancher * 1.03 else f / med), med, f


def phrases(w):
    out, cur = [], []
    for x in w:
        cur.append(x)
        if x["text"].strip().endswith((".", "!", "?")):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


if __name__ == "__main__":
    video, wj = sys.argv[1], sys.argv[2]
    w = json.load(open(wj))
    w = w.get("words", w) if isinstance(w, dict) else w
    ph = phrases(w)
    if "--candidats" in sys.argv:
        de = float(sys.argv[sys.argv.index("--de") + 1]) if "--de" in sys.argv else 0
        a_ = float(sys.argv[sys.argv.index("--a") + 1]) if "--a" in sys.argv else 1e9
        for p in ph:
            if not (de <= p[-1]["end"] <= a_):
                continue
            if not p[-1]["text"].strip().endswith("."):
                continue
            r, m, f = chute(video, p[-12:])
            if r is None:
                continue
            verdict = "BASSE" if r <= SEUIL else "haute"
            print(f"{p[-1]['end']:7.2f} s  {r:4.2f}  {verdict:5}  …{' '.join(x['text'].strip() for x in p[-8:])}")
        sys.exit()
    der = ph[-1]
    # dans un clip coupé, ElevenLabs ne met jamais de ponctuation au dernier mot : seule une virgule ou des « ... » disent « phrase pas finie »
    point = not der[-1]["text"].strip().endswith((",", "...", "…", ":"))
    r, m, f = chute(video, der[-12:])
    print(f"dernière phrase : …{' '.join(x['text'].strip() for x in der[-10:])}")
    print(f"point final : {'oui' if point else 'NON'} · chute de voix : {r:.2f} (fin {f:.0f} Hz / médiane {m:.0f} Hz)" if r else "voix non mesurable")
    bon = point and r is not None and r <= SEUIL
    print("✅ fin basse" if bon else "❌ fin pas basse : finir sur une autre phrase (--candidats)")
    sys.exit(0 if bon else 1)
