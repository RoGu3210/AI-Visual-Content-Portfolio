#!/usr/bin/env python3
"""build_pack.py — assemble the complete YouTube explainer pack.

(1) Down-converts the 5 final frames in output-option-a/ to EXACTLY 1920x1080.
    Source frames are 2752x1536 (slightly wider than 16:9), so we center-crop to
    the 16:9 box first, then Lanczos-resize — no horizontal squish/distortion.
(2) Renders a punchy 1280x720 YouTube thumbnail (built from scratch, crisp text).

All outputs land in explainer-pack/ next to the script + hook.
    py build_pack.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
SRC = HERE / "output-option-a"
OUT = HERE / "explainer-pack"
AR = r"C:\Windows\Fonts\arial.ttf"; ARB = r"C:\Windows\Fonts\arialbd.ttf"
EMO = r"C:\Windows\Fonts\seguiemj.ttf"

FRAMES = [
    ("frame-01-hook.png", "frame-01-hook_1080p.png"),
    ("frame-02-problem.png", "frame-02-problem_1080p.png"),
    ("frame-03-concept.png", "frame-03-concept_1080p.png"),
    ("frame-04-example.png", "frame-04-example_1080p.png"),
    ("frame-05-summary.png", "frame-05-summary_1080p.png"),
]
TARGET = (1920, 1080)

_fc = {}
def F(sz, bold=True):
    k = (bold, int(sz))
    if k not in _fc: _fc[k] = ImageFont.truetype(ARB if bold else AR, int(sz))
    return _fc[k]
def EF(sz):
    k = ("e", int(sz))
    if k not in _fc:
        try: _fc[k] = ImageFont.truetype(EMO, int(sz))
        except Exception: _fc[k] = None
    return _fc[k]
def hx(c):
    c = c.lstrip("#"); return (int(c[0:2],16), int(c[2:4],16), int(c[4:6],16))
def tw(d, s, f): return d.textlength(s, font=f)


def resize_frames():
    tr = TARGET[0] / TARGET[1]
    for src_name, out_name in FRAMES:
        im = Image.open(SRC / src_name).convert("RGB")
        w, h = im.size
        # center-crop to 16:9, then resize
        if w / h > tr:                       # too wide -> trim sides
            nw = round(h * tr); x0 = (w - nw) // 2
            im = im.crop((x0, 0, x0 + nw, h))
        else:                                # too tall -> trim top/bottom
            nh = round(w / tr); y0 = (h - nh) // 2
            im = im.crop((0, y0, w, y0 + nh))
        im = im.resize(TARGET, Image.LANCZOS)
        im.save(OUT / out_name)
        print("frame ->", out_name, im.size)


def make_thumbnail():
    W, H = 1280, 720
    BG = hx("#fdfcf7"); INK = hx("#1e1e1e"); BLUE = hx("#1971c2")
    CORAL = hx("#e8590c"); GREEN = hx("#2f9e44")
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    # sketchy border
    d.rounded_rectangle([18, 18, W-18, H-18], radius=28, outline=INK, width=6)
    # "3-MIN EXPLAINER" kicker badge
    d.rounded_rectangle([60, 70, 470, 138], radius=18, fill=BLUE)
    d.text((84, 84), "3-MIN EXPLAINER", font=F(40), fill="white")
    # title — big, stacked, high contrast
    d.text((60, 188), "STOP PROMPTING", font=F(96), fill=INK)
    d.text((60, 296), "AI ", font=F(96), fill=INK)
    wx = 60 + tw(d, "AI ", F(96))
    d.text((wx, 296), "WRONG", font=F(96), fill=CORAL)
    # caramel underline accent
    d.line([66, 408, 760, 408], fill=hx("#C68642"), width=10)
    # subtitle
    d.text((62, 440), "4 techniques the pros use", font=F(50, bold=False), fill=hx("#444444"))
    # "4 TECHNIQUES" stamp (rotated badge)
    stamp = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); sd = ImageDraw.Draw(stamp)
    sd.ellipse([20, 20, 280, 280], fill=GREEN)
    sd.text((150, 110), "4", font=F(120), fill="white", anchor="mm")
    sd.text((150, 210), "TECHNIQUES", font=F(34), fill="white", anchor="mm")
    stamp = stamp.rotate(-12, resample=Image.BICUBIC, expand=False)
    img.paste(stamp, (W-330, H-340), stamp)
    # robot + sparkles via emoji
    ef = EF(150)
    if ef:
        img.paste_emoji = None
        d.text((150, 520), "🤖", font=ef, embedded_color=True)
        d.text((330, 540), "✨", font=EF(90), embedded_color=True)
    img.save(OUT / "thumbnail.png")
    print("thumbnail ->", img.size)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    resize_frames()
    make_thumbnail()
    # sanity asserts
    for _, out_name in FRAMES:
        assert Image.open(OUT / out_name).size == TARGET, out_name
    assert Image.open(OUT / "thumbnail.png").size == (1280, 720)
    print("OK — pack assembled in", OUT)


if __name__ == "__main__":
    main()
