# Task 6 — Customizing for Clients (Method B demo)

Hands-on demo of the Hour-6 lecture's **Method B — Color Palette Customization**: change the
brand palette in one place and the whole diagram re-skins, automatically, with no layout work.

## What this shows
The ThreadPup **system-architecture** diagram, re-skinned from its warm ThreadPup brand
(cream / caramel / blue-green-orange) to a sample client brand **"Nimbus"** (cool white /
slate / indigo-teal-rose) — **colors only**; layout, text, icons, and the legend↔zone
mapping are untouched.

| | Brand | Look |
|---|---|---|
| Before | ThreadPup | `../task-3-threadpup/architecture.png` (warm) |
| After | Nimbus (client) | [`architecture-nimbus.png`](architecture-nimbus.png) (cool) |

Independently QA'd: palette fully swapped, the 3 functional categories stay clearly distinct
(customer-facing = indigo, backend = teal, third-party = rose), legend still matches the
zones/cards, all text legible, **no leftover warm colors** (65 color values remapped across
46 elements).

## Files
- [`client-color-palette.md`](client-color-palette.md) — the Nimbus brand + full old→new hex mapping (the analog of editing `references/color-palette.md`)
- [`reskin.py`](reskin.py) — applies the mapping to `task-3-threadpup/architecture.excalidraw.json`
- `architecture-nimbus.excalidraw.json` — re-skinned, editable spec
- `architecture-nimbus.png` — the client deliverable (2400×1404, hand-drawn render)

## Re-skin for a real client
1. Edit the `PALETTE` map in `reskin.py` (and document it in `client-color-palette.md`) with the client's hexes.
2. `py reskin.py` → writes `architecture-<client>.excalidraw.json`.
3. `py ../task-3-threadpup/render_preview.py architecture-<client>.excalidraw.json --rough --scale 2 --out architecture-<client>.png`

Every element recolors automatically — that's the Method B promise. (Method A, swapping the
illustration *style*/mascot via reference images + `generate.ts`, was not done — that's the
AI-generation tool's customization layer; this demo covers the palette half.)
