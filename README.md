# Super Studio : ton équipe de 4 robots pour tes reels

Le Scripteur, Le Monteur, Le Carrousel, Le Publieur. Tu filmes. Ils écrivent, montent, dessinent et publient.
Tout tourne sur ton Mac, avec ton abonnement Claude.

## Avant de commencer : 5 obligatoires + 2 conseillés
1. **Claude (obligatoire)** : l'app sur claude.ai/download, abonnement Pro ou plus (le gratuit n'ouvre pas l'onglet Code).
2. **ElevenLabs (obligatoire)** : compte sur elevenlabs.io, formule Creator (il écoute tes vidéos pour les sous-titres). Crée une clé API. Après l'installation : copie-la, puis dis à Claude « Range ma clé ElevenLabs ».
3. **Metricool (obligatoire pour publier)** : compte gratuit sur metricool.com, branche Instagram, TikTok, YouTube. Puis dans Claude : Réglages > Connecteurs > Metricool.
4. **Les 100 musiques (obligatoire pour les montages)** : mets `100-MUSIQUES.zip` (lien envoyé à part) dans Téléchargements AVANT d'installer.
5. **Google Chrome (obligatoire pour les carrousels)** : google.com/chrome, il dessine les images.
6. **Wispr Flow (conseillé)** : wisprflow.ai, tu dictes au lieu d'écrire.
7. **Obsidian (conseillé)** : obsidian.md, gratuit. Ouvre `Documents/Brain` avec, pour lire ta mémoire comme un carnet.

## Installer (ou mettre à jour)
1. Ouvre l'app Claude sur ton Mac, onglet **Code**.
2. Colle cette phrase :

   > Installe les applis qui sont ici : https://github.com/MrDreamax/monteur-ia

3. Clique « Autoriser » quand Claude le demande.

Ton Brain (ta mémoire) arrive dans `Documents/Brain`, déjà rempli de fiches d'experts (hooks, montage, son, vente, Instagram, et 7 grands conseillers comme Hormozi ou Buffett). Pour y ajouter ta voix : « Pose-moi des questions pour remplir mon Brain ».

## Ce que tu peux demander
- **Le Scripteur** : « Écris-moi 3 scripts sur [sujet] » · « Transcris cette vidéo » + un lien ou un fichier · « Traduis cette vidéo mot pour mot » · « Reprends cette vidéo pour ma niche »
- **Le Monteur** : glisse ton rush + « Monte cette vidéo » · « Monte ma vidéo YouTube »
- **Le Carrousel** : « Fais-moi un carrousel sur [sujet] » · « Transforme ce reel en carrousel »
- **Le Publieur** : « Programme ma semaine »
- Perdu ? « Qu'est-ce que tu sais faire ? »

## Monter une vidéo
1. Glisse ton rush dans le chat Claude et écris : « Monte cette vidéo ».
2. Claude te demande comment tu veux ton montage. Dis-le avec tes mots, glisse une vidéo de référence si tu en as une.
3. La vidéo montée s'ouvre avec Cut Notes : tu notes ce qu'il faut changer, Claude corrige.
4. Tout est bon ? Le Publieur la programme avec Metricool, seulement après ton OK.

Pour voir les robots au travail : « Ouvre Super Studio » dans Claude.
**Publication en mode essai** : rien ne part tant que tu ne l'actives pas toi-même (`"mode_essai": false` dans `supermonteur/config.json` et `supercarrousel/config.json`).

## Pour Claude (installation)
1. `git clone https://github.com/MrDreamax/monteur-ia ~/Documents/monteur-ia` (ou `git pull` s'il existe déjà).
2. `bash ~/Documents/monteur-ia/install.sh` (relançable : c'est aussi la mise à jour ; les réglages, la DA, les reels, les carrousels et le Brain de la personne ne sont jamais écrasés, l'ancien moteur est sauvegardé dans `~/.claude/backups/`).
3. Demande son prénom (bouton) et écris-le dans `~/Documents/SuperApps/config.json` → `"nom"`.
4. Lance Super Studio : `bash ~/Documents/SuperApps/super/lancer.sh`, puis vérifie `curl -s localhost:8800/api/etat` (`monteur` et `carrousel` à `true`).
5. Les applis appellent Claude toutes seules : vérifie `claude auth status`. Pas connecté = double-clic sur `~/Documents/SuperApps/superda/connecter-claude.command`.
6. Montre à la personne, en entier dans le chat, le contenu de `BIENVENUE.md` (ce dossier) : ce qu'elle peut demander à chaque robot. Puis propose : « Pose-moi des questions pour remplir mon Brain ».
7. Ne mets jamais `"mode_essai": false` toi-même : c'est à la personne de le faire.
8. « Range ma clé ElevenLabs » : la clé est dans son presse-papier, lance `bash ~/Documents/monteur-ia/ranger-cle-elevenlabs.command` (jamais la clé dans le chat).

Ce qui est installé : les skills `super`, `scripteur`, `supermonteur`, `publieur` et `carrousel` dans `~/.claude/skills/`, Super Studio et ses moteurs dans `~/Documents/SuperApps/`, le Brain dans `~/Documents/Brain/`.

Fiches des 7 conseillers (`Brain/08-Conseillers/`) : d'après roast-room de Nate Herk (licence MIT).

Crédit : Cyril MrDreamax · byStratosphere
