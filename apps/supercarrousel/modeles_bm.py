"""4 modèles repris des carrousels de Brian Mark (@therealbrianmark, récupérés le 12/11/2026,
références dans inspirations/brian-mark/). Notre DA (duo de polices, accent), nos vraies photos, jamais d'image IA.

- duo        : chaque slide = 2 photos l'une sur l'autre, une phrase sur chacune (« J'ai demandé… / La vie m'a donné… »)
- soustitres : 2 images d'une même vidéo l'une sur l'autre, la phrase en sous-titre en bas de chaque image
- bulles     : photo plein cadre, texte dans des bulles blanches façon story Instagram
- infographie: fond papier, gros titre condensé en couleur, dessin au centre, ta photo détourée en bas, « Glisse → »

Types de slide (description.json) :
  {"type":"duo", "photo":"p1", "photo2":"p2", "haut":"…", "bas":"…"}         (duo et soustitres)
  {"type":"bulles", "photo":"p1", "blocs":["…","…"], "place":"haut|milieu|bas"}
  {"type":"info", "kicker":"…", "title":"…", "body":"…", "art":"chart_up"|"svg":"x.svg", "photo":"p1"}
  {"type":"fin", "photo":"p1", "title":"…", "cta":"MOT"}                      (dernière slide, tous modèles)
"""
import base64
import os
import re

import apple
from art import ARTS, BLUE, NAVY

W, H = apple.W, apple.H
MODELES_BM = {"duo": "Deux photos", "soustitres": "Sous-titres", "bulles": "Bulles"}  # Infographie retirée le 12/11 (« c'est moche »)
CONDENSEE = "Oswald"  # gros titres de l'infographie (police condensée, dans superda/fonts)


def _faces(da, superda):
    out, vus = "", set()
    duo = da["commun"]["duo"]
    pols = [duo.get("principale", {}), duo.get("secondaire", {}), {"famille": CONDENSEE, "fichier": CONDENSEE + ".ttf"}]
    for pol in pols:
        f = os.path.join(superda, "fonts", pol.get("fichier", ""))
        if pol.get("fichier") and os.path.exists(f) and pol["famille"] not in vus:
            vus.add(pol["famille"])
            out += f'@font-face{{font-family:"{pol["famille"]}";src:url("file://{f}")}}'
    return out


def _propre(t):
    """Pas de point ni de virgule qui traîne en fin de ligne (« ? », « ! », « … » restent)."""
    lignes = re.split(r"(<br\s*/?>)", t or "")
    t = "".join(x if x.startswith("<br") else re.sub(r"(?<![.…])[.,;]\s*$", "", x) for x in lignes)
    return re.sub(r"(?<=\w)'(?=\w)", "’", t)  # apostrophe typographique


def _papier():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300"><filter id="n">'
           '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" stitchTiles="stitch"/>'
           '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .09 0"/></filter>'
           '<rect width="100%" height="100%" filter="url(#n)"/></svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def css(da, superda, modele):
    duo, c = da["commun"]["duo"], da["commun"]["couleurs"]
    p = duo.get("principale", {})
    fp = f'"{p.get("famille", "Outfit")}",-apple-system,sans-serif'
    acc = c.get("accent") or BLUE
    acc_ph = c.get("accent") or "#6CB4FF"  # sur photo sombre : bleu clair lisible
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{_faces(da, superda)}
*{{box-sizing:border-box;margin:0}}
body{{margin:0;background:#000;-webkit-font-smoothing:antialiased}}
.s{{width:{W}px;height:{H}px;position:relative;overflow:hidden;background:#0B0B0D;font-family:{fp}}}
/* duo + sous-titres : 2 images de 1080 x 720 */
.moitie{{position:absolute;left:0;width:{W}px;height:{H // 2 - 3}px;overflow:hidden}}
.moitie img{{width:100%;height:100%;object-fit:cover;filter:brightness(.78) contrast(1.04) saturate(.92)}}
.moitie .ph{{position:absolute;inset:0}}
.phr{{position:absolute;left:70px;right:70px;text-align:center;color:#fff;font-weight:700;letter-spacing:-.01em;
  text-shadow:0 3px 12px rgba(0,0,0,.7),0 1px 3px rgba(0,0,0,.7)}}
.phr em,.bul em{{font-style:normal;color:{acc_ph}}}
.ombre{{position:absolute;left:0;right:0;bottom:0;height:380px;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.78))}}
.duo .phr{{bottom:70px;font-size:58px;line-height:1.15}}
.st .phr{{bottom:56px;font-size:54px;line-height:1.2;font-weight:600}}
/* bulles façon story */
.plein{{position:absolute;inset:0;width:{W}px;height:{H}px;object-fit:cover}}
.pile{{position:absolute;left:70px;right:70px;display:flex;flex-direction:column;align-items:center;gap:26px;text-align:center}}
.bul{{font-weight:700;font-size:52px;line-height:1.42;color:#0B0B0D}}
.bul span{{background:#fff;padding:6px 18px;border-radius:12px;-webkit-box-decoration-break:clone;box-decoration-break:clone}}
.bul.gros{{font-size:68px}}
.bul.bleu span{{background:{acc};color:#fff}}
.bul.bleu em{{color:#fff}}
/* infographie */
.papier{{background:#ECECEA url({_papier()});color:#111}}
.icol{{position:absolute;top:90px;left:80px;right:80px;bottom:400px;display:flex;flex-direction:column;align-items:center;text-align:center}}
.ik{{font:600 30px {fp};letter-spacing:.02em;margin-bottom:18px}}
.it{{font-family:"{CONDENSEE}",{fp};font-weight:700;text-transform:uppercase;color:{acc};line-height:1.2;letter-spacing:-.005em}}
.ib{{font:500 32px/1.35 {fp};color:#222;margin-top:24px;max-width:780px}}
.iart{{flex:1;min-height:0;width:100%;margin-top:20px;display:flex;justify-content:center}}
.iart svg{{height:100% !important;width:100% !important}}
.moi{{position:absolute;left:50%;bottom:-170px;width:480px;height:640px;transform:translateX(-50%);object-fit:cover;object-position:top}}
.glisse{{position:absolute;right:66px;bottom:54px;font:700 24px {fp};letter-spacing:.12em;color:#111;display:flex;gap:14px;align-items:center}}
.glisse b{{color:{acc};font-size:34px}}
/* fin */
.fin .pile{{bottom:150px}}
.phr .motcta{{font-size:1.35em;font-weight:800}}
.bul.bleu .motcta{{font-weight:800}}
.mot{{font-family:"{CONDENSEE}",{fp};font-weight:700;color:{acc};font-size:170px;line-height:1;text-transform:uppercase}}
</style></head><body>"""


def _img(photos, nom, fg=False):
    return photos[nom] + ("-fg.png" if fg else ".jpg")


def _pos(heads, nom):
    """Centre la moitié (1080 x 720) sur la tête : le haut du crâne + 260 px ≈ le visage."""
    if heads is not None and nom in heads and heads[nom] is None:
        return "50% 35%"  # image de vidéo entière (Sous-titres)
    h = (heads or {}).get(nom) or 300
    return f"50% {min(max((h + 260 - 360) / (H - 720) * 100, 0), 100):.0f}%"


def slide(s, last, photos, da, spec_dir, modele, heads=None):
    t = s["type"]
    if t in ("duo", "photo", "cover") and modele in ("duo", "soustitres"):
        cls = "st" if modele == "soustitres" else "duo"
        p1, p2 = s["photo"], s.get("photo2") or s["photo"]
        haut, bas = s.get("haut") or s.get("title", ""), s.get("bas") or s.get("body", "")
        ombre = '<div class="ombre"></div>' if cls == "st" else ""

        def moitie(nom, txt, y, cle):
            ici = f' style="bottom:{s[cle]}px"' if s.get(cle) is not None else ""  # hauteur du texte réglable (px depuis le bas)
            return (f'<div class="moitie" style="top:{y}px"><img class="ph" src="{_img(photos, nom)}" '
                    f'style="object-position:{_pos(heads, nom)}">{ombre}<div class="phr"{ici}>{_propre(txt)}</div></div>')
        return f'<div class="s {cls}">{moitie(p1, haut, 0, "y_haut")}{moitie(p2, bas, H // 2 + 3, "y_bas")}</div>'
    if t == "bulles" or (modele == "bulles" and t in ("photo", "cover")):
        def pile(blocs, depart, place):
            b = "".join(f'<div class="bul{" gros" if depart + i in s.get("gros", []) else ""}{" bleu" if depart + i in s.get("bleu", []) else ""}">'
                        f'<span>{_propre(x)}</span></div>' for i, x in enumerate(blocs))
            return f'<div class="pile" style="{place}">{b}</div>' if blocs else ""
        blocs = s.get("blocs") or [x for x in (s.get("title"), s.get("body")) if x]
        bas = s.get("blocs_bas") or []  # 2e groupe en bas : libère le visage et le corps
        place = {"haut": "top:130px", "bas": "bottom:150px"}.get(s.get("place"), "top:85px" if bas else "top:50%;transform:translateY(-50%)")
        return (f'<div class="s"><img class="plein" src="{_img(photos, s["photo"])}" style="object-position:{s.get("cadre", "50% 30%")}">'
                f'{pile(blocs, 0, place)}{pile(bas, len(blocs), "bottom:100px")}</div>')
    if t == "info" or modele == "infographie" and t != "fin":
        kick = f'<div class="ik">{s["kicker"]}</div>' if s.get("kicker") else ""
        titre = f'<div class="it t" style="font-size:{s.get("title_size", 96)}px">{_propre(s.get("title", ""))}</div>'
        corps = f'<div class="ib">{s["body"]}</div>' if s.get("body") else ""
        art = ""
        if s.get("svg"):
            art = open(os.path.join(spec_dir, os.path.expanduser(s["svg"]))).read()
        elif s.get("art"):
            art = ARTS[s["art"]](**s.get("args", {}))
        if art:
            art = f'<div class="iart">{art}</div>'
        moi = f'<img class="moi" src="{_img(photos, s["photo"], fg=True)}">' if s.get("photo") else ""
        gl = "" if last else '<div class="glisse">GLISSE <b>→</b></div>'
        return f'<div class="s papier"><div class="icol">{kick}{titre}{corps}{art}</div>{moi}{gl}</div>'
    if t == "fin":
        mot = s.get("cta", "").upper()
        if modele == "infographie":
            moi = f'<img class="moi" src="{_img(photos, s["photo"], fg=True)}">' if s.get("photo") else ""
            return (f'<div class="s papier"><div class="icol" style="top:170px">'
                    f'<div class="ik" style="font-size:44px">{_propre(s.get("title", ""))}</div>'
                    f'<div class="ik" style="font-size:36px;margin-top:20px">Écris en commentaire</div>'
                    f'<div class="it" style="font-size:210px;line-height:1">{mot}</div>'
                    f'<div class="ik" style="font-size:36px;margin-top:10px">et je te l’envoie</div></div>{moi}</div>')
        # 12/11 (l’utilisateur : « cohérence du CTA avec les autres images ») : la dernière slide garde la forme du modèle
        appel = f'Écris <em class="motcta">{mot}</em> en commentaire'
        if modele == "bulles":
            return slide(dict(s, type="bulles", blocs=[s.get("title", "")], blocs_bas=[appel], gros=[1], bleu=[1]),
                         last, photos, da, spec_dir, modele, heads)
        return slide(dict(s, type="duo", haut=s.get("title", ""), bas=appel, photo2=s.get("photo2") or s["photo"]),
                     last, photos, da, spec_dir, modele, heads)
    raise ValueError(f"type de slide inconnu pour {modele} : {t}")
