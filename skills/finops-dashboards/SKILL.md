---
name: finops-dashboards
description: Designs, reviews and builds cost and FinOps dashboards that say what we spend, where it goes, where the month will land against budget and why it moved - headline with delta and forecast, top movers, unit cost per tenant, run or build, showback, budget and anomaly alerts - from billing rules reproduced in code (Hetzner hourly-capped, OpenCost allocation and idle, LiteLLM spend, FOCUS, electricity, SaaS, VAT), with a Grafana dashboard linter and a forecast script. Use when building or reviewing a cost, spend, budget, billing or FinOps dashboard or a Grafana panel in euros or dollars; when spend looks double counted or does not match the invoice; adding a forecast, run-rate, budget, anomaly or idle-resource alert; cost per unit, showback or chargeback; tracking cloud, Kubernetes, LLM token or electricity cost. Dutch - kostendashboard, wat kost dit per maand, klopt de prognose, budgetbewaking, kosten per klant. Not for KPI definitions (kpi-groomer), chart styling (dataviz) or app dashboard UX (product-ux).
---

# FinOps dashboards: the number, its comparison, its forecast, its owner

A money figure is wrong until it has been reconciled with an invoice, and useless until it has a comparison. Every claim here carries a strength label → [evidence.md](evidence.md).

## Scale the procedure

| Request | Run |
| --- | --- |
| New cost dashboard or new cost source | All steps |
| Review an existing cost dashboard | Step 7 first (lint), then 1, 3, 5 |
| "Spend is wrong", "doesn't match the invoice", "doubled" | Steps 2, 4, 7: [reconcile](framework.md#reconcile), [double counting](grafana.md#double-counting) |
| Forecast, budget or anomaly alert | Steps 3, 6 |
| One panel | Steps 3, 5, 7 for that panel |

## Procedure

1. **Name the reader and the decision.** Budget holder (will we land inside budget?), owner (what is mine, what moved?), engineer (which resource, how idle?), finance (does it match, who pays?). One dashboard per reader; variables (`team`, `tenant`, `project`) instead of copies. → [framework.md](framework.md#phases-and-readers)
2. **Reproduce the bill.** Read how the source bills (hourly with a monthly cap, per GB-month, per token, monthly plus setup, kWh) and compute cost the same way in an exporter or recording rule, prices read at runtime. Pin the rule with tests. List the gaps (deleted resources, traffic, credits). → [sources.md](sources.md)
3. **Fix the basis.** One per panel: billed (invoice) or effective (amortized) or list. Net of VAT; VAT applied once, from a named variable. One currency per panel. Periods in the billing timezone. → [framework.md](framework.md#cost-bases), [sources.md](sources.md#vat-and-currency)
4. **Build the series once.** Recording rules for month to date, projected month, run-rate and per-owner cost; `max by (<identity>)` inside every `sum`; a `job` filter on metrics two exporters publish; unit cost as same-window numerator ÷ denominator. → [grafana.md](grafana.md#recording-rules)
5. **Lay it out answer-first.** Row 1: month to date with delta, projected month against budget, full-month run-rate. Then what moved (top movers, month-over-month bridge), where it goes (owner table with unallocated as a row), per unit, per resource, and a trust row (freshness, exporter up, allocated share, known gaps). Stats and tables for single values and comparisons; time series only for change over time. → [layout.md](layout.md)
6. **Forecast and alert.** Pick the projection method that matches the billing model (`python3 scripts/forecast.py capped|linear|daily`); show the band and name the method. Alerts: forecast over budget, budget consumed, anomaly (relative and absolute threshold), unowned spend, idle resources, cost pipeline dead; each tested both ways. → [framework.md](framework.md#forecasts)
7. **Lint, query, reconcile, render.** `python3 scripts/dashboard_lint.py <dashboards>` (24 rules → [checks.md](checks.md)); run each query against the datasource; reconcile one closed month against the invoice; open the dashboard in a browser in both themes. Report what was and was not checked.
8. **Retain.** Billing model, gaps, budget source and reconciliation result go in the repository's runbook; the budget number lives in one place that the alert and the thresholds both read.

## Gotchas

- **Linear run-rate is wrong for capped billing.** Hourly-capped resources stop costing at their cap; month to date ÷ elapsed fraction overshoots (€ 39,31 against € 32,96 in [the case](case-unfold-hetzner.md)). On a mid-month inventory the full-month run-rate is next month's bill, not this month's.
- **Two exporters, one metric name.** OpenCost re-exports kube-state-metrics series by default; `sum(kube_node_status_allocatable)` doubles. Check `count by (job)`.
- **"No data" is not € 0,00.** A dead cost pipeline that renders zero reads as good news; the trust row and a pipeline alert catch it.
- **`currencyEUR` always prints a `.` decimal.** Dutch notation needs `currency:financial:€` and a Dutch browser locale; there is no server setting. Keep 2 decimals; unit prices may show 4.
- **The month is the provider's month.** Hetzner closes in UTC; a `browser` timezone shifts every boundary for the viewer.
- **Grafana 12.2+ rewrites `options.footer` on load**; keep `custom.footer.reducers` in git, and never sum a percentage, ratio or average column.
- **Inventory-based cost misses what was deleted.** Say so on the dashboard until an invoice reconciliation closes the gap.
- **Electricity price is a parameter.** 1 W continuous is 8.76 kWh a year: € 2,28 at € 0,26 per kWh, € 3,50 at € 0,40.

## Example

[case-unfold-hetzner.md](case-unfold-hetzner.md): a Hetzner Cloud project with no billing API, an exporter that reproduces the hourly-capped bill, a dashboard that separates month to date, projected month and run-rate, and what the linter and a false-positive pass on 85 dashboards found.

## Additional resources

- Rule reference and how to run the linter → [checks.md](checks.md)
- Example inputs for `forecast.py` → `examples/`
- Sources and attribution → [NOTICE.md](NOTICE.md)
