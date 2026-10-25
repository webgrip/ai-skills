# Grafana: provisioning, units, queries and recipes for cost panels

Targets Grafana 12.2 and later with grafana-operator v5 and a Prometheus-compatible store (VictoriaMetrics, Prometheus); SQL panels for ledger data. Strength tags: [evidence.md](evidence.md).

Contents: [Provisioning](#provisioning) · [Units and locale](#units-and-locale) · [Stat panels](#stat-panels) · [Tables](#tables) · [Calendar periods](#calendar-periods) · [Recording rules](#recording-rules) · [Query recipes](#query-recipes) · [SQL ledgers](#sql-ledgers) · [Double counting](#double-counting)

## Provisioning

- `GrafanaDashboard` (`grafana.integreatly.org/v1beta1`): dashboard JSON in `spec.json` (block scalar), `instanceSelector` (required, immutable), one of `folderRef`/`folderUID`, optional `datasources[] {inputName, datasourceName}` to resolve `${DS_...}` import inputs, `resyncPeriod` (default 10m). (Strong) Other sources (`url`, `configMapRef`, `grafanaCom`, `gzipJson`) exist; the linter reads `spec.json` and raw `.json`.
- Set a stable `uid` (at most 40 characters, immutable on the CRD) so links like `/d/<uid>` survive.
- Pin every panel's datasource by `uid`. Tools that substitute variables in manifests (Flux `postBuild`) also eat `$`; escape Grafana variables the way the repository does.
- A dashboard edited in the UI and provisioned from git drifts: make git the source and set `editable: false` on finance dashboards that others rely on.

## Units and locale

| Want | Unit id | Renders |
| --- | --- | --- |
| Euro, abbreviated | `currencyEUR` | `€1.23K` above 1000; always a `.` decimal |
| Euro, full digits, viewer's locale | `currency:financial:€` (`:suffix` puts it after) | Full number via the browser's `Intl.NumberFormat` |
| Dollar | `currencyUSD`, `currency:financial:$` | as above |
| Share 0–1 | `percentunit` | 0.42 → 42 % |
| Share 0–100 | `percent` | 42 → 42 % |
| Hours | `h` | |

- Every standard unit, `currencyEUR` included, formats decimals with a `.`. Only `locale` and `currency:financial:` use the browser's locale, so Dutch `€ 1.234,56` appears only for viewers whose browser locale is Dutch; there is no organisation-wide number-locale setting (an open feature request). (Strong for the code path; the nl-NL rendering itself is inferred, not observed. Check in a browser before promising it.)
- Set `decimals` explicitly. Empty decimals are truncated by value (100.456 → 100). (Strong, docs)
- Put the currency in field names ("Month to date EUR") as well, so CSV exports and screenshots keep it.

## Stat panels

- `graphMode`: `none` | `line` | `area` (sparkline). `colorMode`: `value` | `background` | `background_solid` | `none`. `textMode`: `auto` | `value` | `value_and_name` | `name` | `none`. (Strong)
- `showPercentChange: true` shows the change over the queried range; `percentChangeColorMode: inverted` makes a rise red, which is right for cost. (Strong) It needs a range query, so the stat must not be instant-only.
- `noValue`: leave `-` or set a word. Never `0`.
- Thresholds: `mode: absolute`, base step `null`; for a budget of 500 use steps at 400 (orange) and 500 (red). Same numbers as the alert.
- Value mappings for 0/1 status tiles: `{"type": "value", "options": {"0": {"text": "Rejected"}, "1": {"text": "OK"}}}`.

## Tables

- **Footer (12.2+)**: `fieldConfig.defaults.custom.footer.reducers: ["sum"]` applies to all fields; to sum money columns only, put `custom.footer.reducers` in an override that matches them (`byNames`, `byRegexp`). The old `options.footer {show, reducer, fields}` is converted in the browser on every load and stays old in git. (Strong)
- Multi-query tables: instant queries with `format: table`, then `merge` (same label set across queries), then `organize` to rename `Value #A` and hide `Time`. `joinByField` when label sets differ. `calculateField` (binary operation) for derived columns such as "Change EUR" = current − previous. (Strong)
- Sort by the decision column (`options.sortBy`), usually projected or change in euros.
- Cell types worth using: colored text on the change column, gauge cell for share of budget, data links to the per-resource detail.

## Calendar periods

PromQL has no month: duration units stop at `y` (365 days), and `M` is not a unit. `day_of_month()` and `days_in_month()` exist and use UTC. (Strong) MetricsQL adds `timezone_offset("Europe/Amsterdam")` for local months. (Strong)

| Need | How |
| --- | --- |
| Month to date from a counter | dashboard or panel range `now/M` → `now`, then `increase(cost_eur_total[$__range])`; or an exporter that publishes month to date itself |
| Elapsed fraction of the month (UTC) | `(day_of_month() - 1 + (time() % 86400) / 86400) / days_in_month()` |
| Linear projection | `month_to_date / elapsed_fraction`; correct for usage-driven spend only ([framework.md](framework.md#forecasts)) |
| Same point last month | `offset 30d` is an approximation (31-day months shift by a day); for exact comparisons record month to date daily and compare day N with day N |
| Previous full month | range `now-1M/M` → `now-1M/M` in Grafana (Strong), or a recording rule evaluated at month end |

Set the dashboard `timezone` to the billing timezone; `now/M` snaps to midnight in that zone.

## Recording rules

Record cost series once, then every panel and alert reads the same numbers:

```yaml
groups:
  - name: cost
    interval: 5m
    rules:
      - record: team:cost_eur_per_hour:sum
        expr: sum by (team) (max by (team, resource_id) (resource_hourly_cost_eur))
      - record: team:cost_month_to_date_eur:sum
        expr: sum by (team) (max by (team, resource_id) (resource_month_to_date_eur))
      - record: cost_projected_month_eur:sum
        expr: sum(max by (resource_id) (resource_projected_month_eur))
```

- `max by (<identity>)` inside the `sum` collapses duplicate scrapes (two exporter replicas, a job scraped twice) before adding.
- Hourly-cost gauges → euros over a window: `avg_over_time(x[30d]) * 24 * 30`, not `sum_over_time` (which multiplies by the sample count). (Consistent)
- MetricsQL `increase` uses the last sample before the window; `increase_prometheus` keeps Prometheus behaviour. Results can differ near counter starts. (Strong)
- Test each rule with the engine's unit tests (`vmalert -rule=... -test`, `promtool test rules`) on a breaching and a normal fixture.

## Query recipes

```promql
sum(max by (resource_id) (resource_month_to_date_eur))

topk(10, sum by (team) (resource_month_to_date_eur) - sum by (team) (resource_month_to_date_eur offset 30d))

sum(increase(litellm_spend_metric_total[$__range])) / sum(increase(ci_builds_total[$__range]))

sum(resource_month_to_date_eur{team=""}) / sum(resource_month_to_date_eur)

sum(max by (node) (node_total_hourly_cost)) * 730

sum(avg_over_time(node_power_watts[30d])) * 24 * 30 / 1000 * $kwh_price
```

Line by line: total month to date, de-duplicated; top movers against roughly the same day last month; cost per build over the picked range; unallocated share; OpenCost node cost per month; electricity per month from measured watts and a `kwh_price` constant variable.

## SQL ledgers

Postgres (or other SQL) datasources suit ledger-shaped data: LiteLLM spend tables, invoices, SaaS subscriptions.

```sql
SELECT date::date AS "time", sum(spend) AS spend_usd
FROM "LiteLLM_DailyTeamSpend"
WHERE date::date >= date_trunc('month', now() AT TIME ZONE 'UTC')
GROUP BY 1 ORDER BY 1
```

- Alias money columns with the currency (`spend_usd`, `amount_eur`) so the unit and the linter both see them.
- Group in SQL, not with Grafana transformations, for anything over a few thousand rows.
- Read-only database user per datasource; panels never write.
- Format numbers in Grafana, not with `to_char` in SQL, unless the cell is deliberately text.

## Double counting

| Cause | Symptom | Fix |
| --- | --- | --- |
| Two exporters publish one metric name (OpenCost re-exporting kube-state-metrics) | Allocatable, requests and PVC totals exactly 2× | `job` matcher or disable the re-export ([checks.md](checks.md#double-counted-series)) |
| Two replicas of a cost exporter scraped | Totals 2× during rollouts | `max by (<identity>)` inside `sum`, or one replica |
| Idle shared and also shown as its own row | Total > bill | Show idle either shared or separate, never both |
| Footer sums a total row that is already in the data | Footer 2× | Drop the total row from the query |
| Overlapping owner labels (team and project on the same resource, both summed) | Owners add up to more than the bill | Allocate along one dimension per table |
| Billed and effective cost in one panel | Purchases counted twice | One basis per panel ([framework.md](framework.md#cost-bases)) |

Before trusting a total, check `count by (job) (<metric>)` and compare the sum with the provider's figure.
