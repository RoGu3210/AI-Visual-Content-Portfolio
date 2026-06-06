#!/usr/bin/env python3
"""make_diagrams.py — build the two NEW ThreadPup Scenario-2 diagrams as scene
specs in the same simplified element format as architecture.excalidraw.json.

Emits:
  deployment-pipeline.excalidraw.json   — GitHub -> Vercel CI/CD (Method B)
  data-flow.draft.excalidraw.json        — rough v1 (process evidence / "Excalidraw Draft")
  data-flow.excalidraw.json              — polished order data-flow (status by status)

Then feed each through to_excalidraw.py (-> .excalidraw) and render_preview.py (-> .png).
Layouts use generous gaps and >=14px floating-label clearance (Virgil renders wide).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent

# ---- brand / category palette (matches architecture.excalidraw.json) ----
BLUE   = ("#a5d8ff", "#1971c2", "#0b3d66")   # customer-facing
GREEN  = ("#b2f2bb", "#2f9e44", "#14532d")   # backend / CI
ORANGE = ("#ffd8a8", "#e8590c", "#9a3412")   # third-party / deploy
BARK = "#5B3A29"; CARAMEL = "#C68642"; BG = "#FFFDF9"; HDR = "#FFF3E8"


# ---------------- element helpers ----------------
def card(cid, x, y, w, h, palette, text, fs=15):
    f, s, lc = palette
    return {"type": "rectangle", "id": cid, "x": x, "y": y, "width": w, "height": h,
            "roundness": {"type": 3}, "backgroundColor": f, "fillStyle": "solid",
            "strokeColor": s, "strokeWidth": 2,
            "label": {"text": text, "fontSize": fs, "strokeColor": lc}}

def box(cid, x, y, w, h, fill, stroke, text=None, fs=15, lc=BARK, op=100):
    e = {"type": "rectangle", "id": cid, "x": x, "y": y, "width": w, "height": h,
         "roundness": {"type": 3}, "backgroundColor": fill, "fillStyle": "solid",
         "strokeColor": stroke, "strokeWidth": 2, "opacity": op}
    if text is not None:
        e["label"] = {"text": text, "fontSize": fs, "strokeColor": lc}
    return e

def txt(tid, x, y, s, fs=13, color=BARK):
    return {"type": "text", "id": tid, "x": x, "y": y, "text": s,
            "fontSize": fs, "strokeColor": color}

def arrow(aid, x, y, pts, color=BARK, dashed=False, start=False, end=True, sw=2):
    e = {"type": "arrow", "id": aid, "x": x, "y": y,
         "width": max(abs(p[0]) for p in pts), "height": max(abs(p[1]) for p in pts),
         "points": pts, "strokeColor": color, "strokeWidth": sw,
         "endArrowhead": "arrow" if end else None}
    if dashed: e["strokeStyle"] = "dashed"
    if start: e["startArrowhead"] = "arrow"
    return e

def mascot(ox, oy):
    o = [(0,0,18,26,BARK),(38,0,18,26,BARK),(6,6,44,40,"#F2D2A9"),
         (18,20,6,6,"#1e1e1e"),(34,20,6,6,"#1e1e1e"),(24,30,9,6,"#1e1e1e")]
    out = []
    for i,(dx,dy,w,h,c) in enumerate(o):
        out.append({"type":"ellipse","id":f"m{i}","x":ox+dx,"y":oy+dy,"width":w,"height":h,
                    "backgroundColor":c,"fillStyle":"solid","strokeColor":BARK if i<3 else "#1e1e1e",
                    "strokeWidth":2 if i<3 else 1})
    return out

def header(title, sub, hw, legend):
    els = [
        {"type":"rectangle","id":"hdr","x":40,"y":24,"width":hw,"height":92,"roundness":{"type":3},
         "backgroundColor":HDR,"fillStyle":"solid","strokeColor":CARAMEL,"strokeWidth":2},
        txt("title",150,40,title,30,BARK),
        txt("sub",150,82,sub,15,"#8A5A30"),
    ]
    els += mascot(56,42)
    lx = 40 + hw - 250
    sw = [("#4dabf7","#1971c2"),("#51cf66","#2f9e44"),("#ff922b","#e8590c")]
    for i,(lbl,(f,s)) in enumerate(zip(legend, sw)):
        y = 40 + i*26
        els.append({"type":"rectangle","id":f"lg{i}","x":lx,"y":y,"width":22,"height":16,
                    "backgroundColor":f,"fillStyle":"solid","strokeColor":s,"strokeWidth":1})
        els.append(txt(f"lt{i}",lx+30,y-1,lbl,14,"#1e1e1e"))
    return els

def bg(x0,y0,x1,y1):
    return {"type":"rectangle","id":"bg","x":x0,"y":y0,"width":x1-x0,"height":y1-y0,
            "backgroundColor":BG,"fillStyle":"solid","strokeColor":"transparent","strokeWidth":1}

def write(name, title, canvas, elements, note=""):
    spec = {"type":"excalidraw-scene-spec","title":title,"canvas":canvas,"note":note,
            "elements":[{"type":"cameraUpdate","width":int(canvas.split("x")[0]),
                         "height":int(canvas.split("x")[1]),"x":0,"y":0}] + elements}
    (HERE/name).write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print("wrote", name, f"({len(elements)} elements)")


# ==================== 1) DEPLOYMENT PIPELINE ====================
def deployment_pipeline():
    e = [bg(-100,-100,1570,700)]
    e += header("ThreadPup Deployment Pipeline", "GitHub -> Vercel · automated CI/CD",
                1390, ["Source","CI / checks","Deploy"])
    # main flow row (y=330, h=100)
    Y, H = 330, 100
    e += [
        card("dev",   40,  Y,190,H, BLUE,   "\U0001F469‍\U0001F4BB\nDeveloper\npush / open PR"),
        card("gh",    280, Y,190,H, BLUE,   "\U0001F419\nGitHub repo\nmain + PRs"),
        card("ci",    520, Y,210,H, GREEN,  "⚙️\nGitHub Actions\nlint · test · build"),
        card("prod",  780, Y,190,H, ORANGE, "\U0001F53A\nVercel\nProduction deploy"),
        card("supa",  1020,Y,190,H, GREEN,  "\U0001F5C4️\nSupabase\nrun migrations"),
        card("live",  1260,Y,170,H, BLUE,   "\U0001F310\nthreadpup.com\nLIVE", 16),
    ]
    # preview branch (above CI)
    e += [card("prev", 780, 170,210,100, ORANGE, "\U0001F53A\nVercel Preview\nper-PR URL")]
    # main horizontal arrows + short labels (y=380 center; gaps are 50px)
    cy = Y + H//2
    for aid, gx, lbl in [("e1",230,"push"),("e2",470,"PR"),("e3",730,"merge"),
                         ("e4",970,"deploy"),("e5",1210,"live")]:
        e.append(arrow(aid, gx, cy, [[0,0],[50,0]]))
        e.append(txt("l"+aid, gx+25-len(lbl)*3.6, cy-32, lbl, 13))
    # preview elbow: CI top -> up -> right -> Preview bottom
    e.append(arrow("ep", 625, Y, [[0,0],[0,-60],[260,-60]]))
    e.append(txt("lep", 560, Y-46, "on PR", 13))
    # footer note
    e.append(txt("note", 60, 480,
                 "Open a PR -> isolated preview deploy.   Merge to main -> CI passes -> production deploy + DB migrations -> live.",
                 15, "#8A5A30"))
    write("deployment-pipeline.excalidraw.json", "ThreadPup Deployment Pipeline", "1600x620", e,
          note="Linear CI/CD flow; preview branch off CI; 50px gaps, labels >=16px above arrows.")


# ==================== 2) DATA FLOW (draft) ====================
def data_flow_draft():
    """Rough first pass: single pipeline row + a data store, minimal labels.
    Kept as the 'Excalidraw Draft' (process evidence) — pre-notification-layer."""
    e = [bg(-100,-100,1470,520)]
    e += header("ThreadPup Order Data Flow (draft)", "first pass — pipeline + data store",
                1340, ["Customer-facing","Backend","Third-party"])
    Y, H = 170, 96
    e += [
        card("d1", 50,  Y,200,H, BLUE,   "\U0001F6D2\nOrder placed"),
        card("d2", 330, Y,180,H, ORANGE, "\U0001F4B3\nStripe charge"),
        card("d3", 590, Y,200,H, GREEN,  "⚙️\nFulfillment"),
        card("d4", 870, Y,180,H, GREEN,  "\U0001F5A8️\nPrint Shop"),
        card("d5", 1130,Y,200,H, GREEN,  "\U0001F4E6\nShipping"),
    ]
    cy = Y + H//2
    for aid, gx in [("a1",250),("a2",510),("a3",790),("a4",1050)]:
        e.append(arrow(aid, gx, cy, [[0,0],[80,0]]))
    # data store band
    e += [box("db", 50, 360, 1280, 90, GREEN[0], GREEN[1],
              "\U0001F5C4️  Supabase · orders table  (status field)", 16, GREEN[2])]
    for i, cx in enumerate([150,420,690,960,1230]):
        e.append(arrow(f"w{i}", cx, Y+H, [[0,0],[0,94]]))
    write("data-flow.draft.excalidraw.json", "ThreadPup Order Data Flow (draft)", "1440x520", e,
          note="DRAFT v1: pipeline writes to a single Supabase store; no status labels or notification layer yet.")


# ==================== 3) DATA FLOW (polished) ====================
def data_flow():
    e = [bg(-100,-100,1470,760)]
    e += header("ThreadPup Order Data Flow", "How one order moves through the system — status by status",
                1340, ["Customer-facing","Backend","Third-party"])
    # Row A: pipeline (y=160 h=96)
    Y, H = 160, 96
    e += [
        card("d1", 50,  Y,200,H, BLUE,   "\U0001F6D2\nOrder placed\nNext.js storefront"),
        card("d2", 330, Y,180,H, ORANGE, "\U0001F4B3\nStripe\ncharge card"),
        card("d3", 590, Y,200,H, GREEN,  "⚙️\nFulfillment API\ncreate job"),
        card("d4", 870, Y,180,H, GREEN,  "\U0001F5A8️\nPrint Shop\nprint + QC"),
        card("d5", 1130,Y,200,H, GREEN,  "\U0001F4E6\nShipping\nlabel + tracking"),
    ]
    cy = Y + H//2
    for aid, gx, lbl in [("a1",250,"charge"),("a2",510,"fulfil"),("a3",790,"print"),("a4",1050,"pack")]:
        e.append(arrow(aid, gx, cy, [[0,0],[80,0]]))
        e.append(txt("l"+aid, gx+40-len(lbl)*3.6, cy-30, lbl, 13))
    # Row B: Supabase data store (wide), y=350 h=104
    e += [box("db", 50, 350, 1280, 104, GREEN[0], GREEN[1],
              "\U0001F5C4️  Supabase · orders table\nstatus:  pending -> paid -> in_production -> shipped -> delivered",
              16, GREEN[2])]
    # vertical "writes status" arrows from each stage into the store, with status labels
    writes = [("w1",150,"pending"),("w2",420,"paid (webhook)"),("w3",690,"in_production"),
              ("w4",960,"printed"),("w5",1230,"shipped")]
    for aid, cx, lbl in writes:
        e.append(arrow(aid, cx, Y+H, [[0,0],[0,94]], color=GREEN[1]))
        e.append(txt("l"+aid, cx+14, Y+H+34, lbl, 13, GREEN[2]))
    # Row C: notification layer y=540 h=96
    Yc = 540
    e += [
        card("resend", 330, Yc,190,96, ORANGE, "✉️\nResend\nstatus emails"),
        card("cust",   600, Yc,210,96, BLUE,   "\U0001F9D1\nCustomer\ndashboard + inbox"),
    ]
    # db -> resend (on status change)
    e.append(arrow("n1", 425, 454, [[0,0],[0,86]], color=ORANGE[1]))
    e.append(txt("ln1", 439, 480, "on status change", 13, ORANGE[2]))
    # resend -> customer (email)
    e.append(arrow("n2", 520, Yc+48, [[0,0],[80,0]], color=ORANGE[1]))
    e.append(txt("ln2", 540, Yc+16, "email", 13, ORANGE[2]))
    # customer reads dashboard from db (dashed, up)
    e.append(arrow("n3", 705, Yc, [[0,0],[0,-86]], color=BLUE[1], dashed=True))
    e.append(txt("ln3", 719, 480, "views status", 13, BLUE[2]))
    # footer note
    e.append(txt("note", 60, 678,
                 "One order, one status field: each stage writes its status to Supabase; Resend emails the customer on every change; the dashboard reads the same record.",
                 14, "#8A5A30"))
    write("data-flow.excalidraw.json", "ThreadPup Order Data Flow", "1440x760", e,
          note="3 layers: pipeline writes status to Supabase store; Resend notifies on change; customer dashboard reads. Stripe webhook sets 'paid'. Status labels >=14px clear of risers.")


if __name__ == "__main__":
    deployment_pipeline()
    data_flow_draft()
    data_flow()
