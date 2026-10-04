# Visual system: hierarchy, scales, tokens, components

Product UI earns trust through familiarity and consistency, not novelty. If the save button looks different in two places, one of them is wrong. For marketing pages, art direction and distinctiveness, load `expressive-design` instead.

Tiers: **[S]** standard · **[E]** empirical · **[C]** convention or taste default (override with a reason).

Contents: use what exists · hierarchy · scales · type · colour · tokens · component states · primitives · icons · charts · system governance · polish

## Use what exists

1. **Read first.** Look for a design contract (`DESIGN.md`, `system.md`, tokens files, Storybook, the component directory, `components.json`) and the three most similar existing screens. The existing system is the authority; a brownfield product's users have already learned it.
2. **Ladder for controls:** native element → the project's component → a proven headless primitive → hand-rolled, and a hand-rolled control owes the full keyboard, focus and ARIA contract.
3. **Ladder for styling:** existing component variant → semantic token → new token → one-off value. A one-off is a missing variant; record it.
4. **Extract on the second real reuse**, not the first; promote a local token to global once about three components use it ([Curtis](https://nathanacurtis.substack.com/p/naming-tokens-in-design-systems-9e86c7444676)). [C]
5. **Persist decisions** with concrete values (button height, padding, radius, type step) in the repository's design contract, and check new work for drift against it.

## Hierarchy

- **De-emphasize to emphasize.** When the primary thing doesn't stand out, quiet its competitors with weight and colour before enlarging it ([Refactoring UI](https://www.refactoringui.com/book)). [C]
- **Weight and colour before size.** Two weights and about three text colours (default, muted, subtle) cover most product UI; nothing under 400 weight for UI text. [C]
- **Labels are a last resort.** Drop self-evident labels (email, price), merge label into value ("12 left in stock"), or mute the label; emphasise labels only where people scan for them, as in spec sheets ([Refactoring UI](https://refactoringui.com/previews/labels-are-a-last-resort)). [C]
- **Visual hierarchy is separate from document hierarchy.** The `<h1>` need not be the largest thing on an app screen, but heading order stays correct for assistive tech. [S]
- **Group by proximity.** Space between groups is clearly larger than space within them. [E] (Gestalt; see [evaluation.md](evaluation.md#laws-and-folklore))
- **The operator test.** Could someone understand the screen from headings, labels and numbers alone? Section headings say what the area is or what can be done there ("Plan status"), in utility copy, never marketing copy. [C]

## Scales

Put every scalar on a short scale: space, size, radius, type, shadow, opacity, z-index.

| Scale | Default (taste; follow the project's if one exists) | Source |
| --- | --- | --- |
| Space | 2, 4, 8, 12, 16, 24, 32, 48, 64, 80; adjacent steps ≥ ~25 % apart above 8 | [Atlassian space tokens](https://atlassian.design/foundations/spacing), Refactoring UI |
| Radius | 0, 4, 8, 12, full; nested corners: outer = inner + padding | [concentric radius](https://uxplanet.org/corner-radius-of-nested-elements-in-ui-design-4c27bb24a854) |
| Elevation | ~5 levels meaning "closer to the user" (card < dropdown < dialog); borders for structure, shadows for elevation | Refactoring UI |
| Layers | Named z-index tokens: base, dropdown, sticky, overlay, toast | — |
| Density | Comfortable default; compact as a user opt-in token swap (`[data-density=compact]`) for tables and lists, never for dialogs or touch | [Material density](https://m2.material.io/design/layout/applying-density.html) |

A 4/8 grid alone doesn't help choose between 120 and 124; a scale with gaps does. These numbers are defaults, not facts: the surveyed skills contradict each other on spacing grids, press scales and durations.

## Type

- **Fewer sizes in apps.** A productive set of six to eight steps with fixed headings; fluid display type belongs on marketing pages. Carbon's productive set uses a 14 px base, the expressive set 16 px ([Carbon type sets](https://carbondesignsystem.com/elements/typography/type-sets/)). [S]
- **Body copy 16 px; 14 px acceptable for dense chrome and tables at high contrast; 12 px only for metadata.** [C]
- **Form fields compute to ≥ 16 px on touch** or iOS Safari zooms on focus; step down only inside `(pointer: fine)`. Never fix this by blocking zoom. [S]
- **`tabular-nums`** for anything compared vertically or updating in place (tables, money, timers). [C]
- **Wrap by default, truncate by exception.** Before truncating ask: can it wrap, get more room, or disclose progressively? When truncating, the full value stays reachable by keyboard, touch, screen reader and at 200 % zoom; `title` doesn't count ([Primer truncate](https://primer.style/product/components/truncate/accessibility/)). [S]
- **Pick a truncation per field:** wrap identifying text; end-truncate secondary metadata; middle-truncate values that differ at the end (file names, hashes, emails on one domain); clamp previews with "Show more"; never truncate numbers, amounts, dates or anything compared. [C]
- **UI line height** about 1.25–1.45, prose 1.5, and it must survive the 1.4.12 text-spacing override ([WCAG 1.4.12](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html)). [S]
- **Mixed sizes align on the baseline.** `text-wrap: balance` for headings (Baseline); `pretty` is an enhancement (no Firefox). [C]
- **Real characters:** `…` for commands that need more input and for in-progress states ("Rename…", "Saving…"), `×` for dimensions, en dash for ranges, a non-breaking space before units. [C]

## Colour

| Rule | Tier | Source |
| --- | --- | --- |
| Components consume semantic tokens only: canvas, surface, raised, border, text (default, muted, on-emphasis), accent, and status (success, warning, danger, info) each with muted and emphasis variants | [C] | [Primer colour usage](https://primer.style/product/getting-started/foundations/color-usage/) |
| Never colour alone: status gets an icon or text; links in prose get an underline; errors get text | [S] | WCAG [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) |
| Text 4.5:1 (3:1 large); input borders, toggles, focus rings, meaningful icons, chart marks and the selected-versus-unselected difference 3:1 | [S] | [1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), [1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html). A `#e5e7eb` border on white is ~1.2:1 |
| One focus-ring token everywhere: ≥ 2 px, ≥ 3:1, offset, never obscured | [S] | [2.4.7](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html), [2.4.11](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html), [2.4.13](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html) |
| Dark mode is a separately tuned set: no pure black, raised surfaces lighter, accents desaturated, every pairing re-checked | [C] | Material dark theme guidance |
| Light mode reads better for most people; honour `prefers-color-scheme` and offer a toggle | [E] | [NN/g dark mode](https://www.nngroup.com/articles/dark-mode/) |
| `color-scheme: light dark` plus `light-dark()` so native controls follow the theme | [S] | [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme) |
| `forced-colors: active` drops backgrounds and shadows: give background-only components a transparent border; never carry focus by shadow | [S] | [MDN forced-colors](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors) |
| Interaction states from one rule (a state layer: hover ~8 %, focus and pressed ~10 % of the on-colour) instead of a hand-picked hex per component | [C] | [M3 state layers](https://m3.material.io/foundations/interaction/states/state-layers) |
| No translucent chrome over arbitrary content without an opaque fallback; `prefers-reduced-transparency` is Chromium-only, so opaque is the default | [E] | NN/g on Liquid Glass legibility ([NN/g](https://www.nngroup.com/articles/liquid-glass/)) |

Contrast pass/fail is WCAG 2.2. APCA is not a conformance standard; use it only as a secondary check for thin or light-on-dark text.

## Tokens

The W3C Design Tokens Community Group format reached its first stable version, **2025.10**, on 28 October 2025, as a Community Group report rather than a W3C Recommendation ([announcement](https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/), [format](https://www.designtokens.org/tr/2025.10/format/)).

- `.tokens.json` files; a token is an object with `$value` and optional `$type`, `$description`, `$deprecated`, `$extensions`.
- Aliases are `"{group.token}"`; `$ref` JSON Pointers address parts of a value; groups support `$extends` and `$root`.
- `dimension` values are objects (`{"value": 16, "unit": "px"}`); colours are objects with a colour space (OKLCH, Display P3 and others).
- Themes, modes, brands and density go in a separate **resolver** file (`.resolver.json`): sets, modifiers with contexts, a resolution order ([resolver](https://www.designtokens.org/tr/2025.10/resolver/)).
- Tooling is partial: Style Dictionary v5 covers most of it; Figma's export drops composite tokens and descriptions. Check before promising round-trips.

**Tiers:** primitive (`blue-500`) → semantic (`bgColor-danger-emphasis`) → component (`button-primary-bg-hover`) only where needed. Components never reference primitives. **Names:** namespace → object → base → modifier; theme and mode are separate axes ([Curtis](https://nathanacurtis.substack.com/p/naming-tokens-in-design-systems-9e86c7444676)).

## Component states

Every interactive component specifies this matrix before it ships. Screen-level states (empty, partial, offline, no permission) are in [states.md](states.md).

| State | Visual | Semantics |
| --- | --- | --- |
| default | Boundary ≥ 3:1 against its surroundings | Native element or correct role |
| hover | Subtle layer, only under `(hover: hover)`, never the only cue | Hides nothing unreachable otherwise |
| focus-visible | The ring token | `:focus-visible` |
| active / pressed | Immediate (< 100 ms) change | — |
| selected / current | More than colour (check, weight, bar); ≥ 3:1 difference | `aria-selected`, `aria-pressed`, `aria-current`, `checked` |
| disabled | Prefer not disabling; else `aria-disabled` and the reason | Native `disabled` leaves the tab order |
| read-only | Looks like text, selectable, copyable; distinct from disabled | `readonly`, still focusable |
| loading / busy | Same dimensions, label kept or announced | `aria-busy`, completion announced |
| error | Message beside it + icon + colour | `aria-invalid`, `aria-describedby` |
| empty | Says what goes here and how to fill it | — |
| overflow | Wraps, survives 3× text length and long compounds | Reflows at 320 px and 200 % |

## Primitives

Status as of October 2026; the full table with fallbacks is in [platform.md](platform.md#platform-primitives).

- **Native first:** `<dialog>` for modals, `popover` for menus and pickers, `<details name>` for accordions, invoker commands (`commandfor`/`command`, Baseline since December 2025) for declarative open and close, customizable `<select>` (Chrome and Safari; it falls back to a normal select).
- **Headless libraries for the rest**, and never hand-roll a combobox, menu, date picker or dialog focus manager when a primitive exists. React Aria has the deepest interaction and i18n engineering; Base UI reached 1.0 in December 2025 and became shadcn/ui's default in July 2026, with Radix still supported; Ark UI spans React, Solid, Vue and Svelte ([shadcn changelog](https://ui.shadcn.com/docs/changelog), [Ark UI](https://ark-ui.com/)).
- **shadcn-style ownership** means the copied source is yours, including upgrades and drift.
- Server-rendered stacks (Blade, Rails, Django, Livewire, HTMX) get the same rules through native elements and small enhancements; nothing here requires React.

## Icons

- Icon plus visible label by default. Only a few icons are universally recognised (home, print, search, and close in context); the rest are ambiguous ([NN/g icon usability](https://www.nngroup.com/articles/icon-usability/)). [E]
- Icon-only buttons need an accessible name that matches the tooltip, and the visible label must be part of that name for speech users (WCAG [2.5.3](https://www.w3.org/WAI/WCAG22/Understanding/label-in-name.html)). Decorative icons get `aria-hidden="true"`. [S]
- One family on one grid: fixed canvas, consistent stroke, filled meaning selected where that convention holds. Hit area ≥ 24 px even for a 16 px glyph. [C][S]

## Charts in product UI

Table when people look up or compare individual values; chart when the shape is the message (trend, exception). Single values as stat tiles with label, delta, period and comparison basis, not gauges. Avoid dual axes. Colour-blind-safe palettes (Okabe–Ito categorical, viridis sequential), direct labels over legends, zero baseline for bars, and empty, loading and error states for every chart. For chart construction load the `dataviz` skill.

## System governance

- **Component or pattern?** A component when UI and behaviour recur and the API can stay stable; a pattern (a documented recipe) when the arrangement varies by context: empty states, filtering a table, bulk actions. [C]
- **Docs per component:** purpose, when not to use it and what to use instead, anatomy, variants, the state matrix, content rules, do and don't pairs, keyboard map, tokens consumed ([GOV.UK component docs](https://design-system.service.gov.uk/components/)). [C]
- **Consistency beats local optimisation** by default; deviate only with evidence that the local need is real and repeated, then feed it back into the system ([Jakob's law](https://www.nngroup.com/videos/jakobs-law-internet-ux/)). Detached or overridden components are signals of missing variants. [C]
- **Vendor research is not neutral evidence.** Material 3 Expressive's "up to 4× faster" claim is unpublished, vendor-run and a best case against Google's own baseline ([Google Design](https://design.google/library/expressive-material-design-google-research)); the lesson that holds up is that a dominant primary action helps, which is plain hierarchy. [E]

## Polish

- `scrollbar-gutter: stable` on containers whose overflow toggles; `overscroll-behavior: contain` on dialogs, drawers and chat panes. [C]
- Hover effects only inside `@media (hover: hover) and (pointer: fine)`; every tappable element gets an `:active` state. [C]
- Reserve space for late content (images by `aspect-ratio`, error messages, loading buttons that keep their width) so nothing shifts. [S] (CLS)
- Motion in product UI is gated by frequency: anything used many times a day or triggered by the keyboard gets no animation; data people read never moves for style; motion is never the only feedback; reduced motion swaps movement for a fade. [C] For expressive motion and its contract, load `expressive-design`.
