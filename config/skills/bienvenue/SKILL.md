---
name: bienvenue
description: Accueil du kit Claude. Questionnaire de départ (questions cliquables, 3 minutes) qui remplit la partie « Qui je suis » du master prompt et le profil du Brain, propose de rapatrier ce que ChatGPT sait de la personne, règle les skills contenu sur sa marque s'il crée du contenu, puis montre en 5 lignes ce que le kit sait faire. Use right after installing the kit, when « Qui je suis » still says À REMPLIR, or when the user says "bienvenue", "refais mon profil", "présente-toi", "tu sais faire quoi", "range ma clé ElevenLabs", "clé ElevenLabs".
---

# Bienvenue : 3 minutes pour que Claude te connaisse

Ton but : qu'à la fin, Claude parle à cette personne comme un assistant qui la connaît depuis des mois. Ton ton : chaleureux, simple, zéro jargon. La personne est peut-être totalement débutante.

## 1. Dire bonjour (2 lignes max)
« Le kit est installé. Quelques questions pour m'adapter à toi, ensuite tu n'auras plus jamais à te présenter. »

Si `~/.claude/superstudio.txt` (ou l'ancien `~/.claude/kit-claude.txt`) existe et qu'un ancien CLAUDE.md a été sauvegardé (chemin dans `~/.claude/backups/superstudio-*/.claude/CLAUDE.md` ou `~/.claude/backups/kit-*/.claude/CLAUDE.md`) : lis-le, garde ses préférences utiles pour l'étape 3, et dis-le en une ligne.

Puis AskUserQuestion, une question : « Comment tu veux répondre ? »
- **Tout sur une page (Recommandé)** : une page s'ouvre, tu cliques, tu écris 6 phrases, tu copies, tu colles ici. 15 minutes.
- **Ici, une question à la fois** : je te pose les questions dans le chat.

**Tout sur une page** : ouvre `open ~/.claude/skills/bienvenue/questionnaire.html` (Mac) ou `start "" "%USERPROFILE%\.claude\skills\bienvenue\questionnaire.html"` (Windows). Dis en une ligne : « Réponds sur la page, clique Copier mes réponses en bas, puis colle-les ici. » Attends le collage.
Quand le texte collé arrive (il commence par « Configure mon kit Claude avec ces réponses ») : fais les étapes 3 à 8 dans l'ordre avec ces réponses, sans reposer une seule question qui y est (une réponse « (pas répondu) » = choix recommandé pour les clics, « À REMPLIR » pour le texte). Étape 5 : le choix des logiciels est déjà fait, saute l'étape 2 de `logiciels`. Étape 6 : si « Créer du contenu » est coché, lance `ma-marque` en mode express (ses étapes 1 à 4 sont déjà répondues). Ce qui reste à faire à la main (coller la réponse de ChatGPT, donner le logo, ses codes couleurs) : demande-le au moment où tu en as besoin.
**Ici** : continue à l'étape 2.

## 2. Les questions (AskUserQuestion, option recommandée en premier)
Un seul appel avec ces 4 questions :
1. « Tu vas surtout utiliser Claude pour quoi ? » (multiSelect) : Mon travail / mon business · Mes études · Ma vie perso (admin, santé, famille) · Créer du contenu.
2. « Ton niveau avec l'IA ? » : Débutant total · J'utilise déjà ChatGPT · À l'aise.
3. « Comment je te parle ? » : Ultra court, juste l'essentiel (Recommandé) · Court avec un peu d'explication · Détaillé, j'aime comprendre.
4. « Tu viens de ChatGPT ? » : Oui, rapatrie ce qu'il sait de moi (Recommandé si oui) · Oui, mais plus tard · Non.

Puis en texte libre, une seule question : « Ton prénom, et en une phrase : ce que tu fais et ton objectif n°1 pour les 3 prochains mois ? »
Tutoiement par défaut. Si la personne vouvoie, vouvoie-la et note-le.

## 3. Écrire le profil
a) Dans `~/.claude/CLAUDE.md`, remplace UNIQUEMENT ce qu'il y a entre `<!-- PROFIL:DEBUT -->` et `<!-- PROFIL:FIN -->` (garde les deux balises) par :
```
## Qui je suis
- <Prénom>. <ce qu'il fait, 1 ligne>.
- Objectif n°1 (3 mois) : <objectif>.
- J'utilise Claude pour : <usages>.
- Niveau IA : <niveau>. <si débutant : « Pars du principe que je suis un immense débutant. »>
- Je veux l'output, pas le comment. <adapter selon la réponse 3 : ultra court / court + explication / détaillé>
- <tutoiement ou vouvoiement>
```
6 à 8 lignes max : ce bloc est lu à chaque chat.

b) Remplis `~/Documents/Brain/00-Moi/profil.md` (garde l'en-tête, remplace les « À REMPLIR ») avec la version longue.
c) `~/Documents/Brain/hot.md` : remplace « À REMPLIR » par 3 à 5 lignes (qui, objectif n°1, ce qui est en cours).
d) Une ligne en bas de `~/Documents/Brain/log.md` : `- AAAA-MM-JJ · Profil créé (skill bienvenue).`
e) Enregistre aussi l'essentiel dans ta mémoire.

## 4. ChatGPT
- Réponse « Oui, rapatrie » : lance le skill `import-chatgpt` maintenant (lis `~/.claude/skills/import-chatgpt/SKILL.md` et suis-le).
- « Plus tard » : dis en une ligne « Quand tu veux, écris : importe ChatGPT. »

## 5. Les logiciels gratuits
Lance le skill `logiciels` (lis `~/.claude/skills/logiciels/SKILL.md` et suis-le) : il propose en un clic Obsidian, Wispr Flow, Chrome + Claude in Chrome, et installe les outils invisibles dont les skills ont besoin.
Avant l'étape 6 exprès : le script d'essai de `ma-marque` a besoin du pack contenu (Chrome + PyMuPDF).

## 6. Ton contenu (si « Créer du contenu » est coché, ou s'il dit qu'il fait des vidéos)
Dis en 1 ligne : « Tu crées du contenu : je règle tes skills contenu sur ta voix, ta cible et tes couleurs (10 minutes). Maintenant ou plus tard ? » (bouton : Maintenant (Recommandé) · Plus tard).
- Maintenant : si le pack contenu a été refusé à l'étape 5, installe d'abord Chrome et PyMuPDF (skill `logiciels`, partie Pack contenu), sinon le script d'essai plante. Puis lance le skill `ma-marque` (lis `~/.claude/skills/ma-marque/SKILL.md` et suis-le), puis reviens à l'étape 7.
- Plus tard : « Quand tu veux, écris : ma marque. »

### 6 bis. La clé ElevenLabs (si « Créer du contenu » est coché)
ElevenLabs = le site qui écrit tes sous-titres sans faute. L'offre Starter suffit. Sans clé, le Monteur dépanne avec un outil gratuit moins précis.
Si `security find-generic-password -s elevenlabs-api-key -w` répond déjà une clé : saute cette étape. Sinon, une action à la fois :
1. « Crée ton compte sur elevenlabs.io et prends l'offre **Starter** (environ 5 € par mois, largement assez pour tes vidéos ; si un jour il en manque, passe à Creator en un clic), puis ouvre ce lien : https://elevenlabs.io/app/developers/api-keys. Clique sur Create API Key, puis copie la clé. Écris "copié" quand c'est fait. » Bouton : Copié · Plus tard.
2. À « copié » : range la clé toi-même depuis le presse-papier, sans jamais l'afficher ni la demander dans le chat : `CLE="$(pbpaste | tr -d '[:space:]')"; [ ${#CLE} -ge 20 ] && security add-generic-password -U -a "$USER" -s elevenlabs-api-key -w "$CLE" && printf '' | pbcopy && echo OK`. Si ça ne répond pas OK : « Le presse-papier ne contient pas la clé, recopie-la puis écris copié. »
3. Vérifie avec `security find-generic-password -s elevenlabs-api-key -w >/dev/null && echo rangée`, puis dis en 1 ligne : « Clé rangée dans le trousseau de ton Mac, jamais dans un fichier. »
Plus tard : « Quand tu veux, écris : range ma clé ElevenLabs. » (même déroulé).

## 7. La routine du dimanche
Si l'outil de tâches planifiées de l'app est disponible (`create_scheduled_task`) : crée la tâche `audit-du-dimanche`, chaque dimanche à 10h (heure locale), avec ce prompt :
« Lance le skill audit-croyances (~/.claude/skills/audit-croyances/SKILL.md) et suis-le : génère la page d'audit du jour dans ~/Documents/Brain/04-Audits/, ouvre-la, puis dis en une ligne : "Ton audit du dimanche est prêt. Coche tout, clique sur Copier, colle-le dans un chat et écris go." »
Dis en une ligne qu'elle tourne seulement si l'app Claude est ouverte. Outil absent : dis-lui juste « Le dimanche, écris audit ».

## 8. Le guide pas à pas (le message final)
Ouvre le guide : `open ~/Documents/Brain/GUIDE.html` (Mac) ou `start "" "%USERPROFILE%\Documents\Brain\GUIDE.html"` (Windows). Il explique chaque outil : c'est quoi, la phrase à dire, ce que ça donne. Puis écris :

```
C'est prêt, <Prénom>. Ton guide est ouvert : chaque outil, la phrase à dire et ce que ça donne.
Par où commencer (dans cet ordre) :
1. « Positionne-moi » → qui tu vises, ton message, ta bio (tous les outils la lisent)
2. « Crée mon offre » → ce que tu vends, noté sur 10
3. « Écris-moi 3 scripts sur ... » → tes premiers reels
4. Glisse une vidéo + « Monte cette vidéo »
5. « Programme ma semaine » → tes reels partent tout seuls, après ton OK

Le guide est toujours là : dis « montre-moi le guide ».
```
Adapte l'ordre aux usages cochés à l'étape 2 (ex. il ne fait pas de contenu : garde 1, 2, puis « Écris ma page de vente » et « Prépare mon call de vente »). Ne dépasse pas 15 lignes.

### « Montre-moi le guide » (à tout moment)
Ouvre `~/Documents/Brain/GUIDE.html`. Il demande un outil précis : lis sa partie dans `~/Documents/Brain/GUIDE.md` et explique-le en 3 lignes (c'est quoi, la phrase à dire, ce que ça donne), puis propose de le lancer (bouton).

## Relancer
Si la personne relance `bienvenue` plus tard : montre-lui son profil actuel en 5 lignes et demande ce qu'elle veut changer (QCM), au lieu de tout reposer.
