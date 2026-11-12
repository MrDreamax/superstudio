"""Style Calques : détoure TOUT l'extrait une fois (Robust Video Matting, même modèle que matte.py) et l'écrit en
vidéo grise 540x960 (blanc = toi). Le rendu relit ce masque à chaque essai au lieu de recalculer.
  python3 detoure.py clip.mp4 DEBUT FIN masque.mp4
"""
import os, subprocess, sys
import numpy as np
import onnxruntime as ort

src, t0, t1, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
W, H = 1080, 1920
sess = ort.InferenceSession(os.path.expanduser("~/.cache/supermonteur/rvm_mobilenetv3_fp32.onnx"), providers=["CPUExecutionProvider"])
a0 = max(0.0, t0 - 0.5)   # 0,5 s pour chauffer le modèle (contour stable), images non écrites
fps = 30
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{a0:.3f}", "-i", src, "-t", f"{t1 - a0:.3f}", "-vf", f"fps={fps}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", "540x960", "-r", str(fps),
                        "-i", "-", "-c:v", "libx264", "-crf", "10", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
ratio = np.array([0.25], np.float32)
i = n = 0
import cv2
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    x = (np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32) / 255).transpose(2, 0, 1)[None]
    _, pha, *rec = sess.run(None, {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": ratio})
    if a0 + i / fps >= t0 - 1e-3:
        a = (np.clip(pha[0, 0], 0, 1) * 255).astype(np.uint8)
        enc.stdin.write(cv2.resize(a, (540, 960), interpolation=cv2.INTER_AREA).tobytes()); n += 1
        if n % 150 == 0: print(f"{n} images", flush=True)
    i += 1
enc.stdin.close(); enc.wait(); dec.wait()
print(f"masque : {n} images -> {out}")
