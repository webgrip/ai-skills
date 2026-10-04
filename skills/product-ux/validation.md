# Validation: scan, exercise, report

Contents: static scan · QA inventory · exercising with real input · final-build matrix · findings that hold up · reporting

## Static scan

```bash
python3 scripts/ui_scan.py src/                         # exit 1 on any fail finding
python3 scripts/ui_scan.py --fail-on warn --json src/ > ui-scan.json
```

It reads source, so it can't see rendering, behaviour or users. It judges only native lowercase elements; a capitalised component is assumed to own its semantics, so scan the component library too. A finding is a prompt to fix or justify, and a justified exception goes into the report.

| Rule | Severity | Catches |
| --- | --- | --- |
| `unlabelled-field` | fail | Native field with no `<label for>`, wrapping label or `aria-labelledby` (1.3.1, 4.1.2) |
| `placeholder-as-label` | fail | The same, with a placeholder standing in |
| `clickable-non-control` | fail | `div`, `span`, `li`, `td`… with a click handler and no role plus tabindex (2.1.1) |
| `icon-button-no-name` | fail | Button whose only content is an icon, with no accessible name (4.1.2) |
| `img-no-alt` | fail | `<img>` without `alt` (1.1.1) |
| `aria-hidden-focusable` | fail | `aria-hidden="true"` on something focusable |
| `positive-tabindex` | fail | `tabindex` ≥ 1 (2.4.3) |
| `paste-blocked` | fail | Paste prevented (3.3.8, password managers) |
| `zoom-blocked` | fail | `user-scalable=no`, `maximum-scale=1` (1.4.4) |
| `prechecked-consent` | fail | Consent or marketing checkbox ticked by default (GDPR, Planet49) |
| `placeholder-copy` | fail | Lorem ipsum, John Doe, Acme, foo@bar.com |
| `focus-ring-removed` | fail | Outline removed with no `:focus-visible` anywhere (2.4.7) |
| `disabled-submit` | warn | Submit disabled up front or until valid |
| `autocomplete-off` | warn | `autocomplete="off"` on a field (1.3.5) |
| `input-font-zoom` | warn | Field text under 16 px outside a fine-pointer media query (iOS zoom) |
| `small-target` | warn | Button-like selector sized under 24 px (2.5.8) |
| `hover-only-interaction` | warn | Hover handler with no focus equivalent |
| `link-as-button` | warn | `href="#"`, `javascript:` or a link with a click handler and no destination |
| `missing-lang` | warn | `<html>` without `lang` (3.1.1) |
| `vague-error-copy` | warn | "Something went wrong", "invalid input", "oops" |
| `ambiguous-link-text` | warn | "Click here", "Learn more" as the whole link (2.4.4) |
| `confirmshaming` | warn | Decline options that shame ("No thanks, I don't want to save") |
| `native-blocking-dialog` | warn | `alert()`, `confirm()`, `prompt()` |
| `hardcoded-format` | warn | `MM/DD/YYYY` strings, currency symbol concatenation |
| `status-without-live-region` | warn | Toast or snackbar markup with no live region or toast library anywhere (4.1.3) |
| `motion-without-reduced-motion` | warn | Animation with no `prefers-reduced-motion` branch anywhere |
| `generic-action-label` | note | Buttons labelled Submit, OK, Yes, Send |
| `are-you-sure` | note | "Are you sure" confirmations |
| `naive-plural` | note | `item(s)` strings |
| `button-without-type` | note | `<button>` without `type` in a file that has a form |
| `autofocus-steals-context` | note | `autofocus` |
| `truncation-hides-content` | note | Ellipsis or line-clamp; check the full text is reachable |
| `z-index-escalation` | note | `z-index` ≥ 1000 |
| `raw-color-sprawl` | note | More than 16 distinct hex colours outside token files |

Run the scanner and the design judgement in separate passes, or separate subagents, so the scanner's output doesn't anchor the critique.

## QA inventory

Before testing, list what has to be true. Testing against an inventory finds what free-form clicking misses ([openai/skills playwright-interactive](https://github.com/openai/skills/tree/main/skills/.curated/playwright-interactive)).

| Kind | Example |
| --- | --- |
| Task | "An agent can refund a partial order in under 30 s by keyboard" |
| Control | Every button, field, menu, shortcut and drag target in scope |
| State | Each cell of the state matrix chosen in [states.md](states.md) |
| Claim | Every visible promise: "Saved", "Undo", counts, totals, "Last updated 2 min ago" |

When exploration finds a new state, add it to the inventory.

## Exercising with real input

- **Use real input for sign-off.** Clicks, keys and typing through Playwright or a browser; `page.evaluate()` setting state doesn't count.
- **Run full cycles:** initial → changed → back to initial for every toggle, filter and panel.
- **Inspect the densest realistic state** (the worst-case fixture), one post-interaction state and one mid-transition state.
- **Check fit with both numbers and pixels.** Element bounds from `getBoundingClientRect()` *and* screenshots; visible clipping in a screenshot is a failure even if the metrics look fine.
- **Do a short exploratory pass** after the scripted checks: rapid re-trigger, resize while focused, Back mid-flow, double submit, offline.
- **Close with two questions:** what visible part of this interface have I not inspected closely, and what defect would most embarrass this if someone looked?

Tooling: Playwright `page.emulateMedia({ reducedMotion, forcedColors, colorScheme, contrast })` per preference ([Playwright](https://playwright.dev/docs/api/class-page#page-emulate-media)); `toHaveScreenshot` baselines generated in the CI image; `@axe-core/playwright` per page; Storybook interaction tests per component where the project has Storybook.

## Final-build matrix

Pick dimensions from the subject; combine where failures are likely.

- **Flows:** each top task end to end, including error recovery, cancel, Back and the destructive path; the keyboard-only gate from [accessibility.md](accessibility.md#the-keyboard-only-gate).
- **Data:** empty, one, typical, worst-case and 1,000+ fixtures.
- **Roles:** each role that reaches the screen, plus no permission.
- **Layout:** 320 px, an intermediate width, the widest layout; both sides of each breakpoint that changes interaction; 200 % text; the 1.4.12 text-spacing override; the longest real locale; RTL if supported.
- **Preferences:** light, dark, reduced motion, `forced-colors: active`, touch without hover, no script where the stack is server-rendered.
- **Build:** production build, console errors, axe per page, the repository's own gates.
- **Performance:** INP on the top tasks' interactions, CLS after load and after interaction, with tool version and throttling recorded.

## Findings that hold up

A finding is worth reporting only if it survives these gates (after ibelick's improve-ui, impeccable's critique and Krehel's review format):

1. **Rule:** which standard, study, heuristic or design-contract decision it breaks.
2. **Proof:** evidence that it applies here: file and line, screenshot, a reproduction step, or a measured number.
3. **One correction** that the evidence determines.
4. **Falsification:** reopen the evidence and try to disprove it. Drop it if it doesn't hold.

Severity by impact on the task, not by taste:

| Severity | Meaning |
| --- | --- |
| P0 blocker | Users can't complete a task, lose data, or are excluded (keyboard, screen reader) |
| P1 major | A frequent task is slowed or error-prone; a WCAG AA failure with a workaround |
| P2 minor | Friction on infrequent tasks; inconsistency with the system |
| P3 polish | Visual detail with no task impact |

Group systemic issues into one finding with all locations. Cap the list (five in a quick review, fifteen in a full one) and never pad to reach the cap. Say what held up as well as what broke. Usability claims about hierarchy, discoverability or comprehension can't be proven from source alone; mark them as needing rendered or user evidence.

## Reporting

Keep these kinds of evidence separate and name each:

- automated scan
- source review
- rendered inspection
- real-input exercise
- expert method: heuristic evaluation, cognitive walkthrough, KLM ([evaluation.md](evaluation.md))
- test with real users

The report contains:

- **Environment:** commit or build, browser and version, viewport, preferences, commands or harness config.
- **Coverage table:** each area (flows, states, roles, layout, preferences, accessibility, performance) with what was inspected and how.
- **Findings** in the format above, most severe first.
- **Negative confirmation:** defect classes checked and not found.
- **Gaps, named:** "no screen-reader pass", "no physical device", "no Safari", "no real users", "worst-case fixture not rendered at 200 %".

An unexercised state is not a pass. An axe-clean page is not a conformance claim. An agent's walkthrough is not a usability test.
