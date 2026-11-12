---
name: super
description: Ouvre Super Studio (et range la clé ElevenLabs), la vitrine où l'on voit les 4 robots (Le Scripteur, Le Monteur, Le Carrousel, Le Publieur) travailler, dans le navigateur intégré de Claude. Use when "/super", "super studio", "ouvre super", "ouvre le studio", "ouvre super studio", "ouvre mes applis", "qu'est-ce que tu sais faire", "aide", "par où commencer", "range ma clé ElevenLabs", "clé ElevenLabs".
---

# Super Studio

Tout se demande dans le chat. Super Studio montre seulement les robots au travail et leurs résultats.

## Ouvrir
1. `bash ~/Documents/SuperApps/super/lancer.sh`
2. Vérifie : `curl -s localhost:8800/api/etat` doit répondre `monteur` et `carrousel` à `true`. Un `false` : relance une fois, puis dis lequel + la dernière ligne de son `serveur.log`.
3. Ouvre `http://localhost:8800` dans le navigateur intégré de Claude (`preview_start` avec `url`). Jamais dans Chrome.
4. Réponds en 1 ligne : « Super Studio est ouvert. »

## « Qu'est-ce que tu sais faire ? » / « Par où commencer ? »
Montre le contenu de `~/.claude/skills/super/BIENVENUE.md` tel quel.

## « Range ma clé ElevenLabs »
La personne a copié sa clé (elevenlabs.io > clés API). Lance `bash ~/Documents/monteur-ia/ranger-cle-elevenlabs.command` : il la prend dans le presse-papier et la range dans le trousseau du Mac. Jamais la clé collée dans le chat. Fichier absent : relance l'installation (« Installe les applis qui sont ici : https://github.com/MrDreamax/monteur-ia »).
