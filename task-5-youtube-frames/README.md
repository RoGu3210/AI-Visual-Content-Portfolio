# Task 5 — YouTube Explainer Frames (Expand the Pipeline)

Hour-5 **Task 2**: a 5-frame YouTube explainer pack generated from the Hour-4 blog
post ("Prompt Engineering Techniques"), **reusing the task-1 Kie.ai pipeline**
(Nano Banana 2) rather than the Node `excalidraw-gen` tool.

## Deliverables
- `output-option-a/frame-01-hook.png … frame-05-summary.png` — the final pack (16:9, 2K)
- `output-option-a/_variations/` — both variations per frame (iteration evidence)
- [`PROMPT-ITERATIONS.md`](PROMPT-ITERATIONS.md) — **the required write-up**: what I tried, what failed (AI text-garble in 2 of 10 variations), what worked
- [`generate_frames.py`](generate_frames.py) — the driver

## Regenerate
```
py generate_frames.py --test                       # 1 frame, key check
py generate_frames.py --variations 2               # all 5 frames x 2 variations (NB2)
py generate_frames.py --frames 1,5 -v 2            # re-roll specific frames
py generate_frames.py --model nano-banana-pro -v 1 # Pro pass
py generate_frames.py ... --out output-option-a/_x # send to a subfolder
```
Reads `KIE_API_KEY` from `../task-1-kie-infographics/.env`. Output → `output-option-a/`.
**Note on model:** Pro only wins if you constrain its text. With loose prompts NB2 beat Pro
(Pro hallucinated captions/placeholders — Round 3); after adding a strict "render only the
exact text" rule, **Pro won 4 of 5** (Round 4). Final pack = 4 Pro-hardened frames + 1 NB2.
Lesson: constrain the prompt first, then judge the model. See PROMPT-ITERATIONS.md.
