# Super Studio : Claude, réglé pour vendre et créer du contenu

Un seul lien installe tout : ta mémoire (le Brain, déjà remplie de fiches d'experts), ton master prompt, une équipe d'agents et 26 outils pour démarrer, créer ton contenu et vendre.
Tout tourne sur ton Mac, avec ton abonnement Claude. Tu parles à Claude dans le chat : il n'y a aucune appli à ouvrir.

## Avant de commencer
1. **Claude (obligatoire)** : l'app sur claude.ai/download, abonnement Pro ou plus (le gratuit n'ouvre pas l'onglet Code).
2. **ElevenLabs (obligatoire pour monter et transcrire)** : compte sur elevenlabs.io, formule Starter (environ 5 €/mois, suffit largement ; Creator si un jour il en manque). Crée une clé API. Après l'installation : copie-la, puis dis à Claude « Range ma clé ElevenLabs ».
3. **Blotato (obligatoire pour publier)** : compte sur blotato.com (~29 $/mois), branche tes réseaux. Puis dans Claude : Réglages > Connecteurs > Blotato. Il publie tes reels et envoie tes cadeaux en message privé quand on commente ton mot-clé.
4. **Les 100 musiques (obligatoire pour les montages)** : mets `100-MUSIQUES.zip` (lien envoyé à part) dans Téléchargements AVANT d'installer.
5. **Google Chrome (obligatoire pour les carrousels et les PDF)** : google.com/chrome.
6. **Conseillés** : Wispr Flow (wisprflow.ai, tu dictes au lieu d'écrire), Obsidian (obsidian.md, pour lire ta mémoire), Fathom (fathom.video, tes appels transcrits).

## Installer (ou mettre à jour)
1. Ouvre l'app Claude sur ton Mac, onglet **Code**.
2. Colle cette phrase :

   > Installe Super Studio qui est ici : https://github.com/MrDreamax/superstudio

3. Clique « Autoriser » quand Claude le demande. À la fin, Claude lance « Bienvenue » (3 minutes de questions) et ouvre ton guide.

Ton guide pas à pas (chaque outil, la phrase à dire, ce que ça donne) : `Documents/Brain/GUIDE.html`. À tout moment : « Montre-moi le guide ».

## Les 26 outils
- **Démarrer** : Bienvenue, Import ChatGPT, Logiciels, Positionneur
- **Contenu** : Scripteur, Monteur (avec Style Lab et Cut Notes), Carrousel, Publieur (Blotato), Stratège, Slides, Audit Insta
- **Vendre** : Offre, Copywriter, Funnel builder, Page produit, Usine à pubs, Pilote pub, Setter, Closer, Messagerie, Relanceur, Suivi client, Préparateur coaching
- **Équipe** : Team (13 agents qui débattent), Tuto vers agent, Audit des croyances
- **En coulisse** : Ma marque, Anti-IA, Design Apple, Le Limier et Le Stagiaire (agents)

Règle de base : Claude prépare, toi tu décides. Rien n'est envoyé, publié ou payé sans ton OK. **Publication en mode essai** tant que tu ne l'actives pas toi-même.

## Pour Claude (installation)
1. `git clone https://github.com/MrDreamax/superstudio ~/Documents/superstudio` (ou `git -C ~/Documents/superstudio pull` s'il existe déjà).
2. `bash ~/Documents/superstudio/install.sh` (relançable : c'est aussi la mise à jour ; le profil du master prompt, le Brain perso, les réglages, la DA, les reels et les carrousels de la personne ne sont jamais écrasés, rien n'est supprimé chez elle, l'ancienne version est sauvegardée dans `~/.claude/backups/`).
3. Demande son prénom (bouton) et écris-le dans `~/Documents/SuperApps/config.json` → `"nom"`.
4. Le Monteur appelle Claude tout seul : vérifie `claude auth status`. Pas connecté = double-clic sur `~/Documents/SuperApps/superda/connecter-claude.command`.
5. Lance le skill `bienvenue` (~/.claude/skills/bienvenue/SKILL.md) : il remplit le profil et ouvre le guide à la fin.
6. Ne mets jamais `"mode_essai": false` toi-même : c'est à la personne de le faire.
7. « Range ma clé ElevenLabs » : la clé est dans son presse-papier, lance `bash ~/Documents/superstudio/ranger-cle-elevenlabs.command` (jamais la clé dans le chat).

Ce qui est installé : `~/.claude/CLAUDE.md` (master prompt), `~/.claude/agents/` (15 agents), `~/.claude/skills/` (29 skills, dont 3 en coulisse), les moteurs du Monteur et du Carrousel dans `~/Documents/SuperApps/`, le Brain dans `~/Documents/Brain/`.

Outils conseillés, pas inclus faute de licence de redistribution (installe-les toi-même si tu veux) :
- **Principes de contenu** (Remy Gaskell) : https://github.com/aiwithremy/content-principles
- **Finisseur** (better) et **Anti-vibecode** (Melvynx) : https://github.com/Melvynx/shared-skills

Fiches des 7 conseillers (`Brain/08-Conseillers/`) : d'après roast-room de Nate Herk (licence MIT). Design Apple : licence MIT (dans son dossier).

Crédit : Cyril MrDreamax · byStratosphere
