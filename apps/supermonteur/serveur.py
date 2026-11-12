"""SuperMonteur : le petit serveur local (28/10/2026).  python3 serveur.py [port]  ->  http://localhost:8801

Écrans : 0 style · 1 retours · 2 Ma DA (tiroir SuperDA) · 3 publier. Les reels vivent dans reels/<id>/ (etat.json,
retours.json, versions/). « Suivant : corrige mes retours » écrit reels/<id>/demande.json + a-corriger.json (la boîte
que Claude lit, mode d'emploi : CLAUDE.md). Publication réelle depuis le 28/10 (clic confirmé de l’utilisateur, apps/publier.py).
"""
import datetime, io, json, mimetypes, os, re, shutil, subprocess, sys, threading, time, urllib.parse, urllib.request, zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

APP = os.path.dirname(os.path.abspath(__file__))
REELS = os.path.join(APP, "reels")
WEB = os.path.join(APP, "web")
sys.path.insert(0, APP)
import da as DA
from monter import lire, ecrire, etat, pousser_ref, garder_eveille
import images
sys.path.insert(0, os.path.dirname(APP))
import ouvrier_claude
import publier
import reglages_apps

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8801
os.makedirs(REELS, exist_ok=True)
CASES = {  # devine-format.md 3 bis (B-rolls décochés par défaut, maquette 0-style validée)
    "Dynamique": [["titre", "titre"], ["sous_titres", "sous-titres"], ["ecran_coupe", "écran coupé"], ["cartons", "cartons"],
                  ["animations", "animations"], ["mots_geants", "mots géants"], ["brolls", "B-rolls"], ["bruitages", "bruitages"]],
    "Minimaliste": [["titre", "titre"], ["sous_titres", "sous-titres"]],
    "Comparatif": [["titre", "titre"], ["tableau", "tableau"], ["sous_titres", "sous-titres"], ["bruitages", "bruitages"]],
    "Interview": [["titre", "titre"], ["sous_titres", "sous-titres"], ["ecran_coupe", "écran coupé"], ["plein_ecran", "plein écran sur qui parle"]],
    "Inspiration": [],   # 29/10 : remplace « Autre » = le montage d'un reel à reprendre (lien ou vidéo)
}
RESEAUX = ["Instagram", "TikTok", "YouTube Shorts", "Facebook", "LinkedIn"]
LIEN_REF = re.compile(r"https?://([\w-]+\.)?(instagram\.com|tiktok\.com|youtube\.com|youtu\.be)/\S+$")


def D(rid):
    if not re.fullmatch(r"[\w-]+", rid or ""): raise KeyError(rid)
    d = os.path.join(REELS, rid)
    if not os.path.isdir(d): raise KeyError(rid)
    return d


def sonde(f):
    """Ce qui doit être identique pour coller sans réencoder (rapide, zéro perte)."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", f], capture_output=True, text=True, timeout=60)
    st = json.loads(r.stdout or "{}").get("streams", [])
    v = next((x for x in st if x.get("codec_type") == "video"), None)
    a = next((x for x in st if x.get("codec_type") == "audio"), None)
    if not v: raise RuntimeError(f"pas d'image dans {os.path.basename(f)}")
    rot = next((sd.get("rotation") for sd in v.get("side_data_list", []) if "rotation" in sd), 0) or int((v.get("tags") or {}).get("rotate", 0) or 0)
    cle = (v.get("codec_name"), v.get("width"), v.get("height"), v.get("r_frame_rate"), v.get("pix_fmt"), rot,
           a and (a.get("codec_name"), a.get("sample_rate"), a.get("channels")))
    return cle, v, a


def assembler_rushs(rushs, out):
    """Rushes collés bout à bout dans out. Mêmes réglages caméra = copie directe ; sinon réencodage au format du 1er.
    Les rushes d'origine ne sont jamais touchés ; écrit dans .part, gardé seulement si complet."""
    sondes = [sonde(f) for f in rushs]
    part = out + ".part.mp4"
    if len({s[0] for s in sondes}) == 1:
        liste = out + ".liste.txt"
        with open(liste, "w") as fl:
            fl.write("".join("file '" + f.replace("'", "'\\''") + "'\n" for f in rushs))
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", liste, "-map", "0:v:0", "-map", "0:a?",
               "-c", "copy", "-movflags", "+faststart", part]
    else:
        liste = None
        v0 = sondes[0][1]
        w, h = int(v0["width"]), int(v0["height"])
        rot = sondes[0][0][5] or 0
        if abs(int(rot)) % 180 == 90: w, h = h, w
        fps = v0.get("r_frame_rate") or "30/1"
        ent, flt, n = [], "", len(rushs)
        for f in rushs: ent += ["-i", f]
        j = n
        for i, (f, (_, _, a)) in enumerate(zip(rushs, sondes)):
            flt += (f"[{i}:v:0]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
                    f"setsar=1,fps={fps},format=yuv420p[v{i}];")
            if a:
                flt += f"[{i}:a:0]aresample=48000,aformat=channel_layouts=stereo[a{i}];"
            else:   # rush sans son : silence de sa durée
                dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                           capture_output=True, text=True).stdout.strip() or 1)
                ent += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
                flt += f"[{j}:a]anull[a{i}];"
                j += 1
        flt += "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
        cmd = ["ffmpeg", "-y", "-v", "error", *ent, "-filter_complex", flt, "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-c:a", "aac", "-b:a", "256k",
               "-movflags", "+faststart", part]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.getsize(part): raise RuntimeError(r.stderr.strip()[-300:] or "ffmpeg")
        os.replace(part, out)
    finally:
        for x in (part, liste):
            if x and os.path.exists(x): os.remove(x)


def coller_puis_regarder(rid, rushs, rush):
    d = D(rid)
    def fil():
        try:
            assembler_rushs(rushs, rush)
            etat(d, etape="Je regarde ta vidéo…")
            lancer("regarder", rid)
        except Exception as x:
            etat(d, statut="erreur", etape="", erreur=f"Je n'ai pas pu coller tes rushes : {str(x)[-300:]}")
    threading.Thread(target=fil, daemon=True).start()


def lancer(action, rid):
    log = open(os.path.join(D(rid), f"_{action}.log"), "a")
    subprocess.Popen([sys.executable, os.path.join(APP, "monter.py"), action, D(rid)], stdout=log, stderr=log, cwd=APP,
                     start_new_session=True)


# 29/10 : le DERUSH LAB (skill outils/cockpit, cockpit.py --lab) dans l'écran, entre le 1er dérush de Claude et le montage.
# Un petit serveur par reel en statut « derush », sur un port libre à partir de 8830 ; arrêté à « Monter le reel ».
COCKPIT = os.path.expanduser("~/.claude/skills/supermonteur/outils/cockpit/cockpit.py")
LABS = {}   # rid -> (process ou None si repris d'un ancien serveur, pid, port)
VERROU_LAB = threading.Lock()
# 29/10 : serveur redémarré = LABS vide = 2e Lab lancé sur le même reel (+ son aperçu ffmpeg) -> derush de 15 min.
# Le pid et le port du Lab sont écrits dans le dossier du reel ; un Lab vivant est repris, jamais doublé.
LAB_PID = "_derushlab.pid"


def lab_vivant(pid, port):
    try:
        os.kill(pid, 0)
        urllib.request.urlopen(f"http://127.0.0.1:{port}/api/etat", timeout=2)
        return True
    except Exception:
        return False


def port_libre():
    import socket
    pris = {p for _, _, p in LABS.values()}
    for p in range(8830, 8900):
        if p in pris: continue
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)): return p
    raise RuntimeError("aucun port libre pour le Derush Lab")


def lab(rid):
    """Le port du Derush Lab de ce reel (lancé s'il ne tourne pas : 1re ouverture, ou serveur redémarré)."""
    with VERROU_LAB:
        pr, pid, port = LABS.get(rid, (None, None, None))
        if pr and pr.poll() is None: return port
        if not pr and pid and lab_vivant(pid, port): return port
        try:
            pid, port = map(int, open(os.path.join(D(rid), LAB_PID)).read().split())
            if lab_vivant(pid, port):
                LABS[rid] = (None, pid, port)
                return port
        except (OSError, ValueError):
            pass
        port = port_libre()
        log = open(os.path.join(D(rid), "_derushlab.log"), "a")
        pr = subprocess.Popen([sys.executable, COCKPIT, D(rid), "--port", str(port), "--lab"], stdout=log, stderr=log,
                              cwd=D(rid), start_new_session=True)
        LABS[rid] = (pr, pr.pid, port)
        with open(os.path.join(D(rid), LAB_PID), "w") as f:
            f.write(f"{pr.pid} {port}")
        for _ in range(40):   # la page répond en ~1 s ; l'aperçu du rush se fait ensuite dans son coin
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/api/etat", timeout=1)
                break
            except Exception:
                if pr.poll() is not None: break
                time.sleep(.25)
        return port


def arreter_lab(rid):
    with VERROU_LAB:
        pr, pid, _ = LABS.pop(rid, (None, None, None))
        if pr and pr.poll() is None: pr.terminate()
        if not pr and pid:
            try: os.kill(pid, 15)
            except OSError: pass
        try: os.remove(os.path.join(D(rid), LAB_PID))
        except OSError: pass


def lab_valide(d):
    """Le Derush Lab a validé ce dérush (« ✓ Valider le dérush », aucune retouche depuis = mêmes plages) :
    "ok" = Gardien du dérush vert, "rouge" = il voit un point (l’utilisateur peut monter quand même : faux positifs), None = pas validé."""
    C = lire(os.path.join(d, "cockpit-etat.json"), {}) or {}
    L, pl = C.get("lab") or {}, (C.get("derush") or {}).get("plages")
    r2 = lambda x: [[round(a, 2), round(b, 2)] for a, b in (x or [])]
    if not pl or r2(L.get("plages")) != r2(pl): return None
    return "ok" if L.get("ok") else "rouge"


CONSIGNE = """Tu es Claude, DANS l'appli SuperMonteur de l’utilisateur (dossier actuel). Ne publie rien.
l’utilisateur a cliqué « Suivant : corrige mes retours » pour le reel %s (dossier %s, version %s). Ses retours :
%s
Suis la section « Quand l’utilisateur dit corrige mes retours » de CLAUDE.md (lis-le d'abord) et les règles du skill
~/.claude/skills/supermonteur/ (SKILL.md, feedback.md, fichier du style). Regarde l'image au temps de chaque retour
(`ffmpeg -ss <t> -i <dossier>/final.mp4 -frames:v 1 <dossier>/_retour-<n>.jpg` puis Read), corrige plan.json,
lance `python3 monter.py remonter <dossier>`, passe chaque retour traité en "statut": "corrige" + "reponse" (1 ligne) dans retours.json,
retire ce reel de a-corriger.json, et note 1 ligne datée par retour dans feedback-retours.md (ici).
Montage à reprendre (dossier <dossier>/ref/ : la vidéo, planche.jpg = 1 image par seconde, *.analyse.json = coupes, débit, musique, SFX) :
copie son montage pour CE reel seulement, FIDÈLE à son concept et son style (mise en page, couleurs, rythme, zooms, sous-titres,
cartons, motion, transitions, musique, bruitages) : seule la police change, celle de la DA (plan.json "da"). Les images de chaque
plan = celles que l’utilisateur a choisies (liste dans le retour, détail dans images.json), aucune autre. Regarde planche.jpg (Read) et d'autres images au besoin (`ffmpeg -ss <t> -i <vidéo de ref/>`).
Réponds en 1 ligne quand la nouvelle version est montée."""
ESSAIS = {}  # (reel, version) -> nombre d'essais

# 03/11 (RUSH : Opus 15 min sur 4 retours, arrêté sans répondre) : les retours simples passent par Sonnet avec une fiche
# d'1 page (FICHE-RETOURS.md) au lieu de CLAUDE.md + SKILL.md + feedback.md (~45 000 mots), 4 min max. Claude ne fait QUE corriger
# plan.json / words.json et écrire reponses.json ; le serveur prend les images avant, remonte, répond à l’utilisateur et vide la boîte
# lui-même (avant : 4 à 6 allers-retours de Claude, et un Claude qui s'arrête = retours jamais répondus).
# 11/11 (studio Super, « mets le titre en plus gros » : 1 min de Claude pour 1 chiffre) : la fiche et plan.json sont DANS la
# consigne (plus de Read), Claude écrit 1 seul fichier neuf, retouche.json = {"plan": <morceau de plan.json à changer>,
# "reponses": {...}}, que le serveur fusionne lui-même dans plan.json ; le serveur note aussi feedback-retours.md. Il reste
# 2 tours de Claude au lieu de 5 à 7. Les fichiers du dérush (cut.segments.json…) sont remis tels quels si Claude y touche :
# le 10/11 il avait réécrit cut.segments.json à la main, d'où un « plan de 0,11 s » fantôme et la v4 bloquée.
CONSIGNE_RAPIDE = """Tu es Claude dans l'appli SuperMonteur de l’utilisateur. Ne publie rien. Ne lance aucune commande : le serveur remonte
la version suivante tout seul dès que tu as fini. Va vite : 1 seul Write dans le cas courant.
Reel %s, dossier %s, version %s. Retours de l’utilisateur (t = seconde dans la version affichée) et l'image de cet instant :
%s

=== FICHE-RETOURS.md ===
%s

=== plan.json actuel ===
%s

Ce que tu fais :
1. Write %s/retouche.json (fichier neuf) = {"plan": {<SEULEMENT les clés de plan.json qui changent, objets imbriqués fusionnés,
   null = retirer la clé, une liste se donne en entier>}, "reponses": {"<id>": "1 ligne pour l’utilisateur : ce qui a changé"}}.
   Une réponse pour CHAQUE retour ; pas faisable ici = "pas fait : <pourquoi>".
2. Seulement si un retour l'exige : Read une image (retour sur ce qu'on voit à un endroit précis), ou Read + Edit de
   %s/words.json (mot courant mal écrit). Couper un mot / un « euh » : clé "couper" de retouche.json (numéros #k de words.json,
   donnés dans la ligne « note LOCALE »), jamais %s/drop.json (le serveur s'en charge).
Ne touche à aucun autre fichier. Réponds en 1 ligne."""


def fusion(a, p):
    """JSON merge patch (RFC 7396) : p change a ; null retire la clé ; une liste remplace la liste."""
    if not isinstance(p, dict): return p
    a = dict(a) if isinstance(a, dict) else {}
    for k, v in p.items():
        if v is None: a.pop(k, None)
        else: a[k] = fusion(a.get(k), v)
    return a


INTOUCHABLES = ("cut.segments.json", "cut.voice.json", "words.rush.json", "cadre.json")   # sortie du dérush : jamais à la main


def proteger_derush(d):
    """Photo des fichiers du dérush avant Claude ; la fonction rendue les remet tels quels si Claude les a réécrits À LA MAIN
    (fichier changé mais clip.mp4 inchangé = aucun vrai dérush n'a tourné). Un vrai dérush (remonter -> redecoupe) passe."""
    P = lambda f: os.path.join(d, f)
    photo = {f: open(P(f), "rb").read() for f in INTOUCHABLES if os.path.exists(P(f))}
    clip = os.path.getmtime(P("clip.mp4")) if os.path.exists(P("clip.mp4")) else 0
    def remettre():
        if os.path.exists(P("clip.mp4")) and os.path.getmtime(P("clip.mp4")) != clip: return
        for f, b in photo.items():
            neuf = open(P(f), "rb").read()
            if neuf != b and f == "cut.segments.json":   # fin_propre (règle 0) a seulement ramené la fin de la dernière plage : on garde
                try:
                    a_, n_ = json.loads(b), json.loads(neuf)
                    if len(a_) == len(n_) and a_[:-1] == n_[:-1] and n_[-1][0] == a_[-1][0] and n_[-1][1] < a_[-1][1]: continue
                except Exception: pass
            if neuf != b:
                open(P(f), "wb").write(b)
                print(f"{os.path.basename(d)} : {f} remis tel quel (réécrit à la main, sans dérush)", flush=True)
    return remettre


TITRE_MAX = 100   # px : au-delà le titre descend sur le visage (la largeur seule est mesurée) ; DA 62, ancien maximum validé 104 -> 80


def mesure_titre(d, taille=None):
    """Composition à blanc (~0,5 s, rien d'écrit dans le dossier du reel) : tailles RÉELLES des 2 lignes du titre, en px, telles
    que le moteur les rendra (après rétrécissement pour tenir sur 2 lignes). taille = title.size à essayer (nombre ou [l1, l2])."""
    plan = lire(os.path.join(d, "plan.json"), {}) or {}
    if not isinstance(plan.get("title"), dict): return None
    T = dict(plan["title"])
    if taille is not None: T["size"] = taille
    tmp = os.path.join(d, "_taille")
    try:
        os.makedirs(tmp, exist_ok=True)
        ecrire(os.path.join(d, "_taille.plan.json"), {**plan, "title": T, "brolls": [], "inserts": []})
        env = dict(os.environ, PATH=os.path.expanduser("~/.local/bin") + ":" + os.path.expanduser("~/.local/node/bin") + ":" + os.environ.get("PATH", ""))
        subprocess.run(["node", os.path.expanduser("~/.claude/skills/supermonteur/scripts/build.mjs"), "--plan", "_taille.plan.json",
                        "--out", os.path.join(tmp, "index.html")], cwd=d, env=env, capture_output=True, text=True, timeout=60)
        page = open(os.path.join(tmp, "index.html"), encoding="utf-8").read()
        fs = [re.findall(r"\.%s\{[^}]*?font-size:(\d+)px" % k, page) for k in ("ht1", "ht2")]   # la DERNIÈRE règle gagne
        return (int(fs[0][-1]), int(fs[1][-1])) if fs[0] and fs[1] else None
    except Exception as x:
        print("mesure_titre :", x, flush=True)
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        if os.path.exists(os.path.join(d, "_taille.plan.json")): os.remove(os.path.join(d, "_taille.plan.json"))


def titre_max(d):
    """11/11 : (taille actuelle [l1, l2], taille max [l1, l2]) du titre. Le titre tient TOUJOURS sur 2 lignes (règle du 23/10 :
    jamais 3), donc le max dépend du texte. Les 2 lignes grossissent ENSEMBLE, dans les mêmes proportions (un titre 52 / 104 px
    reste 1 / 2) ; la plus grande ligne ne dépasse pas max(TITRE_MAX, sa taille actuelle) (au-delà le titre descend sur le visage)."""
    a = mesure_titre(d)
    if not a: return None
    K = 290 / max(a)
    x = mesure_titre(d, [round(a[0] * K), round(a[1] * K)])
    if not x: return None
    T = (lire(os.path.join(d, "plan.json"), {}) or {}).get("title") or {}
    vues = [k for k, l in enumerate((T.get("l1"), T.get("l2"))) if str(l or "").strip()] or [0]   # une ligne vide ne compte pas
    haut = max(a[k] for k in vues)
    f = min(*(x[k] / a[k] for k in vues), max(TITRE_MAX, haut) / haut)
    return a, (int(a[0] * f), int(a[1] * f))


# 11/11 (studio Super, note « baisse un peu la musique ici » posée à 5 s : la musique avait baissé sur TOUTE la vidéo ; méthode de
# l’utilisateur = seules les notes sont retouchées) : une note posée à un moment précis (t > 0) ne change QUE ce moment.
# - le serveur donne à Claude la fenêtre de la note (t ± 2 s, calée sur les mots) et le mot dit à t avec son numéro ;
# - « plus bas / plus fort » sur la musique = music_zones (mix.py, son seul ~20 s) ; si Claude change quand même le niveau
#   global pour une note locale, le serveur le transforme en zone locale et le dit dans la réponse (localiser) ;
# - « coupe ce mot / ce euh » = retouche.json "couper" (numéros de words.json), traduit ici en drop.json : re-dérush + rendu
#   (~3 min) au lieu de la retouche lourde (~10 min).
TOUT = re.compile(r"partout|tout le long|tout du long|toute la vid|tout le reel|toute la musique|sur toute|du d[ée]but [àa] la fin|"
                  r"en g[ée]n[ée]ral|globalement|dans toute|de toute la", re.I)
MUSIQUE = re.compile(r"musique|\bmusic|\bson\b|\bvolume\b", re.I)


def mots_montage(d):
    W = lire(os.path.join(d, "words.json"), {}) or {}
    return W.get("words", W) if isinstance(W, dict) else (W or [])


def fenetre(W, t, demi=2.0):
    """Fenêtre locale d'une note : t ± demi s, bords posés au début / à la fin du mot qu'ils touchent (jamais au milieu d'un mot)."""
    a, b = max(0.0, t - demi), t + demi
    for w in W:
        if w["start"] <= a < w["end"]: a = w["start"]
        if w["start"] < b <= w["end"]: b = w["end"]
    return round(a, 2), round(b, 2)


def mot_a(W, t):
    """Indice du mot dit à t (sinon le plus proche)."""
    if not W: return None
    for k, w in enumerate(W):
        if w["start"] <= t < w["end"] + 0.05: return k
    return min(range(len(W)), key=lambda k: min(abs(W[k]["start"] - t), abs(W[k]["end"] - t)))


def localiser(dem, ancien, X, R, d, niveau):
    """Note posée à un moment précis + niveau GLOBAL de la musique changé par Claude = on remet le niveau global et on pose
    la même différence en zone locale (music_zones). La réponse dit ce qui a vraiment changé, et où."""
    P = X.get("plan")
    if not isinstance(P, dict) or not isinstance(P.get("music"), dict) or "target" not in P["music"]: return
    vieux = ancien.get("music") if isinstance(ancien.get("music"), dict) else None
    if not vieux: return
    avant = vieux.get("target", niveau)
    neuf = P["music"]["target"]
    if not isinstance(neuf, (int, float)) or not isinstance(avant, (int, float)) or neuf == avant: return
    notes = [r for r in dem.get("retours", []) if MUSIQUE.search(str(r.get("texte")))]
    if not notes or any(float(r.get("t") or 0) <= 0 or TOUT.search(str(r.get("texte"))) for r in notes): return
    W = mots_montage(d)
    delta = round(neuf - avant, 1)
    if "target" in vieux: P["music"]["target"] = avant
    else: P["music"].pop("target")
    if not P["music"]: P.pop("music")
    zones = list(P.get("music_zones") or ancien.get("music_zones") or [])
    for r in notes:
        a, b = fenetre(W, float(r["t"]))
        zones.append({"from": a, "to": b, "db": delta, "note": r["id"]})
        R[str(r["id"])] = (f"Musique {'baissée' if delta < 0 else 'montée'} de {abs(delta):g} dB seulement de {a:.1f} à {b:.1f} s".replace(".", ",")
                           + ", là où tu as posé la note. Le reste de la vidéo ne bouge pas.")
    P["music_zones"] = zones
    print(f"{dem['reel']} : niveau global de la musique remis ({avant}), {delta:+g} dB en zone locale", flush=True)


def couper_mots(d, idx):
    """retouche.json "couper" = numéros de mots de words.json (le montage) -> mêmes mots dans drop.json (numéros de
    words.rush.json). Les mots gardés du rush sont, dans l'ordre, ceux de words.json. Renvoie le texte coupé, ou None."""
    rush = lire(os.path.join(d, "words.rush.json"), {}) or {}
    rush = rush.get("words", rush) if isinstance(rush, dict) else rush
    drop = lire(os.path.join(d, "drop.json"), []) or []
    morts = {i for a, b in drop for i in range(a, b + 1)}
    gardes = [i for i in range(len(rush)) if i not in morts]
    W = mots_montage(d)
    if len(gardes) != len(W): return None
    pris = sorted({int(k) for k in idx if isinstance(k, (int, float)) or str(k).isdigit()} & set(range(len(W))))
    if not pris or len(pris) > 12: return None
    if not os.path.exists(os.path.join(d, "drop.avant.json")): ecrire(os.path.join(d, "drop.avant.json"), drop)   # monter.recaler_plan : temps d'avant
    ecrire(os.path.join(d, "drop.json"), sorted(drop + [[gardes[k], gardes[k]] for k in pris]))
    return " ".join(W[k]["text"] for k in pris)


def corriger_vite(dem):
    """Retours simples : Sonnet dit quoi changer, le serveur fait le reste. True = traité (bien ou mal, l'écran le dit)."""
    rid, d, v = dem["reel"], dem["dossier"], dem.get("version")
    vid = os.path.join(d, f"versions/v{v}.mp4") if os.path.exists(os.path.join(d, f"versions/v{v}.mp4")) else os.path.join(d, "final.mp4")
    cafe = garder_eveille()
    try:
        lignes, W = [], mots_montage(d)
        for r in dem.get("retours", []):
            img = os.path.join(d, f"_retour-{r['id']}.jpg")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{float(r.get('t') or 0):.2f}", "-i", vid, "-frames:v", "1",
                            "-vf", "scale=540:-2", img])
            lignes.append(f"- id {r['id']}, à {r.get('t')} s : « {r.get('texte')} » -> image {img}")
            t = float(r.get("t") or 0)
            if t > 0 and W:   # 11/11 : note posée à un moment précis = on retouche CE moment
                a, b = fenetre(W, t); k = mot_a(W, t)
                autour = " ".join(f"#{j} {W[j]['text']}" for j in range(max(0, k - 4), min(len(W), k + 5)))
                lignes.append(f"  note LOCALE : fenêtre {a}-{b} s ; mot dit à {t} s = #{k} « {W[k]['text']} » ({W[k]['start']}-{W[k]['end']} s) ;"
                              f" autour : {autour}")
        for f in ("reponses.json", "retouche.json"):
            if os.path.exists(os.path.join(d, f)): os.remove(os.path.join(d, f))
        sig = lambda: [os.path.getmtime(os.path.join(d, f)) if os.path.exists(os.path.join(d, f)) else 0 for f in ("plan.json", "words.json", "drop.json")]   # 10/11 : drop.json = mot coupé -> re-dérush (monter.py redecoupe)
        remettre = proteger_derush(d)
        avant = sig()
        etat(d, etape="Claude lit tes retours (~20 s)…")
        fiche = open(os.path.join(APP, "FICHE-RETOURS.md"), encoding="utf-8").read()
        _ids = {r["id"] for r in dem.get("retours", [])}
        _hist = [f"- retour {x['id']} (v{x.get('version')}) : « {x.get('texte')} » -> {x.get('reponse') or '…'}"
                 for x in (lire(os.path.join(d, "retours.json"), []) or []) if x.get("id") not in _ids][-8:]
        if _hist: lignes.append("Retours d'avant sur ce reel (déjà traités, pour le contexte : une consigne de l’utilisateur y reste valable) :\n" + "\n".join(_hist))
        plan_txt = open(os.path.join(d, "plan.json"), encoding="utf-8").read()
        _c = re.search(r"cible (-?[\d.]+)", open(os.path.join(d, "mix.log"), encoding="utf-8").read()) if os.path.exists(os.path.join(d, "mix.log")) else None
        if _c: plan_txt += f"\n(niveau actuel de la musique sous la voix, dernier mix : {_c.group(1)} LUFS)"
        tm = titre_max(d)   # ~1 s ; toujours (« agrandis le texte du haut » ne dit pas « titre »)
        if tm:
            (a1, a2), (m1, m2) = tm
            _T = (lire(os.path.join(d, "plan.json"), {}) or {}).get("title") or {}
            un = a1 == a2 or not str(_T.get("l2") or "").strip()   # ligne 2 vide : une seule taille compte, celle de la ligne 1
            dire = lambda x, y: f"{x}" if un else f"[{x}, {y}]"
            c1, c2 = round(a1 * 1.15), round(a2 * 1.15)
            n1 = max(4, int(len(str(_T.get("l1", ""))) * m1 / c1)); n2 = max(4, int(len(str(_T.get("l2", ""))) * m2 / c2))
            plan_txt += (f"\n(titre : taille rendue aujourd'hui {dire(a1, a2)} px" + ("" if un else " (ligne 1, ligne 2 : 2 tailles, garde la proportion, size en liste)")
                         + f" ; avec CE texte il tient sur 2 lignes jusqu'à {dire(m1, m2)} px, jamais 3 lignes. "
                         f"Plus gros demandé : si ce max est au moins 10 % au-dessus, mets size {dire(min(c1, m1), min(c2, m2))}. "
                         f"Sinon, ça ne se verrait pas. Le texte du titre = l'accroche du reel, une décision de l’utilisateur : tu ne le réécris QUE si "
                         f"le retour EN COURS le permet en toutes lettres (« raccourcis-le », « change le texte », « prends la proposition 1 »…) "
                         f"et qu'aucun retour d'avant ne l'interdit. Alors : même sens, mêmes mots clés, même nombre (pluriel garde pluriel), "
                         f"ligne 1 de {n1} caractères au plus et ligne 2 de {n2} au plus (espaces compris), size {dire(c1, c2)} ; le serveur "
                         f"ramène la taille au max réel. Sinon ne change rien et réponds « pas fait : le titre est déjà au max sur 2 lignes "
                         f"({dire(m1, m2)} px). Pour plus gros, il faut un texte plus court : 1) « … / … » 2) « … / … ». Dis-moi lequel. » "
                         f"(2 propositions qui gardent le sens, mêmes limites de caractères)")
        ok, sortie = ouvrier_claude.lancer(CONSIGNE_RAPIDE % (rid, d, v, "\n".join(lignes), fiche, plan_txt, d, d, d), APP,
                                          ["Read", "Write", "Edit"], delai=240, modele="sonnet")
        remettre()
        X = lire(os.path.join(d, "retouche.json"), {}) or {}
        R = X.get("reponses") or lire(os.path.join(d, "reponses.json"), {}) or {}
        ancien = lire(os.path.join(d, "plan.json"), {}) or {}
        localiser(dem, ancien, X, R, d, float(_c.group(1)) if _c else None)
        if X.get("couper"):
            coupe = couper_mots(d, X["couper"] if isinstance(X["couper"], list) else [X["couper"]])
            if coupe is None:
                for k in R:
                    if re.search(r"coup", str(R[k]), re.I) and not str(R[k]).startswith("pas fait"):
                        R[k] = "pas fait : je n'ai pas retrouvé ce mot dans le rush, à couper dans le chat"
        if isinstance(X.get("plan"), dict) and X["plan"] and fusion(ancien, X["plan"]) != ancien:   # identique = pas de rendu pour rien
            ecrire(os.path.join(d, "plan.json"), fusion(ancien, X["plan"]))
            T = (lire(os.path.join(d, "plan.json"), {}) or {}).get("title")
            if isinstance(T, dict) and "size" in T:   # au-delà de ce qui tient, le moteur rétrécirait en silence : le plan dit ce qu'on verra
                z = [x for x in (T["size"] if isinstance(T["size"], list) else [T["size"]]) if isinstance(x, (int, float)) and 20 <= x <= 300]
                if not z: T.pop("size")
                else:
                    z = [z[0], z[1] if len(z) > 1 else z[0]]; demande = list(z)
                    vues = [k for k, l in enumerate((T.get("l1"), T.get("l2"))) if str(l or "").strip()] or [0]   # une ligne vide ne compte pas
                    plafond = max(TITRE_MAX, *([tm[0][k] for k in vues] if tm else [0]))   # la plus grande ligne VUE : jamais plus haut
                    if max(z[k] for k in vues) > plafond: z = [int(v * plafond / max(z[k] for k in vues)) for v in z]
                    r = list(mesure_titre(d, z) or z)   # recalculé : Claude a pu raccourcir le texte
                    if any(r[k] != z[k] for k in vues):   # le moteur rétrécit : on garde la proportion demandée, à la taille qui tient
                        f_ = min(r[k] / z[k] for k in vues); r = [int(v * f_) for v in z]
                    else: r = z
                    if any(r[k] != demande[k] for k in vues):   # la réponse dit la taille RENDUE, jamais la demandée
                        vu = r[vues[0]] if len(vues) == 1 or r[0] == r[1] else r
                        _tit = {str(q["id"]) for q in dem.get("retours", []) if re.search(r"titre|texte du haut|en haut", str(q.get("texte")), re.I)}
                        for k in R:
                            if (k in _tit or (not _tit and re.search(r"titre|px", str(R[k]), re.I))) and not str(R[k]).startswith("pas fait"):
                                R[k] = f"{R[k]} (en vrai : {vu} px, le max sans passer sur 3 lignes ni descendre sur le visage)"
                    T["size"] = r[0] if r[0] == r[1] else list(r)
                plan = lire(os.path.join(d, "plan.json"), {}); plan["title"] = T; ecrire(os.path.join(d, "plan.json"), plan)
        if not R:
            etat(d, statut="erreur", etape="", erreur="Claude n'a pas fini tes retours en 4 min. Écris « corrige mes retours » dans un chat Claude.")
            return True
        ecrire(os.path.join(d, "reponses.json"), R)
        with open(os.path.join(APP, "feedback-retours.md"), "a", encoding="utf-8") as fb:
            for r in dem.get("retours", []):
                if str(r["id"]) in R:
                    fb.write(f"{datetime.date.today():%Y-%m-%d} | {rid} | retour {r['id']} (v{v}) : « {r.get('texte')} » -> {R[str(r['id'])]}\n")
        if sig() != avant:
            etat(d, etape="Je remonte la version suivante…")
            r = subprocess.run([sys.executable, os.path.join(APP, "monter.py"), "remonter", d], cwd=APP,
                               stdout=open(os.path.join(d, f"_remonter-v{(v or 0) + 1}.log"), "a"), stderr=subprocess.STDOUT)
            if r.returncode: return True   # monter.py a déjà mis l'écran en erreur, avec la raison
        tous = lire(os.path.join(d, "retours.json"), []) or []
        for x in tous:
            if str(x.get("id")) in R and x.get("statut") == "a_faire":
                fait = not str(R[str(x["id"])]).startswith("pas fait")
                x.update(statut="corrige" if fait else "a_faire", reponse=R[str(x["id"])])
        ecrire(os.path.join(d, "retours.json"), tous)
        if sig() == avant: etat(d, statut="retours", etape="")
        return True
    finally:
        if cafe: cafe.terminate()


def ouvrier():
    """Dès qu'un reel arrive dans a-corriger.json, Claude corrige et remonte la version suivante tout seul."""
    while True:
        try:
            for dem in lire(os.path.join(APP, "a-corriger.json"), []) or []:
                rid, d = dem.get("reel"), dem.get("dossier")
                if not rid or not d or not os.path.isdir(d):
                    continue
                if lire(os.path.join(d, "etat.json"), {}).get("format") == "16:9":   # 09/11 RUSH : montage 16:9 fait à la main (sous_titres.py), le correcteur auto ne sait que le 9:16 : la demande attend un chat
                    if lire(os.path.join(d, "etat.json"), {}).get("statut") == "correction":
                        etat(d, statut="retours", etape="Vidéo 16:9 : écris « corrige mes retours » dans le chat Claude.")
                    continue
                cle = (rid, dem.get("version"))
                ESSAIS[cle] = ESSAIS.get(cle, 0) + 1
                if ESSAIS[cle] > 2:
                    if lire(os.path.join(d, "etat.json"), {}).get("statut") == "correction":
                        etat(d, statut="erreur", etape="", erreur="Claude n'a pas réussi à corriger tes retours (détails : supermonteur/_claude.log). "
                                                                 "Demande « corrige mes retours » dans un chat Claude.")
                    continue
                if not any(r.get("auto") for r in dem.get("retours", [])):   # retour auto (montage à reprendre) = ancien chemin, Opus
                    try:
                        corriger_vite(dem)
                    finally:
                        boite = lire(os.path.join(APP, "a-corriger.json"), []) or []
                        ecrire(os.path.join(APP, "a-corriger.json"), [x for x in boite if x.get("reel") != rid or x.get("date") != dem.get("date")])
                    break
                retours = "\n".join(f"- à {r.get('t')} s : {r.get('texte')}" for r in dem.get("retours", []))
                remettre = proteger_derush(d)   # 11/11 : même protection sur le chemin lourd (Opus)
                ouvrier_claude.lancer(CONSIGNE % (rid, d, dem.get("version"), retours), APP,
                                      ["Read", "Write", "Edit", "Glob", "Grep", "Bash(python3 monter.py remonter:*)", "Bash(ffmpeg -ss:*)"],
                                      delai=2400)
                remettre()
                break  # un reel à la fois, puis on relit la boîte
        except Exception as x:
            print("ouvrier :", x, flush=True)
        time.sleep(3)


def metricool():
    """Lecture seule. Le serveur ne parle pas à Metricool (c'est Claude, par le connecteur, getBrandSettings) : il lit
    metricool.json, écrit par Claude. Absent ou « branche: false » = mode Télécharger."""
    m = lire(os.path.join(APP, "metricool.json"), {}) or {}
    return {"branche": bool(m.get("branche")), "compte": m.get("compte", ""), "verifie": m.get("verifie", ""),
            "essai": reglages_apps.mode_essai(APP)}  # config.json "mode_essai": false = le bouton Publier publie pour de vrai


def legendes(d):
    """Une légende par réseau (legende-courte : 1-2 phrases, 0 hashtag). Claude les écrit dans legendes.json ; sinon brouillon
    tiré du titre, à relire."""
    L = lire(os.path.join(d, "legendes.json"))
    if L: return L
    p = lire(os.path.join(d, "plan.json"), {}) or {}
    t = p.get("title") or {}
    sujet = (t.get("l1", "") + " " + t.get("l2", "")).strip() or "Nouveau reel"
    return {r: sujet for r in RESEAUX} | {"_brouillon": True}


MONTAGES = reglages_apps.chemin("montages")
PAS_UN_REEL = re.compile(r"test|cockpit|essai|video-use", re.I)


def importer_montages():
    """Les reels montés dans un chat (montages/<date>-<nom>/) apparaissent aussi dans « Tes reels » : reels/<id> devient
    un raccourci vers leur dossier (même format que le moteur), avec un etat.json et ses versions (_v1, _v2… puis final.mp4)
    rangées en versions/vN.mp4 par lien dur (aucune copie, l'ancienne image reste si final.mp4 est refait)."""
    if not os.path.isdir(MONTAGES):
        return
    for nom in os.listdir(MONTAGES):
        src = os.path.join(MONTAGES, nom)
        if (not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[\w-]+", nom) or PAS_UN_REEL.search(nom)
                or os.path.lexists(os.path.join(REELS, nom)) or not os.path.isfile(os.path.join(src, "final.mp4"))):
            continue
        try:
            anciennes = sorted((x for x in os.listdir(src) if re.fullmatch(r"_v\d+", x) and os.path.isfile(os.path.join(src, x, "final.mp4"))),
                               key=lambda x: int(x[2:]))
            os.makedirs(os.path.join(src, "versions"), exist_ok=True)
            versions = []
            for n, f in enumerate([os.path.join(x, "final.mp4") for x in anciennes] + ["final.mp4"], 1):
                cible = os.path.join(src, "versions", f"v{n}.mp4")
                if not os.path.exists(cible):
                    os.link(os.path.join(src, f), cible)
                dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cible],
                                     capture_output=True, text=True).stdout.strip()
                versions.append({"n": n, "fichier": f"versions/v{n}.mp4", "duree": round(float(dur or 0), 2),
                                 "date": datetime.datetime.fromtimestamp(os.path.getmtime(cible)).isoformat(timespec="seconds")})
            if not os.path.exists(os.path.join(src, "etat.json")):
                ecrire(os.path.join(src, "etat.json"), {
                    "id": nom, "nom": nom[11:].upper(), "importe": "monté dans un chat", "statut": "retours", "etape": "",
                    "cree": datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(src, "final.mp4"))).isoformat(timespec="seconds"),
                    "version": len(versions), "versions": versions})
            if not os.path.exists(os.path.join(src, "retours.json")):
                ecrire(os.path.join(src, "retours.json"), [])
            os.symlink(src, os.path.join(REELS, nom))
        except Exception as x:
            print("import", nom, x, file=sys.stderr)


def carte(rid):
    """Une ligne de « Tes reels » : l'état + le titre du reel + une vignette (image à 1,5 s de la dernière version,
    faite une fois puis gardée ; refaite si une nouvelle version sort)."""
    d = os.path.join(REELS, rid)
    e = lire(os.path.join(d, "etat.json"), {})
    if not e or e.get("cache"):   # 29/10 : projet supprimé depuis l'accueil = caché, aucun fichier effacé
        return None
    t = (lire(os.path.join(d, "plan.json"), {}) or {}).get("title") or {}
    e["titre"] = re.sub(r"<[^>]+>", "", " ".join(x for x in (t.get("l1"), t.get("l2")) if x) if isinstance(t, dict) else str(t)).strip()
    v = (e.get("versions") or [{}])[-1].get("fichier")
    if not (v and os.path.isfile(os.path.join(d, v))) and os.path.isfile(os.path.join(d, "final.mp4")):
        v = "final.mp4"   # 10/11 (studio, Publieur : miniatures vides) : reel monté dans un chat = pas de versions, mais un final.mp4
    vig = os.path.join(d, "vignette.jpg")
    if v and os.path.isfile(os.path.join(d, v)):
        if not os.path.exists(vig) or os.path.getmtime(vig) < os.path.getmtime(os.path.join(d, v)):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.5", "-i", os.path.join(d, v), "-frames:v", "1",
                            "-vf", "scale=180:-2", vig], timeout=20)
    if os.path.exists(vig):   # 10/11 : vignette gardée même si la vidéo a été déplacée
        e["vignette"] = f"/media/{rid}/vignette.jpg?t={int(os.path.getmtime(vig))}"
    return e


def titre_reel(d):
    t = (lire(os.path.join(d, "plan.json"), {}) or {}).get("title") or {}
    return re.sub(r"<[^>]+>", "", " ".join(x for x in (t.get("l1"), t.get("l2")) if x) if isinstance(t, dict) else str(t)).strip()


def publieur():
    """Dès qu'un reel a un publication.json « a_faire » (clic confirmé de l’utilisateur), Claude l'envoie à Metricool."""
    for r in os.listdir(REELS):   # un envoi coupé par un redémarrage du serveur : on ne sait pas ce qui est parti
        d = os.path.join(REELS, r)
        if os.path.isdir(d) and publier.etat(d).get("statut") == "en_cours":
            publier._maj(d, statut="erreur", etape="", message="Envoi coupé (serveur relancé) : vérifie le planner Metricool avant de relancer.")
    while True:
        try:
            for r in sorted(os.listdir(REELS)):
                d = os.path.join(REELS, r)
                if os.path.isdir(d) and publier.etat(d).get("statut") == "a_faire":
                    e = lire(os.path.join(d, "etat.json"), {})
                    publier.lancer(d, "SuperMonteur", {"video": os.path.join(d, e["versions"][-1]["fichier"]), "legendes": legendes(d)})
        except Exception as x:
            print("publieur :", x, flush=True)
        time.sleep(3)


def fiche(rid):
    d = D(rid)
    e = lire(os.path.join(d, "etat.json"), {})
    r = lire(os.path.join(d, "retours.json"), []) or []
    e["retours"] = r
    e["cases_du_style"] = CASES
    e["images"] = lire(os.path.join(d, "images.json")) if e.get("statut") == "images" else None   # 29/10 écran « Tes images »
    if e["images"]:   # le titre du reel, montré dans le brouillon avec sa police
        t = (lire(os.path.join(d, "plan.json"), {}) or {}).get("title") or {}
        e["images"]["titre"] = re.sub(r"<[^>]+>", "", " ".join(x for x in (t.get("l1"), t.get("l2")) if x) if isinstance(t, dict) else str(t)).strip()
    if e.get("statut") == "derush" and not e.get("derush_ok"):   # 29/10 : l'écran montre le Derush Lab de ce reel
        try:
            v = lab_valide(d)
            rouge = [x["controle"] + " : " + x["detail"] for x in lire(os.path.join(d, "gardien-derush.json"), []) or [] if x.get("ok") is False]
            e["lab"] = {"port": lab(rid), "valide": v, "rouge": rouge[0] if v == "rouge" and rouge else ""}
        except Exception as x:
            e["lab"] = {"erreur": str(x)[:200]}
    e["publication"] = publier.etat(d)
    e["deja_publie"] = publier.deja_publie(rid)
    ty = (lire(os.path.join(d, "plan.json"), {}) or {}).get("typo") or {}
    if ty.get("t1", {}).get("size") and ty.get("t2", {}).get("size"):  # tailles propres à CE reel (un retour les a changées)
        e["tailles_reel"] = f'{ty["t2"]["size"]} · {ty["t1"]["size"]} px'
    return e


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def envoyer(self, code, corps, ctype="application/json; charset=utf-8", extra=None):
        if isinstance(corps, (dict, list)): corps = json.dumps(corps, ensure_ascii=False).encode()
        elif isinstance(corps, str): corps = corps.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(corps)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items(): self.send_header(k, v)
        self.end_headers()
        self.wfile.write(corps)

    def fichier(self, p):
        """Avec Range : la vidéo se déplace image par image dans le lecteur."""
        if not os.path.isfile(p): return self.envoyer(404, {"erreur": "introuvable"})
        taille = os.path.getsize(p)
        ctype = mimetypes.guess_type(p)[0] or "application/octet-stream"
        rg = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
        a, b = 0, taille - 1
        if rg:
            a = int(rg.group(1) or 0)
            b = min(int(rg.group(2)) if rg.group(2) else taille - 1, taille - 1)
        self.send_response(206 if rg else 200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(b - a + 1))
        self.send_header("Cache-Control", "no-store")
        if rg: self.send_header("Content-Range", f"bytes {a}-{b}/{taille}")
        self.end_headers()
        with open(p, "rb") as f:
            f.seek(a)
            reste = b - a + 1
            try:
                while reste > 0:
                    bloc = f.read(min(1 << 20, reste))
                    if not bloc: break
                    self.wfile.write(bloc)
                    reste -= len(bloc)
            except (BrokenPipeError, ConnectionResetError):
                pass

    def corps(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    # ------------------------------------------------------------------------------------------------------- GET
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        p = urllib.parse.unquote(u.path)  # 12/11 : dossiers avec accent (hookcorvée) arrivent en %C3%A9 -> décodés une fois ici pour toutes les routes
        try:
            if p in ("/", "/index.html"): return self.fichier(os.path.join(WEB, "index.html"))
            if p.startswith("/web/"): return self.fichier(os.path.join(WEB, os.path.basename(p)))
            if p.startswith("/fonts/"): return self.fichier(os.path.join(WEB, "fonts", os.path.basename(p)))
            if p == "/api/alerte":   # 29/10 : ElevenLabs refuse (mots.py) -> bandeau rouge en haut de l'écran
                f = os.path.expanduser("~/.claude/skills/supermonteur/.alerte-elevenlabs.json")
                if os.path.exists(f): return self.envoyer(200, json.load(open(f)))
                sm = os.path.join(APP, ".sans-musique.json")  # reel monté sans musique (monter.py)
                frais = os.path.exists(sm) and time.time() - os.path.getmtime(sm) < 2 * 3600  # 2 h après le montage, puis plus rien
                return self.envoyer(200, json.load(open(sm)) if frais else {})
            if p == "/api/reels":
                importer_montages()
                L = [carte(r) for r in sorted(os.listdir(REELS), reverse=True) if os.path.isdir(os.path.join(REELS, r))]
                return self.envoyer(200, [x for x in L if x])
            m = re.fullmatch(r"/api/reel/([\w-]+)", p)
            if m: return self.envoyer(200, fiche(m.group(1)))
            if p == "/api/da": return self.envoyer(200, DA.resume())
            if p == "/api/superda":
                url = DA.superda_url()
                try:
                    urllib.request.urlopen(url + "/api/da", timeout=1.5)
                    ok = True
                except Exception:
                    ok = False
                return self.envoyer(200, {"url": url, "en_marche": ok})
            if p == "/api/metricool": return self.envoyer(200, metricool())
            m = re.fullmatch(r"/media/([\w-]+)/(.+)", p)
            if m:
                d = D(m.group(1))
                f = os.path.normpath(os.path.join(d, m.group(2)))
                if not f.startswith(d + os.sep): return self.envoyer(403, {"erreur": "non"})
                return self.fichier(f)
            m = re.fullmatch(r"/api/telecharger/([\w-]+)", p)
            if m: return self.telecharger(m.group(1))
            return self.envoyer(404, {"erreur": "introuvable"})
        except KeyError:
            return self.envoyer(404, {"erreur": "reel introuvable"})

    def telecharger(self, rid):
        """Mode Télécharger : la vidéo + ses 5 légendes (une par réseau), dans un zip."""
        d = D(rid)
        e = lire(os.path.join(d, "etat.json"), {})
        v = os.path.join(d, e["versions"][-1]["fichier"])
        L = legendes(d)
        txt = "\n\n".join(f"{r}\n{L.get(r, '')}" for r in RESEAUX)
        if L.get("_brouillon"): txt = "Brouillon tiré du titre : demande à Claude d'écrire les vraies légendes.\n\n" + txt
        nom = f"{e.get('nom', rid)}-v{e.get('version')}"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
            z.write(v, f"{nom}.mp4")
            z.writestr("legendes.txt", txt)
        self.envoyer(200, buf.getvalue(), "application/zip", {"Content-Disposition": f'attachment; filename="{nom}.zip"'})

    # ------------------------------------------------------------------------------------------------------ POST
    def do_POST(self):
        p = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
        o = self.headers.get("Origin")  # serrure : seule la page SuperMonteur peut envoyer des ordres, pas un autre site
        if o and o not in (f"http://localhost:{PORT}", f"http://127.0.0.1:{PORT}"):
            return self.envoyer(403, {"erreur": "refusé"})
        try:
            if p == "/api/upload": return self.upload()
            m = re.fullmatch(r"/api/ref-fichier/([\w-]+)", p)
            if m: return self.ref_fichier(m.group(1))
            m = re.fullmatch(r"/api/image-fichier/([\w-]+)/(\d+)", p)
            if m: return self.image_fichier(m.group(1), int(m.group(2)))
            b = self.corps()
            if p == "/api/nouveau": return self.nouveau(b.get("rush", ""))
            if p == "/api/assembler": return self.assembler(b.get("rushs") or [])
            if p == "/api/demande-da":   # « Demande à Claude » du tiroir quand SuperDA ne tourne pas : Claude la lit
                L = lire(os.path.join(APP, "demandes-da.json"), []) or []
                L.append({"date": datetime.datetime.now().isoformat(timespec="seconds"), "reel": b.get("reel"), "texte": b.get("texte", "")})
                ecrire(os.path.join(APP, "demandes-da.json"), L)
                return self.envoyer(200, {"ok": True})
            m = re.fullmatch(r"/api/(\w+)/([\w-]+)", p)
            if not m: return self.envoyer(404, {"erreur": "introuvable"})
            act, rid = m.groups()
            d = D(rid)
            e = lire(os.path.join(d, "etat.json"), {})
            if act == "reprendre":   # 11/11 : « Réessayer » relance VRAIMENT l'étape ratée (collage ou lecture), sans renvoyer les vidéos
                if e.get("statut") != "erreur" or e.get("version") or os.path.exists(os.path.join(d, "words.rush.json")):
                    return self.envoyer(409, {"erreur": "rien à reprendre"})
                if e.get("rushs") and not os.path.isfile(e.get("rush", "")):
                    etat(d, statut="regarde", etape=f"J'assemble tes {len(e['rushs'])} rushes…", erreur=None)
                    coller_puis_regarder(rid, e["rushs"], e["rush"])
                else:
                    etat(d, statut="regarde", etape="Je regarde ta vidéo…", erreur=None)
                    lancer("regarder", rid)
                return self.envoyer(200, fiche(rid))
            if act == "monter":
                if e.get("statut") in ("montage",): return self.envoyer(409, {"erreur": "déjà en cours"})
                style = b.get("style") if b.get("style") in CASES else e.get("conseil", "Dynamique")
                # 29/10 : montage à reprendre pour CE reel (lien Instagram / TikTok / YouTube, ou vidéo glissée) ; la police reste la DA
                ref, lien, fic = None, (b.get("lien") or "").strip(), os.path.basename(b.get("fichier") or "")
                if lien:
                    if not LIEN_REF.match(lien): return self.envoyer(400, {"erreur": "colle un lien Instagram, TikTok ou YouTube"})
                    ref = {"lien": lien}
                elif fic:
                    if not os.path.isfile(os.path.join(d, "ref", fic)): return self.envoyer(400, {"erreur": "vidéo à reprendre introuvable : glisse-la à nouveau"})
                    ref = {"fichier": fic}
                if style == "Inspiration" and not ref: return self.envoyer(400, {"erreur": "colle le lien ou glisse la vidéo à reprendre"})
                etat(d, statut="montage", style=style, cases=b.get("cases", {}), reference=ref, etape="Je prépare le montage…", erreur=None)
                lancer("monter", rid)
                return self.envoyer(200, fiche(rid))
            if act == "derush_ok":  # 29/10 « Monter le reel » sous le Derush Lab : monter.py attend ce feu vert
                if e.get("statut") != "derush": return self.envoyer(409, {"erreur": "le dérush est déjà validé"})
                v = lab_valide(d)
                if not v: return self.envoyer(409, {"erreur": "clique d'abord « ✓ Valider le dérush » en bas"})
                if v == "rouge" and not b.get("forcer"): return self.envoyer(409, {"erreur": "le Gardien voit un point à régler"})
                arreter_lab(rid)
                etat(d, derush_ok=True, etape="Je prends ton dérush…")
                try:   # le monter.py qui attendait est toujours là ? (Mac redémarré = non : on relance la suite)
                    os.kill(int(e.get("pid_derush") or 0), 0)
                    vivant = int(e.get("pid_derush") or 0) > 0 and "monter.py" in subprocess.run(
                        ["ps", "-o", "command=", "-p", str(e["pid_derush"])], capture_output=True, text=True).stdout
                except Exception:
                    vivant = False
                if not vivant:
                    etat(d, statut="montage")
                    lancer("suite", rid)
                return self.envoyer(200, fiche(rid))
            if act == "images":     # 29/10 « Monter avec ces images » : ses choix, puis Claude monte au style de la référence
                if e.get("statut") != "images": return self.envoyer(409, {"erreur": "les images sont déjà envoyées"})
                images.prendre(d, b.get("pris") or {})
                pousser_ref(d, texte=e.get("images_texte"))
                return self.envoyer(200, fiche(rid))
            if act == "retour":
                R = lire(os.path.join(d, "retours.json"), []) or []
                texte = (b.get("texte") or "").strip()
                if not texte: return self.envoyer(400, {"erreur": "retour vide"})
                R.append({"id": max([x["id"] for x in R] or [0]) + 1, "t": round(float(b.get("t", 0)), 2), "texte": texte,
                          "statut": "a_faire", "version": e.get("version", 1), "reponse": "",
                          "date": datetime.datetime.now().isoformat(timespec="seconds"),
                          **({"auto": "lourd"} if b.get("lourd") else {})})   # 10/11 studio : images à ajouter, style à refaire = Claude complet (Opus), pas le correcteur rapide
                ecrire(os.path.join(d, "retours.json"), R)
                return self.envoyer(200, fiche(rid))
            if act == "effacer":     # retirer un retour pas encore envoyé (faute de frappe)
                R = [x for x in lire(os.path.join(d, "retours.json"), []) if not (x["id"] == b.get("id") and x["statut"] == "a_faire")]
                ecrire(os.path.join(d, "retours.json"), R)
                return self.envoyer(200, fiche(rid))
            if act == "suivant":
                R = lire(os.path.join(d, "retours.json"), []) or []
                a_faire = [x for x in R if x["statut"] == "a_faire"]
                if not a_faire: return self.envoyer(400, {"erreur": "aucun retour à corriger"})
                dem = {"reel": rid, "dossier": d, "version": e.get("version"), "date": datetime.datetime.now().isoformat(timespec="seconds"),
                       "retours": a_faire, "a_faire": "Lire CLAUDE.md : corriger plan.json pour chaque retour, puis python3 monter.py remonter <dossier>, puis statut corrige + reponse dans retours.json"}
                ecrire(os.path.join(d, "demande.json"), dem)
                boite = lire(os.path.join(APP, "a-corriger.json"), []) or []
                boite = [x for x in boite if x.get("reel") != rid] + [dem]
                ecrire(os.path.join(APP, "a-corriger.json"), boite)
                etat(d, statut="correction", etape="Retours envoyés : Claude corrige et remonte la version suivante.")
                return self.envoyer(200, fiche(rid))
            if act == "valider":
                etat(d, statut="valide", valide_le=datetime.datetime.now().isoformat(timespec="seconds"))
                return self.envoyer(200, fiche(rid))
            if act == "rouvrir":
                etat(d, statut="retours")
                return self.envoyer(200, fiche(rid))
            if act == "cacher":      # 29/10 « Supprimer » de l'accueil (2 clics) : le projet disparaît, ses fichiers et le rush restent
                etat(d, cache=datetime.datetime.now().isoformat(timespec="seconds"))
                return self.envoyer(200, {"ok": True})
            if act == "publier":
                if reglages_apps.mode_essai(APP):
                    return self.envoyer(400, {"ok": False, "message": "Mode essai : rien n'est publié. Pour publier pour de vrai : "
                                                                      "supermonteur/config.json, \"mode_essai\": false."})
                # 28/10 : vraie publication. Le clic confirmé = le OK de l’utilisateur pour CE reel ; Claude envoie (apps/publier.py).
                reseaux, quand = [r for r in (b.get("reseaux") or []) if r in RESEAUX], b.get("quand") or ""
                if not reseaux:
                    return self.envoyer(400, {"ok": False, "message": "Choisis au moins un réseau."})
                ok, msg = publier.demander(d, "reel", reseaux, quand, titre_reel(d) or e.get("nom", rid), cles_registre=(rid,),
                                           forcer=bool(b.get("forcer")))
                if msg.startswith("DEJA:"): return self.envoyer(409, {"deja": msg[5:]})
                if not ok: return self.envoyer(400, {"ok": False, "message": msg})
                return self.envoyer(200, {"ok": True, "message": msg, "publication": publier.etat(d)})
            return self.envoyer(404, {"erreur": "action inconnue"})
        except KeyError:
            return self.envoyer(404, {"erreur": "reel introuvable"})

    def nouveau(self, rush, rushs=None):
        rush = os.path.expanduser(rush.strip().strip("'\""))
        if not rushs and not os.path.isfile(rush): return self.envoyer(400, {"erreur": f"vidéo introuvable : {rush}"})
        base = re.sub(r"[^\w-]", "", os.path.splitext(os.path.basename(rush))[0]).lower() or "reel"
        rid = f"{datetime.date.today():%Y-%m-%d}-{base}"
        k = 2
        while True:   # 29/10 : deux imports dans la même seconde plantaient (FileExistsError)
            try: os.makedirs(os.path.join(REELS, rid)); break
            except FileExistsError:
                rid = f"{datetime.date.today():%Y-%m-%d}-{base}-{k}"
                k += 1
        d = os.path.join(REELS, rid)
        ecrire(os.path.join(d, "etat.json"), {"id": rid, "nom": os.path.splitext(os.path.basename(rush))[0], "rush": rush,
                                              "cree": datetime.datetime.now().isoformat(timespec="seconds"), "statut": "regarde",
                                              "etape": f"J'assemble tes {len(rushs)} rushes…" if rushs else "Je regarde ta vidéo…",
                                              "version": 0, "versions": [], **({"rushs": rushs} if rushs else {})})
        ecrire(os.path.join(d, "retours.json"), [])
        if rushs:   # 11/11 : plusieurs rushes = 1 seule vidéo, collés bout à bout puis regardés
            coller_puis_regarder(rid, rushs, rush)
        else:
            lancer("regarder", rid)
        return self.envoyer(200, fiche(rid))

    def assembler(self, rushs):
        """11/11 (l’utilisateur : « j'avais deux rushes ») : plusieurs vidéos = UNE vidéo, dans l'ordre reçu."""
        rushs = [os.path.expanduser(str(r).strip()) for r in rushs if str(r).strip()]
        manque = [r for r in rushs if not os.path.isfile(r)]
        if not rushs or manque: return self.envoyer(400, {"erreur": f"vidéo introuvable : {(manque or ['aucune'])[0]}"})
        if len(rushs) == 1: return self.nouveau(rushs[0])
        base = re.sub(r"[^\w-]", "", os.path.splitext(os.path.basename(rushs[0]))[0]) or "rush"
        out, k = os.path.join(REELS, "_rushs", f"{base}-plus-{len(rushs) - 1}.mp4"), 2
        while os.path.exists(out):
            out, k = os.path.join(REELS, "_rushs", f"{base}-plus-{len(rushs) - 1}-{k}.mp4"), k + 1
        return self.nouveau(out, rushs)

    def upload(self):
        """Vidéo glissée sur la page : copiée dans reels/_rushs/ (pas de copie si elle vient déjà du Mac par son chemin)."""
        nom = os.path.basename(urllib.parse.unquote(self.headers.get("X-Nom", "rush.mp4")))
        dst = os.path.join(REELS, "_rushs")
        os.makedirs(dst, exist_ok=True)
        p = os.path.join(dst, re.sub(r"[^\w.-]", "_", nom))
        n = int(self.headers.get("Content-Length") or 0)
        # 29/10 (RUSH : copie arrêtée à 5,8 / 6,4 Go, vidéo illisible) : copie dans .part, gardée seulement si complète
        part = p + ".part"
        with open(part, "wb") as f:
            while n > 0:
                bloc = self.rfile.read(min(1 << 20, n))
                if not bloc: break
                f.write(bloc)
                n -= len(bloc)
        if n > 0:
            os.remove(part)   # copie partielle faite par ce serveur, jamais la vidéo d'origine
            return self.envoyer(400, {"erreur": "import coupé en route : colle plutôt le chemin de la vidéo"})
        os.replace(part, p)
        if self.headers.get("X-Seul"): return self.envoyer(200, {"chemin": p})   # 11/11 : un rush d'un lot, assemblé ensuite
        return self.nouveau(p)

    def image_fichier(self, rid, n):
        """29/10 : sa vidéo glissée sur un plan de l'écran « Tes images » (il l'a filmée pour ce plan) : copiée dans
        reels/<id>/images/, ajoutée aux choix du plan et choisie."""
        dst = os.path.join(D(rid), "images")
        os.makedirs(dst, exist_ok=True)
        nom = re.sub(r"[^\w.-]", "_", os.path.basename(urllib.parse.unquote(self.headers.get("X-Nom", "video.mp4"))))
        p = os.path.join(dst, f"perso-{n}-{nom}")
        reste = int(self.headers.get("Content-Length") or 0)
        with open(p + ".part", "wb") as f:
            while reste > 0:
                bloc = self.rfile.read(min(1 << 20, reste))
                if not bloc: break
                f.write(bloc)
                reste -= len(bloc)
        if reste > 0:
            os.remove(p + ".part")
            return self.envoyer(400, {"erreur": "import coupé en route : glisse-la à nouveau"})
        os.replace(p + ".part", p)
        try:
            images.perso(D(rid), n, p)
        except Exception as x:
            return self.envoyer(400, {"erreur": f"vidéo illisible : {str(x)[:120]}"})
        return self.envoyer(200, fiche(rid))

    def ref_fichier(self, rid):
        """Vidéo à reprendre glissée sur l'écran 0 : copiée dans reels/<id>/ref/ (lue par monter.py après la v1)."""
        dst = os.path.join(D(rid), "ref")
        os.makedirs(dst, exist_ok=True)
        nom = re.sub(r"[^\w.-]", "_", os.path.basename(urllib.parse.unquote(self.headers.get("X-Nom", "reference.mp4"))))
        n = int(self.headers.get("Content-Length") or 0)
        with open(os.path.join(dst, nom), "wb") as f:
            while n > 0:
                bloc = self.rfile.read(min(1 << 20, n))
                if not bloc: break
                f.write(bloc)
                n -= len(bloc)
        return self.envoyer(200, {"fichier": nom})


if __name__ == "__main__":
    print(f"SuperMonteur : http://localhost:{PORT}")
    threading.Thread(target=ouvrier, daemon=True).start()
    threading.Thread(target=publieur, daemon=True).start()
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
