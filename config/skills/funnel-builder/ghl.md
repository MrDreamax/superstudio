# GoHighLevel : le mode d'emploi du Funnel Builder

Lu sur l'aide officielle. H = https://help.gohighlevel.com/support/solutions/articles/ (H/<numéro> s'ouvre avec le numéro seul).
**Vérifie à l'écran avant chaque clic** : les noms de menus bougent. « (déduit) » = pas écrit dans l'aide, à confirmer à l'écran. Un écart entre ce fichier et l'écran → l'écran gagne, et corrige ce fichier.

## Le plan
- Starter (97 $/mois) = 3 sous-comptes, funnels, domaines, workflows, paiements, emails payés à l'usage (0,675 $ les 1 000). https://www.gohighlevel.com/pricing

## 1. Le funnel et ses pages
- Sites > Funnels > New Funnel > From Blank. Puis Add New Step (150 étapes max). H/155000005057, H/155000005071
- Une page = section pleine largeur > ligne à 1 colonne > élément. H/155000005071
- Élément de code : Quick Add > Custom > « Code Element » > « Open Code Editor » > coller > Save. H/155000006924
- Un script qui doit tourner au chargement : couper « Optimise javascript » si besoin (événement `hydrationDone`). H/155000002421
- Pas écrit dans l'aide : taille max du code, `<style>` et `<script>` acceptés, page entière en un seul élément. → Teste à l'aperçu (téléphone + ordinateur) avant d'aller plus loin.
- Lien vers l'étape suivante depuis le HTML collé : pas écrit. On met l'adresse de l'étape commande dans le bouton (prepare_page.py --commande). Les boutons natifs ont l'action « Go to Next Step ». H/155000006914
- Titre de l'onglet : réglages SEO de la page (le `<title>` du HTML collé ne compte pas) (déduit).

## 2. Les produits et la devise
- Payments > Products > + Create Product > Pricing : « One time », montant, devise. La devise d'un prix ne se change pas ensuite : crée un nouveau prix. H/155000005071
- Devise par défaut : Settings > Business Profile > Currency (sinon celle du pays). https://ideas.gohighlevel.com/changelog/businesses-can-now-set-a-default-currency
- Produit numérique : Shipping and Delivery = Digital + fichier joint au produit → bouton « Download » après le paiement. H/155000005071

## 3. La commande, le petit plus, Apple Pay, les cases
- Étape commande > onglet Products > + Add Product (Main ou Bump). Puis élément « Two-Step Order » (réglages : Order Bump, Cart mode, Coupon). H/48000980307 ; en 1 étape : H/155000007238
- Petit plus dans le constructeur de formulaires : élément « Sell Products », type « Bump Product ». Un bump ne s'affiche que s'il y a un produit principal. H/155000005767
- Apple Pay / Google Pay (Stripe seulement) : Payments > Integrations > Stripe > Manage Payment Methods > « Funnels - One-Step / Two-Step Order Form ». Apple Pay demande de vérifier le domaine. Réglages test et réel séparés. H/48001229200, H/155000005164
- Case « Conditions générales » : interrupteur dans les réglages du formulaire de commande (texte + lien), obligatoire pour payer, sur les 2 étapes. → On y met la renonciation au droit de rétractation + le lien des CGV. https://ideas.gohighlevel.com/changelog/enable-terms-and-conditions-on-1-step-and-2-step-order-forms, H/155000006325
- Case « je veux recevoir les emails » séparée : **pas native** sur les formulaires de commande (demande ouverte du 05/09/2026). Piste : un formulaire du constructeur de formulaires (champ case à cocher + élément « Sell Products ») à la place du « Two-Step Order » (déduit, à tester). Sans case d'accord : pas de relance de panier.
- Un avis d'utilisateur (pas officiel) dit que la case CGV n'est pas gardée sur la fiche du contact : garde une capture de la page de commande datée comme preuve.

## 4. L'offre en 1 clic après l'achat
- Funnels V2 + formulaire ou commande natifs. Elle réutilise la carte, sans ressaisie. Sur l'étape : un bouton action « One click up/down sell product » + le produit. 1 produit par étape, quantité 1. Même domaine pour toutes les étapes. Élément « Order Confirmation » sur la dernière page. L'acheteur voit 2 débits, 1 reçu. H/155000006914
- « Non merci » : un bouton ou lien « Go to Next Step » vers la page merci (déduit).

## 5. Le mode test
- Stripe d'abord : Payments > Integrations > Connect Stripe. H/155000005073
- Puis Payments > Integrations > Configure Providers > interrupteur Live / Test, par canal (formulaire en 1 étape, en 2 étapes…). H/155000007346
- Cartes de test (Stripe, pas GHL) : 4242 4242 4242 4242, date future, CVC au choix ; 3D Secure : 4000 0000 0000 3220. https://docs.stripe.com/testing
- Apple Pay en mode test : pas confirmé.
- **Avant de vendre en vrai** : remettre le canal en Live (OK de l'utilisateur).

## 6. Les workflows
- Livraison : déclencheur « Order Submitted » (Payments, funnels V2) ; filtres Product is, Funnel, Page, Submission Type (Primary / Bump / Upsell). Allumer « Allow Multiple » (l'offre après l'achat re-déclenche). Pas de longue attente. H/48001228664
- Autres déclencheurs : « Payment Received » (Source = Funnel, Payment Status = Success) H/155000003534 ; « Order Form Submission » (Bump / Opt-In / Sale / Upsell, sans les montants) H/155000003253. Comparatif : H/155000004303
- Actions : « Send Email » (From Name, From Email, Subject, corps, pièce jointe de la médiathèque) H/155000002472 ; « Add Contact Tag » H/155000003111 ; « Wait » H/155000002470.
- Tester un workflow : bouton « Test Workflow » (choisir un contact, Run Test), « pas parfait à 100 % » selon l'aide. H/155000001254

## 7. Le panier abandonné (pas automatique sur un funnel)
- L'email automatique de panier abandonné = boutiques seulement. H/155000001718 ; déclencheur « Abandoned Checkout » = boutiques seulement. H/155000007380
- Sur un funnel : « Order Form Submission », Submission Type = Opt-In (coordonnées laissées, pas de paiement) → Wait → If/Else « a le tag acheteur ? » → sinon la séquence. Le tag acheteur vient du workflow de livraison (déduit). H/155000003253
- Seulement aux personnes qui ont coché l'accord emails (voir 3).

## 8. Instagram : commentaire → DM
- Connexion : Settings > Integrations > Facebook & Instagram ; compte Instagram professionnel (Business ou Creator) lié à une page Facebook. H/155000002055, H/48001213003
- Déclencheur : Automations > Workflows > Triggers > Facebook/Instagram Events > « Instagram Comment(s) On A Post ». Filtres : Page Is, Post Type (posts publiés ou adresse d'un post), Post Is, « Contains Phrase » ou « Exact Match » sur une liste de mots, réponse aux commentaires de 1er niveau seulement. Les commentaires du workflow lui-même ne relancent pas la boucle. H/155000004646
- Accents et majuscules : pas écrit → mets toutes les variantes (ex. ÉQUIPE, Équipe, équipe, EQUIPE, Equipe, equipe).
- Action : **« Instagram Interactive Messenger », Reply Type « Reply to Comment via DM »** (fenêtre de 7 jours). PAS l'action « Instagram DM » simple : elle n'arrive que si la personne a écrit en DM dans les 24 h. H/155000003298, H/155000004662, H/155000002055
- « Reply in Comment » : une réponse publique tirée au hasard dans ta liste, peut aimer le commentaire. H/155000002055
- Test : pas de simulation. On commente le mot pour de vrai, depuis un autre compte, sous un post de test (OK de l'utilisateur : le commentaire est public).

## 9. Les emails
- Par défaut, un nouveau sous-compte envoie depuis les serveurs partagés de HighLevel ; un domaine à soi est facultatif : Settings > Email Services > Dedicated Domain and IP > Add Domain. H/48001226115
- Nom et adresse de l'expéditeur : dans l'action « Send Email », ou Workflow > Settings > Communication > Sender details. H/48000979925, H/155000004428

## 10. Le domaine des pages
- Settings > Domains & URL Redirects > + Connect a domain > Funnel. H/48001153720 (mis à jour)
- Domaine racine : enregistrement A, hôte `@`, valeur 162.159.140.166. Sous-domaine : CNAME vers sites.ludicrous.cloud (jamais A et CNAME sur le même hôte). Cloudflare : « DNS only ». Jusqu'à 24 h.
- Changer les DNS = action de l'utilisateur. Avant : vérifie avec `dig` et `curl` ce que le domaine fait tourner aujourd'hui (le basculer coupe l'ancien site).

## 11. La médiathèque
- Fichiers (zip compris) et images : 100 Mo max par l'écran. H/48001216629
- Le nom du fichier dans l'adresse publique : pas écrit. Pour un livrable qui doit garder son nom (ex. un zip + version.json côte à côte), héberge-le ailleurs.

## Astuces vues à l'écran
- Sans domaine connecté, aucune page n'est en ligne : seulement des aperçus `sites.leadconnectorhq.com/preview/<id>`. Le test de paiement de bout en bout demande un domaine.
- Le constructeur de pages et celui des workflows tournent dans un cadre d'un autre site : read_page, find et JavaScript ne les voient pas. Travaille à la capture d'écran.
- Menus déroulants natifs du constructeur : clique, tape les premières lettres de l'option (ex. « Hide »), puis Entrée.
- Coller un long HTML : `LANG=en_US.UTF-8 pbcopy < fichier`, clic dans l'éditeur de code, cmd+v. Sans `LANG`, les accents sont cassés.
- Le chemin `commande` est réservé : prends `paiement`.
- Email d'un workflow : un « From Name » exige un « From Email ». Sans adresse choisie, laisse les deux vides (valeurs par défaut).
- Le déclencheur Instagram reste grisé (« No Instagram page was found ») tant qu'Instagram n'est pas connecté.
- Les fichiers de la médiathèque reçoivent un nom au hasard (…/media/<id>.jpg).
- Nouveau produit : coupe « Include in Online store » (sinon il part dans la boutique).

## Ce que GoHighLevel ne fait pas
- Créer une page de funnel par API ou MCP : navigateur seulement.
- Panier abandonné automatique sur un funnel (voir 7).
- Case d'accord emails séparée sur le formulaire de commande (voir 3).
- Simuler un commentaire Instagram (voir 8).
