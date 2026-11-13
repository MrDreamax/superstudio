#!/bin/bash
# Range les musiques du Monteur dans ~/Documents/Montage/MUSIQUE.
# Usage : ranger-musiques.command [chemin d'un .zip ou d'un dossier]
# Sans chemin : cherche dans Téléchargements, Bureau et à côté de ce dossier
# un zip ou un dossier dont le nom contient « musique » (ex. « 100 MUSIQUES-20261113T101010Z-001.zip »).
# Relançable : ne recopie pas un titre déjà présent, ne supprime rien.
set -u
ICI="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/Documents/Montage/MUSIQUE"
mkdir -p "$DEST"

SOURCES=()
if [[ $# -gt 0 ]]; then
  for a in "$@"; do SOURCES+=("${a/#\~/$HOME}"); done
else
  while IFS= read -r f; do SOURCES+=("$f"); done < <(
    find "$HOME/Downloads" "$HOME/Desktop" "$ICI/.." -maxdepth 1 \( -iname '*musique*.zip' -o \( -type d -iname '*musique*' \) \) 2>/dev/null | sort -u
  )
fi
[[ ${#SOURCES[@]} -gt 0 ]] || { echo "PAS_TROUVE : aucun fichier musique dans Téléchargements ni sur le Bureau."; exit 2; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
N0=$(find "$DEST" -type f \( -iname '*.mp3' -o -iname '*.m4a' -o -iname '*.wav' \) | wc -l | tr -d ' ')
for s in "${SOURCES[@]}"; do
  [[ "$s" == "$DEST" ]] && continue
  if [[ -f "$s" && "$s" == *.[zZ][iI][pP] ]]; then
    echo "Ouverture de $(basename "$s")…"
    d="$(mktemp -d "$TMP/z.XXXX")"; unzip -q -o "$s" -d "$d" -x '__MACOSX/*' || { echo "Zip abîmé : $s"; continue; }
    s="$d"
  fi
  [[ -d "$s" ]] || continue
  # le dossier racine (« 100 MUSIQUES ») saute : on garde les sous-dossiers d'ambiance
  RAC="$s"; while [[ $(find "$RAC" -mindepth 1 -maxdepth 1 ! -name '.*' ! -name '__MACOSX' | wc -l) -eq 1 && -d "$(find "$RAC" -mindepth 1 -maxdepth 1 ! -name '.*' ! -name '__MACOSX')" ]]; do RAC="$(find "$RAC" -mindepth 1 -maxdepth 1 ! -name '.*' ! -name '__MACOSX')"; done
  rsync -a --ignore-existing --exclude '__MACOSX' --exclude '.DS_Store' --exclude '._*' "$RAC/" "$DEST/"
done
N1=$(find "$DEST" -type f \( -iname '*.mp3' -o -iname '*.m4a' -o -iname '*.wav' \) | wc -l | tr -d ' ')
if [[ "$N1" -gt 0 ]]; then echo "OK : $N1 musiques dans Documents/Montage/MUSIQUE ($((N1-N0)) nouvelles)."; else echo "VIDE : aucune musique trouvée dans ce fichier."; exit 3; fi
