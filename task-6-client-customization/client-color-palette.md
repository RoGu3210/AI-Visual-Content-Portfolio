# Client re-skin — "Nimbus" (Method B: palette customization)

Demonstrates Hour-6 **Method B**: change the brand palette in one place and the whole
diagram re-skins. Sample client **Nimbus** — a cool, modern SaaS brand (vs ThreadPup's warm
caramel/cream). The 3 functional categories stay clearly distinct, just re-hued.

## Nimbus brand
| Role | Hex |
|------|-----|
| Background | `#F6F8FB` (cool white) |
| Primary | `#4F46E5` (indigo) |
| Ink / text | `#1E293B` (slate) |
| Secondary text | `#475569` |

## Category re-hue (keeps 3 distinguishable)
| Category | ThreadPup | Nimbus |
|----------|-----------|--------|
| Customer-facing | warm blue | **indigo** (fill `#c7d2fe`, stroke `#4F46E5`) |
| Backend & fulfillment | green | **teal** (fill `#99f6e4`, stroke `#0d9488`) |
| Third-party APIs | orange | **rose** (fill `#fecdd3`, stroke `#e11d48`) |

## Full hex mapping (old → new)
Applied by [`reskin.py`](reskin.py) to `task-3-threadpup/architecture.excalidraw.json`:

```
# brand / neutral
#FFFDF9 -> #F6F8FB   #FFF3E8 -> #E9EDF6   #C68642 -> #4F46E5
#5B3A29 -> #1E293B   #8A5A30 -> #475569   #F2D2A9 -> #CBD5E1
# customer-facing (blue -> indigo)
#4dabf7 -> #818cf8   #1971c2 -> #4F46E5   #a5d8ff -> #c7d2fe
#dbe4ff -> #e0e7ff   #4a9eed -> #4F46E5   #155a9c -> #3730a3   #0b3d66 -> #312e81
# backend (green -> teal)
#51cf66 -> #2dd4bf   #2f9e44 -> #0d9488   #b2f2bb -> #99f6e4
#d3f9d8 -> #ccfbf1   #22c55e -> #0d9488   #14532d -> #115e59
# third-party (orange -> rose)
#ff922b -> #fb7185   #e8590c -> #e11d48   #ffd8a8 -> #fecdd3
#ffe8cc -> #ffe4e6   #9a3412 -> #9f1239
```

Run: `py reskin.py` → writes `architecture-nimbus.excalidraw.json`, then render it with
task-3's `render_preview.py --rough`. To re-skin for a real client, edit the mapping here +
in `reskin.py` and re-run — every element recolors automatically.
