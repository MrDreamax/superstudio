# DA visuelle : l'ambiance choisie sur de VRAIES photos (branchée dans le Style Lab client : `outils/style-lab/STYLE-LAB.md`)

Le client ne remplit rien : on lui MONTRE jusqu'à 4 ambiances tirées de ses vraies images, il clique sur celle qu'il préfère. Jamais d'image générée par IA.

1. **Matière** : ses photos (celles qu'il glisse, ou `~/Documents/Brain/00-Moi/photos/`) et des images de ses rushs dans des lieux ou des lumières différents :
   `ffmpeg -ss <t> -i <rush> -frames:v 1 -vf "scale=1080:-1" ref/ambianceN.jpg` (net, visage bien centré).
2. **4 ambiances au plus** (Premium sombre · Cinéma chaud · Clair épuré · Énergique coloré, adaptées à ce qu'on a vraiment) : une vraie image par ambiance. Moins de 4 images différentes = moins de cartes, on ne remplit jamais avec du faux.
3. **Planche** : `hstack` des images en une planche, vérifier qu'on le reconnaît. Le client choisit dans le Style Lab (section « Ton ambiance », `round.py --da-images`).
4. **Fiche** : `da/<prenom>.json` (modèle `exemple.json`), couleurs tirées de l'image choisie (dégradé `list`, `halo`, `glow`). Fait tout seul par `round.py lock` ; polices, couleur, musique et rythme se choisissent aussi dans le Style Lab. `QUESTIONNAIRE.md` = seulement la légende.

Pas assez d'images : on saute la section ambiance, le reste du Style Lab marche pareil.
