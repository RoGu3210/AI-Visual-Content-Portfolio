#!/usr/bin/env python3
"""build_kit.py — Scenario 3: a week of ThreadPup LinkedIn content.

Builds 5 standalone branded infographics (1080x1350), one per business aspect,
in ONE consistent visual style (cream + caramel + bark, dog mascot, shared
chrome) — then assembles a ready-to-post carousel: Cover + the 5 + CTA = 7 slides.

Why Method B (branded PIL) over AI generation: the 5 posts must look like one
set. A template guarantees identical palette/typography/footer; AI image models
have no seed and drift between images.

    py build_kit.py
Outputs:
    content-kit/post-1.png .. post-5.png          (standalone daily posts)
    content-kit/carousel/slide-01.png .. slide-07.png  (cover + 5 + CTA)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
CREAM = (255, 253, 249); CARD = (255, 250, 242)
BARK = "#5B3A29"; CARAMEL = "#C68642"; GRAY = "#6b6b6b"; GREEN = "#2f9e44"
BLUE = "#1971c2"; ORANGE = "#e8590c"; PURPLE = "#7048e8"
TINT = {"blue": "#a5d8ff", "green": "#b2f2bb", "orange": "#ffd8a8", "purple": "#d0bfff"}
HERE = Path(__file__).parent
OUT = HERE / "content-kit"; CAR = OUT / "carousel"
AR = r"C:\Windows\Fonts\arial.ttf"; ARB = r"C:\Windows\Fonts\arialbd.ttf"
EMO = r"C:\Windows\Fonts\seguiemj.ttf"

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
    if isinstance(c, tuple): return c
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
def rrect(d, box, r, fill=None, outline=None, w=3):
    d.rounded_rectangle(box, radius=r, fill=(hx(fill) if fill else None),
                        outline=(hx(outline) if outline else None), width=w)
def emoji(d, x, y, ch, sz):
    ef = EFnt(sz)
    if ef: d.text((x, y), ch, font=ef, embedded_color=True)

def header(d, kicker, title_lines, mascot=True):
    text(d, (72, 112), kicker, F(29, True), hx(CARAMEL))
    if mascot: dog(d, W-176, 96, 1.7)
    y = 164
    for ln in title_lines:
        text(d, (72, y), ln, F(57, True), hx(BARK)); y += 70
    uw = max(textw(ln, F(57, True)) for ln in title_lines)
    d.line([76, y+6, 76 + min(uw, 580), y+6], fill=hx(CARAMEL), width=8)
    return y + 50

def footer(d, page=None):
    d.line([72, 1242, W-72, 1242], fill=hx("#ead9c6"), width=3)
    dog(d, 72, 1262, 1.0); text(d, (142, 1268), "ThreadPup", F(26, True), hx(BARK))
    text(d, (W-72, 1270), (f"{page:02d} / 07" if page else "threadpup.com"), F(22), hx(GRAY), "ra")


# ---------------- 1) WHAT THREADPUP IS ----------------
def aspect_what(page=None):
    img, d = canvas(); header(d, "MEET THREADPUP", ["Custom tees,", "printed on demand"])
    feats = [
        ("🎨", "Design your own", "Upload your art or use the live editor — preview it on the shirt instantly.", CARAMEL),
        ("🖨️", "Printed on demand", "Each shirt is made only when it's ordered. No minimums, no leftover stock.", GREEN),
        ("🚚", "Shipped to your door", "Produced and shipped in days — tracked the whole way to the doorstep.", BLUE),
    ]
    y = 392
    for ic, hd, bd, ac in feats:
        rrect(d, [72, y, 1008, y+228], 24, fill=CARD, outline=ac, w=3)
        emoji(d, 110, y+76, ic, 70)
        text(d, (236, y+44), hd, F(36, True), hx(BARK))
        for i, ln in enumerate(wrap(bd, F(27), 720)):
            text(d, (236, y+104+i*38), ln, F(27), hx(GRAY))
        y += 258
    footer(d, page); return img

# ---------------- 2) HOW AN ORDER FLOWS ----------------
def aspect_flow(page=None):
    img, d = canvas(); header(d, "BEHIND THE SCENES", ["What happens", "after you click Buy"])
    steps = [
        ("🛒", "Order placed", "status: pending", BLUE),
        ("💳", "Payment", "Stripe charges the card → paid", ORANGE),
        ("🖨️", "Production", "Print shop prints + quality-checks", GREEN),
        ("📦", "Packed & labeled", "tracking number created → shipped", GREEN),
        ("🚚", "Delivered", "status: delivered — they're happy!", BLUE),
    ]
    x, w, h = 150, 780, 116; y = 386
    for i, (ic, lb, sub, ac) in enumerate(steps):
        rrect(d, [x, y, x+w, y+h], 20, fill=CARD, outline=ac, w=3)
        d.rounded_rectangle([x, y, x+12, y+h], radius=6, fill=hx(ac))
        emoji(d, x+40, y+h//2-30, ic, 50)
        text(d, (x+120, y+24), lb, F(31, True), hx(BARK))
        text(d, (x+120, y+68), sub, F(24), hx(GRAY))
        if i < len(steps)-1:
            cx = x + w//2; d.line([cx, y+h, cx, y+h+26], fill=hx(CARAMEL), width=4)
            d.polygon([(cx-9, y+h+16), (cx+9, y+h+16), (cx, y+h+28)], fill=hx(CARAMEL))
        y += h + 30
    footer(d, page); return img

# ---------------- 3) THE TECH STACK ----------------
def aspect_stack(page=None):
    img, d = canvas(); header(d, "UNDER THE HOOD", ["The ThreadPup", "tech stack"])
    def chip(x, y, label, ac, fill):
        w = textw(label, F(29, True)) + 52
        rrect(d, [x, y, x+w, y+62], 18, fill=fill, outline=ac, w=3)
        text(d, (x+w/2, y+15), label, F(29, True), hx(BARK), "ma")
    def layer(y, name, ac, fill, chips):
        d.rounded_rectangle([72, y, 110, y+42], radius=10, fill=hx(fill), outline=hx(ac), width=3)
        text(d, (128, y+4), name, F(31, True), hx(BARK))
        cx, cy = 76, y + 66
        for c in chips:
            wd = textw(c, F(29, True)) + 52
            if cx + wd > 1000: cx = 76; cy += 78
            chip(cx, cy, c, ac, fill); cx += wd + 22
        return cy + 96
    y = 392
    y = layer(y, "Customer-facing", BLUE, TINT["blue"], ["Next.js", "Vercel"])
    y = layer(y, "Backend & fulfillment", GREEN, TINT["green"], ["Supabase", "Fulfillment API", "Print Shop"])
    y = layer(y, "Third-party APIs", ORANGE, TINT["orange"], ["Stripe", "Resend"])
    text(d, (72, 1110), "Serverless, type-safe, and built to scale.", F(28, True), hx(CARAMEL))
    footer(d, page); return img

# ---------------- 4) THE CUSTOMER JOURNEY ----------------
def aspect_journey(page=None):
    img, d = canvas(); header(d, "THE CUSTOMER JOURNEY", ["From discovery", "to repeat order"])
    steps = [
        ("🔍", "Discover", "Finds ThreadPup via search & social", PURPLE),
        ("🎨", "Customize", "Designs a shirt in the editor", BLUE),
        ("🛒", "Buy", "Checks out securely with Stripe", GREEN),
        ("📦", "Receive", "Gets the order, tracked end to end", ORANGE),
        ("🔁", "Repeat", "Comes back to design even more", CARAMEL),
    ]
    x, w, h = 150, 780, 116; y = 386
    for i, (ic, lb, sub, ac) in enumerate(steps):
        rrect(d, [x, y, x+w, y+h], 20, fill=CARD, outline=ac, w=3)
        d.rounded_rectangle([x, y, x+12, y+h], radius=6, fill=hx(ac))
        emoji(d, x+40, y+h//2-30, ic, 50)
        text(d, (x+120, y+24), lb, F(31, True), hx(BARK))
        text(d, (x+120, y+68), sub, F(24), hx(GRAY))
        if i < len(steps)-1:
            cx = x + w//2; d.line([cx, y+h, cx, y+h+26], fill=hx(CARAMEL), width=4)
            d.polygon([(cx-9, y+h+16), (cx+9, y+h+16), (cx, y+h+28)], fill=hx(CARAMEL))
        y += h + 30
    footer(d, page); return img

# ---------------- 5) WHY IT WORKS ----------------
def aspect_why(page=None):
    img, d = canvas(); header(d, "WHY IT WORKS", ["Print-on-demand,", "done right"])
    cards = [
        ("⚡", "Fast fulfillment", "Days, not weeks — from click to doorstep.", CARAMEL),
        ("📦", "Zero inventory risk", "Print only what's ordered. No dead stock.", GREEN),
        ("🔁", "Repeat buyers", "One-click reorders bring people back.", BLUE),
        ("❤️", "A brand people love", "A friendly mascot + clean UX they remember.", ORANGE),
    ]
    gx = [72, 560]; gy = [404, 800]; w, h = 448, 360
    for i, (ic, hd, bd, ac) in enumerate(cards):
        x = gx[i % 2]; y = gy[i // 2]
        rrect(d, [x, y, x+w, y+h], 24, fill=CARD, outline=ac, w=3)
        emoji(d, x+34, y+30, ic, 62)
        text(d, (x+34, y+120), hd, F(32, True), hx(BARK))
        for j, ln in enumerate(wrap(bd, F(25), w-68)):
            text(d, (x+34, y+172+j*34), ln, F(25), hx(GRAY))
    text(d, (W//2, 1192), "Lean economics. Happy customers.", F(26, True), hx(CARAMEL), "ma")
    footer(d, page); return img

# ---------------- COVER ----------------
def cover(page=None):
    img, d = canvas()
    text(d, (W//2, 150), "THREADPUP · A 5-PART BREAKDOWN", F(28, True), hx(CARAMEL), "ma")
    for i, ln in enumerate(["How a custom-tee", "startup actually works"]):
        text(d, (W//2, 232 + i*78), ln, F(60, True), hx(BARK), "ma")
    dog(d, W//2 - 115, 440, 4.6)
    sub = wrap("Five quick infographics: the product, the order flow, the tech stack, the customer journey, and why it works.", F(30), W-220)
    y = 720
    for ln in sub: text(d, (W//2, y), ln, F(30), hx(GRAY), "ma"); y += 44
    d.rounded_rectangle([W//2-135, 880, W//2+135, 954], radius=22, fill=hx(BARK))
    text(d, (W//2, 898), "Swipe →", F(33, True), "white", "ma")
    footer(d, page); return img

# ---------------- CTA ----------------
def cta(page=None):
    img, d = canvas()
    text(d, (W//2, 150), "THAT'S THE WHOLE BUILD", F(28, True), hx(CARAMEL), "ma")
    text(d, (W//2, 218), "That's ThreadPup.", F(60, True), hx(BARK), "ma")
    dog(d, W//2 - 100, 320, 3.6)
    chips = ["Product", "Order flow", "Tech stack", "Journey", "Why it works"]
    f = F(26, True); gap = 22
    ws = [textw(c, f) + 48 for c in chips]
    rows = [chips[:3], chips[3:]]; wsr = [ws[:3], ws[3:]]
    y = 600
    for ri, row in enumerate(rows):
        total = sum(wsr[ri]) + gap*(len(row)-1); cx = (W - total)//2; ry = y + ri*78
        for ci, c in enumerate(row):
            w = wsr[ri][ci]
            rrect(d, [cx, ry, cx+w, ry+60], 18, fill=CARD, outline=CARAMEL, w=3)
            text(d, (cx+w/2, ry+14), c, f, hx(BARK), "ma"); cx += w + gap
    d.rounded_rectangle([W//2-320, 838, W//2+320, 918], radius=22, fill=hx(GREEN))
    text(d, (W//2, 858), "Save this if you're building e-commerce", F(28, True), "white", "ma")
    text(d, (W//2, 968), "Follow for weekly build breakdowns →", F(26), hx(GRAY), "ma")
    footer(d, page); return img


POSTS = [("post-1", aspect_what), ("post-2", aspect_flow), ("post-3", aspect_stack),
         ("post-4", aspect_journey), ("post-5", aspect_why)]

def main():
    OUT.mkdir(parents=True, exist_ok=True); CAR.mkdir(parents=True, exist_ok=True)
    # standalone posts (no page counter)
    for name, fn in POSTS:
        im = fn(None); assert im.size == (W, H), im.size
        im.save(OUT / f"{name}.png"); print("post ->", name)
    # carousel: cover + 5 + cta, with page counters
    seq = [cover] + [fn for _, fn in POSTS] + [cta]
    for i, fn in enumerate(seq, 1):
        im = fn(i); assert im.size == (W, H), im.size
        im.save(CAR / f"slide-{i:02d}.png"); print("slide ->", f"slide-{i:02d}.png")
    print("OK — content kit in", OUT)

if __name__ == "__main__":
    main()
