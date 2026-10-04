---
name: expressive-design
description: Designs, critiques and builds distinctive, memorable web pages from the subject's own evidence - a claim ledger, one thesis object carrying the visual identity, a still composition that holds with motion off, parallel design directions, a motion contract per effect, and a validation matrix plus a source scanner for reduced-motion, zoom, focus, layout-shift, template-look and fake-proof failures. Use when a page looks generic, templated, flat or AI-made, or when asked to make it pop, stand out, feel premium, bolder, memorable or on-brand; redesigning or art-directing a landing, product, launch, campaign, portfolio, event, docs-entry or open-source project page; turning a product, report or dataset into a scroll story or interactive explainer; adding scroll-driven animation, view transitions or 3D to a site; reviewing motion or visual design for accessibility and honesty. Not for routine copy edits, single-component tweaks, or mockups with no build.
---

# Expressive design

Make the subject recognizable, understandable and worth inspecting. "Make it pop" is a composition problem before it is an animation problem, and a truth problem before both.

## Set the expression budget

| Surface | Spend boldness on | Keep prototypical |
| --- | --- | --- |
| Landing, launch, campaign, event, portfolio | Hero, thesis object, chapter rhythm, one demonstration | Nav, links, forms, footer |
| Product or project home | Hero and one evidence chapter | Pricing, docs links, install path |
| Docs, dashboards, tools, forms | Entry points, empty states, one signature detail | Everything people use repeatedly |
| Explainer, report, scroll story | The object's journey and reader-paced steps | Reading column, captions, navigation |

Conventional skeleton, distinctive flesh: first impressions reward prototypical structure and low complexity, so distinctiveness lives in the focal element, the type and the subject's own imagery. Argue for it on memorability, never on promised conversion; there is no controlled evidence that it converts.

## Procedure

1. **Ground the promise.** Inspect the live page, repository, docs, brand sources and the thing itself. Write the **claim ledger** (claim → evidence → status → permitted wording) and the **hero pair**: a memorable hook beside a plain category line. Name the visitor's first decision and the proof it needs. Missing evidence gets a labelled pending slot, never an invented artifact. → [evidence.md](evidence.md)
2. **Research mechanisms, not surfaces.** Collect 6–12 references from many sources, including outside the category (physical products, editorial, events, instruments, signage). For each, write a **mechanism card**: observed mechanism, why it fits, what to adapt, what not to borrow. Inspect rendered pages. One reference studied closely produces pastiche. → [evidence.md](evidence.md#reference-research)
3. **Find the thesis object.** Find one consequential artifact or action that can carry the identity, constrain several design axes at once, and carry the evidence. Mine these sources:
   - the subject's **output** (a report, a diff, a receipt, a print)
   - its **unit of work** (a ticket, a fold, a request)
   - its **hardware or material** (LED grid, paper, sunlight)
   - its **place**
   - its **process** (input → check → decision)
   - its **people's tools**

   The strongest identities derive from one source. Daylight's sun path fixes layout angle, shadow direction and motion vector. Nothing's LED grid becomes its typeface.
4. **Diverge in parallel.** Build 3 directions side by side, never in sequence:
   - **Faithful**: the existing brand, recomposed.
   - **Amplified**: the thesis object at extreme scale.
   - **Strange**: an unexpected material or metaphor from step 2.

   Each direction gets mood words, a token plan (4–6 named colors with roles, type roles), a flatplan and a rendered hero still. Critique them together, then converge. Record the choice as Question → Options → Criteria → choice. Showing one design alone inflates its rating.
5. **Compose the still.** Judge with motion off, at desktop and at 320 px.
   - Climb the **flatness ladder**: hierarchy, axis, silhouette, rhythm, accent, voice, material, and motion last.
   - Write the **flatplan** so no two neighbouring chapters share loud/quiet, dense/open and light/dark.
   - Run the **template diff** against the default page you would have produced. Every match needs a reason.
   - Run the critique tests on screenshots: blur, grayscale, thumbnail, logo swap, 5-second.
   - Preserve brand invariants. Keep illustrative geometry distinct from an official mark.

   → [composition.md](composition.md), [generic-tells.md](generic-tells.md)
6. **Make evidence the spectacle.** Follow the thesis object through cause and consequence: input, action, output, checks, decision. Open detail at the moment it answers a visitor's question. Use real artifacts with provenance, and put a recorded, sample or simulated label *beside* each demonstration. Recompose for touch and narrow screens; a front-facing, selectable view beats a shrunken diorama. The message must survive zero interaction and no script.
7. **Give motion a contract.** For each effect, write one row: purpose, trigger, end state, interruption, selection, alternatives, controls. Allow one expressive demonstration and keep everything else productive and brief. Use one authoritative selection state for visual, content, URL and ARIA. Reserve layout before enhancement. Reduce motion; don't remove it: fades and reader-advanced steps keep the identity. Gate Limited features (scroll-driven animations, cross-document view transitions) with `@supports`. → [motion.md](motion.md)
8. **Build and validate.** Use the project's existing stack. Prefer semantic server-rendered content with small enhancements, and CSS or SVG geometry before WebGL. Run `python3 scripts/design_scan.py <src>`, then exercise the final-build matrix on the production build. Report environment, states exercised, measurements and named gaps. → [validation.md](validation.md)
9. **Retain.** Keep the claim ledger, mechanism cards, the decision record and the validation record next to the page source, in the repository's docs convention. Follow the requested delivery scope and the repository's release process; designing a page does not authorize publishing it.

## Gotchas

- **Never fabricate** live activity, customers, logos, quotes, reviews, benchmarks, spend or success. Fake urgency, fake reviews and fake social proof are blacklisted in EU and US law, not just in taste. Supplied facts stay marked as supplied until verified.
- **Effects don't fix hierarchy.** Adding motion, glass or gradient to a flat page makes a flat page that moves. Fix rungs 1–4 of the ladder first.
- **Anti-slop lists breed second-order slop.** Cream paper, serif and terracotta, or near-black with acid green, is today's template. Derive every choice from the subject.
- **Restraint frames the loud moment.** One exaggerated element only reads against precise, quiet surroundings.
- **You cannot judge what you have not rendered.** Take screenshots at each breakpoint and preference, and use a fresh subagent with only the screenshots as the 5-second reader.
- **Controls must match reality.** A replay or pause control exists only where its effect runs, at that breakpoint and motion preference.
- **Reduced motion may be silently on** in the test browser. Read the active preference and exercise both states, or disclose the untested one.
- **Lab is not field and axe-clean is not conformant.** Report exactly what was exercised.

## Example

[case-unfold.md](case-unfold.md) shows a developer-tool site moved from clear to memorable: a folded-paper evidence object, a recorded fixture labelled as one, and the seams the verification tested. Use it as an example of the reasoning, not as a layout to copy.
