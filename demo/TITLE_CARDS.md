# Legibright — title-card & thumbnail specs

`demo/cards/` has both the SVG source and a **rendered PNG** for each card, at final resolution,
ready to drop straight into a video editor or the Devpost thumbnail upload — no conversion needed:

| File | Size | Use |
|---|---|---|
| `title-open.png` | 1920×1080 | opening card (Scene 1) |
| `title-close.png` | 1920×1080 | closing card (Scene 6) |
| `transition-trust-accuracy.png` | 1920×1080 | 1–2 sec transition into Scene 3 |
| `transition-self-audit.png` | 1920×1080 | 1–2 sec transition into Scene 5 |
| `thumbnail.png` | 1280×720 | Devpost gallery thumbnail |

Regenerate any of them from the `.svg` source with `rsvg-convert -w <width> -h <height> in.svg -o out.png`
(installed via `brew install librsvg`). Below is the spec so anything you rebuild stays on-brand.

## Palette (locked)
| Token | Hex | Where |
|---|---|---|
| Ink (background) | `#1E1B4B` | every card background; the L's vertical stroke |
| Indigo | `#4F46E5` | the checkmark stroke (light-on-dark: use `#6366F1`) |
| Indigo-light | `#6366F1` | check on dark cards, secondary accent |
| Lavender text | `#C7D2FE` | taglines on dark |
| Muted lavender | `#818CF8` | footnotes / URLs / kickers |
| White | `#FFFFFF` | wordmark, the L stroke on dark |

**Verdict colors never change:** 🟢 `#16A34A` · 🟡 `#CA8A04` · 🔴 `#DC2626`. Keep them semantic so a
juror reads the verdict instantly — do not tint them indigo.

## Fonts
Wordmark **Space Grotesk 700**; body **Inter** (Arial fallback). The SVGs list both so they degrade.

## 1 · Open title card — 1920×1080 (`title-open.svg`)
Ink background · ✓-L mark centered (~200 px tall, white L + `#6366F1` check) · **Legibright** wordmark
128 px white · tagline "A statistical trust layer that catches overfit & data leakage in DataHub."
38 px `#C7D2FE` · kicker "BUILD WITH DATAHUB · THE AGENT HACKATHON" 26 px `#818CF8`, tracked. Hold 2–3 s.

## 2 · Close card — 1920×1080 (`title-close.svg`)
Same mark · **Legibright** 112 px · **"make model trust legible."** 44 px `#C7D2FE` · repo URL
`github.com/bogacsmz/legibright-trust-audit` 30 px `#818CF8`. Hold 3–4 s over the last VO line.

## 3 · Devpost thumbnail — 1280×720 (`thumbnail.svg`)
Ink→`#312B7A` diagonal gradient · mark + **Legibright** + "Catch overfit & data leakage — inside
DataHub." · one proof line "🔴 NOT TRUSTWORTHY · Trust Score 28/100 · written back to the graph".
Export PNG at 1280×720 (Devpost gallery ratio). Text must survive being scaled to a small card — keep
it to three lines.

## 4 · Transition cards — 1920×1080 (`transition-trust-accuracy.svg`, `transition-self-audit.svg`)
Same ink background + small ✓-L mark, no wordmark (mid-video, not the open/close). One big white
headline (~90–104 px) + one lavender `#C7D2FE` subtitle (~38–42 px). Hold 1–2 seconds — these are
quick beat-markers between live-screen segments, not full title cards.

## 5 · Beat lower-thirds (in-editor, not pre-rendered)
For each beat's ON-SCREEN TEXT (see `SCRIPT.md`): a semi-transparent ink bar (`#1E1B4B` @ 82%) across
the lower third, text in white/`#C7D2FE`, ~34–40 px. Keep the terminal readable above it.

## 6 · Watermark (all live-screen beats)
`legibright-mark.svg` bottom-right, ~44 px, ~55% opacity, 24 px margin. Never over the verdict card.

## Export
PNGs in `demo/cards/` are already rendered at final resolution. To regenerate after editing an SVG:
`rsvg-convert -w 1920 -h 1080 demo/cards/title-open.svg -o demo/cards/title-open.png` (thumbnail is
1280×720). For 2× crispness on a 4K timeline, render at double the target (e.g. `-w 3840 -h 2160`).
