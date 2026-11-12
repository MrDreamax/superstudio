"""Nettoie la voix avec ElevenLabs Voice Isolator puis la remonte à -14 LUFS Coût : ~1 000 crédits ElevenLabs par minute d'audio.
  python3 voix_clean.py entree.mp4 sortie.mp4 (vidéo copiée telle quelle, son remplacé)"""
import os, subprocess, sys, tempfile, requests
src, out = sys.argv[1], sys.argv[2]
key = subprocess.run(["security", "find-generic-password", "-s", "elevenlabs-api-key", "-w"], capture_output=True, text=True).stdout.strip()
tmp = tempfile.mkdtemp()
wav = os.path.join(tmp, "voix.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "44100", wav], check=True)
iso = os.path.splitext(out)[0] + "_iso.mp3"   # gardé : relancer ne repaie pas
if not os.path.exists(iso):
  r = requests.post("https://api.elevenlabs.io/v1/audio-isolation", headers={"xi-api-key": key},
                    files={"audio": ("voix.wav", open(wav, "rb"), "audio/wav")}, timeout=600)
  if r.status_code >= 400: sys.exit(f"ElevenLabs refuse : {r.status_code} {r.text[:300]}")
  open(iso, "wb").write(r.content)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", iso, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-af", "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000,aformat=channel_layouts=stereo", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
print("voix nettoyée :", out)
