#!/bin/bash
# Montage rapide depuis un chat. Cible : moins de 3 min après la réponse de la personne.
#   1) Dès que le rush arrive, AVANT la question :  bash vite.sh prepare <rush>      -> affiche l'id
#      (transcription + choix des prises + titre se préparent pendant que la personne décrit son montage)
#   2) Après sa réponse :                           bash vite.sh monte <id> [Style] [cases JSON]
#      ex. bash vite.sh monte 2026-11-13-img_1 Minimaliste '{"titre":true,"sous_titres":true}'
#      Sortie : 1 ligne JSON d'ouvre.py (html, review, fps, nom, round, url) ou « ERREUR ... ».
#      Ensuite Claude fait les 4 gestes Cut Notes (publish html, asset review, review/current, open).
#   Les deux d'un coup (rien à demander) : bash vite.sh <rush> [Style] [cases JSON]
set -u
APP="$(cd "$(dirname "$0")" && pwd)"; API=http://localhost:8801
curl -s -o /dev/null "$API/api/reels" || { bash "$APP/lancer.sh" >/dev/null 2>&1; sleep 2; }

prepare() {
  curl -s -X POST "$API/api/nouveau" -H 'Content-Type: application/json' \
    -d "$(python3 -c 'import json,sys;print(json.dumps({"rush":sys.argv[1]}))' "$1")" \
    | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])'
}

monte() {
  local ID="$1" STYLE="${2:-Minimaliste}" CASES="${3:-}"
  [ -z "$CASES" ] && CASES='{"titre":true,"sous_titres":true}'
  local D="$APP/reels/$ID"
  st() { python3 -c "import json;e=json.load(open('$D/etat.json'));print(e.get('statut',''))"; }
  while [ "$(st)" = "regarde" ]; do sleep 2; done
  curl -s -o /dev/null -X POST "$API/api/monter/$ID" -H 'Content-Type: application/json' -d "{\"style\":\"$STYLE\",\"cases\":$CASES}"
  sleep 2
  while [ "$(st)" = "montage" ]; do sleep 3; done
  if [ "$(st)" = "erreur" ]; then
    echo "ERREUR $(python3 -c "import json;print(json.load(open('$D/etat.json')).get('erreur',''))")"; return 1
  fi
  python3 ~/.claude/skills/supermonteur/outils/cut-notes/ouvre.py "$D"
}

case "${1:-}" in
  prepare) prepare "$2" ;;
  monte) shift; monte "$@" ;;
  *) ID=$(prepare "$1") || { echo "ERREUR nouveau"; exit 1; }; shift; monte "$ID" "$@" ;;
esac
