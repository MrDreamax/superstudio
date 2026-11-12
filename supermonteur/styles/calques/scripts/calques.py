"""Style Calques : reprise du reel @viashaan « mots derrière la tête » (Brain/02-Formations/
viashaan-sous-titres-ia-derriere-la-tete.md). Chaque image = une pile : décor, mots DERRIÈRE toi, toi (masque de detoure.py),
mots DEVANT, lueurs. Une caméra virtuelle recadre chaque phrase (zoom, poussée lente, à-coup) comme si c'était un autre plan.
Un style par scène :
  orbite   mots qui tournent autour de la tête (moitié derrière, moitié devant)
  choc     un mot géant qui fonce vers la caméra (flou de vitesse, secousse)
  neon     sous-titres qui brillent + mot-clé en néon rose, image teintée
  lueur    sous-titres blancs qui brillent
  geant    mot géant en couleur derrière la tête, petits sous-titres au-dessus
  tracking fond crème, silhouette noire, cadre jaune sur le visage, mot en serif italique
  contour  pointillés qui suivent ton corps + texte qui longe ta silhouette
  serif    mot géant serif italique derrière la tête, vignette
  filaire  décor remplacé par une pièce en lignes blanches 3D
  or       mot géant doré 3D derrière la tête, petit texte en arc, flèche
  python3 calques.py plan.json                 -> rendu.mp4 (+ sons) dans le dossier du plan
  python3 calques.py plan.json --images 1.0,5.2 -> images PNG seulement (réglage rapide)
Zones Instagram respectées (memory instagram-dead-zones) : texte entre 270 et 1480 px, 65 px des bords, 120 px à droite en bas.
"""
import json, math, os, random, subprocess, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

SK = os.path.expanduser("~/.claude/skills/supermonteur")
FONTS = os.path.join(SK, "fonts")
W, H, FPS = 1080, 1920, 30
TOP, BOT, MX = 270, 1480, 65
random.seed(7)

# ------------------------------------------------------------------ polices et sprites
_F, _S = {}, {}


def font(name, size, wght=None, wdth=None):
    k = (name, size, wght, wdth)
    if k not in _F:
        p = name if name.startswith("/") else os.path.join(FONTS, name)
        f = ImageFont.truetype(p, int(size))
        try:
            vals = []
            for a in f.get_variation_axes():
                n = a["name"].decode() if isinstance(a["name"], bytes) else str(a["name"])
                vals.append(wght if (n == "Weight" and wght) else wdth if (n == "Width" and wdth) else a["default"])
            f.set_variation_by_axes(vals)
        except Exception:
            pass
        _F[k] = f
    return _F[k]


def sprite(text, fnt, fill=(255, 255, 255)):
    """Texte -> RGBA prémultiplié float32 (marge = 0,5 x taille pour flou et lueur). Centre du sprite = centre du texte."""
    k = (text, id(fnt), fill)
    if k in _S: return _S[k]
    l, t, r, b = fnt.getbbox(text)
    pad = int(fnt.size * 0.5)
    im = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - l, pad - t), text, font=fnt, fill=tuple(fill) + (255,))
    a = np.asarray(im, np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    _S[k] = a
    return a


def teinte(spr, rgb, alpha=1.0):
    o = np.zeros_like(spr)
    o[..., 3] = spr[..., 3] * alpha
    o[..., :3] = o[..., 3:4] * (np.array(rgb, np.float32) / 255)
    return o


def paste(cv, spr, cx, cy, scale=1.0, rot=0.0, op=1.0, blur=0.0):
    if op <= 0.01 or scale <= 0.01: return
    h, w = spr.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale)
    M[0, 2] += cx - w / 2; M[1, 2] += cy - h / 2
    c = np.array([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]], np.float32) @ M.T
    x0, x1 = int(max(0, c[:, 0].min() - 2)), int(min(cv.shape[1], c[:, 0].max() + 2))
    y0, y1 = int(max(0, c[:, 1].min() - 2)), int(min(cv.shape[0], c[:, 1].max() + 2))
    if x1 <= x0 or y1 <= y0: return
    M[0, 2] -= x0; M[1, 2] -= y0
    o = cv2.warpAffine(spr, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if blur > 0.4: o = cv2.GaussianBlur(o, (0, 0), blur)
    if op < 1: o *= op
    reg = cv[y0:y1, x0:x1]
    reg[:] = o + reg * (1 - o[..., 3:4])


OMBRE = [0.55]   #  (mur clair, RUSH) : "ombre": 0.9 dans plan.json = ombre plus forte sous les textes blancs


def ombre(cv, spr, cx, cy, scale=1.0, rot=0.0, op=1.0, blur=0.0, force=None, dy=5):
    paste(cv, teinte(spr, (0, 0, 0), OMBRE[0] if force is None else force), cx, cy + dy * scale, scale, rot, op, blur + 7 * scale)


def vecteur(cv, dessine):
    """Dessin PIL (traits, flèches, HUD) sur un calque plein cadre, collé dans cv."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dessine(ImageDraw.Draw(im), im)
    a = np.asarray(im, np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    cv[:] = a + cv * (1 - a[..., 3:4])


def ease(u): u = min(max(u, 0.0), 1.0); return 1 - (1 - u) ** 3


def pop(u, depart=0.8, depasse=0.05):
    """80 % -> 105 % -> 100 % (6 images à 30 i/s = u de 0 à 1 en 0,2 s)."""
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    if u < 0.6: return depart + (1 + depasse - depart) * ease(u / 0.6)
    return 1 + depasse * (1 - ease((u - 0.6) / 0.4))


# ------------------------------------------------------------------ mots
def propre(t):
    t = t.replace("'", "’").strip()
    t = t.rstrip(",.;:")
    lo = t.lower()
    lo = lo.replace("l’ia", "l’IA")
    if lo in ("ia", "ia?"): lo = lo.replace("ia", "IA")
    return lo


def groupes(mots, maxi=3):
    out, cur = [], []
    for m in mots:
        cur.append(m)
        if len(cur) >= maxi or m["text"][-1:] in ",.?!": out.append(cur); cur = []
    if cur: out.append(cur)
    return out


def apparition(t, debut, dur=0.13):
    """0 -> 1 quand le mot sort de ta bouche (flou 8 -> 0, monte de 14 px)."""
    return ease((t - debut + 0.02) / dur)


def ligne(cv, mots, t, cx, y, fnt, fill=(255, 255, 255), glow=None, glowcv=None, shadow=True, gap=None, monte=14, maj=False):
    """Une ligne de sous-titres centrée, chaque mot apparaît sur sa voix."""
    sprs = [sprite(propre(m["text"]).upper() if maj else propre(m["text"]), fnt, fill) for m in mots]
    gap = gap if gap is not None else fnt.size * 0.28
    pad = int(fnt.size * 0.5)
    ws = [s.shape[1] - 2 * pad for s in sprs]
    tot = sum(ws) + gap * (len(ws) - 1)
    k = min(1.0, (W - 2 * MX - 20) / max(tot, 1))   # gros sous-titres, une ligne trop large rétrécit
    ws = [w_ * k for w_ in ws]; gap *= k; tot *= k
    x = max(MX, min(W - MX - tot, cx - tot / 2))
    for s, w_, m in zip(sprs, ws, mots):
        u = apparition(t, m["start"])
        if u > 0:
            px, py = x + w_ / 2, y + monte * (1 - u)
            if shadow: ombre(cv, s, px, py, k, op=u, blur=8 * (1 - u))
            paste(cv, s, px, py, k, op=u, blur=8 * (1 - u))
            if glow is not None and glowcv is not None: paste(glowcv, teinte(s, glow), px, py, k, op=u)
        x += w_ + gap
    return tot


def sous_menton(c, y):
    """(juge : « virus cognitif » sur le menton) : y jamais au-dessus de bas du visage + 50 px, jamais sous 1420 px."""
    top, hx, hw = c["tete"]
    return min(0.74 * H, max(y, top + 1.45 * hw + 50))


def groupes_sans(ws, exclus, maxi=3):
    ids = {id(m) for m in exclus}
    return [g2 for g2 in ([m for m in g if id(m) not in ids] for g in groupes(ws, maxi)) if g2]


def suite(ws, cle):
    """Mots de ws qui forment la suite « cle » (minuscules, apostrophes ’). -> liste ou []"""
    cl = [propre(x).lower() for x in cle.split()]
    for i in range(len(ws)):
        if [propre(x["text"]).lower() for x in ws[i:i + len(cl)]] == cl: return ws[i:i + len(cl)]
    return []


def groupe_du_moment(gs, t):
    cur = None
    for g in gs:
        if g[0]["start"] - 0.02 <= t: cur = g
    return cur


# ------------------------------------------------------------------ tête et contour
def tete(m):
    """m = masque 0-1 (plein cadre ou réduit). -> (haut, centre x, largeur tête) en px du cadre 1080x1920."""
    h, w = m.shape
    s = W / w
    c0, c1 = int(w * 0.3), int(w * 0.7)   # 40 % du milieu : une main levée ne compte pas (prompt viashaan)
    rows = np.where(m[:, c0:c1].max(1) > 0.5)[0]
    if len(rows) == 0: return None
    top = rows[0]
    xt = c0 + int(np.mean(np.where(m[top, c0:c1] > 0.5)[0]))
    r = min(h - 1, top + int(0.06 * h))
    on = m[r] > 0.5
    if not on[xt]:
        cols = np.where(on)[0]
        if len(cols) == 0: return None
        xt = cols[np.argmin(abs(cols - xt))]
    a = xt
    while a > 0 and on[a - 1]: a -= 1
    b = xt
    while b < w - 1 and on[b + 1]: b += 1
    return top * s, (a + b) / 2 * s, (b - a) * s


def chemin_corps(ms):
    """Contour du corps : de bas-gauche, par-dessus la tête, jusqu'à bas-droite. -> points (N,2) tous les 2 px + normales."""
    small = cv2.resize(ms, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    small = cv2.morphologyEx(small, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))   # bras/mains fins gommés
    small = cv2.GaussianBlur(small, (0, 0), 6)
    b = cv2.resize((small > 0.5).astype(np.uint8), (W, H), interpolation=cv2.INTER_NEAREST)
    cs, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cs: return None, None
    c = max(cs, key=cv2.contourArea)[:, 0, :].astype(np.float32)
    k = 41
    pad = np.concatenate([c[-k:], c, c[:k]])
    ker = np.ones(k) / k
    c = np.stack([np.convolve(pad[:, 0], ker, "same"), np.convolve(pad[:, 1], ker, "same")], 1)[k:-k]
    n = len(c)
    it = int(np.argmin(c[:, 1]))
    def marche(sens):
        out, i = [], it
        for _ in range(n):
            p = c[i]
            if p[1] > 0.70 * H or p[0] < 3 or p[0] > W - 3: break
            out.append(p); i = (i + sens) % n
        return out
    a, bb = marche(1), marche(-1)
    gauche, droite = (a, bb) if (len(a) and len(bb) and np.mean([p[0] for p in a[:200]]) < np.mean([p[0] for p in bb[:200]])) else (bb, a)
    pts = np.array(gauche[::-1] + droite[1:], np.float32)
    if len(pts) < 50: return None, None
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
    s = np.arange(0, d[-1], 2.0)
    pts = np.stack([np.interp(s, d, pts[:, 0]), np.interp(s, d, pts[:, 1])], 1)
    tg = np.gradient(pts, axis=0)
    tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-6
    nr = np.stack([tg[:, 1], -tg[:, 0]], 1)
    # normale vers l'extérieur
    j = len(pts) // 2
    q = (pts[j] + nr[j] * 12).astype(int)
    if 0 <= q[1] < H and 0 <= q[0] < W and ms[q[1], q[0]] > 0.5: nr = -nr
    return pts, nr


def chemin_tete(ms, hx):
    """(poing levé qui emmêlait le texte) : silhouette tête + épaules SANS les bras. Pour chaque ligne, le bloc de
    colonnes qui contient le centre de la tête ; les bords s'élargissent seulement en descendant (cône lisse, pas de cou)."""
    small = cv2.resize(ms, (W // 4, H // 4), interpolation=cv2.INTER_AREA) > 0.5
    h4, w4 = small.shape
    cx = int(hx / 4)
    ys, xl, xr = [], [], []
    for y in range(h4):
        if y > 0.70 * h4: break
        row = small[y]
        if not row[min(max(cx, 0), w4 - 1)]:
            if ys: break
            continue
        a = b = min(max(cx, 0), w4 - 1)
        while a > 0 and row[a - 1]: a -= 1
        while b < w4 - 1 and row[b + 1]: b += 1
        ys.append(y); xl.append(a); xr.append(b)
    if len(ys) < 20: return None, None
    ys, xl, xr = np.array(ys, np.float32) * 4, np.array(xl, np.float32) * 4, np.array(xr, np.float32) * 4
    k = 9
    xl = np.convolve(np.pad(xl, k, mode="edge"), np.ones(k) / k, "same")[k:-k]
    xr = np.convolve(np.pad(xr, k, mode="edge"), np.ones(k) / k, "same")[k:-k]
    xl = np.minimum.accumulate(xl); xr = np.maximum.accumulate(xr)   # le cône ne rétrécit jamais en descendant
    mid = (xl[0] + xr[0]) / 2
    pts = np.concatenate([np.stack([xl[::-1], ys[::-1]], 1), [[mid, ys[0] - 6]], np.stack([xr, ys], 1)]).astype(np.float32)
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
    s_ = np.arange(0, d[-1], 2.0)
    pts = np.stack([np.interp(s_, d, pts[:, 0]), np.interp(s_, d, pts[:, 1])], 1)
    k = 25
    pts = np.stack([np.convolve(np.pad(pts[:, j], k, mode="edge"), np.ones(k) / k, "same")[k:-k] for j in (0, 1)], 1)
    tg = np.gradient(pts, axis=0)
    tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-6
    nr = np.stack([tg[:, 1], -tg[:, 0]], 1)
    j = int(np.argmin(pts[:, 1]))
    if nr[j, 1] > 0: nr = -nr      # au sommet, la normale extérieure monte
    return pts, nr


# ------------------------------------------------------------------ styles
def st_orbite(c):
    t, ws, (top, hx, hw) = c["t"], c["mots"], c["tete"]
    hy = top + 0.30 * hw
    f = font("Outfit.ttf", 124, 700)
    #  (13 mots empilés sur RUSH) : 6 mots max autour de la tête ; le plus récent arrive devant à droite,
    # les autres reculent d'un cran (52°) vers l'arrière, le 6e s'efface.
    dits = [m for m in ws if t >= m["start"] - 0.02]
    for j, m in enumerate(reversed(dits)):
        if j > 3: break   # juge v2 : 4 mots max, plus gros
        u = apparition(t, m["start"], 0.18)
        if u <= 0: continue
        if j == 3: u *= max(0.0, 1 - (t - dits[-1]["start"]) / 0.25)
        cran = j + (1 - ease((t - dits[-1]["start"]) / 0.25)) * (-1 if j else 0)
        phi = math.radians(30 - 68 * max(cran, 0) + 10 * (t - c["de"]))
        x = hx + 0.38 * W * math.cos(phi)
        y = hy - 0.02 * H + 0.06 * H * math.sin(phi)
        prof = math.sin(phi)
        sc = (1 + 0.16 * prof) * (0.7 + 0.3 * u)
        s = sprite(propre(m["text"]), f)
        demi = (s.shape[1] / 2 - f.size * 0.5) * sc
        x = max(MX + demi, min(W - MX - demi, x))
        cv = c["B"] if prof < -0.05 else c["F"]
        ombre(cv, s, x, y, sc, -6, u)
        paste(cv, s, x, y, sc, -6, u, 6 * (1 - u) if u < 1 else 0)   # juge v3 : mots pâles -> opaques, nets une fois posés


def st_choc(c):
    t, ws, (top, hx, hw) = c["t"], c["mots"], c["tete"]
    cle = c["sc"].get("mot", "")
    km = next((m for m in ws if propre(m["text"]).upper() == cle), ws[-1])
    petits = [m for m in ws if m is not km]
    if petits: ligne(c["F"], petits, t, W / 2, max(TOP + 50, top - 320), font("Outfit.ttf", 80, 700))
    u = ease((t - km["start"] + 0.12) / 0.30)
    if u <= 0: return
    taille = 300
    while font("BebasNeue-Regular.ttf", taille).getlength(cle) > 0.88 * W: taille -= 10
    s = sprite(cle, font("BebasNeue-Regular.ttf", taille), (236, 236, 236))
    y = max(TOP + 200, top - 110)
    sc = 2.5 - 1.5 * u
    for k in (3, 2, 1):  # traînée de vitesse
        paste(c["F"], s, W / 2, y, sc * (1 + 0.14 * k * (1 - u * 0.7)), -7, 0.22 / k * (1 - 0.6 * u), 10 + 8 * k)
    ombre(c["F"], s, W / 2, y, sc, -7, min(1, u * 3), 22 * (1 - u))
    paste(c["F"], s, W / 2, y, sc, -7, min(1, u * 3), 22 * (1 - u))


def st_lueur(c, exclure=()):
    t, ws = c["t"], c["mots"]
    g = groupe_du_moment(groupes_sans(ws, exclure), t)
    if g: ligne(c["F"], g, t, W / 2, sous_menton(c, 0.64 * H), font("Outfit.ttf", 86, 700), glow=(255, 255, 255), glowcv=c["G"])
    c["glow"] = (0.55, 9, 26)


def st_neon(c):
    t, ws = c["t"], c["mots"]
    cle = c["sc"]["mot"].split()
    i = next(i for i, m in enumerate(ws) if propre(m["text"]) == cle[0])
    km = ws[i:i + len(cle)]
    ks = km[0]["start"]
    if t < ks - 0.02:
        return st_lueur(c, exclure=km)
    u = t - ks
    clign = [1, 0, 1, 1, 0.2, 1, 1, 1, 0.5, 1]
    on = clign[int(u * FPS)] if u * FPS < len(clign) else 1.0
    f = font("Outfit.ttf", 128, 500)
    s = sprite(" ".join(cle), f, (255, 228, 236))
    y = c["etat"].setdefault("y_neon", sous_menton(c, 0.66 * H))
    paste(c["F"], s, W / 2, y, 1.0, 0, on)
    paste(c["G"], teinte(s, (255, 40, 110)), W / 2, y, 1.04, 0, on)
    c["glow"] = (1.9 * on, 6, 30)
    c["teinte"] = ((1.0, 0.42, 0.52), 0.45 * on)


def geant_pose(c, txt, fnt_name, wght, fill, couvre=0.6, largeur=0.85):
    """Taille et place du mot géant : ~85 % de la largeur, la tête couvre ~60 % de la hauteur des lettres (viashaan)."""
    top = c["etat"]["top0"] if "top0" in c["etat"] else c["tete"][0]
    if c.get("dit"): c["etat"].setdefault("top0", c["tete"][0])   # figé sur l'image où le mot est dit (prompt viashaan)
    taille = 400
    while taille > 60:
        f = font(fnt_name, taille, wght)
        l, t_, r, b = f.getbbox(txt)
        if r - l <= min(largeur * W, W - 2 * MX - 20): break
        taille -= 8
    h = b - t_
    cy = top + (couvre - 0.5) * h   # la tête couvre « couvre » de la hauteur des lettres
    cy = max(TOP + h / 2 + 10, cy)
    return f, cy, h


def st_geant(c):
    t, ws = c["t"], c["mots"]
    cle = c["sc"]["mot"]
    kms = suite(ws, cle)                      # « CLAUDE CODE » = 2 mots
    km = kms[0]
    c["dit"] = t >= km["start"] - 0.02
    f, cy, h = geant_pose(c, cle, "Outfit.ttf", 800, None, couvre=0.15, largeur=0.9)
    vus = " ".join(propre(x["text"]).upper() for x in kms if t >= x["start"] - 0.02)
    u = (t - km["start"] + 0.02) / 0.2
    sc = pop(u)
    if sc > 0 and vus:
        s = sprite(vus, f, tuple(c["sc"].get("couleur", (232, 131, 107))))
        paste(c["B"], s, W / 2, cy, sc, 0, min(1, u * 2.5))
        if c["sc"].get("logo") and len(vus.split()) == len(cle.split()):
            soleil(c["F"], W / 2 + f.getlength(cle) / 2 + 10, cy - h * 0.55, h * 0.55, min(1, (t - kms[-1]["start"]) / 0.4))
    g = groupe_du_moment(groupes_sans(ws, kms), t)
    if g:
        ligne(c["F"], g, t, W / 2, max(TOP + 40, cy - h / 2 - 70), font("Outfit.ttf", 80, 700))


def st_tracking(c):
    t, ws, m = c["t"], c["mots"], c["m"]
    top, hx, hw = c["tete"]
    creme = np.array([237, 233, 225], np.float32) / 255
    noir = np.array([18, 16, 15], np.float32) / 255
    #  (RUSH : trous blancs dans la silhouette au niveau du micro et des mains) : silhouette pleine, trous bouchés
    mp = cv2.resize(m, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    mp = cv2.morphologyEx(mp, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    pl_ = (mp > 0.5).astype(np.uint8)
    cs_, _ = cv2.findContours(pl_, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    plein = np.zeros_like(pl_)
    cv2.drawContours(plein, cs_, -1, 1, thickness=-1)
    plein = cv2.resize(plein.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    m = np.maximum(m, np.clip(plein * 1.0 - 0.0, 0, 1) * (cv2.GaussianBlur(plein, (0, 0), 2) > 0.98))
    c["base"][:] = creme * (1 - m[..., None]) + noir * m[..., None]
    sz = 1.3 * hw
    fy = top + 0.58 * sz
    cle = c["sc"]["mot"]
    km = next(x for x in ws if propre(x["text"]) == cle)
    p0 = ease((t - c["de"]) / 0.5)
    e = c["etat"]
    if int(t * FPS) % 3 == 0 or "conf" not in e: e["conf"] = random.uniform(0.912, 0.948)
    def hud(d, im):
        # arc brun décoratif qui se dessine
        pts = [(-60 + i * 16, 0.10 * H + 0.05 * H * math.sin(i / 52 * math.pi) - i * 1.6) for i in range(int(52 * p0) + 1)]
        if len(pts) > 1: d.line(pts, fill=(146, 98, 52, 255), width=24, joint="curve")
        jaune = (244, 196, 48, 255)
        x0, y0, x1, y1 = hx - sz / 2, fy - sz / 2, hx + sz / 2, fy + sz / 2
        k = sz * 0.22
        for (ax, ay, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            d.line([(ax, ay + sy * k), (ax, ay), (ax + sx * k, ay)], fill=jaune, width=6)
        for ex in (hx - 0.17 * sz, hx + 0.17 * sz):
            ey = fy - 0.04 * sz
            d.line([(ex - 14, ey), (ex + 14, ey)], fill=jaune, width=4); d.line([(ex, ey - 14), (ex, ey + 14)], fill=jaune, width=4)
        mono = font("/System/Library/Fonts/Menlo.ttc", 27)
        # le HUD va du côté où il n'y a pas de silhouette (texte sombre illisible sur le noir)
        def noir(xa, xb):
            xa, xb = int(max(0, xa)), int(min(W, xb))
            return float(m[int(max(0, fy - 40)):int(min(H, fy + 40)), xa:xb].mean()) if xb > xa else 1.0
        tw = mono.getlength("X 0000  Y 0000")
        gauche_ok, droite_ok = x0 - 24 - tw > MX, x1 + 24 + tw < W - MX
        if gauche_ok and (not droite_ok or noir(x0 - 24 - tw, x0 - 24) <= noir(x1 + 24, x1 + 24 + tw)):
            gx, an, zone = x0 - 24, "ra", (x0 - 24 - tw, x0 - 24)
        elif droite_ok:
            gx, an, zone = x1 + 24, "la", (x1 + 24, x1 + 24 + tw)
        else:   # pas de place sur les côtés : sous le cadre
            gx, an, zone = hx - tw / 2, "la", (hx - tw / 2, hx + tw / 2)
            fy_t = y1 + 50
        coul = (237, 233, 225, 255) if noir(*zone) > 0.5 else (30, 28, 26, 255)
        yt = locals().get("fy_t", fy)
        coul = (30, 28, 26, 255)   # texte sombre + contour crème : lisible sur le fond ET sur la silhouette
        for yy_, tx in ((yt - 34, f"VISAGE {e['conf']:.3f}"), (yt + 4, f"X {int(c['src_xy'][0]):04d}  Y {int(c['src_xy'][1]):04d}")):
            d.text((gx, yy_), tx, font=mono, fill=coul, anchor=an, stroke_width=4, stroke_fill=(237, 233, 225, 255))
    vecteur(c["F"], hud)
    serif = font("InstrumentSerif-Italic.ttf", 175)
    u = apparition(t, km["start"], 0.18)
    if u > 0:
        s = sprite(cle, serif, (22, 20, 18))
        paste(c["F"], s, 0.38 * W, TOP + 105 + 12 * (1 - u), 1, 0, u, 8 * (1 - u))
    g = groupe_du_moment(groupes_sans(ws, [km]), t)
    if g: ligne(c["F"], g, t, W / 2, 0.68 * H, font("Outfit.ttf", 88, 700), fill=(255, 255, 255), shadow=False)


def st_contour(c):
    t, ws, e = c["t"], c["mots"], c["etat"]
    ms = e["ms"] = c["m"] if "ms" not in e else 0.85 * e["ms"] + 0.15 * c["m"]
    pts, nr = chemin_corps(c["m"])   # pointillés collés au masque de CETTE image (le lissage les faisait traîner sur le visage)
    if pts is None: return st_lueur(c)
    dec = (t * 60) % 26
    def trace(d, im):
        L = len(pts)
        i = int(dec / 2)
        while i < L - 7:
            seg = [tuple(p) for p in pts[i:i + 7]]
            d.line([(x + 2, y + 2) for x, y in seg], fill=(0, 0, 0, 110), width=4)
            d.line(seg, fill=(255, 255, 255, 235), width=3); i += 12
        for j in range(60, L, 180):
            x, y = pts[j]
            d.rectangle([x - 7, y - 7, x + 7, y + 7], fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=2)
    vecteur(c["F"], trace)
    pts, nr = chemin_tete(ms, c["tete"][1])
    if pts is None: return
    #  (juge : texte trop dense) : un groupe court à la fois (coupé aux virgules, 4 mots max), centré sur le sommet
    f = font("Outfit.ttf", 64, 700)
    bloc = groupe_du_moment(groupes(ws, maxi=4), t)
    if not bloc: return
    off = pts + nr * 72   # juge v3 : texte collé aux pointillés
    dd = np.r_[0, np.cumsum(np.hypot(*np.diff(off, axis=0).T))]
    ss = np.arange(0, dd[-1], 2.0)
    off = np.stack([np.interp(ss, dd, off[:, 0]), np.interp(ss, dd, off[:, 1])], 1)
    k_ = 15
    off = np.stack([np.convolve(np.pad(off[:, j], k_, mode="edge"), np.ones(k_) / k_, "same")[k_:-k_] for j in (0, 1)], 1)
    pts = off
    lg = sum(f.getlength(propre(m["text"]) + " ") for m in bloc)
    s_pos = max(0.0, int(np.argmin(pts[:, 1])) * 2 - lg / 2)
    for m in bloc:
        u = apparition(t, m["start"], 0.12)
        for ch in propre(m["text"]) + " ":
            adv = f.getlength(ch)
            k = int((s_pos + adv / 2) / 2)
            if k >= len(pts): return
            if ch != " " and u > 0:
                p = pts[k]
                ang = math.degrees(math.atan2(*(pts[min(k + 8, len(pts) - 1)] - pts[max(k - 8, 0)])[::-1]))
                spr = sprite(ch, f)
                ombre(c["F"], spr, p[0], p[1], 1, -ang, u, 0, 0.6, 3)
                paste(c["F"], spr, p[0], p[1], 1, -ang, u, 6 * (1 - u))
            s_pos += adv


def st_serif(c):
    t, ws = c["t"], c["mots"]
    cle = c["sc"]["mot"].split()
    i = next(i for i, m in enumerate(ws) if propre(m["text"]) == cle[0])
    km = ws[i:i + len(cle)]
    txt = " ".join(cle)
    c["dit"] = t >= km[0]["start"] - 0.02
    f, cy, h = geant_pose(c, txt, "InstrumentSerif-Italic.ttf", None, None, couvre=0.45, largeur=0.9)
    u = apparition(t, km[0]["start"], 0.22)
    if u > 0:
        s = sprite(txt, f, tuple(c["sc"].get("couleur", (255, 255, 255))))   # couleur au choix (mur clair)
        ombre(c["B"], s, W / 2, cy, 1.08 - 0.08 * u, 0, u * 0.8, 10 * (1 - u))
        paste(c["B"], s, W / 2, cy, 1.08 - 0.08 * u, 0, u, 10 * (1 - u))
    g = groupe_du_moment(groupes_sans(ws, km), t)
    if g: ligne(c["F"], g, t, W / 2, max(TOP + 40, cy - h / 2 - 60), font("Outfit.ttf", 80, 700))
    c["vignette"] = 0.55


def st_filaire(c):
    t, ws, m = c["t"], c["mots"], c["m"]
    top, hx, hw = c["tete"]
    cle0 = suite(ws, c["sc"]["mot"])
    ks = cle0[0]["start"] if (cle0 and c["sc"].get("au_mot", True)) else c["de"]
    pf = ease((t - ks + 0.05) / 0.35)          # la pièce (Beeble) est vraie, PUIS elle devient des lignes au mot-clé
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    fond = (np.array([44, 28, 19], np.float32) * (1 - yy) + np.array([20, 13, 9], np.float32) * yy) / 255
    if pf > 0:
        c["base"][:] = (fond * pf + c["base"] * (1 - pf)) * (1 - m[..., None]) + c["base"] * m[..., None]
    p = ease((t - ks) / 0.7)
    vx, vy = W / 2, 0.36 * H
    bx0, bx1, by0, by1 = 0.25 * W, 0.75 * W, 0.31 * H, 0.60 * H
    traits = [((bx0, by0), (bx1, by0)), ((bx1, by0), (bx1, by1)), ((bx1, by1), (bx0, by1)), ((bx0, by1), (bx0, by0)),
              ((bx0, by0), (-40, -60)), ((bx1, by0), (W + 40, -60)), ((bx0, by1), (-40, H * 0.80)), ((bx1, by1), (W + 40, H * 0.80)),
              ((0.10 * W, 0.70 * H), (0.10 * W, 0.34 * H)), ((0.10 * W, 0.34 * H), (0.19 * W, 0.37 * H)),
              ((0.84 * W, 0.46 * H), (0.96 * W, 0.43 * H)), ((0.84 * W, 0.53 * H), (0.96 * W, 0.51 * H))]
    def dessin(d, im):
        for k, (a, b) in enumerate(traits):
            q = min(1, max(0, p * 1.6 - k * 0.05))
            if q <= 0: continue
            e_ = (a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q)
            d.line([a, e_], fill=(238, 232, 222, 215), width=3)
    vecteur(c["B"], dessin)
    cle = c["sc"]["mot"].split()
    km = cle0
    i = ws.index(km[0])
    y = max(TOP + 120, top - 70)
    g = groupe_du_moment(groupes(ws[:i]), t)
    if t < km[0]["start"] - 0.02:
        if g: ligne(c["F"], g, t, W / 2, y, font("Outfit.ttf", 80, 700))
    else:
        av = [x for x in ws[max(0, i - 2):i]]
        ligne(c["F"], av, 99, W / 2, y - 110, font("Outfit.ttf", 76, 700))
        u = apparition(t, km[0]["start"], 0.2)
        s = sprite(" ".join(cle), font("InstrumentSerif-Italic.ttf", 132))
        ombre(c["F"], s, W / 2, y + 6, 1, 0, u, 8 * (1 - u))
        paste(c["F"], s, W / 2, y + 6 + 12 * (1 - u), 1, 0, u, 8 * (1 - u))


def st_dit(c):
    """(« des textes en néon, des gros textes ou même des textes en italique ») : chaque bloc prend le style qu'il nomme."""
    t, ws = c["t"], c["mots"]
    blocs = [(suite(ws, d_["mots"]), d_["style"]) for d_ in c["sc"]["dits"]]
    blocs = [b for b in blocs if b[0]]
    actif = None
    for b in blocs:
        if t >= b[0][0]["start"] - 0.02: actif = b
    if actif is None:
        return st_lueur(c, exclure=[x for b in blocs for x in b[0]])
    mots_, style = actif
    y = c["etat"].setdefault("y_dit", sous_menton(c, 0.60 * H))
    vus = [x for x in mots_ if x["start"] - 0.02 <= t]
    txt = " ".join(propre(x["text"]) for x in vus)
    u = (t - mots_[0]["start"] + 0.02) / 0.2
    if style == "neon":
        clign = [1, 0, 1, 1, 0.2, 1, 1, 1, 0.5, 1]
        k = int((t - mots_[0]["start"]) * FPS)
        on = clign[k] if 0 <= k < len(clign) else 1.0
        s = sprite(txt, font("Outfit.ttf", 120, 500), (255, 228, 236))
        paste(c["F"], s, W / 2, y, 1.0, 0, on)
        paste(c["G"], teinte(s, (255, 40, 110)), W / 2, y, 1.04, 0, on)
        c["glow"] = (1.9 * on, 6, 30)
        c["teinte"] = ((1.0, 0.42, 0.52), 0.45 * on)
    elif style == "caps":
        taille = 240
        while font("BebasNeue-Regular.ttf", taille).getlength(txt.upper()) > 0.86 * W: taille -= 10
        s = sprite(txt.upper(), font("BebasNeue-Regular.ttf", taille))
        sc = pop(u, 0.75, 0.07)
        ombre(c["F"], s, W / 2, y, sc, 0, 1, 0, 0.6, 8)
        paste(c["F"], s, W / 2, y, sc)
    else:   # serif italique
        s = sprite(txt, font("InstrumentSerif-Italic.ttf", 150))
        v = apparition(t, mots_[0]["start"], 0.2)
        ombre(c["F"], s, W / 2, y, 1, 0, v, 8 * (1 - v))
        paste(c["F"], s, W / 2, y + 12 * (1 - v), 1, 0, v, 8 * (1 - v))


def st_fleches(c):
    """(« il sait exactement où se trouve la zone de danger sur Instagram ») : sous-titres + la zone interdite
    s'allume en rouge + flèches dessinées vers les boutons de droite."""
    t, ws = c["t"], c["mots"]
    g = groupe_du_moment(groupes(ws), t)
    if g: ligne(c["F"], g, t, W / 2, c["etat"].setdefault("y_f", min(sous_menton(c, 0.56 * H), 0.72 * H)), font("Outfit.ttf", 86, 700))
    z = suite(ws, c["sc"].get("zone", "zone"))
    f_ = suite(ws, c["sc"].get("fleches", "Instagram"))
    pz = ease((t - z[0]["start"]) / 0.3) if z else 0
    pa = ease((t - f_[0]["start"]) / 0.5) if f_ else 0
    def dessin(d, im):
        if pa > 0:
            for k, yb in enumerate((1180, 1330, 1460)):
                q = min(1, max(0, pa * 1.5 - k * 0.25))
                if q <= 0: continue
                x0, y0 = W - 330, yb - 150 + 40 * k
                x1, y1 = W - 140, yb
                pts = [((1 - v) * x0 + v * x1 + 30 * math.sin(v * math.pi), (1 - v) * y0 + v * y1 - 40 * math.sin(v * math.pi)) for v in [i / 20 * q for i in range(21)]]
                d.line(pts, fill=(255, 255, 255, 245), width=7, joint="curve")
                if q > 0.9:
                    (xa, ya), (xb, yb2) = pts[-3], pts[-1]
                    ang = math.atan2(yb2 - ya, xb - xa)
                    for da in (0.5, -0.5):
                        d.line([(xb, yb2), (xb - 30 * math.cos(ang + da), yb2 - 30 * math.sin(ang + da))], fill=(255, 255, 255, 245), width=7)
    def zone(d, im):
        if pz > 0:
            a = int(80 * pz)
            d.rectangle([0, BOT, W, H], fill=(255, 59, 48, a))
            d.rectangle([W - 120, 1100, W, BOT], fill=(255, 59, 48, a))
            d.line([(0, BOT), (W - 120, BOT)], fill=(255, 110, 100, int(220 * pz)), width=3)
            d.line([(W - 120, 1100), (W - 120, BOT)], fill=(255, 110, 100, int(220 * pz)), width=3)
    if pz > 0: vecteur(c["F"], zone)      # juge v2 : invisible derrière -> voile de l'interface Insta, devant, 30 %
    if pa > 0: vecteur(c["F"], dessin)


_OR = {}


def sprite_or(txt, taille):
    k = (txt, taille)
    if k in _OR: return _OR[k]
    f = font("Archivo.ttf", taille, 900, 112)
    l, t, r, b = f.getbbox(txt)
    pad = int(taille * 0.4)
    w, h = r - l + 2 * pad, b - t + 2 * pad + 24
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).text((pad - l, pad - t), txt, font=f, fill=255)
    A = np.asarray(im, np.float32) / 255
    out = np.zeros((h, w, 4), np.float32)
    for k_ in range(16, 0, -1):  # profondeur 3D
        Ak = np.roll(np.roll(A, int(k_ * 0.5), 1), int(k_ * 1.1), 0)
        col = np.array([92, 58, 18], np.float32) / 255 * (0.55 + 0.45 * (1 - k_ / 16))
        out[..., :3] = Ak[..., None] * col + out[..., :3] * (1 - Ak[..., None])
        out[..., 3] = Ak + out[..., 3] * (1 - Ak)
    yy = np.linspace(0, 1, h, dtype=np.float32)
    ty, tb = (pad - 0) / h, (pad + (b - t)) / h
    v = np.clip((yy - ty) / max(tb - ty, 1e-3), 0, 1)
    stops = [(0, (255, 240, 178)), (0.32, (236, 186, 76)), (0.5, (148, 98, 28)), (0.6, (252, 218, 120)), (1, (172, 116, 34))]
    grad = np.zeros((h, 3), np.float32)
    for j in range(3):
        grad[:, j] = np.interp(v, [s_[0] for s_ in stops], [s_[1][j] for s_ in stops]) / 255
    face = np.repeat(grad[:, None, :], w, 1)
    Ab = cv2.GaussianBlur(A, (0, 0), 3)
    gy = cv2.Sobel(Ab, cv2.CV_32F, 0, 1, ksize=5)
    gx = cv2.Sobel(Ab, cv2.CV_32F, 1, 0, ksize=5)
    lum = np.clip((gy + gx * 0.5) * 0.06, -1, 1)
    face = np.clip(face + np.clip(lum, 0, 1)[..., None] * 0.55 - np.clip(-lum, 0, 1)[..., None] * 0.35, 0, 1)
    out[..., :3] = A[..., None] * face + out[..., :3] * (1 - A[..., None])
    out[..., 3] = A + out[..., 3] * (1 - A)
    out[..., :3] *= 1  # déjà prémultiplié (couleurs posées sur alpha)
    _OR[k] = (out, A)
    return _OR[k]


def st_or(c):
    t, ws = c["t"], c["mots"]
    cle = c["sc"]["mot"]
    km = suite(ws, cle)[0]
    if t >= km["start"] - 0.02: c["etat"].setdefault("top0", c["tete"][0])
    top = c["etat"].get("top0", c["tete"][0])
    taille = 300
    while taille > 80:
        l, t_, r, b = font("Archivo.ttf", taille, 900, 112).getbbox(cle)
        if r - l <= 0.82 * W: break
        taille -= 10
    spr, A = sprite_or(cle, taille)
    hh = b - t_
    cy = max(TOP + hh / 2 + 150, top + 0.0 * hh)   # 150 px au-dessus = place pour le petit texte en arc, sous la zone Insta
    u = (t - km["start"] + 0.02) / 0.27
    sc = pop(u, 0.7, 0.06)
    if sc > 0:
        s = spr.copy()
        q = (t - km["start"] - 0.35) / 0.8   # reflet qui traverse
        if 0 < q < 1:
            hh_, ww_ = s.shape[:2]
            X, Y = np.meshgrid(np.arange(ww_), np.arange(hh_))
            band = np.exp(-(((X + Y * 0.5) - (q * (ww_ + hh_))) / 40.0) ** 2).astype(np.float32)
            s[..., :3] = np.clip(s[..., :3] + band[..., None] * A[..., None] * 0.6, 0, 1)
        paste(c["B"], teinte(spr, (0, 0, 0), 0.6), W / 2 + 6, cy + 14, sc, 0, min(1, u * 2), 14)
        paste(c["B"], s, W / 2, cy, sc, 0, min(1, u * 2))
    av = ws[:ws.index(km)]
    if t < km["start"] - 0.02:
        g = groupe_du_moment(groupes(av), t)
        if g: ligne(c["F"], g, t, W / 2, sous_menton(c, 0.62 * H), font("Outfit.ttf", 84, 700))
        return
    # petit texte en arc au-dessus du mot doré (les 2 mots d'avant)
    arc = c["sc"].get("arc") or " ".join(propre(m["text"]) for m in av[-2:])
    apres = ws[ws.index(km) + 1:]
    g = groupe_du_moment(groupes(apres), t)
    if g: ligne(c["F"], g, t, W / 2, sous_menton(c, 0.62 * H), font("Outfit.ttf", 84, 700))
    f = font("Outfit.ttf", 84, 700)
    R = 560
    ccx, ccy = W / 2, cy - hh / 2 - 78 + R
    tot = f.getlength(arc)
    a = -tot / 2
    for ch in arc:
        adv = f.getlength(ch)
        th = (a + adv / 2) / R
        x, y = ccx + R * math.sin(th), ccy - R * math.cos(th)
        if ch != " ":
            spr_c = sprite(ch, f)
            ombre(c["F"], spr_c, x, y, 1, -math.degrees(th), 1, 4, 0.9, 4)
            paste(c["F"], spr_c, x, y, 1, -math.degrees(th), 1)
        a += adv
    # flèche dessinée vers la droite et le bas
    p = ease((t - km["start"] - 0.3) / 0.45)
    if p > 0:
        # vers le bouton commentaire d'Instagram (à droite, ~1330 px de haut)
        x0, y0 = W / 2 + 0.28 * W, cy + hh * 0.75
        x1, y1 = W - 118, 0.665 * H
        cxb, cyb = x1 + 40, y0 + (y1 - y0) * 0.35
        n_ = int(40 * p) + 1
        pts = [((1 - u_) ** 2 * x0 + 2 * (1 - u_) * u_ * cxb + u_ ** 2 * x1, (1 - u_) ** 2 * y0 + 2 * (1 - u_) * u_ * cyb + u_ ** 2 * y1)
               for u_ in [k / 40 for k in range(n_)]]
        def fl(d, im):
            if len(pts) > 1:
                d.line(pts, fill=(255, 255, 255, 250), width=11, joint="curve")
                if len(pts) > 6:
                    (xa, ya), (xb, yb) = pts[-4], pts[-1]
                    ang = math.atan2(yb - ya, xb - xa)
                    for da in (2.5, -2.5):
                        d.line([(xb, yb), (xb - 52 * math.cos(ang + da * 0.24), yb - 52 * math.sin(ang + da * 0.24))], fill=(255, 255, 255, 250), width=11)
        vecteur(c["F"], fl)


# ------------------------------------------------------------------ : fidèle à l'original (retours de l’utilisateur sur RUSH)
def mains(c):
    """Hauteur des mains = un tiers du corps sous le haut de la tête (la détection de peau prenait le pantalon,
    éclairé chaud par Beeble, et posait les textes aux hanches). Lissé. -> (x, y)"""
    top, hx, hw = c["tete"]
    m = c["m"]
    col = m[:, int(max(0, hx - 60)):int(min(W, hx + 60))].max(1)
    rows = np.where(col > 0.5)[0]
    bas = float(rows[-1]) if len(rows) else H
    p = (hx, top + c["sc"].get("mains", 0.33) * (bas - top))
    e = c["etat"]
    e["mains"] = p if "mains" not in e else (0.85 * e["mains"][0] + 0.15 * p[0], 0.85 * e["mains"][1] + 0.15 * p[1])
    return e["mains"]


def mains_peau(c):
    """(ancienne version, gardée) Centre des mains par la couleur de peau."""
    top, hx, hw = c["tete"]
    b = (np.clip(c["base"], 0, 1) * 255).astype(np.uint8)
    small = cv2.resize(b, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    ycc = cv2.cvtColor(small, cv2.COLOR_RGB2YCrCb)
    peau = (ycc[..., 1] > 135) & (ycc[..., 1] < 180) & (ycc[..., 2] > 80) & (ycc[..., 2] < 130)
    ms = cv2.resize(c["m"], (W // 4, H // 4)) > 0.5
    y_menton = int((top + 1.45 * hw) / 4)
    peau &= ms
    peau[:max(0, y_menton)] = False
    peau = cv2.morphologyEx(peau.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    ys, xs = np.nonzero(peau)
    e = c["etat"]
    if len(xs) > 30:
        p = (float(np.median(xs)) * 4, float(np.median(ys)) * 4)
        e["mains"] = p if "mains" not in e else (0.8 * e["mains"][0] + 0.2 * p[0], 0.8 * e["mains"][1] + 0.2 * p[1])
    return e.get("mains")


def sprite_italique(txt, taille, wght=800, pente=0.22):
    """Grosses italiques (Outfit penchée) : « chunky italics » de l'original."""
    s = sprite(txt, font("Outfit.ttf", taille, wght))
    h, w = s.shape[:2]
    M = np.array([[1, -pente, pente * h], [0, 1, 0]], np.float32)
    return cv2.warpAffine(s, M, (int(w + pente * h), h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def st_dit2(c):
    """Comme l'original : petits mots ET néon sur les mains, GROSSES CAPITALES empilées en haut à droite au-dessus de la
    tête, grosses italiques sur les mains qui se dissolvent à la fin."""
    t, ws = c["t"], c["mots"]
    top, hx, hw = c["tete"]
    mn = mains(c) or (W / 2, sous_menton(c, 0.6 * H))
    mx_, my_ = min(max(mn[0], 260), W - 260), min(max(mn[1], TOP + 300), BOT - 120)
    blocs = [(suite(ws, d_["mots"]), d_["style"]) for d_ in c["sc"]["dits"]]
    blocs = [b for b in blocs if b[0]]
    actif = None
    for b in blocs:
        if t >= b[0][0]["start"] - 0.02: actif = b
    if actif is None:
        g = groupe_du_moment(groupes_sans(ws, [x for b in blocs for x in b[0]], 2), t)
        if g: ligne(c["F"], g, t, mx_, my_, font("Outfit.ttf", 78, 700), glow=(255, 255, 255), glowcv=c["G"])
        c["glow"] = (0.5, 8, 22)
        return
    mots_, style = actif
    vus = [x for x in mots_ if x["start"] - 0.02 <= t]
    u = (t - mots_[0]["start"] + 0.02) / 0.2
    fin_bloc = c["sc"]["a"]
    for b in blocs:
        if b[0][0]["start"] > mots_[0]["start"]: fin_bloc = b[0][0]["start"]; break
    if style == "neon":
        clign = [1, 0, 1, 1, 0.2, 1, 1, 1, 0.5, 1]
        k = int((t - mots_[0]["start"]) * FPS)
        on = clign[k] if 0 <= k < len(clign) else 1.0
        lignes_ = [" ".join(propre(x["text"]) for x in vus[:2]), " ".join(propre(x["text"]) for x in vus[2:])]
        for j, l_ in enumerate([l for l in lignes_ if l]):
            s = sprite(l_, font("Outfit.ttf", 104, 500), (255, 228, 236))
            yy = my_ - 50 + j * 112
            paste(c["F"], s, mx_, yy, 1.0, 0, on)
            paste(c["G"], teinte(s, (255, 40, 110)), mx_, yy, 1.04, 0, on)
        c["glow"] = (1.9 * on, 6, 30)
        c["teinte"] = ((1.0, 0.42, 0.52), 0.45 * on)
    elif style == "caps":
        f = font("BebasNeue-Regular.ttf", 230)
        x0 = max(hx + hw * 0.2, W * 0.52)
        y0 = max(TOP + 120, top - 330)
        for j, x in enumerate(vus):
            v = (t - x["start"] + 0.02) / 0.2
            s = sprite(propre(x["text"]).upper(), f)
            demi = s.shape[1] / 2 - f.size * 0.5
            cx = min(x0 + demi, W - MX - demi)
            ombre(c["F"], s, cx, y0 + j * 205, pop(v, 0.75, 0.07), 0, 1, 0, 0.6, 8)
            paste(c["F"], s, cx, y0 + j * 205, pop(v, 0.75, 0.07))
    else:   # grosses italiques sur les mains, dissolution floue avant le plan suivant
        d_ = max(0.0, (t - (fin_bloc - 0.35)) / 0.35)
        lignes_ = [" ".join(propre(x["text"]) for x in vus[:2]), " ".join(propre(x["text"]) for x in vus[2:])]
        for j, l_ in enumerate([l for l in lignes_ if l]):
            s = sprite_italique(l_, 96)
            v = apparition(t, mots_[0]["start"], 0.15)
            yy = my_ - 50 + j * 104
            ombre(c["F"], s, mx_, yy, 1 + 0.15 * d_, 0, v * (1 - d_), 6 + 30 * d_)
            paste(c["F"], s, mx_, yy, 1 + 0.15 * d_, 0, v * (1 - d_), 8 * (1 - v) + 30 * d_)


def silhouette_creme(c, fond=(237, 233, 225), corps=(18, 16, 15)):
    m = c["m"]
    mp = cv2.resize(m, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    mp = cv2.morphologyEx(mp, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    pl_ = (mp > 0.5).astype(np.uint8)
    cs_, _ = cv2.findContours(pl_, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    plein = np.zeros_like(pl_)
    cv2.drawContours(plein, cs_, -1, 1, thickness=-1)
    plein = cv2.resize(plein.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    m2 = np.maximum(m, plein * (cv2.GaussianBlur(plein, (0, 0), 2) > 0.98))
    f_, k_ = np.array(fond, np.float32) / 255, np.array(corps, np.float32) / 255
    c["base"][:] = f_ * (1 - m2[..., None]) + k_ * m2[..., None]
    return m2


def ruban(c, p, pts_fn, epais=46):
    """Ruban marron qui se dessine (original : « behind my head? »), moitié derrière toi, moitié devant."""
    n = 80
    pts = [pts_fn(i / n) for i in range(int(n * p) + 1)]
    if len(pts) < 2: return
    def trace(cv, garde):
        def d_(d, im):
            for i in range(len(pts) - 1):
                if garde(i / n):
                    v = i / n
                    col = (int(120 + 40 * v), int(78 + 20 * v), 40, 255)
                    d.line([pts[i], pts[i + 1]], fill=col, width=epais)
                    d.ellipse([pts[i + 1][0] - epais / 2, pts[i + 1][1] - epais / 2, pts[i + 1][0] + epais / 2, pts[i + 1][1] + epais / 2], fill=col)
        vecteur(cv, d_)
    trace(c["B"], lambda v: v < 0.62)
    trace(c["F"], lambda v: v >= 0.62)


def st_accroche(c):
    """Original : « Wait, » en italique seul, puis les mots arrivent par la droite et tournent en anneau autour de la tête
    (flous et petits au fond, derrière la tête), puis coupe sur fond crème + silhouette noire + « head? » géant + ruban."""
    t, ws = c["t"], c["mots"]
    top, hx, hw = c["tete"]
    coupe = suite(ws, c["sc"].get("coupe", "autour"))
    if coupe and t >= coupe[0]["start"] - 0.03:
        silhouette_creme(c)
        reste = ws[ws.index(coupe[0]):]
        geant = reste[-1]
        petits = reste[:-1]
        e = c["etat"]; e.setdefault("top_c", top)
        tp = e["top_c"]
        f = font("InstrumentSerif-Italic.ttf", 330)
        s = sprite(propre(geant["text"]), f, (20, 18, 16))
        v = apparition(t, geant["start"], 0.2)
        cy = tp + 0.05 * 330
        if v > 0: paste(c["B"], s, W / 2 + 40, cy, 1.08 - 0.08 * v, 0, v, 8 * (1 - v))
        ligne(c["F"], petits, t, W / 2 - 60, cy - 230, font("InstrumentSerif-Italic.ttf", 92), fill=(20, 18, 16), shadow=False)
        p = ease((t - coupe[0]["start"]) / 0.6)
        ruban(c, p, lambda u: (0.62 * W + 0.30 * W * math.sin(u * 5.2 + 0.4) * (1 - 0.3 * u), -60 + u * 1.15 * H))
        return
    f_ring = font("Outfit.ttf", 96, 700)
    for i, m in enumerate(ws):
        if coupe and m in coupe: break
        if t < m["start"] - 0.02: continue
        age = t - m["start"]
        if i == 0:   # « Attends, » en serif italique, seul, puis il part dans l'anneau
            s = sprite(propre(m["text"]) + ",", font("InstrumentSerif-Italic.ttf", 130))
            v = apparition(t, m["start"], 0.2)
            nxt = ws[1]["start"] if len(ws) > 1 else 9
            if t < nxt:
                paste(c["F"], s, 0.30 * W, top - 0.05 * H, 1, 0, v, 8 * (1 - v)); continue
            age = t - nxt
            phi = math.radians(150 + 240 * age)
        else:
            phi = math.radians(15 + 240 * age)       # entre à droite, passe devant, part à gauche puis derrière
            s = sprite(propre(m["text"]), f_ring)
        if math.degrees(phi) > 330: continue
        prof = math.sin(phi)
        x = hx + 0.40 * W * math.cos(phi)
        y = top - 0.045 * H + 0.03 * H * prof - 0.035 * H * math.cos(phi)
        sc = 0.62 + 0.38 * (prof + 1) / 2
        flou = 0 if prof > -0.1 else 3 * (-0.1 - prof)          # juge : de face = net, au fond à peine flou
        op = min(1, apparition(t, m["start"], 0.12)) * (1.0 if prof > -0.1 else 0.85)
        cv = c["B"] if prof < -0.1 else c["F"]
        demi = (s.shape[1] / 2) * sc * 0.6
        x = max(MX + demi, min(W - MX - demi, x))
        ombre(cv, s, x, y, sc, -4, op * 0.8, flou)
        paste(cv, s, x, y, sc, -4, op, flou)


def st_rien(c):
    """Transition (balayage du buste) : pas de texte, juste le mouvement et un whoosh."""
    return


def st_tracking2(c):
    """Original : cadre jaune sur le VRAI visage, flash inversé bleu nuit, puis fond crème + silhouette noire +
    « traque mon » en serif + « VISAGE » tapé en grosses capitales avec un curseur jaune."""
    t, ws = c["t"], c["mots"]
    top, hx, hw = c["tete"]
    sz = 1.3 * hw
    fy = top + 0.58 * sz
    e = c["etat"]
    flash = suite(ws, c["sc"].get("flash", "mon"))
    tape = suite(ws, c["sc"].get("tape", "visage"))
    tf = flash[0]["start"] if flash else c["de"] + 0.5
    if int(t * FPS) % 3 == 0 or "conf" not in e: e["conf"] = random.uniform(0.912, 0.948)
    jaune, bleu = (244, 196, 48, 255), (70, 120, 255, 255)
    phase = 1 if t < tf else (2 if t < tf + 5 / FPS else 3)
    if phase == 2:
        silhouette_creme(c, fond=(16, 22, 42), corps=(245, 245, 250))
    elif phase == 3:
        silhouette_creme(c)
    def cadre(d, im):
        col = jaune if phase != 2 else bleu
        x0, y0, x1, y1 = hx - sz / 2, fy - sz / 2, hx + sz / 2, fy + sz / 2
        k = sz * 0.22
        for (ax, ay, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            d.line([(ax, ay + sy * k), (ax, ay), (ax + sx * k, ay)], fill=col, width=6)
        mono = font("/System/Library/Fonts/Menlo.ttc", 27)
        if phase == 1:
            d.text((x1 + 10, y0 - 6), "VISAGE", font=mono, fill=jaune, stroke_width=3, stroke_fill=(0, 0, 0, 160))
            return
        for ex in (hx - 0.17 * sz, hx + 0.17 * sz):
            ey = fy - 0.04 * sz
            d.line([(ex - 14, ey), (ex + 14, ey)], fill=col, width=4); d.line([(ex, ey - 14), (ex, ey + 14)], fill=col, width=4)
        tw = mono.getlength("X 0000  Y 0000")
        if x0 - 24 - tw > MX: gx, an, yb = x0 - 24, "ra", y0 + 10
        elif x1 + 24 + tw < W - MX: gx, an, yb = x1 + 24, "la", y0 + 10
        else: gx, an, yb = max(MX, x0), "la", y0 - 90          # pas de place sur les côtés : au-dessus du cadre
        txt_col = (30, 28, 26, 255) if phase == 3 else (245, 245, 250, 255)
        for yy_, tx in ((yb, f"VISAGE {e['conf']:.3f}"), (yb + 38, f"X {int(c['src_xy'][0]):04d}  Y {int(c['src_xy'][1]):04d}")):
            d.text((gx, yy_), tx, font=mono, fill=txt_col, anchor=an)
        if phase == 3:
            p0 = ease((t - tf) / 0.45)
            pts = [(-60 + i * 18, 0.07 * H + 0.06 * H * math.sin(i / 50 * math.pi) - i * 1.2) for i in range(int(50 * p0) + 1)]
            if len(pts) > 1: d.line(pts, fill=(146, 98, 52, 255), width=30, joint="curve")
    vecteur(c["F"], cadre)
    if phase == 3:
        av = ws[max(0, ws.index(tape[0]) - 2):ws.index(tape[0])] if tape else []
        ligne(c["F"], av, 99, W / 2, TOP + 60, font("InstrumentSerif-Italic.ttf", 100), fill=(22, 20, 18), shadow=False)
        if tape and t >= tape[0]["start"] - 0.02:
            mot = propre(tape[0]["text"]).upper()
            n = min(len(mot), int((t - tape[0]["start"]) / 0.05) + 1)
            f = font("BebasNeue-Regular.ttf", 190)
            s = sprite(mot[:n], f, (22, 20, 18))
            wfull = f.getlength(mot)
            x_g = W / 2 - wfull / 2   # centré AU-DESSUS de la tête (noir sur noir = illisible)
            yv = max(TOP + 190, min(TOP + 205, top - 85))
            paste(c["F"], s, x_g + f.getlength(mot[:n]) / 2, yv)
            if n < len(mot) or int(t * 4) % 2 == 0:
                def cur(d, im):
                    xc = x_g + f.getlength(mot[:n]) + 8
                    d.rectangle([xc, yv - 72, xc + 42, yv + 72], fill=(244, 196, 48, 255))
                vecteur(c["F"], cur)
        apres = ws[ws.index(tape[0]) + 1:] if tape else ws
        g = groupe_du_moment(groupes(apres), t)
        if g and t >= g[0]["start"]: ligne(c["F"], g, t, W / 2, min(BOT - 70, fy + sz / 2 + 140), font("Outfit.ttf", 84, 700), fill=(255, 255, 255), shadow=True)   # ombre : lisible sur le crème ET sur le noir
    elif phase == 1:
        g = groupe_du_moment(groupes(ws[:ws.index(flash[0])] if flash else ws), t)
        if g: ligne(c["F"], g, t, W / 2, sous_menton(c, 0.62 * H), font("Outfit.ttf", 84, 700))


def st_rdv(c):
    """« Ce dimanche à vingt heures » : DIMANCHE en grosses capitales + 20 H doré géant derrière la tête."""
    t, ws = c["t"], c["mots"]
    top = c["etat"].setdefault("top0", c["tete"][0])
    jour = suite(ws, c["sc"].get("jour", "dimanche"))
    heure = suite(ws, c["sc"].get("heure", "vingt heures"))
    if jour and t >= jour[0]["start"] - 0.02:
        v = (t - jour[0]["start"] + 0.02) / 0.2
        f = font("BebasNeue-Regular.ttf", 190)
        s = sprite("DIMANCHE", f)
        ombre(c["F"], s, W / 2, TOP + 65, pop(v, 0.7, 0.06), 0, 1, 0, 0.7, 8)
        paste(c["F"], s, W / 2, TOP + 65, pop(v, 0.7, 0.06))
    if heure and t >= heure[0]["start"] - 0.02:
        spr, A = sprite_or(c["sc"].get("texte_heure", "20 H"), 280)
        v = (t - heure[0]["start"] + 0.02) / 0.25
        cy = max(TOP + 285, top - 40)   # la tête ne touche que le bas du « 20 H » ; 35 px sous DIMANCHE
        paste(c["B"], teinte(spr, (0, 0, 0), 0.6), W / 2 + 6, cy + 14, pop(v, 0.7, 0.06), 0, 1, 14)
        paste(c["B"], spr, W / 2, cy, pop(v, 0.7, 0.06))
    # pas de « ce à » avant DIMANCHE ; après « vingt heures », la suite en petit sous le menton
    if heure:
        g = groupe_du_moment(groupes(ws[ws.index(heure[-1]) + 1:]), t)
        if g: ligne(c["F"], g, t, W / 2, sous_menton(c, 0.64 * H), font("Outfit.ttf", 84, 700))


def soleil(cv, x, y, r, p):
    """Petit logo soleil orange (comme l'astérisque de Claude dans l'original)."""
    def d_(d, im):
        for k in range(12):
            a = k * math.pi / 6 + p * 0.6
            rr = r * (1 if k % 2 == 0 else 0.72) * ease(p * 1.5)
            d.line([(x, y), (x + rr * math.cos(a), y + rr * math.sin(a))], fill=(222, 120, 92, 255), width=max(4, int(r * 0.16)))
    vecteur(cv, d_)


def st_carton(c):
    """plein écran en DÉGRADÉ (jamais d'aplat,
    règle ), la phrase apparaît mot à mot sur la voix ; mots-clés en or 3D et en serif italique. Finir le
    carton PILE sur le cut : le saut d'image disparaît."""
    t, ws = c["t"], c["mots"]
    cache = c["cache"]
    fond = c["sc"].get("fond", "brun")
    # dégradé diagonal BIEN visible, bronze -> brun -> presque noir
    FONDS = {"brun": ([150, 92, 44], [58, 34, 20], [10, 8, 7]), "nuit": ([120, 80, 40], [40, 26, 16], [6, 5, 5]),
             "ambre": ([176, 108, 46], [70, 40, 20], [14, 9, 6])}
    if "_carton" + fond not in cache:
        Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
        v = np.clip((X / W) * 0.35 + (Y / H) * 0.85 - 0.05, 0, 1)[..., None]       # haut-gauche clair -> bas-droite sombre
        c1, c2, c3 = (np.array(v_, np.float32) for v_ in FONDS[fond])
        g = np.where(v < 0.5, c1 * (1 - v * 2) + c2 * (v * 2), c2 * (1 - (v - 0.5) * 2) + c3 * ((v - 0.5) * 2)) / 255
        r = np.hypot((X - W * 0.3) / W, (Y - H * 0.2) / H)[..., None]
        g = g + np.clip(0.5 - r, 0, 1) * 0.10                                       # halo doux en haut à gauche
        rng = np.random.default_rng(3)
        g += (rng.standard_normal((H, W, 1)).astype(np.float32) * 0.012)   # grain léger
        cache["_carton" + fond] = np.clip(g, 0, 1)
    c["base"][:] = cache["_carton" + fond]
    zoom = 1.0   # plus de zoom, rien ne bouge
    lignes_ = c["sc"]["lignes"]   # [{"mots": "...", "style": "sans|or|serif|petit"}]
    tailles = {"sans": 86, "or": 250, "serif": 170, "petit": 66, "caps": 230}
    hauteurs = {"sans": 112, "or": 250, "serif": 190, "petit": 92, "caps": 215}
    tot = sum(hauteurs[l["style"]] for l in lignes_)
    y = H * 0.46 - tot / 2
    for l in lignes_:
        hh = hauteurs[l["style"]]
        cy = H * 0.46 + (y + hh / 2 - H * 0.46) * zoom
        ms_ = suite(ws, l["mots"])
        vus = [x for x in ms_ if t >= x["start"] - 0.02]
        y += hh
        if not vus: continue
        txt = " ".join(propre(x["text"]) for x in vus)
        v = apparition(t, vus[-1]["start"], 0.14)
        # chaque mot a déjà SA place (ligne entière mise en page), il apparaît sur place en fondu : aucun recentrage
        if l["style"] == "or":
            tx_or = " ".join(propre(x["text"]) for x in ms_).upper()   # « l'IA » : le l ressemblait à un I
            ta_ = tailles["or"]
            while ta_ > 90:
                l0, t0_, r0, b0 = font("Archivo.ttf", ta_, 900, 112).getbbox(tx_or)
                if r0 - l0 <= W - 2 * MX - 40: break
                ta_ -= 10                                                   # « CLIENTS » débordait de l'écran
            spr, A = sprite_or(tx_or, ta_)
            u = apparition(t, ms_[0]["start"], 0.18)
            paste(c["F"], teinte(spr, (0, 0, 0), 0.6), W / 2 + 6, cy + 14, 1, 0, u, 14)
            paste(c["F"], spr, W / 2, cy, 1, 0, u, 6 * (1 - u))
        elif l["style"] == "serif":
            ligne(c["F"], ms_, t, W / 2, cy, font("InstrumentSerif-Italic.ttf", tailles["serif"]), shadow=True, monte=0)
        elif l["style"] == "caps":
            f_ = font("BebasNeue-Regular.ttf", tailles["caps"])
            plein = " ".join(propre(x["text"]) for x in ms_).upper()
            while f_.getlength(plein) > W - 2 * MX - 20 and f_.size > 100: f_ = font("BebasNeue-Regular.ttf", f_.size - 10)
            ligne(c["F"], ms_, t, W / 2, cy, f_, shadow=True, monte=0, maj=True)
        elif l["style"] == "petit":
            ligne(c["F"], ms_, t, W / 2, cy, font("Outfit.ttf", tailles["petit"], 600), fill=(225, 210, 190), shadow=False, monte=0)
        else:
            ligne(c["F"], ms_, t, W / 2, cy, font("Outfit.ttf", tailles["sans"], 700), shadow=True, monte=0)


STYLES = {"orbite": st_orbite, "choc": st_choc, "neon": st_neon, "lueur": st_lueur, "geant": st_geant, "dit": st_dit, "fleches": st_fleches, "dit2": st_dit2, "accroche": st_accroche, "rien": st_rien, "tracking2": st_tracking2, "rdv": st_rdv, "carton": st_carton,
          "tracking": st_tracking, "contour": st_contour, "serif": st_serif, "filaire": st_filaire, "or": st_or}

# sons par style : (moment, fichier, volume dB, pic du son en s)
def sons_scene(sc, ws):
    out = []
    de = sc["de"]
    def at(t, f, db, pic=0.0): out.append((max(0, t - pic), f, db))
    st = sc["style"]
    cle = sc.get("mot", "")
    def debut_cle():
        s_ = suite(ws, cle) if cle else []
        if s_: return s_[0]["start"]
        for m in ws:
            if propre(m["text"]).upper() == cle.upper() or propre(m["text"]) == cle.split()[0] if cle else False: return m["start"]
        return de
    if st == "accroche":
        for m in ws[1:]: at(m["start"], "tick.wav", -26, 0.004)
        s_ = suite(ws, sc.get("coupe", "autour"))
        if s_: at(s_[0]["start"], "whoosh.wav", -16, 0.131)
    elif st == "rien":
        at(de + 0.05, "jet.wav", -14, 0.544)
    elif st == "tracking2":
        s_ = suite(ws, sc.get("flash", "mon"))
        if s_: at(s_[0]["start"], "glitch.wav", -18, 0.05)
        s_ = suite(ws, sc.get("tape", "visage"))
        if s_:
            for k in range(6): at(s_[0]["start"] + 0.05 * k, "click.wav", -24, 0.004)
    elif st == "carton":
        at(de, "whoosh.wav", -15, 0.131)
        for l in sc.get("lignes", []):
            if l["style"] == "or":
                s_ = suite(ws, l["mots"])
                if s_: at(s_[0]["start"], "impact.wav", -17, 0.066)
    elif st == "rdv":
        s_ = suite(ws, sc.get("jour", "dimanche"))
        if s_: at(s_[0]["start"], "impact.wav", -14, 0.066)
        s_ = suite(ws, sc.get("heure", "vingt heures"))
        if s_: at(s_[0]["start"], "shimmer.wav", -17, 0.03)
    elif st == "dit2":
        for d_ in sc.get("dits", []):
            s_ = suite(ws, d_["mots"])
            if s_: at(s_[0]["start"], {"neon": "glitch.wav", "caps": "impact.wav", "serif": "whoosh.wav"}[d_["style"]], -17, {"caps": 0.066, "serif": 0.131}.get(d_["style"], 0.05))
    elif st == "dit":
        for d_ in sc.get("dits", []):
            s_ = suite(ws, d_["mots"])
            if s_: at(s_[0]["start"], {"neon": "glitch.wav", "caps": "impact.wav", "serif": "whoosh.wav"}[d_["style"]], -17, {"caps": 0.066, "serif": 0.131}.get(d_["style"], 0.05))
    elif st == "fleches":
        s_ = suite(ws, sc.get("zone", "zone"))
        if s_: at(s_[0]["start"], "snatch.wav", -18, 0.386)
        s_ = suite(ws, sc.get("fleches", "Instagram"))
        if s_:
            for k in range(3): at(s_[0]["start"] + 0.12 * k, "tick.wav", -20, 0.004)
    elif st == "orbite":
        for m in ws: at(m["start"], "tick.wav", -24, 0.004)
    elif st == "choc":
        k = debut_cle(); at(k + 0.18, "jet.wav", -16, 0.544); at(k + 0.18, "impact.wav", -14, 0.066)
    elif st == "neon":
        at(debut_cle(), "glitch.wav", -20, 0.05)
    elif st == "geant":
        k = debut_cle(); at(k, "snatch.wav", -16, 0.386); at(k, "pop.wav", -18, 0.03)
    elif st == "tracking":
        at(de, "glitch.wav", -24); at(debut_cle(), "click.wav", -16, 0.004)
    elif st == "contour":
        for m in ws: at(m["start"], "tick.wav", -27, 0.004)
    elif st == "serif":
        at(debut_cle(), "whoosh.wav", -18, 0.131)
    elif st == "filaire":
        at(de, "shimmer.wav", -18, 0.03)
    elif st == "or":
        k = debut_cle(); at(k, "impact.wav", -14, 0.066); at(k + 0.3, "shimmer.wav", -18, 0.03)
    else:
        at(de, "whoosh.wav", -22, 0.131)
    return out


# ------------------------------------------------------------------ caméra
def cameras(plan, tops):
    cams = []
    for sc in plan["scenes"]:
        i0, i1 = int(sc["de"] * FPS), max(int(sc["de"] * FPS) + 1, int(sc["a"] * FPS))
        info = [x for x in tops[i0:i1] if x]
        top = float(np.median([x[0] for x in info])) if info else 400
        cx = float(np.median([x[1] for x in info])) if info else W / 2
        z = sc.get("zoom", 1.0)
        place = sc.get("tete_a", 0.30)   # la tête arrive à 30 % de la hauteur (de la place pour le mot géant)
        cams.append((cx, top, z, place))
    return cams


def matrice(cam, t, de, a, secousse=0.0):
    cx, top, z, place = cam
    p = (t - de) / max(a - de, 1e-3)
    zz = z * (1 + 0.04 * p) * (1 + 0.035 * math.exp(-(t - de) * 14))   # poussée lente + à-coup au début du plan
    ox, oy = W / 2, place * H
    x0 = cx - ox / zz
    y0 = top - oy / zz
    x0 = min(max(x0, 0), W - W / zz)
    y0 = min(max(y0, 0), H - H / zz)
    sx = random.uniform(-1, 1) * secousse; sy = random.uniform(-1, 1) * secousse
    return np.array([[zz, 0, -x0 * zz + sx], [0, zz, -y0 * zz + sy]], np.float32)


# ------------------------------------------------------------------ rendu
def lit_tops(masque, n):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", masque, "-vf", "scale=270:480", "-f", "rawvideo", "-pix_fmt", "gray", "-"])
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 480, 270).astype(np.float32) / 255
    return [tete(f) for f in fr[:n]]


def compose(base, m, B, F, G, ctx):
    if ctx.get("teinte"):
        col, k = ctx["teinte"]
        base[:] = base * (1 - k) + base * np.array(col, np.float32) * k + np.array([0.10, 0.0, 0.03], np.float32) * k
    if ctx.get("vignette"):
        if "_vig" not in ctx["cache"]:
            Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
            r = np.hypot((X - W / 2) / (W * 0.62), (Y - H * 0.42) / (H * 0.62))
            ctx["cache"]["_vig"] = np.clip(1 - (r - 0.55) * 0.9, 0.25, 1)[..., None].astype(np.float32)
        v = ctx["cache"]["_vig"]
        base[:] = base * (1 - ctx["vignette"] + ctx["vignette"] * v)
    mm = m[..., None]
    out = base * (1 - B[..., 3:4] * (1 - mm)) + B[..., :3] * (1 - mm)
    out = out * (1 - F[..., 3:4]) + F[..., :3]
    if ctx.get("glow") and G[..., 3].max() > 0:
        k, s1, s2 = ctx["glow"]
        small = cv2.resize(G[..., :3], (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        g = cv2.GaussianBlur(small, (0, 0), s1 / 4) * 0.6 + cv2.GaussianBlur(small, (0, 0), s2 / 4) * 0.6
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR) * k
        out = 1 - (1 - out) * (1 - np.clip(g, 0, 1))
    return np.clip(out, 0, 1)


def main():
    plan_p = sys.argv[1]
    d = os.path.dirname(os.path.abspath(plan_p))
    plan = json.load(open(plan_p))
    OMBRE[0] = plan.get("ombre", 0.55)
    clip, masque = plan["clip"], os.path.join(d, plan["masque"])
    t0, t1 = plan["t0"], plan["t1"]
    mots = json.load(open(plan["mots"]))
    mots = mots.get("words", mots) if isinstance(mots, dict) else mots
    mots = [m for m in mots if t0 <= m["start"] < t1]
    scenes = plan["scenes"]
    for sc in scenes: sc["_mots"] = [m for m in mots if sc["de"] <= m["start"] < sc["a"]]
    n = int(round((t1 - t0) * FPS))
    tops = lit_tops(masque, n)
    cams = cameras(plan, tops)
    images = None
    if "--images" in sys.argv:
        images = [float(x) for x in sys.argv[sys.argv.index("--images") + 1].split(",")]
    etats = [dict() for _ in scenes]
    cache = {}

    def rend(i, frame, msmall):
        t = t0 + i / FPS
        k = max(j for j, sc in enumerate(scenes) if sc["de"] <= t + 1e-6) if t >= scenes[0]["de"] else 0
        sc = scenes[k]
        sec = 0.0
        if sc["style"] == "choc":
            km = sc["_mots"][-1]["start"] if sc["_mots"] else sc["de"]
            dt = t - (km + 0.18)
            if 0 < dt < 0.3: sec = 18 * (1 - dt / 0.3)
        M = matrice(cams[k], t, sc["de"], sc["a"], sec)
        if sc.get("descend") and t >= sc.get("descend_des", 0): M[1, 2] += sc["descend"]   # fond uni : on peut descendre l'image
        base = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32) / 255
        Ms = M.copy(); Ms[:, :2] *= W / msmall.shape[1]
        m = cv2.warpAffine(msmall, Ms, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).astype(np.float32) / 255
        m = np.clip((m - 0.04) / 0.92, 0, 1)
        info = tete(m) or (400.0, W / 2, 260.0)
        e = etats[k]
        if "lisse" in e:
            info = tuple(0.7 * a + 0.3 * b for a, b in zip(e["lisse"], info))
        e["lisse"] = info
        inv = cv2.invertAffineTransform(M)
        src_xy = inv @ np.array([info[1], info[0] + 0.62 * 1.08 * info[2], 1.0])
        B = np.zeros((H, W, 4), np.float32); F = np.zeros_like(B); G = np.zeros_like(B)
        ctx = {"t": t, "mots": sc["_mots"], "tete": info, "m": m, "B": B, "F": F, "G": G, "base": base, "sc": sc,
               "de": sc["de"], "etat": e, "src_xy": src_xy, "cache": cache}
        if sc["_mots"]: STYLES[sc["style"]](ctx)
        out = compose(ctx["base"], m, B, F, G, ctx)
        return (out * 255 + 0.5).astype(np.uint8)

    if images:
        for tt in images:
            ts = min(tt, plan.get("gel") or tt)   # après le gel : image et masque figés
            fr = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{ts:.3f}", "-i", clip, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
            ms = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{ts - t0:.3f}", "-i", masque, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"])
            o = rend(int(round((tt - t0) * FPS)), np.frombuffer(fr, np.uint8).reshape(H, W, 3), np.frombuffer(ms, np.uint8).reshape(960, 540))
            if "--reperes" in sys.argv:   # lignes rouges = zones Instagram (270 / 1480 px, 65 px des bords)
                o = o.copy(); o[TOP - 2:TOP + 2] = (255, 0, 0); o[BOT - 2:BOT + 2] = (255, 0, 0); o[:, MX - 2:MX + 2] = (255, 0, 0); o[:, W - MX - 2:W - MX + 2] = (255, 0, 0)
            p = os.path.join(d, f"img_{tt:05.2f}.png")
            Image.fromarray(o).save(p); print(p)
        return

    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-i", clip, "-t", f"{t1 - t0:.3f}", "-vf", f"fps={FPS}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    # le masque démarre lui aussi à t0 (avant, il repartait de 0 : rendu partiel = mauvaise silhouette)
    dm = subprocess.Popen(["ffmpeg", "-v", "error", "-i", masque, "-vf", f"trim=start_frame={round(t0 * FPS)},setpts=PTS-STARTPTS", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    muet = os.path.join(d, "_muet.mp4")
    SON = sys.argv[sys.argv.index("--son") + 1] if "--son" in sys.argv else None   # refaire seulement le son sur une image déjà rendue
    if SON: subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SON, "-map", "0:v", "-c", "copy", muet], check=True); n = 0
    enc = None if SON else subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", muet], stdin=subprocess.PIPE)
    gel = plan.get("gel")
    i, buf, mb = 0, None, None
    while i < n:
        if gel is None or t0 + i / FPS < gel or buf is None:
            b2, m2 = dec.stdout.read(W * H * 3), dm.stdout.read(540 * 960)
            if len(b2) < W * H * 3 or len(m2) < 540 * 960:
                if buf is None: break
            else:
                buf, mb = b2, m2
        enc.stdin.write(rend(i, np.frombuffer(buf, np.uint8).reshape(H, W, 3), np.frombuffer(mb, np.uint8).reshape(960, 540)).tobytes())
        i += 1
        if i % 90 == 0: print(f"{i}/{n} images", flush=True)
    if enc: enc.stdin.close(); enc.wait()
    dec.kill(); dm.kill()

    # son : voix d'origine + bruitages calés sur les mots, sous la voix
    sfx_dir = os.path.join(d, plan.get("sfx", "sfx"))
    ev = [e_ for sc in scenes for e_ in sons_scene(sc, sc["_mots"])]
    fin_voix = (gel if gel else t1) - t0
    ins, fil = ["-ss", f"{t0:.3f}", "-t", f"{fin_voix:.3f}", "-i", clip], []
    for j, (tt, f, db) in enumerate(ev):
        ins += ["-i", os.path.join(sfx_dir, f)]
        ms_ = int(max(0, tt - t0) * 1000)
        fil.append(f"[{j + 1}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={db}dB,adelay={ms_}|{ms_}[s{j}]")
    fil.append("[0:a]aformat=sample_rates=48000:channel_layouts=stereo,afade=t=out:st=%.2f:d=0.12,apad=whole_dur=%.3f[v]" % (fin_voix - 0.12, t1 - t0))
    mus = plan.get("musique")
    n_in = len(ev) + 1
    if mus:
        ins += ["-ss", f"{mus.get('depuis', 0):.3f}", "-i", os.path.join(d, mus["src"])]
        fil.append(f"[{len(ev) + 1}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={mus.get('db', -22)}dB,"
                   + ("afade=t=in:d=%s," % plan.get("fondu_musique", 0.3) if plan.get("fondu_musique", 0.3) else "") + f"afade=t=out:st={t1 - t0 - 1.0:.2f}:d=1.0,atrim=0:{t1 - t0:.3f}[mu]")
        n_in += 1
    fil.append("[v]" + "".join(f"[s{j}]" for j in range(len(ev))) + ("[mu]" if mus else "") + f"amix=inputs={n_in}:normalize=0:duration=first,alimiter=limit=0.79:attack=0.5:release=60:level=false[a]")   # pic à +0,3 dB sans limiteur
    son = os.path.join(d, "_son.m4a")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fil), "-map", "[a]", "-c:a", "aac", "-b:a", "192k", son], check=True)
    out = os.path.join(d, plan.get("sortie", "rendu.mp4"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", muet, "-i", son, "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest", out], check=True)
    os.remove(muet); os.remove(son)
    print("rendu :", out)


if __name__ == "__main__":
    main()
