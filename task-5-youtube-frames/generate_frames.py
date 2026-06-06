#!/usr/bin/env python3
"""Expand the Pipeline (Hour-5 Task 2): generate a 5-frame YouTube explainer pack
from the Hour-4 blog post ("Prompt Engineering Techniques"), reusing the task-1
Kie.ai client (Nano Banana 2). Frames: hook -> problem -> concept -> example ->
summary, 16:9 widescreen.

Usage:
  py generate_frames.py --test                 # 1 frame, 1 variation (key check)
  py generate_frames.py --variations 2         # all 5 frames, 2 variations each
  py generate_frames.py --frames 3,4 -v 1      # regenerate specific frames
Prompts live in PROMPTS below; edit + rerun to iterate. Output -> output-option-a/.
"""
from __future__ import annotations
import argparse, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

T1 = Path(__file__).resolve().parent.parent / "task-1-kie-infographics"
sys.path.insert(0, str(T1))
import generate_infographic as gi  # noqa: E402  reuse the proven client

OUT = Path(__file__).resolve().parent / "output-option-a"

STYLE = (
    "Clean hand-drawn Excalidraw sketchnote style, 16:9 widescreen, plain near-white "
    "paper background. Bold hand-lettered text, soft pastel accents (muted blue, green, "
    "coral, warm yellow), simple doodle icons, generous white space, modern and "
    "uncluttered. Keep on-image text short; all text large, legible and spelled correctly. "
    "STRICT TEXT RULE: render ONLY the exact words specified for this frame — add no other "
    "captions, labels, banners, taglines, watermarks or placeholder text, never write filler "
    "like 'sample text' and never describe the image in words, and never replace a required "
    "number or word with an icon."
)

PROMPTS = {
    1: ("hook", STYLE + " ONLY two pieces of text on the whole image: a big centered headline "
        "\"You're prompting AI wrong\" and a smaller line beneath it \"6 quick fixes\". Do NOT "
        "add any other captions, labels, sticky-notes or paragraphs anywhere. Doodles: a "
        "puzzled person on the left and a friendly waving robot on the right, a few sparkles, "
        "lots of empty space. A punchy YouTube hook frame."),
    2: ("problem", STYLE + " Top headline: \"Vague in, vague out\". On the left a tiny messy "
        "sticky-note prompt; a big hand-drawn arrow pointing right; on the right a robot "
        "shrugging with floating question marks and a small red squiggle. Shows the problem "
        "with lazy prompts."),
    3: ("concept", STYLE + " Top headline: \"Prompt engineering\". Four labeled rounded boxes "
        "in a row, each with a small doodle icon, reading: \"Zero-shot\", \"Few-shot\", "
        "\"Chain-of-thought\", \"Role\". Thin arrows linking them left to right. A clean "
        "concept-overview frame."),
    4: ("example", STYLE + " Top headline: \"Show your steps\". A box on the left contains "
        "exactly this word problem: \"Maya has 7 apples. She buys 4 more. How many now?\". A "
        "big arrow points right to three short numbered steps: \"1. Start with 7\", \"2. Add "
        "4\", \"3. 7 + 4 = 11\", then a final answer \"Maya has 11 apples\" with a green check "
        "mark. Write all numbers as digits; do not replace any number with an icon."),
    5: ("summary", STYLE + " Top headline: \"Prompt like a pro\". A tidy checklist of exactly "
        "four ticked items: \"Give examples\", \"Show your steps\", \"Assign a role\", \"Be "
        "specific\". Below the checklist, ONE short call-to-action line: \"Try it on your next "
        "prompt\". A friendly robot giving a thumbs-up in the corner. No other text and no "
        "placeholder words anywhere."),
}

def one(n: int, name: str, prompt: str, k: int, api_key: str) -> dict:
    dest = OUT / f"frame-{n:02d}-{name}_v{k}.png"
    rec = {"frame": n, "name": name, "var": k, "path": str(dest), "ok": False}
    try:
        tid = gi.create_task(prompt, "16:9", "2K", "png", api_key)
        data = gi.poll_task(tid, api_key, timeout=300, interval=3.0)
        size = gi.download_image(gi.extract_url(data), dest)
        rec.update(ok=True, bytes=size, credits=data.get("creditsConsumed"))
    except SystemExit as e:
        rec["error"] = f"auth/credit: {e}"
    except Exception as e:  # noqa: BLE001
        rec["error"] = str(e)
    return rec

def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--variations", "-v", type=int, default=2)
    p.add_argument("--frames", help="comma list of frame numbers, e.g. 3,4 (default all)")
    p.add_argument("--test", action="store_true", help="frame 1, 1 variation only")
    p.add_argument("--out", help="override output directory")
    p.add_argument("--model", default="nano-banana-2", help="nano-banana-2 (draft) or nano-banana-pro (final)")
    a = p.parse_args(argv)
    global OUT
    if a.out:
        OUT = Path(a.out)
    gi.MODEL = a.model  # the task-1 client reads MODEL when building the request
    OUT.mkdir(parents=True, exist_ok=True)
    gi.load_env()
    api_key = gi.get_api_key()
    frames = [1] if a.test else (
        [int(x) for x in a.frames.split(",")] if a.frames else sorted(PROMPTS))
    variations = 1 if a.test else a.variations
    jobs = [(n, PROMPTS[n][0], PROMPTS[n][1], k) for n in frames for k in range(1, variations+1)]
    print(f"Generating {len(jobs)} image(s) [16:9, 2K, {a.model}] -> {OUT}/\n")
    start = time.monotonic(); results = []
    with ThreadPoolExecutor(max_workers=min(len(jobs), 8)) as pool:
        futs = {pool.submit(one, n, nm, pr, k, api_key): (n, k) for (n, nm, pr, k) in jobs}
        for f in as_completed(futs):
            r = f.result(); results.append(r)
            tag = "OK  " if r["ok"] else "FAIL"
            print(f"  [{tag}] frame-{r['frame']:02d}-{r['name']}_v{r['var']}"
                  + (f"  ({r['bytes']/1024:,.0f} KB)" if r["ok"] else f"  {r.get('error')}"))
    ok = [r for r in results if r["ok"]]
    cr = sum(r.get("credits") or 0 for r in ok)
    print(f"\n{len(ok)}/{len(results)} ok in {time.monotonic()-start:.0f}s"
          + (f"  |  {cr} credits" if cr else ""))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
