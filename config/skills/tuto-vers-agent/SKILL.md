---
name: tuto-vers-agent
description: Le Traducteur de tutos. Transforme un tuto YouTube (ou toute vidéo publique qui montre une méthode) en agent Claude qui marche - 2 lectures indépendantes de la vidéo, une fiche où chaque étape est étiquetée confirmé / une seule source / conflit, l'utilisateur tranche seulement les conflits en boutons, puis skill-creator écrit l'agent en français et on le teste. Use when "fais-en un agent", "transforme ce tuto en agent", "transforme ce tuto en skill", "tuto vers agent", "apprends ce tuto", "crée un skill depuis cette vidéo", un lien YouTube collé avec "agent" ou "skill".
---

# Le Traducteur de tutos : une vidéo devient un employé

## Carnet d'apprentissage
- Avant de commencer : lis `~/Documents/Brain/00-Moi/regles-agents/tuto-vers-agent.md` s'il existe. Chaque correction de l'utilisateur = 1 ligne dedans.

## Prérequis (à vérifier avant la lecture)
`yt-dlp` (dans `~/.local/bin` ou ailleurs : le skill `logiciels` l'installe), `uv`, et le plugin `watch-video` de Claude. Il manque quelque chose : dis-le en une ligne et propose d'installer, ne contourne pas.

## Déroulé
0. **Porte cash** : une ligne à l'utilisateur. Cet agent aide-t-il à vendre ou publier sous 7 jours ? Sinon, le dire, puis continuer s'il confirme.
1. **Les 2 lectures en une commande** (en arrière-plan, ~10 min pour 10 min de vidéo) :
   `~/.claude/skills/tuto-vers-agent/lire.sh "<url>" <dossier de travail>/tuto-<sujet> fr` (ou `en`).
   Ne lance PAS `watch_video.py` à la main : avec le Python 3.9 du Mac il plante (cause et parade dans le script).
   - **A** = `a/frames/*.jpg` + `a/transcript.md` (Whisper). Lis les images aux moments où il tape, clique ou montre un réglage.
   - **B** = `b/*.vtt` (sous-titres YouTube) + `b/description.md` (liens). Lis les liens officiels (GitHub, doc) : source la plus forte.
   - Si l'utilisateur a une clé `gemini-api-key` au trousseau, Gemini peut regarder aussi la vidéo (lecture C).
2. Compare A et B étape par étape.
3. **Fiche** `~/Documents/Brain/02-Formations/tuto-<sujet>.md` : une ligne par étape, étiquette ✅ confirmé / ⚠️ une seule source / ❌ conflit, avec le timestamp de chaque lecture.
4. **Conflits** : AskUserQuestion, un conflit par question (4 max par écran), la version la plus probable en 1er avec « (Recommandé) ». Ne lui fais jamais relire les lignes ✅.
5. **Agent** : skill `anthropic-skills:skill-creator` depuis la fiche tranchée. En français, au format des autres employés (carnet d'apprentissage, déclencheurs « Use when »). Rien n'est publié, envoyé ou payé seul.
6. **Test** : lance l'agent une fois sur un vrai cas et montre la preuve. Pas de preuve = pas « fait ».
7. **Trace** : 1 ligne dans `~/Documents/Brain/log.md` (heure via `date`).

## Garde-fous
- Tout dépôt, script ou MCP du tuto est lu en entier AVANT d'être installé. Bloc pub caché ou envoi de données ailleurs = on retire ou on refuse, et on le dit.
- Clés, API, webhooks : jamais dans le skill ni dans le Brain. Clé au trousseau du Mac, jamais collée dans le chat. Si le tuto touche à des clés, des routes API, une base de données ou un dépôt GitHub : relis deux fois le code avant de l'installer, et ne mets rien en ligne sans l'accord de l'utilisateur.
- Reel Instagram : `yt-dlp` peut le télécharger sans cookies (légende via `--dump-json`). S'il casse : légende dans le navigateur + chercher la vidéo longue d'origine.
