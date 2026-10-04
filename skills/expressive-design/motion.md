# Motion: purpose, contract, platform, floors

Contents: purpose · the contract · timing · reduce, don't remove · platform status · accessibility floors · performance · 3D · scrolljacking

## Purpose: one per effect, or cut it

| Purpose | Explains | Example | Under reduced motion |
| --- | --- | --- | --- |
| **Transition** | Where am I, where did that come from | Shared-element morph between list and detail | Cross-fade |
| **Feedback** | Cause → effect of my action | Button press, drag release, check passes | Keep it; shorten it |
| **Supplement** | Something appeared without me leaving | Popover, toast, inline expansion | Fade only |
| **Demonstration** | How the subject works | The thesis object folds, assembles, processes | Stepped states the reader advances |
| **Decoration** | Nothing | Ambient drift, hover wobble | Remove first |

Categories after [Nabors](https://alistapart.com/article/patterns-and-purpose/) and [NN/g](https://www.nngroup.com/articles/animation-purpose-ux/). Ration decoration like sugar. An expressive page earns its one big moment as a *demonstration* of the thesis object, and keeps everything else productive and quiet. This is Carbon's productive versus expressive split ([Carbon](https://carbondesignsystem.com/elements/motion/overview/)).

## The contract

Write one row per effect before building it. The row is the spec, and a test checks each column.

| Column | Resolve |
| --- | --- |
| Purpose | Which row of the purpose table; which relationship it explains |
| Trigger | Arrival, intent (hover/focus/scroll into view) or direct selection |
| End state | Where it settles; the settled frame must be a complete, readable composition |
| Interruption | Can the visitor stop and inspect? Behavior on focus, tab hidden, scrolled offscreen, rapid re-trigger |
| Selection | The **one** state that drives visual, content, URL fragment and ARIA together |
| Alternatives | Reduced motion, no script, touch without hover, narrow viewport, 200 % text |
| Controls | Pause, replay or step controls exist only where the effect exists, at that breakpoint and preference |

Rules that follow from the contract:

- A replay button is not a pause button. Anything automatic that runs more than 5 s beside other content needs pause, stop or hide ([WCAG 2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html)). Auto-updating content gets no 5-second exemption.
- Never hold essential text at `opacity: 0` waiting for an entrance. It delays LCP and hides content from anyone whose script fails.
- Prefer finite gestures that settle, and self-paced stepping, over loops and timers.
- Let people cancel motion; never make them wait for it to finish ([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/motion)).

## Timing and easing

- **Duration.** About 100 ms for feedback, 200–300 ms for panels and modals, about 400 ms for large moves. At 500 ms it drags, and frequent actions should be shorter ([NN/g](https://www.nngroup.com/articles/animation-duration/)). Duration grows with distance travelled ([Carbon](https://carbondesignsystem.com/elements/motion/overview/)). The one expressive demonstration may run longer only because the visitor controls or can skip it.
- **Easing.** Ease-out for entering and exiting, ease-in-out for things moving on screen, never ease-in for UI ([Kowalski](https://emilkowal.ski/ui/great-animations)). Material 3 standard: `cubic-bezier(0.2, 0, 0, 1)`; emphasized-decelerate: `cubic-bezier(0.05, 0.7, 0.1, 1)` ([M3](https://github.com/material-components/material-components-android/blob/master/docs/theming/Motion.md)).
- **Springs.** Use them for spatial properties (position, size, rotation), where overshoot reads as physical. Opacity and color get critically damped springs or plain easing. On the web, approximate springs with `linear()`, which is Baseline Widely available.
- **Interruptibility.** A CSS *transition* retargets from its current value. A *keyframe animation* restarts from zero. Use transitions for anything that can re-trigger quickly.
- **Repetition.** Never animate keyboard-initiated or high-frequency actions.

## Reduce, don't remove

- Write the still state first. Put motion inside `@media (prefers-reduced-motion: no-preference)`, so browsers that don't support the query get the safe default ([Tatiana Mac](https://www.tatianamac.com/posts/prefers-reduced-motion)).
- Under `reduce`, swap spatial motion for fades or stepped states. Changes in color, opacity or blur are not "motion" for [WCAG 2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html). The demonstration survives as reader-advanced steps, so the identity survives too.
- Vestibular triggers ([Val Head](https://alistapart.com/article/designing-safer-web-animation-for-motion-sensitivity/)): large motion relative to the viewport, a mismatch between scroll direction and speed (parallax, scrolljacking), and big zooms. Camera fly-throughs hit all three.
- Listen for `matchMedia(...).addEventListener('change', …)`, and offer an on-page motion toggle that persists ([Smashing](https://www.smashingmagazine.com/2021/10/respecting-users-motion-preferences/)).
- `forced-colors: active` removes shadows and background images. Hierarchy carried only by shadow disappears, so add borders.

## Platform status (Baseline, October 2026)

Re-check on the [web-features explorer](https://web-platform-dx.github.io/web-features-explorer/) before relying on any row.

| Feature | Status | Use as |
| --- | --- | --- |
| Web Animations API, `linear()` easing, size container queries, `prefers-contrast`, `forced-colors`, OffscreenCanvas | Widely | Baseline tools |
| `@starting-style`, `transition-behavior: allow-discrete`, Popover API, `content-visibility`, same-document View Transitions, container style queries | Newly | Fine with a graceful no-animation path |
| Anchor positioning | Disputed: web.dev says Newly, explorer says Limited, interop bugs open | Enhancement with fallback positioning |
| Scroll-driven animations (`animation-timeline: scroll()/view()`) | Limited: no stable Firefox | Wrap in `@supports (animation-timeline: view())`; the unsupported path must be the full static story |
| Cross-document View Transitions (`@view-transition { navigation: auto; }`) | Limited: no Firefox | Free enhancement; unsupported browsers just navigate |
| `interpolate-size` / `calc-size()`, `@container scroll-state()` | Limited: Chromium only | Enhancement; snapping is the fallback |
| `prefers-reduced-transparency`, WebGPU | Limited | Extra on top of a legible default; WebGL2 fallback |

View Transitions gotchas: a duplicate `view-transition-name` on two rendered elements makes the browser skip the transition, and the page is frozen during the update callback. For reduced motion, use a subtler animation that keeps the relationship, not `animation: none` everywhere ([Chrome](https://developer.chrome.com/docs/web-platform/view-transitions/same-document)).

## Accessibility floors (WCAG 2.2 AA unless marked)

| SC | Floor | Where expressive pages fail it |
| --- | --- | --- |
| [1.4.4](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html) Resize text | 200 % without loss | vw-only fluid type; fixed-height hero boxes |
| [1.4.10](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) Reflow | No 2-D scroll at 320 px wide or 256 px tall | Pinned scroll stages; wide code; oversized display words |
| [1.4.12](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) Text spacing | Survives 1.5 line-height, 0.12 em letter-spacing | Fixed-height animated text containers |
| [2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) Pause, stop, hide (A) | Control for auto motion > 5 s | Marquees, looping hero video, Lottie loops |
| [2.3.1](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html) Three flashes (A) | ≤ 3 flashes per second | Strobing transitions, glitch effects |
| [2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) Animation from interactions (AAA) | Interaction motion can be disabled | Scroll-linked parallax with no reduce branch |
| [2.4.11](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html) Focus not obscured | Focus never fully hidden | Sticky headers, cookie bars; fix with `scroll-padding` |
| [2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) Target size | 24 × 24 CSS px or spacing exception | Tiny step dots and scrubbers |

WCAG 3 is a working draft, still years from being normative. WCAG 2.2 AA is what EN 301 549 and the European Accessibility Act build on.

## Performance

- Animate `transform` and `opacity` ([web.dev](https://web.dev/articles/animations-guide)). `will-change` is a last resort: toggle it from script around the effect, never set it in bulk ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/will-change)).
- Core Web Vitals at p75 are LCP ≤ 2.5 s, INP ≤ 200 ms and CLS ≤ 0.1 ([web.dev](https://web.dev/articles/vitals)). INP counts clicks, taps and key presses. Heavy animation setup inside a click handler hurts it, so yield first.
- Reserve geometry before enhancement (`aspect-ratio`, `min-height`, explicit `width`/`height`). Scroll-triggered reveals that move layout do count toward CLS ([web.dev](https://web.dev/articles/optimize-cls)).
- The LCP hero image gets `fetchpriority="high"`, is never lazy-loaded and is discoverable in HTML ([web.dev](https://web.dev/articles/optimize-lcp)).
- Kill font-swap shift with `size-adjust` and the ascent, descent and line-gap overrides on a fallback `@font-face` ([Chrome](https://developer.chrome.com/blog/font-fallbacks)).
- Scroll-driven CSS animations stay smooth under main-thread load, where scroll-listener JavaScript janks ([Chrome](https://developer.chrome.com/blog/scroll-animation-performance-case-study)).
- Lab is not field. INP barely exists in the lab, and a Lighthouse score is a distribution, not a number ([scoring](https://developer.chrome.com/docs/lighthouse/performance/performance-scoring)).

## 3D, canvas, WebGL

WebGL earns its cost only when the 3D *is* the content: a configurator, spatial data, a generative identity. For cards, tilts, folds, depth and logo motion, CSS 3D transforms (`perspective`, `rotate3d`) and SVG run on the compositor and stay in the accessibility tree. Stripe Connect built its spatial metaphors in CSS ([Stripe](https://stripe.com/blog/connect-front-end-experience)). If you do ship WebGL:

1. Ship a static poster first, as the LCP candidate.
2. Initialize the canvas when it scrolls into view.
3. Swap or skip it under reduced motion.
4. Handle context loss.
5. Give it a text alternative.
6. Prefer OffscreenCanvas in a worker.

Apple-style scroll-scrubbed frame sequences cost tens of megabytes ([CSS-Tricks measured ~56 MB](https://css-tricks.com/lets-make-one-of-those-fancy-scrolling-animations-used-on-apple-product-pages/)). Budget them and ship a single-image fallback.

## Scrolljacking

Hijacking scroll speed or direction disorients people and frustrates goal-driven reading, and it is worse on mobile ([NN/g](https://www.nngroup.com/articles/scrolljacking-101/)). Scroll-*linked* animation that leaves native scroll alone is the alternative. If a pinned stage is unavoidable:

- keep the direction vertical
- keep text short
- interleave normal-scroll sections
- give an escape hatch (sticky nav, skip link)
- stack the steps statically on mobile, with each step sized from `innerHeight` rather than `vh` ([The Pudding](https://pudding.cool/process/responsive-scrollytelling/))
