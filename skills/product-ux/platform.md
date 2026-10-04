# Platform: touch, mobile web, responsive, primitives, performance, conventions, keyboard

Tiers: **[S]** standard or platform guideline · **[E]** empirical · **[C]** convention. Baseline statuses come from the web-features dataset v3.40.1 and MDN browser-compat-data of 1 October 2026; re-check on the [web-features explorer](https://web-platform-dx.github.io/web-features-explorer/) before relying on a Limited row.

Contents: touch · mobile web mechanics · responsive · platform primitives · performance as UX · single-page apps · platform conventions · keyboard and power users

## Touch

| Rule | Tier | Evidence |
| --- | --- | --- |
| Primary controls ≥ 44 × 44 CSS px; never under 24 × 24; grow the hit area with padding when the glyph is small | [S] | WCAG [2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) (AA floor), [2.5.5](https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html); [Apple 44 pt](https://developer.apple.com/design/human-interface-guidelines/buttons); [Android 48 dp](https://support.google.com/accessibility/android/answer/7101858) |
| ≥ 8 px between adjacent targets; destructive further from frequent | [S][E] | [NN/g touch targets](https://www.nngroup.com/articles/touch-target-size/) |
| Physical basis: 9.2 mm for single taps, 7.6 mm for serial taps | [E] | [Parhi, Karlson & Bederson 2006](https://www.semanticscholar.org/paper/Target-size-study-for-one-handed-thumb-use-on-small-Parhi-Karlson/7fc3a48e6ce88c56a5e5b921e1ee2e0c0e3af976) |
| Bigger targets at edges and corners than in the centre (~7 mm centre, ~9 edge, ~12 corner) | [E] | [Hoober 2017](https://www.uxmatters.com/mt/archives/2017/03/design-for-fingers-touch-and-people-part-1.php) |
| Activate on the up event (`click`), so sliding off cancels | [S] | WCAG [2.5.2](https://www.w3.org/WAI/WCAG22/Understanding/pointer-cancellation.html) |
| No single grip: 49 % one-handed, 36 % cradled, 15 % two hands; a third of one-handed use is the left thumb | [E] | n=1,333 ([Hoober 2013](https://www.uxmatters.com/mt/archives/2013/02/how-do-users-really-hold-mobile-devices.php)) |
| Primary content in the centre, where taps are most accurate | [E] | Hoober 2017 |
| Every gesture has a visible control; multipoint and path gestures need a single-pointer alternative; every drag has a no-drag alternative (Move to…, up/down buttons, tap the slider track) | [S] | WCAG [2.5.1](https://www.w3.org/WAI/WCAG22/Understanding/pointer-gestures.html), [2.5.7](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html); [NN/g swipe](https://www.nngroup.com/articles/contextual-swipe/) |
| Swipe-to-delete acts immediately with Undo, no confirm dialog | [C] | NN/g swipe |
| Never take over system gestures (edge swipe back, predictive back, home indicator) | [S] | [Apple gestures](https://developer.apple.com/design/human-interface-guidelines/gestures), [Android predictive back](https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture) |
| Long-press and hover are never the only path to anything | [S] | Apple HIG |

**Folklore:** the green/yellow/red "thumb zone" chart is a heuristic its own data source calls "well-known, but incorrect"; people reach the top corners (Hoober 2017). The MIT Touch Lab fingertip figures have no primary paper behind them; use them to explain why, never as a spec.

## Mobile web mechanics

- **Viewport units:** `min-height: 100vh; min-height: 100svh;` for layouts that must fit with browser chrome; `dvh` sparingly, because it relayouts as the URL bar moves. All Baseline Widely ([web.dev](https://web.dev/blog/viewport-units)). [S]
- **The keyboard is ignored by viewport units.** `interactive-widget=resizes-content` works in Chrome and Firefox for Android, not in any shipped Safari. Position keyboard-adjacent UI with `window.visualViewport` (Widely); the VirtualKeyboard API is Chromium-only. [S]
- **Never let a fixed bar cover the focused field** (WCAG [2.4.11](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html)): un-stick bottom bars while a field has focus, and set `scroll-padding` to the sticky header and footer heights. [S]
- **Safe areas:** `viewport-fit=cover` plus `padding-bottom: max(1rem, env(safe-area-inset-bottom))` on edge-anchored bars. [S]
- **Keyboards:** `type="email|tel|url|search"`, `inputmode`, `enterkeyhint`, `autocomplete` tokens; `one-time-code` triggers SMS-code suggestions. [S]
- **Hover is an enhancement.** Gate it behind `(hover: hover) and (pointer: fine)`; some devices misreport hover. [S]
- **Pressed state:** if you remove `-webkit-tap-highlight-color`, provide your own `:active` style. [C]
- **`position: sticky` fails silently** under any ancestor with `overflow: hidden|auto|scroll`; use `overflow: clip` when you only need clipping. [S]
- **iOS home-screen web apps in the EU:** Apple removed them in the iOS 17.4 betas and reversed that before release (March 2024). Every iOS browser and installed web app is still WebKit; there is no install prompt; push and badging work only once installed ([The Register](https://www.theregister.com/software/2024/03/02/apple-reverses-decision-to-remove-home-screen-web-apps-in-eu/307995), [OWA 2025 review](https://open-web-advocacy.org/blog/owa-2025-review/)). Build a progressively enhanced site and write your own "Add to Home Screen" instructions. [S]

## Responsive

- Breakpoints in rem where the content breaks, not at device widths; range syntax (`@media (width >= 40rem)`). [C]
- Components respond to their container (`container-type: inline-size`, Widely); the viewport only shapes the page shell. Container style queries became Baseline in May 2026. [S]
- Navigation transforms by size: bottom bar on compact screens, rail on medium, sidebar or top nav on wide. Material 3 Expressive deprecates the navigation drawer for an expanded rail ([Android adaptive navigation](https://developer.android.com/develop/adaptive-apps/guides/build-adaptive-navigation)). [S]
- **Feature parity:** change presentation on mobile, never remove features; people switch devices mid-task ([NN/g](https://www.nngroup.com/articles/mobile-first-not-mobile-only/)). [E]
- Images get `width` and `height` (or `aspect-ratio`), `srcset` with an accurate `sizes`, `loading="lazy"` only below the fold and never on the LCP image. [S]

## Platform primitives

| Feature | Status, October 2026 | Use and fallback |
| --- | --- | --- |
| `<dialog>` + `showModal()` | Widely | Every modal. Never `tabindex` on the dialog |
| `<dialog closedby>` | Limited (no stable Safari) | Backdrop-click handler as fallback |
| Popover API | Newly (Jan 2025) | Menus, pickers, non-modal overlays; not modal, no focus trap |
| `popover="hint"`, interest invokers | Limited | Enhancement only; never essential information |
| Invoker commands (`commandfor`/`command`) | Newly (Dec 2025) | Feature-detect `'command' in HTMLButtonElement.prototype` |
| CSS anchor positioning (core) | Interoperable since Jan 2026; dataset says Limited only for `position-visibility` | `@supports (anchor-name: --a)`, Floating UI fallback |
| Customizable `<select>` | Limited (no Firefox) | Falls back to a normal select by itself; don't build an ARIA listbox just to style one |
| `<details name>` | Newly | Exclusive accordion; older browsers allow several open |
| `field-sizing: content` | Newly (Jun 2026) | `rows` plus `resize: vertical` |
| `:user-invalid` / `:user-valid` | Widely | Error styling after interaction; still render text errors |
| `inert` | Widely | Off-canvas drawers |
| Same-document View Transitions | Newly (Oct 2025) | Feature-detect; reduced-motion branch |
| Cross-document View Transitions | Limited (no Firefox) | Pure enhancement |
| Container scroll-state queries | Limited (Chrome) | IntersectionObserver sentinel |
| `light-dark()`, relative colour, `:has()`, nesting | Newly to Widely | Safe |
| `@scope` | Newly (Mar 2026) | Naming conventions or CSS modules |
| Navigation API | Newly (Jan 2026) | History API + `popstate` |
| `ariaNotify()` | Newly (Sep 2026) | A polite live region |
| `scheduler.yield()` | Limited (no Safari) | `setTimeout(0)` fallback |

## Performance as UX

- **INP ≤ 200 ms at p75**: input delay + processing + paint to the next frame, for clicks, taps and keys ([web.dev INP](https://web.dev/articles/inp)). Paint the acknowledgement first (pressed state, spinner, optimistic row), then yield and do the work; split tasks over 50 ms ([web.dev long tasks](https://web.dev/articles/optimize-long-tasks)). [S]
- **CLS ≤ 0.1**: reserve final dimensions before skeletons; late banners, cookie bars and toasts that push content are the classic failures ([web.dev CLS](https://web.dev/articles/cls)). [S]
- **Perceived thresholds**: 0.1 s instant, 1 s flow, 10 s attention ([Nielsen](https://www.nngroup.com/articles/response-times-3-important-limits/)). Mutations should finish within about 500 ms or acknowledge immediately. [E][C]
- **React specifics:** non-urgent updates in `startTransition`, never controlled text input; Suspense boundaries follow the designed loading sequence, not one per component; `useOptimistic` for low-risk actions only ([react.dev](https://react.dev/reference/react/useTransition), [Suspense](https://react.dev/reference/react/Suspense)). [C]

## Single-page apps

- **On route change:** update `document.title` (WCAG [2.4.2](https://www.w3.org/WAI/WCAG22/Understanding/page-titled.html)), move focus to the new `<h1>` (`tabindex="-1"`) or a skip link, and announce the page politely. Focusing a heading tested best with screen-reader, magnifier, voice and switch users; resetting to the top was overwhelming ([Gatsby, Sutton 2019](https://www.gatsbyjs.com/blog/2019-07-11-user-testing-accessible-client-routing/)). [E]
- **Restore scroll on Back/Forward** after the content has rendered; scroll to top or the hash on push. [C]
- **Stay bfcache-eligible:** no `unload` handlers, `beforeunload` only while there are unsaved changes, refresh stale data on `pageshow` with `persisted` ([web.dev bfcache](https://web.dev/articles/bfcache)). [S]
- **Back closes a full-screen sheet on mobile**, because Android system Back follows history. [S]

## Platform conventions

Follow the platform you build for; on the open web follow web conventions (links look like links, browser Back works) instead of imitating one OS.

| Topic | Apple | Material / Android | Windows / Fluent | Web default |
| --- | --- | --- | --- | --- |
| Dialog button order | Confirm trailing, Cancel leading | Confirm trailing | Primary leftmost, Close rightmost | Pick one order and keep it everywhere |
| Destructive | Red role, never the default button | Error colour confirm, text Cancel | At least one safe action, Esc triggers it | Never the default; focus the safe action |
| Back | Visible top-leading Back plus edge swipe | System Back follows history; predictive back on by default for Android 16 targets | System Back | Browser Back must work and close overlays |
| Sheets | Swipe to dismiss; one at a time; Cancel leading, Done trailing; confirm if unsaved | Bottom sheets, scrim | Drawers in consistent positions | A bottom-sheet `<dialog>` mirroring these |
| Switch vs checkbox | Switches in list rows | Switch applies immediately | Toggle switch applies immediately | `role="switch"` applies immediately; checkboxes in forms with Save |

Sources: [Apple HIG buttons](https://developer.apple.com/design/human-interface-guidelines/buttons), [sheets](https://developer.apple.com/design/human-interface-guidelines/sheets), [alerts](https://developer.apple.com/design/human-interface-guidelines/alerts); [Microsoft dialogs](https://learn.microsoft.com/en-us/windows/apps/design/controls/dialogs-and-flyouts/dialogs); [Fluent 2 dialog](https://fluent2.microsoft.design/components/web/react/core/dialog/usage); [NN/g toggles](https://www.nngroup.com/articles/toggle-switch-guidelines/).

**Recent platform shifts:** iOS 26 Liquid Glass floated and minimised tab bars; NN/g documented legibility, target and discoverability problems ([NN/g](https://www.nngroup.com/articles/liquid-glass/)), and iOS 26.1 and 27 added a tinted mode, stronger diffusion and a transparency slider ([MacRumors](https://www.macrumors.com/2026/06/10/how-liquid-glass-is-changing-in-ios-27/)). Material 3 Expressive added button groups, split buttons, a FAB menu and docked toolbars; Google's Material Web components are in maintenance mode. Neither is a reason to put glass or expressive shapes into a web product UI.

## Keyboard and power users

- Focus rings on keyboard focus via `:focus-visible`, ≥ 3:1, never obscured. [S]
- **Single-character shortcuts** (`j`, `k`, `e`) must be switchable off, remappable to include a modifier, or active only while the component has focus, and never fire inside text fields (WCAG [2.1.4](https://www.w3.org/WAI/WCAG22/Understanding/character-key-shortcuts.html)). Speech users trigger them by dictating. [S]
- **Conventions:** `Ctrl/⌘ K` or `/` for search or commands, `?` for a shortcut sheet, `Esc` to close, `Ctrl/⌘ Enter` to submit multi-line text. Never override browser, OS or screen-reader keys ([MDN aria-keyshortcuts](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-keyshortcuts)). [C]
- **Make shortcuts visible** in tooltips, menus and the command palette, and add `aria-keyshortcuts`. Unseen shortcuts don't exist for most people. [C]
- **A command palette accelerates experts but is not discoverable**: add it on top of visible navigation, never instead of it, and show each command's shortcut in its row ([cmdk](https://github.com/pacocoursey/cmdk), [APG combobox](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/)). [C]
- **Composite widgets** (tabs, menus, grids, toolbars) are one tab stop with arrow keys inside, using roving tabindex ([APG keyboard](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/)). [S]
- **Efficiency features for repeat users:** sensible defaults that remember the last choice, bulk actions, saved and shareable views, inline edit, keyboard paths for the top tasks. Measure them with KLM in [evaluation.md](evaluation.md#klm-estimates). [C]
