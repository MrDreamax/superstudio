# Super Studio : ton équipe de 4 robots pour tes reels

Le Scripteur, Le Monteur, Le Carrousel, Le Publieur. Tu filmes. Ils écrivent, montent, dessinent et publient.
Tout tourne sur ton Mac, avec ton abonnement Claude.

## Avant de commencer : 4 obligatoires + 2 conseillés
1. **Claude (obligatoire)** : l'app sur claude.ai/download, abonnement Pro ou plus (le gratuit n'ouvre pas l'onglet Code).
2. **ElevenLabs (obligatoire)** : compte sur elevenlabs.io, formule Creator (il écoute tes vidéos pour les sous-titres). Crée une clé API, copie-la, puis double-clic sur `ranger-cle-elevenlabs.command`.
3. **Metricool (obligatoire pour publier)** : compte gratuit sur metricool.com, branche Instagram, TikTok, YouTube. Puis dans Claude : Réglages > Connecteurs > Metricool.
4. **Les 100 musiques (obligatoire pour les montages)** : mets `100-MUSIQUES.zip` (lien envoyé à part) dans Téléchargements AVANT d'installer.
5. **Wispr Flow (conseillé)** : wisprflow.ai, tu dictes au lieu d'écrire.
6. **Obsidian (conseillé)** : obsidian.md, gratuit. Ouvre `Documents/Brain` avec, pour lire ta mémoire comme un carnet.

## Installer (ou mettre à jour)
1. Ouvre l'app Claude sur ton Mac, onglet **Code**.
2. Colle cette phrase :

   > Installe les applis qui sont ici : https://github.com/MrDreamax/monteur-ia

3. Clique « Autoriser » quand Claude le demande.

Ton Brain (ta mémoire, vide au départ) arrive dans `Documents/Brain`. Pour le remplir : « Pose-moi des questions pour remplir mon Brain ».

## Monter une vidéo
1. Glisse ton rush dans le chat Claude et écris : « Monte cette vidéo ».
2. Claude te demande comment tu veux ton montage. Dis-le avec tes mots, glisse une vidéo de référence si tu en as une.
3. La vidéo montée s'ouvre avec Cut Notes : tu notes ce qu'il faut changer, Claude corrige.
4. Tout est bon ? Le Publieur la programme avec Metricool, seulement après ton OK.

Pour voir les robots au travail : « Ouvre Super » dans Claude.
**Publication en mode essai** : rien ne part tant que tu ne l'actives pas toi-même (`"mode_essai": false` dans `supermonteur/config.json` et `supercarrousel/config.json`).

## En option
- **Recherche de reels viraux** (Veille) : demande le connecteur Apify dans Claude.
- **Scanner cerveau** (Veille) : demande le connecteur Higgsfield dans Claude.
- Sans eux, tout le reste marche.

## Pour Claude (installation)
1. `git clone https://github.com/MrDreamax/monteur-ia ~/Documents/monteur-ia` (ou `git pull` s'il existe déjà).
2. `bash ~/Documents/monteur-ia/install.sh` (relançable : c'est aussi la mise à jour ; les réglages, la DA, les reels, les carrousels et les veilles de la personne ne sont jamais écrasés, l'ancien moteur est sauvegardé dans `~/.claude/backups/`).
3. Demande son prénom (bouton) et écris-le dans `~/Documents/SuperApps/config.json` → `"nom"`.
4. Lance Super : `bash ~/Documents/SuperApps/ouvrir-super.sh`, puis vérifie `curl -s localhost:8800/api/etat` (les 4 à `true`).
5. Les applis appellent Claude toutes seules : vérifie `claude auth status`. Pas connecté = double-clic sur `~/Documents/SuperApps/superda/connecter-claude.command`.
6. Remplis avec la personne `~/Documents/SuperApps/superveille/ma-marque.md`. Monter dans le chat, sans l'appli : lis `~/.claude/skills/supermonteur/mode-client.md`.
7. Ne mets jamais `"mode_essai": false` toi-même : c'est à la personne de le faire.

Ce qui est installé : les skills `super`, `superveille`, `supermonteur`, `publieur` et `carrousel` dans `~/.claude/skills/`, l'appli dans `~/Documents/SuperApps/`.

Crédit : l’utilisateur l’utilisateur · byStratosphere
