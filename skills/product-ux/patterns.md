# Patterns: forms, actions, navigation, feedback, data, search, onboarding, settings

Tiers: **[S]** standard or live-service-tested design system · **[E]** empirical study or large audit · **[C]** convention or expert opinion. Where good sources disagree, the conflict is written out; pick by context and record why.

Contents: forms · actions · navigation · feedback · data-dense UI · search · onboarding · settings and permissions

## Forms

| Rule | Tier | Evidence |
| --- | --- | --- |
| Cut fields before styling them. The best optional field is the deleted one | [E] | Average checkout has 11.3 fields against a reachable 8; ~17 % have abandoned an order over a long checkout ([Baymard](https://baymard.com/blog/checkout-flow-average-form-fields)) |
| Labels above fields; label closer to its own field than to the one above | [E] | Eye-tracking: one saccade versus ~500 ms label-to-field with left labels ([Penzo](https://www.uxmatters.com/mt/archives/2006/07/label-placement-in-forms.php)). Directional only: no n reported, stripped forms |
| Never use the placeholder as the label, nor for hints | [E][S] | Seven harms: vanishes, can't be checked, looks pre-filled ([NN/g](https://www.nngroup.com/articles/form-design-placeholders/)); not read by all screen readers, fails contrast ([GOV.UK](https://design-system.service.gov.uk/components/text-input/)) |
| Single column; only tightly paired short fields share a row (city + postcode) | [E] | Multi-column forms get skipped and misread ([Baymard](https://baymard.com/blog/avoid-multi-column-forms)) |
| Hint between label and input, tied with `aria-describedby` | [S] | [GOV.UK text input](https://design-system.service.gov.uk/components/text-input/) |
| Right `autocomplete` token on every personal-data field | [S] | WCAG [1.3.5](https://www.w3.org/WAI/WCAG22/Understanding/identify-input-purpose.html); autofill is the biggest mobile speed-up |
| `inputmode="numeric"` on a text input for codes, cards and PINs; `type=number` only for true counters | [S] | Scroll-wheel changes, strips leading zeros, engine differences ([GOV.UK](https://design-system.service.gov.uk/components/text-input/)) |
| Field width signals answer length (4-character year, postcode-sized postcode) | [S] | [GOV.UK widths](https://design-system.service.gov.uk/components/text-input/) |
| Accept formats leniently, normalise on the server; never mask or reformat what was typed | [E] | 89 % ignore format examples and type their own way ([Baymard](https://baymard.com/blog/input-fields)) |
| One "Full name" field by default; no title field; Unicode, no short caps | [E][S] | 42 % typed their full name into "First name" ([Baymard](https://baymard.com/blog/checkout-flow-average-form-fields)); [GOV.UK names](https://design-system.service.gov.uk/patterns/names/); [falsehoods about names](https://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names/) |
| Memorable dates as three fields; a picker only for near dates, always beside a text input | [S] | [GOV.UK dates](https://design-system.service.gov.uk/patterns/dates/) |
| Phone is one `type=tel` field | [S] | Split fields break paste and autofill ([GOV.UK](https://design-system.service.gov.uk/patterns/telephone-numbers/)) |
| Address lookup with a manual fallback; hide "line 2" behind a link | [E] | 30 % hesitate at line 2 ([Baymard](https://baymard.com/blog/checkout-flow-average-form-fields)); [GOV.UK addresses](https://design-system.service.gov.uk/patterns/addresses/) |

**Required versus optional (sources disagree).** GOV.UK marks only optional fields with "(optional)" and bans asterisks ([GOV.UK](https://design-system.service.gov.uk/patterns/question-pages/)). Baymard found 32 % hit errors when only optional fields were marked and recommends marking both ([Baymard](https://baymard.com/blog/required-optional-form-fields)). Cut optional fields first; on a mostly-required form mark the exceptions "(optional)"; on a long mixed form, mark both. Never by colour or asterisk alone.

**Validation timing (sources disagree).** Inline validation beat submit-only by +22 % success and −42 % time, on-blur beat on-keystroke, and on-focus was worst (Wroblewski with Etre, n=22, [A List Apart](https://alistapart.com/article/inline-validation-in-web-forms/)). GOV.UK and Adam Silver default to submit-only because live validation interrupts, floods screen readers and misfires ([GOV.UK](https://design-system.service.gov.uk/patterns/validation/), [Silver](https://adamsilver.io/blog/live-validation-is-problematic/)). Use:

- **Short or one-question pages:** validate on submit.
- **Long forms:** add on-blur checks for hard, format-checkable fields (username availability, IBAN, card Luhn), and skip easy ones.
- **Reward early, punish late:** an error clears on the keystroke that fixes it; a new error waits for blur ([Baymard](https://baymard.com/research-articles/inline-form-validation)). Never flag an empty field on blur.
- **Always validate again on submit and on the server.**

**On submit with errors** [S]: an error summary at the top headed "There is a problem", linking to each field, receives focus; the `<title>` gains "Error: "; each field shows the same wording inline with `aria-describedby` ([GOV.UK error summary](https://design-system.service.gov.uk/components/error-summary/), [error message](https://design-system.service.gov.uk/components/error-message/)). Keep every typed value, including card numbers (WCAG [3.3.7](https://www.w3.org/WAI/WCAG22/Understanding/redundant-entry.html); 34 % of sites clear them, [Baymard](https://baymard.com/research-articles/preserve-card-details-on-error)). Copy rules for the messages live in [content.md](content.md).

**Passwords and sign-in** [S]: no composition rules, no forced rotation, minimum 15 characters as a single factor (8 with MFA), allow at least 64, check a breached-password blocklist, allow paste and managers, offer show-password, drop "confirm password" ([NIST 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html)). No cognitive test without an assist: paste for one-time codes, `autocomplete="one-time-code"`, passkeys, no per-digit boxes that block paste (WCAG [3.3.8](https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html)).

**Multi-step** [S]: start with one thing per page, a Back link, "Continue", and a Check-your-answers page with Change links that return to it ([GOV.UK question pages](https://design-system.service.gov.uk/patterns/question-pages/), [check answers](https://design-system.service.gov.uk/patterns/check-answers/)). Defer account creation until after the transaction ([Baymard](https://baymard.com/lists/cart-abandonment-rate)). Warn before unsaved work is lost; autosave long forms.

**Don't disable submit** [S][C]: keep it enabled and explain errors on click. Disabled buttons give no reason, fail contrast by exemption and drop out of the tab order ([GOV.UK](https://design-system.service.gov.uk/components/button/), [Axess Lab](https://axesslab.com/disabled-buttons-suck/), [Roselli](https://adrianroselli.com/2024/02/dont-disable-form-controls.html)). If something must look unavailable, use `aria-disabled="true"` plus the reason. Disable only while the request is in flight, and make the server idempotent.

## Actions

| Rule | Tier | Evidence |
| --- | --- | --- |
| Label with verb + object naming the result ("Save changes", "Delete 3 invoices"); never OK/Yes/Submit | [S][C] | [NN/g](https://www.nngroup.com/articles/ok-cancel-or-cancel-ok/); the label reflects the state the system moves into |
| One primary action per view; secondary as outline or link | [E] | A visually recessive Cancel prevented accidental cancels (n=23, [LukeW](https://www.lukew.com/ff/entry.asp?571)) |
| Destructive actions away from frequent benign ones, signalled by more than colour, never the default button | [S] | [NN/g proximity](https://www.nngroup.com/articles/proximity-consequential-options/); [Apple HIG buttons](https://developer.apple.com/design/human-interface-guidelines/buttons) |
| `<a href>` navigates, `<button>` acts; never `<div onclick>` | [S] | [Using ARIA](https://www.w3.org/TR/using-aria/); only real links open in a new tab |
| Acknowledge within 0.1 s: label becomes "Saving…", width stays fixed, completion announced | [E] | [Nielsen response limits](https://www.nngroup.com/articles/response-times-3-important-limits/); unacknowledged clicks get retried and duplicated |
| Prevent double submit in the client *and* with a server idempotency key | [S] | [GOV.UK button](https://design-system.service.gov.uk/components/button/); [Stripe idempotency](https://docs.stripe.com/api/idempotent_requests) |
| Unavailable because of role or plan? Say so and name who can ("Only admins can delete. Ask Sam.") | [C] | Beats a silent disabled control |

**Undo beats confirm** for frequent reversible actions (archive, move to trash), because confirmations become habit clicks ([NN/g](https://www.nngroup.com/articles/confirmation-dialog/)). Confirm only serious, irreversible or costly actions, and make the dialog specific: "Delete 'Q3 report' and its 14 comments? This can't be undone", with buttons "Delete report" / "Keep report", focus on the safe one ([APG dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)). Typed-name confirmation for the most dangerous (delete workspace).

## Navigation

| Rule | Tier | Evidence |
| --- | --- | --- |
| Desktop: show the main navigation; no hamburger | [E] | Hidden nav used 27 % versus 48 % visible, ≥39 % slower (n=179, [NN/g](https://www.nngroup.com/articles/hamburger-menus/)) |
| Mobile: 3–5 labelled destinations in a bottom bar; menu only beyond that, labelled "Menu" | [E][S] | Same study: 57 % versus 86 % on mobile; [Apple HIG tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars) |
| Site nav is `<nav>` + lists + links with disclosure buttons, never ARIA `menu`/`menubar` | [S] | APG's own caveat ([APG](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/examples/disclosure-navigation/), [Roselli](https://adrianroselli.com/2017/10/dont-use-aria-menu-roles-for-site-nav.html)) |
| Group and label from evidence: card sort (~15 people) to generate, tree test to evaluate | [E] | [NN/g card sorting](https://www.nngroup.com/articles/card-sorting-how-many-users-to-test/), [tree testing](https://www.nngroup.com/articles/tree-testing/) |
| Specific, front-loaded labels; no "More", "Learn more", clever brand terms | [E] | Information foraging ([Pirolli & Card](https://doi.org/10.1037/0033-295X.106.4.643), [NN/g scent](https://www.nngroup.com/articles/information-scent/)) |
| URL is state: filters, sort, tab, page, selected record, open panel each get a URL; Back closes overlays and restores scroll | [E] | 59 % of sites break a Back expectation ([Baymard](https://baymard.com/blog/back-button-expectations)) |
| Deep links work cold, after login, without bouncing to home | [C] | Follows from URL as state |
| Breadcrumbs show hierarchy, not history; last item is current, not a link | [C][S] | [NN/g](https://www.nngroup.com/articles/breadcrumbs/), [APG](https://www.w3.org/WAI/ARIA/apg/patterns/breadcrumb/) |

The number of top-level items is decided by tasks, not by a memory-span rule; see [evaluation.md](evaluation.md#laws-and-folklore).

## Feedback

| Rule | Tier | Evidence |
| --- | --- | --- |
| Default to inline feedback where the change happened, or a persistent banner for page-level outcomes | [S] | Primer discourages toasts ([Primer](https://primer.style/accessibility/patterns/accessible-notifications-and-messages/)); [GOV.UK banner](https://design-system.service.gov.uk/components/notification-banner/) |
| If a toast: no buttons inside, ≥ 6 s with pause on hover and focus, a reopenable history, text sent to a live region that already exists | [S][C] | Auto-dismiss fails 2.2.1 ([Roselli](https://adrianroselli.com/2020/01/defining-toast-messages.html)); [Byrne-Haber](https://www.sheribyrnehaber.com/designing-toast-messages-for-accessibility/) |
| Status messages are programmatic: `role="status"` for results, `role="alert"` for errors, region rendered empty at load | [S] | WCAG [4.1.3](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) |
| Latency: < 0.1 s nothing; ~1 s subtle cue; 2–10 s spinner or skeleton; > 10 s determinate progress, cancel, keep working | [E] | [Nielsen](https://www.nngroup.com/articles/response-times-3-important-limits/); animated progress made people wait ~3× longer ([NN/g](https://www.nngroup.com/articles/progress-indicators/)) |
| Don't flash a loader: show after ~300 ms, keep ≥ ~500 ms once shown; skeletons mirror final layout | [C] | No primary study; follows from the limits above ([NN/g skeletons](https://www.nngroup.com/articles/skeleton-screens/)) |
| Optimistic updates only for high-success, reversible actions; visible rollback with the reason and a retry | [C] | Never for payments or irreversible deletes ([React useOptimistic](https://react.dev/reference/react/useOptimistic)) |
| Success messages persist rather than fade | [E] | Fading ticks made users think the field broke again ([Wroblewski](https://alistapart.com/article/inline-validation-in-web-forms/)) |
| Empty states, by kind: first use (value + one action, optional labelled sample data), no results (echo query, offer a way out), cleared ("All done"), error, no permission | [C] | [NN/g empty states](https://www.nngroup.com/articles/empty-state-interface-design/) |
| Modal only to prevent critical errors or for a short task the user started; never modal on modal, never for upsell | [C] | [NN/g modals](https://www.nngroup.com/articles/modal-nonmodal-dialog/) |
| Native `<dialog>` + `showModal()`: inert background, Esc closes, visible title and close button, focus returns to the trigger | [S] | [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog), [APG](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) |
| Tooltips never carry essential information; open on hover and focus; dismissible, hoverable, persistent; no `title`-only tips | [S] | WCAG [1.4.13](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html); [NN/g](https://www.nngroup.com/articles/tooltip-guidelines/) |
| Notifications: separate transient ("Saved") from actionable ("Sam requested review"); actionable items persist with read state; channels set in settings | [C] | Primer + Byrne-Haber |

## Data-dense UI

| Rule | Tier | Evidence |
| --- | --- | --- |
| Right-align numbers, `tabular-nums`, units in the header, consistent decimals | [C] | Long-standing convention ([Few](https://www.perceptualedge.com/articles/Whitepapers/Communicating_Numbers.pdf)); no controlled study |
| First column is a human-readable identifier; sticky header (and key column) beyond the viewport | [C] | [NN/g data tables](https://www.nngroup.com/articles/data-tables/) |
| Sort: `<button>` in `<th>`, `aria-sort`, direction in icon + text, state in the URL | [S] | [APG sortable table](https://www.w3.org/WAI/ARIA/apg/patterns/table/examples/sortable-table/) |
| Row detail by task: inline edit (one value), side panel (keeps list context), modal (focused edit), expandable row (secondary detail) | [C] | NN/g data tables |
| Bulk: row checkboxes, "select all on page", then an explicit "Select all 1,240 matching"; persistent count and action bar; destructive bulk confirms with the count | [C] | Design-system convention |
| Paginate tables, "Load more" for lists, infinite scroll only for aimless feeds (then reachable footer, `role="feed"`, position kept on Back) | [E] | [Baymard](https://baymard.com/blog/number-of-items-loaded-by-default), [NN/g](https://www.nngroup.com/articles/infinite-scrolling-tips/) |
| Filters: several values per facet, an applied-filters bar with one-click removal and "Clear all", visible count, each change a history step | [E] | 20–28 % lack the applied bar, which cuts errors ([Baymard](https://baymard.com/blog/how-to-design-applied-filters)) |
| Narrow screens: a labelled, focusable scroll region around the table; never `display:block` on table parts | [S] | Strips semantics ([Roselli](https://adrianroselli.com/2020/11/under-engineered-responsive-tables.html)); allowed under [1.4.10](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) |
| Dashboards: one screen; every number gets context (target, prior period); position and length before colour; colour flags exceptions; stat tiles and tables for single values, charts when the shape is the point | [C][E] | Few, *Information Dashboard Design*; Cleveland & McGill perception ranking. For chart craft load the `dataviz` skill |
| Compact density as an opt-in token swap, never below 24 px targets | [C][S] | WCAG [2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html); [Material density](https://m2.material.io/design/layout/applying-density.html) |

## Search

- Visible text field, not an icon; usage rose 91 % when a link became a box ([NN/g](https://www.nngroup.com/articles/search-visible-and-simple/)). [E]
- Autocomplete: ≤ 10 suggestions desktop, 4–8 mobile; bold the completion, not the typed part; keyboard support; the active suggestion fills the field. Only 19 % of sites get all of it right ([Baymard](https://baymard.com/blog/autocomplete-design)). Build it as the APG combobox ([APG](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/)). [E][S]
- Keep the query in the box on the results page (33 % clear it, [Baymard](https://baymard.com/blog/persist-search-queries)). [E]
- Zero results is never a dead end: echo the query, suggest fixes, offer to relax filters ("0 with 'In stock'; show 12 without it") ([Baymard](https://baymard.com/blog/no-results-page)). [E]
- Default scope "All"; show an active scope and a one-click widen. Tolerate misspellings. [E]

## Onboarding

- Skip upfront tours: tutorials don't improve task performance and people want to start ([NN/g](https://www.nngroup.com/articles/onboarding-tutorials/)). Use help the user pulls, at the moment of need. [E]
- The empty state is the onboarding: what the area is for, one primary action, optional sample data labelled as sample and removable in one click. [C]
- Progressive disclosure, at most two levels, split by task frequency ([NN/g](https://www.nngroup.com/articles/progressive-disclosure/)). [C]
- Explain only what is new to this product, never conventions. Measure activation by the first meaningful task done, not tour completion. [C]

## Settings and permissions

- A switch applies immediately; a form with Save uses checkboxes. The switch label names the on state ([NN/g](https://www.nngroup.com/articles/toggle-switch-guidelines/); `<input type="checkbox" role="switch">`). [C]
- Don't mix autosave and explicit save on one page. With Save, guard navigation and show the saved state inline. [C]
- Changing a setting never changes context (no submit or navigation on `change`, WCAG [3.2.2](https://www.w3.org/WAI/WCAG22/Understanding/on-input.html)). [S]
- Ask for permissions in context, at the moment of obvious benefit, never on load; a soft pre-prompt first; always a settings path back ([web.dev](https://web.dev/articles/push-notifications-permissions-ux)). [C]
- Destructive settings live in a separated danger zone with specific labels, stated consequences, typed confirmation when irreversible, and a grace period where the domain allows it. [C]
- Roles: show what a role can do before assigning it; show *why* something is unavailable; never let a permission change mid-flow lose the user's input. [C]
