# ThreadPup — LinkedIn Content Kit (Scenario 3)

A week of LinkedIn visual content: **5 standalone infographics**, each explaining
a different aspect of the ThreadPup business, in **one consistent visual style** —
plus a **7-slide carousel** that bundles them (cover that earns the scroll + CTA close).

**Method:** Method B — branded PIL/Excalidraw-style template (`../build_kit.py`).
Chosen over AI generation specifically because the five posts must look like one
set: a template guarantees identical palette, typography, mascot, and footer.
AI image models have no seed and drift between images.

## Files
| File | Aspect |
|------|--------|
| `post-1.png` | What ThreadPup is — design-your-own, print-on-demand |
| `post-2.png` | How an order flows — click → pay → print → pack → deliver |
| `post-3.png` | The tech stack — Next.js · Vercel · Supabase · Stripe · Resend |
| `post-4.png` | The customer journey — discover → customize → buy → receive → repeat |
| `post-5.png` | Why it works — fast fulfillment, zero inventory risk, repeat buyers |
| `carousel/slide-01.png` | **Cover** — "How a custom-tee startup actually works" + Swipe → |
| `carousel/slide-02..06.png` | the 5 aspects (with `0X / 07` page counters) |
| `carousel/slide-07.png` | **CTA** — recap chips + "Save this…" + "Follow…" |
| `captions.md` | Mon–Fri post captions (hook + body + CTA + hashtags) + carousel caption |

All slides are **1080×1350** (LinkedIn 4:5 portrait). Rebuild: `py ../build_kit.py`.

> The earlier 4-slide `../carousel-output/` (order-flow teardown) is kept as a prior
> iteration / bonus. This kit is the Scenario 3 deliverable.
