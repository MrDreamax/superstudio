# Slide Notes : retours slide par slide

Le « Cut Notes » des slides. Une page locale : chaque slide en grand, un champ de retour, « Supprimer », « + Ajouter une slide ici », bouton « J'ai fini ». Tout s'enregistre tout seul dans notes.json.

1. Rendre les PNG du deck (a1.png, a2.png…).
2. `python3 prepare.py <dossier_png> <scratchpad>/slide-notes` (scratchpad : macOS bloque ~/Documents pour les serveurs).
3. Ajouter dans `.claude/launch.json` (en JSON, jamais `cat >`) : `/bin/sh -c "cd <dossier> && exec python3 server.py . 8823"`, puis preview_start « slide-notes ».
4. Après chaque version, 2 boutons dans le chat : « Corriger » et « C'est parfait » (jamais un seul). « Corriger » : lire `<dossier>/notes.json` (items dans l'ordre : slide {id, note, del} ou new {after, note}), montrer 1 ligne de plan par retour, corriger, re-rendre, relancer prepare.py (les notes restent).
5. « Corriger » avec 0 note : lui demander en 1 ligne s'il a laissé des retours. « C'est parfait » : deck validé, livrer PDF + PNG.

## Dans Claude (artifact, par défaut) : noir + bleu comme Style Lab / Cut Notes
Même index.html, il tourne aussi en artifact (sans slides.json, il passe sur la base Claude).
1. Copier index.html dans `<deck>/slide-notes/artifact/slide-notes.html`, publier (capabilities `{"db": {}, "assets": {}}`, icône slides). URL dans `<deck>/slide-notes/slide-notes.url` (1 artifact par deck, réutilisé).
2. Uploader les JPG de `img/` en assets (`file_paths`, 25 par appel).
3. ArtifactData set `deck/current` = `{"name": ..., "slides": [{"id": "a1", "img": "/_blob/<id>"}, ...]}` (la page se met à jour toute seule).
4. Artifact open.
5. « Corriger » : ArtifactData get `notes/current` (même forme que notes.json : items slide {id, note, del} / new {after, note}, done).

Carrousel : même outil, préfixe `slide-` (`prepare.py <dossier du carrousel> <dossier>/slide-notes slide-`), le format 3:4 est gardé.
