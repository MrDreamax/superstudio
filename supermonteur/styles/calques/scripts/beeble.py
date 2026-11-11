"""Beeble SwitchX (09/11/2026, l’utilisateur : « je veux le meilleur rendu possible, s'il faut payer Beeble je paye. Ne garde pas
mon décor de base. ») : change la pièce de chaque plan et ré-éclaire la personne pour qu'elle colle.
API : https://developer.beeble.ai/docs (720p par défaut depuis le 09/11 = 0,10 $ / s ; "resolution": 1080 dans le json = 0,30 $ / s ; 8 s = 240 images max par vidéo, 2,77 Mpx max).
Clé lue dans le trousseau (service beeble-api-key), jamais dans un fichier.

  python3 beeble.py plans.json
plans.json = {"clip": "clip.mp4", "masque": "masque.mp4", "sortie": "clip_beeble.mp4", "seed": 7,
              "plans": [{"de": 0, "a": 2.7, "piece": "A", "image": 1.2}, ...],
              "pieces": {"A": "prompt anglais de la pièce", ...}}
Pour chaque pièce : 1 image de référence (image du plan + prompt -> même cadrage, nouvelle pièce), réutilisée par tous les
plans de cette pièce (même pièce d'un plan à l'autre, même graine). Puis chaque plan en vidéo (masque = notre détourage, mode
custom), recollés avec le SON D'ORIGINE (rush intouchable). Tout est mis en cache dans beeble/ : relancer ne repaie rien.
"""
import json, os, subprocess, sys, time
import requests

API = "https://api.beeble.ai/v1"


def cle():
    k = subprocess.run(["security", "find-generic-password", "-s", "beeble-api-key", "-w"], capture_output=True, text=True).stdout.strip()
    if not k: sys.exit("Pas de clé Beeble dans le trousseau (service beeble-api-key).")
    return k


def post(url, **kw):
    """Beeble : 10 demandes par minute. Un 429 = on attend et on recommence (jusqu'à 2 min)."""
    for _ in range(9):
        r = requests.post(url, **kw)
        if r.status_code != 429: return r
        print("  Beeble : trop de demandes, j'attends 15 s", flush=True); time.sleep(15)
    return r


def envoie(key, chemin, mime):
    r = post(f"{API}/uploads", headers={"x-api-key": key}, json={"filename": os.path.basename(chemin)}, timeout=60)
    r.raise_for_status()
    j = r.json()
    url = j.get("upload_url") or j.get("url")
    with open(chemin, "rb") as f:
        requests.put(url, data=f, headers={"Content-Type": mime}, timeout=600).raise_for_status()
    return j.get("beeble_uri") or j.get("uri")


def soumet(key, corps, cache):
    """Envoie le travail sans attendre (le .json garde l'id : relancer ne repaie pas)."""
    if os.path.exists(cache + ".json"): return
    r = post(f"{API}/switchx/generations", headers={"x-api-key": key}, json=corps, timeout=120)
    if r.status_code >= 400: sys.exit(f"Beeble refuse : {r.status_code} {r.text[:300]}")
    json.dump(r.json(), open(cache + ".json", "w"))


def genere(key, corps, cache):
    if os.path.exists(cache + ".json"):
        job = json.load(open(cache + ".json"))
    else:
        r = requests.post(f"{API}/switchx/generations", headers={"x-api-key": key}, json=corps, timeout=120)
        if r.status_code >= 400: sys.exit(f"Beeble refuse : {r.status_code} {r.text[:300]}")
        job = r.json(); json.dump(job, open(cache + ".json", "w"))
    while True:
        j = requests.get(f"{API}/switchx/generations/{job['id']}", headers={"x-api-key": key}, timeout=60).json()
        if j["status"] == "completed": break
        if j["status"] == "failed": sys.exit(f"Beeble échec ({os.path.basename(cache)}) : {j.get('error')}")
        print(f"  {os.path.basename(cache)} : {j['status']} {j.get('progress') or 0} %", flush=True)
        time.sleep(6)
    url = j["output"]["render"]
    ext = ".png" if corps["generation_type"] == "image" else ".mp4"
    with open(cache + ext, "wb") as f: f.write(requests.get(url, timeout=600).content)
    print(f"  {os.path.basename(cache)} : fini ({j.get('credits_charged')} crédits facturés)")
    return cache + ext


def main():
    p = json.load(open(sys.argv[1]))
    d = os.path.dirname(os.path.abspath(sys.argv[1]))
    B = os.path.join(d, "beeble"); os.makedirs(B, exist_ok=True)
    clip, masque = os.path.join(d, p["clip"]), os.path.join(d, p["masque"])
    key = cle()
    seed = p.get("seed", 7)
    refs, jobs = {}, []
    for i, pl in enumerate(p["plans"]):
        nom = f"plan{i + 1:02d}"
        src, alpha = os.path.join(B, nom + "_src.mp4"), os.path.join(B, nom + "_alpha.mp4")
        dur = pl["a"] - pl["de"]
        if not os.path.exists(src):
            # 09/11 : découpe à l'IMAGE près (Beeble refuse un masque qui a 1 image de moins que la vidéo)
            fa, nf = round(pl["de"] * 30), round(dur * 30)
            tr = f"trim=start_frame={fa}:end_frame={fa + nf},setpts=PTS-STARTPTS"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", clip, "-vf", tr, "-an",
                            "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", src], check=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", masque, "-vf", tr + ",scale=1080:1920:flags=bicubic,format=gray",
                            "-c:v", "libx264", "-crf", "8", "-pix_fmt", "yuv420p", alpha], check=True)
        pc = pl["piece"]
        if pc not in refs:   # image de référence de la pièce, faite sur une image de ce plan
            img = os.path.join(B, f"piece_{pc}_src.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{pl['de'] + pl.get('image', dur / 2):.3f}", "-i", clip,
                            "-frames:v", "1", img], check=True)
            ia = os.path.join(B, f"piece_{pc}_alpha.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{pl['de'] + pl.get('image', dur / 2):.3f}", "-i", masque,
                            "-frames:v", "1", "-vf", "scale=1080:1920,format=gray", ia], check=True)
            cache = os.path.join(B, f"piece_{pc}")
            refs[pc] = cache
            if not os.path.exists(cache + ".png"):
                print(f"pièce {pc} : image de référence envoyée")
                soumet(key, {"generation_type": "image", "source_uri": envoie(key, img, "image/png"),
                             "alpha_mode": "custom", "alpha_uri": envoie(key, ia, "image/png"),
                             "prompt": p["pieces"][pc], "max_resolution": p.get("resolution", 720), "seed": seed}, cache)
        jobs.append((nom, pc, src, alpha))
    for pc, cache in refs.items():
        if not os.path.exists(cache + ".png"): genere(key, {"generation_type": "image"}, cache)
    for nom, pc, src, alpha in jobs:   # 09/11 : toutes les vidéos en même temps (Beeble : 5 travaux à la fois)
        out = os.path.join(B, nom)
        if not os.path.exists(out + ".mp4"):
            print(f"{nom} (pièce {pc}) envoyé")
            soumet(key, {"generation_type": "video", "source_uri": envoie(key, src, "video/mp4"),
                         "alpha_mode": "custom", "alpha_uri": envoie(key, alpha, "video/mp4"),
                         "reference_image_uri": envoie(key, refs[pc] + ".png", "image/png"),
                         "prompt": p["pieces"][pc], "max_resolution": p.get("resolution", 720), "seed": seed,
                         "idempotency_key": f"{os.path.basename(d)}-{nom}-{seed}-{abs(hash(p['pieces'][pc])) % 10**8}"}, out)
    for nom, pc, src, alpha in jobs:
        out = os.path.join(B, nom)
        if not os.path.exists(out + ".mp4"): genere(key, {"generation_type": "video"}, out)
    # recollage : chaque plan remis à 1080x1920, 30 i/s, durée exacte ; son d'origine du clip
    lst = os.path.join(B, "liste.txt")
    with open(lst, "w") as f:
        for i, pl in enumerate(p["plans"]):
            n = os.path.join(B, f"plan{i + 1:02d}")
            norm = n + "_1080.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", n + ".mp4", "-vf", f"scale=1080:1920:flags=lanczos,fps=30,trim=end_frame={round((pl['a'] - pl['de']) * 30)}",
                            "-an", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", norm], check=True)
            f.write(f"file '{norm}'\n")
    sortie = os.path.join(d, p.get("sortie", "clip_beeble.mp4"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", clip, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k", "-t", f"{sum(pl['a'] - pl['de'] for pl in p['plans']):.3f}", sortie], check=True)   # -shortest + copie du son coupait la vidéo à 21 images
    print("clip avec nouveaux décors :", sortie)


if __name__ == "__main__":
    main()
