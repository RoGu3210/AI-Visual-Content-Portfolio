# ThreadPup — Color Palette

Brand + functional colors for the ThreadPup infographics. All functional fills/strokes
use Excalidraw's built-in pastel palette so the diagrams stay clean and on-theme.

## Brand colors (titles, accents, mascot)
| Token | Hex | Use |
|-------|-----|-----|
| Caramel | `#C68642` | Primary brand accent, title underline |
| Bark | `#5B3A29` | Headings / dark text accent |
| Cream | `#FFF8F0` | Soft background tint (optional) |
| Collar Green | `#2f9e44` | Friendly CTA accent |
| Sky | `#1971c2` | Link / secondary accent |

## Architecture — functional color codes
| Category | Fill | Stroke | Components |
|----------|------|--------|-----------|
| 🔵 Customer-facing | `#a5d8ff` | `#1971c2` | Customer, Next.js Storefront (Vercel) |
| 🟢 Backend services | `#b2f2bb` | `#2f9e44` | Supabase, Fulfillment API, Print Shop* |
| 🟠 Third-party APIs | `#ffd8a8` | `#e8590c` | Stripe, Resend |

\* Print Shop is shown green as an internal fulfillment/operations step (the diagram's
3-color legend covers customer-facing / backend / third-party).

## Customer journey — phase color codes
| Phase | Fill | Stroke | Stages |
|-------|------|--------|--------|
| 🟣 Awareness | `#d0bfff` | `#7048e8` | Discovery, Landing page |
| 🔵 Consideration | `#a5d8ff` | `#1971c2` | Browse catalog, Customize shirt |
| 🟢 Purchase | `#b2f2bb` | `#2f9e44` | Add to cart, Checkout, Order confirmation email |
| 🟠 Post-purchase | `#ffd8a8` | `#e8590c` | Production, Shipping, Delivery, Review request, Repeat |

## Text colors (on white)
- Primary text: `#1e1e1e` · Secondary/sub: `#757575`
- Colored headings use dark stroke variants (`#1971c2`, `#2f9e44`, `#e8590c`, `#7048e8`)
  for contrast — never light pastels on white.
