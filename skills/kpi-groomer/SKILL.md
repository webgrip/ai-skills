---
name: kpi-groomer
description: Define, groom and facilitate KPI sets for teams, organizations, projects and individuals — complete KPI definitions (formula, data source, owner, baseline, target, the decision it changes), Goodhart speed/quality pairs, timeboxed KPI-choosing workshops the team owns, mapping KPIs onto existing dashboards, review-and-retire cadence, and the ethics gate for person-level metrics (SPACE, GDPR/works council). Use when defining or choosing KPIs or metrics for a team, organization or project, preparing or facilitating a KPI session or metrics workshop, reviewing or grooming an existing KPI set or dashboard for steering value, pairing a speed metric with a quality metric, deciding whether or how to measure individual people, or when asked what should we measure, which KPIs matter, or to put targets on a dashboard.
---

# KPI groomer — metrics that change decisions

## Resolve the measurement contract first

The consuming repo's `AGENTS.md` (or CLAUDE.md) carries a **Measurement contract**
(template in this plugin's README): where KPI definitions live, the measurement
charter, dashboard base URL + access, teams in scope, existing data sources, and the
person-level policy. Without one: inventory the dashboards and exporters that exist,
ask which teams are in scope, and suggest adding the block.

## The bar: every KPI names the decision it changes

A complete definition has: **formula (incl. denominator and exclusions) · data source ·
frequency · direction · baseline → target (or signal threshold) · owner · review-by
date · the decision it changes** (Hubbard's test: name the threshold at which you'd
decide differently). A KPI that changes no decision comes off the list. Max ~5 per
team. Measure the baseline before setting any target. For durations, use percentiles —
averages hide the skewed distribution the decision cares about.

## Goodhart pairs

Every speed/volume KPI gets a quality counterpart in the same set. The gaming test:
*"how do we improve this number while making the work worse?"* — the answer names the
missing pair. A set with unpaired speed metrics is an incentive to ship worse, faster.

## Level decides the metric

| Level | Question it answers | Shape |
| --- | --- | --- |
| Organization | are we healthy, are promises kept? | north-star set, ≤7, owner per KPI |
| Team | is our flow improving? | ≤5, chosen BY the team, speed/quality-paired |
| Project/customer | promised vs delivered? | one standard set, identical per project |
| Person | am I growing, is my load sane? | self-insight only — ethics gate below |

Don't aggregate blindly upward — each level answers a different question. Don't compare
teams on each other's KPIs; contexts differ and the comparison gets gamed.

## Inventory before defining

List what is already measured (dashboards, exporters, board data) and map candidate
KPIs onto existing panels first. A gap becomes a data ticket; a KPI without a live data
source is a wish, not a KPI. Teams whose work no pipeline covers get metrics that fit
their work — never borrowed developer metrics.

## The KPI-choosing workshop

Timebox ≤ 1.5 h, whole team present. Three questions structure it — the GQM order
(goal → question → metric), never metrics-first: *what do we want to improve?* → *how
would we SEE it improving?* → *what is the quality pair so we don't optimize it to
death?* Open the live dashboards during the session — choosing from what you see beats
choosing from a list. The facilitator brings a menu as a starting point, never a
mandate: KPIs imposed on a team get ignored or gamed. Check the result against the
SPACE floor: the set spans ≥3 dimensions and includes ≥1 perceptual (survey) measure.
Output: a concept set in the definition format, ratified against the charter afterward.

## Person-level metrics — the ethics gate

Default: measure teams and systems, not individuals — individual activity metrics
(commits, hours, tickets) measure activity, not value, and rankings kill collaboration.
Person-level visibility only when ALL four hold: **symmetry** (the person sees exactly
what any viewer sees) · **purpose limitation** (coaching/workload, never silent
appraisal input — appraisal requires a separately agreed HR process) · **transparency**
(everyone knows what is collected and who sees it) · **no leaderboards, ever**. In the
EU these are personal data (GDPR); in NL any system that *can* track employee
performance is a *personeelsvolgsysteem* — the effect decides, not the stated purpose —
requiring a works-council consent check (WOR art. 27). No ratified charter → treat
everything as team-level only.

## Keep it alive

Review on the contract's cadence (default: quarterly). Each KPI defends itself with the
decision it changed since last review — otherwise retire it. Dashboards are the
artifact: every KPI panel links to its definition, and definition + panel change in the
same MR. Fewer KPIs, watched, beat many, ignored.

## Additional resources

- Frameworks (DORA, SPACE, DevEx, flow metrics, EBM), misuse patterns, and the source
  catalog → [reference.md](reference.md)
- Tickets for KPI work (session tickets, data tickets, the write-to-teach pass) → the
  `product-owner` skill
