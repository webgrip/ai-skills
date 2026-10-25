# FinOps method: cost bases, allocation, forecasts, anomalies, alerts

Strength tags point at [evidence.md](evidence.md): **Strong**, **Consistent**, **Contested**, **Anecdotal**.

Contents: [Phases and readers](#phases-and-readers) · [Cost bases](#cost-bases) · [FOCUS columns](#focus-columns) · [Allocation, showback, chargeback](#allocation-showback-chargeback) · [Unit economics](#unit-economics) · [Forecasts](#forecasts) · [Budgets](#budgets) · [Anomalies](#anomalies) · [Alerts](#alerts) · [Allocation hygiene](#allocation-hygiene) · [Reconcile](#reconcile)

## Phases and readers

The FinOps Foundation framework has three phases, **Inform, Optimize, Operate**, and groups capabilities under domains: Understand Usage & Cost (Data Ingestion, Allocation, Reporting & Analytics, Anomaly Management), Quantify Business Value (Planning & Estimating, Forecasting, Budgeting, KPIs & Benchmarking, Unit Economics), Optimize Usage & Cost, and Manage the FinOps Practice (incl. Invoicing & Chargeback). (Strong)

A dashboard serves one phase and one reader. Write the reader's decision before the first panel:

| Reader | Question | First row shows |
| --- | --- | --- |
| Budget holder, exec | Will we land inside budget? What moved? | Month to date with delta, projected month against budget, top mover |
| Team or service owner | What is mine, and why did it change? | My cost this month, change by component, unit cost |
| Engineer optimizing | Which resource, how idle, what to cut? | Per-resource table sorted by projected cost, idle and efficiency |
| Finance | Does it match the invoice? Who pays? | Billed cost by invoice period, allocation coverage, chargeback per owner |

The framework's maturity steps for Reporting & Analytics: Crawl shows actual spend and trend only, Walk adds projected versus actual, Run surfaces variance as soon as a threshold is breached. (Strong) A dashboard without a projection is Crawl.

## Cost bases

Pick one basis per panel and name it in the description.

| Basis | What it is | Use for |
| --- | --- | --- |
| **Billed** (cash, invoiced) | What the invoice says for the billing period; upfront purchases appear as spikes | Reconciling to invoices, cash planning |
| **Effective** (amortized) | Usage cost with prepayments and commitments spread over the period they cover | Showback, trends, unit cost, anomaly baselines |
| **List** | Usage × public price, before discounts | Savings achieved, what-if |
| **Contracted** | Usage × your negotiated price | Rate optimization |

Without amortization a reserved-instance or yearly SaaS fee shows as a spike on the day it is charged; AWS's worked example spreads $30 upfront plus $2.48 per month to $0.165 per day. (Strong) For homelab-scale estates (hourly-capped clouds, monthly SaaS, electricity) billed and effective are usually equal; say so rather than leaving it implicit.

**Net vs gross.** Keep every series net of VAT. Business invoices under EU reverse charge carry 0 % VAT ([sources.md](sources.md#vat-and-currency)); apply VAT once, at display, only when the reader pays it.

## FOCUS columns

FOCUS (FinOps Open Cost and Usage Specification) normalizes billing exports; v1.4 is the current release and AWS, Azure and Google Cloud export at 1.2. (Strong) When a source is FOCUS-shaped, use these columns; when it is not (Hetzner, electricity), name your own series after them so the semantics carry over.

| Column | Meaning | Panel use |
| --- | --- | --- |
| `BilledCost` | Cost as invoiced in the billing period; 0 for usage fully covered by a commitment | Invoice reconciliation |
| `EffectiveCost` | Amortized cost recognized in the charge period; 0 on the purchase row it spreads | Showback, trends, unit cost |
| `ListCost`, `ContractedCost` | List or contracted unit price × pricing quantity | Savings, rate work |
| `ChargePeriodStart` | Start of the period the charge applies to | Time axis |
| `BillingPeriodStart` | Invoice period | Grouping for reconciliation |
| `ChargeCategory` | Usage, Purchase, Tax, Credit, Adjustment | Exclude Tax for net; show Credit separately |
| `ChargeClass` | `Correction` for a correction to a closed billing period | Flag closed months that changed |

Summed over a purchase and the usage it covers, EffectiveCost equals BilledCost; per period the two differ. (Strong) Never add the two in one panel.

## Allocation, showback, chargeback

- **Showback** reports cost to the owner without moving money; the framework says it is always required. **Chargeback** posts the cost into the owner's budget and P&L. (Strong)
- Allocate by an ownership label (`team`, `tenant`, `project`, `cluster`, `role`). Show unallocated cost as its own row, named, never folded into "other".
- **Shared and idle cost.** Kubernetes cost tools split node cost into allocated (max of request and usage, per pod) and idle (the rest). OpenCost returns idle as an `__idle__` row; `shareIdle` spreads it over owners. (Strong) Decide per dashboard: show idle separately (engineering view, it is the target for rightsizing) or share it (chargeback view, so totals match the bill). State which.
- A chargeback table's footer must equal the bill. If it does not, the difference is a row.

## Unit economics

Unit cost = cost of the thing ÷ units of value it produced over the same period: per tenant, customer, run, build, request, token, GB stored. (Strong as framework guidance) Rules:

- Numerator and denominator over the same window and the same scope. `sum(increase(cost[30d])) / sum(increase(builds[30d]))`, never an instantaneous cost over a monthly count.
- Use effective cost so commitments do not spike the unit cost on purchase day.
- Show the unit cost next to the volume: a falling unit cost with rising volume is good, the same unit cost with collapsing volume means fixed cost is spread thinner.
- Unit prices may carry more than 2 decimals (€ 0,0042 per run); totals do not.
- Fully loaded unit cost (with shared platform cost) is the Walk step; start with direct cost and say so.

## Forecasts

`scripts/forecast.py` implements the three methods below.

| Method | Formula | Right when | Wrong when |
| --- | --- | --- | --- |
| **Inventory projection** (`capped`) | Each resource: billed units to period end × price, capped per the provider's rule | Billing is per resource-hour with a cap (Hetzner Cloud), or flat subscriptions | Usage-driven spend |
| **Linear run-rate** (`linear`) | Month to date ÷ elapsed fraction of the month | Smooth usage-driven spend | Capped billing (overshoots once resources hit their cap), front-loaded charges, month starts |
| **Daily trend with band** (`daily`) | Complete days so far + mean daily × remaining days, ± 1.96 × sd × √remaining | Daily cost series with noise | Strong weekly seasonality (use same-weekday means), fewer than ~7 days of data |

- **Capped billing breaks the linear run-rate.** For the inventory in [the case](case-unfold-hetzner.md), month to date on the 25th is € 31,10; extrapolating linearly gives € 39,31 while the bill will be € 32,96. (Anecdotal, one estate, reproducible with the example files)
- **Seasonal projection**: replace the mean with the mean of the same weekday over the last 4–8 weeks; for monthly seasonality compare with the same day last month, not last 30 days.
- **Driver-based** forecasts (cost = units forecast × unit cost) are the framework's Run step. (Strong) Use them when a business number (tenants, runs) drives spend.
- Show the band, not only the point; label the method in the description.
- Measure forecast accuracy: |forecast at day N − actual| ÷ actual, recorded per month. Framework maturity targets for forecast variance: Crawl below 20 %, Walk below 10 %, Run below 5 %. Budget variance targets are separate: 20 %, 15 %, 12 %. (Strong)

## Budgets

- One budget literal, one source: the alert rule, a recording rule, or a dashboard constant; the panel thresholds reference the same number. The linter cannot cross-check files; grep.
- **Burn-down**: remaining budget against remaining days. Ideal line = budget × (remaining days ÷ days in month); show actual remaining as the second series, or as a bar gauge with the ideal as threshold.
- Budget used % is a 0–1 ratio under `percentunit`.
- Month boundaries in the billing timezone.

## Anomalies

An anomaly is spend that differs (usually higher) from what was expected; the framework measures time to detect, time to notify the owner and how long anomalies stay unresolved. (Strong) AWS, Azure and Google all forecast an expected baseline from history and flag deviations; Google combines a deviation percentage with an absolute cost impact. (Strong)

Practical detectors, cheapest first:

| Detector | Rule | Notes |
| --- | --- | --- |
| Robust z (modified z-score) | 0.6745 × (x − median) ÷ MAD; flag above 3.5 | NIST recommends it over the plain z-score, whose maximum is bounded by (n−1)/√n on small samples (Strong). `forecast.py daily` prints these |
| Seasonal baseline | Today vs same weekday, last 4 weeks; flag above k × MAD | Cuts weekday/weekend false positives |
| Absolute floor | Ignore deviations below a euro amount | Stops 300 % alerts on € 0,02 |

Require both a relative and an absolute threshold (Google's rule, Strong as vendor doc). Route the alert to the owner label, with the top contributing resource in the message.

## Alerts

| Alert | Expression shape | For / route |
| --- | --- | --- |
| Forecast breach | projected month > budget | 15–60 min; budget holder |
| Budget consumed | month to date > 80 % / 100 % of budget | owner; 100 % pages only if spend is still accruing |
| Anomaly | daily cost above baseline by both % and € | owner of the top contributor |
| Unowned spend | cost with empty owner label > threshold, or a resource outside known clusters older than N hours | platform team |
| Idle resource | allocated cost with near-zero usage for days; unattached IPs, volumes, snapshots | owner, weekly digest rather than page |
| Pipeline dead | exporter not scraped, last refresh older than 2 × interval, API token rejected | platform; a silent cost pipeline reports € 0 or stale numbers |

Every cost alert is tested both ways (fires on a breaching fixture, stays quiet on a normal one) with the rule engine's own unit test (`vmalert -rule ... -test`, `promtool test rules`).

## Allocation hygiene

Measure it on the dashboard, in the trust row:

- **Allocated share** = cost with a valid owner label ÷ total cost. Framework maturity: Crawl at least 70 %, Walk 85 %, Run above 90 %. (Strong)
- **Unallocated cost** in euros, as a named row and a stat.
- **Untagged resources** count by kind, with the cost they carry.
- Run: ownership metadata enforced as a precondition for provisioning (admission policy, Terraform validation). (Strong)

## Reconcile

A cost dashboard is trusted after one reconciliation, not after it renders:

1. Pick a closed month. Take the invoice (or the provider's consumption CSV) total, net.
2. Compute the same month from your series at month end. Differences above 1 % get a named cause: deleted resources (inventory-based exporters never see them), traffic overage, rounding, taxes, credits, FX.
3. Write the gaps into the panel description and the runbook. Re-reconcile after any exporter or price change.
