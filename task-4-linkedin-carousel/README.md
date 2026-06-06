# ThreadPup → LinkedIn Carousel

A ready-to-post **LinkedIn carousel** (4 slides, **1080×1350**, 4:5 portrait) built from
the ThreadPup infographics in [`../task-3-threadpup/`](../task-3-threadpup/).

## The deck → `carousel-output/`
Upload these in order as a LinkedIn document/carousel:

| File | Slide |
|------|-------|
| `slide-01.png` | **Cover / hook** — "What happens after you click 'Buy'?" + mascot + Swipe → |
| `slide-02.png` | **System Architecture** — the diagram + a feed-legible "stack by layer" summary |
| `slide-03.png` | **Customer Journey** — all 12 stages as a portrait 2-column snake |
| `slide-04.png` | **CTA** — stack chips + "Save this…" + "Follow for more" |

All slides are exactly 1080×1350.

## How it's built
- `build_carousel.py` — composes the 4 slides (clean branded chrome: number pill,
  footer wordmark + dog mascot; diagram slides are diagram-dominant so the diagram's
  own header is the title — no duplicate chrome titles). Run: `py build_carousel.py`
- `journey-carousel.excalidraw.json` — a **portrait** rebuild of the journey (2-column
  snake) made specifically for the carousel; the wide horizontal timeline in task-3 is
  illegible when shrunk to portrait width. Render with task-3's
  `render_preview.py … --rough --scale 2 --out journey-carousel.png`.
- `journey-carousel.png` — rendered source used by slide 3.
- Source diagrams: `../task-3-threadpup/architecture.png` (used directly on slide 2).

To regenerate everything: re-render `journey-carousel.png`, then `py build_carousel.py`.

## Quality
Reviewed across **3 adversarial multi-agent QA passes** (slides audited by fresh-context
agents for mobile-thumbnail legibility, safe margins, overflow, balance, branding).
Rev-1 problems (illegible diagram labels, dead space, duplicate titles, no hook) were all
fixed in rev-2; final scores **9 / 9 / 9 / 8**, verdict **ready to post**, no must-fixes.

> Note: the PNGs are clean hand-drawn-style renders from the project tooling. For the
> exact Excalidraw look on the embedded diagrams, re-export those from Excalidraw; the
> carousel chrome/layout is produced by `build_carousel.py`.
