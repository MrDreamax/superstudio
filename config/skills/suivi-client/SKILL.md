---
name: suivi-client
description: Le Suivi client. Après un appel client (enregistré avec Fathom, ou une transcription collée), sort les prochaines étapes - to-do par personne, brouillon WhatsApp à ta voix, PDF court seulement si tu le demandes. Part TOUJOURS de la transcription complète. N'envoie jamais rien. Use when "next steps", "prochaines étapes", "c'est quoi les next steps avec X", "à partir de mon dernier call avec X", "plan d'action pour X", "message WhatsApp pour X", "to-do de X", "récap de mon call", "PDF pour X".
---

# Suivi client : de l'appel à l'action en 5 minutes

## Carnet
Lis d'abord ~/Documents/Brain/00-Moi/regles-agents/suivi-client.md s'il existe. Ses règles passent AVANT ce fichier. Si l'utilisateur corrige ou refuse ton travail : 1 ligne `JJ/MM/AAAA · correction · problème → règle` dans ce carnet, et dis-le en une ligne.
Preuves clients (repérer un gain, le chiffrer, demander le témoignage au bon moment) : ~/Documents/Brain/02-Formations/experts-resultats-clients-temoignages.md.
Après un appel individuel : experts-art-du-coaching.md §7-E (action du client au format « Après [ancre], je [mini-action]. Si [obstacle], alors [plan B] », seulement si elle est dite dans l'appel) ; client qui n'avance pas : experts-customer-success-resultats.md §9-D ; plainte dans l'appel : experts-satisfaction-customer-care.md §9-C.

## Règles qui ne bougent pas
- Source = la transcription COMPLÈTE du dernier appel (connecteur Fathom : get_meeting_transcript ; sinon la transcription collée) + chaque doc ou image envoyé. La fiche client dans le Brain (01-Projets/ ou 07-Clients/) sert de contexte, jamais de source des décisions.
- Tout format, sujet ou règle du livrable vient de l'appel. Pas dans l'appel = pas dans le livrable, ou marqué [à valider].
- N'envoie jamais rien au client : l'utilisateur envoie lui-même.
- Pas de transcription (Fathom pas branché, rien collé) : dis-le en 1 ligne (fathom.video, gratuit) et demande-la. Jamais de résumé de mémoire.

## Étapes
1. **Trouver l'appel** : lien collé → get_recording_by_url. Sinon list_meetings / search_meetings par nom.
2. **To-do par personne**, dans l'ordre de priorité (1 = ce qui bloque le reste) : le client (et chaque membre de son équipe nommé), puis l'utilisateur. 1 ligne par tâche, verbe d'action, échéance si elle est dite.
3. **Rendu par défaut dans le chat** (15 lignes max) : la to-do + un brouillon WhatsApp.
   - WhatsApp : tutoiement si l'utilisateur tutoie le client dans l'appel, 5 à 8 lignes, puces, 1 question fermée à la fin, zéro mot de doute (« je pense », « peut-être »).
4. **PDF seulement s'il le demande** : 1 à 3 pages, ~40 mots max par bloc, 1 schéma par page, planning à la semaine, lien du replay en haut, aux couleurs de sa marque (00-Moi/marque.json, outil `python3 ~/Documents/Brain/_outils/page_pdf.py`). Titres sans point. Vérifie le PDF (nombre de pages, images chargées) avant de l'envoyer. Dossier : ~/Documents/Contenu/clients/<client>/.
5. **Brain** : mets à jour « Prochaines étapes » dans la fiche client avec les décisions exactes de l'appel. 1 ligne en bas de ~/Documents/Brain/log.md.
