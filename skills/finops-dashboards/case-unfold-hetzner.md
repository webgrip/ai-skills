# Case: Unfold's Hetzner Cloud bill on a homelab Grafana

One worked pass through the procedure on a real dashboard: webgrip's homelab watches what the small Hetzner Cloud project behind the Unfold production cluster costs. Use it for the reasoning, not as a layout to copy. Figures are from October 2026.

## The reader and the decision

The owner pays the bill and set a budget of € 50 net per month. The questions: will this month stay under € 50, what does a normal month cost, did something get left running? An engineer's question comes second: which resource costs what.

## Modelling the bill

Hetzner has no cost API ([sources.md](sources.md#hetzner-cloud)). A small standard-library exporter reads the inventory and `GET /pricing` every five minutes and recomputes the bill the way Hetzner does: started hours × hourly price, capped at the monthly price per resource per UTC calendar month; per-GB items over 730 hours. It publishes per resource: hourly price, monthly cap, billable hours, month to date, projected month, creation time; plus pipeline health (token configured, API authorized, last success). Unit tests pin the billing rule; a mutation script breaks it and checks the tests fail.

Inventory: three control-plane servers and a VPN coordinator at € 5,49 per month cap, one worker at € 8,49, five primary IPv4 at € 0,50, one 0.43 GB snapshot. A full month is **€ 32,96**, which matches the figure computed by hand from Hetzner's own Usage page.

Gaps written into the dashboard's text panel and the runbook: resources deleted earlier in the month are invoiced but invisible to the API; traffic overage is not counted. The invoice is net (EU reverse charge), so every figure is net EUR.

## Three numbers that answer three questions

On 25 October the cluster was one day old. The live series read:

| Panel | Value | Answers |
| --- | --- | --- |
| Month to date | € 0,28 | What has been spent this month |
| Projected end of month | € 8,36 | What this month's invoice will say |
| Full-month run-rate | € 32,96 | What every following month will cost |

A single "forecast" would have hidden this: the linear run-rate (month to date ÷ elapsed fraction) is meaningless on a cluster created mid-month, and the full-month figure overstates October by a factor of four. Even for an inventory that existed all month, linear extrapolation overshoots capped billing: with the example inventory in `examples/hetzner-inventory.json`, month to date on the 25th at 12:30 UTC is € 31,10, linear extrapolation says € 39,31, and the bill will be € 32,96, because each resource stops costing once it reaches its cap. Reproduce it:

```bash
python3 scripts/forecast.py --at 2026-10-25T12:30:00Z --budget 50 capped --inventory examples/hetzner-inventory.json
python3 scripts/forecast.py --at 2026-10-25T12:30:00Z linear --mtd 31.10
```

## What the dashboard got right

- Answer first: the first row holds the three numbers above, then counts of billed things, then the trust tiles (token, refresh age, scrape).
- Stats and tables for single values and comparisons; no time series at all, because every question is a current value.
- `currencyEUR` with 2 decimals on totals, 4 decimals on hourly prices only.
- `max by (kind, id)` inside every `sum`, so a duplicate scrape cannot double the bill.
- "No value" renders as `no data`, never € 0,00.
- Projected end of month carries the budget as thresholds (orange at € 40, red at € 50).
- A leftover-server tile (servers without the cluster label) with an alert after two hours, for the temporary servers an image upload leaves behind.
- The billing model and its gaps are on the dashboard, in three sentences.

## What the linter found

`python3 scripts/dashboard_lint.py` on the dashboard: 7 findings, none of them a false positive.

| Finding | Panel | Improvement |
| --- | --- | --- |
| `budget-without-reference` (fail) | Full-month run-rate | Add the € 50 budget as thresholds: the run-rate is next month's bill and is the number the budget is really about |
| `headline-without-comparison` (note) | Month to date | Add a comparison: same day last month (once a previous month exists) or the share of budget used |
| `boolean-as-number` (note) | API token, Exporter scrape | Map 0/1 to "Rejected"/"OK" and "Down"/"Up" |
| `legacy-table-footer` (note) | Cost per role, Cost per resource | Move `options.footer` to an override with `custom.footer.reducers: ["sum"]` on the EUR columns; Grafana 13 rewrites the old form on every load |
| `billing-timezone-browser` (note) | dashboard | Set `timezone: utc`, the zone Hetzner closes months in; with `browser`, a viewer in Amsterdam sees a month that starts at 02:00 UTC |

Reading the rest of the setup with the same eyes found two things no file lint sees:

- The budget alert sums `hcloud_cost_resource_projected_month_eur` by project **without** the `max by (kind, id)` the dashboard uses, so a duplicate scrape would double the alert's number but not the panel's. Use the same expression, ideally one recording rule both read.
- The budget lives in three places (alert rule, panel thresholds, panel description). One recording rule or constant would keep them equal.

## False-positive pass

The same linter on all 85 dashboards in that Grafana (1,681 panels) first produced false positives that became exemptions and careful-fixture tests: `topk` legends (labels are kept), token-price multipliers such as `* 1.25` read as VAT, SQL that formats money into text, threshold lines on time series, budget tiles that display the budget itself, and a tokenizer bug that cut `sum(` into `su`. What remained were real defects: five legends naming a label the `sum by` had dropped (blank legends in Kyverno panels), and requests/allocatable totals summed over both kube-state-metrics and OpenCost series. The duplication was confirmed live: eight `kube_*` metric names came from both `job="kube-state-metrics"` and `job="opencost"`.

## What verification established

The live series were read from VictoriaMetrics on the day; the full-month figure matched the Usage-page computation. Not yet done: reconciliation against a real invoice (the first full month closes on 31 October and Hetzner may invoice up to 28 days later), a CVD check of the threshold colours, and a viewer test of the dashboard at laptop width.
