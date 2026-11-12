"""Repère les images isolées incohérentes d'une sortie Beeble une image (ou 2-3 d'affilée) qui ne ressemble ni à
la précédente ni à la suivante alors que ces deux-là se ressemblent, dans un même plan (jamais sur une coupe).
Docteur : aussi une blouse qui disparaît (part de blanc sur le torse qui s'effondre par rapport au plan).
  python3 images_folles.py video.mp4 plans.json -> liste + images de contrôle dans controle/folles/
  python3 images_folles.py video.mp4 plans.json --repare sortie.mp4 -> chaque image folle remplacée par sa voisine propre (son intact)
"""
import json, os, subprocess, sys
import numpy as np

src, plans_p = sys.argv[1], sys.argv[2]
W, H, w, h, FPS = 1080, 1920, 108, 192, 30
plans = json.load(open(plans_p))
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vf', f'scale={w}:{h}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
V = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(np.float32)
N = len(V)
role = np.array([next((p['role'] for p in plans if p['de'] <= i / FPS < p['a']), plans[-1]['role']) for i in range(N)])
plan_i = np.array([next((k for k, p in enumerate(plans) if p['de'] <= i / FPS < p['a']), len(plans) - 1) for i in range(N)])
G = V.mean(3)
d = lambda a, b: float(np.abs(G[a] - G[b]).mean())
# blanc de la blouse sur le torse (docteur) : pixels clairs et peu saturés
T = V[:, int(h * 0.58):int(h * 0.80), int(w * 0.25):int(w * 0.85)]
mx, mn = T.max(3), T.min(3)
blanc = ((mx > 185) & (mx - mn < 40)).mean((1, 2))
folles = set()
for k in range(len(plans)):
    idx = np.where(plan_i == k)[0]
    if len(idx) < 6: continue
    a, b = idx[0] + 1, idx[-1] - 1                       # jamais la 1re / dernière image d'un plan (coupe)
    pas = np.array([d(i, i - 1) for i in range(a, b + 1)])
    base = max(np.median(pas), 0.8)
    for i in range(a, b + 1):
        for L in (1, 2, 3):                                # 1 à 3 images folles d'affilée
            j = i + L
            if j > b + 1: break
            if d(i, i - 1) > 4 * base and d(j - 1, j) > 4 * base and d(i - 1, j) < 2 * base:
                folles.update(range(i, j)); break
    # Beeble rate souvent la 1re (ou les 2-3 premières / dernières) image d'un plan : elle saute par rapport à la suite
    for bout in (list(idx[:6]), list(idx[::-1][:6])):
        for L in (1, 2, 3):
            if d(bout[L - 1], bout[L]) > 4 * base and d(bout[L], bout[L + 1]) < 2.5 * base:
                folles.update(int(x) for x in bout[:L]); break
    # couleur du torse très différente du reste du plan (blouse blanche -> pull gris : saut trop faible pour le test au-dessus)
    C = T[idx].mean((1, 2)); med_c = np.median(C, 0); dist = np.sqrt(((C - med_c) ** 2).sum(1))
    seuil = max(22.0, 5 * np.median(dist))
    for n, i in enumerate(idx):                      # seulement les bords du plan (là où Beeble se trompe) : une main devant le torse au milieu = normal
        if dist[n] > seuil and (n < 3 or n >= len(idx) - 3): folles.add(int(i))
    if role[idx[0]] == 'DOC':
        med = np.median(blanc[idx])
        for i in idx[1:-1]:
            if blanc[i] < 0.5 * med and med > 0.08: folles.add(int(i))
folles = sorted(folles)
print(f'{N} images, {len(folles)} images folles :', [f'{i} ({i / FPS:.2f} s)' for i in folles])
os.makedirs('controle/folles', exist_ok=True)
for i in folles:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', f'select=between(n\\,{i - 1}\\,{i + 1}),scale=270:480,tile=3x1',
                    '-frames:v', '1', f'controle/folles/{i:05d}.jpg'], check=True)
json.dump(folles, open(os.path.splitext(src)[0] + '.folles.json', 'w'))
if '--repare' in sys.argv:
    out = sys.argv[sys.argv.index('--repare') + 1]
    fs = set(folles)
    def propre(i):
        for k in range(1, 6):
            if i - k >= 0 and i - k not in fs and plan_i[i - k] == plan_i[i]: return i - k
            if i + k < N and i + k not in fs and plan_i[i + k] == plan_i[i]: return i + k
        return i
    # fenêtre glissante simple (la 1re version perdait 58 images sur 2191 -> son décalé)
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', src, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', '-c:a', 'copy', out],
                           stdin=subprocess.PIPE)
    buf, lus, ecrites = {}, 0, 0
    def lit_jusqua(k):
        global lus
        while lus <= k:
            fr = dec.stdout.read(W * H * 3)
            if len(fr) < W * H * 3: break
            buf[lus] = fr; lus += 1
    for o in range(N):
        lit_jusqua(o + 6)
        src_i = propre(o) if o in fs else o
        enc.stdin.write(buf.get(src_i, buf[o])); ecrites += 1
        for k in [k for k in buf if k < o - 6]: del buf[k]
    print('images écrites', ecrites, '/', N)
    enc.stdin.close(); enc.wait(); print('->', out)
