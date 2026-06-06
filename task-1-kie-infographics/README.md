# Workflow Infographic

Turn text content into professional **hand-drawn (Excalidraw-style) infographic
images** using **Nano Banana 2 on [Kie.ai](https://kie.ai)** — driven from inside
Claude Code. No design skills required.

## How it fits together

```
You: "/infographic-generator smartwatches"
        │
        ▼
Claude (the skill)            generate_infographic.py            Kie.ai
─────────────────────         ──────────────────────            ──────────────
 1. search the web        →                                  
 2. read & summarize a    →   takes the finished prompt   →   createTask
    source into 3–5           creates N parallel tasks         (nano-banana-2)
    short sections            polls until each is done    ←   recordInfo
 3. craft an Excalidraw    →  downloads the images        ←   result image URL
    style prompt
 4. run the script         →  saves PNGs to generated/
 5. show & curate results
```

**Division of labor:** Claude does the research, summarizing, and prompt-writing.
The script does *only* the Kie.ai API work (create → poll → download). The API
returns **one image per request**, so "2 variations" = 2 requests run in parallel.

## Setup (one time)

1. **Python** — uses the `py` launcher (Python 3.12 is installed). Install the one
   dependency (already present here, but for portability):
   ```powershell
   py -m pip install -r requirements.txt
   ```
2. **API key** — get one at <https://kie.ai/api-key>, then:
   ```powershell
   Copy-Item .env.example .env
   ```
   Open `.env` and paste your key:
   ```
   KIE_API_KEY=sk-...your real key...
   ```
   `.env` is gitignored — keep your key out of any commit. The key is never printed.

## Usage

### A) Via the skill (recommended)
In Claude Code, run:
```
/infographic-generator <topic, URL, or "turn this content into an infographic">
```
Claude finds a source (or uses what you give it), summarizes it, builds the prompt,
runs the generator, and shows you the results to curate.

### B) Direct from the terminal
If you already have prompt text:
```powershell
py generate_infographic.py --prompt-file prompt.txt --name my_infographic --variations 2
```
Or inline:
```powershell
py generate_infographic.py --prompt "a hand-drawn Excalidraw infographic about ..." --variations 2
```

**Common flags** (`py generate_infographic.py --help` for all):

| Flag | Default | Meaning |
|------|---------|---------|
| `--prompt` / `--prompt-file` | — | the image prompt (one is required) |
| `--name` | `infographic` | base filename → `generated/<name>_v1.png` |
| `--variations` | `2` | number of images (parallel requests) |
| `--aspect-ratio` | `3:4` | portrait; also `2:3`, `9:16`; landscape `16:9` |
| `--resolution` | `2K` | `1K` ≈ $0.04, `2K` ≈ $0.06, `4K` ≈ $0.09 / image |
| `--output-format` | `png` | `png` or `jpg` |
| `--out` | `generated` | output directory |
| `--timeout` | `300` | max seconds to wait per variation |

Outputs land in [generated/](generated/) as `<name>_v1.png`, `<name>_v2.png`, …

## How this maps to the lesson

| Lesson step | Where it lives |
|-------------|----------------|
| 1 — Find a website & generate | The skill (search + fetch) → the script (Kie.ai call) |
| 2 — Write strong prompts | The Excalidraw **prompt template** in `SKILL.md` |
| 3 — Review & curate | Skill step 5; you pick the best `_vN.png` and iterate |
| 4 — Organize files | Everything saved to `generated/`, consistent `<name>_vN` naming |
| 5 — Troubleshooting | The table below |
| 6 — Quick reference | "Best practices" below |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `401 Unauthorized` | key missing/invalid | check `KIE_API_KEY` in `.env` |
| `402 Payment Required` | out of credits | top up at <https://kie.ai> |
| `429 Too Many Requests` | rate limit (~20 creates / 10s) | script auto-backs-off; just rerun if it persists |
| Task `fail` state | model couldn't render the prompt | simplify: fewer sections, shorter text, retry |
| Text unreadable / crowded | too much copy on the image | cut sections, shorten bullets, or `--resolution 4K` |
| Image link "expired" | Kie.ai URLs expire ~24h | N/A — the script downloads immediately |
| Timed out | slow generation | increase `--timeout` |

## Best practices (quick reference)
- **Clarity & structure first** — a clear title + 3–5 short sections beats a wall of text.
- **Generate multiple variations** and pick the best.
- **Iterate** — refine the prompt and regenerate; rarely perfect on the first try.
- **Keep outputs organized** in `generated/` with consistent names for easy reuse in
  presentations, blogs, or social posts.

---
*Built on Kie.ai Nano Banana 2 · Runs locally · No cloud setup required.*
