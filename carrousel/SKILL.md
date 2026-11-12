---
name: carrousel
description: Le Carrousel. Carrousel Instagram (1080x1440, nombre de slides libre, le plus court qui dit tout) au modèle validé - bleu-blanc, vraies photos de l'utilisateur + illustrations 2D SVG, jamais d'image IA. Livre PNG + légende, ne publie jamais. Use when "carrousel", "carousel", "fais-moi un carrousel", "carrousel de la semaine", "transforme ce reel en carrousel", "carrousel sur X", "carousel maker".
---

## CHEZ TOI (client) : CE BLOC PASSE AVANT TOUT LE RESTE DE CE FICHIER
- On fait le carrousel dans le chat, sans ouvrir d'appli avant. Rendu des images : Google Chrome doit être installé sur le Mac (google.com/chrome) ; absent = dis-le en 1 ligne avec ce lien.
- Ses photos : celles qu'il glisse dans le chat, ou `~/Documents/Brain/00-Moi/photos/` s'il en a rangé. Jamais une photo inventée, jamais d'image IA.
- Sa voix : `~/Documents/Brain/00-Moi/` s'il est rempli. Pas de veille, pas d'onglet SuperDA : sa DA est déjà réglée (`~/Documents/SuperApps/superda/da.json`).
- Publier : c'est le skill `publieur` (Blotato), après son OK.
- Un fichier ou un skill cité plus bas qui n'existe pas chez lui : ignore-le.






# Le Carrousel : une grande idée, le moins de slides possible, la DA de la marque

Modèle validé après 5 versions refusées. Ne pas le redécider : l'appliquer.
Référence visuelle : la planche que nomme ton carnet (le carrousel validé).
Référence technique : `exemples/exemple-v4.json` (le skill la reconstruit au pixel près).

## Photos et vidéos de l'utilisateur
Seulement des images qu'il accepte : ses interdits (shooting, look, période) sont dans son carnet et passent avant tout. Vaut pour tout : site, carrousel, slides, montage, B-roll, cover, pub.

## Carnet d'apprentissage
- Avant de commencer : lis `~/Documents/Brain/00-Moi/regles-agents/carrousel.md`. Ses règles passent AVANT ce fichier.
- Si l'utilisateur corrige, note ou refuse ton travail (même en passant) : ajoute UNE ligne dans ce carnet, `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`. Si elle contredit une ancienne, remplace l'ancienne. Dis-le en une ligne : « Noté dans mon carnet : ... ».

## : SuperCarrousel (maquettes validées, CODÉ)
> Section pour l'auteur : chez un client, le carrousel se fait dans le chat (bloc client en tête).
**L'appli existe** : `~/Documents/SuperApps/supercarrousel/` (http://localhost:8797, lancer `bash .../apps/supercarrousel/lancer.sh` ; mode d'emploi côté Claude : son `README.md` et `python3 sc.py a-faire`). Pour l’utilisateur, un carrousel passe par elle : je lis ses demandes avec `sc.py`, j'écris la description, elle rend avec ce moteur.
- 3 départs : **Un reel** (fichier OU lien Instagram / TikTok / YouTube : images + texte du reel, voir 3 bis) · **Un carrousel à reprendre** (lien d'un carrousel qui marche, : FIDÈLE à son concept et son style : mise en page, couleurs, ordre, rythme ; on change SEULEMENT la police et les mots ; images : je les propose ou je les demande à l’utilisateur, slide par slide) · **Une idée** (sujet écrit ou dicté).
- Je fabrique tout d'un coup (pas de validation du texte avant), les slides apparaissent une par une.
- Puis écran de retours (une slide en grand, retour accroché à la slide, « Corrigé ✓ ▶ Revoir », « Suivant : corrige mes retours » / « C'est parfait, on publie ») ; « Ma DA » en tiroir.
- Publier : skill `publieur` (Blotato), après son OK, sur les réseaux qu'il a cochés. Légende écrite par moi, courte.
- **Plus d'alternance obligatoire photo / dessin** : chaque slide prend le visuel qui sert son idée.
- Pas de nombre de slides imposé. Jamais de ponctuation seule en fin de ligne.

## : nouveau modèle style Apple (validé par l’utilisateur)
> Section pour l'auteur : chez un client, sa DA (`~/Documents/SuperApps/superda/da.json`) passe avant.
Remplace le tableau ci-dessous pour l’utilisateur : blanc, SF Pro, photo bord à bord + cheveux détourés qui dépassent, dessins sur cercle bleu clair, fin = 3 bulles iMessage. Branché dans le moteur : mettre `"style": "apple"` dans la description → `carrousel.py` appelle `scripts/apple.py` (rendu local par Chrome, **pas besoin d'Open Carrusel**, ~20 s pour 8 slides).
Exemple complet : `exemples/exemple-apple.json` (copier, adapter). Types : `cover` (kicker, title, photo, accent ; couverture « sujet géant » détourage `scripts/detoure.swift`), `photo` (title, body ou steps ; `"pop": false` si la personne est petite dans l'image), `list` (kicker, title, items = [{icon, t, d}] : liste à icônes, icônes dans `apple.py` ICONS), `art` (title, body, steps, ou `cta` + `cta_q` + `cta_line` pour la fin en 3 bulles). Note manuscrite : `note` + `note_pos`.
Le détourage ne garde que la tête au-dessus de la photo (mains et bruit effacés). Vérifier quand même le haut de chaque slide photo en grand.

## Le modèle (ce qui est validé)
| Élément | Règle |
|---|---|
| Format | 3:4, 1080x1440, AUCUN nombre de slides imposé. 3 slides si 3 suffisent |
| Polices | Montserrat 700 majuscules (couverture, CTA) + Instrument Serif italique (titres), Montserrat 500 (phrases) |
| Alternance | PAS obligatoire : photo ou dessin selon l'idée de la slide (couverture = photo) |
| Illustrations | 2D motion design dessinées en SVG (`art.py`) : fond blanc, grand cercle bleu très clair, aplats, 2 à 4 petits éléments déco |
| Interdit | images générées par IA, quel que soit l'outil. Pas de @, pas de numéro de slide |
| Couverture | **« sujet géant »** (remède 1 d'Ayo, validée en 2 rounds) : fond blanc, titre 2 lignes à gauche, `"accent"` = le mot clé seul en bleu, tête détourée en très grand dont les cheveux frôlent le bas du titre, AUCUN bouton ni flèche. Photo cadrée BUSTE obligatoire (en pied → le moteur reprend l'ancienne couverture et le dit). 7 mots max. Modèle : `(exemple retiré)`. Ancienne : `"cover_style": "ancienne"` |
| Slides | 1 idée par slide : titre serif + 1 phrase courte (ou liste 1-2-3 de 3 lignes courtes). Jamais de pavé |
| Fin | « Commente MOT » + la ressource promise. Flèche de swipe partout sauf sur la dernière |

## Étapes (⏱ ~25 min : annonce-le au début, dis le temps réel à la fin)

### 1. La grande idée (une seule par carrousel)
Le sujet doit toucher un problème de la cible de sa stratégie (00-Moi/strategie-contenu.md, ou celle que nomme son carnet).

### 2. Le texte
- Couverture : écris 10 titres (Résultat, Objection ou Temps, chiffre si possible), garde le meilleur. Elle et la slide 2 doivent accrocher seules.
- Chaque slide ouvre la suivante (« … », question, « mais »). Une slide de preuve vers la fin.
- Preuves autorisées seulement : celles de son Brain (00-Moi/profil.md, son carnet) et des cas clients chiffrés SANS nom tirés du Brain. Rien d'inventé.
- Légende : 4 à 6 lignes qui prolongent (pas un copier-coller des slides), finit par le CTA. 5 hashtags max.

### 3. Les photos (4 slides)
- Jamais : vie intime, photos où quelqu'un d'autre est au premier plan, portraits retouchés ou possiblement IA.
- Planches pour choisir : `python3 scripts/planches.py <dossier_scratchpad> "<mot-clé 1>" "<mot-clé 2>"`, puis lis les planches.
- Chaque photo doit coller à SA slide (ex. preuve = scène devant une salle, posture = sourire en costume). Varie les shootings.
- Couverture : la tête doit laisser de la place au-dessus (« tête y≈ » entre 300 et 450 dans la sortie de `prep.py`).

### 3 bis. Pas de photos perso ? Les images viennent d'un reel
La plupart des gens n'ont pas de shooting : le carrousel se fait depuis un reel déjà tourné.
- Vidéo : le RUSH d'abord (avant montage, zéro texte sur l'image ; chez l’utilisateur `~/Documents/Montage/MONTAGES/<projet>/clip.mp4`, transcription `words.json` à côté). Le reel fini seulement s'il n'y a rien d'autre, et alors seulement des images sans texte sur le visage.
- `python3 scripts/reel2frames.py <video> <out>/_reel --words <words.json>` (~30 s) : 16 images nettes prises entre deux mots (bouche au repos), étalées dans le temps, + `00-candidates.jpg` (planche numérotée) + `texte.txt` (la transcription).
- Lis la planche, garde 4 images variées (gestes différents, pas les yeux fermés, pas la main devant le visage), mets-les en `"src"` des `photos` d'une description `"style": "apple"`.
- Le texte des slides vient du script du reel (`texte.txt`) : même idée, découpée en autant de slides qu'il faut (pas 8 par défaut), avec la méthode de l'étape 2.
- Image face caméra = visage très gros : mets la note manuscrite du côté opposé à la tête.
Exemple réel : `~/Documents/Contenu/carrousels/2026-10-23-sans-teleprompteur/description.json`.

### 4. Les illustrations (4 slides)
- `scripts/art.py` : `apples_grid` (tous pareils / `red_at` = celui qui est différent), `copies` (copier les gros comptes), `stairs` (3 étapes), `chart_up` (résultats, croissance), `chat` (DM, setting), `checklist` (erreurs, étapes), `camera` (tourner face caméra, le trac), `script_long` (script appris par cœur, barré).
- Sujet nouveau : écris une nouvelle fonction dans `art.py` (mêmes couleurs, `frame`, dessin entre y 80 et 820, 2 à 4 éléments `deco`) et ajoute-la à `ARTS` pour la réutiliser. Ou un fichier `.svg` à côté de la description (`"svg": "mon-dessin.svg"`).

### 5. La description puis le montage
- Lance Open Carrusel : `preview_start` avec `name: "open-carrusel"` (config dans le `.claude/launch.json` du dossier de travail). En dernier recours : `cd ~/open-carrusel && npm run dev -- -p 3210` en arrière-plan.
- `python3 ~/.claude/skills/carrousel/scripts/carrousel.py <spec.json>` (SANS `-I` : les scripts s'importent entre eux). ~1 min. Il prépare les photos, monte, exporte les PNG, la planche, la légende et `spec.json`.

### 6. Vérifier (jamais livrer sans)
Lis `00-planche.png`, puis en grand chaque slide douteuse. Contrôle :
- texte lisible, pas de mot seul sur une ligne (force avec `<br>` et `&nbsp;`) ;
- mot de couverture lisible : la tête ne cache pas une lettre entière (ajuste `word_top`) ;
- illustration qui ne touche pas le texte ; photo qui colle au sujet de la slide ;
- bon mot-clé à la fin ; 8 PNG en 1080x1440.
Corrige la description et relance.

### 7. Livrer
- `SendUserFile` de la planche + 3 à 5 lignes : sujet, d'où il vient (veille, script…), ce qui reste à faire.
- Ne publie et ne programme JAMAIS sans son feu vert explicite.
- Une info absente du Brain : dis « je ne l'ai pas ». Ne l'invente pas.

## Technique
- Open Carrusel : `~/open-carrusel` (open source, MIT), patché pour le 3:4 et les vraies italiques. L'éditeur sur http://localhost:3210 permet à l'utilisateur de voir ou retoucher.
- `prep.py` utilise le modèle de détourage du skill supermonteur (`~/.cache/supermonteur/rvm_mobilenetv3_fp32.onnx`). Le SSD doit être branché.
- Porte cash : un carrousel apporte confiance et enregistrements, pas un deal sous 7 jours. Si l'utilisateur y passe plus d'une demi-journée, dis-le une fois (avec le chiffre de son fichier `actions` s'il en a un).

- · Texte parasite derrière la personne (écran de projecteur) : ne JAMAIS le gommer lettre par lettre (taches, cheveux coupés, 3 tours ratés). Méthode qui marche : passer la photo une 1re fois dans le moteur, prendre `_sources/<clé>-fg.png` (détourage), poser le sujet sur un fond uni fait de la médiane de chaque ligne hors sujet et hors lettres, lissé en vertical (sigma 60), puis relancer avec cette image. Photo carrée de profil (1024 px) = visage trop zoomé : à éviter en slide photo.
