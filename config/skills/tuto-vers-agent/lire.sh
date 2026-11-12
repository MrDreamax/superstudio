#!/bin/zsh
# Lit une vidéo deux fois, de façon indépendante.
#   lire.sh <url> <dossier> [fr|en]
# A = images + Whisper (plugin watch-video)  -> <dossier>/a/
# B = sous-titres YouTube + description/liens -> <dossier>/b/
# Pourquoi ce script : le plugin watch-video peut planter avec le Python 3.9 du Mac
# (vieux yt_dlp + dataclass slots) et la dernière version de PyAV (metadata_errors).
# Donc : téléchargement par un yt-dlp récent (~/.local/bin ou PATH), puis plugin lancé en Python 3.13 via uv, av<16.
set -e
URL="$1"; OUT="$2"; LANGUE="${3:-fr}"
[[ -z "$URL" || -z "$OUT" ]] && { echo "usage : lire.sh <url> <dossier> [fr|en]"; exit 2; }
YTDLP=~/.local/bin/yt-dlp
[[ -x "$YTDLP" ]] || YTDLP=$(command -v yt-dlp || true)
UV=~/.local/bin/uv
[[ -x "$UV" ]] || UV=$(command -v uv || true)
[[ -z "$YTDLP" ]] && { echo "yt-dlp introuvable (skill logiciels pour l'installer)"; exit 4; }
[[ -z "$UV" ]] && { echo "uv introuvable (skill logiciels pour l'installer)"; exit 5; }
WV=$(find ~/Library/Application\ Support/Claude -name watch_video.py -path "*scripts*" 2>/dev/null | head -1)
[[ -z "$WV" ]] && { echo "plugin watch-video introuvable"; exit 3; }
mkdir -p "$OUT/dl" "$OUT/b"

# Lecture B d'abord (rapide) : sous-titres + description + liens
$YTDLP -q --skip-download --write-auto-subs --write-subs --sub-langs "${LANGUE}.*" --sub-format vtt \
  -o "$OUT/b/src.%(ext)s" "$URL" 2>&1 | grep -v WARNING || true
$YTDLP -q --skip-download --dump-json "$URL" 2>/dev/null \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print('# '+d.get('title',''));print(d.get('uploader',''),'·',d.get('upload_date',''));print();print(d.get('description',''))" \
  > "$OUT/b/description.md" || true

# Lecture A : vidéo 720p max, puis images + Whisper
$YTDLP -q -f "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720]/b" --merge-output-format mp4 \
  -o "$OUT/dl/video.%(ext)s" "$URL" 2>&1 | grep -v WARNING || true
$UV run -q --python 3.13 --with faster-whisper --with "av<16" --with yt-dlp --with Pillow --with imagehash \
  python "$WV" "$OUT/dl/video.mp4" --lang "$LANGUE" --whisper local --dedup --resolution 1280 \
  --workdir "$OUT/a" > "$OUT/a.json" 2> "$OUT/a.err"

echo "A : $(ls "$OUT/a/frames" | wc -l | tr -d ' ') images, transcription $OUT/a/transcript.md"
echo "B : $(ls "$OUT/b"/*.vtt 2>/dev/null | wc -l | tr -d ' ') sous-titres, $OUT/b/description.md"
