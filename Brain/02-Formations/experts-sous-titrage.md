---
description: "Sous-titres incrustés : normes Netflix, BBC, W3C, vitesse de lecture."
type: formation
statut: actif
sujets: [montage]
---
# Experts : sous-titrage (sous-titres incrustés des reels 9:16 face cam)

Date : 2026-10-13.
Complète `experts-montage-high-prod.md` (sections D, S15 à S20) sans le répéter.

Niveaux : **[P]** primaire (guide officiel, étude publiée, expert lui-même, ou mesure faite par moi sur un fichier réel) · **[S]** un tiers décrit · **[H]** hypothèse à tester (mon calcul ou ma proposition).
Les guides Netflix et BBC sont écrits pour le cinéma et la télé. Aucun ne parle des reels. Je dis à chaque fois ce qui se transfère et ce qui ne se transfère pas.

---

## L'idée en 5 lignes

1. La taille actuelle (52 px) est au bon endroit. Le monteur humain est à ~57 px (mesuré), Victor à ~45 px, le BBC conseille 40-48 px à l'affichage sur un téléphone moyen (mon calcul à partir de son guide). On allège le poids visuel (graisse, ombre), pas la taille.
2. Le bas du texte peut descendre jusqu'à y = 1520 px, dans les 35 % du bas que Meta dit de laisser libres (y > 1248). La zone doit être 45 % à 60 %.
3. Les blocs de Victor (mesurés) : 1 ligne, 2 à 6 mots, 0,4 à 1,75 s chacun, sans aucune animation d'entrée. Ceux du monteur humain : 2 à 4 mots, majuscules.
4. Les guides officiels disent : 20 caractères par seconde au maximum (Netflix), 160-180 mots/min (BBC), 130-160 mots/min (DCMP), et une étude de 2018 montre que 20 caractères/s ne gênent pas la compréhension. Un reel dépasse souvent 200 mots/min : c'est la limite.
5. Le guide DCMP dit que la casse mixte se lit mieux et que les majuscules sont pour "crier". Je garde les majuscules, avec blocs courts.

Sauf deux points qui évitent un reel raté : la zone du bas (2) et zéro faute de transcription. Le sous-titre aide la rétention (+12 % de temps vu chez Meta, tests internes), pas la conversion directement.

---

## Les experts et sources retenus

| Source | Pourquoi crédible (1 ligne) | Ce qu'on a lu |
|---|---|---|
| **Netflix, English Timed Text Style Guide** | Guide officiel du plus gros diffuseur de sous-titres. | Page entière + "General Requirements" + "Subtitle Timing Guidelines". |
| **BBC Subtitle Guidelines** | Guide officiel du diffuseur public britannique, avec une version spéciale pour la vidéo verticale 9:16. | Page entière téléchargée, sections 3 (lignes), 4 et 5 (durée, synchro), 9.2 (taille), 10 (position) lues. |
| **DCMP, Captioning Key** | Guide américain de référence du sous-titrage pour sourds et malentendants. | Page d'accueil + section "Presentation Rate". |
| **W3C, WCAG 2.1** | Norme internationale d'accessibilité. | Critères 1.4.3 (contraste) et 1.2.2 (sous-titres). |
| **Szarkowska et Gerber-Morón, PLOS ONE 2018** | Étude publiée, eye-tracking, "Viewers can keep up with fast subtitles". | Environ 75 % de l'article (résumé par outil). |
| **Legge et Bigelow, Journal of Vision 2011** | Revue scientifique de référence sur la taille de lecture. | Environ 69 % de l'article (résumé par outil). |
| **Meta (pubs)** | Annonceur, tests internes. | Pages "Updated Features for Video Ads" et "Reels ads". |
| **Wampus, Isaac** | Recoupés avec leurs vidéos. | Passages sur les sous-titres, le texte et l'animation. |

---

## Les mesures sur 3 références (reels réels)

Méthode : image extraite en 1080x1920, fenêtre de la zone de sous-titre, boîte englobante des pixels clairs. Les sources 720x1280 sont agrandies : précision environ ±10 %. Durées des blocs relevées toutes les 0,25 s sur 8 s de reel 04 et 05. [P mesure locale]

| Reel | Casse et graisse | Hauteur du texte | Police estimée | Position (centre) | Mots par bloc | Durée d'un bloc | Animation d'entrée |
|---|---|---|---|---|---|---|---|
| Victor 05, selfie, 87 k | minuscules, gras | 35-47 px (ascendantes + descendantes) | ~44-47 px | y ≈ 648 px (34 %), au-dessus du visage | 2 à 6 | 0,75 à 1,75 s | aucune (coupe sèche, 1 image vide) |
| Victor 04, studio, 171 k | minuscules, fin | 31-56 px | ~45-47 px | y ≈ 985 px (51 %) | 2 à 6 | 0,4 à 1,5 s | aucune |
| Victor 06, studio, 58 k | minuscules | 36-53 px | – | y ≈ 990 px (52 %) | – | – | – |
| Monteur humain (FINAL.mp4) | MAJUSCULES | hauteur de capitale 40 px | ≈ 57 px (capitale Montserrat = 0,70 em) | y ≈ 1175 px (61 %), sur le t-shirt | 2 à 4 | – | – |

Vitesse de lecture mesurée chez Victor : "que has hecho todo este año" 27 caractères en 1,5 s = 18 car/s ; "y terminar este año" 19 car en 1,0-1,25 s = 15-19 car/s ; "Hacer la misma mierd*" 21 car en 1,5-1,75 s = 12-14 car/s. [P mesure]

---

## Les règles (groupées)

### A. Longueur d'un bloc
- Netflix (cinéma) : 42 caractères par ligne, 2 lignes maximum, de préférence une ligne. Coupures : après la ponctuation, avant les conjonctions et les prépositions. Garder ensemble nom + article, nom + adjectif, prénom + nom, verbe + pronom sujet. [P] https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-Timed-Text-Style-Guide (I.10 et II.13).
- BBC pour la vidéo verticale 9:16 : 90 % de la largeur au maximum, soit l'équivalent de ~25 caractères par ligne ; 3 lignes maximum. [P] BBC 3.1 et 3.3 (https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/).
- Mesuré : blocs de 2 à 6 mots chez Victor, 2 à 4 chez le monteur humain. [P mesure]
- Wampus : "caractère par bloc réglé à 8", pour éviter le style mot par mot dans l'outil. [P] Y7M6z4WN27g [34:25]. (Je n'ai lu que ce passage-là.)

### B. Durée et vitesse
- BBC : 160 à 180 mots/min, soit 0,33 à 0,375 s par mot. Durée minimale d'un bloc : environ 0,3 s par mot (1,2 s pour 4 mots), à raccourcir seulement si une coupe d'image l'impose. [P] BBC 4 et 4.1.
- BBC : garder des durées cohérentes d'un bloc à l'autre. [P] BBC 4.4.
- Netflix (cinéma) : 20 caractères par seconde pour les adultes (17 pour les enfants). Durée minimale 5/6 s (20 images à 24 i/s), maximale 7 s. Écart minimal entre deux sous-titres : 2 images, quelle que soit la cadence. Le minimum de 5/6 s est prévu pour les sous-titres d'un ou deux mots. [P] Netflix, "General Requirements" et "Subtitle Timing Guidelines".
- DCMP : maximum 130, 140 ou 160 mots/min selon le niveau du public, à ne pas dépasser. Il est possible d'afficher les sous-titres 15 images avant ou après l'audio ("à peine perceptible"). [P] https://dcmp.org/learn/captioningkey/601
- Étude 2018 : à 12, 16 ou 20 caractères/s, la compréhension ne change pas. À 12 car/s, les gens relisent environ 2 sous-titres lents sur 3, contre 1 sur 5 pour les rapides. Les auteurs jugent le temps d'affichage de la règle des 6 secondes "inutilement long pour les spectateurs modernes". [P] Szarkowska et Gerber-Morón, PLOS ONE (https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199331).
- Mesuré chez Victor : 12 à 19 caractères/s. [P mesure]

### C. Synchronisation
- Le bloc apparaît quand la parole commence et disparaît à peu près quand elle finit : un sous-titre qui reste trop longtemps est relu. [P] BBC 5.1.
- Ne jamais anticiper la parole de plus de 1,5 s, ni rester plus de 1,5 s après. Jamais plus de 2 s de retard. [P] BBC 5.2 et 5.4.
- Un sous-titre doit être à l'écran tant que les lèvres bougent. [P] BBC 5.3.
- Écart entre deux blocs : 2 images minimum (Netflix), ou ≥ 0,5 s. Victor : 1 image vide, coupe sèche. [P] Netflix + mesure.

### D. Taille, position, contraste
- BBC, vidéo 9:16 : hauteur de ligne de 3,9 à 4,5 % de la hauteur de l'image = 75 à 86 px en 1920. Avec une interligne de 120-125 % (exemples du guide), ça donne une police de 60 à 72 px (mon calcul **[H]**). C'est la taille "d'écriture". À l'affichage sur un téléphone de 5,5 pouces, le guide conseille de la réduire à ×0,67, soit 40 à 48 px ; sur un petit téléphone, ×1. [P] BBC 9.2.1 et 9.2.2.
- BBC : sous-titres dans les 75 % centraux de la hauteur et les 90 % centraux de la largeur (vidéo 9:16). Les sous-titres d'une vidéo verticale sont placés un peu plus haut, dans le tiers du bas, parce que les visages sont dans la moitié du haut. Ne pas cacher la bouche. [P] BBC 10 et 10.1.
- Meta (pubs) : laisser libres le haut 14 % (269 px), le bas 35 % (y > 1248 px) et les côtés 6 % (65 px). [P pubs] Meta Ads Guide, Instagram Reels. Pour l'organique, rien d'officiel : **[H]**.
- Taille de lecture : taille critique d'impression ≈ 0,2° de hauteur d'x (consensus, plage 0,15-0,3°). Lecture fluide entre 0,2° et 2°. À 40 cm, 0,2° = 1,4 mm. [P] Legge et Bigelow, PMC3428264.
- Contraste : texte normal ≥ 4,5:1 ; grand texte (18 pt, ou 14 pt gras) ≥ 3:1. [P] https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
- Sous-titres : ne pas cacher une information utile de l'image. [P] WCAG 1.2.2.
- Netflix : police sans empattement proportionnelle (Arial), blanche. Taille calculée pour tenir 42 caractères en largeur. [P] Netflix I.7 et II.9.
- BBC : fond noir par ligne avec 0,5 em de marge de chaque côté, sans trou entre deux lignes. [P] BBC 9.2.4.

Mon calcul pour le téléphone (**[H]**, hypothèses : écran de 65 mm de large soit 0,060 mm par pixel de reel, lecture à 40 ou 50 cm) :

| Police Montserrat (capitales) | Hauteur capitale | Angle à 40 cm | Angle à 50 cm | Hauteur d'x en minuscules | Angle à 50 cm |
|---|---|---|---|---|---|
| 44 px | 30,8 px = 1,9 mm | 0,27° | 0,21° | 22,8 px | 0,16° |
| 48 px | 33,6 px = 2,0 mm | 0,29° | 0,23° | 24,8 px | 0,17° |
| 52 px (actuel) | 36,4 px = 2,2 mm | 0,31° | 0,25° | 26,9 px | 0,19° |
| 57 px (monteur humain) | 39,9 px = 2,4 mm | 0,34° | 0,28° | 29,5 px | 0,20° |

Lecture : en capitales, la limite de 0,2° est atteinte vers 44 px à 50 cm. En minuscules (hauteur d'x), c'est dès 57 px à 50 cm. Les capitales semblent donc plus sûres que le style de Victor pour des yeux de 40-50 ans, à police égale. Attention : la taille critique de Legge est mesurée sur la hauteur d'x des minuscules. La transposer aux capitales est mon hypothèse. La vraie marge est entre 48 et 52 px.

### E. Mise en valeur et animation
- Colorer certains mots parce que "l'attention dure 5 secondes". [P] Wampus Y7M6z4WN27g [34:25].
- Ne pas mettre de texte partout : un texte qui "pop" toutes les secondes devient irritant. Du texte seulement quand c'est important. [P] Isaac ciAywjey0cY [12:57].
- Animation de texte d'Isaac : départ à 70 %, 110 % sept images plus tard, retour à 100 % cinq images après. [P] ciAywjey0cY [13:40]. (Sa cadence d'images n'est pas dite dans le passage lu.)
- Mesure : Victor n'anime pas ses sous-titres : un bloc remplace l'autre sur une image. [P mesure]
- DCMP : la casse mixte se lit mieux. Les capitales sont réservées au cri. [P] https://dcmp.org/learn/captioningkey (section 3, "Text").
- Affichage mot par mot : en sous-titrage en direct, il aurait fait passer environ 90 % du temps de regard sur le texte et 10 % sur l'image (Romero-Fresco). D'où l'idée d'afficher le bloc entier d'un coup, comme Victor. **[S]** : trouvé dans un résumé de recherche, je n'ai pas ouvert l'étude.

### F. Sans le son
- Tests internes Meta : les vidéos avec sous-titres gagnent en moyenne 12 % de temps de visionnage. 41 % des vidéos testées n'avaient presque plus de sens sans le son. [P pubs] https://www.facebook.com/business/news/updated-features-for-video-ads

---

## Ce que je n'ai pas trouvé

- Une zone sûre officielle d'Instagram pour les reels organiques. Seulement celle des pubs de Meta.
- Un guide officiel de sous-titrage spécifique aux reels ou au format court. Netflix et BBC parlent de cinéma et de télé (le BBC a une partie vidéo verticale, la seule officielle trouvée).
- Un expert reconnu des sous-titres animés de reels qui donne des chiffres autres que Wampus et Isaac. Les tutoriels "style Hormozi" que j'ai croisés sont des tiers sans crédit (non lus, non utilisés).
- Une étude sur les majuscules contre la casse mixte pour des sous-titres courts de vidéo verticale. Je n'ai que le guide DCMP.
- Une étude sur le sous-titrage mot par mot de reels avec eye-tracking : un résumé de recherche cite une étude de Romero-Fresco sur le direct, que je n'ai pas ouverte ([S]).
- Le BBC "Subtitle Guidelines" : ses règles de position à l'écran dépendent d'un cadre "processeur de sous-titres" (tailles réduites selon l'écran). Mon calcul de 40-48 px est une transposition, pas une phrase du guide.
- La distance de lecture d'un téléphone (35-50 cm) et la largeur d'écran (65 mm) sont mes hypothèses. Legge et Bigelow prennent 40 cm comme exemple.
- Les pages Apple (taille de texte iOS) et Adobe (zones sûres Premiere) n'ont pas pu être lues (erreur 403 ou contenu vide).

---

## Tableau des sources

| # | Source + URL | Niveau | Sujet | % lu |
|---|---|---|---|---|
| 1 | Netflix, English Timed Text Style Guide https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-Timed-Text-Style-Guide | P | 42 car/ligne, 20 car/s, coupures, police | résumé des sections demandées (100 % des points cherchés) |
| 2 | Netflix, General Requirements https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617-Timed-Text-Style-Guide-General-Requirements | P | durée min 5/6 s, max 7 s | idem |
| 3 | Netflix, Subtitle Timing Guidelines https://partnerhelp.netflixstudios.com/hc/en-us/articles/360051554394-Timed-Text-Style-Guide-Subtitle-Timing-Guidelines | P | écart 2 images, coupes | idem |
| 4 | BBC Subtitle Guidelines https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/ | P | 160-180 mots/min, 9:16, taille, position | page entière téléchargée, ~20 % lue (sections utiles) |
| 5 | DCMP Captioning Key https://dcmp.org/learn/captioningkey et /601 | P | casse mixte, 130-160 mots/min | pages d'accueil + 601 |
| 6 | W3C, WCAG 2.1, 1.4.3 et 1.2.2 https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html | P | contraste, sous-titres | critères lus |
| 7 | Szarkowska et Gerber-Morón, PLOS ONE 2018 https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199331 | P | vitesse 12/16/20 car/s | ~75 % (résumé par outil) |
| 8 | Legge et Bigelow, "Does print size matter for reading?", J. Vision 2011, https://pmc.ncbi.nlm.nih.gov/articles/PMC3428264/ | P | taille critique 0,2°, plage 0,2-2° | ~69 % (résumé par outil) |
| 9 | Meta, "Updated Features for Video Ads" https://www.facebook.com/business/news/updated-features-for-video-ads | P (pubs) | +12 %, 41 % sans son | extraits cités lus |
| 10 | Meta Ads Guide, Instagram Reels https://www.facebook.com/business/ads-guide/update/image/instagram-reels | P (pubs) | zone sûre 14 / 35 / 6 % | confirmée par recherche, page non relue |
| 11 | Reels de Víctor Heras (ref/victor-heras 04, 05, 06) | P mesure | taille, position, durée de bloc | mesures de plusieurs images par reel |
| 13 | Wampus, Unedited Edits EP9 https://www.youtube.com/watch?v=Y7M6z4WN27g | P | mots colorés, 8 caractères | passages ciblés (~15 %) |
| 14 | Isaac, "How I Actually Edit Viral Videos" https://www.youtube.com/watch?v=ciAywjey0cY | P | texte, pop 70-110-100 | passages ciblés (~20 %) |
| 15 | Résumé de recherche citant Romero-Fresco (UAB) sur le mot par mot en direct | S | 90 % du regard sur le texte | non ouvert |
