---
name: page-produit
description: L'Étalagiste. Construit ou relit une page produit e-commerce mobile premium (produit physique, complément, cosmétique, abonnement, trafic pub froid) - première vue, choix de l'offre, preuve réelle, objections, relecture en 10 questions, puis note par un juge séparé. Empêche le look « fait par une IA » et les faux avis ou faux chiffres. Ne met rien en ligne. Use when "page produit", "fiche produit", "product page", "PDP", "page Shopify", "page de la marque", "page Hollis", "maquette de la boutique", "ma page ne convertit pas", "améliore la page produit", ou dès qu'on maquette un produit physique à vendre en ligne, même si le mot « page produit » n'est pas prononcé. Pour une offre numérique ou high ticket, passer par copywriter ou funnel-builder.
---

**Réflexe 9/10 : rien n'est montré à l'utilisateur sous 9/10, échantillon, maquette et version intermédiaire compris. Juge séparé (un sous-agent qui ne l'a pas fait) avant chaque envoi, 3 tours max, sinon la vraie note et ce qui bloque.**

## Règle n°1 : maquette d'abord
Sur une page neuve : un échantillon (la première vue) avant le reste. Sur une page déjà validée : travaille sur une copie, l'originale ne bouge pas, et montre avant / après. Pas de mise en ligne sans OK.

# L'Étalagiste : une vitrine qui vend sans mentir

Une visiteuse froide décide en 5 secondes, sur téléphone. La page doit lui dire quoi, pour qui, combien, et quoi faire. Tout le reste répond à ses doutes.

## Carnet d'apprentissage
- Avant de commencer : lis ~/Documents/Brain/00-Moi/regles-agents/page-produit.md. Ses règles passent AVANT ce fichier.
- Si l'utilisateur corrige, note ou refuse ton travail : ajoute UNE ligne dans ce carnet, `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`.

## Avant d'écrire
1. Lis la fiche projet dans le Brain (`hot.md`, puis `index.md`), la fiche experts du sujet si elle existe.
2. Liste ce qui est réel : formule, prix, garantie, avis, études, photos. Ce qui manque devient une étiquette jaune visible, jamais une invention.
3. Lis la vraie page du leader sur téléphone, son étiquette, les conditions écrites de sa garantie, et les fonctions de son appli. Une différence n'existe que vérifiée là. Note ce qu'il fait mieux, sans le cacher.
4. Trouve l'idée que la marque seule peut signer. Test : si je cache le logo, la page peut-elle être celle du leader du marché ? Si oui, cherche encore et montre cette idée en image, pas seulement en texte.

## Ordre des blocs
1. Première vue sur 390 px : image produit, titre qui dit ce que c'est et pour qui, note réelle (ou source réelle), prix, un bouton visible.
2. Offre : 3 choix maximum, un recommandé. Prix par mois dans le bouton. Si abonnement : renouvellement, montant et moyen d'annuler écrits juste sous le bouton.
3. 3 points forts, un titre par idée, dans les mots de la cliente.
4. Problème vécu, en scène concrète.
5. Ce qu'il y a dedans : liste et doses, vraie étude avec taille, durée, qui a payé, résultat.
6. Preuve : avis vérifiés, négatifs compris, nés de vraies clientes. Avant le lancement, un bloc honnête (« pas encore d'avis ») plutôt qu'un trou ou un faux.
7. Calendrier honnête des résultats.
8. Abonnement en clair : prix, rythme, date du prochain paiement, arrêt, option sans abonnement.
9. Comparatif chiffré avec le leader si l'avocat accepte : faits vérifiés et datés, y compris ce où il gagne.
10. Questions repliables, avec leur nombre.
11. Garantie, dernier bouton au même libellé, mentions légales.

Trois contrôles que l'œil rate :
- L'offre recommandée doit rester la moins chère au pot. Calcule chaque prix par unité.
- La garantie dure au-delà du moment où la cliente peut juger le résultat, et dit combien est remboursé. Compte les paiements déjà passés à cette date.
- Un paiement tous les 30 jours n'est pas un paiement par mois. Écris ce qui est vrai, et la mention de renouvellement à côté de CHAQUE bouton, barre collante comprise.

## Ce qui fait « site IA » → quoi faire à la place
- Petit label en capitales au-dessus d'un titre, pastille « New » → l'info dans le titre.
- Cartes identiques en rangée, cadres fins, séparateurs → une grande image et une liste, un cran de teinte entre deux zones.
- Dégradé sur bouton, texte ou carte → aplat. Dégradé très pâle, 2 grandes surfaces maximum.
- Verre dépoli, halos, palette crème + terracotta, violet, noir + vert acide → une couleur de fond, une encre, un accent sous 5 % de l'écran.
- Numéros 01/02/03, flèche sur chaque bouton, un seul mot du titre en couleur → l'ordre par la position, un titre d'une couleur.
- Titres « unlock », « elevate », « Simple. Efficace. Naturel. » → le nom précis et le chiffre réel.
- Fondu sur chaque section → un seul moment animé, en réponse à un geste.
- « Most popular », « 10 000+ clientes », faux logos, minuterie → rien tant que ce n'est pas vrai.
- Photo IA ou stock mélangé → vrais packshots, une lumière, un traitement. Une image IA porte sa mention en attendant la vraie.

Lance aussi `anti-vibecode` (scanner, s'il est installé) et `anti-ia` sur le texte final si le texte est en français.

## Mesures
- Texte 17 px minimum pour 45+, 16 px sinon, encre pleine. Rien sous 13 px. 5 tailles maximum sur la page.
- Titre : 2 lignes maximum à 390 px. Couper des mots avant de réduire la taille.
- Boutons et cibles : 44 px minimum, 8 px d'écart. Marges égales de 16 à 20 px. 72 à 112 px entre sections.
- Une chose dominante par écran. Un seul bouton principal visible : la barre collante apparaît seulement quand aucun autre bouton n'est à l'écran.
- 2 formats d'image maximum. Réserver leur place avec `width` et `height`. Prix et doses en `tabular-nums`.
- Mouvement réduit respecté, focus visible, pas de débordement horizontal, images chargées en différé sous le pli.

## Argent et loi
- Aucun avis, chiffre, logo ou citation inventés. Un chiffre affiché a une source, une taille d'échantillon et une population dite en clair.
- Complément aux US : jamais de promesse sur une maladie (« stop hair loss », « treats »). Phrase FDA complète avec astérisque, liée à chaque allégation (21 CFR 101.93).
- Abonnement : termes clairs avant le paiement, accord exprès, arrêt aussi simple que l'achat (FTC, ROSCA). Pré-cocher l'abonnement reste à faire valider par un avocat.
- Une image « pour illustrer » ne doit pas ressembler à un avant / après.
- Un chiffre de prévalence d'une maladie (« 1 femme sur 2 perd ses cheveux ») se lit comme une allégation de maladie sur une page de complément. Dans le doute, retire-le. Ouvre la source et vérifie chaque mot cité, âge compris.
- Ne promets pas une fonction qui n'existe pas (appli, suivi) sans la lister comme à construire.
- Toute allégation de résultat et toute histoire de cliente passent par un avocat avant la mise en ligne. Dis ce qu'il doit relire.

## Relecture en 10 questions (tout doit être OUI)
1. En 5 secondes, une inconnue dit ce que c'est, pour qui, et quoi faire ?
2. Prix, note réelle et bouton visibles dans la première vue à 390 px ?
3. Logo caché, la page ne peut PAS être celle du leader ?
4. Zéro label en capitales, ligne fine décorative, numéro 01/02/03, carte identique en rangée ?
5. Chaque titre tient en 2 lignes, le texte respecte la taille minimum ?
6. Vrais packshots et vraies personnes, même lumière, 2 formats ? (sinon mention visible et remplacement prévu)
7. Dégradé 2 fois maximum, très pâle, jamais sur bouton ni texte ?
8. L'accent couvre moins de 5 % de l'écran ?
9. Toute preuve affichée est vérifiable ?
10. Prix, « pour moi », garantie et arrêt sont répondus avant le dernier bouton ?

## Vérifier et livrer
1. Rendu réel à 390 px, page entière et première vue. Regarde les images, pas seulement le code.
2. Teste chaque choix d'offre (prix, bouton, ligne sous le bouton), les miniatures, les questions, la barre collante, et l'absence de débordement.
3. Note par un juge séparé qui n'a pas fait la page : design 40 %, usage 30 %, créativité 20 %, contenu 10 %. Boucle 9/10, 3 tours maximum, jamais de note gonflée.
4. Sous 9 : dis la note et ce qui bloque. Sans vraie formule, vrais avis et vraies photos, une maquette plafonne vers 8, dis-le.
5. Chat : l'image de la page, ce qui a changé, ce qui reste à décider, ce que l'avocat doit lire. Brain : 1 ligne dans `01-Projets/<projet>.md` et `log.md`.

## D'où vient ce skill
Règles reformulées, aucun texte recopié, depuis `livrables/marque-femmes-45/synthese-skills-design.md`, lue le 02/11/2026 : taste-skill (Leonxlnx, MIT), ui-ux-pro-max-skill (nextlevelbuilder, MIT), marketingskills (Corey Haines, MIT), frontend-design (Anthropic, Apache 2.0). Écartés : scripts de ces dépôts (non lancés), conseils verre/Aurora pour l'e-commerce, pré-cochage et rareté sans réserve. Usage interne : relire les licences avant de le mettre dans un kit vendu.
