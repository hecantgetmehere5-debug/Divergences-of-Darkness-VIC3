"""Link every Vic3 land province to the Vic2 (DoD) province that covers the same ground.

The two maps use different projections, so the link is fitted from matching place
names: Vic3 hub names (city/port/farm/mine/wood) against Vic2 province names. A
polynomial fit with outlier rejection gives the global shape, then a local
correction from the nearest matched pairs fixes regional drift.

Usage: py tools/vic3_map_link.py <vic3_game_dir> <vic2_mod_dir> <out_csv>
Output columns: vic3_province,state,vic2_province,dist  (dist = 0 when the mapped
point fell inside a Vic2 land province, else the pixel distance searched)
"""
import csv, re, sys, unicodedata
from pathlib import Path
import numpy as np
from PIL import Image

V3, V2, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
Image.MAX_IMAGE_PIXELS = None


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", s)


# ---------- Vic3: states, provinces, hubs ----------
states, hubs = {}, {}
for f in sorted((V3 / "map_data/state_regions").glob("*.txt")):
    if f.name.startswith("99_"):
        continue
    text = f.read_text(encoding="utf-8-sig")
    for m in re.finditer(r"^(STATE_\w+)\s*=\s*\{(.*?)^\}", text, re.S | re.M):
        name, body = m.group(1), m.group(2)
        pm = re.search(r"provinces\s*=\s*\{([^}]*)\}", body)
        states[name] = ["x" + p.strip('"')[1:].upper() for p in pm.group(1).split()]
        for kind in ("city", "port", "farm", "mine", "wood"):
            hm = re.search(rf"\b{kind}\s*=\s*\"?(x[0-9A-Fa-f]{{6}})", body)
            if hm:
                hubs[(name, kind)] = "x" + hm.group(1)[1:].upper()
prov_state = {p: s for s, ps in states.items() for p in ps}

hubname = {}
for f in (V3 / "localization/english").rglob("*.yml"):
    for line in f.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        m = re.match(r'\s*HUB_NAME_(STATE_\w+)_(city|port|farm|mine|wood):\d*\s*"([^"]+)"', line)
        if m:
            hubname[(m.group(1), m.group(2))] = m.group(3)

img3 = np.asarray(Image.open(V3 / "map_data/provinces.png").convert("RGB"))
H3, W3 = img3.shape[:2]
code3 = (img3[..., 0].astype(np.uint32) << 16) | (img3[..., 1].astype(np.uint32) << 8) | img3[..., 2]
flat = code3.ravel()
uniq, inv = np.unique(flat, return_inverse=True)
ys, xs = np.divmod(np.arange(flat.size), W3)
cnt = np.bincount(inv)
cx3 = np.bincount(inv, xs) / cnt
cy3 = np.bincount(inv, ys) / cnt
hex3 = ["x%06X" % c for c in uniq]
idx3 = {h: i for i, h in enumerate(hex3)}
del ys, xs

# ---------- Vic2 ----------
land2 = {}
with open(Path(__file__).resolve().parent.parent / "start_data/provinces.csv", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        land2[int(r["province"])] = r["name"]
color2id = {}
for line in (V2 / "map/definition.csv").read_text(encoding="latin-1").splitlines()[1:]:
    p = line.split(";")
    try:
        r, g, b = (int(re.sub(r"\D", "", v)) for v in p[1:4])
        color2id[(r << 16) | (g << 8) | b] = int(p[0])
    except (ValueError, IndexError):
        continue
img2 = np.asarray(Image.open(V2 / "map/provinces.bmp").convert("RGB"))
H2, W2 = img2.shape[:2]
code2 = (img2[..., 0].astype(np.uint32) << 16) | (img2[..., 1].astype(np.uint32) << 8) | img2[..., 2]
lut = {c: i for c, i in color2id.items()}
u2, inv2 = np.unique(code2.ravel(), return_inverse=True)
pid2 = np.array([lut.get(int(c), 0) for c in u2], dtype=np.int32)[inv2].reshape(H2, W2)
landmask = np.isin(pid2, np.array(list(land2)))
yy, xx = np.nonzero(landmask)
pp = pid2[yy, xx]
c2n = np.bincount(pp, minlength=4000)
c2x = np.bincount(pp, xx, minlength=4000) / np.maximum(c2n, 1)
c2y = np.bincount(pp, yy, minlength=4000) / np.maximum(c2n, 1)

# ---------- control points ----------
by_name2 = {}
for pid, nm in land2.items():
    by_name2.setdefault(norm(nm), []).append(pid)
pairs = []
for key, nm in hubname.items():
    h = hubs.get(key)
    k = norm(nm)
    if not h or h not in idx3 or len(k) < 4 or len(by_name2.get(k, [])) != 1:
        continue
    pid = by_name2[k][0]
    i = idx3[h]
    pairs.append((cx3[i], cy3[i], c2x[pid], c2y[pid]))
P = np.array(pairs)
print("name matches:", len(P))


def feats(x, y):
    x, y = x / W3, y / H3
    cols = [np.ones_like(x)]
    for d in range(1, 6):
        for a in range(d + 1):
            cols.append(x ** (d - a) * y ** a)
    return np.stack(cols, -1)


keep = np.ones(len(P), bool)
for it in range(8):
    A = feats(P[keep, 0], P[keep, 1])
    cx = np.linalg.lstsq(A, P[keep, 2], rcond=None)[0]
    cy = np.linalg.lstsq(A, P[keep, 3], rcond=None)[0]
    Af = feats(P[:, 0], P[:, 1])
    err = np.hypot(Af @ cx - P[:, 2], Af @ cy - P[:, 3])
    thr = max(15.0, 3 * np.median(err[keep]))
    keep = err < thr
print("inliers:", keep.sum(), "median err px:", round(float(np.median(err[keep])), 1))
Pi = P[keep]
res = np.stack([Pi[:, 2] - feats(Pi[:, 0], Pi[:, 1]) @ cx, Pi[:, 3] - feats(Pi[:, 0], Pi[:, 1]) @ cy], 1)


def to_v2(x, y):
    A = feats(x, y)
    gx, gy = A @ cx, A @ cy
    d = np.hypot(Pi[None, :, 0] - x[:, None], Pi[None, :, 1] - y[:, None])
    k = np.argsort(d, 1)[:, :6]
    dk = np.take_along_axis(d, k, 1)
    w = 1 / (dk + 20) ** 2
    w /= w.sum(1, keepdims=True)
    gx += (w * res[k, 0]).sum(1)
    gy += (w * res[k, 1]).sum(1)
    return gx, gy


# ---------- link every Vic3 land province ----------
land3 = [h for h in prov_state if h in idx3]
ii = np.array([idx3[h] for h in land3])
out = []
for s in range(0, len(ii), 2000):
    b = ii[s:s + 2000]
    gx, gy = to_v2(cx3[b], cy3[b])
    for j, (x, y) in enumerate(zip(gx, gy)):
        x, y = int(round(x)) % W2, int(np.clip(round(y), 0, H2 - 1))
        best, dist = 0, 0
        if landmask[y, x]:
            best = int(pid2[y, x])
        else:
            for r in range(2, 80, 2):
                y0, y1, x0, x1 = max(0, y - r), min(H2, y + r + 1), max(0, x - r), min(W2, x + r + 1)
                win = landmask[y0:y1, x0:x1]
                if win.any():
                    wy, wx = np.nonzero(win)
                    q = np.argmin((wy + y0 - y) ** 2 + (wx + x0 - x) ** 2)
                    best, dist = int(pid2[wy[q] + y0, wx[q] + x0]), r
                    break
        out.append((land3[s + j], prov_state[land3[s + j]], best, dist))

with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["vic3_province", "state", "vic2_province", "dist"])
    w.writerows(out)
print("linked:", sum(1 for o in out if o[2]), "/", len(out), "unlinked:", sum(1 for o in out if not o[2]))
