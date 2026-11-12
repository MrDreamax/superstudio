---
description: "Motion design des reels : easing GSAP, durées, Ben Marriott, NN/g."
type: formation
statut: actif
sujets: [montage]
---
# Experts : motion design (reels 9:16 face cam)

Date : 2026-10-13.
Niveaux : [P] primaire (guide officiel, ou l'expert lui-même) · [S] secondaire (un tiers décrit) · [H] hypothèse (ma proposition, aucune source) · [C] calcul fait par moi à partir d'une source (voir "Courbes officielles en syntaxe GSAP").

## L'idée en 5 lignes
1. Entrée : "ease out" (démarrage vif, arrivée douce). Sortie : "ease in" (plus courte que l'entrée). Jamais linéaire, sauf une dérive très lente.
2. Les 4 sources officielles (GSAP, Google Material, IBM Carbon, Nielsen Norman) donnent des durées qui tiennent dans 100 à 500 ms, jusqu'à 700 ms pour les grands mouvements. Ton moteur est déjà dans cette zone presque partout.
3. Ce qui manque au moteur : (a) aucune sortie douce (tout disparaît à la coupe) ; (b) un rebond `back.out(2)` sur les pastilles, alors que ta charte dit "jamais de rebond".
4. Ben Marriott : un petit mouvement inverse avant le grand (anticipation) dirige l'œil. On le garde pour les moments héros seulement, très petit.
5. Un seul mouvement important à la fois : on guide le regard, on ne le disperse pas.

## Les experts retenus
- **GSAP (doc officielle)** : la bibliothèque du moteur. Lu : 2 pages (extraction).
- **Google, Material Design 3** (via le dépôt officiel material-components-android) : durées en ms, courbes en cubic-bezier. Lu : page "Motion" (extraction).
- **IBM Carbon** (guide officiel) : durées, courbes "productive" et "expressive". Lu : page "Motion overview".
- **Nielsen Norman Group** (cabinet de recherche en UX, article "Executing UX Animations: Duration and Motion Characteristics") : durées 100-500 ms, entrée contre sortie. Lu : page entière (extraction).
- **Ben Marriott** : motion designer et formateur (Sydney), cours "Master Motion Design" ; environ 10 ans de métier selon des pages tierces, liste de clients NON trouvée [S]. Lu : 3 vidéos (anticipation, match cut, transition).
- **Jake Bartlett** : formateur After Effects depuis plus de 10 ans, 30+ cours Skillshare, "Lead Educator" chez Battle Axe depuis 2022 (profil Adobe, School of Motion) [S]. Lu : 2 vidéos (graph editor, courbes).
- **School of Motion** : école de motion design ; vidéo d'intro sur les 12 principes (paraphrase de "The Illusion of Life", livre non lu) [S].
- **Issara Willenskomer** ("UX in Motion") : plus de 20 ans, projets de motion pour de grandes marques (biographie UX Magazine) [S]. Lu : l'article "UX in Motion Manifesto" : AUCUN chiffre en ms.

## Courbes officielles en syntaxe GSAP (mon calcul [C])
Méthode : j'ai pris chaque `cubic-bezier` officiel, calculé sa courbe, et cherché l'ease GSAP intégré le plus proche (erreur moyenne sur 400 points ; plus c'est petit, mieux c'est ; sous 0,05 = très proche).
| Courbe officielle | Ease GSAP le plus proche | Erreur |
|---|---|---|
| Material standard-decelerate (0, 0, 0, 1) = "entrée" | `circ.out` ou `power3.out` | 0,019 / 0,049 |
| Material emphasized-decelerate (0,05 ; 0,7 ; 0,1 ; 1) = entrée "forte" | `expo.out` | 0,050 |
| Material emphasized-accelerate (0,3 ; 0 ; 0,8 ; 0,15) = sortie "forte" | `power2.in` | 0,025 |
| Material standard-accelerate (0,3 ; 0 ; 1 ; 1) = sortie | `sine.in` | 0,053 |
| Material standard (0,2 ; 0 ; 0 ; 1) = reste à l'écran | `power2.out` | 0,039 |
| Carbon productive "entrance" (0, 0, 0,38, 0,9) | `power1.out` | 0,016 |
| Carbon expressive "entrance" (0, 0, 0,3, 1) | `power2.out` | 0,048 |
| Carbon "exit" (0,2 ; 0 ; 1 ; 0,9) | `sine.in` | 0,062 |
| CSS ease-out (0, 0, 0,58, 1) | `sine.out` | 0,014 |
| CSS ease-in-out (0,42 ; 0 ; 0,58 ; 1) | `power1.inOut` ou `sine.inOut` | 0,006 / 0,012 |
Lecture simple : entrée douce = `power1.out` / `sine.out` ; entrée normale = `power2.out` / `power3.out` ; entrée forte = `expo.out` ; sortie = `power2.in`. La doc GSAP n'explique pas la force des `power1` à `power4` : cette table est donc la preuve chiffrée.

## Les règles (groupées, chacune avec sa source)

### A. Courbes
- **A1. GSAP : l'ease par défaut est `power1.out`. "Ease out" démarre vite, ralentit à l'arrivée : "le meilleur pour les transitions d'interface, car rapide au départ, donc réactif".** [P] https://gsap.com/resources/getting-started/Easing et https://gsap.com/docs/v3/Eases/ (familles : none, power1 à 4, back, bounce, circ, elastic, expo, sine, steps ; variantes in, out, inOut).
- **A2. Entrée = ease-out. Sortie = ease-in. Le linéaire paraît peu naturel. L'entrée dure un peu plus que la sortie : 300 ms pour apparaître, 200 à 250 ms pour disparaître.** [P] Nielsen Norman Group https://www.nngroup.com/articles/animation-duration/ (page entière).
- **A3. Material 3 : "decelerate" pour ce qui ENTRE à l'écran, "accelerate" pour ce qui SORT, "standard" pour ce qui reste à l'écran. "Emphasized" = les mêmes, plus marqués.** [P] https://raw.githubusercontent.com/material-components/material-components-android/master/docs/theming/Motion.md
- **A4. Carbon : "expressive" (visible) réservé aux "moments rares et importants" ; "productive" (discret) pour le reste.** [P] https://carbondesignsystem.com/elements/motion/overview/
- **A5. "Quand utiliser l'easing ? Toujours." Le linéaire paraît "inachevé, brusque, distrayant".** [P] Issara Willenskomer https://uxmag.com/articles/creating-usability-with-motion-the-ux-in-motion-manifesto (principe 1, "Easing").
- **A6. "Offset et delay" : des objets décalés dans le temps montrent qu'ils sont distincts (aucune valeur chiffrée).** [P] même article (principe 2).
- **A7. Niveau 1 : "easy ease" (F9). Niveau 2 : augmenter l'influence des poignées dans l'éditeur de courbes = beaucoup plus lisse et plus fort. L'easing, c'est la répartition des images : plus serrées au début et à la fin, plus espacées au milieu.** [P] Jake Bartlett https://www.youtube.com/watch?v=6zrEKEuJGKs [01:09]-[02:44] ; https://www.youtube.com/watch?v=7pOCtlrrE3Y [03:28]-[04:15].
- **A8. Sauf pour un effet très sec, les courbes doivent s'enchaîner sans angle vif.** [P] Ben Marriott https://www.youtube.com/watch?v=LcWJKYbYvi8 [09:04]-[09:19].

### B. Durées
- **B1. La plupart des animations : 100 à 500 ms. 100 ms = bas du perceptible (retour simple, case à cocher). 200 à 300 ms = changement d'écran important. 400 ms = "très lent", pour les grands mouvements. À 500 ms, "ça traîne".** [P] NN/g https://www.nngroup.com/articles/animation-duration/. Elles sont plus souvent trop longues que trop courtes.
- **B2. Material, jetons de durée : court 50, 100, 150, 200 ms ; moyen 250, 300, 350, 400 ; long 450, 500, 550, 600 ; très long 700, 800, 900, 1000. "La durée augmente avec l'aire et le trajet de l'animation."** [P] material-components-android docs/theming/Motion.md.
- **B3. Carbon, jetons : 70 ms (bouton), 110 (fondu), 150 (petits déplacements), 240 (toast, expansion), 400 (grande expansion), 700 (fond qui s'assombrit). Plus la distance ou l'échelle est grande, plus c'est long.** [P] https://carbondesignsystem.com/elements/motion/overview/
- **B4. Trois images suffisent à faire comprendre un mouvement ; l'anticipation peut durer presque 3 fois le mouvement principal quand on veut l'exagérer.** [P] Ben Marriott https://www.youtube.com/watch?v=LcWJKYbYvi8 [04:15]-[05:36] et [09:34]-[09:50].

### C. Anticipation et regard
- **C1. Anticipation = un petit mouvement qui précède le grand (ex. reculer avant de lancer). Elle dit au spectateur "regarde ici, quelque chose arrive". Ce n'est pas un rebond.** [P] Ben Marriott https://www.youtube.com/watch?v=LcWJKYbYvi8 [01:54]-[02:41] et [05:51]-[07:10] ("eye tracing" : tu contrôles où l'œil va).
- **C2. Pour faire disparaître un élément pendant une transition, le faire au moment du mouvement le plus rapide.** [P] Ben Marriott https://www.youtube.com/watch?v=UVDpgP7sRbw [06:29]-[06:44].
- **C3. Les 12 principes d'animation (Disney) : slow in / slow out, anticipation, follow through, arcs, timing, mise en scène... Source du livre "The Illusion of Life" (non lu).** [S] School of Motion https://www.youtube.com/watch?v=mT2Fv5bF6Ik [00:53]-[03:18].

## Ce que je n'ai pas trouvé
- **Issara Willenskomer : aucune durée en ms.** Son article UX Magazine donne les 12 principes sans chiffre ; l'article Medium d'origine est bloqué (403) ; son livre "UX in Motion" non lu.
- **"The Illusion of Life" (Thomas et Johnston) : extrait non obtenu.** Les 12 principes viennent de la paraphrase de School of Motion [S] (livre non lu, Google Books sans quota).
- **GSAP** : la doc ne dit pas la force de `power1` à `power4` ni les paramètres de `back` et `elastic` (pages lues). La table ci-dessus est mon calcul.
- **Aucune source donne des durées pour du texte animé en vidéo verticale.** Les chiffres de R1, R5, R6, R7, R9 sont des adaptations [H] des durées d'interface.
- Vidéos non lues : Ben Marriott "Master Motion Design" (EyHO1liVCpo), Jake Bartlett "Top Easing Tools" (IIBqi3K32c4), Issara "Live Q&A" (v7UG64yhYHc, 1 h).
- Pas de test A/B sur des reels réels : tout reste à valider.

## Tableau des sources
| # | Source + URL | Niveau | Sujet | % lu |
|---|---|---|---|---|
| 1 | GSAP, "Easing" https://gsap.com/resources/getting-started/Easing | P | in/out/inOut, `power1.out` pour l'UI | page entière, extraction automatique |
| 2 | GSAP, "Eases" https://gsap.com/docs/v3/Eases/ | P | familles, ease par défaut | page entière, extraction automatique |
| 3 | Google Material 3 (material-components-android, Motion.md) https://raw.githubusercontent.com/material-components/material-components-android/master/docs/theming/Motion.md | P | jetons de durée, courbes | fichier entier, extraction automatique |
| 4 | IBM Carbon, Motion https://carbondesignsystem.com/elements/motion/overview/ | P | jetons, productive / expressive | page entière, extraction automatique |
| 5 | Nielsen Norman Group, "Executing UX Animations" https://www.nngroup.com/articles/animation-duration/ | P | 100-500 ms, entrée / sortie | page entière, extraction automatique |
| 6 | Issara Willenskomer, "UX in Motion Manifesto" https://uxmag.com/articles/creating-usability-with-motion-the-ux-in-motion-manifesto | P | easing "toujours", offset et delay | article entier ; aucun chiffre |
| 7 | Ben Marriott, "The #1 Skill All Animators Need" https://www.youtube.com/watch?v=LcWJKYbYvi8 | P | anticipation, regard, courbes | environ 98 % |
| 8 | Ben Marriott, "This Animation Technique Works Every Time" https://www.youtube.com/watch?v=ythBGTLjot8 | P | match cut 100 à 105 % | environ 95 % |
| 9 | Ben Marriott, "After Effects Smooth Transitions pt.1" https://www.youtube.com/watch?v=UVDpgP7sRbw | P | retirer un élément au pic de vitesse | environ 63 % (jusqu'à 7:01 sur 11:09) |
| 10 | Jake Bartlett, "Beautiful easing curves in After Effects" https://www.youtube.com/watch?v=6zrEKEuJGKs | P | niveaux d'easing | environ 75 % (jusqu'à 7:20 sur 9:48) |
| 11 | Jake Bartlett, "The LAST graph editor tutorial you'll ever need" https://www.youtube.com/watch?v=7pOCtlrrE3Y | P | easing = répartition des images | environ 50 % (jusqu'à 12:49 sur 25:10, dont 2 min de sponsor) |
| 12 | School of Motion, "The Power of Animation Principles" https://www.youtube.com/watch?v=mT2Fv5bF6Ik | S | 12 principes (paraphrase) | environ 15 % (les 3 premières minutes utiles ; le reste = tutoriel After Effects) |
| 15 | guide-opus-motion-design-cassandre-rollet.md (durées, "non : rebonds") | P (déjà sourcé) | règles OPUS | relu, non modifié |
| 16 | Disney, "The Illusion of Life" | - | 12 principes | 0 % |
