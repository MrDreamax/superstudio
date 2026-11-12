#!/usr/bin/env python3
"""Transcrit une vidéo mot pour mot (fichier du Mac OU lien Instagram / TikTok / YouTube).
  python3 transcrire.py <fichier ou lien> [--langue fr|en|es...]
Sortie : le texte dit, en paragraphes, à l'écran + un fichier .txt dans ~/Documents/Scripts/transcriptions/.
Moteur : ElevenLabs (clé dans le trousseau, service elevenlabs-api-key), Whisper du Mac en secours.
"""
import os, re, subprocess, sys, tempfile, time

MOTEUR = os.path.expanduser("~/.claude/skills/supermonteur/scripts")
sys.path.insert(0, MOTEUR)
from mots import transcrire  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith("--")]
if not args:
    sys.exit("Donne un fichier vidéo ou un lien.")
src = args[0]
langue = sys.argv[sys.argv.index("--langue") + 1] if "--langue" in sys.argv else None
OUT = os.path.expanduser("~/Documents/Scripts/transcriptions")
os.makedirs(OUT, exist_ok=True)

if re.match(r"https?://", src):
    tmp = tempfile.mkdtemp(prefix="transcrire-")
    ytdlp = os.path.expanduser("~/.local/bin/yt-dlp")
    cmd = [ytdlp if os.path.exists(ytdlp) else "yt-dlp", "-q", "--no-playlist", "-f", "bestaudio/best",
           "-o", os.path.join(tmp, "video.%(ext)s"), src]
    r = subprocess.run(cmd, capture_output=True, text=True)
    fichiers = [os.path.join(tmp, f) for f in os.listdir(tmp)]
    if r.returncode or not fichiers:
        sys.exit("Impossible de récupérer cette vidéo (compte privé, lien faux, ou Instagram qui bloque). "
                 "Télécharge-la sur ton Mac et glisse le fichier dans le chat.")
    video, nom = fichiers[0], re.sub(r"[^\w-]+", "-", src.split("?")[0].rstrip("/").split("/")[-1])[:40]
else:
    video = os.path.expanduser(src)
    if not os.path.exists(video):
        sys.exit(f"Fichier introuvable : {video}")
    nom = os.path.splitext(os.path.basename(video))[0]

try:
    try:
        words, moteur = transcrire(video, langue=langue, secours=True)
    except TypeError:
        words, moteur = transcrire(video, langue=langue)
except Exception as e:
    sys.exit(f"Transcription impossible : {e}")

texte, phrase = [], []
for w in words:
    m = (w.get("word") or w.get("text") or "").strip() if isinstance(w, dict) else str(w).strip()
    if not m:
        continue
    phrase.append(m)
    if re.search(r"[.!?…]$", m) and len(phrase) > 6:
        texte.append(" ".join(phrase)); phrase = []
if phrase:
    texte.append(" ".join(phrase))
txt = re.sub(r"\s+([,.!?…])", r"\1", "\n".join(texte))
txt = re.sub(r"\s+'\s*", "'", txt)
chemin = os.path.join(OUT, f"{time.strftime('%Y-%m-%d')} {nom or 'video'}.txt")
open(chemin, "w", encoding="utf-8").write(txt + "\n")
print(txt)
print(f"\n[{len(' '.join(texte).split())} mots · {moteur} · rangé dans {chemin}]")
