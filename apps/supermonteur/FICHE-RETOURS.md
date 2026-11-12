# Fiche retours : corriger vite (notes locales)

Collée dans la consigne de l'ouvrier de SuperMonteur (Claude Sonnet, sans chat) à chaque « Suivant : corrige mes retours ». But : la version
suivante en moins de 2 min. Tu modifies les fichiers, le serveur remonte la vidéo et répond à l’utilisateur tout seul.

## Ce que tu touches (1 seul fichier dans le cas courant)
- `<dossier>/retouche.json` (fichier neuf, Write) : `{"plan": {<les clés de plan.json qui changent>}, "reponses": {"<id>": "..."}}`.
  Le serveur fusionne `plan` dans plan.json (objets imbriqués fusionnés, `null` = retirer la clé, une liste se donne en entier)
  et note feedback-retours.md lui-même. Ex. titre plus gros : `{"plan": {"title": {"size": 72}}, "reponses": {"6": "..."}}`.
- `<dossier>/words.json` : les mots des sous-titres (`{"words": [{"text", "start", "end"}, ...]}`), temps du montage (Read + Edit).
- Couper un mot : clé `"couper": [<numéros #k de words.json>]` dans retouche.json (jamais drop.json : le serveur s'en charge).
Rien d'autre (jamais cut.segments.json ni les fichiers du dérush : le serveur les remet tels quels). Aucune commande.

## Les champs de plan.json
- `title` : `{"l1": "...", "l2": "...", "start": 0, "end": 999, "top": 350}`. 2 lignes de longueur proche, une seule taille,
  la promesse forte du reel (jamais la 1re phrase coupée en 2). Pas de virgule, point ni deux-points. Nombres en chiffres
  (« +35 ans »). `top` = hauteur en px (plus grand = plus bas). Pas de titre = retirer la clé `title`.
- `fixes` : `{"mot faux": "mot juste"}` change CHAQUE occurrence dans les sous-titres. Un mot courant (« dis », « la ») :
  corrige-le dans `words.json` à son indice, pas dans `fixes`.
- `subMax` : nombre de mots max par sous-titre (3 = court).
- `couleurs` : `[{"mot": "live", "couleur": "#FFD60A", "ecrit": "Live", "start": 20, "end": 25}]` = CE mot du sous-titre en
  couleur (même police, même taille), écrit comme `ecrit` (majuscule, orthographe). `start`/`end` (s, optionnels) = seulement à
  cet endroit. Marche AVEC un titre et en montage rapide. Jaune par défaut #FFD60A.
- `music` : `{"src": "<fichier>", "from": <seconde de départ dans le morceau>, "target": <niveau sous la voix, LUFS>, ...}`.
  `target` absent = niveau du dernier mix (donné dans la consigne, souvent -32). Plus bas = plus négatif. Pas de musique = retirer `music`.
- `music_zones` : `[{"from": 2.9, "to": 7.0, "db": -4}]` = la musique change de `db` SEULEMENT entre from et to (secondes du
  montage). Une liste se donne en entier : recopie les zones déjà là. Le son seul est refait (~20 s).
- `typo` : style du texte (couleurs, ombre). Ne l'ajoute que si l’utilisateur demande une couleur ou une ombre.
- `subY` : hauteur des sous-titres en px (1100 à 1340). Absent = calculé sur la vidéo.
- `duree_min` : 0 = pas de règle « plus d'1 minute ».
- Le reste (`cam`, `words`, `da`, `cases`, `style_supermonteur`, `_note`) : ne pas toucher.

## Cas courants
- « faute dans le sous-titre » : `fixes` (ou `words.json` pour un mot courant).
- « mets ce mot en jaune / en couleur », « avec une majuscule » : `couleurs` (et `ecrit` pour la majuscule). Toujours faisable.
- Un point ou une virgule entre 2 chiffres dans le titre (« 5.2 », « 1,5 ») reste tel quel : écris-le normalement.
- « titre » (texte, place) : `title.l1` / `title.l2` (texte) ou `title.top` (place).
- « titre plus gros / plus petit » : `title.size` en px (un nombre = les 2 lignes). Sans `size`, c'est la DA (souvent 62) :
  +15 % par demande (62 -> 72 -> 82). Le titre reste TOUJOURS sur 2 lignes (jamais 3) : la consigne te donne sa taille
  actuelle et sa taille max avec ce texte, et quoi faire si le max est trop proche pour que ça se voie.
- « sous-titres trop longs » : `subMax` à 3.
- « musique » : autre `from` (temps fort) ; un autre morceau seulement s'il le demande.
- « musique plus basse / plus forte » SANS moment précis (t = 0) ou avec « partout », « toute la vidéo » : `music.target` -4 / +4
  (ex. -32 -> -36). Le son seul est refait (~20 s), l'image reste.
- « coupe ce mot », « enlève le euh », « coupe le "en fait" » : `"couper": [#k, ...]` (12 mots max), numéros de la ligne
  « note LOCALE » ou de words.json. Le serveur recoupe le rush et remonte (~3 min).
- « cut plus serré » partout, « bug ici » sur une coupe, « enlève cette phrase » longue : c'est le dérush, pas faisable ici.
  Réponds `"pas fait : dérush (coupe à <t> s), à refaire dans le chat"`. Le serveur le laisse à faire, bien visible.

## Note posée à un moment précis (t > 0, ligne « note LOCALE ») : ne change QUE ce moment
Méthode de l’utilisateur : seules les notes sont retouchées, le reste de la vidéo ne bouge pas.
- Musique (« baisse la musique ici », « trop fort là ») : `music_zones` sur la fenêtre donnée (`db` -4 / +4), JAMAIS
  `music.target`. « À partir d'ici » = de t à la fin (to = 999). Réponse : « Musique baissée de 4 dB de a à b s seulement ».
- Titre (« enlève le titre ici ») : `title.start` / `title.end`.
- Mot (faute, mot à couper) : le mot #k de la ligne « note LOCALE ».
- Ce qui ne se règle que pour toute la vidéo (couleur, police, taille des sous-titres, hauteur des sous-titres, morceau de
  musique) : fais-le sur toute la vidéo ET dis-le : « fait sur toute la vidéo : le moteur ne sait pas le faire juste à cet endroit ».

## Temps du retour
`t` = seconde dans la version affichée. Le mot dit à cet instant = celui de `words.json` dont `start <= t < end`.
