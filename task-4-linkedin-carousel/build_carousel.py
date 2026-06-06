#!/usr/bin/env python3
"""Build a ready-to-post LinkedIn carousel (1080x1350) from the ThreadPup
diagrams. 4 slides: Cover (hook) -> System Architecture -> Customer Journey ->
CTA. Diagram slides are diagram-dominant (the diagram's own header is the
title, so no duplicate chrome title); architecture slide adds a feed-legible
stack summary to fill the canvas. Reflects the multi-agent QA pass."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
CREAM = (255, 253, 249)
BARK = "#5B3A29"; CARAMEL = "#C68642"; GRAY = "#6b6b6b"; GREEN = "#2f9e44"
HERE = Path(__file__).parent
SRC = HERE.parent / "task-3-threadpup"
OUT = HERE / "carousel-output"
AR = r"C:\Windows\Fonts\arial.ttf"; ARB = r"C:\Windows\Fonts\arialbd.ttf"; EMO = r"C:\Windows\Fonts\seguiemj.ttf"

_fc = {}
def F(sz, bold=False):
    k = (bold, int(sz))
    if k not in _fc: _fc[k] = ImageFont.truetype(ARB if bold else AR, int(sz))
    return _fc[k]
def EFnt(sz):
    k = ("e", int(sz))
    if k not in _fc:
        try: _fc[k] = ImageFont.truetype(EMO, int(sz))
        except Exception: _fc[k] = None
    return _fc[k]
def hx(c):
    c = c.lstrip("#"); return (int(c[0:2],16), int(c[2:4],16), int(c[4:6],16))

def is_emoji(ch):
    cp = ord(ch)
    return (0x1F000 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF or 0x2B00 <= cp <= 0x2BFF or
            cp in (0xFE0F, 0x200D) or 0x1F1E6 <= cp <= 0x1F1FF)
def _runs(s):
    out, cur, ce = [], "", None
    for ch in s:
        e = is_emoji(ch)
        if cur and e != ce: out.append((cur, ce)); cur = ""
        cur += ch; ce = e
    if cur: out.append((cur, ce))
    return out
def textw(s, f):
    ef = EFnt(f.size)
    return sum((ef or f).getlength(r) if e else f.getlength(r) for r, e in _runs(s))
def text(d, xy, s, f, fill, anchor="la"):
    x, y = xy; ef = EFnt(f.size); total = textw(s, f)
    if "m" in anchor: x -= total/2
    elif anchor.startswith("r"): x -= total
    for r, e in _runs(s):
        if e and ef:
            try: d.text((x, y), r, font=ef, embedded_color=True)
            except Exception: d.text((x, y), r, fill=fill, font=f)
            x += ef.getlength(r)
        else:
            d.text((x, y), r, fill=fill, font=f); x += f.getlength(r)
def wrap(s, f, maxw):
    words = s.split(); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if textw(t, f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def dog(d, x, y, s):
    def E(rx, ry, rw, rh, fill, stroke, sw=2):
        d.ellipse([x+rx*s, y+ry*s, x+(rx+rw)*s, y+(ry+rh)*s], fill=hx(fill), outline=hx(stroke), width=max(1, int(sw*s)))
    E(0,0,18,26,"#5B3A29","#5B3A29"); E(38,0,18,26,"#5B3A29","#5B3A29")
    E(6,6,44,40,"#F2D2A9","#5B3A29"); E(18,20,6,6,"#1e1e1e","#1e1e1e",1)
    E(34,20,6,6,"#1e1e1e","#1e1e1e",1); E(24,30,9,6,"#1e1e1e","#1e1e1e",1)

def canvas():
    img = Image.new("RGB", (W, H), CREAM); return img, ImageDraw.Draw(img)
def num_pill(d, n):
    d.rounded_rectangle([72, 64, 138, 130], radius=16, fill=hx(CARAMEL))
    text(d, (105, 73), f"{n:02d}", F(34, True), "white", "ma")
def footer(d, n):
    d.line([72, 1212, W-72, 1212], fill=hx("#ead9c6"), width=3)
    dog(d, 72, 1232, 1.0); text(d, (142, 1238), "ThreadPup", F(27, True), hx(BARK))
    text(d, (W-72, 1242), f"{n:02d} / 04", F(23), hx(GRAY), "ra")

def fit(img, path, box):
    im = Image.open(path).convert("RGBA"); x0, y0, x1, y1 = box
    sc = min((x1-x0)/im.width, (y1-y0)/im.height)
    nw, nh = int(im.width*sc), int(im.height*sc)
    im = im.resize((nw, nh), Image.LANCZOS)
    px, py = x0 + ((x1-x0)-nw)//2, y0 + ((y1-y0)-nh)//2
    img.paste(im, (px, py), im); return px, py, nw, nh

def slide_cover():
    img, d = canvas()
    text(d, (W//2, 168), "E-COMMERCE · SYSTEM DESIGN", F(27, True), hx(CARAMEL), "ma")
    for i, ln in enumerate(["What happens after", "you click “Buy”?"]):
        text(d, (W//2, 252 + i*84), ln, F(62, True), hx(BARK), "ma")
    dog(d, W//2 - 115, 420, 4.6)   # enlarged brand hero
    sub = wrap("A visual teardown of ThreadPup's e-commerce stack — architecture + the customer journey.", F(30), W-240)
    y = 700
    for ln in sub: text(d, (W//2, y), ln, F(30), hx(GRAY), "ma"); y += 44
    d.rounded_rectangle([W//2-135, 846, W//2+135, 920], radius=22, fill=hx(BARK))
    text(d, (W//2, 864), "Swipe →", F(33, True), "white", "ma")
    footer(d, 1)
    return img

def swatch_row(d, y, color, stroke, title, desc):
    d.rounded_rectangle([72, y, 116, y+44], radius=10, fill=hx(color), outline=hx(stroke), width=3)
    text(d, (134, y+4), title, F(29, True), hx(BARK))
    tx = 134 + textw(title, F(29, True))
    text(d, (tx, y+7), "  " + desc, F(26), hx(GRAY))

def slide_architecture():
    img, d = canvas(); num_pill(d, 2)
    fit(img, SRC/"architecture.png", (28, 150, W-28, 720))
    text(d, (72, 760), "The stack, by layer", F(30, True), hx(CARAMEL))
    swatch_row(d, 812, "#a5d8ff", "#1971c2", "Customer-facing", "Customer, Next.js storefront (Vercel)")
    swatch_row(d, 884, "#b2f2bb", "#2f9e44", "Backend & fulfillment", "Supabase, Fulfillment API, Print Shop")
    swatch_row(d, 956, "#ffd8a8", "#e8590c", "Third-party APIs", "Stripe payments, Resend emails")
    text(d, (72, 1052), "Order flow: Customer → Storefront → Stripe → Supabase → Fulfillment → Print Shop → Resend", F(22), hx(GRAY))
    footer(d, 2)
    return img

def slide_journey():
    img, d = canvas(); num_pill(d, 3)
    fit(img, HERE/"journey-carousel.png", (24, 150, W-24, 1196))
    footer(d, 3)
    return img

def slide_cta():
    img, d = canvas()
    text(d, (W//2, 132), "From Click to Doorstep", F(52, True), hx(BARK), "ma")
    text(d, (W//2, 206), "The full ThreadPup stack, end to end", F(28), hx(GRAY), "ma")
    dog(d, W//2 - 112, 296, 4.0)
    chips = ["Next.js", "Supabase", "Stripe", "Fulfillment API", "Print Shop", "Resend"]
    f = F(28, True); gap = 26
    rows = [chips[:3], chips[3:]]
    y = 620
    for ri, row in enumerate(rows):
        ws = [textw(c, f) + 56 for c in row]; total = sum(ws) + gap*(len(row)-1)
        cx = (W - total)//2; ry = y + ri*88
        for ci, c in enumerate(row):
            w = ws[ci]
            d.rounded_rectangle([cx, ry, cx+w, ry+64], radius=18, fill=CREAM, outline=hx(CARAMEL), width=3)
            text(d, (cx+w/2, ry+16), c, f, hx(BARK), "ma"); cx += w + gap
    d.rounded_rectangle([W//2-310, 858, W//2+310, 938], radius=22, fill=hx(GREEN))
    text(d, (W//2, 878), "Save this if you're building e-commerce", F(28, True), "white", "ma")
    text(d, (W//2, 980), "Follow for more build breakdowns →", F(26), hx(GRAY), "ma")
    footer(d, 4)
    return img

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    slides = [slide_cover(), slide_architecture(), slide_journey(), slide_cta()]
    for i, s in enumerate(slides, 1):
        assert s.size == (W, H), s.size
        s.save(OUT / f"slide-{i:02d}.png"); print("wrote", f"slide-{i:02d}.png", s.size)

if __name__ == "__main__":
    main()
