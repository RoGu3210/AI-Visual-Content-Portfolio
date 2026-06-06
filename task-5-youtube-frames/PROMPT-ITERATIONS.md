# Task 2 — Expand the Pipeline: prompt-iteration log

**Goal:** turn the Hour-4 blog post (`task-2-prompt-carousel/references/blog-post.md`,
"Prompt Engineering Techniques") into a 5-frame **YouTube explainer pack**
(hook → problem → concept → example → summary), reusing the **task-1 Kie.ai
client** (`generate_infographic.py`, Nano Banana 2) instead of building the Node
`excalidraw-gen` project.

- Driver: [`generate_frames.py`](generate_frames.py) — imports the task-1 client, generates each frame at **16:9 / 2K / nano-banana-2**.
- Output: [`output-option-a/`](output-option-a/) — final `frame-01-hook.png … frame-05-summary.png`; the raw variations are kept in `output-option-a/_variations/` as evidence.
- QA: done by a fresh-context subagent (the main session was image-capped) — see [[image-qa-via-subagents]].

## What I tried (prompt-design decisions)
1. **5-frame narrative**, not 6 blog headings — a YouTube explainer wants a story arc (hook→problem→concept→example→summary), so I distilled the 6 techniques into: hook ("you're prompting AI wrong"), problem ("vague in, vague out"), concept (4 named techniques), example (chain-of-thought on a word problem), summary (4-item checklist + CTA).
2. **Deliberately short on-image text.** AI image models garble long/secondary text, so every prompt keeps text to a big headline + ≤4 short labels. Shared `STYLE` preamble enforces: "keep on-image text short; all text large, legible and spelled correctly."
3. **Consistent style token** across all 5 prompts (hand-drawn Excalidraw sketchnote, near-white paper, pastel accents, simple doodles, 16:9) so the pack looks like one set.
4. **2 variations per frame** as a hedge — generate twice, keep the cleaner one. Cheaper and faster than re-prompting blind.
5. **Model:** NB2 ($) for drafts/iteration. (Use `nano-banana-pro` for a final client cut — complex text/layout renders cleaner.)

## What failed
Even with short-text prompts, **2 of 10 variations garbled text** — the canonical Nano-Banana failure on *secondary* text:
- **frame-01 hook · v2** — invented gibberish caption pills at the bottom: *"Prom more / demriation"*, *"Untgiatet / unheibility"*, *"Denation promptiry"*. (Headline was fine; the model hallucinated extra captions.)
- **frame-05 summary · v1** — rendered a literal placeholder *"Call-to action"* and a misspelling *"learn howe!"* in the CTA box.
- **frame-04 example · v2** — text was spelled OK but the *logic* was muddled (a cupcake word-problem whose steps didn't read cleanly).

**Lesson:** the model is reliable on the single big headline and short labels, but the more secondary text you ask for (captions, CTAs, multi-step math), the more likely it garbles or hallucinates. The failures clustered exactly where a frame asked for extra small text.

## What worked — Round 1
- **Short-text + 2-variation + pick-the-clean-one** gave a usable, spelling-clean variation for **every** frame in round 1:
  | Frame | R1 pick | Why |
  |-------|--------|-----|
  | 01 hook | v1 | clean headline + "6 quick fixes" (v2 garbled) — *later improved in R2* |
  | 02 problem | **v1** ✅ | clean "Vague in, vague out", clear note→arrow→shrugging robot |
  | 03 concept | **v1** ✅ | four tidy boxes: Zero-shot / Few-shot / Chain-of-thought / Role |
  | 04 example | **v1** ✅ | "Maya has 7 apples… +4 = 11", correct math, clean 3-step reasoning |
  | 05 summary | v2 | clean checklist + spelled CTA (v1 had placeholder text) — *later improved in R2* |
- Independent QA scored the round-1 pack **9/10**.

## Round 2 — refining the two text-heavy frames (failure → fix)
The round-1 *discards* showed the failure lived in **secondary** text, so I re-prompted the
two worst-affected frames (hook, summary) to **explicitly cap the text**, regenerated 2
variations each, and compared old vs new:

| Frame | What round-1 produced | Prompt refinement | Round-2 result |
|---|---|---|---|
| 01 hook | a variation hallucinated 3 gibberish caption pills (*"Prom more / demriation"*) | added: *"ONLY two pieces of text … do NOT add any other captions, labels, sticky-notes or paragraphs"* | both variations clean **and** finally included the requested sparkles → **promoted to final** |
| 05 summary | leaked a literal template label *"RECAP & CALL-TO-ACTION"* + 3 wrong CTAs + stray "WRITER/EXPERT" tags | replaced vague *"a recap/CTA frame"* with *"ONE short call-to-action line: 'Try it on your next prompt' … no placeholder words"* | clean 4-item checklist + the single correct CTA, zero placeholder text → **promoted to final (decisive fix)** |

**The lesson that generalized:** vague directions like *"a recap/CTA frame"* invite the model
to invent — and garble — text. **Naming the exact strings and forbidding extra text** is what
fixed it. Frames 2–4 never needed a second round because their prompts already named every
piece of on-image text.

## Final selection (after the model rematch in Rounds 3–4 below)
- frame-01 hook → **Pro (hardened)** · frame-02 problem → **NB2 (R2)** · frame-03 concept → **Pro (hardened)** · frame-04 example → **Pro (hardened)** · frame-05 summary → **Pro (hardened)**
- All spelling-clean, math correct (7+4=11), consistent style. Frame-02 stayed NB2 because hardened-Pro still leaked one note caption.
- Raw variations preserved in `output-option-a/_variations/`: `round-1` (the _v1/_v2 set), `round-2`, `pro` (first Pro test), `pro-hardened` (Round 4).

## Round 3 — NB2 vs Nano-Banana-Pro (the "use Pro for finals" test)
The lesson says to use **nano-banana-pro** for final/client versions, so I regenerated all 5
frames at Pro (refined prompts, 1 variation each) and had a fresh agent compare them to the
NB2 finals on the decisive axis — **text quality**. Result was the opposite of expectation:

| Frame | NB2 | PRO | Winner |
|---|---|---|---|
| 01 hook | clean | clean | NB2 (tie; tidier 2-line layout) |
| 02 problem | clean | added off-spec caption *"Problem with lazy prompts"* | **NB2** |
| 03 concept | clean | hallucinated a meta-caption banner *"Clean concept-overview"* | **NB2** |
| 04 example | clean, `7+4=11` legible | math ok but buried the result: *"24 ÷ 2 = 🍪"* (icon over the numeral) | **NB2** |
| 05 summary | clean | placeholder *"Sample text"* inside a book icon | **NB2** |

**Verdict: kept the full NB2 pack.** Pro drew nicer linework but **hallucinated extra /
placeholder / meta text on 4 of 5 frames** — it "fills" space with invented captions, which
is exactly the failure mode this content can't afford. (Pro candidates archived in
`output-option-a/_variations/pro/`.)

**Lesson:** "newer / pricier model = cleaner output" is an assumption, not a fact — **verify
on your actual content**. For tightly-specified text frames, the model that best *obeys the
text constraints* wins, and here that was NB2 with the constrained round-2 prompts.

## Round 4 — Pro with hardened guardrails (the rematch)
Round 3's loss was *instruction-following*, not capability — Pro filled space with invented
text. So I added a **STRICT TEXT RULE** to every prompt (*"render ONLY the exact words
specified … no extra captions/banners/placeholders, never swap a number for an icon"*) and
pinned frame-04's exact problem + steps, then re-ran all 5 at Pro.

| Frame | hardened-Pro result | Winner |
|---|---|---|
| 01 hook | clean text, richer pencil linework | **Pro** |
| 02 problem | still leaked a note caption *"Tiny messy sticky-note prompt"* | NB2 |
| 03 concept | clean labels, no meta-banner this time | **Pro** |
| 04 example | the *exact* specified steps, digits (not icons), 7 + 4 = 11 | **Pro** |
| 05 summary | clean checklist + single CTA, bolder | **Pro** |

**Result: the guardrails flipped it — Pro now wins 4 of 5.** The lone holdout (frame-02) shows
the rule is strong but not absolute. **Final pack = 4 Pro-hardened frames + 1 NB2.**

**The real lesson (updated from Round 3):** Pro wasn't "worse" — it was *under-constrained*.
The cheaper model looked cleaner in Round 3 only because its simpler prompts gave it less room
to hallucinate. Give the stronger model **equally strict text constraints** and it wins on
craft. So: **constrain the prompt first, then judge the model.**

## If iterating further
- Re-roll frame-02 on Pro with an explicit "the note has NO words, only scribbles" line to try for an all-Pro pack.

## Cost
~**360 Kie credits** total — 12 key-check + 120 R1 (5×2 NB2) + 48 R2 (2×2 NB2) + 90 R3
(5×1 Pro) + 90 R4 (5×1 Pro-hardened) — ≈ $2–2.7. Final pack = 4 Pro-hardened + 1 NB2.
