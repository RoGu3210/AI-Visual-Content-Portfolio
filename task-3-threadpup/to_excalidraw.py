#!/usr/bin/env python3
"""
to_excalidraw.py — convert a saved scene spec (the simplified element format used
by the Excalidraw MCP create_view, stored in our *.excalidraw.json files) into a
real, importable .excalidraw scene file you can load via Excalidraw > Menu > Open.

Usage:
    py to_excalidraw.py architecture.excalidraw.json customer-journey.excalidraw.json
Writes architecture.excalidraw, customer-journey.excalidraw next to each input.
"""
from __future__ import annotations
import json
import math
import random
import string
import sys
from pathlib import Path

random.seed(7)  # deterministic output across runs


def _line_count(text: str, font_size: int, usable_w: float) -> int:
    """Estimate how many rendered lines `text` needs at `font_size` inside
    `usable_w` px, honoring explicit newlines plus word-wrap."""
    lines = 0
    for seg in text.split("\n"):
        w = len(seg) * font_size * 0.55
        lines += max(1, math.ceil(w / usable_w)) if w > 0 else 1
    return max(1, lines)


def rid() -> str:
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(16))


def nonce() -> int:
    return random.randint(1, 2**31 - 1)


def _base(el: dict) -> dict:
    return {
        "id": el.get("id") or rid(),
        "type": el["type"],
        "x": el["x"],
        "y": el["y"],
        "width": el.get("width", 0),
        "height": el.get("height", 0),
        "angle": 0,
        "strokeColor": el.get("strokeColor", "#1e1e1e"),
        "backgroundColor": el.get("backgroundColor", "transparent"),
        "fillStyle": el.get("fillStyle", "solid"),
        "strokeWidth": el.get("strokeWidth", 2),
        "strokeStyle": el.get("strokeStyle", "solid"),
        "roughness": el.get("roughness", 1),
        "opacity": el.get("opacity", 100),
        "groupIds": [],
        "frameId": None,
        "roundness": el.get("roundness", None),
        "seed": nonce(),
        "version": 1,
        "versionNonce": nonce(),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False,
    }


def _text(tid, text, fs, x, y, w, h, *, container=None, align="left", valign="top", color="#1e1e1e"):
    return {
        "id": tid, "type": "text", "x": x, "y": y, "width": w, "height": h,
        "angle": 0, "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
        "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
        "roundness": None, "seed": nonce(), "version": 1, "versionNonce": nonce(),
        "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
        "locked": False, "text": text, "fontSize": fs, "fontFamily": 1,
        "textAlign": align, "verticalAlign": valign, "containerId": container,
        "originalText": text, "lineHeight": 1.25, "autoResize": True,
    }


def convert(elements: list) -> list:
    out: list = []
    for el in elements:
        t = el.get("type")
        if t == "cameraUpdate":
            continue
        if t in ("rectangle", "ellipse", "diamond"):
            shape = _base(el)
            lbl = el.get("label")
            if lbl:
                tid = rid()
                shape["boundElements"] = [{"type": "text", "id": tid}]
                fs = lbl.get("fontSize", 16)
                usable_w = max(10, shape["width"] - 16)
                nlines = _line_count(lbl["text"], fs, usable_w)
                text_h = nlines * fs * 1.25
                # grow the container if the wrapped label is taller than it
                if shape["height"] < text_h + 16:
                    shape["height"] = round(text_h + 16)
                ty = shape["y"] + (shape["height"] - text_h) / 2
                out.append(shape)
                out.append(_text(
                    tid, lbl["text"], fs,
                    shape["x"] + 8, ty,
                    usable_w, text_h,
                    container=shape["id"], align="center", valign="middle",
                    color=lbl.get("strokeColor", "#1e1e1e"),
                ))
            else:
                out.append(shape)
        elif t == "text":
            b = _base(el)
            fs = el.get("fontSize", 16)
            _maxline = max((len(s) for s in el["text"].split("\n")), default=0)
            _nlines = max(1, el["text"].count("\n") + 1)
            b.update({
                "width": max(10, int(_maxline * fs * 0.55)),
                "height": fs * 1.25 * _nlines, "text": el["text"], "fontSize": fs,
                "fontFamily": 1, "textAlign": "left", "verticalAlign": "top",
                "containerId": None, "originalText": el["text"],
                "lineHeight": 1.25, "autoResize": True,
            })
            out.append(b)
        elif t in ("arrow", "line"):
            b = _base(el)
            b.update({
                "points": el.get("points", [[0, 0], [el.get("width", 0), el.get("height", 0)]]),
                "lastCommittedPoint": None, "startBinding": None, "endBinding": None,
                "startArrowhead": el.get("startArrowhead", None),
                "endArrowhead": el.get("endArrowhead", "arrow" if t == "arrow" else None),
                "elbowed": False,
            })
            lbl = el.get("label")
            if lbl:
                tid = rid()
                b["boundElements"] = [{"type": "text", "id": tid}]
                fs = lbl.get("fontSize", 14)
                out.append(b)
                out.append(_text(
                    tid, lbl["text"], fs,
                    b["x"], b["y"] - fs, max(10, int(len(lbl["text"]) * fs * 0.55)), fs * 1.25,
                    container=b["id"], align="center", valign="middle",
                ))
            else:
                out.append(b)
    return out


def main(argv: list) -> int:
    if not argv:
        sys.exit("Usage: py to_excalidraw.py <spec.excalidraw.json> [...]")
    for arg in argv:
        src = Path(arg)
        spec = json.loads(src.read_text(encoding="utf-8"))
        scene = {
            "type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
            "elements": convert(spec.get("elements", [])),
            "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
            "files": {},
        }
        out = src.with_name(src.name.replace(".excalidraw.json", ".excalidraw"))
        out.write_text(json.dumps(scene, indent=1), encoding="utf-8")
        print(f"wrote {out.name}  ({len(scene['elements'])} elements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
