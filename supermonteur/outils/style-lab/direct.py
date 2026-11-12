#!/usr/bin/env python3
"""Style Lab DIRECT : tout le style (sous-titres + titre) réglé en direct sur UNE page, zéro rendu.
La page passe le rush une fois et dessine sous-titres et titre par-dessus (mêmes px, polices et ombres que build.mjs). Préparation ~1 min.

  1) python3 direct.py prep --clip clip.mp4 --words words.json --start 0 --end 14.6 --keyword faux \\
        --title "La fin des|infopreneurs ?"--title-end 4.5 --suby 1340 --out <dossier SOUS ~/Documents/Montage>
     -> <out>/clip.mp4 (720p, son), <out>/fonts/*.ttf, <out>/data.json
  2) Publier <out>/style-lab-direct.html (capabilities db + user + assets), uploader clip.mp4 + fonts/*.ttf en assets.
  3) python3 direct.py page --out <out> --assets assets.json (assets.json = {"clip.mp4": id, "Montserrat.ttf": id, ...})
     -> réécrit style-lab-direct.html avec les ids, republier le même fichier.
  4) Quand il écrit « suivant » : ArtifactData list `submissions` -> la plus récente = ses choix (champ `choix`).
"""
import argparse, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
FONTS = ["Montserrat.ttf", "Anton-Regular.ttf", "LilitaOne-Regular.ttf", "Cinzel.ttf", "SpaceGrotesk.ttf", "InstrumentSerif-Italic.ttf"]   # 5 polices les plus différentes + serif du mot fort


def prep(a):
    out = os.path.abspath(os.path.expanduser(a.out)); os.makedirs(os.path.join(out, "fonts"), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.start), "-to", str(a.end), "-i", a.clip, "-vf", "scale=720:1280:flags=lanczos",
                    "-c:v", "libx264", "-crf", "29", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
                    "-movflags", "+faststart", os.path.join(out, "clip.mp4")], check=True)
    for f in FONTS:
        src = os.path.join(SKILL, "fonts", f)
        if not os.path.exists(src): src = os.path.expanduser(f"~/Documents/Montage/STYLE-LAB/fonts/{f}")
        shutil.copy(src, os.path.join(out, "fonts", f))
    W = json.load(open(a.words))["words"]
    W = [{"t": round(w["start"] - a.start, 3), "e": round(w["end"] - a.start, 3), "w": w["text"].strip()}
         for w in W if w["start"] >= a.start - 0.01 and w["end"] <= a.end + 0.01 and w["text"].strip()]
    # élisions et ponctuation seule recollées au mot d'avant (comme build.mjs)
    M = []
    for w in W:
        if M and (re.match(r"^['’-]", w["w"]) or re.match(r"^[.,!?…;:%]+$", w["w"])):
            M[-1]["w"] += w["w"].replace("’", "'"); M[-1]["e"] = w["e"]
        else: M.append(w)
    # haut des cheveux pendant le titre (même mesure que build.mjs) -> la page remonte le titre s'il touche la tête
    try:
        ht = float(subprocess.run(["python3", os.path.join(SKILL, "scripts", "headtop.py"), a.clip, str(a.start), str(a.start + a.title_end)],
                                  capture_output=True, text=True, check=True).stdout.strip())
    except Exception: ht = None
    l1, l2 = a.title.split("|")
    data = {"words": M, "keyword": a.keyword.lower(), "title": {"l1": l1, "l2": l2, "end": a.title_end},
            "subY": a.suby, "dur": round(a.end - a.start, 2), "headTop": ht}
    json.dump(data, open(os.path.join(out, "data.json"), "w"), ensure_ascii=False)
    page(argparse.Namespace(out=out, assets=None))
    print(f"OK -> {out} (clip {os.path.getsize(os.path.join(out, 'clip.mp4')) // 1024} Ko, {len(M)} mots)")


def page(a):
    out = os.path.abspath(os.path.expanduser(a.out))
    data = json.load(open(os.path.join(out, "data.json")))
    A = json.load(open(a.assets)) if a.assets else {}
    data["assets"] = {k: "/_blob/" + v for k, v in A.items()}
    html = open(os.path.join(HERE, "direct.html")).read().replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    open(os.path.join(out, "style-lab-direct.html"), "w").write(html)
    print(os.path.join(out, "style-lab-direct.html"))


if __name__ == "__main__":
    p = argparse.ArgumentParser(); sp = p.add_subparsers(dest="cmd", required=True)
    b = sp.add_parser("prep")
    for k in ("--clip", "--words", "--keyword", "--title", "--out"): b.add_argument(k, required=True)
    for k in ("--start", "--end"): b.add_argument(k, type=float, required=True)
    b.add_argument("--title-end", type=float, default=4.5); b.add_argument("--suby", type=int, default=1300)
    g = sp.add_parser("page"); g.add_argument("--out", required=True); g.add_argument("--assets")
    a = p.parse_args()
    prep(a) if a.cmd == "prep" else page(a)
