#!/usr/bin/env python3
"""Method B demo — palette customization. Remap the ThreadPup architecture diagram's
colors to a client palette ("Nimbus") in one place; every element recolors automatically.
Run: py reskin.py   ->  architecture-nimbus.excalidraw.json
Then render: py ../task-3-threadpup/render_preview.py architecture-nimbus.excalidraw.json --rough --scale 2 --out architecture-nimbus.png
"""
import json
from pathlib import Path

# old -> new (keys lowercased; matching is case-insensitive)
PALETTE = {
    # brand / neutral
    "#fffdf9": "#F6F8FB", "#fff3e8": "#E9EDF6", "#c68642": "#4F46E5",
    "#5b3a29": "#1E293B", "#8a5a30": "#475569", "#f2d2a9": "#CBD5E1",
    # customer-facing: blue -> indigo
    "#4dabf7": "#818cf8", "#1971c2": "#4F46E5", "#a5d8ff": "#c7d2fe",
    "#dbe4ff": "#e0e7ff", "#4a9eed": "#4F46E5", "#155a9c": "#3730a3", "#0b3d66": "#312e81",
    # backend: green -> teal
    "#51cf66": "#2dd4bf", "#2f9e44": "#0d9488", "#b2f2bb": "#99f6e4",
    "#d3f9d8": "#ccfbf1", "#22c55e": "#0d9488", "#14532d": "#115e59",
    # third-party: orange -> rose
    "#ff922b": "#fb7185", "#e8590c": "#e11d48", "#ffd8a8": "#fecdd3",
    "#ffe8cc": "#ffe4e6", "#9a3412": "#9f1239",
}

def remap(c, stats):
    if isinstance(c, str) and c.lower() in PALETTE:
        stats[0] += 1
        return PALETTE[c.lower()]
    return c

def main():
    src = Path(__file__).resolve().parent.parent / "task-3-threadpup" / "architecture.excalidraw.json"
    spec = json.loads(src.read_text(encoding="utf-8"))
    stats = [0]
    for el in spec.get("elements", []):
        for k in ("backgroundColor", "strokeColor"):
            if k in el:
                el[k] = remap(el[k], stats)
        lbl = el.get("label")
        if isinstance(lbl, dict) and "strokeColor" in lbl:
            lbl["strokeColor"] = remap(lbl["strokeColor"], stats)
    spec["title"] = spec.get("title", "ThreadPup System Architecture") + " — Nimbus client re-skin"
    spec["note"] = "Method B palette customization: ThreadPup palette remapped to the Nimbus brand (slate + indigo/teal/rose) via reskin.py. Functional 3-category color-coding preserved (customer-facing=indigo, backend=teal, third-party=rose)."
    out = Path(__file__).resolve().parent / "architecture-nimbus.excalidraw.json"
    out.write_text(json.dumps(spec, indent=1), encoding="utf-8")
    print(f"wrote {out.name}  ({stats[0]} color values remapped across {len(spec['elements'])} elements)")

if __name__ == "__main__":
    main()
