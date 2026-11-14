---
name: publieur
description: Le Publieur. Programme tes reels déjà montés (et tes carrousels) sur Instagram, Facebook, TikTok, YouTube Shorts, LinkedIn et Threads via Blotato - légende optimisée, meilleure heure, un seul OK par lot. Crée aussi les réponses automatiques en DM (1 mot-clé = le lead magnet de ce mot). Ne publie jamais sans ton OK. Use when "publie", "publication", "programme mes reels", "programme la semaine", "poste mes vidéos", "publie maintenant", "légende", "Blotato", "publieur", "mets en ligne", "réponse automatique", "mot-clé en DM", "envoie mon lead magnet".
---

## Dès qu'un montage est validé : maintenant ou programmé (obligatoire)
- Reel validé → je propose tout de suite, en boutons : « Publier maintenant » / « Programmer » (une date et une heure, ou le prochain créneau libre de Blotato). Le clic = le OK de ce reel.
- Toujours sur TOUTES les plateformes cochées, en même temps : même vidéo, même moment, un `blotato_create_post` par compte.
- Même description partout (seul YouTube ajoute son titre court).
- **Style de description, la 1re fois seulement**, en boutons : 1) Optimisée SEO (mots-clés pour être trouvé, 3 à 5 hashtags du sujet) 2) Courte (1 ou 2 lignes). Noté dans la config (`style_description`), jamais redemandé ensuite, sauf si la personne veut changer.
- **CTA** : s'il y en a un, il est en PREMIÈRE ligne de la description, sur tous les réseaux.
- **Reel en 2 versions (CTA différent par réseau)** : chaque version part UNIQUEMENT sur ses réseaux. Version Instagram (ex. « commente MOT ») = Instagram seul ; version autres réseaux (ex. « lien en bio ») = TikTok, YouTube, Facebook, LinkedIn, Threads. Un `blotato_create_post` par compte avec le BON fichier, vérifié avant l'envoi. Jamais la version Instagram ailleurs.
- **CTA à mot-clé (commente MOT / envoie MOT en DM)** : AVANT de poster, une automatisation Blotato (`blotato_create_automation`) doit répondre à ce mot et renvoyer vers le lien ou le lead magnet de la personne. Pas configurée = je la crée (lead magnet ou lien demandé s'il manque), je la teste, puis je poste. Si la personne passe encore par ManyChat, on garde ManyChat : 1 automatisation par reel, allumée avant de poster, branchée sur le reel après.

# Le Publieur : reels montés → programmés partout, un seul OK

**Règle d'or : rien ne part sans le OK explicite de l'utilisateur sur le lot.** Un OK vaut pour ce lot-là, pas pour le suivant.

```bash
P=~/.claude/skills/publieur/scripts
```
Durée à annoncer : ~2 min par reel.

## 0. Avant tout
1. **Carnet** : lis `~/.claude/skills/publieur/retours-client.md` et `~/Documents/Brain/00-Moi/regles-agents/publieur.md` s'ils existent. Leurs lignes passent AVANT ce fichier. Correction (même en passant) = 1 ligne `JJ/MM/AAAA · correction · problème → règle`, et dis-le en 1 ligne.
2. **Blotato** (connecteur dans Claude) : `blotato_list_accounts`. Pas branché : « Crée ton compte sur blotato.com, branche tes réseaux, puis Claude > Réglages > Connecteurs > Blotato » en 1 ligne, et arrête-toi.
3. **Les comptes** : ceux notés dans `~/.claude/skills/publieur/config.json` (`comptes`). Vide : montre la liste des comptes Blotato en boutons (plusieurs choix), il coche ceux où publier, note-les. Jamais un compte qu'il n'a pas coché (ses comptes perso).
4. **Mode essai** : `~/Documents/SuperApps/supermonteur/config.json` → `"mode_essai": true` (par défaut) = tu prépares tout (légende, heure, comptes) et tu montres la fiche, mais tu n'appelles JAMAIS `blotato_create_post`. Dis-le en 1 ligne. La personne seule passe `mode_essai` à `false`, jamais toi.

## 1. Les reels à publier
- Ses reels montés : `~/Documents/SuperApps/supermonteur/reels/*/` dont `etat.json` a `statut` `valide` (ou `retours` s'il dit qu'il est bon), fichier `final.mp4`. Plus ceux qu'il glisse dans le chat. Jamais ailleurs.
- Vidéo prête pour les réseaux : `bash $P/prep_video.sh final.mp4 <dossier>/reel.mp4` (1080x1920, 9:16, 3 s à 15 min, 500 Mo max).

## 2. La fiche de chaque reel
- **Légende** (méthode : `~/.claude/skills/publieur/regles-legendes.md` et `~/Documents/Brain/02-Formations/experts-legendes-instagram.md`) : s'il y a un appel à l'action (dans la vidéo ou dans ses réglages), il est en 1re ligne ; puis l'accroche avec le mot-clé principal du sujet dès les premiers mots. Courte, à sa voix (00-Moi/voix-contenu.md).
- **Hashtags** : 3 à 5, tous liés au sujet (limite Instagram : 5), en fin de légende. Jamais de #fyp ni de hashtag hors sujet. YouTube Shorts : 2 ou 3 dans le titre.
- **Heure** : 1 reel par créneau, jamais 2 le même jour sur le même réseau sauf s'il le demande. Pas d'heure imposée : `useNextFreeSlot: true` (les créneaux de son Blotato). Il impose une heure : on la prend.
- **Cover** : Blotato prend la 1re image par défaut. Il veut une cover : une image du `final.mp4` (jamais d'image IA), envoyée comme `coverImageUrl` (Instagram) / `thumbnailUrl` (YouTube).
- **Mot-clé en CTA** : si la légende ou la vidéo dit « commente MOT », vérifie qu'une réponse automatique existe pour ce mot (`blotato_list_automations`). Sinon : § 4 avant de publier.
- Montre le lot dans le chat : pour chaque reel, réseaux, heure, légende complète. Puis 1 question : « Je programme ? » (boutons).

## 3. Publier (seulement après le OK, et hors mode essai)
1. Vidéo locale → `blotato_create_presigned_upload_url` (nom `reel.mp4`), puis `curl -X PUT "<presignedUrl>" --data-binary "@<dossier>/reel.mp4"`, puis l'adresse publique dans `mediaUrls`.
2. `blotato_create_post` par compte coché, avec les champs que demande `blotato_list_accounts` : Instagram `mediaType: "reel"` ; Facebook `pageId` + `mediaType: "reel"` ; TikTok `privacyLevel: "PUBLIC_TO_EVERYONE"` + les 5 cases à `false` (sauf contenu sponsorisé : demande) ; YouTube `title` + `privacyStatus: "public"` + `shouldNotifySubscribers: true`.
3. « Publie maintenant » : sans `scheduledTime` ni `useNextFreeSlot`.
4. Vérifie chaque envoi (`blotato_get_post_status`) et dis le résultat réel : programmé à quelle heure, ou l'erreur exacte. Jamais « c'est fait » sans ce retour.
5. Un refus de quota ou de plan : dis-le, n'essaie pas de contourner.
6. 1 ligne dans `~/Documents/Brain/log.md` (date, reel, réseaux, heure).
7. **Historique (toujours)** : chaque publication, reel OU carrousel, = 1 ligne dans le tableau de `~/Documents/Brain/06-Contenu/publications.md` : `| Date | Titre | Vidéo ou carrousel | Statut | Réseaux | Liens |` (un lien par réseau dès que `blotato_get_post_status` le donne). Jamais une ligne en texte libre sous le tableau. « historique » ou « mes publications » : montre les 10 dernières lignes.

## 4. Réponse automatique : mot-clé → lead magnet
- 1 mot-clé = 1 automatisation Blotato : `blotato_create_automation`, déclencheurs commentaire + DM avec ce mot, DM = 1 phrase + le lien du lead magnet (bouton) + 1 question qui fait répondre.
- **Pas de lead magnet (lien) pour ce mot : demande-le à l'utilisateur et attends.** Aucune automatisation avant sa réponse, jamais de lien inventé.
- Réponse publique sous le commentaire : écrite dans sa langue (3 variantes), pas les textes anglais par défaut.
- Créée en brouillon (`isActive: false`), montrée, activée seulement après son OK. Puis test : il envoie le mot en DM depuis un autre compte, tu vérifies `blotato_list_automation_runs` (`completed`).

## 5. Carrousels
Même chemin : les images (PNG) du Carrousel en `mediaUrls` (plusieurs adresses = carrousel Instagram / LinkedIn), légende du Carrousel, même OK.

## Règles
- Un fichier ou un outil cité qui n'existe pas chez lui : ignore-le.
- Jamais de publication sur un compte non coché, jamais sans OK, jamais en mode essai.
- Tu ne réponds jamais à un commentaire ni à un DM à sa place (hors réponse automatique validée).
