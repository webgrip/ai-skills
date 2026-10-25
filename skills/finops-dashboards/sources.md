# Cost sources: how each bills, and how to turn it into series

Reproduce the provider's billing rule in code, pin it with tests, and reconcile once against an invoice ([framework.md](framework.md#reconcile)). Prices change: read them from the provider's API or a dated data file at runtime, never from this page. Strength tags: [evidence.md](evidence.md).

Contents: [Hetzner Cloud](#hetzner-cloud) · [Hetzner dedicated](#hetzner-dedicated-robot-and-server-auction) · [Kubernetes allocation](#kubernetes-allocation-opencost-kubecost) · [LLM and API spend](#llm-and-api-spend-litellm) · [Electricity](#electricity) · [SaaS](#saas-and-subscriptions) · [VAT and currency](#vat-and-currency)

## Hetzner Cloud

**Billing rule** (Hetzner docs, Strong):

- Every started hour at the hourly price, never more than the monthly price per resource per calendar month. Servers bill while powered off.
- Primary IPv4 bills while it exists, assigned or not; primary IPv6 is free.
- Backups add 20 % of the server price; snapshots bill per GB-month on their compressed size; volumes bill hourly with a monthly cap.
- Only outgoing traffic bills, beyond the included volume, in 100 MB blocks. Usage notifications at 75 % and 100 % do not stop traffic.
- Invoices arrive in arrears, can come up to 28 days after month end, and no invoice is issued below € 10 for up to three months. The console shows the current month's usage only.

**No billing or usage API.** The Cloud API has `GET /pricing` (net and gross, per location: server types, primary IPs, image price per GB-month, backup percentage, included traffic, price per TB) and the inventory endpoints; nothing returns cost. (Strong, API spec) So an exporter computes:

```text
month_to_date(resource) = min(started_hours(max(created, month_start), now) × hourly, monthly_cap)
projected(resource)     = min(started_hours(max(created, month_start), next_month_start) × hourly, monthly_cap)
per-GB items            = size_gb × price_per_gb_month, hourly = that ÷ 730
```

`forecast.py capped` implements the same rule for an inventory file. **Gaps to state on the dashboard**: resources deleted earlier in the month are on the invoice but not in the API (month to date undercounts them unless the exporter remembers them); traffic overage is not in the inventory; price changes apply to new orders and rescales from their effective date (Hetzner adjusted prices on 15 June 2026, e.g. CX23 € 3,99 → € 5,49 per month; Strong). Read prices from `/pricing`, so a price change lands without a code change.

**Labels**: put `role` and `cluster` (or `team`) labels on servers in Hetzner; let primary IPs inherit their server's labels when they have none. A server without the cluster label older than a couple of hours is the classic leftover (image-upload helper, hand-made test box): alert on it.

## Hetzner dedicated (Robot) and Server Auction

Dedicated servers carry a monthly price plus a one-time setup fee (example in the 2026 price notice: AX42 at € 97,30 per month plus € 49 setup; Strong). Server Auction machines have no setup fee and can usually be cancelled immediately. (Strong) Whether dedicated servers bill hourly like Cloud is contested between Hetzner pages; model them as monthly and reconcile. Robot has no cost API either: keep a small dated data file (server, monthly, setup, start date) and export it as series, or take the consumption CSV each invoice carries.

## Kubernetes allocation (OpenCost, Kubecost)

- OpenCost prices nodes (cloud price lists, or custom prices per CPU core-hour, RAM GiB-hour and storage GB-hour for on-prem) and allocates them to pods as **max(request, usage)**; the remainder is **idle**. (Strong) Kubecost uses the same definition: idle = cluster cost − allocated CPU, RAM and GPU cost. (Strong)
- `/allocation` returns `cpuCost`, `ramCost`, `pvCost`, `networkCost`, `loadBalancerCost`, `sharedCost`, `totalCost`, and efficiency fields; `includeIdle`, `shareIdle` and `idleByNode` default to false, and idle appears as an `__idle__` row. (Strong)
- Prometheus metrics include `node_total_hourly_cost`, `node_cpu_hourly_cost`, `node_ram_hourly_cost`, `pv_hourly_cost` and `container_cpu_allocation`. Hourly costs are gauges: monthly = average over the window × hours, never `sum_over_time` (that depends on the scrape interval).
- **Double counting**: OpenCost re-exports kube-state-metrics series under the same names while `EMIT_KSM_V1_METRICS` is on (the default; Helm `opencost.metrics.kubeStateMetrics.emitKsmV1Metrics`). (Strong, source) Filter on `job` or turn the flag off; see [checks.md](checks.md#double-counted-series).
- On-prem nodes: price them from the real cost (amortized hardware over its life + electricity at the wall + share of network), not cloud list prices; otherwise the "savings" panels are fiction.

## LLM and API spend (LiteLLM)

- `LiteLLM_SpendLogs` (Postgres) has one row per request: `spend`, hashed `api_key`, `model`, `model_group`, `user`, `team_id`, `end_user`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `startTime`, `request_tags`. Daily rollup tables (`LiteLLM_DailyUserSpend`, `LiteLLM_DailyTeamSpend`, with a `date` string) are cheaper for Grafana SQL panels. (Strong, source)
- Budgets per key, user or team: `max_budget`, `soft_budget`, `budget_duration`, `budget_reset_at`. (Strong)
- Prometheus metrics, when the `prometheus` callback is on: `litellm_spend_metric`, `litellm_total_tokens_metric` (and `_input_`/`_output_`), `litellm_remaining_{team,api_key,user,org}_budget_metric`. Whether `/metrics` needs an Enterprise licence changed across releases: check the deployed tag. `/global/spend/report` is Enterprise-only. (Strong, source at main)
- `spend` is the provider list price LiteLLM computed, in USD unless configured otherwise. Show USD with `currencyUSD`, or convert with a named FX series; never relabel.
- Unit cost: cost per run, per ticket, per merged PR = spend joined on the run's key or tag ÷ outcomes. Silent model fallbacks change the cost per run without errors; show spend by model next to it.

## Electricity

- Energy in kWh = average watts × hours ÷ 1000. One watt drawn continuously is 8.76 kWh per year.
- **Price is a parameter, not a constant.** In the Netherlands in 2026 the marginal all-in price (supply incl. VAT plus energy tax incl. VAT) is about € 0,26 per kWh on an average variable contract; contracts range to € 0,40. (Strong for the components, the sum is computed) One watt continuous then costs € 2,28 (at € 0,26), € 2,63 (€ 0,30), € 3,07 (€ 0,35) or € 3,50 (€ 0,40) per year. The fixed energy-tax reduction is per connection and does not change the marginal price.
- Measure at the wall (smart plug, PDU, UPS) where possible; modelled power from CPU utilisation is an estimate and the panel says so.
- Allocation: node power × pod share of node CPU (or of requests) gives a per-namespace energy cost; label it "modelled".

## SaaS and subscriptions

- No API, usually: keep a dated data file (`vendor, plan, monthly_net, currency, billing_period, renews_on, owner`) in git, export it as gauges, and show it in the same tables as metered spend.
- Yearly plans: effective cost = yearly ÷ 12 per month; billed cost spikes in the renewal month. Show renewals coming up in the next 60 days as a table.
- Seat-based plans: unit cost per active user, with seats bought vs used.

## VAT and currency

- **Store net.** Business-to-business services across EU borders fall under reverse charge: the supplier invoices 0 % VAT and the buyer self-accounts at its own rate (Directive 2006/112/EC, art. 44 and 196; Strong). A Hetzner invoice to a Dutch business with a VAT ID therefore shows 0 % VAT.
- Consumers are charged VAT; for electronically supplied services the rate is generally the customer's country's rate (Consistent, place-of-supply rules). Dutch rates: 21 % standard, 9 % reduced, 0 %. (Strong)
- Show gross only when the reader pays VAT and cannot reclaim it, apply it once from a named variable, and put "incl. VAT" in the title.
- **Currency**: one currency per panel; convert with a dated FX series named in the description. EUR with 2 decimals; in Dutch notation `€ 1.234,56` ([grafana.md](grafana.md#units-and-locale) for what Grafana can and cannot render).
