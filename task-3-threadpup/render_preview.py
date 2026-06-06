#!/usr/bin/env python3
"""Raster preview / export of *.excalidraw.json scene specs — the "render JSON
-> PNG -> spot layout issues" half of the self-check loop. Coordinates match
Excalidraw 1:1.

Modes:
  (default)      clean crisp render (Arial), good for layout/overlap checks
  --rough        hand-drawn sketch look: wobbly strokes + Ink Free handwriting font
  --uniform      render every input centered in one shared SQUARE frame (carousel)
  --scale N      output scale (2 = "2x resolution")
  --out NAME     output filename (single-file mode only)

Emoji render via Segoe UI Emoji. Usage:
  py render_preview.py architecture.excalidraw.json --scale 2 --rough --out architecture.png
  py render_preview.py s1.json s2.json ... --uniform --scale 2 --rough
"""
import json, math, random, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = r"C:\Windows\Fonts\arial.ttf"
HAND_PATH = r"C:\Windows\Fonts\Inkfree.ttf"
EMOJI_PATH = r"C:\Windows\Fonts\seguiemj.ttf"

ROUGH = False
AMP = 2.2          # stroke wobble amplitude (px)
STEP = 16          # path resample spacing (px)

_fc = {}
def font(size, path=None):
    path = path or (HAND_PATH if ROUGH else FONT_PATH)
    key = (path, int(size))
    if key not in _fc:
        try: _fc[key] = ImageFont.truetype(path, max(1, int(size)))
        except Exception: _fc[key] = ImageFont.truetype(FONT_PATH, max(1, int(size)))
    return _fc[key]

def emoji_font(size):
    key = ("emoji", int(size))
    if key not in _fc:
        try: _fc[key] = ImageFont.truetype(EMOJI_PATH, max(1, int(size)))
        except Exception: _fc[key] = None
    return _fc[key]

def is_emoji(ch):
    cp = ord(ch)
    return (0x1F000 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF or 0x2B00 <= cp <= 0x2BFF or
            0x2190 <= cp <= 0x21FF or cp in (0xFE0F, 0x200D, 0x20E3) or 0x1F1E6 <= cp <= 0x1F1FF)

def split_runs(s):
    runs, cur, ce = [], "", None
    for ch in s:
        e = is_emoji(ch)
        if cur and e != ce: runs.append((cur, ce)); cur = ""
        cur += ch; ce = e
    if cur: runs.append((cur, ce))
    return runs

def line_width(line, fs):
    w = 0
    for run, e in split_runs(line):
        f = (emoji_font(fs) or font(fs)) if e else font(fs)
        w += f.getlength(run)
    return w

def draw_runs(draw, line, fs, x, y, col):
    for run, e in split_runs(line):
        ef = emoji_font(fs)
        if e and ef:
            try: draw.text((x, y), run, font=ef, embedded_color=True)
            except Exception: draw.text((x, y), run, fill=col, font=font(fs))
            x += ef.getlength(run)
        else:
            draw.text((x, y), run, fill=col, font=font(fs)); x += font(fs).getlength(run)

def hex_rgba(c, op=100):
    if c in ("transparent", None): return None
    c = c.lstrip("#"); return (int(c[0:2],16), int(c[2:4],16), int(c[4:6],16), int(255*op/100))

# ---------- hand-drawn geometry ----------
def jit(pts, rng, amp):
    return [(x + rng.uniform(-amp, amp), y + rng.uniform(-amp, amp)) for x, y in pts]

def resample(ap, step=STEP):
    out = []
    for i in range(len(ap)-1):
        ax, ay = ap[i]; bx, by = ap[i+1]; d = math.hypot(bx-ax, by-ay); n = max(1, int(d/step))
        for k in range(n): out.append((ax+(bx-ax)*k/n, ay+(by-ay)*k/n))
    out.append(ap[-1]); return out

def rrect_path(x0, y0, x1, y1, rad, step=14):
    rad = max(0, min(rad, (x1-x0)/2, (y1-y0)/2)); pts = []
    def edge(ax, ay, bx, by):
        d = math.hypot(bx-ax, by-ay); n = max(1, int(d/step))
        for i in range(n+1): pts.append((ax+(bx-ax)*i/n, ay+(by-ay)*i/n))
    def arc(cx, cy, s, e):
        n = max(2, int(abs(e-s)/(math.pi/2)*5))
        for i in range(n+1):
            a = s+(e-s)*i/n; pts.append((cx+rad*math.cos(a), cy+rad*math.sin(a)))
    edge(x0+rad, y0, x1-rad, y0); arc(x1-rad, y0+rad, -math.pi/2, 0)
    edge(x1, y0+rad, x1, y1-rad); arc(x1-rad, y1-rad, 0, math.pi/2)
    edge(x1-rad, y1, x0+rad, y1); arc(x0+rad, y1-rad, math.pi/2, math.pi)
    edge(x0, y1-rad, x0, y0+rad); arc(x0+rad, y0+rad, math.pi, 1.5*math.pi)
    return pts

def ellipse_path(cx, cy, rx, ry, step=12):
    n = max(10, int(2*math.pi*max(rx, ry)/step))
    return [(cx+rx*math.cos(2*math.pi*i/n), cy+ry*math.sin(2*math.pi*i/n)) for i in range(n)]

def draw_shape(d, kind, box, rad, fill, stroke, sw, rng):
    x0, y0, x1, y1 = box
    if not ROUGH:
        if kind == "rectangle": d.rounded_rectangle(box, radius=rad, fill=fill, outline=stroke, width=sw)
        else: d.ellipse(box, fill=fill, outline=stroke, width=sw)
        return
    base = rrect_path(x0, y0, x1, y1, rad) if kind == "rectangle" else ellipse_path((x0+x1)/2, (y0+y1)/2, (x1-x0)/2, (y1-y0)/2)
    p = jit(base, rng, AMP)
    if fill: d.polygon(p, fill=fill)
    if stroke: d.line(p + [p[0]], fill=stroke, width=sw, joint="curve")

def draw_arrow(d, ap, col, sw, dashed, end_head, start_head, rng):
    pts = jit(resample(ap), rng, AMP*0.8) if ROUGH else ap
    # keep endpoints anchored so connectors still touch
    if ROUGH: pts[0] = ap[0]; pts[-1] = ap[-1]
    if dashed:
        for i in range(len(pts)-1):
            p, q = pts[i], pts[i+1]
            n = max(1, int(math.hypot(q[0]-p[0], q[1]-p[1])/8))
            for k in range(0, n, 2):
                a = (p[0]+(q[0]-p[0])*k/n, p[1]+(q[1]-p[1])*k/n)
                b = (p[0]+(q[0]-p[0])*(k+1)/n, p[1]+(q[1]-p[1])*(k+1)/n)
                d.line([a, b], fill=col, width=sw)
    else:
        d.line(pts, fill=col, width=sw, joint="curve")
    def head(tip, prev):
        ang = math.atan2(tip[1]-prev[1], tip[0]-prev[0]); L = 12*math.copysign(1,1)*SCALE
        for da in (math.radians(150), -math.radians(150)):
            hp = [tip, (tip[0]+L*math.cos(ang+da), tip[1]+L*math.sin(ang+da))]
            if ROUGH: hp = jit(hp, rng, AMP*0.6); hp[0] = tip
            d.line(hp, fill=col, width=sw)
    if end_head: head(ap[-1], ap[-2])
    if start_head: head(ap[0], ap[1])

# ---------- scene drawing ----------
SCALE = 1.5
def draw_scene(spec, ox, oy, scale, W, H):
    global SCALE; SCALE = scale
    TX = lambda x: (x + ox) * scale
    TY = lambda y: (y + oy) * scale
    Sv = lambda v: v * scale
    base = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    for idx, el in enumerate(spec.get("elements", [])):
        t = el.get("type")
        if t == "cameraUpdate": continue
        rng = random.Random(idx * 9973 + 7)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        if t in ("rectangle", "ellipse", "diamond"):
            box = [TX(el["x"]), TY(el["y"]), TX(el["x"])+Sv(el.get("width",0)), TY(el["y"])+Sv(el.get("height",0))]
            fill = hex_rgba(el.get("backgroundColor","transparent"), el.get("opacity",100))
            stroke = hex_rgba(el.get("strokeColor","#1e1e1e"), el.get("opacity",100))
            sw = max(1, int(el.get("strokeWidth",2)*scale))
            if el.get("strokeColor") == "transparent": stroke = None
            if el.get("id") == "bg":   # backdrop: always clean
                d.rectangle(box, fill=fill); base = Image.alpha_composite(base, layer); continue
            rad = 12*scale if (t == "rectangle" and el.get("roundness")) else 0
            draw_shape(d, "rectangle" if t != "ellipse" else "ellipse", box, rad, fill, stroke, sw, rng)
            base = Image.alpha_composite(base, layer)
            lbl = el.get("label")
            if lbl:
                text_block(ImageDraw.Draw(base), lbl["text"], lbl.get("fontSize",16), TX(el["x"]), TY(el["y"]),
                           Sv(el.get("width",0)), Sv(el.get("height",0)), "center", "middle", lbl.get("strokeColor","#1e1e1e"))
        elif t == "text":
            text_block(ImageDraw.Draw(base), el["text"], el.get("fontSize",16), TX(el["x"]), TY(el["y"]),
                       0, 0, "left", "top", el.get("strokeColor","#1e1e1e"))
        elif t in ("arrow", "line"):
            pts = el.get("points", [[0,0],[el.get("width",0),el.get("height",0)]])
            ap = [(TX(el["x"]+px), TY(el["y"]+py)) for px, py in pts]
            col = hex_rgba(el.get("strokeColor","#1e1e1e"))[:3]; sw = max(1, int(el.get("strokeWidth",2)*scale))
            draw_arrow(d, ap, col, sw, el.get("strokeStyle") == "dashed",
                       el.get("endArrowhead","arrow" if t == "arrow" else None), el.get("startArrowhead"), rng)
            base = Image.alpha_composite(base, layer)
    return base

def text_block(draw, text, fs, px, py, pw, ph, align, valign, color):
    fsS = fs * SCALE; lines = text.split("\n"); lh = fs*1.25*SCALE; total = lh*len(lines)
    y = py + (ph-total)/2 if valign == "middle" else (py + ph - total if valign == "bottom" else py)
    col = hex_rgba(color)[:3]
    for ln in lines:
        tw = line_width(ln, fsS)
        x = px + (pw-tw)/2 if align == "center" else (px + pw - tw if align == "right" else px)
        draw_runs(draw, ln, fsS, x, y, col); y += lh

def bbox(spec, pad=40):
    xs, ys = [], []
    for el in spec.get("elements", []):
        if el.get("type") == "cameraUpdate" or el.get("id") == "bg": continue
        x, y, w, h = el.get("x",0), el.get("y",0), el.get("width",0), el.get("height",0)
        if el.get("type") in ("arrow","line"):
            for a, b in el.get("points",[[0,0],[w,h]]): xs.append(x+a); ys.append(y+b)
        else: xs += [x, x+w]; ys += [y, y+h]
    if not xs: return (0,0,1200,900)
    return (min(xs)-pad, min(ys)-pad, max(xs)+pad, max(ys)+pad)

def render_autofit(spec_path, scale, out=None):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    x0, y0, x1, y1 = bbox(spec)
    W, H = int((x1-x0)*scale), int((y1-y0)*scale)
    img = draw_scene(spec, -x0, -y0, scale, W, H)
    name = out or Path(spec_path).name.replace(".excalidraw.json", ".preview.png")
    img.convert("RGB").save(Path(spec_path).parent / name)
    print("wrote", name, f"{W}x{H}", "rough" if ROUGH else "clean")

def render_uniform(files, scale, pad=48):
    specs = [(f, json.loads(Path(f).read_text(encoding="utf-8"))) for f in files]
    boxes = {f: bbox(sp, pad=0) for f, sp in specs}
    side = max(max(b[2]-b[0], b[3]-b[1]) for b in boxes.values()) + 2*pad
    px = int(side*scale); print(f"uniform frame {side:.0f}^2 -> {px}px", "rough" if ROUGH else "clean")
    for f, sp in specs:
        cx0, cy0, cx1, cy1 = boxes[f]; cw, ch = cx1-cx0, cy1-cy0
        img = draw_scene(sp, (side-cw)/2 - cx0, (side-ch)/2 - cy0, scale, px, px)
        name = Path(f).name.replace(".excalidraw.json", ".png")
        img.convert("RGB").save(Path(f).parent / name); print("  wrote", name)

if __name__ == "__main__":
    argv = sys.argv[1:]
    ROUGH = "--rough" in argv
    uniform = "--uniform" in argv
    scale = 1.5; out = None
    if "--scale" in argv: scale = float(argv[argv.index("--scale")+1])
    if "--out" in argv: out = argv[argv.index("--out")+1]
    skip = {"--rough", "--uniform"}
    files = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i-1] not in ("--scale", "--out"))]
    if uniform: render_uniform(files, scale)
    else:
        for a in files: render_autofit(a, scale, out)
