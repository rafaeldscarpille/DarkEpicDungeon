"""Constrói a spritesheet do Capitão Scarpa (classe PIRATE) no formato "pack" do jogo.

Entrada : scripts/source/capitao-scarpa-folha.png  (folha com fundo marrom esfumaçado)
Saída   : assets/sprites/characters/pirate/pirate_{idle,walk,run,attack,death,extra}.png
          (uma tira horizontal por animação, células 128x128, fundo transparente)
          + pirate_config.json (quadros, fps, origem de cada quadro)
          assets/pixel-art/characters/pirate-hd3*.png + pirate-hd3.json
          (folha "pack" que o jogo carrega = as tiras acima em sequência + mapa)

Fidelidade à arte enviada:
- o personagem fica com ~98 px de altura no quadro e o jogo o desenha com
  escala 0.5 ("hiRes"), ou seja, praticamente 1 pixel da textura por pixel de tela.
  (os outros heróis têm ~70 px com escala 0.7 — mesmo tamanho final na tela);
- as cores são as da folha original: sem redução de paleta, sem contraste extra
  e sem contorno adicionado (o desenho já tem o próprio contorno);
- o recorte tira 1 px da borda para não carregar o marrom do fundo.

Uso:  python scripts/build_pirate_sprites.py [previa.png]
"""
import json
import os
import sys

import cv2
import numpy as np
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "scripts", "source", "capitao-scarpa-folha-v2.png")
OUT_DIRS = [os.path.join(ROOT, "assets", "pixel-art", "characters"),
            os.path.join(ROOT, "Projeto atualizado", "assets", "pixel-art", "characters")]
PREVIEW = sys.argv[1] if len(sys.argv) > 1 else None

FW = FH = 128
FOOT = 118            # linha dos pés no quadro (mesma dos outros heróis)
STAND_H = 68          # altura em pé: a mesma dos outros heróis (Samurai 68, Xamã 67)
GAME_SCALE = 0.7      # mesma grade de pixel dos outros heróis

# ---------------------------------------------------------------- recorte
img = cv2.cvtColor(cv2.imread(SRC, cv2.IMREAD_UNCHANGED)[:, :, :3], cv2.COLOR_BGR2RGB).astype(np.float32)
H, W = img.shape[:2]

fig = np.zeros((H, W), bool)
for _ in range(4):  # fundo = média borrada só dos pixels que não são figura
    w = (~fig).astype(np.float32)
    bg = cv2.GaussianBlur(img * w[..., None], (0, 0), 18) / (cv2.GaussianBlur(w, (0, 0), 18)[..., None] + 1e-4)
    fig = ndi.binary_dilation(ndi.binary_opening(np.sqrt(((img - bg) ** 2).sum(2)) > 22), iterations=2)
diff = np.sqrt(((img - bg) ** 2).sum(2))
for y0, y1 in [(10, 50), (232, 270), (440, 478), (645, 682), (852, 892)]:
    diff[y0:y1, 0:160] = 0  # rótulos de texto ("PARADO", "ANDANDO"...)

mask = ndi.binary_fill_holes(ndi.binary_closing(diff > 27, iterations=3))
# brilho difuso em volta do sabre (cinza-amarronzado, sem saturação) — não faz parte do sprite
r_, g_, b_ = img[..., 0], img[..., 1], img[..., 2]
lum = 0.3 * r_ + 0.59 * g_ + 0.11 * b_
glow = (img.max(2) - img.min(2) < 22) & (lum > 60) & (lum < 118) & (r_ >= b_) & (diff < 75)
glow[:640] = False
mask &= ~glow
mask = ndi.binary_opening(mask, iterations=1)
lab, _ = ndi.label(mask)
objs = ndi.find_objects(lab)
big, small = [], []
for i, sl in enumerate(objs):
    area = int((lab[sl] == i + 1).sum())
    f = dict(id=i + 1, x0=sl[1].start, x1=sl[1].stop, y0=sl[0].start, y1=sl[0].stop, area=area)
    (big if area > 2500 else small).append(f)
for s in small:  # pedaços soltos (barra do casaco, ponta do sabre) voltam para a figura mais próxima
    if s["area"] < 15:
        continue
    cx, cy = (s["x0"] + s["x1"]) / 2, (s["y0"] + s["y1"]) / 2
    dist = lambda b: np.hypot(max(b["x0"] - cx, 0, cx - b["x1"]), max(b["y0"] - cy, 0, cy - b["y1"]))
    best = min(big, key=dist)
    if dist(best) < 14:
        lab[lab == s["id"]] = best["id"]
        best.update(x0=min(best["x0"], s["x0"]), x1=max(best["x1"], s["x1"]),
                    y0=min(best["y0"], s["y0"]), y1=max(best["y1"], s["y1"]))

ROWS = {"idle": (0, 235), "walk": (235, 440), "run": (440, 645), "atk": (645, 850), "death": (850, 1024)}
figs = {k: sorted([f for f in big if a <= (f["y0"] + f["y1"]) / 2 < b], key=lambda f: f["x0"]) for k, (a, b) in ROWS.items()}
for _fs in figs.values():
    for _f in _fs:
        _f["src"] = (img, lab)


def segment_dark_sheet(path, erase=()):
    """Folha de andar/correr (2 linhas x 8 quadros, fundo escuro com brilho avermelhado).

    Botas e calças escuras quase somem no fundo: limiar baixo ligado às partes fortes
    da figura, aceitando só pixels mais escuros ou mais saturados que o fundo.
    """
    from skimage.filters import apply_hysteresis_threshold
    im = cv2.cvtColor(cv2.imread(path, cv2.IMREAD_UNCHANGED)[:, :, :3], cv2.COLOR_BGR2RGB).astype(np.float32)
    for (y0, y1, x0, x1) in erase:                      # rótulos de texto: vira fundo
        im[y0:y1, x0:x1] = im[y0:y1, x1:x1 + 1]
    fg = np.zeros(im.shape[:2], bool)
    for _ in range(4):
        w = (~fg).astype(np.float32)
        bgi = cv2.GaussianBlur(im * w[..., None], (0, 0), 18) / (cv2.GaussianBlur(w, (0, 0), 18)[..., None] + 1e-4)
        fg = ndi.binary_dilation(ndi.binary_opening(np.sqrt(((im - bgi) ** 2).sum(2)) > 22), iterations=2)
    df = np.sqrt(((im - bgi) ** 2).sum(2))
    weak = (df > 11) & ((im.mean(2) < bgi.mean(2) - 6) | (im.max(2) - im.min(2) > bgi.max(2) - bgi.min(2) + 18))
    mk = apply_hysteresis_threshold(np.where(weak | (df > 27), df, 0), 11, 27)
    mk = ndi.binary_opening(ndi.binary_fill_holes(ndi.binary_closing(mk, iterations=2)), iterations=1)
    lb, _ = ndi.label(mk)
    bigs, smalls = [], []
    for i, sl in enumerate(ndi.find_objects(lb)):
        area = int((lb[sl] == i + 1).sum())
        f = dict(id=i + 1, x0=sl[1].start, x1=sl[1].stop, y0=sl[0].start, y1=sl[0].stop, area=area, src=(im, lb))
        (bigs if area > 2500 else smalls).append(f)
    for sm in smalls:
        if sm["area"] < 15:
            continue
        cx, cy = (sm["x0"] + sm["x1"]) / 2, (sm["y0"] + sm["y1"]) / 2
        dist = lambda bb: np.hypot(max(bb["x0"] - cx, 0, cx - bb["x1"]), max(bb["y0"] - cy, 0, cy - bb["y1"]))
        best = min(bigs, key=dist)
        if dist(best) < 14:
            lb[lb == sm["id"]] = best["id"]
            best.update(x0=min(best["x0"], sm["x0"]), x1=max(best["x1"], sm["x1"]),
                        y0=min(best["y0"], sm["y0"]), y1=max(best["y1"], sm["y1"]))
    return bigs


# Folha v3 (scripts/source/capitao-scarpa-folha-v3.png): todas as animações do mesmo
# desenho e na mesma escala — PARADO, ANDANDO, CORRENDO, MORRENDO e ATACANDO, 8 quadros cada.
V3_SRC = os.path.join(ROOT, "scripts", "source", "capitao-scarpa-folha-v3.png")
_v3 = segment_dark_sheet(V3_SRC, erase=[(10, 48, 0, 160), (218, 256, 0, 160), (424, 462, 0, 160),
                                        (616, 656, 0, 160), (806, 846, 0, 160)])
for _n, _a, _b in [("idle", 0, 215), ("walk", 215, 420), ("run", 420, 612), ("death", 612, 805), ("atk", 805, 1024)]:
    figs[_n] = sorted([f for f in _v3 if _a <= (f["y0"] + f["y1"]) / 2 < _b], key=lambda f: f["x0"])

# a folha v2 desenha todas as linhas na mesma escala: uma escala só para todas as animações
# (o personagem em pé mede ~177 px na folha → STAND_H no jogo)
SCALE = {k: STAND_H / 177 for k in ("idle", "walk", "run", "atk", "death")}
# folha de andar/correr (scripts/source/capitao-scarpa-andar-correr.png): pirata com ~282 px
# folha v3: o pirata em pé mede ~189 px; a mesma escala para todas as animações
SCALE = {k: STAND_H / 189 for k in ("idle", "walk", "run", "atk", "death")}

# ---------------------------------------------------------------- animações
# Folha v2 (scripts/source/capitao-scarpa-folha-v2.png): todas as poses de lado e o
# sabre sempre na mesma mão. vertical: "row" mantém a altura relativa ao chão da linha
# (a corrida sobe e desce de verdade); "feet" encosta cada quadro no chão (a queda).
ANIMS = {
    "idle":   dict(src=[("idle", i) for i in range(8)], v="row", h="torso", fps=6, loop=True),
    # andando e correndo: folha própria com as pernas alternando (8 + 8 quadros), na ordem
    # desenhada, alinhados pelo quadril e mantendo o sobe-e-desce de cada linha
    "walk":   dict(src=[("walk", i) for i in range(8)], v="row", h="hip", fps=11, loop=True),
    "run":    dict(src=[("run", i) for i in range(8)], v="row", h="hip", fps=14, loop=True),
    "attack": dict(src=[("atk", i) for i in range(8)], v="row", h="torso", fps=13, loop=False),
    "death":  dict(src=[("death", i) for i in range(8)], v="feet", h="bbox", fps=9, loop=False),
}
ORDER = ["idle", "walk", "run", "attack", "death"]
STRIP_DIR = os.path.join(ROOT, "assets", "sprites", "characters", "pirate")


def shrink(f, s):
    """Recorta a figura (sem 1 px da borda) e reduz com média de área em alfa pré-multiplicado."""
    pad = 2
    x0, x1, y0, y1 = f["x0"] - pad, f["x1"] + pad, f["y0"] - pad, f["y1"] + pad
    simg, slab = f["src"]
    m = slab[y0:y1, x0:x1] == f["id"]
    m = ndi.binary_erosion(m, iterations=1, border_value=0)
    m = m.astype(np.float32)
    rgb = simg[y0:y1, x0:x1] / 255.0
    ow, oh = max(1, round((x1 - x0) * s)), max(1, round((y1 - y0) * s))
    a = cv2.resize(m, (ow, oh), interpolation=cv2.INTER_AREA)
    c = cv2.resize(rgb * m[..., None], (ow, oh), interpolation=cv2.INTER_AREA) / np.maximum(a[..., None], 1e-4)
    return np.clip(c, 0, 1), a


def _feat(t):
    a = t[..., 3] / 255.0
    g = (t[..., :3].mean(2) / 255.0 * a).astype(np.float32)
    ys = np.nonzero(a.sum(1))[0]
    m = np.zeros_like(g)
    m[ys.min():int(ys.min() + (ys.max() - ys.min()) * 0.5)] = 1
    return g * m


_win = cv2.createHanningWindow((FW, FW), cv2.CV_32F)


def build_strip(name, spec):
    figs_ = [figs[r][i] for r, i in spec["src"]]
    ground = {}
    for (r, _), f in zip(spec["src"], figs_):
        ground[r] = max(ground.get(r, 0), f["y1"])
    strip = np.zeros((FH, FW * len(figs_), 4), np.uint8)
    for k, ((row, _), f) in enumerate(zip(spec["src"], figs_)):
        sc = SCALE[row]
        c, a = shrink(f, sc)
        blur = cv2.GaussianBlur(c, (0, 0), 0.7)                     # nitidez leve (cores preservadas)
        c = np.clip(c + (c - blur) * 0.45, 0, 1)
        m = a > 0.5
        q = (c * 255).round().astype(np.uint8)
        ys, xs = np.nonzero(m)
        if spec["h"] == "hip":                                      # quadril: faixa entre 50% e 62% da altura
            hb = (ys > ys.min() + (ys.max() - ys.min()) * .50) & (ys < ys.min() + (ys.max() - ys.min()) * .62)
            cx = xs[hb].mean() if hb.any() else xs.mean()
        elif spec["h"] == "torso":                                    # centro do tronco: o sabre não desloca o corpo
            top = ys < (ys.min() + ys.max()) / 2
            cx = xs[top].mean() if top.any() else xs.mean()
        else:                                                       # centro da figura (corpo deitado cabe inteiro)
            cx = (xs.min() + xs.max()) / 2
        lift = round((ground[row] - f["y1"]) * sc) if spec["v"] == "row" else 0
        offx, offy = int(round(64 - cx)), FOOT - lift - ys.max()
        tx, ty = xs + offx, ys + offy
        ok = (tx >= 0) & (tx < FW) & (ty >= 0) & (ty < FH)
        if (~ok).any():
            raise SystemExit(f"{name} quadro {k}: {int((~ok).sum())} px fora da célula")
        tile = np.zeros((FH, FW, 4), np.uint8)
        tile[ty, tx, :3] = q[ys, xs]
        tile[ty, tx, 3] = 255
        strip[:, k * FW:(k + 1) * FW] = tile
    if spec["loop"] and spec["h"] == "torso":                      # alinhamento fino do tronco (sem tremer)
        base = _feat(strip[:, :FW].astype(np.float32))
        for k in range(1, len(figs_)):
            tile = strip[:, k * FW:(k + 1) * FW]
            (dx, _), _ = cv2.phaseCorrelate(base, _feat(tile.astype(np.float32)), _win)
            sx = -int(round(dx))
            if sx and abs(sx) <= 4 and not tile[:, :abs(sx)].any() and not tile[:, -abs(sx):].any():
                strip[:, k * FW:(k + 1) * FW] = np.roll(tile, sx, axis=1)
    return strip


def write_png(path, arr):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(cv2.imencode(".png", cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA))[1].tobytes())


strips, start = {}, {}
for name in ORDER:
    strips[name] = build_strip(name, ANIMS[name])
    write_png(os.path.join(STRIP_DIR, f"pirate_{name}.png"), strips[name])

n = 0
for name in ORDER:
    start[name] = n
    n += strips[name].shape[1] // FW
    print(f"pirate_{name}.png", strips[name].shape[1] // FW, "quadros", f"{strips[name].shape[1]}x{FH}")

# folha do jogo = as animações em sequência (o formato "pack" que o jogo já usa)
# ---------------------------------------------------------------- padrão visual do jogo
# Os heróis do jogo têm ~68 px, 14-23 cores chapadas e contorno escuro. A arte enviada é
# "pintada" (centenas de tons) e cada quadro gerado muda um pouco os detalhes, o que pisca
# na tela. Aqui: (1) parado vira um único desenho com respiração de 1 px (como os outros);
# (2) paleta única de PALETTE cores para todas as animações; (3) limpeza de pixels soltos;
# (4) borda interna escurecida (contorno sem engrossar a silhueta).
PALETTE = 40


def breathe(base):
    """4 quadros de respiração: o tronco desce 1 px e volta; pernas paradas."""
    ys = np.nonzero(base[..., 3].any(1))[0]
    waist = int(ys.min() + (ys.max() - ys.min()) * 0.56)
    down = base.copy()
    top = base[:waist].copy()
    down[:waist] = 0
    sub = down[1:waist + 1]
    m = top[..., 3] > 0
    sub[m] = top[m]
    return [base, base, down, down]


def quantize_all(strips_):
    allpx = np.concatenate([st[st[..., 3] > 0][:, :3] for st in strips_.values()]).astype(np.float32)
    lab_px = cv2.cvtColor(allpx[None] / 255.0, cv2.COLOR_RGB2LAB)[0]
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 80, 0.1)
    _, _, cen = cv2.kmeans(lab_px.astype(np.float32), PALETTE, None, crit, 5, cv2.KMEANS_PP_CENTERS)
    pal = (cv2.cvtColor(cen[None].astype(np.float32), cv2.COLOR_LAB2RGB)[0] * 255).clip(0, 255)
    out = {}
    for k, st in strips_.items():
        q = st.copy()
        m = st[..., 3] > 0
        lp = cv2.cvtColor(st[..., :3].astype(np.float32)[m][None] / 255.0, cv2.COLOR_RGB2LAB)[0]
        idx = ((lp[:, None, :] - cen[None]) ** 2).sum(-1).argmin(1)
        q[m, :3] = pal[idx].round().astype(np.uint8)
        out[k] = q
    return out, pal


def clean_and_outline(st):
    st = st.copy()
    a = st[..., 3] > 0
    rgb = st[..., :3].astype(int)
    for _ in range(2):   # pixel solto no meio de uma área de cor única -> cor da área
        nb = [np.roll(rgb, s_, axis=ax) for ax, s_ in ((0, 1), (0, -1), (1, 1), (1, -1))]
        na = [np.roll(a, s_, axis=ax) for ax, s_ in ((0, 1), (0, -1), (1, 1), (1, -1))]
        same = (np.abs(nb[0] - nb[1]).sum(-1) < 8) & (np.abs(nb[2] - nb[3]).sum(-1) < 8) & (np.abs(nb[0] - nb[2]).sum(-1) < 8)
        odd = a & na[0] & na[1] & na[2] & na[3] & same & (np.abs(rgb - nb[0]).sum(-1) > 8)
        rgb[odd] = nb[0][odd]
    st[..., :3] = rgb.astype(np.uint8)
    k4 = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    nbc = ndi.convolve(a.astype(int), k4, mode="constant")
    st[a & (nbc <= 1), 3] = 0                      # fiapos de 1 px na borda
    a = st[..., 3] > 0
    edge = a & ~ndi.binary_erosion(a, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    dark = (st[..., :3].astype(int) * 0.38 + np.array([10, 6, 6])).clip(0, 255).astype(np.uint8)
    st[edge, :3] = dark[edge]
    return st


# a arte enviada é bem mais escura que os outros heróis: clareia (gama) e satura um pouco
for _k, _st in strips.items():
    _m = _st[..., 3] > 0
    _c = _st[..., :3].astype(np.float32) / 255.0
    _c = _c ** 0.82
    _l = _c.mean(-1, keepdims=True)
    _c = np.clip(_l + (_c - _l) * 1.15, 0, 1)
    _st[..., :3] = np.where(_m[..., None], (_c * 255).round(), _st[..., :3]).astype(np.uint8)
strips, _pal = quantize_all(strips)
for k in strips:
    strips[k] = np.concatenate([clean_and_outline(strips[k][:, i * FW:(i + 1) * FW])
                                for i in range(strips[k].shape[1] // FW)], axis=1)
    write_png(os.path.join(STRIP_DIR, f"pirate_{k}.png"), strips[k])
n = 0
for name in ORDER:
    start[name] = n
    n += strips[name].shape[1] // FW

sheet = np.concatenate([strips[k] for k in ORDER], axis=1)
I = lambda name, k=0: start[name] + k
cnt = lambda name: strips[name].shape[1] // FW
amap = {
    "idle": [I("idle", k) for k in range(cnt("idle"))],
    "idlevar": [I("idle", k) for k in (3, 4, 3)],
    "walk": [I("walk", k) for k in range(cnt("walk"))],
    "run": [I("run", k) for k in range(cnt("run"))],
    # ataque (arma: preparação 320 ms, golpe 120 ms, recuperação 240 ms):
    # 0 postura · 1 prepara · 2 recua o sabre | 3 avança · 4 golpe amplo | 5 extensão · 6 continuação · 7-8 volta
    # 0 postura · 1 prepara · 2 sabre erguido | 3 golpe | 4 recolhe · 6 abaixa · 7 postura
    # (o 5 da folha ergue o sabre de novo para um 2º golpe; fica de fora do golpe simples)
    "attackW": [I("attack", k) for k in (0, 1, 2)], "attackH": [I("attack", 3)],
    "attackR": [I("attack", k) for k in (4, 6, 7)],
    "windupA": I("attack", 1), "windup": I("attack", 2), "hitA": I("attack", 3), "hit": I("attack", 3), "recovery": I("attack", 6),
    "guardStart": I("attack", 0), "guard": I("attack", 0),
    "hurt": I("death", 0), "hurtB": I("death", 1), "stunA": I("death", 1), "stunB": I("death", 2),
    "dashA": I("run", 0), "dash": I("run", 3),
    "castA": I("attack", 1), "cast": I("attack", 3), "castC": I("attack", 6),
    "deathSeq": [I("death", k) for k in range(cnt("death"))],
    "deathA": I("death", 0), "deathB": I("death", 3), "deathC": I("death", cnt("death") - 1),
}

# retrato do HUD: quadrado centrado no rosto do primeiro quadro parado
ys, xs = np.nonzero(sheet[:, :FW, 3] > 0)
top = int(ys.min())
fx = int(round(xs[ys < top + 22].mean()))
P = 22                 # mesmo recorte de retrato dos outros heróis (22x22)
portrait = [fx - P // 2 + 1, max(0, top - 1), P, P]

layout = {"frameW": FW, "frameH": FH, "scale": GAME_SCALE, "hiRes": False, "footY": FOOT, "bakedWeapon": True,
          "portrait": portrait, "fps": {k: ANIMS[k]["fps"] for k in ANIMS if ANIMS[k]["fps"]} | {"idlevar": 3},
          "anchors": [[80, 76]] * n, "torso": [[64, 80]] * n, "head": [[64, top + 12]] * n, "map": amap}

KEY = "pirate-v3a"           # nome novo a cada mudança grande: o cache offline do jogo não serve a versão velha
png = cv2.imencode(".png", cv2.cvtColor(sheet, cv2.COLOR_RGBA2BGRA))[1].tobytes()
for d in OUT_DIRS:
    if not os.path.isdir(os.path.dirname(d)):
        continue
    os.makedirs(d, exist_ok=True)
    for name in [f"{KEY}-body.png"] + [f"{KEY}-t{t}-body.png" for t in range(5)]:
        open(os.path.join(d, name), "wb").write(png)
    json.dump(layout, open(os.path.join(d, f"{KEY}.json"), "w"), separators=(",", ":"))
    for old in [f"pirate-{k}{e}" for k in ("pack", "hd", "hd2", "hd3", "hd4", "hd5", "hd6", "hd7", "hd8", "px1") for e in ("-body.png", ".json")] + \
               [f"pirate-{k}-t{t}-body.png" for k in ("pack", "hd", "hd2", "hd3", "hd4", "hd5", "hd6", "hd7", "hd8", "px1") for t in range(5)]:
        if os.path.exists(os.path.join(d, old)):
            os.remove(os.path.join(d, old))
json.dump({"cell": [FW, FH], "scale": GAME_SCALE, "footY": FOOT,
           "animations": {k: {"frames": cnt(k), "file": f"pirate_{k}.png", "size": [cnt(k) * FW, FH],
                              "fps": ANIMS[k]["fps"], "loop": ANIMS[k]["loop"],
                              "source": [f"{r}#{i}" for r, i in ANIMS[k]["src"]]} for k in ORDER},
           "gameSheet": f"assets/pixel-art/characters/{KEY}-body.png", "map": amap},
          open(os.path.join(STRIP_DIR, "pirate_config.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"OK {KEY}-body.png", sheet.shape, len(png), "bytes;", n, "quadros; retrato", portrait)

if PREVIEW:  # prévia: uma linha por animação, ampliada 2x
    rows = []
    wmax = max(v.shape[1] for v in strips.values())
    for k in ORDER:
        r = np.zeros((FH, wmax, 4), np.uint8)
        r[:, :strips[k].shape[1]] = strips[k]
        rows.append(r)
    pv = np.concatenate(rows, 0)
    al = pv[..., 3:4] / 255.0
    out = (pv[..., :3] * al + np.array([38, 32, 36]) * (1 - al)).astype(np.uint8)
    for k in range(len(ORDER) + 1):
        out[k * FH - 1 if k else 0, :] = (90, 80, 70)
    out[np.arange(len(ORDER) * FH), :][..., 0]
    out = cv2.resize(out, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    for k in range(len(ORDER)):                                     # linha do chão (footY)
        out[(k * FH + FOOT) * 2 + 1, :, :] = (70, 110, 70)
    cv2.imwrite(PREVIEW, cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
