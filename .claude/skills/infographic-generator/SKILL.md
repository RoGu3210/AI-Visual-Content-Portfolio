---
name: infographic-generator
description: Generate hand-drawn (Excalidraw-style) infographic images from a topic or supplied content using Kie.ai Nano Banana 2. Use when the user wants to create or visualize an infographic, turn a website's or document's content into a graphic, or runs /infographic-generator. The user supplies a topic (or content/URL); you research it, summarize it into a few visual sections, craft a hand-drawn-style prompt, and call generate_infographic.py to produce the images.
---

# Infographic Generator (Kie.ai Nano Banana 2)

Turn a topic, a URL, or pasted content into a professional **hand-drawn,
Excalidraw-style infographic**. You (Claude) do the research and prompt-crafting;
the local script `generate_infographic.py` handles the Kie.ai API call, polling,
and downloading.

## When to use
- "Make an infographic about X"
- "Turn this page / article / doc into an infographic"
- `/infographic-generator <topic-or-url>`

## Inputs you need before generating
- **Topic or content.** If the user gave a topic, you'll find a source. If they
  gave a URL or pasted text, use that directly — skip the search.
- **Defaults** (override only if the user asks): portrait `3:4`, `2K`,
  `png`, `2` variations.

## Workflow

### 1. Find a source (skip if the user supplied content/URL)
- Use `WebSearch` for the topic; pick **one** content-rich page — a product page,
  company/overview page, or a focused blog post. Avoid thin or login-walled pages.
- Tell the user which source you picked.

### 2. Extract the content
- Use `WebFetch` on the chosen page.
- Distill into **3–5 sections** max. Each section = a short **heading** + **2–3
  supporting points** (a few words each, not sentences). Pick a clear **title**.
- Fewer, shorter pieces beat dense text — image models render short text far more
  legibly. If the topic is big, narrow it.

### 3. Craft the prompt
- Fill in the **prompt template** below with the title and sections.
- Write the finished prompt to a scratch file named `prompt_<slug>.txt` inside the
  `task-1-kie-infographics/` folder (long prompts are hard to pass on the PowerShell
  command line, and `prompt_*.txt` is gitignored). Use `Write` for this.

### 4. Generate
Run from the task-1 folder (`c:\Users\Mark Abe\Desktop\Workflow Infographic\task-1-kie-infographics`):

```
py generate_infographic.py --prompt-file prompt_<slug>.txt --name <slug> --variations 2 --aspect-ratio 3:4 --resolution 2K --output-format png --out generated
```
(Or from the project root, prefix the script path: `py task-1-kie-infographics/generate_infographic.py ... --out task-1-kie-infographics/generated`.)

- The script auto-loads `KIE_API_KEY` from `.env`. Confirm `.env` has a real key
  before the first run; if missing, point the user to `.env.example` and
  https://kie.ai/api-key.
- Each variation costs ~$0.06 at 2K. Confirm with the user before going above 3.

### 5. Review & curate
- List the saved files in `generated/` (`<slug>_v1.png`, `<slug>_v2.png`).
- Briefly assess readability, flow, and whether sections look overcrowded.
- Offer to **refine and regenerate**: shorten copy, drop a section, switch
  orientation, or bump `--resolution 4K` for sharper text. Iterate — don't expect
  a perfect first pass.

## Prompt template (hand-drawn / Excalidraw style)
Fill the ALL-CAPS placeholders, then delete any unused section lines.

```
A clean, professional hand-drawn infographic in the Excalidraw sketchnote style,
on a plain near-white background. Rough hand-sketched line work, slightly wobbly
rounded rectangles and boxes, hand-drawn arrows and connectors linking ideas, and
soft pastel accent colors (muted blue, green, coral, yellow) used sparingly. Casual
hand-lettered headings with a clean, evenly legible body font; all text spelled
correctly and large enough to read. Portrait orientation, generous white space,
clear top-to-bottom visual hierarchy — NOT crowded.

Title at the top: "TITLE_HERE"

Sections (each in its own sketched box, connected with arrows to show flow):
1. SECTION_1_HEADING — point, point, point
2. SECTION_2_HEADING — point, point, point
3. SECTION_3_HEADING — point, point, point
4. SECTION_4_HEADING — point, point, point

Add small, simple doodle icons next to each section that match its meaning, and one
optional friendly mascot doodle in a corner. Minimal, modern, uncluttered — like a
designer's clean whiteboard sketch.
```

### Style guidance
- **Keep total on-image text small** — headings + 2-3 short bullets per section.
- Name the **layout/flow** explicitly (top-to-bottom, arrows between boxes, or a
  timeline) so sections connect logically.
- Re-state "all text spelled correctly and readable" — it measurably helps.

## Defaults & flags
| Flag | Default | Notes |
|------|---------|-------|
| `--variations` | 2 | parallel requests; 1 image each |
| `--aspect-ratio` | 3:4 | portrait; also 2:3 / 9:16. Landscape: 16:9 |
| `--resolution` | 2K | 1K cheapest, 4K sharpest text |
| `--output-format` | png | or jpg |
| `--out` | generated | output folder |

## Troubleshooting (quick)
- **401** → key missing/invalid in `.env`. **402** → out of credits (top up at kie.ai).
- **429** → rate limit; the script backs off automatically, just rerun if needed.
- **`fail` state** → simplify the prompt (fewer sections, shorter text) and retry.
- **Text unreadable / crowded** → cut sections, shorten copy, or `--resolution 4K`.
- Full guide: see `README.md`.
