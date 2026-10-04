# Accessibility: the floor for product UI

WCAG 2.2 AA is the build target. It is a floor, not a quality bar: an interface can pass every criterion and still be hard to use, and a clean automated scan is not a conformance claim.

Contents: legal status · the criteria product UI fails most · ARIA and widgets · focus management · the keyboard-only gate · what automation can't see

## Legal status (October 2026)

| Fact | Source |
| --- | --- |
| The European Accessibility Act (Directive 2019/882) has applied since 28 June 2025 to products and services placed on the market after that date: e-commerce, banking, e-books, transport ticketing, telecoms and more. Microenterprises are exempt for services, not products; existing service contracts have transition periods to 2030. In the Netherlands the ACM enforces most services | [EUR-Lex](https://eur-lex.europa.eu/eli/dir/2019/882/oj) |
| EN 301 549 v4.1.1 (published September 2026) references WCAG 2.2 AA but is not yet cited in the Official Journal; until it is, v3.2.1 (WCAG 2.1 AA) gives presumption of conformity. Build to 2.2 AA now: it is a superset except for the removed 4.1.1 | [AccessibleEU](https://accessible-eu-centre.ec.europa.eu/content-corner/news/european-accessibility-standard-en-301-549-has-been-updated-2026-09-07_en) |
| WCAG 3 is a Working Draft (latest 10 September 2026); no law references it. Don't design "to WCAG 3", and APCA contrast is not normative | [W3C](https://www.w3.org/WAI/news/2026-09-10/wcag3/) |

This is a design floor, not legal advice. Escalate real compliance questions to whoever owns them.

## The criteria product UI fails most

| SC (level) | Floor | Typical product failure | Fix |
| --- | --- | --- | --- |
| [1.1.1](https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html) Non-text content (A) | Text alternative | Icon-only buttons, avatars, status icons | Accessible name; `alt=""` for decoration |
| [1.3.1](https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html) Info and relationships (A) | Structure in markup | Placeholder or loose text as label; div tables; fake headings | `<label for>`, `<th scope>`, real headings, `<fieldset>` + `<legend>` for groups |
| [1.3.5](https://www.w3.org/WAI/WCAG22/Understanding/identify-input-purpose.html) Input purpose (AA) | `autocomplete` tokens | `autocomplete="off"` on sign-in and address | Matching tokens |
| [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) Use of colour (A) | Not colour alone | Red border as the only error; status dots | Text, icon, shape |
| [1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) / [1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) Contrast (AA) | 4.5:1 text, 3:1 UI | Grey placeholders, pale input borders, faint selected state | Token pairs checked in both themes |
| [1.4.4](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html) / [1.4.10](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) Resize, reflow (AA) | 200 %; no 2-D scroll at 320 px | Fixed-height panels, blocked zoom, sideways tables | Intrinsic sizing; scroll regions only for tables, code, maps |
| [1.4.12](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) Text spacing (AA) | Survives the override | Clipped buttons and badges | No fixed heights on text containers |
| [1.4.13](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html) Hover or focus content (AA) | Dismissible, hoverable, persistent | Tooltips that vanish or cover | Esc dismisses; pointer can move onto it |
| [2.1.1](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html) Keyboard (A) | Everything operable by keyboard | Clickable divs, drag-only reorder, hover menus | Native controls; keyboard alternatives |
| [2.1.4](https://www.w3.org/WAI/WCAG22/Understanding/character-key-shortcuts.html) Character key shortcuts (A) | Can be switched off or scoped | Single-key shortcuts firing while typing | Modifier, off switch, or focus scope |
| [2.2.1](https://www.w3.org/WAI/WCAG22/Understanding/timing-adjustable.html) Timing adjustable (A) | Time limits adjustable | Session expiry that loses a form; auto-dismissed toasts with actions | Warn and extend; keep input; persistent messages |
| [2.4.3](https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html) Focus order (A) | Logical order | Positive `tabindex`; dialogs that don't take focus | DOM order; managed focus |
| [2.4.7](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html) Focus visible (AA) | Visible indicator | `outline: none` | `:focus-visible` ring token |
| [2.4.11](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html) Focus not obscured (AA) | Not entirely hidden | Sticky headers, cookie bars, chat widgets | `scroll-padding`; un-stick while typing |
| [2.5.7](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html) Dragging (AA) | Non-drag alternative | Kanban, sortable lists, sliders, column resize | Move menu, up/down buttons, track click |
| [2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) Target size (AA) | 24 × 24 or spacing | Row actions, close buttons, pagination dots | Pad the hit area |
| [3.2.2](https://www.w3.org/WAI/WCAG22/Understanding/on-input.html) On input (A) | No surprise context change | Select that navigates on change | Explicit button |
| [3.2.6](https://www.w3.org/WAI/WCAG22/Understanding/consistent-help.html) Consistent help (A) | Same relative place | Help link moving between pages | Fixed layout slot |
| [3.3.1](https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html) / [3.3.3](https://www.w3.org/WAI/WCAG22/Understanding/error-suggestion.html) Errors (A/AA) | Identified in text, with a fix | "Invalid input" | Cause and fix; see [content.md](content.md) |
| [3.3.4](https://www.w3.org/WAI/WCAG22/Understanding/error-prevention-legal-financial-data.html) Error prevention (AA) | Reversible, checked or confirmed | One-click payment or deletion | Review step, undo or confirmation |
| [3.3.7](https://www.w3.org/WAI/WCAG22/Understanding/redundant-entry.html) Redundant entry (A) | No re-typing in one process | Cleared form after an error; re-asking the address | Keep and pre-fill |
| [3.3.8](https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html) Accessible authentication (AA) | No cognitive test without an assist | Blocked paste, per-digit OTP boxes, puzzle CAPTCHAs | Paste, managers, passkeys, `one-time-code` |
| [4.1.2](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html) Name, role, value (A) | Exposed to assistive tech | Custom toggles without state; `aria-hidden` on focusable | Native elements or full ARIA |
| [4.1.3](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) Status messages (AA) | Announced without focus | Silent toasts, result counts, "Saved" | Live regions present at load |

Aim for 2.4.13 Focus Appearance (AAA: ≥ 2 px perimeter, ≥ 3:1 change) as the house focus style anyway.

## ARIA and widgets

- **First rule of ARIA:** a native element with the semantics you need beats ARIA. Don't change native semantics, keep every ARIA control keyboard-operable, never hide a focusable element ([Using ARIA](https://www.w3.org/TR/using-aria/)). Pages with ARIA average more detected errors than pages without ([WebAIM Million](https://webaim.org/projects/million/)): no ARIA beats bad ARIA.
- **Composite widgets** are one tab stop with arrows inside, via roving tabindex or `aria-activedescendant` ([APG keyboard](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/)).
- **Tabs** switch views within a page; if each tab has its own URL, it is navigation: links with `aria-current` ([APG tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)).
- **Disclosure** (`<button aria-expanded>` or `<details>`) covers show/hide and navigation submenus. `menu`/`menubar` are for application command menus only.
- **Combobox** follows the APG pattern exactly, with the result count in a polite status region ([APG combobox](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/)).
- **Switch** is `<input type="checkbox" role="switch">` and applies immediately.
- **Use the library's accessible primitive** (React Aria, Base UI, Radix, Ark UI, Headless UI) before writing a widget, and test its keyboard map rather than assuming it.

## Focus management

| Moment | Focus goes to | Source |
| --- | --- | --- |
| Dialog opens | First control, or a static element at the top for long content; the safe button for destructive dialogs | [APG dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) |
| Dialog closes | The control that opened it (or the next logical one if it was deleted) | APG |
| Submit with errors | The error summary | [GOV.UK](https://design-system.service.gov.uk/components/error-summary/) |
| Route change | New `<h1>` or a skip link, with a polite announcement | [Gatsby 2019](https://www.gatsbyjs.com/blog/2019-07-11-user-testing-accessible-client-routing/) |
| Item deleted from a list | Next item, else previous, else the list heading or empty state | Convention |
| Content loaded inline (Load more) | Stay put; announce the count; first new item gets focus only if the user asked to move there | Convention |
| Panel or drawer (non-modal) | Into the panel when opened by keyboard; no focus trap | APG |

Skip link first in the tab order ([WCAG 2.4.1](https://www.w3.org/WAI/WCAG22/Understanding/bypass-blocks.html)). Sticky chrome never covers the focused element.

## The keyboard-only gate

Before calling any flow done, complete its primary task with the keyboard alone, from entry to confirmation, including error recovery and the destructive path. Record pass or fail per step. A flow that fails this gate is not shippable, whatever the scan says.

Checklist per step: reachable by Tab in a logical order; visible focus; operable with Enter, Space, arrows or Esc as the pattern expects; nothing obscured; announcements for status changes; focus lands somewhere sensible after every action.

## What automation can't see

axe-core finds roughly half of WCAG issues, and its "incomplete" results need a person ([axe-core](https://github.com/dequelabs/axe-core)). A Lighthouse accessibility score of 100 is not conformance. Automation can't judge whether:

- an accessible name is meaningful;
- the focus order matches the task;
- an error message helps;
- a live region is too chatty;
- the reading order of a reflowed layout makes sense;
- a screen-reader user can finish the task.

The last needs a screen-reader pass at minimum, and real users with disabilities for anything you would claim publicly. Report which of these you exercised.
