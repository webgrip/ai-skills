# Flows and states: design the sequence, then every cell

Screens are frames of a flow. Most product-UI bugs live between the frames: the back button mid-wizard, the session that expires during a long form, the list that has one item, the permission revoked while a page is open. Design those before the happy path looks finished.

Contents: flow map · screen state inventory · the state matrix · statecharts · worst-case data · edge-case checklist

## Flow map

For each top task (from [framing.md](framing.md)), write the flow as states and transitions, not as a sequence of mock-ups.

```text
Entry points:   nav · deep link (cold, logged out) · notification · search result · back from detail
Steps:          list → select → edit → review → confirm → result
Branches:       validation error · server error · conflict (someone else edited) · no permission
Exits:          cancel (what is kept?) · back (state preserved?) · close tab mid-step (resume?)
Interruptions:  session expiry · offline · another tab changed the data · role changed
Result:         where the user lands, what they see, what they can do next (no dead ends)
```

Rules that fall out of it:

- **Every entry point works cold.** A deep link into step 3 either restores context or explains and routes back.
- **Every exit says what survives.** Cancel discards on purpose; Back and an accidental close keep the draft wherever data could be lost.
- **Every step has a way back** that doesn't lose input, including the browser Back button.
- **Every result offers the next step**: view the thing, do another, undo.
- **Session expiry never eats work.** Warn before the limit, allow extending, keep the draft, and return to the same place after re-authentication (WCAG [2.2.1](https://www.w3.org/WAI/WCAG22/Understanding/timing-adjustable.html)).

## Screen state inventory

Every view has more states than the ideal one. The "UI stack" names the core five ([Hurff](https://www.scotthurff.com/posts/why-your-user-interface-is-awkward-youre-ignoring-the-ui-stack/)); product UI needs the rest.

| State | Question it answers | Design rule |
| --- | --- | --- |
| Ideal | Typical data, everything works | The one everyone designs |
| First use (empty) | "What is this and how do I start?" | Value + one primary action; optional labelled sample data |
| No results | "Why is it empty now?" | Echo query and filters, offer a way out |
| Cleared | "I finished everything" | Quiet completion, no nag |
| One item | Pluralisation, layout with a single row | `Intl.PluralRules`; no grid built for many |
| Partial | Some data loaded or some fields missing | Show what exists; mark what is missing |
| Huge | 1,000+ rows, long values | Pagination, virtualisation, truncation rules |
| Loading | First load versus refresh versus background revalidation | Reserve layout; skeleton only for slow first loads; keep stale data visible on refresh |
| Slow | 2–10 s and beyond | Progress, cancel, keep working |
| Error | Whole view versus one region versus one action | Smallest blast radius; say what failed and what still works |
| Offline / stale | Network gone, data old | Show age; queue or block writes explicitly |
| No permission | Role can't see or do it | Say why and who can grant it; no broken controls |
| Read-only | Visible but not editable (archived, locked, someone else's) | Distinct from disabled; explain the lock |
| Conflict | Someone changed it meanwhile | Show both versions; never silently overwrite |
| Success | The action worked | Inline confirmation, next step, undo where possible |

## The state matrix

For each screen in scope, build the matrix and treat every cell as designed or explicitly out of scope:

```text
screen × data state (empty · one · typical · huge · partial · error · stale)
       × role (each role that reaches it, including none)
       × device (narrow touch · wide pointer · 200 % text)
       × preference (light · dark · reduced motion · forced colours)
```

The matrix is too big to render exhaustively, so pick by risk: every data state at the narrowest and widest size, every role once, preferences on the densest screen. Record which cells were rendered and which were reasoned about only; that list goes into the validation report.

## Statecharts

When a component or flow has more than a few interacting booleans (`isLoading`, `isError`, `isEditing`, `hasDraft`), model it as one explicit state machine so impossible combinations can't be represented: Harel statecharts ([Harel 1987](https://doi.org/10.1016/0167-6423%2887%2990035-9)), implemented with a discriminated union, a reducer or a library such as XState ([XState](https://stately.ai/docs/xstate)). One authoritative state drives visual, content, URL and ARIA together.

```text
idle → submitting → (success | invalid | failed)
invalid → editing → submitting
failed → (retrying | editing)
success → idle   (with undo window)
```

## Worst-case data

Lorem ipsum and "John Doe" prove nothing. Build a fixture from the real schema and break the layout on purpose (after Kowalski's break-ui, [emilkowalski/skills](https://github.com/emilkowalski/skills)):

1. **Map every rendered value**: source, type, the limit the schema, database or API allows, and whether it can be missing.
2. **Build plausible fixtures at those limits**: a 60-character email, "Aleksandra Wiśniewska-Kowalczyk", a Dutch compound such as "Arbeidsongeschiktheidsverzekering", an RTL name, 1,284 members, €1.234.567,89, a null avatar, a 2,000-character note.
3. **Add Empty, One and 1,000+ variants.**
4. **Inject at the data boundary** (mock API, seed, story args), never by editing markup, behind a dev-only switch kept in the URL.
5. **Check** at the real container width, 320 px, the widest layout, 200 % zoom, dark mode and RTL.
6. **Keep the fixture** as a regression story or test.

| Failure signature | Usual fix |
| --- | --- |
| Avatar or icon squashed | `flex-shrink: 0` |
| Row overflows sideways | `min-width: 0` on flex and grid children; `minmax(0, 1fr)` |
| Unbreakable email or URL | `overflow-wrap: anywhere` |
| "1 members" | `Intl.PluralRules` / ICU messages |
| Wrong initials for composed names | `Intl.Segmenter` |
| Numbers jitter while updating | `tabular-nums` |
| Truncated with no way to read it | Detail view, expand control, or focusable tooltip |
| Badge or button clips at 200 % | Remove fixed heights |

Text expansion is largest for short strings: strings up to 10 characters can grow 200–300 % in translation, long ones about 30 % ([W3C i18n](https://www.w3.org/International/articles/article-text-size)). Pseudo-localise with +40 % and long compounds.

## Edge-case checklist

Run through it per flow and mark each item handled, not applicable, or open:

- zero, one, many, too many
- long, short, missing, malformed, Unicode, RTL, emoji
- slow network, offline, timeout, partial failure, retry, double submit
- concurrent edit, stale tab, deleted while viewing
- permission missing, revoked mid-flow, role downgrade
- session expired mid-task, re-authentication returns to the same place
- deep link cold, refresh mid-flow, Back from every step, open in new tab
- first-time user and the 200-times-a-day user
- keyboard only, screen reader, 200 % text, touch without hover
- locale: dates, numbers, currency, plurals, sorting (`Intl.Collator`), time zones
