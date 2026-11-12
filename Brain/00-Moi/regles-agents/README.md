---
description: "Comment marchent les carnets des agents : chaque correction = 1 règle dans le carnet de l'agent. À lire avant d'écrire dans un carnet."
type: index
statut: actif
sujets: [ia]
---
# Carnets d'apprentissage des agents

Un carnet par agent. Chaque correction que tu fais devient une règle définitive : l'agent ne refait jamais deux fois la même erreur.

## Comment ça tourne
1. Chaque agent lit son carnet AVANT de travailler. Le carnet passe avant le reste de ses consignes.
2. Tu corriges, notes ou refuses un travail (même en passant, dans n'importe quel chat) → Claude ajoute UNE ligne dans le carnet de l'agent concerné : `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`.
3. Les membres du board ne peuvent pas écrire (lecture seule) : c'est le skill `team` qui écrit leurs règles quand tu contestes un avis.
4. Chaque dimanche, Le Psy (audit-croyances) fait le ménage : doublons fusionnés, règles contradictoires signalées.

## Qui est qui
| Fichier | Nom | Rôle |
|---|---|---|
| head-of-common-sense.md | Head of Common Sense | board : bon sens, dernier mot |
| head-of-common-sense-2.md | Head of Common Sense 2 | board : contredit le premier |
| devil-advocate.md | Devil Advocate | board : l'angle mort |
| skipper.md | Skipper | board : connaît tout le Brain |
| closer.md | Le Closer | board : vente |
| media-buyer.md | Media Buyer | board : publicité en ligne |
| money-maker.md | Money Maker | board : le chemin le plus court vers l'argent |
| cmo.md | CMO | board : marketing |
| strategist.md | Stratège | board : vision 6 à 24 mois |
| cto.md | CTO | board : technique, outils |
| copy-chief-a.md | Copy Chief A | board : écrit |
| copy-chief-b.md | Copy Chief B | board : contredit le A |
| compliance-officer.md | Compliance Officer | board : règles pub et légales |
| expert-scraper.md | Le Limier | trouve les bons experts |
| audit-croyances.md | Le Psy | skill audit-croyances |
| scripteur.md | Le Scripteur | skill scripteur : scripts de reels et de YouTube |
| supermonteur.md | Le Monteur | skill supermonteur : montage des reels |
| carrousel.md | Le Carrousel | skill carrousel |
| slides.md | Le Projectionniste | skill slides |
| publieur.md | Le Publieur | skill publieur : programmation des posts |
| anti-ia.md | Le Gommeur | skill anti-ia : retire le ton IA |
| usine-pubs.md | L'Usine à pubs | skill usine-pubs |
| audit-insta.md | L'Auditeur Insta | skill audit-insta |
| ma-marque.md | Ma marque | skill ma-marque : voix, cible, DA |
| setter.md | Le Setter IA | skill setter : commentaires qualifiés et brouillons de réponses (l'humain envoie) |
| preparateur-coaching.md | Le Préparateur de coaching | skill preparateur-coaching : préparer et récapituler les calls de groupe |
| stagiaire.md | Les Stagiaires IA | agent stagiaire (petit modèle) : tâches mécaniques en volume, toujours vérifiées |
| stratege-contenu.md | Le Stratège | skill stratege-contenu : chiffres et sujets |
| funnel-builder.md | Le Funnel builder | skill funnel-builder : tunnel GoHighLevel |
| pilote-pub.md | Le Pilote pub | skill pilote-pub : couper / garder / pousser |
| page-produit.md | L'Étalagiste | skill page-produit : page produit e-commerce |
| suivi-client.md | Le Suivi client | skill suivi-client : prochaines étapes après un appel |
| relance-leads.md | Le Relanceur | skill relance-leads : leads qui dorment |
| apple-design.md | Le Designer Apple | skill apple-design (en coulisse) : pages fluides |
| copywriter.md | Le Copywriter | skill copywriter : pages, DM, emails, légendes |
| messagerie.md | L'Ambassadeur | skill messagerie : brouillons de messages |
| offre.md | Le Créateur d'offres | skill offre : offre notée sur 10 |
| positionneur.md | Le Positionneur | skill positionneur : fiche de positionnement |
| tuto-vers-agent.md | Le Traducteur de tutos | skill tuto-vers-agent : tuto devient agent |
