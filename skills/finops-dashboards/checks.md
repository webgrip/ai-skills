# Linter rules: what each finding means and what to do

`scripts/dashboard_lint.py` reads Grafana dashboard JSON, or GrafanaDashboard CRDs that carry it in `spec.json` (block scalar). It contacts nothing. Severity: **fail** makes a number wrong, **warn** makes it misleading or fragile, **note** costs the reader time. Evidence for each rule: [evidence.md](evidence.md).

Contents: [Rule table](#rule-table) · [Money correctness](#money-correctness) · [Comparison and forecast](#comparison-and-forecast) · [Queries](#queries) · [Display](#display) · [Running it](#running-it) · [What it cannot see](#what-it-cannot-see)

## Rule table

| # | Rule | Severity | Fires when |
| --- | --- | --- | --- |
| 1 | `currency-unit-missing` | fail | a money panel has no currency unit on its money fields |
| 2 | `currency-mismatch` | fail | the unit's currency differs from the metric's `_eur`/`_usd` suffix and the query converts nothing |
| 3 | `cents-as-euros` | fail | a `cents` series sits under a currency unit without `/ 100` |
| 4 | `currency-decimals` | warn | currency with automatic decimals, or not the house decimals (default 2); unit prices need at least 2 |
| 5 | `percent-scale` | fail | a ratio under `percent`, or `* 100` under `percentunit` |
| 6 | `no-value-as-zero` | fail | `noValue` on a money panel renders as 0 |
| 7 | `single-value-as-timeseries` | warn | a period total or an instant query drawn as a time series |
| 8 | `budget-without-reference` | fail | a budget, forecast, projected or run-rate tile with no threshold, max or second query |
| 9 | `headline-without-comparison` | note | a money stat with no delta, threshold or sparkline |
| 10 | `missing-description` | warn | a money panel without a description |
| 11 | `rate-without-aggregation` | warn | `rate()`/`increase()` on a money panel returns raw series |
| 12 | `legend-label-dropped` | fail | the legend names a label the outer aggregation removed |
| 13 | `double-counted-series` | fail | `sum`/`count` over a metric both kube-state-metrics and OpenCost publish, without a `job` filter |
| 14 | `hardcoded-vat` | warn | a VAT factor (1.21, 1.19, or another rate beside a VAT word) is a literal in a query |
| 15 | `datasource-missing` | warn | a query has no datasource uid, or an import input with no matching variable |
| 16 | `period-follows-picker` | warn | a month-to-date tile computed over `$__range` while the range is not `now/M` |
| 17 | `billing-timezone-browser` | note | a money dashboard with timezone `browser` or unset |
| 18 | `missing-forecast` | warn | spend-to-date panels and no forecast, run-rate or budget panel anywhere |
| 19 | `legacy-table-footer` | note | a table uses the pre-12.2 `options.footer` |
| 20 | `non-additive-footer-sum` | fail | a footer sums a percentage, ratio, average or per-unit column |
| 21 | `boolean-as-number` | note | a 0/1 status stat without value mappings |
| 22 | `red-green-only` | note | red against green is the only signal (no text, or a coloured area) |
| 23 | `gauge-for-money` | note | a radial gauge for money |
| 24 | `pie-for-money` | note | a pie chart for money |

## Money correctness

### currency-unit-missing

A money panel is one with a currency unit anywhere, a non-count query over a metric whose name ends in a money word (`_eur`, `_usd`, `_cost`, `_spend`, `_price`, `_cents`, optionally `_total`), or SQL that selects a money column as a number. Without a unit the reader cannot tell euros from dollars or cents. Fix: `currencyEUR` with `decimals: 2`, or `currency:financial:€` for full digits in the viewer's browser locale ([grafana.md](grafana.md#units-and-locale)). Count panels over cost metrics (`count(...)`) and SQL that formats money into text are exempt.

### currency-mismatch

`llm_spend_usd` under `currencyEUR` shows a dollar figure with a euro sign. Convert in the query with a named rate series or variable, then the rule is satisfied by the `*`; or show the source currency.

### cents-as-euros

Ledgers often store integer cents (Stripe amounts, invoice lines). Divide by 100 in the query or SQL.

### currency-decimals

Grafana truncates automatic decimals by value: the docs' own example shows 100.456 as 100. Money uses the house decimals everywhere (`--decimals`, default 2). A unit price (title or column says per hour, per run, per token, cost per, hourly) may show more, never fewer than 2. A headline in the thousands may round in the tile if the table beside it keeps the cents ([layout.md](layout.md#numbers)).

### percent-scale

`percent` expects 0–100, `percentunit` expects 0–1. Budget used = spend / budget is a 0–1 ratio: use `percentunit`, or multiply by 100 and keep `percent`.

### no-value-as-zero

"No data" and "€ 0,00 spent" are different facts. A broken exporter showing € 0,00 reads as good news. Keep the default `-` or a word such as `no data`.

## Comparison and forecast

### single-value-as-timeseries

Month to date, projected month and run-rate are one number each. Draw them as a stat (with a sparkline when the trend matters) and keep time series for "how did daily spend move". Instant queries in a time series render a single dot.

### budget-without-reference

A forecast is only actionable against the budget. Add the budget as thresholds (absolute steps at, say, 80 % and 100 % of budget), as `max` on a bar gauge, or as a second query. Panels that display the budget itself (the metric name contains `budget`) are exempt.

### headline-without-comparison

A bare number does not say good or bad. Add one of: `showPercentChange` with `percentChangeColorMode: inverted` (a rise in cost shows red), a second query for the same day last month, budget thresholds, or `graphMode: area`.

### missing-description

Every money figure has a definition the reader cannot see: net or gross, billed or amortized, which period and timezone, what is excluded. Put it in the panel description, one or two sentences.

### missing-forecast

A dashboard that reports spend to date and never says where the month will land answers yesterday's question. Add projected end of period against budget ([framework.md](framework.md#forecasts), `scripts/forecast.py`).

## Queries

### rate-without-aggregation

Raw `rate()` series churn with every pod restart; a table footer or a stacked chart then adds the fragments. Aggregate to the dimension the reader allocates by: `sum by (namespace) (rate(...))`.

### legend-label-dropped

`sum by (rule_result) (...)` with legend `{{result}}` renders an empty legend. Name a label the aggregation keeps. `topk`, `bottomk`, `limitk` and `without` keep labels and are not checked.

### double-counted-series

OpenCost re-exports kube-state-metrics series under the same names unless `EMIT_KSM_V1_METRICS` is false. Seen live in one cluster: `kube_node_status_allocatable`, `kube_node_status_capacity`, `kube_node_labels`, `kube_pod_owner`, `kube_pod_container_status_running`, `kube_pod_container_resource_requests`, `kube_persistentvolume_capacity_bytes` and `kube_persistentvolumeclaim_info` came from both `job="kube-state-metrics"` and `job="opencost"`. Check yours with `count by (__name__, job) ({__name__=~"kube_.*"})`. Fix: a `job` matcher, or `max by (node, resource)` inside the `sum`. A ratio of two such sums (requests / allocatable) cancels and is exempt; the absolute numbers do not.

### hardcoded-vat

Store and chart money net. Gross is net × (1 + rate) where the rate depends on the buyer and the service ([sources.md](sources.md#vat-and-currency)); a literal 1.21 is wrong for a reverse-charged invoice and silently stale when a rate changes. Apply VAT once, from a dashboard constant variable or a labelled series, and say "incl. VAT" in the title. Token prices such as `* 1.25` are not flagged unless a VAT word is near.

### datasource-missing

A panel without a datasource uid falls back to the default datasource and breaks when it changes. `${DS_X}` left from an import, with no variable `DS_X`, never resolves.

### period-follows-picker

`increase(cost_eur_total[$__range])` titled "Month to date" shows the last 7 days when someone picks 7 days. Pin the panel (`timeFrom: now/M`), set the dashboard range to `now/M`, or compute the period in the query ([grafana.md](grafana.md#calendar-periods)).

### billing-timezone-browser

Providers close months in their own timezone (Hetzner: UTC). With `browser`, a viewer in Amsterdam sees October start at 02:00 UTC. Set `timezone` to the billing timezone.

## Display

### legacy-table-footer

Grafana 12.2 replaced `options.footer {show, reducer, fields}` with per-field `fieldConfig.defaults.custom.footer.reducers` (or an override with `custom.footer.reducers`) and converts the old form in the browser on every load. Dashboards provisioned from git stay in the old form. Rewrite it so what is in git is what renders.

### non-additive-footer-sum

A sum of shares, ratios, averages or unit prices is meaningless (a column of shares sums to 100 %; a sum of averages is no average). Sum money columns only; put `mean` or nothing on the others. Hourly prices are additive across resources (the result is the burn rate) and are exempt.

### boolean-as-number

A tile reading `1` needs its description to be understood. Map 0 and 1 to words (`OK`, `Rejected`, `Stale`).

### red-green-only

About 1 in 12 men cannot reliably tell red from green. When colour alone carries the state (`textMode: none`, coloured threshold areas, state timelines), add text or use a blue/orange pair. Thresholds on a tile that also prints its value are not flagged.

### gauge-for-money

Radial gauges spend space on an arc and are read less accurately than position on a common scale. Use a bar gauge (Grafana's closest to a bullet graph) or a stat with budget thresholds ([layout.md](layout.md#panel-choice)).

### pie-for-money

Angles and areas are judged worse than positions. Compare amounts in a sorted table or bar chart; keep the share as a column.

## Running it

```bash
python3 scripts/dashboard_lint.py path/to/dashboards/            # text, exit 1 on any fail
python3 scripts/dashboard_lint.py --json --fail-on warn file.yaml # CI gate on warn and above
python3 scripts/dashboard_lint.py --decimals 0 file.json          # house style without cents
python3 scripts/dashboard_lint.py --rules                         # the table above
```

Findings print as `severity rule path:line [panel] message -> checks.md#rule`. A `json` value that is not a block scalar, or `gzipJson`, is listed under skipped: lint the rendered JSON instead.

## What it cannot see

- Whether a query returns the right data. Run it, and reconcile one month against the invoice ([framework.md](framework.md#reconcile)).
- Whether the budget in a threshold matches the budget in the alert rule. Keep one source and grep for the other.
- How it renders: open the dashboard at the width people use, in light and dark.
- Panels from plugins outside the core set (dynamic text, Infinity tables) are not judged as money panels.
