# Worked example: an orders admin table people use 200 times a day

A constructed example that shows the procedure's reasoning end to end. The product, ticket counts and timings are illustrative, not a shipped case or a measured result. Use it to see how the artefacts connect, not as a layout to copy.

**Request:** "Support agents say the orders table is slow to work with. Make it better." Laravel + Inertia + React, an existing component library, no access to agents.

## 1. Evidence ledger

| Source | Finding | Status |
| --- | --- | --- |
| Ticket export, 90 days | 61 internal tickets mention "orders page"; top clusters: "lost my filters" (19), "can't find the refund button" (14), "page jumps when loading" (9) | Recorded |
| Route logs | `/orders` ~200 views per agent per day; 72 % of sessions apply a status filter | Recorded |
| Code | Filters live in `useState`; refund lives in a kebab menu on the detail page; rows render before totals load | Read |
| Requester | "Most refunds are partial" | Supplied, unverified |

## 2. Job stories and task model

- When a customer calls about a late order, I want to find it by name or order number in seconds, so I can answer while they're on the line. *(tickets: 23)*
- When a customer asks for a partial refund, I want to refund the line items from the list, so I don't lose my place in the queue. *(tickets: 14; "partial" is supplied)*

| Task | Frequency | Cost of error | Users | Stance |
| --- | --- | --- | --- | --- |
| Find order | ~120/day | Low | Expert | Fast: search focused by `/`, filters kept in the URL |
| Partial refund | ~40/day | High (money) | Expert | Fast and safe: inline, previewed, undo window, no confirmation dialog |
| Export CSV | weekly | Low | Mixed | Discoverable, guided |

## 3. Flow and states

Flow for the refund: list → row expand → line items → amount → preview → refund → row shows "Refunded €12,50 · Undo (30 s)".

The states that broke in the code: refresh resets filters (URL not state); totals load after rows and shift the table (no reserved width); an order with 40 line items overflows the expanded row; a refund failing with 409 (already refunded elsewhere) shows "Something went wrong".

The worst-case fixture added a 64-character customer name, a 40-line order, €12.345,67 totals and an empty filter result.

## 4. Findings (merged from three independent passes plus the scan)

| # | Severity | Finding | Rule | Proof | Correction |
| --- | --- | --- | --- | --- | --- |
| 1 | P1 | Filters reset on refresh and Back | URL as state ([Baymard](https://baymard.com/blog/back-button-expectations)) | `Orders.tsx:88` `useState`; reproduced in the browser | Encode filters and sort in the query string |
| 2 | P1 | Partial refund needs 4 screens | Flexibility and efficiency (heuristic 7) | KLM: 9.3 s versus 5.5 s inline | Inline refund in the expanded row |
| 3 | P1 | Row actions are clickable `<div>`s; keyboard users can't refund | WCAG 2.1.1 | `ui_scan.py`: `clickable-non-control` × 3 | `<button>` with visible label |
| 4 | P2 | Table shifts when totals arrive | CLS ([web.dev](https://web.dev/articles/cls)) | CLS 0.18 in the lab trace | Reserve the totals column width; `tabular-nums` |
| 5 | P2 | 409 shows "Something went wrong" | Heuristic 9; [content.md](content.md#errors) | `RefundController.php:54` | "This order was already refunded by Sam at 14:02. Nothing was charged twice." |

What held up: search is fast (INP 80 ms in the lab), the status colours are paired with text labels, and the danger styling on "Cancel order" is already separated from routine actions.

Discarded during falsification: a pass flagged "too many columns". The column-usage log shows all eight are used weekly, and the narrow layout already scrolls inside a labelled region, so it was dropped.

## 5. Validation status

```text
Validation status
- Evidence used: 90-day ticket export (61 tickets), route logs, code; "most refunds are partial" supplied
- Checked by agent: ui_scan (0 fail after fixes) · 3 heuristic passes (overlap 4 of 7) · cognitive walkthrough of
  refund · KLM for find and refund · keyboard-only gate on refund (pass) · worst-case fixture at 320 px and 200 % ·
  axe on /orders (0 violations of rules run)
- NOT validated with users: that agents refund from the list rather than the ticket; that a 30 s undo
  window suits phone calls
- Recommended human test: 5 agents, 3 scenarios (late order lookup, partial refund, refund conflict), SEQ per task
- Instrumented to learn: refund_started / refund_completed / refund_undone, filter_restored_from_url
```

The lesson worth transferring: the biggest wins came from the task model (frequency × cost) and the URL-state and state-inventory checks, not from visual changes. The visual system was left alone because agents had already learned it.
