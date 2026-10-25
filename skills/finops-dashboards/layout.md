# Layout: answer first, compare everything, colour sparingly

A dashboard is "the most important information needed to achieve one or more objectives, consolidated and arranged on a single screen so the information can be monitored at a glance" (Few). Strength tags: [evidence.md](evidence.md).

Contents: [Row order](#row-order) · [Panel choice](#panel-choice) · [Numbers](#numbers) · [Comparisons](#comparisons) · [Colour](#colour) · [Words](#words) · [Accessibility](#accessibility)

## Row order

| Row | Holds | Panels |
| --- | --- | --- |
| 1. Answer | Where we are and where we will land | Month to date with delta vs same day last month · Projected month against budget (thresholds) · Full-month run-rate · Budget left |
| 2. What moved | The cause of the delta | Top movers table (change in €, sorted) · Month-over-month bridge (waterfall) by owner or service |
| 3. Where it goes | Allocation | Cost per owner, service or role table with month to date, projected, share; unallocated as a named row |
| 4. Per unit | Efficiency | Cost per tenant, run, build, customer; with the volume beside it |
| 5. Detail | Per resource | Sortable, filterable table: resource, owner, hourly or unit price, month to date, projected |
| 6. Trust | Whether to believe rows 1–5 | Data freshness · exporter up · token accepted · allocated share · reconciliation gap · known gaps text |

Put the trust row last but never drop it: a cost pipeline that silently stops reports € 0,00 or a frozen number, and both look like good news. Use variables (`team`, `tenant`, `project`) instead of one dashboard per owner. Keep the screen to rows 1–3 at 1080p; rows 4–6 below the fold or in a linked detail dashboard.

## Panel choice

| Content | Panel | Not |
| --- | --- | --- |
| One number (month to date, projected, run-rate) | Stat, `graphMode: area` if the trend matters, `showPercentChange` | Time series of a single value |
| A number against a target | Stat with budget thresholds, or bar gauge with `max` = budget | Radial gauge |
| Comparing owners, services, resources | Table sorted by the decision column, or horizontal bar chart | Pie or donut |
| Exact values to look up | Table with currency columns and a footer sum on money columns only | Chart with tooltips |
| Change between two periods, decomposed | Waterfall/bridge: previous total → per-owner deltas → current total | Two pies side by side |
| Daily spend over time | Time series or bars by day, stacked only when the stack total is meaningful | Stacked areas of rates per pod |
| Budget burn-down | Time series: remaining budget against the ideal line | Gauge |
| Distribution of unit cost | Histogram or table of percentiles | Average alone |

Why: position on a common scale is read more accurately than length, angle or area; the crowdsourced replication found area (bubbles) worse than angle (pies) and both clearly worse than position (Strong). Tables beat graphs for looking up specific values, graphs beat tables for seeing patterns (cognitive fit, Consistent). The bullet graph was designed to replace gauges: a featured measure, one or two comparison markers and 2–5 qualitative ranges in shades of one hue (Strong as specification; its efficiency claim is the author's, not tested). Grafana has no bullet graph; a bar gauge with `max` and thresholds is the nearest.

## Numbers

- **House rule: EUR, 2 decimals, Dutch notation `€ 1.234,56`.** Tables always keep the cents. Unit prices may show 4 decimals.
- Few's counterpoint: a headline of € 3.848.305,93 reads faster as € 3,8 M (Contested against the 2-decimal rule). Resolve it per tile: under € 10.000 keep cents; above, a rounded headline is acceptable only when the exact figure sits in the table beside it.
- Right-align money in tables (Grafana does this for numbers), same decimals in a column, unit in the column header ("Month to date EUR") so exports keep it.
- Never let "no data" render as 0.

## Comparisons

Every headline number carries one comparison (Few's pitfall: data without context):

- **Delta** against the same point in the previous period (day 25 vs day 25), as € and %. A rise in cost is bad: `percentChangeColorMode: inverted`.
- **Target**: budget as thresholds; show the variance as a percentage, which Few recommends showing directly instead of making the reader compute it.
- **Forecast**: projected month next to month to date, with the method in the description.
- Variance colours follow IBCS: red and green for variances only, red bad and green good relative to the target; actual solid, plan outlined, forecast hatched (Consistent, IBCS summary). Grafana cannot hatch: mark forecast series with a dashed line and the word "forecast" in the legend.

## Colour

- Neutral by default (one fixed colour per tile). Colour encodes state only where a threshold means something.
- Threshold palette for money: blue (fine) → orange (watch) → red (over). Avoid red against green as the only cue; when you use them, the value or a word must also say it.
- One hue in several intensities for qualitative ranges (the bullet-graph rule), not a rainbow.
- Same owner, same colour across every panel: use field overrides by name, not the palette order.

## Words

- Title says what and when: "Projected end of month", "Cost per CI build, this month". Not "Cost".
- Description: basis (net, billed/amortized), period and timezone, source, known gaps. One or two sentences.
- A text panel at the top for the billing model and gaps only when the dashboard is the reader's first contact with the source; keep it to three lines.
- Column names carry the unit: "Projected month EUR", "Billable hours".

## Accessibility

- Colour is never the only means of conveying information, and graphical objects need 3:1 contrast against their background (WCAG 2.2 SC 1.4.1 and 1.4.11, Strong).
- About 1 in 12 men has a colour vision deficiency, mostly red-green (Strong). Test with a CVD simulator or the grayscale screenshot test.
- Value mappings turn 0/1 into words; tooltips are not accessible to keyboard users, so the table carries the exact numbers.
- Check light and dark theme: Grafana's named colours shift between them; fixed hex colours do not.
