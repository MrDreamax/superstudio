---
name: supermonteur
description: Le Monteur. Monte ta vidéo brute en reel 9:16 prêt à poster (coupes, sous-titres, titre, musique, B-rolls si tu en veux) et une vidéo YouTube 16:9 entière ; découpe une vidéo longue en reels. Te demande comment tu veux ton montage (avec une référence si tu en as une), puis Cut Notes pour tes retours et Style Lab pour ton style. Use when "monte cette vidéo", "monte-moi ce rush", "monte ce reel", "montage", "montage YouTube", "monte ma vidéo YouTube", "sous-titre cette vidéo", "sous-titres", "face cam", "podcast", "interview", "voix off", "green screen", "comparaison", "B-roll", "découpe cette vidéo en reels", "extraits", "clips", "transforme ce live en reels", "recycle cette vidéo", "change mon style", "style lab", "monteur".
---

## CHEZ TOI (client) : CE BLOC PASSE AVANT TOUT LE RESTE DE CE FICHIER ET DE workflow.md
Ce qui est installé : le moteur `~/Documents/SuperApps/supermonteur` (API `http://localhost:8801`), Cut Notes, Style Lab, les 100 musiques (`~/Documents/Montage/MUSIQUE`). Pas d'Epidemic Sound, jamais d'image ni de vidéo IA. Un fichier cité plus bas qui n'existe pas chez lui (Brain de l'auteur, références, archives) : ignore-le.
1. **Rush + « Monte cette vidéo »** : `bash ~/Documents/SuperApps/supermonteur/lancer.sh` (démarre le moteur s'il dort), puis `curl -s -X POST localhost:8801/api/nouveau -H 'Content-Type: application/json' -d '{"rush": "<chemin du rush>"}'` (réponse = la fiche, son `id`).
2. **UNE question ouverte**, si la personne n'a pas déjà décrit le montage voulu : « Décris-moi comment tu veux ton montage. Tu as une référence ? Si oui, glisse-la-moi et dis-moi tout ce que tu veux ici. » Zéro suggestion, zéro bouton, zéro liste de styles.
3. **Sa réponse → le style** (noms pour toi seul, jamais écrits à la personne) : rien de précis = `Minimaliste` (défaut) ; des images, du rythme, des cartons = `Dynamique` ; une comparaison = `Comparatif` ; une discussion à deux = `Interview` ; une référence = `Inspiration` + `"lien"` (lien Instagram, TikTok, YouTube).
4. Attends que la vidéo soit lue (`curl -s localhost:8801/api/reel/<id>` : `statut` n'est plus `regarde`), puis `curl -s -X POST localhost:8801/api/monter/<id> -H 'Content-Type: application/json' -d '{"style": "<Style>", "lien": "<lien ou vide>"}'`. Le montage tourne seul (quelques minutes) : dis-le en 1 ligne.
5. Ses demandes précises (un titre, couper un passage, une musique calme) : dès la 1re version, `POST /api/retour/<id>` `{"texte": "<sa demande>"}` puis `POST /api/suivant/<id>`.
6. **Montage fini** (`statut` = `retours`) : Cut Notes s'ouvre, sans rien demander : `python3 ~/.claude/skills/supermonteur/outils/cut-notes/ouvre.py ~/Documents/SuperApps/supermonteur/reels/<id>`, puis les gestes listés en tête de `ouvre.py`. Dans le chat : 1 ligne + un seul bouton « Suivant ».
7. « Suivant » : ses notes deviennent des retours (`ouvre.py <dossier> --notes <out_dir>`), le moteur ne retouche QUE les moments notés. Tout est bon : `curl -s -X POST localhost:8801/api/valider/<id>` (le reel passe en `valide`), puis propose « Programme ma semaine » (Le Publieur).
8. Style Lab : seulement s'il dit « change mon style ». Jamais de question de style en boutons.




**reels d'essai SUPPRIMÉS**. Je ne monte jamais de reel d'essai ni de 2e hook ; le Publieur n'envoie plus de TRIAL_REEL.

**Maquette d'abord** : tout NOUVEAU style ou design passe par 3 versions et 2 rounds avant d'exécuter (détail : `cahier-des-charges.md`). Un rush normal suit l'ordre rapide ci-dessous : le style se demande dans le chat, par une question ouverte (remplace la règle).

# SUPERMONTEUR : rush → reel premium

**Sommaire (un seul Monteur).** Lire seulement le fichier du cas, au moment où il sert :
- Rush court → reel : ce fichier + `styles/<style>.md`.
- Vidéo longue (YouTube, live, call de groupe, conférence) → plusieurs reels : `video-longue.md`.
- **Vidéo YouTube 16:9 entière (style theyo, plus autonome)** : `styles/youtube-theyo.md` + grille `note-10-youtube.md`.
- Rush + enregistrement iPad (dessin sur le mur) : `styles/tableau-mur.md`.
- **Style horizontal, pour du vertical (validé, ex-« style soowei »)** : rush horizontal zoomé en 4:3 entre deux bandes noires, titre d'une ligne au-dessus, sous-titres sur l'image : `styles/horizontal.md` + `scripts/horizontal.py`. Pas de question de style.
- **Rush horizontal en 16:9 sous-titré (SuperMonteur le fait seul)** : style Minimaliste sur un rush horizontal = dérush 1920x1080 + `serrer.py` + `scripts/soustitres169.py` (sous-titres en bas y=975, découpe auto aux bons endroits, champ `lignes` pour corriger le texte). Autre style sur un rush horizontal = message clair (style horizontal dans un chat). Retours sur un 16:9 = dans le chat (le correcteur auto ne sait que le 9:16).
- Client : `mode-client.md`.
Interne (absent du kit client) : `video-longue.md` et `styles/tableau-mur*`. Fichier absent = dire en 1 ligne que ce mode n'est pas dans le kit.

**Les règles de ce skill sont rangées à côté.** Quand un autre fichier cite « SKILL.md », une étape, le brief ou le cahier des charges, c'est ici :
- Brief, étapes 1 à 9, champs de `plan.json`, Gardien, livraison, boucle feedback : `workflow.md`.
- Cahier des charges (coupes, zones mortes, sous-titres, univers, maquette, DA) : `cahier-des-charges.md`.
- Toute décision de musique : `musique.md`. Choix d'un son : `sfx.md`. B-rolls : `brolls.md`.


```bash
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"
S=~/.claude/skills/supermonteur/scripts
$S/setup.sh            # 1re fois sur une machine : doit afficher SETUP OK
```
Dossiers : `<dossier>` = `dossier` de `~/Documents/Brain/00-Moi/marque.json` (sinon ~/Documents/Contenu) ; `<sorties>` = son `sorties` (sinon `<dossier>`).
Annoncer la durée au lancement et à la fin (titre + sous-titres : ~1 min ; avec rendu : 2 à 3 min pour 1 min de vidéo).

## Photos et vidéos de l'utilisateur
Seulement des images qu'il accepte : ses interdits (shooting, look, période) sont dans `feedback.md` et passent avant tout ; dans la bibliothèque B-roll, la période exclue des réglages (`brolls_periode_exclue`) est écartée par `scripts/broll_tri.py`. Vaut pour tout : site, carrousel, slides, montage, B-roll, cover, pub.

## Ordre de lecture (dans le dossier du skill)
1. **`feedback.md`** = le SEUL carnet des retours de l'utilisateur. Il passe avant le reste ; si deux lignes se contredisent, la plus RÉCENTE gagne.
2. **`regles-experts.md`** (12 domaines d'experts sourcés). Partie A = à appliquer dans chaque plan ; parties B et C = seulement avec l'accord de l'utilisateur. Si un expert contredit `feedback.md`, l'utilisateur gagne.
3. Chez un client (`config.json` → `client` rempli) : **`mode-client.md`** puis `retours-client.md` (SES retours passent avant tout).
4. Après le brief : **UNIQUEMENT le fichier du style choisi** (ne pas lire les autres).
5. Étape 8 : `note-10.md` (9/10 minimum, juge L'Œil Gemini). Modifier un script ou rendu cassé : `moteur.md`.


**LES 5 STYLES, LES SEULS (dicté par l'utilisateur ; renommés le même jour).** On ne propose rien d'autre, toujours sous CES noms. **Les 5 ont TOUJOURS une musique**.

| Style | Ce qu'on voit | Fichier |
|---|---|---|
| 1. Dynamique (face caméra) | MIX à équilibrer de 4 plans : split screen (face cam + animation), face cam seule, carton plein écran en dégradé propre, animation plein écran | `styles/face-cam.md` |
| 2. Minimaliste (clip, FAQ, selfie) | titre ou question qui RESTE jusqu'à la fin + sous-titres + musique, rien d'autre | `styles/raw.md` |
| 3. Comparatif (tier list, mauvais / bien / excellent, comparaison en T) | sous-titres + fondu sombre au-dessus de la tête avec le titre + le tableau | `styles/montage-viral.md` |
| 4. Interview | MIX split screen (les 2 personnes) + plein écran sur celle qui parle (déjà établi) | `styles/a-plusieurs.md` |


**l'appli Super est RETIRÉE, tout passe par le chat Claude. Style Lab et Cut Notes font partie du montage :**
- **Montage fini = Cut Notes s'ouvre TOUT SEUL, sans rien demander** (v1 comme chaque retouche) : `python3 outils/cut-notes/ouvre.py <dossier du reel>` (ou `--attendre` en arrière-plan si le montage tourne dans SuperMonteur : il rend la main au statut « retours »), puis dans le MÊME tour les 4 gestes listés en tête de `ouvre.py` (publier ou garder l'artifact du reel, envoyer review.mp4, écrire `review/current`, `Artifact open`). Le robot Monteur de la vitrine affiche « j'attends tes notes ». Dans le chat : 1 ligne + un seul bouton « Suivant ».
- **« Suivant »** : `ArtifactData list notes` (avec `out_dir`) puis `python3 outils/cut-notes/ouvre.py <dossier> --notes <out_dir>` en arrière-plan : les notes deviennent des retours SuperMonteur, le correcteur ne retouche QUE les moments notés, et à la nouvelle version Cut Notes repart au tour suivant (mêmes 4 gestes, même artifact). Ensuite passer chaque note en `fixed` + `reply` (lu dans `retours.json`). 0 note ouverte = demander en 1 ligne s'il a laissé des retours, rien n'est validé.
   **Quand il clique « Suivant » dans le chat** : lire `etat.json` du reel. `statut` = `correction` : Claude corrige déjà, je ne relance rien. Sinon : `POST http://localhost:8801/api/suivant/<id>` (même effet que le bouton de l'écran), et l'ouvrier remonte la version suivante. Puis de nouveau un seul bouton « Suivant ». Validation et publication : boutons de l'écran. Consigne donnée dans sa demande (ex. un titre) : SuperMonteur ne la reçoit pas, je l'écris dans `plan.json` et je la monte à ce même « Suivant ».
2. **Dérush** (`workflow.md`, étapes 1 à 3) → durée exacte et seconde de la punchline connues. **Derush Lab RETIRÉ** : le dérush part direct au montage, dans SuperMonteur comme dans un chat. Ne plus lancer cockpit.py --lab avant de monter.
3. **En même temps** : les B-rolls (seulement s'il en veut, choisis par moi, `brolls.md`) ET la musique (`musique.md`).
**l'appli SuperMonteur est CODÉE** (écran 0 style → montage → retours → Publier, Ma DA en tiroir) : `~/Documents/SuperApps/supermonteur/` ; « corrige mes retours » = mode d'emploi `apps/supermonteur/CLAUDE.md`.
4. **La pause = Cut Notes, ouvert tout seul (voir plus haut)** ; l'écran Retours de l'appli reste en secours (façon Cut Notes, Apple clair) : vidéo + retours accrochés à l'image (écrire ou dicter), « Corrigé ✓ ▶ Revoir », « Suivant : corrige mes retours » / « C'est parfait, on publie », « Ma DA » en tiroir, puis Télécharger (la publication se fait dans le chat avec le Publieur). Les 5 styles ET leurs aperçus respectent la zone interdite d'Instagram (haut 270, bas 1480, côtés 65, 120 à droite sous 1100 px). Règles complètes : Brain `01-Projets/superda-supermonteur.md`.
5. **Titre + sous-titres seuls (rien d'autre dans plan.json) : `python3 $S/express.py .`** (PAR DÉFAUT, validé par l’utilisateur) = même découpage des sous-titres, même mix, même Gardien, mais sans rendu Chrome : RUSH en 1 min 3 s au lieu de 6 min 9 s. Il sort en code 2 si le plan a autre chose -> monte.sh. SuperMonteur (monter.py) le choisit seul.
6. **Validation** : la vidéo finale + la note /10. La publication se fait dans un autre chat (Le Publieur), pas dans le chat du montage. Les réparations d'outils aussi.

## Non négociable, tous les styles (détail : `cahier-des-charges.md`)
- **Un rendu raté ne se garde pas.** Dès qu'un rendu est remplacé par un meilleur, l'ancien est effacé. On garde seulement le rush et le final validé. Pas de copies en double.
- Images et vidéos générées par IA : JAMAIS, dans aucun style.
- Zones mortes Instagram : `node $S/zones.mjs .` attendu « OK : 0 ».
- Jamais de coupe au milieu d'une phrase. Cuts au ras de la voix entre deux phrases, queue du mot entière.
- Zéro silence audible, zéro micro-coupure, chaque plan ≥ 2 s ou phrase entière.
- Jamais d'étalonnage ni de traitement du son du rush sans sa demande.
- Le Gardien est BLOQUANT : `python3 $S/gardien.py .`, un seul ❌ = on corrige, JAMAIS on livre.
- Rush renommé après la v1 (`renommer_rush.py`, SuperMonteur le fait seul).
- Note `note-10.md` obligatoire. Livraison : la vraie vidéo seulement.


**Après chaque reel : boucle feedback** (`workflow.md`, étape 9) : chaque retour = 1 ligne datée dans `feedback.md` et dans le carnet Brain `00-Moi/regles-agents/supermonteur.md`, le fichier de règles concerné corrigé pour qu'il n'y ait jamais deux versions, et une note mesurable = 1 contrôle de plus dans `gardien.py`.

- `derush.py ... --plan` = calcule les plages seules (3 s, aucun rendu) pour tester un correctif. Les bords de prises suivent la VRAIE attaque mesurée du mot supprimé (jamais le temps Whisper) ; une phrase courte avec vraie voix n'est jamais retirée.

- **cartons d'arbitre** (variante du Comparatif, RUSH) : `"cartons"` dans plan.json = rangée de cases au-dessus de la tête, un carton rouge tombe à chaque « carton rouge », le vert en dernier, titre de l'élément dessous ; posé par `scripts/cartons.py` (lancé seul par monte.sh). Cadre d'origine (pas cadre.py) pour garder la place au-dessus de la tête.
