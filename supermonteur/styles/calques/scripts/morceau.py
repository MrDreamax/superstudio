"""Retoucher seulement la FIN (ou toute partie après un cut) d'un reel Calques, sans tout re-rendre (RUSH :
l’utilisateur « pourquoi aussi long pour modifier la fin ? » : changer 1 s à la fin = 25 min avant, ~3 min avec ce script).
  python3 morceau.py plan.json DEPUIS ANCIEN_FINAL.mp4 ANCIEN_MASQUE.mp4
DEPUIS = seconde d'un CUT (début d'une prise) ; tout ce qui est avant est repris tel quel de l'ancien final et de l'ancien
masque. Le clip et plan.json sont déjà à jour (nouvelle fin). Sortie = plan["sortie"]."""
import json, os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__))
plan_p, T, ancien, m_ancien = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
d = os.path.dirname(os.path.abspath(plan_p)); plan = json.load(open(plan_p))
j = lambda f: os.path.join(d, f)
N = round(T * 30)
run = lambda *a: subprocess.run(list(a), check=True)
# 1. masque : début repris, fin détourée
run("python3", os.path.join(D, "detoure.py"), j(plan["clip"]), str(T), str(plan["t1"]), j("_m_fin.mp4"))
run("ffmpeg", "-v", "error", "-y", "-i", m_ancien, "-i", j("_m_fin.mp4"), "-filter_complex",
    f"[0:v]trim=end_frame={N},setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1[v]",
    "-map", "[v]", "-c:v", "libx264", "-crf", "10", "-pix_fmt", "yuv420p", j(plan["masque"]))
# 2. rendu de la fin seule (musique continue : départ décalé, sans fondu d'entrée)
p2 = dict(plan, t0=T, sortie="_fin.mp4", fondu_musique=0, scenes=[s for s in plan["scenes"] if s["a"] > T])   # sinon les bruitages d'avant tombent tous au début
if p2.get("musique"): p2["musique"] = dict(p2["musique"], depuis=p2["musique"].get("depuis", 0) + T)
json.dump(p2, open(j("_plan_fin.json"), "w"), ensure_ascii=False)
run("python3", os.path.join(D, "calques.py"), j("_plan_fin.json"))
# 3. recollage image à image + son
run("ffmpeg", "-v", "error", "-y", "-i", ancien, "-i", j("_fin.mp4"), "-filter_complex",
    f"[0:v]trim=end_frame={N},setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1[v];"
    f"[0:a]atrim=0:{N / 30:.4f},asetpts=PTS-STARTPTS[x];[1:a]asetpts=PTS-STARTPTS[y];[x][y]concat=n=2:v=0:a=1[s]",
    "-map", "[v]", "-map", "[s]", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
    j(plan.get("sortie", "final.mp4")))
for f in ("_m_fin.mp4", "_fin.mp4", "_plan_fin.json"): os.remove(j(f))
print("fin retouchée :", j(plan.get("sortie", "final.mp4")))
