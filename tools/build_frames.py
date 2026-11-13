"""Composite app screenshots into Apple's official product bezels (assets/bezels) -> assets/framed."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
BEZ, SCR, OUT = ROOT / "assets/bezels", ROOT / "assets/screens", ROOT / "assets/framed"

def hole(bezel):
    """Mask and bbox of the screen area around the centre: transparent in some of Apple's bezels,
    a flat grey placeholder in others."""
    cx, cy = bezel.width // 2, bezel.height // 2
    if bezel.getpixel((cx, cy))[3] < 128:
        b = bezel.split()[3].point(lambda v: 255 if v >= 128 else 0)
        ImageDraw.floodfill(b, (cx, cy), 100)
        m = np.asarray(b) == 100
    else:
        b = bezel.convert("RGB"); ImageDraw.floodfill(b, (cx, cy), (255, 0, 255), thresh=24)
        m = (np.asarray(b) == (255, 0, 255)).all(2)
    ys, xs = np.where(m)
    return m, (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)

def frame(bezel_name, shot, out, width):
    bezel = Image.open(BEZ / bezel_name).convert("RGBA")
    m, (x0, y0, x1, y1) = hole(bezel)
    canvas = Image.new("RGBA", bezel.size, (0, 0, 0, 0))
    mask = Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MaxFilter(7))
    if shot:
        shot_im = Image.open(SCR / shot).convert("RGBA").resize((x1 - x0 + 4, y1 - y0 + 4), Image.LANCZOS)
        canvas.paste(shot_im, (x0 - 2, y0 - 2))
        canvas.putalpha(mask)
    if bezel.getpixel((bezel.width // 2, bezel.height // 2))[3] < 128:
        canvas.alpha_composite(bezel)                      # see-through screen: bezel goes on top
    else:
        under = bezel.copy(); under.alpha_composite(canvas); canvas = under   # placeholder screen: cover it
    h = round(canvas.height * width / canvas.width)
    canvas.resize((width, h), Image.LANCZOS).save(OUT / out, quality=88, method=6)
    W, H = bezel.size
    return out, (x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H), (width, h)

def _coeffs(dst, src):
    """Perspective coefficients for Image.transform: maps each output (dst) corner to its source corner."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))

def _line(ts, vs):
    """Least-squares v = m*t + c."""
    m, c = np.polyfit(ts, vs, 1)
    return m, c

def frame_folded(bezel_name, shot, out, width, axis):
    """Apple's partially open iPhone Duo bezels come flattened, with a placeholder on the angled screen.
    Finds the two screen halves, and warps each half of the screenshot onto its half. axis "x": the fold is
    vertical (open like a book); axis "y": the fold is horizontal (top half upright, bottom half flat)."""
    bezel = Image.open(BEZ / bezel_name).convert("RGBA")
    bezel = bezel.resize((bezel.width * 3 // 10, bezel.height * 3 // 10), Image.LANCZOS)
    if axis == "y":  # work with a vertical fold, then turn back
        bezel = bezel.transpose(Image.TRANSPOSE)
    a = np.asarray(bezel).astype(int)
    lum = a[..., :3].sum(2) // 3
    lit = ((lum >= 24) & (lum <= 80) & (a[..., 3] > 200)).astype("uint8") * 255
    m = Image.fromarray(lit).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(13)).copy()  # close the placeholder text, cut thin leaks
    for fx_seed in ((.3, .5), (.7, .5), (.87, .5)) if axis == "y" else ((.3, .5), (.7, .5)):  # both halves: a bright crease can part them
        seed = (int(m.width * fx_seed[0]), int(m.height * fx_seed[1]))
        if m.getpixel(seed) == 255:
            ImageDraw.floodfill(m, seed, 100)
    m = m.point(lambda v: 255 if v == 100 else 0).filter(ImageFilter.MaxFilter(21)).filter(ImageFilter.MinFilter(13)).point(lambda v: 100 if v else 0)
    mask = np.asarray(m) == 100
    ys, xs = np.where(mask); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    cols = np.arange(x0, x1 + 1)
    top = np.array([np.where(mask[:, x])[0].min() for x in cols]); bot = np.array([np.where(mask[:, x])[0].max() for x in cols])
    w = x1 - x0
    h = np.convolve(bot - top, np.ones(9) / 9, "same")
    if axis == "x":  # book: both halves lean back, so the screen is shortest at the fold
        mid = slice(w // 4, 3 * w // 4); fx = int(cols[mid][np.argmin(h[mid])])
    else:            # laptop: the upright half has a constant width, the flat half widens towards you
        base = np.median(h[w // 5:w // 2]); fx = int(cols[w // 2:][np.argmax(h[w // 2:] > base * 1.025)])
    src = Image.open(SCR / shot).convert("RGBA")
    if axis == "y":
        src = src.transpose(Image.TRANSPOSE)
    W, H = src.size
    canvas = Image.new("RGBA", bezel.size, (0, 0, 0, 0))
    for side in (0, 1):
        ca, cb = (x0, fx) if side == 0 else (fx, x1)
        span = cb - ca
        inner = np.arange(ca + int(span * .2), cb - int(span * .2))
        mt, ct = _line(inner, top[inner - x0]); mb, cbm = _line(inner, bot[inner - x0])
        # outer edge: per row, the mask's outermost x on this side
        ty, by = mt * (ca if side == 0 else cb) + ct, mb * (ca if side == 0 else cb) + cbm
        rows = np.arange(int(ty + (by - ty) * .25), int(by - (by - ty) * .25))
        edge = np.array([(np.where(mask[y, ca:cb + 1])[0].min() if side == 0 else np.where(mask[y, ca:cb + 1])[0].max()) + ca for y in rows])
        me, ce = _line(rows, edge)  # x = me*y + ce
        def corner(ml, cl):  # meet of y = ml*x + cl and x = me*y + ce
            y = (ml * ce + cl) / (1 - ml * me); return (me * y + ce, y)
        o_top, o_bot = corner(mt, ct), corner(mb, cbm)
        f_top, f_bot = (fx, mt * fx + ct), (fx, mb * fx + cbm)
        dst = [o_top, f_top, f_bot, o_bot] if side == 0 else [f_top, o_top, o_bot, f_bot]
        sx0, sx1 = (0, W / 2) if side == 0 else (W / 2, W)
        warped = src.transform(bezel.size, Image.PERSPECTIVE, _coeffs(dst, [(sx0, 0), (sx1, 0), (sx1, H), (sx0, H)]), Image.BICUBIC)
        part = mask.copy(); part[:, :fx] &= side == 0; part[:, fx:] &= side == 1
        canvas.paste(warped, (0, 0), Image.fromarray((part * 255).astype("uint8")))
    out_im = bezel.copy(); out_im.alpha_composite(canvas)
    if axis == "y":
        out_im = out_im.transpose(Image.TRANSPOSE)
    box = out_im.getbbox(); out_im = out_im.crop(box)
    hh = round(out_im.height * width / out_im.width)
    out_im.resize((width, hh), Image.LANCZOS).save(OUT / out, quality=88, method=6)
    return out, (0, 0, 1, 1), (width, hh)

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    jobs = []
    for s in ["home-saved", "home-today", "setup-interval", "setup-repeat", "setup-custom", "home", "workout", "zones", "logex", "lock", "calendar", "meals", "exercises", "strength", "byweight"]:
        jobs.append(("iphone-18-pro-black.png", s + ".png", s + ".webp", 620))
    for s in ["watch-done", "watch-controls", "watch-active", "watch-rest", "watch-repeat"]:
        jobs.append(("watch-ultra-ocean-black.png", s + ".png", s + ".webp", 620))
    D = "duo/iPhone Duo - Star White - "
    jobs.append((D + "Inner Open Landscape.png", "duo-open.png", "duo-open.webp", 1500))
    jobs.append((D + "Inner Open Portrait.png", "duo-upright.png", "duo-upright.webp", 1090))
    jobs.append((D + "Outer Closed Portrait.png", "duo-closed.png", "duo-closed.webp", 900))
    print(*frame_folded(D + "Inner Partially Open Landscape.png", "duo-book.png", "duo-book.webp", 1500, "x")[::2])
    print(*frame_folded(D + "Inner Partially Open Portrait.png", "duo-bench.png", "duo-bench.webp", 1300, "y")[::2])
    jobs.append(("iphone-18-pro-black.png", None, "bezel-iphone.webp", 900))
    jobs.append(("watch-ultra-ocean-black.png", None, "bezel-watch.webp", 620))
    for j in jobs:
        name, rect, size = frame(*j)
        print(name, size, " ".join(f"{v * 100:.3f}%" for v in rect))
