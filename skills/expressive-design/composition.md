# Composition: the still frame

Judge every page with motion disabled first. If the still frame does not hold, motion only decorates a weak layout.

Contents: the flatness ladder · levers · the flatplan · typography · color · critique tests

## The flatness ladder

When a competent design "doesn't pop", climb in this order and stop at the first rung that fixes it. Effects come last because they are the cheapest to add and the weakest at fixing hierarchy.

| Rung | Question | Typical move |
| --- | --- | --- |
| 1. Hierarchy | Is there one obvious first thing? | Make the focal element ≥ 3× the next-largest; cap at three size tiers per viewport |
| 2. Axis | Is everything centered? | Move to a strong off-center axis (text on columns 1–7 of 12, open field right), then align everything to it |
| 3. Silhouette | Does the page have a recognizable shape at thumbnail size? | Crop the thesis object tighter than feels safe so the edge cuts it; run one element full-bleed |
| 4. Rhythm | Do neighbouring sections look the same? | Re-plan the flatplan so neighbours differ on at least one of loud/quiet, dense/open, light/dark |
| 5. Accent | Does the spot color mean one thing? | Reserve it for the focal element or the primary action; more than ~3 uses per viewport and it stops being an accent |
| 6. Voice | Could the type belong to any site? | Give display type a face with a Display or `opsz` cut, real weight contrast, tight leading |
| 7. Material | Is there a surface, texture or depth model drawn from the subject? | Derive it from the thesis object (paper folds, LED grid, sunlight angle) |
| 8. Motion | Is something still unexplained? | Add one finite gesture that explains a relationship; see [motion.md](motion.md) |

**Emphasize by de-emphasizing.** When two things compete, shrink or desaturate one. Do not enlarge the other.

## Levers

- **Scale contrast.** Hierarchy comes from value and saturation contrast against the surroundings, not from the hue itself ([NN/g](https://www.nngroup.com/articles/visual-design-cheat-sheet/)). Asymmetric balance reads as energy, symmetric balance as calm ([NN/g](https://www.nngroup.com/articles/principles-visual-design/)).
- **Ordered asymmetry.** Tschichold: asymmetry "must not degenerate into unrest"; order is expressed through size, weight, line arrangement and color ([The New Typography](https://openlab.citytech.cuny.edu/langecomd3504fa2020-monday/files/2018/10/Tschichold_NewTypo.pdf)).
- **Strict grid, one break.** A grid break reads as intentional only when the grid is visibly strict everywhere else. Allow one break per chapter, and make it the focal element: a full-bleed image, a headline overrunning its column, or an object cropped by the viewport.
- **Whitespace as ground.** An empty field next to a dense block makes the block the figure. Make the gaps between groups at least 2× the gaps within them, so grouping survives the squint test.
- **Selective exaggeration.** Let one object dominate at an absurd scale while everything around it stays precise and small. Physical-product and event sites (Teenage Engineering, Nothing, Stripe Sessions) use this. Exaggerating several things at once just makes noise.
- **Conventional skeleton, distinctive flesh.** First impressions form in 17–50 ms, and *prototypical*, low-complexity pages score highest ([Tuch et al.](https://research.google/pubs/the-role-of-visual-complexity-and-prototypicality-regarding-first-impression-of-websites-working-towards-understanding-aesthetic-judgments/)). Keep navigation, link styling and page furniture where people expect them. Spend the distinctiveness on the focal element, the type and the subject's own imagery.

## The flatplan

Before building, write the scroll as a magazine flatplan: one row per chapter.

| Chapter | Job (visitor question answered) | Loud/quiet | Dense/open | Light/dark | Focal element |
| --- | --- | --- | --- | --- | --- |

No two neighbours may share all three states. A row of identical density repeated down the page ("hero, three cards, three cards, CTA") is the most common cause of a flat page. Magazines alternate dense and open spreads for the same reason: every-dense tires the reader and every-airy feels thin.

## Typography

- **The type is the voice.** One or two families; if two, make them clearly distinct. Treat the headline as part of the composition, not a delivery vehicle. A neutral family can work if it gets real display treatment: Linear kept Inter and added Inter Display for headings ([Linear](https://linear.app/now/how-we-redesigned-the-linear-ui)). What reads as generic is one weight at default tracking.
- **Display scale.** Leading 0.9–1.05 with negative tracking at hero sizes. Prefer faces with an `opsz` axis or a separate Display cut, because the fine detail at 120 px and up is what makes it look expensive ([MDN font-optical-sizing](https://developer.mozilla.org/en-US/docs/Web/CSS/font-optical-sizing)).
- **Body.** Measure 45–75 characters, about 66 ideal ([Bringhurst](http://webtypography.net/2.1.2), [Butterick](https://practicaltypography.com/line-length.html)). Leading 120–145 % ([Butterick](https://practicaltypography.com/line-spacing.html)).
- **Fluid scale.** Define a small-screen and a large-screen scale and interpolate with `clamp()`. A steeper ratio on desktop makes display type dramatic without crushing mobile ([Utopia](https://utopia.fyi/blog/designing-with-fluid-type-scales/)).
- **Zoom guard.** Write the preferred value as `rem + vw`, never `vw` alone, and keep max ≤ 2.5 × min, so 200 % zoom still enlarges text ([Smashing](https://www.smashingmagazine.com/2023/11/addressing-accessibility-concerns-fluid-type/), [Roselli](https://adrianroselli.com/2019/12/responsive-type-and-zoom.html)).
- **Type as artifact.** The strongest type choices come from the subject. Nothing's dot-matrix face echoes its LED hardware, and Vercel's Geist echoes its Swiss-grid engineering voice ([Geist](https://vercel.com/font)).

## Color

- **Work in OKLCH.** Equal lightness *looks* equal across hues, so ramps can be generated by stepping L at fixed C and H ([Evil Martians](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl)). Linear derives whole themes from three inputs (base, accent, contrast) in LCH ([Linear](https://linear.app/now/how-we-redesigned-the-linear-ui)).
- **Recipe.** One neutral ramp at low chroma, tinted toward the accent hue, plus one high-chroma accent with one meaning. Use dominant color with a sharp accent, never an evenly spread palette.
- **Immersive chapters.** For a dark chapter, invert the same ramp (same hue, flipped L) so it stays in the system. Light/dark alternation is a rhythm lever.
- **Albers.** A color is never seen as it is ([Interaction of Color](https://www.designersreviewofbooks.com/2010/10/interaction-of-color-by-josef-albers/)). Judge the accent in place, against its real neighbours.
- **Contrast floor.** WCAG 2.2 AA is the pass/fail: 4.5:1 for text, 3:1 for large text and non-text UI, no rounding ([W3C](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)). The WCAG 3 contrast algorithm is still undetermined ([WCAG 3 draft](https://www.w3.org/TR/wcag-3.0/)). Use APCA only as a secondary check for thin display weights and light-on-dark text ([APCA](https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html)).
- **Translucency.** Glass passes contrast on one background and fails on another ([NN/g](https://www.nngroup.com/articles/glassmorphism/)). Put it over a ground you control, or use solid surfaces.

## Critique tests

Run these on rendered screenshots, never on the code. You cannot see a layout you have not rendered.

| Test | How | Pass |
| --- | --- | --- |
| **Blur** (reproducible squint, [LukeW](https://www.lukew.com/ff/entry.asp?2013=)) | `filter: blur(8px)` on a screenshot | 1–3 masses read; the largest is the intended focal point |
| **Grayscale** | `filter: grayscale(1)` | Hierarchy survives; nothing important vanishes (value, not hue, carries it) |
| **Thumbnail** | View at ~200 px wide beside 3 peers' thumbnails | Recognizable silhouette, distinguishable from the peers |
| **Logo swap** | Replace the name and mark with a competitor's | It should look wrong. If it still fits, the identity is generic |
| **Template diff** | Write down the default page you would produce for this prompt, then list every match | Each match is a deliberate choice, not an accident |
| **5-second** ([Lyssna](https://www.lyssna.com/guides/five-second-testing-guide/)) | Show for 5 s; ask "what is it?" and "what stood out?" | Category named correctly; the thesis object named as the standout |
| **Describe-it** | Ask a fresh reader to describe it to a friend in one sentence | Not "a SaaS site with a gradient" |
| **Remove one thing** | Remove the weakest accessory | Nothing is lost. Repeat until something is |
| **Motion off** | Reduced motion and no JavaScript | Identity, content and hierarchy intact |

A fresh subagent given only the screenshots makes a good fresh reader for the 5-second and describe-it tests.
