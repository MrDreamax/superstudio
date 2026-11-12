# Règles du Brain (pour Claude)

Tu n'as pas besoin d'ouvrir ce dossier : Claude le lit et l'écrit pour toi. Son but : que chaque nouveau chat sache déjà qui tu es, tes projets et tes décisions.

## Lire
1. `hot.md` : l'état actuel en 1 minute. Toujours en premier.
2. `index.md` : une ligne par fichier. Puis seulement les fichiers utiles.
3. `tail -20 log.md` = ce qui a changé récemment.

## Les dossiers
- `00-Moi` : qui tu es, tes objectifs, tes préférences, ta façon de parler.
- `01-Projets` : un fichier par projet.
- `02-Formations` : fiches d'experts sourcées (hooks, montage, son, prix, vente, pub...) + tes propres formations.
- `03-Livres` : notes de lecture.
- `04-Audits` : bilans, chiffres, ce qui marche ou pas.
- `05-Decisions` : les décisions prises, et pourquoi.
- `06-Contenu` : scripts, idées, ce qui a marché sur les réseaux.
- `07-Clients` : une fiche par client.
- `08-Conseillers` : 7 cerveaux d'experts (Hormozi, Buffett, Bezos...), licence MIT, voir `08-Conseillers/README.md`.
- `09-SOP` : tes méthodes pas à pas.
- `_a-trier` : tu y jettes du brut (notes, PDF, captures, audios). Dis « range le Brain » et Claude range tout.

## Écrire une note
- Nom : minuscules-avec-tirets.md. Date devant si c'est daté : `AAAA-MM-JJ-sujet.md`.
- En-tête en haut du fichier :
```
---
description: "Ce qu'il y a dedans. À lire quand ..."
type: moi | projet | formation | livre | audit | decision | contenu | client | systeme
statut: actif
---
```
- Après : 1 ligne en bas de `log.md`, `hot.md` si l'état actuel change, puis `python3 ~/Documents/Brain/_outils/brain.py` (refait l'index).
- Jamais de mot de passe, clé API ou token en clair.

## Quand une note devient fausse
Ne la supprime pas : mets `statut: remplacé` + `remplace_par: "[[chemin/de/la/nouvelle]]"` dans son en-tête.
