#!/usr/bin/env python3
"""Style Lab « détaillé » (11/11) : la version d'origine, round par round, 1 seule variable par carte.
Round 1 = sous-titres (police, taille, emplacement, mot fort). Les rounds suivants (titre, cartons et chiffres,
transitions et sons) partent de ce qui a été gardé (--keep).

  python3 rounds.py build --round 1 --client moi --clip clip.mp4 --words words.json --start 0.1 --end 7.4 \\
      --keyword temps --music "/chemin/musique.mp3" --music-from 1.5 --out ~/Documents/Montage/STYLE-LAB/<client>/r1
  -> <out>/round.json + 1 dossier par carte (full.mp4 avec le son, preview.mp4 muet) + planche-<section>.jpg
  Puis : upload des assets, `round.py db` pour écrire la base, comme STYLE-LAB.md étape 3.
"""
import argparse, concurrent.futures as cf, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round as R   # make / render / finish / FONTS / SCALES du Style Lab client

# 4 familles VRAIMENT différentes (juge 11/11 : Montserrat / Poppins / Inter se confondaient) ; le mot fort reste en Instrument Serif
FONTS = [("Montserrat.ttf", "InstrumentSerif-Italic.ttf", "Montserrat", "Large et sobre, celle de la maison."),
         ("BebasNeue-Regular.ttf", "InstrumentSerif-Italic.ttf", "Bebas", "Haute et serrée, look affiche."),
         ("Cinzel.ttf", "InstrumentSerif-Italic.ttf", "Cinzel", "Capitales à empattements, luxe classique."),
         ("SpaceGrotesk.ttf", "InstrumentSerif-Italic.ttf", "Space Grotesk", "Moderne et tech, un peu décalée.")]
R.SCALES.setdefault("SpaceGrotesk.ttf", 1.0)
SIZES = [(40, "Petite", "Discrète, on voit plus ton visage."), (52, "Moyenne", "Celle de la maison."), (64, "Grande", "Lisible de loin."),
         (76, "Très grande", "Les mots prennent toute la place.")]
PLACES = [(950, "Haut du torse", "Juste sous le visage."), (1120, "Milieu du torse", "Entre le visage et la ceinture."),
          (None, "Bas (auto)", "Calculée sur ton rush : la zone sombre la plus lisible, loin du visage.")]
KW = [(True, "Avec mot fort", "Au moment du mot clé, il remplace le sous-titre : seul, en grand, en italique."), (False, "Sans mot fort", "Le sous-titre normal continue, plus sobre.")]


def build(a):
    out = os.path.abspath(os.path.expanduser(a.out))
    os.makedirs(os.path.join(out, "_base"), exist_ok=True)
    R.sh(["ffmpeg", "-v", "error", "-y", "-ss", str(a.start), "-to", str(a.end), "-i", a.clip, "-c:v", "libx264", "-crf", "16", "-preset", "medium",
          "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", os.path.join(out, "_base", "clip.mp4")])
    W = json.load(open(a.words))["words"]
    W = [{**w, "start": round(w["start"] - a.start, 3), "end": round(w["end"] - a.start, 3)} for w in W if w["start"] >= a.start - 0.01 and w["end"] <= a.end + 0.01]
    json.dump({"words": W}, open(os.path.join(out, "_base", "words.json"), "w"), ensure_ascii=False)
    mus = {"src": os.path.abspath(a.music), "from": a.music_from}
    F0 = FONTS[0]
    pal = {"text": "#FFFFFF", "halo": "0,0,0", "glow": "0,0,0", "accent": "#2F74FF"}

    L = json.loads(a.lock or "{}")   # choix des rounds d'avant (R1 : sans, subSize, subY)
    if L.get("sans"): F0 = (L["sans"], F0[1]) + tuple(F0[2:])
    TITLE = None
    if a.title:
        l1, l2 = a.title.split("|"); TITLE = {"l1": l1, "l2": l2, "start": 0, "end": a.title_end, "top": 280}

    def variant(name, sans=None, serif=None, size=None, y=None, kw=True, title=None):
        sans, serif = sans or F0[0], serif or F0[1]
        size = size or L.get("subSize"); y = y or L.get("subY")
        da = R.base_da(a.client, (sans, serif), pal, [5, 8])
        if size: da["subSize"] = round(size * R.SCALES.get(sans, 1))
        d = os.path.join(out, name); os.makedirs(d, exist_ok=True)
        for f in ("clip.mp4", "words.json"):
            p = os.path.join(d, f)
            if not os.path.exists(p):
                try: os.link(os.path.join(out, "_base", f), p)
                except OSError: R.shutil.copy(os.path.join(out, "_base", f), p)
        json.dump(da, open(os.path.join(d, "da.json"), "w"), ensure_ascii=False, indent=1)
        plan = {"cam": "clip.mp4", "words": "words.json", "da": "da.json", "fixes": json.loads(a.fixes or "{}"),
                "keywords": [a.keyword] if kw else [], "music": mus}
        if y: plan["subY"] = y
        if title: plan["title"] = title; plan["keywords"] = []
        json.dump(plan, open(os.path.join(d, "plan.json"), "w"), ensure_ascii=False, indent=1)
        return d

    cards, jobs = [], set()
    def card(cid, sec, label, desc, d, meta):
        jobs.add(d)
        cards.append({"id": cid, "section": sec, "label": label, "desc": desc, "kind": "video",
                      "file_full": os.path.join(d, "full.mp4"), "file_preview": os.path.join(d, "preview.mp4"), "sound": False, "meta": meta})

    if a.round == "2":
        return build2(a, out, variant, card, cards, jobs, TITLE)
    base = variant("base")
    for i, (sans, serif, lab, desc) in enumerate(FONTS):
        d = base if i == 0 else variant(f"police-{'abcd'[i]}", sans, serif)
        card(f"r1-police-{'abcd'[i]}", "police", lab, desc, d, {"fonts": {"sans": sans, "serif": serif, "sub": sans}})
    for i, (px, lab, desc) in enumerate(SIZES):
        d = base if px == 52 else variant(f"taille-{px}", size=px)
        card(f"r1-taille-{px}", "taille", f"{lab} ({px} px)", desc, d, {"subSize": px})
    places = [tuple(x) for x in json.loads(a.places)] if a.places else PLACES
    for i, (y, lab, desc) in enumerate(places):
        d = base if y is None else variant(f"place-{y}", y=y)
        card(f"r1-place-{'abc'[i]}", "place", lab, desc, d, {"subY": y})
    for on, lab, desc in KW:
        d = base if on else variant("sans-mot-fort", kw=False)
        card(f"r1-motfort-{'oui' if on else 'non'}", "motfort", lab, desc, d, {"motFort": on})

    print(f"rendu de {len(jobs)} variantes (3 en parallèle)…", flush=True)
    with cf.ThreadPoolExecutor(3) as ex: list(ex.map(R.render, sorted(jobs)))
    with cf.ThreadPoolExecutor(3) as ex: list(ex.map(R.finish, sorted(jobs)))

    sections = [{"id": "police", "name": "Ta police", "use": "Même vidéo, seule la police change.", "order": 1},
                {"id": "taille", "name": "Ta taille", "use": "Même vidéo, seule la taille des sous-titres change.", "order": 2},
                {"id": "place", "name": "Ton emplacement", "use": "Même vidéo, seule la hauteur des sous-titres change.", "order": 3},
                {"id": "motfort", "name": "Ton mot fort", "use": "Avec ou sans le mot clé en grand.", "order": 4}]
    finish_round(a, out, cards, sections, "1", f"Round 1 : tes sous-titres, {a.client}", ["Round 2 : ton titre. Round 3 : cartons et chiffres. Round 4 : transitions et sons."])


def finish_round(a, out, cards, sections, num, title, notes):
    for i, c in enumerate(cards): c["order"] = i + 1
    rnd = {"title": title, "round": num, "aspect": "9:16",
           "intro": "Une seule chose change par carte. « Garder celle-ci » sur UNE carte par section, une note si besoin, puis « Envoyer mon avis ».",
           "notes": notes}
    json.dump({"round": rnd, "sections": sections, "cards": cards, "client": a.client}, open(os.path.join(out, "round.json"), "w"), ensure_ascii=False, indent=1)
    fnt = os.path.join(R.SKILL, "fonts", "Montserrat.ttf")
    t = a.thumb_at if a.thumb_at is not None else (a.end - a.start) / 2
    for s in sections:
        thumbs = []
        for j, c in enumerate(cc for cc in cards if cc["section"] == s["id"]):
            p = os.path.join(out, f"_thumb-{c['id']}.jpg")
            tt = a.kw_at if s["id"] == "motfort" and a.kw_at is not None else t
            R.sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{tt:.2f}", "-i", c["file_full"], "-frames:v", "1", "-vf",
                  f"scale=360:640,drawtext=fontfile={fnt}:text={'ABCD'[j]}:x=16:y=16:fontsize=44:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=8", p])
            thumbs.append(p)
        ins = sum((["-i", p] for p in thumbs), [])
        R.sh(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", f"hstack={len(thumbs)}", "-frames:v", "1", os.path.join(out, f"planche-{s['id']}.jpg")])
        for p in thumbs: os.remove(p)
    print(f"OK {len(cards)} cartes -> {os.path.join(out, 'round.json')}")


T2_FONTS = [("InstrumentSerif-Italic.ttf", "Instrument Serif", "Fine et élégante, celle de la maison."),
            ("PlayfairDisplay-Italic.ttf", "Playfair", "Classique, contrastée."),
            ("BodoniModa-Italic.ttf", "Bodoni", "Magazine de mode, très fine."),
            ("DMSerifDisplay-Italic.ttf", "DM Serif", "Épaisse, elle claque.")]


def build2(a, out, variant, card, cards, jobs, T):
    """Round 2 : le titre du début (2 lignes : petites capitales + serif italique). 1 variable par carte."""
    base = variant("base", title=T)
    for i, (serif, lab, desc) in enumerate(T2_FONTS):
        d = base if i == 0 else variant(f"t-police-{'abcd'[i]}", serif=serif, title=T)
        card(f"r2-police-{'abcd'[i]}", "tpolice", lab, desc + " Regarde la 2e ligne.", d, {"fonts": {"serif": serif}})
    for k, sz, lab, desc in [("petit", [38, 84], "Petit", "Discret, le visage d'abord."), ("moyen", None, "Moyen", "Celui de la maison."),
                             ("grand", [56, 132], "Grand", "Il saute aux yeux.")]:
        d = base if sz is None else variant(f"t-taille-{k}", title={**T, "size": sz})
        card(f"r2-taille-{k}", "ttaille", lab, desc, d, {"titleSize": sz})
    for k, top, lab, desc in [("haut", 280, "En haut", "Au-dessus de ta tête."), ("bas", 1150, "Sur le torse", "Plus bas, sous ton visage.")]:
        d = base if top == 280 else variant(f"t-place-{k}", title={**T, "top": top})
        card(f"r2-place-{k}", "tplace", lab, desc, d, {"titleTop": top})
    for k, box, lab, desc in [("ombre", None, "Ombre seule", "Le texte directement sur l'image."), ("encadre", True, "Encadré noir", "Un cadre arrondi derrière le texte.")]:
        d = base if box is None else variant(f"t-fond-{k}", title={**T, "box": box})
        card(f"r2-fond-{k}", "tfond", lab, desc, d, {"titleBox": box})
    print(f"rendu de {len(jobs)} variantes (3 en parallèle)…", flush=True)
    with cf.ThreadPoolExecutor(3) as ex: list(ex.map(R.render, sorted(jobs)))
    with cf.ThreadPoolExecutor(3) as ex: list(ex.map(R.finish, sorted(jobs)))
    sections = [{"id": "tpolice", "name": "Police du titre", "use": "Même vidéo, seule la police de la 2e ligne change.", "order": 1},
                {"id": "ttaille", "name": "Taille du titre", "use": "Même vidéo, seule la taille du titre change.", "order": 2},
                {"id": "tplace", "name": "Place du titre", "use": "Même vidéo, seule la hauteur du titre change.", "order": 3},
                {"id": "tfond", "name": "Fond du titre", "use": "Avec ou sans cadre derrière.", "order": 4}]
    finish_round(a, out, cards, sections, "2", f"Round 2 : ton titre, {a.client}", ["Round 3 : cartons et chiffres. Round 4 : transitions et sons."])


if __name__ == "__main__":
    p = argparse.ArgumentParser(); sp = p.add_subparsers(dest="cmd", required=True)
    b = sp.add_parser("build")
    for k in ("--clip", "--words", "--keyword", "--music", "--out"): b.add_argument(k, required=True)
    for k in ("--start", "--end"): b.add_argument(k, type=float, required=True)
    b.add_argument("--music-from", type=float, default=0); b.add_argument("--thumb-at", type=float); b.add_argument("--places", help='[[y ou null, "label", "desc"], ...] : 3 hauteurs adaptées au cadrage du rush'); b.add_argument("--kw-at", type=float, help="moment du mot fort (planche motfort)")
    b.add_argument("--round", default="1"); b.add_argument("--client", default="client"); b.add_argument("--fixes")
    b.add_argument("--lock", help='choix gardés avant : {"sans": "Montserrat.ttf", "subSize": 52, "subY": null}')
    b.add_argument("--title", help="round 2 : « ligne 1|ligne 2 » du titre (SES mots)"); b.add_argument("--title-end", type=float, default=4.0)
    a = p.parse_args()
    build(a)
