#!/usr/bin/env bash
# Super Studio : installe (ou met à jour) TOUT en une fois :
#   1. le master prompt (~/.claude/CLAUDE.md), 2. les agents, 3. les skills, 4. le Brain (mémoire + fiches d'experts),
#   5. les moteurs du Monteur et du Carrousel (~/Documents/SuperApps), les musiques, les outils.
# Usage : bash install.sh   (depuis le dossier téléchargé). Relançable sans risque : c'est aussi la mise à jour.
#
# Ce que le script ne touche JAMAIS une fois installé :
#   - la partie « Qui je suis » du CLAUDE.md (entre les balises PROFIL)
#   - le Brain perso : 00-Moi, 01-Projets, 04-Audits, 05-Decisions, 06-Contenu, 07-Clients, hot.md, log.md, index.md
#   - supermonteur : config.json, da/<client>.json, retours-client.md, broll_exclus.txt, ref/
#   - publieur : config.json, retours-client.md · carrousel : retours-client.md
#   - applis : config.json, superda/da.json + img/ + historique/, reels/, projets/, journaux
#   - ~/Documents/Montage et ~/Documents/Contenu
# Rien n'est supprimé chez la personne : un outil d'une ancienne version reste là. Tout fichier remplacé est
# d'abord sauvegardé dans ~/.claude/backups/superstudio-<date>/.
set -euo pipefail

ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CL="$HOME/.claude"
BR="$HOME/Documents/Brain"
TS="$(date +%Y%m%d-%H%M%S)"
BK="$CL/backups/superstudio-$TS"
URL="https://github.com/MrDreamax/superstudio"
mkdir -p "$CL/agents" "$CL/skills" "$BR"
backup() { local rel="${1#"$HOME"/}"; mkdir -p "$BK/$(dirname "$rel")"; cp -R "$1" "$BK/$rel"; }

# ---------- 1. Master prompt ----------
NEW="$ICI/config/CLAUDE.md"; DEST="$CL/CLAUDE.md"
if [[ -f "$DEST" ]] && grep -q '<!-- PROFIL:DEBUT -->' "$DEST"; then
  BLOCK="$(mktemp)"; OUT="$(mktemp)"
  awk '/<!-- PROFIL:DEBUT -->/{f=1} f{print} /<!-- PROFIL:FIN -->/{f=0}' "$DEST" > "$BLOCK"
  awk -v bf="$BLOCK" '/<!-- PROFIL:DEBUT -->/ { while ((getline l < bf) > 0) print l; skip=1; next }
    /<!-- PROFIL:FIN -->/ { skip=0; next } !skip { print }' "$NEW" > "$OUT"
  if ! cmp -s "$OUT" "$DEST"; then backup "$DEST"; cp "$OUT" "$DEST"; fi
  rm -f "$BLOCK" "$OUT"; echo "Master prompt mis à jour (ton profil est intact)."
elif [[ -f "$DEST" ]]; then
  backup "$DEST"; cp "$NEW" "$DEST"; echo "Ancien CLAUDE.md sauvegardé dans $BK/.claude/CLAUDE.md (Bienvenue récupère ce qui compte)."
else
  cp "$NEW" "$DEST"; echo "Master prompt installé."
fi

# ---------- 2. Agents ----------
n=0
for f in "$ICI"/config/agents/*.md; do
  d="$CL/agents/$(basename "$f")"
  if [[ -f "$d" ]] && ! cmp -s "$f" "$d"; then backup "$d"; fi
  cp "$f" "$d"; n=$((n + 1))
done
echo "$n agents installés."

# ---------- 3. Skills (hors Monteur, Publieur, Carrousel, Scripteur : plus bas) ----------
n=0
for s in "$ICI"/config/skills/*/; do
  name="$(basename "$s")"; d="$CL/skills/$name"
  if [[ -d "$d" ]] && ! diff -rq "$s" "$d" >/dev/null 2>&1; then backup "$d"; fi
  mkdir -p "$d"; rsync -a --exclude config.json --exclude retours-client.md "$s" "$d/"; n=$((n + 1))
done
echo "$n skills installés."

# ---------- 4. Le Brain ----------
for dir in 02-Formations 03-Livres 08-Conseillers _outils; do mkdir -p "$BR/$dir"; cp -R "$ICI/Brain/$dir/." "$BR/$dir/"; done
for f in README.md GUIDE.md GUIDE.html; do [[ -f "$ICI/Brain/$f" ]] && cp "$ICI/Brain/$f" "$BR/$f"; done
( cd "$ICI/Brain"
  for p in 00-Moi 01-Projets 04-Audits 05-Decisions 06-Contenu 07-Clients hot.md log.md index.md; do
    [[ -e "$p" ]] || continue
    find "$p" -type f | while read -r f; do [[ -e "$BR/$f" ]] || { mkdir -p "$BR/$(dirname "$f")"; cp "$f" "$BR/$f"; }; done
  done )
mkdir -p "$HOME/Documents/Contenu/medias/rushes" "$HOME/Documents/Contenu/medias/photos"
echo "Brain prêt dans $BR ($(find "$BR" -name '*.md' | wc -l | tr -d ' ') fiches). Guide : $BR/GUIDE.html"
{ echo "Super Studio installé le $(date '+%d/%m/%Y %H:%M')"; echo "Lien (pour « mets à jour Super Studio ») : $URL"; echo "Brain : $BR"; } > "$CL/superstudio.txt"

# ---------- 5. Monteur, Publieur, Carrousel, Scripteur et leurs moteurs ----------
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/supermonteur"
PSRC="$(dirname "$SRC")/publieur"
DEST="$HOME/.claude/skills/supermonteur"
PDEST="$HOME/.claude/skills/publieur"
CSRC="$(dirname "$SRC")/carrousel"
CDEST="$HOME/.claude/skills/carrousel"
ASRC="$(dirname "$SRC")/apps"
ADEST="$HOME/Documents/SuperApps"
MONT="$HOME/Documents/Montage"
TS="$(date +%Y%m%d-%H%M%S)"

[[ -d "$SRC" ]] || { echo "Dossier supermonteur introuvable à côté de install.sh"; exit 1; }
[[ "$(uname)" == "Darwin" ]] || echo "Attention : testé sur Mac seulement."

[[ -d "$DEST" ]] && backup "$DEST"
mkdir -p "$DEST"
# moteur remplacé ; fichiers du client protégés (exclus = ni copiés ni supprimés)
rsync -a --delete \
  --exclude config.json --exclude retours-client.md --exclude broll_exclus.txt \
  --exclude 'da/*.json' --exclude ref/ \
  "$SRC/" "$DEST/"
cp "$SRC/da/exemple.json" "$DEST/da/exemple.json"

if [[ ! -f "$DEST/config.json" ]]; then
  sed "s#~/#$HOME/#g" "$SRC/config.exemple.json" > "$DEST/config.json"
  echo "Réglages créés : $DEST/config.json"
fi
[[ -f "$DEST/retours-client.md" ]] || printf '# Mes retours (lus AVANT chaque montage, passent avant tout le reste)\nFormat : JJ/MM/AAAA · reel · ce qui n%sallait pas → règle\n\n' "'" > "$DEST/retours-client.md"
[[ -f "$DEST/broll_exclus.txt" ]] || echo "# B-rolls à ne jamais utiliser (une action de _INDEX.csv par ligne)" > "$DEST/broll_exclus.txt"
mkdir -p "$MONT/B-ROLLS" "$MONT/MUSIQUE" "$MONT/SFX" "$MONT/LIVRES" "$MONT/RUSHS"

# Publieur : config.json absent = 1er lancement (Claude le crée avec lui, mode-client.md), jamais écrasé ensuite
if [[ -d "$PSRC" ]]; then
  if [[ -d "$PDEST" ]]; then
    backup "$PDEST"
  fi
  mkdir -p "$PDEST"
  rsync -a --delete --exclude config.json --exclude retours-client.md "$PSRC/" "$PDEST/"
  # 12/11 : réglages du Publieur créés une fois (avant : jamais créés, « Réglages introuvables »), reels lus dans le Monteur
  if [[ ! -f "$PDEST/config.json" ]]; then
    sed 's#"montages": "~/Documents/Montage/LIVRES"#"montages": "~/Documents/SuperApps/supermonteur/reels"#' "$PDEST/config.exemple-client.json" > "$PDEST/config.json"
  fi
  [[ -f "$PDEST/retours-client.md" ]] || printf '# Mes retours sur la publication (lus AVANT chaque semaine, passent avant tout le reste)\nFormat : JJ/MM/AAAA · reel · problème → règle\n\n' > "$PDEST/retours-client.md"
  mkdir -p "$MONT/PUBLICATION"
fi

# Carrousel : le moteur des carrousels (style Apple), utilisé par SuperCarrousel
if [[ -d "$CSRC" ]]; then
  if [[ -d "$CDEST" ]]; then
    backup "$CDEST"
  fi
  mkdir -p "$CDEST"
  rsync -a --delete --exclude retours-client.md --exclude __pycache__ "$CSRC/" "$CDEST/"
  [[ -f "$CDEST/retours-client.md" ]] || printf '# Mes retours sur les carrousels (lus AVANT chaque carrousel)\nFormat : JJ/MM/AAAA · carrousel · ce qui n%sallait pas → règle\n\n' "'" > "$CDEST/retours-client.md"
fi

# Super et ses 4 outils : le code est remplacé, les données de la personne jamais touchées
if [[ -d "$ASRC" ]]; then
  mkdir -p "$ADEST"
  rsync -a --delete \
    --exclude config.json --exclude /superda/da.json --exclude /superda/img/ --exclude /superda/historique/ --exclude /superda/inspiration/ \
    --exclude demandes.jsonl --exclude /supermonteur/reels/ --exclude /supercarrousel/projets/ --exclude metricool.json \
    --exclude '*.log' --exclude a-corriger.json --exclude feedback-retours.md --exclude .rendu.lock --exclude _outils/ \
    --exclude preuves/ --exclude __pycache__ --exclude /super/ --exclude /ouvrir.command --exclude /ouvrir-super.sh \
    --exclude ma-marque.md --exclude /superveille/enregistres/ --exclude /superveille/enregistres.json --exclude '/superveille/*.lock' \
    --exclude /superveille/veilles/ --exclude /superveille/mes-notes/ --exclude '/superveille/tournage*.json' --exclude /superveille/reglages.json \
    "$ASRC/" "$ADEST/"
  for a in "" supermonteur/ supercarrousel/; do
    [[ -f "$ADEST/${a}config.json" ]] || cp "$ADEST/${a}config.exemple.json" "$ADEST/${a}config.json"
  done
  [[ -f "$ADEST/superda/da.json" ]] || cp "$ADEST/superda/da.defaut.json" "$ADEST/superda/da.json"
  # 1.7 : tailles par défaut revues (titre 62 px en une seule taille, sous-titres 54 px). Seulement si la personne
  # n'a jamais touché aux tailles (encore 104 · 52 de la 1.6) : sinon ses réglages restent.
  python3 - "$ADEST/superda/da.json" <<'PYDA' || true
import json, sys
p = sys.argv[1]
d = json.load(open(p))
m, duo = d.get("montage", {}), d.get("commun", {}).get("duo", {})
if m.get("titre", {}).get("taille") == 104 and m.get("sous_titres", {}).get("taille") == 52:
    m["titre"].update(taille=62, decalage=60, _y=350)
    m["sous_titres"].update(taille=54, majuscules=False)
    if duo.get("id") == "moderne" and "ratio_ligne1" not in duo.get("principale", {}):
        duo["principale"].update(graisse_ligne1=700, ratio_ligne1=1)
        duo.get("secondaire", {})["graisse"] = 700
    for r in d.get("_resume", {}).get("montage", []):
        if r.get("cle") == "tailles":
            r["valeur"] = "62 · 54 px"
    json.dump(d, open(p, "w"), ensure_ascii=False, indent=1)
    print("Tailles du titre et des sous-titres mises à jour (62 · 54 px).")
# 1.7.2 : duo Apple (SF Pro) par défaut. Seulement si la DA n'a jamais été enregistrée (« maj » d'origine).
if d.get("maj") == "2026-10-28T10:53:06+01:00" and duo.get("id") == "moderne":
    cat = json.load(open(p.replace("da.json", "catalogue.json")))
    apple = next(x for x in cat["duos"] if x["id"] == "apple")
    d["commun"]["duo"] = {k: apple[k] for k in ("id", "nom", "principale", "secondaire")}
    for r in d.get("_resume", {}).get("montage", []) + d.get("_resume", {}).get("carrousels", []):
        if r.get("cle") == "duo":
            r["valeur"] = "Apple"
    json.dump(d, open(p, "w"), ensure_ascii=False, indent=1)
    print("Police par défaut : SF Pro (duo Apple).")
PYDA
  mkdir -p "$ADEST/superda/img" "$MONT/MONTAGES" "$MONT/PUBLICATION"
  [[ -f "$ADEST/superda/img/frame.jpg" ]] || cp "$ASRC/superda/img/frame.jpg" "$ADEST/superda/img/frame.jpg"
  chmod +x "$ADEST"/*/lancer.sh "$ADEST/superda/connecter-claude.command"
fi

# Scripteur : remplacé à chaque mise à jour (13/11 : plus d'appli Super, rien n'est supprimé chez la personne)
for s in scripteur; do
  [[ -d "$HOME/.claude/skills/$s" ]] && backup "$HOME/.claude/skills/$s"
  if [[ -d "$(dirname "$SRC")/$s" ]]; then mkdir -p "$HOME/.claude/skills/$s"; rsync -a --delete "$(dirname "$SRC")/$s/" "$HOME/.claude/skills/$s/"; fi
done

bash "$DEST/scripts/setup.sh"
# SF Pro (police Apple) : jamais livrée avec Super, prise sur CE Mac (elle y est déjà), pour le Monteur et SuperDA
if [[ -f /System/Library/Fonts/SFNS.ttf ]]; then
  for f in "$DEST/fonts" "$ADEST/superda/fonts"; do [[ -d "$f" ]] && cp /System/Library/Fonts/SFNS.ttf "$f/SF-Pro.ttf"; done
else
  echo "Attention : SF Pro introuvable sur ce Mac, le duo Apple utilisera une autre police."
fi
# Le Scripteur : yt-dlp (récupère une vidéo depuis un lien pour la transcrire)
mkdir -p "$HOME/.local/bin"
[[ -x "$HOME/.local/bin/yt-dlp" ]] || curl -fsSL https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos -o "$HOME/.local/bin/yt-dlp" && chmod +x "$HOME/.local/bin/yt-dlp" || echo "Attention : yt-dlp pas installé (liens de vidéos pour Le Scripteur)."
/usr/bin/python3 -c "import yt_dlp" 2>/dev/null || /usr/bin/python3 -m pip install --user -q yt-dlp || echo "Attention : module yt-dlp pas installé (Le Scripteur)."
# modules en plus pour les carrousels (lecture d'un reel, détourage)
python3 -c "import scipy, cv2" 2>/dev/null || python3 -m pip install --user -q scipy opencv-python-headless || echo "Attention : scipy / opencv pas installés (carrousels depuis un reel)."
# 1.7 (juge 1.6 : 1er démarrage du Carrousel = 188 s) : le tout 1er chargement de ces modules est long, on le fait ici
echo "Préparation du Carrousel (jusqu'à 3 min la première fois)…"
/usr/bin/python3 -c "import numpy, scipy.ndimage, PIL" 2>/dev/null || true
# Les 100 musiques si leur ZIP est posé à côté
mkdir -p "$HOME/Documents/Montage"
for z in "$ICI/100-MUSIQUES.zip" "$ICI/../100-MUSIQUES.zip" "$HOME/Downloads/100-MUSIQUES.zip"; do
    # 12/11 : le dossier MUSIQUE existe déjà (mkdir plus haut) : on teste la présence de mp3, pas du dossier
  if [[ -f "$z" && -z "$(find "$HOME/Documents/Montage/MUSIQUE" -name '*.mp3' -print -quit 2>/dev/null)" ]]; then echo "Installation des 100 musiques…"; unzip -q "$z" -d "$HOME/Documents/Montage" && echo "100 musiques installées dans Documents/Montage/MUSIQUE."; break; fi
done
[[ -n "$(find "$HOME/Documents/Montage/MUSIQUE" -name '*.mp3' -print -quit 2>/dev/null)" ]] || echo "Attention : pas encore de musiques. Mets 100-MUSIQUES.zip à côté de ce dossier et relance, ou pose tes mp3 dans Documents/Montage/MUSIQUE."
# ElevenLabs obligatoire (transcription des rushs)
security find-generic-password -s elevenlabs-api-key -w >/dev/null 2>&1 || echo "À FAIRE : clé ElevenLabs. Copie ta clé (elevenlabs.io), puis dis à Claude : « Range ma clé ElevenLabs »."
echo "Super Studio installé (version $(cat "$ICI/VERSION"))."
[[ -d "$BK" ]] && echo "Sauvegarde des anciens fichiers : $BK"
echo "Publication en mode essai : rien ne part tant que tu ne l'actives pas."
B="$(dirname "$SRC")/BIENVENUE.md"; [[ -f "$B" ]] && { echo; cat "$B"; }
