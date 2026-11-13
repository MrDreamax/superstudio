# Slide Notes : retours slide par slide

Le « Cut Notes » des slides. Une page locale : chaque slide en grand, un champ de retour, « Supprimer », « + Ajouter une slide ici », bouton « J'ai fini ». Tout s'enregistre tout seul dans notes.json.

1. Rendre les PNG du deck (a1.png, a2.png…).
2. `python3 prepare.py <dossier_png> <scratchpad>/slide-notes` (scratchpad : macOS bloque ~/Documents pour les serveurs).
3. Ajouter dans `.claude/launch.json` (en JSON, jamais `cat >`) : `/bin/sh -c "cd <dossier> && exec python3 server.py . 8823"`, puis preview_start « slide-notes ».
4. L’utilisateur écrit « suivant » : lire `<dossier>/notes.json` (items dans l'ordre : slide {id, note, del} ou new {after, note}), montrer 1 ligne de plan par retour, corriger, re-rendre, relancer prepare.py (les notes restent).
5. « suivant » avec 0 note : lui demander en 1 ligne s'il a laissé des retours.
