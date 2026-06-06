# YouTube Explainer Pack — "Stop Prompting AI Wrong: 4 Techniques"

A complete, ready-to-record explainer pack: **script + thumbnail + hook + the 5
infographic frames**, packaged in one folder. (Scenario 1 deliverable.)

**Method used:** Method A — Kie.ai Nano Banana 2 AI image generation (the 5
frames). See `../PROMPT-ITERATIONS.md` for the full prompt-engineering /
model-comparison write-up and `../_variations/` for iteration evidence.

## Contents
| File | What it is |
|------|------------|
| `script.md` | 3-minute narration (~450 words) with timecodes, mapped to the 5 frames |
| `hook.txt` | Spoken + on-screen hook, title options, description, pinned comment |
| `thumbnail.png` | YouTube thumbnail, **1280×720** |
| `frame-01-hook_1080p.png` | Visual moment 1 — Hook |
| `frame-02-problem_1080p.png` | Visual moment 2 — Problem ("vague in, vague out") |
| `frame-03-concept_1080p.png` | Visual moment 3 — 4 techniques |
| `frame-04-example_1080p.png` | Visual moment 4 — Chain-of-thought example |
| `frame-05-summary_1080p.png` | Visual moment 5 — Checklist + CTA |

## The 5 key visual moments
1. **Hook** — "You're prompting AI wrong" + 4 quick fixes
2. **Problem** — Vague in, vague out
3. **Concept** — Zero-shot · Few-shot · Chain-of-thought · Role
4. **Example** — "Maya has 7 apples … +4 = 11", reasoned step by step
5. **Summary** — 4-item checklist + CTA "Try it on your next prompt"

## Specs
- Frames exported at **exactly 1920×1080** (center-cropped from the 2752×1536
  source to 16:9, then Lanczos-resized — no distortion). Rebuild: `py ../build_pack.py`.
- Thumbnail rendered crisp from scratch (1280×720) for legible text at feed size.
