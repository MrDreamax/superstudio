# Style Calques : mots derrière la tête, un style par phrase

Reprise du reel de @viashaan (recette : Brain/02-Formations/viashaan-sous-titres-ia-derriere-la-tete.md).
Premier usage : un reel FR ((exemple retiré)).
Échantillon de test : (exemple retiré) (rush RUSH, 33 s, 10 styles).

## Comment ça marche
Chaque image = une pile : décor, mots DERRIÈRE toi, toi (détouré), mots DEVANT, lueurs.
Une caméra virtuelle recadre chaque phrase (zoom, poussée lente, à-coup au début) : un seul plan filmé ressemble à plusieurs.

## Lancer
1. Détourage de tout l'extrait (une fois, ~1 min pour 33 s) :
   `python3 styles/calques/scripts/detoure.py clip.mp4 DEBUT FIN masque.mp4`
2. Écrire `plan.json` (modèle : (exemple retiré)) : clip, mots (ElevenLabs), masque, t0, t1,
   et une scène par phrase `{de, a, style, mot, zoom, tete_a}`.
3. Réglage rapide en images : `python3 styles/calques/scripts/calques.py plan.json --images 1.6,5.0,...`
4. Rendu : `python3 styles/calques/scripts/calques.py plan.json` -> vidéo + voix + bruitages (dossier `sfx/` à côté du plan).

## Les 10 styles (clé `style`)
| style | ce qu'on voit | `mot` |
|---|---|---|
| orbite | mots qui tournent autour de la tête, jamais devant le visage | - |
| choc | un mot géant qui fonce vers la caméra, traînée + secousse | le mot en MAJUSCULES |
| neon | sous-titres lumineux puis mot-clé en néon rose qui clignote, image teintée | 1 ou 2 mots |
| lueur | sous-titres blancs qui brillent, à hauteur de poitrine | - |
| geant | mot géant en couleur DERRIÈRE la tête (la tête couvre ~60 % des lettres), pop 80 -> 105 -> 100 % | MAJUSCULES |
| tracking | fond crème, silhouette noire, cadre jaune sur le visage + chiffres, mot en serif italique | 1 mot |
| contour | pointillés qui suivent ton corps + la phrase qui longe ta silhouette | - |
| serif | mot géant serif italique derrière la tête, vignette | 1 à 3 mots |
| filaire | décor remplacé par une pièce en lignes blanches 3D qui se dessinent | 1 à 3 mots (serif) |
| or | mot géant doré 3D derrière la tête, 2 mots en arc au-dessus, flèche | MAJUSCULES |

## Règles (tirées de viashaan, gardées)
- 2 polices : Outfit (presque tout) + Instrument Serif italique (le mot qui compte). Bebas pour le choc, Archivo 900 pour l'or.
- Une couleur pour presque tout ; la couleur d'accent = le mot à retenir.
- Chaque mot apparaît sur sa voix (temps ElevenLabs), flou -> net en 0,13 s.
- Zones Instagram : texte entre 270 et 1480 px, 65 px des bords.
- Chaque mouvement a son son (earshot ou SSD), sous la voix (-14 à -27 dB).
- Tourner avec 1/3 de vide au-dessus de la tête, haut sombre uni, lumière sur les cheveux.

## Limites connues
- Le contour suit le masque : il tremble un peu si tu bouges vite (lissage 75/25 d'une image à l'autre).
- Pas encore de musique ni de fausse pièce (Beeble, test prévu sur le plan 8 du reel).

## Choix de l’utilisateur
« Plus lisible » plutôt que « plus caché » : la tête couvre au plus ~50 % de la hauteur du mot géant (geant couvre=0.5, serif 0.45, or posé sur le crâne). Ne pas enfoncer plus sans qu'il le demande.

## Décors Beeble
`scripts/beeble.py beeble.json` (modèle : (exemple retiré)) : 1 image de pièce par décor puis chaque plan en vidéo (masque custom = detoure.py), envoyés en parallèle, cache dans beeble/ (relancer ne repaie pas). Clé : trousseau `beeble-api-key`. **720p par défaut (choix de l’utilisateur)** = 0,10 $ / s ; `"resolution": 1080` dans beeble.json = 0,30 $ / s (rien d'autre ne baisse le prix), 8 s max par plan, vidéo et masque coupés à l'IMAGE près. Puis refaire detoure.py sur clip_beeble.mp4.
Appris : prompts « night time, dim moody… » sinon la pièce sort en plein jour ; un décor PAR phrase (juge : 10 s dans la même pièce = monotone) ; styles ajoutés « dit » (chaque bloc prend le style qu'il nomme) et « fleches » (zone de danger Insta + flèches vers les boutons) ; textes 80-90 px minimum (juge : illisible sur téléphone en dessous).

## Retours de l’utilisateur sur la v1 -> styles fidèles à l'original
- `accroche` : 1er mot en serif italique seul, puis anneau de mots qui entrent à droite et passent derrière la tête (nets de face), puis coupe fond crème + silhouette + dernier mot géant serif derrière la tête + ruban marron (`coupe`: mot de la coupe).
- `rien` : transition (balayage du buste filmé), pas de texte, un whoosh. Garder ces mouvements au dérush : c'est le « OH » de l'original.
- `dit2` : petits mots et néon/italiques à la HAUTEUR DES MAINS (1/3 du corps sous la tête : la couleur de peau confond le pantalon éclairé chaud), capitales empilées en haut à droite.
- `tracking2` : cadre jaune sur le vrai visage -> flash bleu nuit 5 images -> crème + silhouette, « traque mon » serif + mot tapé en Bebas avec curseur jaune ; `descend` (px) descend l'image pour faire de la place au-dessus.
- `rdv` : jour en capitales + heure en or 3D derrière la tête (« insiste sur dimanche 20 h »).
- `geant` + `"logo": true` : petit soleil orange à côté (astérisque de Claude dans l'original).
- Fin d'un reel = UN seul décor (3 pièces dans la même prise = « bizarre », l’utilisateur). Beeble ne refait que les plans changés.
- Musique : `"musique": {"src", "depuis", "db"}` dans plan.json ; temps fort (attaque.py) calé sur le CTA ; 15-17 dB sous la voix.
- `carton` : plein écran en dégradé diagonal BIEN visible bronze -> noir (`fond` brun / nuit / ambre ; un fond trop sombre = « fais un carton avec un dégradé »), texte IMMOBILE : chaque mot a sa place finale dès le début et apparaît en fondu (recentrage + zoom = « on a du mal à lire »), `lignes` = [{mots, style sans|caps|serif|or|petit}], mots qui apparaissent sur la voix, le mot doré se règle seul à la largeur. Un carton qui finit PILE sur un cut cache le saut d'image ; enchaîner 2-3 cartons de fonds différents pour le rythme.

## Beeble : prompter juste, jamais rattraper en post-prod (reprise docteur, l’utilisateur)
« N'essaie jamais de rattraper un truc en post-prod, c'est horrible. Laisse la version de Beeble, même si c'est pas parfait : c'était à toi de mieux prompter avec de meilleures réf. À vouloir cacher un défaut on l'amplifie. Le cadrage ne devait pas bouger. »
- Zéro retouche par-dessus une sortie Beeble (pas de zones figées collées, pas de logo recollé image par image) : un défaut qui passe, on le laisse.
- Tout se joue AVANT : image de référence au cadrage EXACT de la source (jamais décalée ni dézoomée), prompt qui verrouille la caméra (« static locked-off tripod shot, no camera movement, no zoom, no parallax »), masque qui garde le plus possible de la personne (garder seulement la tête = Beeble refait toute la pièce et le décor glisse).
- Logos / textes voulus dans le décor : déjà présents et nets dans l'image de référence, puis acceptés tels que Beeble les rend.
- Coût annoncé + OK de l’utilisateur avant tout lot payant ; 1 plan test payant montré avant le lot entier.

## Images folles de Beeble
Beeble rate souvent la 1re image (parfois 2-3, ou la dernière) de chaque plan : blouse oubliée, pull d'une autre couleur, décor qui saute. Isolée = 1/30 s, mais l’utilisateur la voit sur pause.
- Après CHAQUE sortie Beeble : `scripts/images_folles.py video.mp4 plans.json` -> liste + planches avant/folle/après dans controle/folles/ ; REGARDER la planche.
- Réparer : `--repare sortie-fix.mp4` = chaque image folle remplacée par l'image propre la plus proche du MÊME plan (son intact, durée identique). Ce n'est pas une retouche par-dessus Beeble : on retire une image ratée.
- Ne jamais exclure les débuts / fins de plan du contrôle (c'est là qu'elles sont).

## Objet tenu raté par le masque
Laptop doré sur mur beige : detoure.py perd le couvercle. Pas de bricolage de masques. Options propres : alpha_mode \"select\" de Beeble (1 image clé PNG + alpha_keyframe_index, son IA propage) ou ce plan sans Beeble. Mur clair sans Beeble : \"ombre\": 0.92 dans plan.json et \"couleur\": [28,28,30] sur geant / serif.

## Correction rapide (clients compris)
Une correction = seulement le morceau touché : `scripts/morceau.py plan.json DEPUIS ANCIEN_FINAL ANCIEN_MASQUE` (DEPUIS = un cut). Ne jamais relancer detoure.py ni calques.py sur tout le reel pour une retouche. Garder chaque version (final_vN.mp4) et son masque.

## Voix plus forte et plus claire
`scripts/voix_clean.py clip.mp4 clip_voix.mp4` = ElevenLabs Voice Isolator (~1 000 crédits/min, fichier _iso.mp3 gardé : relancer ne repaie pas) + -14 LUFS. Puis `calques.py plan.json --son image.mp4` refait SEULEMENT le son sur une image déjà rendue, et le final se cale à -14 LUFS (crête < -1,5 dB).
