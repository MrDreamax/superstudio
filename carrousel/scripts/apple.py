"""Style « Apple » des carrousels (validé par l’utilisateur le 22/10/2026, 2 rounds), appelé par carrousel.py quand
la description contient "style": "apple". Rendu en local avec Chrome (pas besoin d'Open Carrusel).
  Fond blanc, titres SF Pro gras serrés, sous-titre gris, notes manuscrites Kalam couleur principale.
  Photo BORD À BORD (touche les bords gauche et droit) ; la personne détourée dépasse au-dessus : seulement les cheveux.
  Dessins sur le cercle clair d'art.py. Dernière slide : 3 bulles de message (question / MOT / réponse).
Types de slide :
  cover : "kicker" (petit titre), "title", "photo", "accent" (mot clé en bleu) ; « sujet géant » du 07/11/2026,
          "cover_style": "ancienne" = photo bord à bord + cheveux qui dépassent (22/10)
  photo : "photo", "title", "body" | "steps" ; "pop": false = photo sans dépassement (sujet petit dans l'image)
  list  : "kicker", "title", "items" [{"icon" (ICONS), "t", "d"}] ; "gap", "top", "title_size" (12/11/2026)
  art   : "art" (art.py) ou "svg", "title", "body" | "steps" | "cta" (+ "cta_q", "cta_line")
Commun : "note" + "note_pos" ({"top":..,"left"|"right":..}) pour une note manuscrite de 3 à 5 mots.
"""
import os
import re
import subprocess

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageOps
from scipy import ndimage

from art import ARTS, BLUE

W, H = 1080, 1440
MODEL = os.path.expanduser("~/.cache/supermonteur/rvm_mobilenetv3_fp32.onnx")  # modèle du skill supermonteur
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HAIR = 110  # pixels de cheveux qui dépassent au-dessus de la photo (choix de l’utilisateur : « jusqu'aux cheveux »)
INK, MUTE, GRAY = "#1D1D1F", "#6E6E73", "#E9E9EB"

CSS = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0}}
body{{margin:0;background:#fff;font-family:-apple-system,"SF Pro Display",system-ui,sans-serif;-webkit-font-smoothing:antialiased;color:{INK}}}
.s{{width:{W}px;height:{H}px;position:relative;overflow:hidden;background:#fff}}
.t{{font-weight:700;letter-spacing:-.035em;line-height:1.02}}
.k{{font-size:34px;font-weight:600;color:{BLUE}}}
.sub{{font-size:40px;color:{MUTE};margin-top:24px;letter-spacing:-.01em;line-height:1.3}}
.ctr{{text-align:center}}
.note{{position:absolute;font-family:Kalam,cursive;color:{BLUE};font-size:44px;transform:rotate(-4deg);z-index:5;white-space:nowrap}}
.arrow{{position:absolute;right:56px;bottom:52px;font-size:44px;color:#86868B}}
.card{{position:absolute;left:0;width:{W}px;background-repeat:no-repeat;background-size:{W}px {H}px}}
.pop{{position:absolute;left:0;top:0;width:{W}px;overflow:hidden}}
.pop img{{position:absolute;left:0;width:{W}px;height:{H}px}}
.art{{display:block;width:{W}px;height:900px}}
.steps{{display:inline-flex;flex-direction:column;gap:22px;text-align:left;margin-top:30px}}
.step{{display:flex;gap:24px;align-items:center;font-size:40px;letter-spacing:-.01em}}
.n{{flex:0 0 60px;height:60px;border-radius:50%;background:{BLUE};color:#fff;font-weight:700;font-size:30px;display:flex;align-items:center;justify-content:center}}
.chat{{position:absolute;left:90px;right:90px;display:flex;flex-direction:column;gap:22px;font-size:42px;line-height:1.25}}
.b{{padding:22px 38px;max-width:780px}}
.them{{align-self:flex-start;background:{GRAY};border-radius:40px 40px 40px 12px}}
.me{{align-self:flex-end;background:#0A84FF;color:#fff;font-weight:600;border-radius:40px 40px 12px 40px}}
.ic{{flex:0 0 120px;height:120px;border-radius:50%;background:#EAF3FB;color:{BLUE};display:flex;align-items:center;justify-content:center}}
.li{{display:flex;gap:40px;align-items:center}}
.li b{{display:block;font-size:48px;letter-spacing:-.025em;line-height:1.1}}
.li span{{display:block;font-size:34px;color:{MUTE};margin-top:8px;line-height:1.25;letter-spacing:-.01em}}
</style></head><body>"""


def prep_photo(p, name, work):
    """Recadrage 3:4 aux teintes naturelles + détourage local (RVM). Renvoie le haut de la tête (px)."""
    im = ImageOps.exif_transpose(Image.open(p["src"])).convert("RGB")
    iw, ih = im.size
    cw = min(iw, ih * 3 / 4) / p.get("zoom", 1.0)
    ch = cw * 4 / 3
    cx = min(max(p.get("fx", 0.5) * iw, cw / 2), iw - cw / 2)
    cy = min(max(p.get("fy", 0.45) * ih, ch / 2), ih - ch / 2)
    im = im.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.LANCZOS)
    im.save(f"{work}/{name}.jpg", quality=92)
    rgb = np.asarray(im, np.float32) / 255
    sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    x = rgb.transpose(2, 0, 1)[None]
    rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
    for _ in range(4):  # même image 4 fois pour stabiliser l'état récurrent de RVM
        _, pha, *rec = sess.run(None, {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3],
                                       "downsample_ratio": np.array([0.25], np.float32)})
    alpha = np.where(pha[0, 0] < 0.15, 0, pha[0, 0])  # coupe le voile de bruit autour du sujet
    lab, n = ndimage.label(alpha > 0.5)
    if n > 1:  # ne garde que la plus grande tache (la personne) : pas de traînées isolées au-dessus de la photo
        keep = np.argmax(ndimage.sum(np.ones_like(alpha), lab, range(1, n + 1))) + 1
        alpha = alpha * ndimage.binary_dilation(lab == keep, iterations=6)
    ys = np.where(alpha > 0.5)[0]
    head = int(ys.min()) if len(ys) else 0
    # au-dessus de la photo, seule la tête dépasse : on garde la tache qui part du haut du crâne et on efface
    # mains, doigts et bruit qui ne la touchent pas (sans couper les côtés des cheveux)
    cut = head + HAIR + 5
    lab, _ = ndimage.label(alpha[:cut] > 0.5)
    top = lab[head][alpha[head] > 0.5]
    if len(top):
        alpha[:cut] *= ndimage.binary_dilation(lab == np.bincount(top).argmax(), iterations=4)
    Image.fromarray((np.dstack([rgb, alpha]) * 255).astype(np.uint8)).save(f"{work}/{name}-fg.png")
    return head


def photo_block(name, head, top, h, pop=True):
    """Photo bord à bord de `top` à `top+h` ; si pop, les cheveux détourés dépassent de HAIR px au-dessus."""
    off = min(max(head + HAIR, 0), H - h) if pop else max(0, min(H - h, int(head - 120)))
    html = f'<div class="card" style="top:{top}px;height:{h}px;background-image:url({name}.jpg);background-position:0 {-off}px"></div>'
    if pop:  # le détourage ne sert qu'AU-DESSUS de la photo : dedans, la vraie photo reste intacte
        html += f'<div class="pop" style="height:{top}px"><img src="{name}-fg.png" style="top:{top - off}px"></div>'
    return html

# Icônes au trait pour le type "list" (12/11/2026), dessinées dans un carré 48x48, trait bleu
ICONS = {
    "grille": '<rect x="7" y="7" width="14" height="14" rx="3"/><rect x="27" y="7" width="14" height="14" rx="3"/><rect x="7" y="27" width="14" height="14" rx="3"/><rect x="27" y="27" width="14" height="14" rx="3"/>',
    "cible": '<circle cx="24" cy="24" r="17"/><circle cx="24" cy="24" r="10"/><circle cx="24" cy="24" r="3" fill="currentColor"/>',
    "eclair": '<path d="M27 5 11 27h12l-3 16 17-23H25z" stroke-linejoin="round"/>',
    "alerte": '<path d="M24 6 4 41h40z" stroke-linejoin="round"/><path d="M24 19v10"/><circle cx="24" cy="35" r="1.5" fill="currentColor"/>',
    "bulle": '<path d="M8 10h32a3 3 0 0 1 3 3v18a3 3 0 0 1-3 3H20l-9 7v-7H8a3 3 0 0 1-3-3V13a3 3 0 0 1 3-3z" stroke-linejoin="round"/><path d="M15 20h18M15 26h11"/>',
    "camera": '<rect x="4" y="13" width="28" height="22" rx="4"/><path d="m32 21 12-7v20l-12-7z" stroke-linejoin="round"/>',
    "cadeau": '<rect x="6" y="18" width="36" height="24" rx="3"/><path d="M4 12h40v6H4zM24 12v30M24 12c-4-8-13-6-10 0M24 12c4-8 13-6 10 0"/>',
}


def icon(name):
    return (f'<div class="ic"><svg viewBox="0 0 48 48" width="64" height="64" fill="none" stroke="currentColor" '
            f'stroke-width="3.2" stroke-linecap="round">{ICONS[name]}</svg></div>')


def text(s, size):
    out = f'<h2 class="t" style="font-size:{s.get("title_size", size)}px">{s["title"]}</h2>'
    if s.get("body"):
        out += f'<p class="sub">{s["body"]}</p>'
    if s.get("steps"):
        out += '<div class="steps">' + "".join(f'<div class="step"><div class="n">{i}</div><div>{t}</div></div>'
                                              for i, t in enumerate(s["steps"], 1)) + "</div>"
    return out


def note(s):
    if not s.get("note"):
        return ""
    pos = ";".join(f"{k}:{v}px" for k, v in s.get("note_pos", {"top": 470, "right": 60}).items())
    return f'<div class="note" style="{pos}">{s["note"]}</div>'


# ---- Couverture « sujet géant » (remède 1 d'Ayo, VALIDÉE par l’utilisateur le 07/11/2026, 2 rounds) ----
# Fond blanc, titre à gauche 2 lignes 165 px, seul le mot "accent" en bleu, tête détourée en très grand dont les
# cheveux frôlent le bas du titre, ombre douce, aucun bouton. Modèle : (exemple retiré)
COVERS = {}
SWIFT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "detoure.swift")
HEAD_W, HEAD_CX, OVER = 549, 696, 49  # calés sur A-final.png  # largeur de la tête à l'écran, son centre, cheveux qui mangent le titre (px)


def prep_cover(name, work):
    """Détourage complet par la détection de sujet Apple (garde micro et mains), puis mesure de la tête."""
    fg = f"{work}/{name}-fgv.png"
    subprocess.run(["swift", SWIFT, f"{work}/{name}.jpg", fg], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    a = np.asarray(Image.open(fg))[:, :, 3] > 128
    ys = np.where(a.any(1))[0]
    top, bot = int(ys.min()), int(ys.max())
    band = a[top:top + max(120, int(.18 * (bot - top)))]
    cols = np.where(band.any(0))[0]  # largeur de la tête = haut du sujet (18 % de sa hauteur)
    COVERS[name] = dict(top=top, bot=bot, cx=float(cols.mean()), w=float(cols.max() - cols.min() + 1))
    if HEAD_W / COVERS[name]["w"] > 2.4:  # personne en pied ou petite : la tête géante serait floue
        COVERS[name]["petit"] = True
        print(f"  ! couverture : sujet trop petit dans « {name} », ancienne couverture utilisée (prends une photo cadrée buste)")


def cover_geant(s):
    p, c = s["photo"], COVERS[s["photo"]]
    if c.get("petit"):
        return None
    size = s.get("title_size", 165)
    title = s["title"]
    acc = s.get("accent")
    if acc and acc in title:  # seul le mot clé en bleu (dernière occurrence)
        i = title.rfind(acc)
        title = title[:i] + f'<span style="color:{BLUE}">{acc}</span>' + title[i + len(acc):]
    lignes = [re.sub(r"<[^>]+>", "", l) for l in s["title"].split("<br>")]
    size = min(size, int(940 / (.42 * max(len(l) for l in lignes))))  # chaque ligne tient sur la largeur
    bottom = 150 + len(lignes) * size * .9
    sc = min(max(HEAD_W / c["w"], 1.0), 2.4) * s.get("zoom_tete", 1.0)
    fin = 64 + .42 * size * len(lignes[-1])  # bout de la dernière ligne du titre
    # les cheveux ne frôlent le titre que si la dernière ligne s'arrête avant la tête ; sinon la tête passe dessous
    y_hair = bottom - OVER if fin < HEAD_CX else bottom + 24
    if y_hair + (c["bot"] - c["top"]) * sc < H:  # le sujet doit toucher le bas de la slide
        sc = (H - y_hair) / (c["bot"] - c["top"])
    X, Y = HEAD_CX - c["cx"] * sc, y_hair - c["top"] * sc
    kicker = f'<div class="k" style="font-size:32px">{s["kicker"]}</div>' if s.get("kicker") else ""
    hx0, hx1 = HEAD_CX - .62 * c["w"] * sc, HEAD_CX + .62 * c["w"] * sc  # au-dessus du bas du titre : la tête seule
    clip = f"polygon({hx0:.0f}px 0,{hx1:.0f}px 0,{hx1:.0f}px {bottom:.0f}px,{W}px {bottom:.0f}px,{W}px {H}px,0 {H}px,0 {bottom:.0f}px,{hx0:.0f}px {bottom:.0f}px)"
    return (f'<div style="position:absolute;left:64px;top:96px">{kicker}'
            f'<h1 class="t" style="font-size:{size}px;font-weight:800;letter-spacing:-.045em;line-height:.9;margin-top:22px">{title}</h1></div>'
            f'<div style="position:absolute;inset:0;clip-path:{clip};filter:drop-shadow(0 6px 22px rgba(0,0,0,.16))">'
            f'<img src="{p}-fgv.png" style="position:absolute;left:{X:.0f}px;top:{Y:.0f}px;width:{W*sc:.0f}px;height:{H*sc:.0f}px"></div>')


def slide(s, last, heads, spec_dir):
    arrow = "" if last else '<div class="arrow">→</div>'
    t = s["type"]
    geant = cover_geant(s) if t == "cover" and s.get("cover_style") != "ancienne" else None
    if geant:
        inner, arrow = geant, ""  # validée le 07/11/2026 : pas de flèche ni de bouton sur la couverture
    elif t == "cover":
        p = s["photo"]
        kicker = f'<div class="k">{s["kicker"]}</div>' if s.get("kicker") else ""
        inner = (f'<div class="ctr" style="padding-top:110px">{kicker}'
                 f'<h1 class="t" style="font-size:{s.get("title_size", 112)}px;margin-top:18px">{s["title"]}</h1></div>'
                 + photo_block(p, heads[p], s.get("photo_top", 620), 700))
    elif t == "photo":
        p = s["photo"]
        pop = s.get("pop", True)  # sans dépassement (sujet petit dans l'image) : la photo part du haut de la slide
        inner = (photo_block(p, heads[p], 300 if pop else 0, 700 if pop else 1000, pop)
                 + f'<div class="ctr" style="position:absolute;left:60px;right:60px;top:{1050 if pop else 1060}px">{text(s, 92)}</div>')
    elif t == "list":  # liste à icônes (12/11/2026) : kicker + titre en haut, puis une ligne par élément
        kicker = f'<div class="k">{s["kicker"]}</div>' if s.get("kicker") else ""
        rows = "".join(f'<div class="li">{icon(it["icon"])}<div><b>{it["t"]}</b>'
                       + (f'<span>{it["d"]}</span>' if it.get("d") else "") + '</div></div>'
                       for it in s["items"])
        gap = s.get("gap", 56)
        inner = (f'<div style="padding:{s.get("top", 120)}px 80px 0">{kicker}'
                 f'<h2 class="t" style="font-size:{s.get("title_size", 96)}px;margin-top:18px">{s["title"]}</h2>'
                 f'<div style="display:flex;flex-direction:column;gap:{gap}px;margin-top:80px">{rows}</div></div>')
    elif t == "art":
        if s.get("photo") and s.get("cta"):  # 12/11/2026 : fin avec une vraie photo (conférence) au lieu d'un dessin
            art = f'<div style="height:660px"></div>' + photo_block(s["photo"], heads[s["photo"]], 0, s.get("photo_h", 640), False)
        elif s.get("svg"):
            art = open(os.path.join(spec_dir, os.path.expanduser(s["svg"]))).read()
        else:
            art = ARTS[s["art"]](**s.get("args", {}))
        if s.get("cta"):  # dernière slide : dessin plus petit + 3 bulles de message
            if not s.get("photo"):
                art = art.replace('<svg class="art"', '<svg class="art" style="height:660px"', 1)
            q = s.get("cta_q", "Tu veux la ressource ?")
            dy = s.get("cta_shift", 0)  # 12/11/2026 : descend titre + bulles quand le bas reste vide
            inner = (f'<div style="height:{dy}px"></div>' + art + f'<div class="ctr">{text(s, 84)}</div>'
                     f'<div class="chat" style="top:{930 + dy}px"><div class="b them">{q}</div><div class="b me">{s["cta"].upper()}</div>'
                     f'<div class="b them">{s.get("cta_line", "Envoyé en DM. Bonne lecture.")}</div></div>'
                     f'<div class="note" style="top:{1070 + dy}px;left:110px">écris ça en commentaire →</div>')
        else:
            inner = art + f'<div class="ctr" style="padding:0 60px">{text(s, 104)}</div>'
    else:
        raise ValueError(f"type de slide inconnu : {t}")
    return f'<div class="s">{inner}{note(s)}{arrow}</div>'


def build(spec, spec_dir, out):
    work = os.path.join(out, "_sources")
    os.makedirs(work, exist_ok=True)
    heads = {n: prep_photo(p, n, work) for n, p in spec.get("photos", {}).items()}
    slides = spec["slides"]
    for s in slides:
        if s["type"] == "cover" and s.get("cover_style") != "ancienne":
            prep_cover(s["photo"], work)
    for i, s in enumerate(slides, 1):
        page = os.path.join(work, f"slide-{i}.html")
        with open(page, "w") as f:
            f.write(CSS + slide(s, i == len(slides), heads, spec_dir) + "</body></html>")
        subprocess.run([CHROME, "--headless=new", "--use-mock-keychain", "--disable-gpu", "--hide-scrollbars",
                        "--virtual-time-budget=8000", f"--window-size={W},{H}", f"--screenshot={out}/slide-{i}.png",
                        f"file://{page}"], stderr=subprocess.DEVNULL, check=True)
    return len(slides)
