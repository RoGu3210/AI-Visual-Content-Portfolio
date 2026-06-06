# ThreadPup Technical Diagrams — open, export & share

Editable Excalidraw diagrams (Method B), redesigned clean + professional and
audited for layout/readability. **The 3 Scenario-2 deliverables are the first
three rows; the customer-journey is a bonus marketing view.**

| Diagram | Open (editable) | Source spec | PNG export (2×) |
|---------|-----------------|-------------|-----------------|
| **System Architecture** (services & connections) | `architecture.excalidraw` | `architecture.excalidraw.json` | `architecture.png` |
| **Deployment Pipeline** (GitHub → Vercel CI/CD) | `deployment-pipeline.excalidraw` | `deployment-pipeline.excalidraw.json` | `deployment-pipeline.png` |
| **Order Data Flow** (status by status) | `data-flow.excalidraw` | `data-flow.excalidraw.json` | `data-flow.png` |
| *Order Data Flow — DRAFT (process evidence)* | `data-flow.draft.excalidraw` | `data-flow.draft.excalidraw.json` | `data-flow.draft.png` |
| *Customer Journey (bonus, marketing funnel)* | `customer-journey.excalidraw` | `customer-journey.excalidraw.json` | `customer-journey.png` |

## Live Excalidraw share link
The deployment pipeline was also pushed through the **Excalidraw MCP** (`create_view`
+ `export_to_excalidraw`) to verify the Method-B output renders in the real tool and
to produce a shareable, fully-editable link:

- **Deployment Pipeline:** https://excalidraw.com/#json=Nu6vDyRJbGCNWqYvvbJMD,3rbbD0q8YYJxRDV1DeVdGQ

> Note: the MCP/web renderer doesn't draw emoji and is tuned for compact 4:3 views, so
> the shared link uses an emoji-free, reframed version. The wide, emoji-rich technical
> diagrams are best served by the file pipeline below — open the `.excalidraw` files for
> the full-fidelity, hand-drawn versions.

## Open a local `.excalidraw` file
1. Go to excalidraw.com → **Menu (☰) → Open** (Ctrl+O).
2. Pick the `.excalidraw` file from `task-3-threadpup/`. It loads fully editable.
3. Re-export if desired: **Menu → Export image → PNG, 2× scale**.

## Build pipeline (how these were made)
- `py make_diagrams.py` — builds the deployment-pipeline + data-flow specs (and the draft)
  from a small parameterized builder.
- `py to_excalidraw.py <spec>.excalidraw.json …` — spec → importable `.excalidraw`.
- `py render_preview.py <spec>.excalidraw.json --scale 2 --rough --out <name>.png` — spec → PNG.

## Design notes
- **Branded header** (cream + caramel) with the ThreadPup dog mascot, title, tagline, legend.
- **Architecture:** blue Customer-facing / green Backend / orange Third-party zones; icons +
  labeled data-flow arrows. **Deployment pipeline:** linear CI/CD with a PR-preview branch off
  CI. **Data flow:** 3 layers — pipeline writes a `status` to Supabase (the data store), Resend
  notifies the customer on each change, the dashboard reads the same record; Stripe webhook sets `paid`.
- Floating arrow/label clearance kept ≥14px (Virgil renders ~25% wider than Arial); 0px gaps
  where arrows meet a connected card border are expected. Colors in `color-palette.md`.
