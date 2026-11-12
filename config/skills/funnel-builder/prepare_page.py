"""Prépare la page de vente du Copywriter pour l'élément de code de GoHighLevel.

1er passage (liste les images à envoyer dans la médiathèque GHL) :
    python3 prepare_page.py <page.html> --sortie <dossier>
    -> <dossier>/images.json = {"carte.jpg": "", ...} à remplir avec l'adresse de chaque image une fois envoyée

2e passage (page prête à coller) :
    python3 prepare_page.py <page.html> --sortie <dossier> --images <dossier>/images.json --commande <lien de l'étape commande>
    -> <dossier>/page-ghl.html : un morceau de page (polices + style + contenu + script), sans <html>, <head> ni <body>,
       images remplacées, chaque bouton href="#" pointé vers la commande (les ancres #section restent).

Refuse si une image locale n'a pas d'adresse, ou si un bouton reste sans lien.
"""
import json, pathlib, re, sys

args = sys.argv[1:]

def option(nom):
    if nom in args:
        i = args.index(nom); v = args[i + 1]; del args[i:i + 2]; return v
    return None

sortie = pathlib.Path(option('--sortie') or '.').expanduser()
images_json = option('--images')
commande = option('--commande')
if len(args) != 1:
    sys.exit(__doc__)
page = pathlib.Path(args[0]).expanduser()
html = page.read_text(encoding='utf-8')
sortie.mkdir(parents=True, exist_ok=True)

# Images locales : src="x.jpg" et url(x.jpg), hors http(s), data: et ancres
LOCAL = r'(?!https?:|data:|#|//)[^"\')\s]+\.(?:png|jpe?g|webp|gif|svg|mp4)'
locales = sorted(set(re.findall(r'src="(' + LOCAL + ')"', html)) | set(re.findall(r'url\([\'"]?(' + LOCAL + r')[\'"]?\)', html)))

if not images_json:
    modele = {nom: '' for nom in locales}
    (sortie / 'images.json').write_text(json.dumps(modele, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'IMAGES {len(locales)} à envoyer dans la médiathèque GHL :')
    for nom in locales:
        f = page.parent / nom
        print(f'- {nom} ({f.stat().st_size / 1e3:.0f} ko)' if f.is_file() else f'- {nom} (INTROUVABLE à côté de la page)')
    print(f'Puis remplis {sortie / "images.json"} et relance avec --images et --commande.')
    sys.exit(0)

if not commande:
    sys.exit('MANQUE : --commande <lien de l\'étape commande>')
carte = json.loads(pathlib.Path(images_json).expanduser().read_text(encoding='utf-8'))
vides = [n for n in locales if not carte.get(n, '').startswith('http')]
if vides:
    sys.exit('IMAGES SANS ADRESSE : ' + ', '.join(vides))
for nom in locales:
    html = html.replace(f'src="{nom}"', f'src="{carte[nom]}"')
    html = re.sub(r'url\([\'"]?' + re.escape(nom) + r'[\'"]?\)', f'url({carte[nom]})', html)

n_boutons = len(re.findall(r'<a\b[^>]*href="#"', html))
html = re.sub(r'(<a\b[^>]*?)href="#"', lambda m: f'{m.group(1)}href="{commande}"', html)

# Morceau de page : on garde polices, style, contenu du body et scripts ; GHL fournit html/head/body
tete = re.search(r'<head[^>]*>(.*?)</head>', html, re.S | re.I)
corps = re.search(r'<body[^>]*>(.*?)</body>', html, re.S | re.I)
if not corps:
    sys.exit('PAS DE <body> : la page du Copywriter doit être un HTML complet.')
garde = ''
if tete:
    garde = '\n'.join(re.findall(r'<link\b[^>]*>|<style\b.*?</style>', tete.group(1), re.S | re.I))
titre = re.search(r'<title>(.*?)</title>', html, re.S | re.I)
# GHL entoure l'élément de code d'une section, d'une ligne (1 170 px max) et d'une colonne avec des marges : on les retire
pleine_largeur = ('<style>.c-section:has(.c-custom-code),.c-row:has(.c-custom-code),.c-column:has(.c-custom-code),'
                  '.c-section:has(.c-custom-code)>.inner,.c-row:has(.c-custom-code)>.inner,.c-column:has(.c-custom-code)>.inner'
                  '{padding:0!important;margin:0!important;max-width:none!important;width:100%!important}</style>')
morceau = garde + '\n' + pleine_largeur + '\n' + corps.group(1).strip() + '\n'
(sortie / 'page-ghl.html').write_text(morceau, encoding='utf-8')

print(f'PAGE {sortie / "page-ghl.html"} ({len(morceau.encode()) / 1e3:.0f} ko)')
ancres = len(re.findall(r'<a\b[^>]*href="#\w', morceau))
print(f'IMAGES remplacées : {len(locales)} · BOUTONS vers la commande : {n_boutons} · ancres gardées : {ancres}')
if titre:
    print(f'TITRE à mettre dans les réglages SEO de la page GHL : {titre.group(1).strip()}')
if n_boutons == 0:
    print('ATTENTION : aucun bouton href="#" trouvé, vérifie que la page mène bien à la commande.')
