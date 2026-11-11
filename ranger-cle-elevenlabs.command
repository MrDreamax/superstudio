#!/bin/bash
# Range ta clé ElevenLabs dans le trousseau du Mac (jamais dans un fichier).
# 1. Sur elevenlabs.io, crée une clé API et copie-la.  2. Double-clic sur ce fichier.
CLE="$(pbpaste | tr -d '[:space:]')"
if [[ ${#CLE} -lt 20 ]]; then echo "Copie d'abord ta clé ElevenLabs (Cmd+C), puis relance ce fichier."; read -n1 -p "Touche pour fermer"; exit 1; fi
security add-generic-password -U -a "$USER" -s elevenlabs-api-key -w "$CLE" && echo "Clé ElevenLabs rangée. Tu peux fermer cette fenêtre." 
printf '' | pbcopy   # on vide le presse-papier
read -n1 -p "Touche pour fermer"
