# Reference — frameworks, definition hygiene, law, failure modes, sources

Contents: [Frameworks](#the-frameworks-and-what-each-is-for) · [Definition
hygiene](#definition-hygiene--the-full-field-list) · [Delivery data that stays
honest](#delivery-data-that-stays-honest) · [Ethics & law (EU/NL)](#ethics--law-eunl) ·
[Person-level data in practice](#person-level-data-in-practice) · [Failure
modes](#failure-modes-checklist) · [Sources](#source-catalog)

## The frameworks, and what each is for

| Framework | What it gives you | The documented misuse |
| --- | --- | --- |
| **DORA** (five keys: change lead time, deploy frequency, change fail rate, failed-deploy recovery time, deploy rework rate) | A balanced speed+stability set at **application/service level**; baseline → discuss friction → improve ONE constraint → iterate | Targets (gets gamed), cross-team comparison ("context matters"), leaderboards, per-person attribution — all warned against on dora.dev itself |
| **SPACE** (Satisfaction, Performance, Activity, Communication, Efficiency/flow) | The selection floor: a set spans **≥3 dimensions** and includes **≥1 perceptual (survey) measure**; the myths table (productivity ≠ activity, ≠ individual, ≠ one metric) | Cherry-picking Activity metrics only — the exact myth the paper opens with |
| **DevEx** (feedback loops, cognitive load, flow state) | Pair perception (survey) with workflow (system) data per dimension | Treating surveys as "soft" and dropping them — they are half the signal |
| **Flow metrics** (Kanban Guide / Vacanti): WIP, throughput, cycle time, work item age | The generic vocabulary that fits ANY kind of work (also non-dev teams); **SLE = percentile + timebox** ("85% ≤ 8 days") derived from historical scatter; work item age is the only leading indicator of the four | Averages on right-skewed distributions; monthly throughput "targets" on small-n teams (coin flips) |
| **EBM** (scrum.org): Current Value, Unrealized Value, Time-to-Market, Ability-to-Innovate | The governance model to copy: **areas fixed, measures chosen locally** — no mandatory metrics | Adopting its example measures verbatim as mandates |
| **North-star / driver trees** (Amplitude playbook) | Org level: one outcome you can't move directly + 3–5 input metrics as levers; the tree is an explicit causal-belief model | A "north star" nobody can influence, with no input metrics under it |
| **Leading vs lagging** (Kaplan & Norton, Balanced Scorecard) | Outcomes confirm the strategy worked; drivers tell you mid-flight — a healthy set has both | All-lagging sets: you learn you failed, quarterly |

Two provenance anchors worth citing in sessions: the **decision test** is Hubbard
(*How to Measure Anything*): a measurement that could change no decision has no value —
and name the threshold at which you'd decide differently. The **pairing rule** is Grove
(*High Output Management*): every effect metric gets a counter-effect metric so
optimizing one can't silently degrade the other.

The workshop spine is **GQM** (Basili): Goal (object, purpose, quality focus,
viewpoint) → Questions → Metrics — in that order. Metrics chosen before goals is the
failure GQM exists to prevent.

## Definition hygiene — the full field list

Name · formula **including denominator and exclusions** · data source/system of record ·
measurement level (team/service — never person unless the ethics gate passed) ·
direction · current **baseline** (measure before any target) · signal threshold or
target, with why that number · **the decision it changes + who makes it** · owner ·
review cadence · review-by/retire-by date · its guardrail pair.

Percentiles over averages for anything skewed (cycle time, latency). Ratios carry their
n ("96% of 20" means nothing). Vanity metrics (cumulative counts that only go up — Ries)
demonstrate no cause and effect; actionable metrics do.

## Delivery data that stays honest

- **Deploy frequency counts deployment records** against production-tier environments,
  never green pipelines: a pipeline count once reported 29 deploys a day.
- **Store each deployment's ref**, so lead time and drift can be computed from what
  actually runs.
- **A trunk bypass is a hotfix only when it is a fix** (a `fix` change, a `hotfix` branch);
  call the rest "direct to release branch" instead of flattering the incident count.
- **Show drift with its age**: per repo, release-branch commits not on trunk and production
  commits the acceptance environment lacks (the forge's compare API, cached per SHA pair),
  next to the age of the oldest change waiting in each stage.
- No people, no rankings — delivery data is a service-level view.

## Ethics & law (EU/NL)

- SPACE and DORA both: measure teams and systems, **never rank individuals**; individual
  activity metrics miss invisible work, vary by task type, and are trivially gamed.
- Person-level data = personal data (GDPR): legitimate-interest balancing, transparency
  toward employees, retention limits; systematic employee monitoring is on the AP's
  mandatory-**DPIA** list.
- NL: a system that *can* track presence, behavior or performance of employees is a
  **personeelsvolgsysteem** — **the effect decides, not the stated purpose** — requiring
  works-council consent under **WOR art. 27 lid 1 sub l** (monitoring) and **sub k**
  (personal-data processing rules). A dashboard with per-developer filters qualifies,
  even when built "for coaching". Per-developer AI usage (tokens or cost per person) and
  review data that links reviewer to author plausibly qualify too; a cost-control purpose
  does not take them out of scope.
- The rest of art. 27: no consent is needed where a CAO already regulates the matter
  (lid 3); the employer can ask the kantonrechter for substitute permission (lid 4); a
  decision taken without consent is void if the OR invokes that in writing within one
  month (lid 5).
- Which body applies depends on size: an OR is required from (as a rule) 50 people
  (art. 2). A personeelsvertegenwoordiging, below 50, has consent rights only for sub b,
  d and m — **not sub l**. Check which body the company actually has; GDPR and the
  DPA's conditions apply either way.
- The DPA (Autoriteit Persoonsgegevens): monitoring must be necessary and outweigh the
  intrusion; the basis is legitimate interest, because employee consent is unusable under
  the power imbalance; employees are told in advance; "Stemt de OR er niet mee in, dan mag
  u niet controleren."

## Person-level data in practice

- **Count, don't name.** Default to team or repo aggregates; a usage view shows totals and
  a *count* of active developers, never a list of who.
- **Strip identity where the data enters, until consent exists.** Agent telemetry stamps
  every datapoint with the user's email, account ids, a user id and a session id (Claude
  Code sends the email whenever the user is signed in, with no client switch to turn it
  off), and LLM-gateway metrics carry key alias, user and email labels. Drop them in the
  collector or the scrape config, not in the dashboard — the `agent-platform` skill, where
  installed, has the collector side.
- **Per-person series live in their own store.** A per-person series that also carries
  `team` shows every member their teammates' numbers through any team-scoped datasource;
  hiding a board does not hide the data. Keep those series in a separate small store that
  only the people entitled to them can query, and drop them from the shared one.
- **Print the rules on the per-person view itself:** who may read it (an explicit grant,
  listed), what it is never used for (performance review, ranking, bonus), rows sorted by
  name and never by value, and what each number cannot tell — review counts say nothing
  about care; merged counts show how work was cut up; open PRs are a flow problem; pickup
  and cycle time carry meetings, holidays and part-time contracts; pair work is credited
  to one name; bots are filtered out.

## Failure modes checklist

1. **Metric graveyard** — defined, dashboarded, never reviewed. Cause: no owner + no
   decision + no retire path. Cure: review-by date; a metric unreviewed 2–3 cycles is a
   retirement candidate; retire explicitly (announce, archive the definition).
2. **Leaderboards / weaponized metrics** — triggers Goodhart gaming and destroys the
   psychological safety the data collection depends on.
3. **Christmas tree** — 30–40 metrics because every stakeholder added one. Cure: the
   3–5 cap + Hubbard's decision test per metric.
4. **Cargo-culting another company's metrics** — a metric answers a local question
   (GQM); it doesn't transplant. DORA: context matters.
5. **Measuring what's easy over what matters** — activity counts because the tooling
   has them (SPACE myth #1; McNamara fallacy).
6. **Targets on proxies** — Goodhart. Mitigations: pairing (Grove), trends over
   absolutes (DORA), signal thresholds instead of incentive-linked targets.

## Source catalog

| Topic | Source |
| --- | --- |
| DORA metrics + misuse guidance | dora.dev/guides/dora-metrics/ · dora.dev/quickcheck/ (baseline) |
| SPACE paper | queue.acm.org/detail.cfm?id=3454124 (blocks automated fetches — link, don't scrape) |
| DevEx papers | queue.acm.org/detail.cfm?id=3595878 · …?id=3639443 (DevEx in Action) |
| Flow metrics / SLE | kanbanguides.org/the-kanban-guide/ · Vacanti, *Actionable Agile Metrics for Predictability* |
| EBM guide | scrum.org/resources/online-evidence-based-management-guide |
| SLI/SLO/error budgets | sre.google/sre-book/service-level-objectives/ · sre.google/workbook/error-budget-policy/ |
| Decision test | Hubbard, *How to Measure Anything* (2007) |
| Pairing indicators | Grove, *High Output Management* (1983) |
| GQM | cs.umd.edu/users/mvz/handouts/gqm.pdf (Basili et al., 1994) |
| North-star trees | Amplitude North Star Playbook (amplitude.com/blog/product-north-star-metric) |
| NL works council & monitoring | autoriteitpersoonsgegevens.nl (OR-privacyboekje; DPIA list; "Voorwaarden voor controle werknemers") · WOR arts. 2, 27, 35c, 35d (wetten.overheid.nl/BWBR0002747) |
| Goodhart in practice | jellyfish.co/blog/goodharts-law-in-software-engineering-and-how-to-avoid-gaming-your-metrics/ |
