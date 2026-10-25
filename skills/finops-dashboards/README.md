# finops-dashboards

Designs, reviews and builds cost and FinOps dashboards: what we spend, where it goes, where the month will land against budget, and why it moved. It sits beside `kpi-groomer` (which KPIs to have), `dataviz` (how to draw a chart) and `product-ux` (dashboards as app screens); this one is about money being right and readable.

What it does:

- **Reproduces the bill before charting it.** Billing rules for Hetzner Cloud (hourly with a monthly cap, no billing API), Hetzner dedicated and Server Auction, OpenCost and Kubecost allocation and idle cost, LiteLLM spend and budgets, electricity in kWh with the price as a parameter, SaaS subscriptions, and EU reverse-charge VAT.
- **One cost basis per panel**, named after the FOCUS columns: billed, effective (amortized), list. Net of VAT, one currency, the provider's timezone.
- **Answer-first layout.** Month to date with a delta, projected month against budget, full-month run-rate; then movers, allocation, unit cost, per resource, and a trust row. Stats and tables for single values and comparisons.
- **Forecasts that match the billing model.** Inventory projection for capped billing, linear run-rate for usage, a daily trend with a band and robust anomaly flags.
- **Alerts** for forecast breach, budget consumed, anomalies (relative and absolute), unowned spend, idle resources and a dead cost pipeline.
- **Grafana specifics**: grafana-operator CRDs, currency units and what Grafana can and cannot do for Dutch number format, the 12.2 table-footer change, calendar periods in PromQL and MetricsQL, recording rules, SQL ledgers, and six ways totals get double counted.
- **Evidence-graded.** FinOps Foundation framework and maturity targets, FOCUS v1.4, Grafana and OpenCost docs and source, Few's pitfalls and bullet-graph specification, Cleveland–McGill and Heer–Bostock on graphical perception, NIST on robust outliers, WCAG 2.2; each claim labelled Strong, Consistent, Contested or Anecdotal.

## Install

```text
/plugin install finops-dashboards@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s finops-dashboards`.

## Example prompts

- "Build a Grafana dashboard for our Hetzner Cloud costs with a budget of 50 euro a month."
- "Review this cost dashboard before I show it to finance."
- "Our Kubernetes cost total is twice what the nodes cost. Why?"
- "Add an anomaly alert for LLM spend per API key."
- "Wat kost ons cluster per maand, en klopt de prognose?"

## Scripts

```bash
python3 skills/finops-dashboards/scripts/dashboard_lint.py path/to/dashboards/
python3 skills/finops-dashboards/scripts/dashboard_lint.py --json --fail-on warn dashboard.yaml
python3 skills/finops-dashboards/scripts/forecast.py --budget 50 capped --inventory inventory.json
python3 skills/finops-dashboards/scripts/forecast.py linear --mtd 31.10
python3 skills/finops-dashboards/scripts/forecast.py --budget 30 daily --csv daily-spend.csv
```

`dashboard_lint.py` reads dashboard JSON or GrafanaDashboard CRDs (`spec.json`) and contacts nothing; 24 rules, exit status 1 at or above `--fail-on` (default `fail`). `forecast.py` reads local files only. Both need only the Python standard library (3.9+). `test.sh` runs the linter on `fixtures/careless` (every rule must fire) and `fixtures/careful` (nothing may fire), the unit tests, and checks that the example inputs still reproduce the figures in the case study.
