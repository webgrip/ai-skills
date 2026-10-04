# Validation: build, exercise, report

Contents: static scan · regression traps · final-build matrix · tooling · reporting

## Static scan

```bash
python3 scripts/design_scan.py src/            # exit 1 on any fail finding
python3 scripts/design_scan.py --fail-on warn --json src/ > scan.json
```

It reads source, so it cannot see rendering. A clean scan never replaces the matrix below. A finding is a prompt to fix or justify; a justified exception goes in the rationale.

| Rule | Severity | Catches |
| --- | --- | --- |
| `motion-without-reduced-motion` | fail | Keyframes, transitions-on-scroll, view transitions or motion libraries with no `prefers-reduced-motion` branch anywhere |
| `focus-ring-removed` | fail | `outline: none` / `outline-none` with no `:focus-visible` replacement anywhere (2.4.7) |
| `zoom-blocked` | fail | `user-scalable=no`, `maximum-scale=1` (1.4.4, 1.4.10) |
| `fake-live-activity` | fail | "people are viewing this", "just signed up", "only 3 left" copy |
| `placeholder-copy` | fail | Lorem ipsum, John/Jane Doe, Acme |
| `autoplay-audio` | fail | Autoplaying `<video>`/`<audio>` without `muted` (1.4.2) |
| `infinite-animation` | warn | Endless loops that need pause (2.2.2) or a reduced-motion stop |
| `looping-video-no-control` | warn | Autoplay + loop video without `controls` |
| `layout-keyframes` | warn | Keyframes animating top/left/width/height/margin/padding/inset/font-size |
| `transition-all` | warn | `transition: all` |
| `will-change-sprawl` | warn | More than 3 `will-change` declarations |
| `img-no-dimensions` | warn | `<img>` with no width/height or aspect-ratio (CLS) |
| `font-face-no-display` | warn | `@font-face` with no `font-display` |
| `vw-only-type` | warn | Font size driven by `vw` alone (1.4.4) |
| `scroll-hijack-library` | warn | Lenis, Locomotive Scroll, fullPage.js and kin |
| `wheel-prevent-default` | warn | Non-passive wheel/touch listeners |
| `unsourced-multiplier` | warn | "10x faster" style claims needing a ledger row |
| `vague-social-proof` | warn | "Trusted by thousands", "loved by developers", ★★★★★ |
| `generic-gradient` | note | Blue-violet gradients, `from-indigo-* to-violet-*` utilities |
| `glass-everywhere` | note | Backdrop blur on more than 3 rules |
| `default-type-only` | note | `font-family` made only of default sans families |
| `emoji-heading-icon` | note | Emoji used as heading icons |
| `full-viewport-vh` | note | `100vh` heroes that overflow behind mobile browser bars |

## Regression traps

These traps were observed in shipped work. They are failure modes, not mandates for a particular DOM or breakpoint.

| Failure | Correction |
| --- | --- |
| A focused desktop panel becomes the hidden mobile panel after resize | Sync selection when a panel receives focus; reflow preserves the focused content |
| A replay button remains after mobile CSS or reduced motion disables the animation | Controls exist only where their effect exists |
| Hydration collapses a tall stack into one panel and shifts the page | Reserve stable first-paint geometry for the enhanced mode; keep a readable no-script stack |
| Works at normal text size, clips at enlarged text | Intrinsic sizing or container queries; test narrow + 200 % text together |
| Translation or code pushes the page sideways | Real localized copy; `min-width: 0` on flex/grid children; wrap prose; confine code scroll to a labelled region |
| Visual restructuring breaks a definition list or heading order | Recheck semantics after every composition change |
| The test browser silently runs reduced motion | Read the active preference; exercise both states or disclose which went untested |
| Entrance animation holds the hero at `opacity: 0` | Settled state renders first; animate from it, not to it |
| Two elements share a `view-transition-name` | The transition is skipped; generate unique names |

## Final-build matrix

Pick dimensions from the actual subject, and combine them where failures are likely.

- **Composition:** desktop, intermediate and 320 px; both sides of every interaction-changing breakpoint; the critique tests from [composition.md](composition.md) on screenshots.
- **Content:** real locales (the longest one), light and dark, 200 % text, the 1.4.12 text-spacing override, narrow + enlarged together.
- **Interaction:** keyboard order, visible focus, focus under sticky chrome, direct selection, deep links, rapid re-trigger, interruption, resize while focused.
- **Preferences:** touch without hover, normal motion, reduced motion, `forced-colors: active`, `prefers-contrast: more`, no script.
- **Forms:** error and success states with safe test data in a local or dedicated environment.
- **Build:** production build; axe scan per page; console errors; CSP; the repository's own gates.
- **Performance:** mobile and desktop loading with tool version, throttling and origin recorded; CLS after enhancement and after interaction checked separately from load.

## Tooling

- Playwright `page.emulateMedia({ reducedMotion, forcedColors, contrast, colorScheme })`, or set the same options per project to run the suite once per preference ([Playwright](https://playwright.dev/docs/api/class-page#page-emulate-media)).
- Use `toHaveScreenshot` for both motion states, with baselines generated in the CI image ([snapshots](https://playwright.dev/docs/test-snapshots)).
- `@axe-core/playwright` finds roughly half of WCAG issues, and its "incomplete" results need a human. It cannot judge motion purpose, vestibular risk or flashing ([axe-core](https://github.com/dequelabs/axe-core)).
- Use Lighthouse CI with multiple runs and treat the result as a distribution ([LHCI](https://github.com/GoogleChrome/lighthouse-ci)). Field data (CrUX/RUM) outranks lab data.
- Flashing video goes through PEAT. Reflow is checked at 320 × 256 px. Text spacing is checked by injecting the 1.4.12 stylesheet and asserting nothing clips.

## Reporting

Report what was exercised, where, and what was not:

- Commit or build id, environment, browser and version, and the commands or harness config.
- Results per state, with measured numbers and the tool version.
- Gaps, named explicitly: for example "no Safari", "no physical device", "no screen-reader user", "no field INP", "normal motion checked by source only".

Keep these kinds of evidence distinct: automated scan, source review, browser exercise and physical-device test. An unexercised state is not a pass. A single lab score is not a budget, and an axe-clean page is not a conformance claim.

Primary references to re-check when relevant: [W3C pause, stop, hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html), [animation from interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html), [reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html), [web.dev animations](https://web.dev/articles/animations-guide), [Web Vitals](https://web.dev/articles/vitals).
