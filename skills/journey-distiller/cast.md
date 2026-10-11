# Role catalog

Start from this list, drop what the product cannot touch, add what its domain has. Every row on the
answer page carries: who, would do, mostly in, your guess, evidence. The owner classifies each as
**core**, **secondary**, **edge**, **outside the product** or **not a user**.

## Builders and reviewers

| Role | Usually does | Usually needs | Watch for |
|---|---|---|---|
| Solo developer or freelancer | everything: plans, builds, reviews, bills | speed, low ceremony, one place for all of it | often the owner dogfooding; a valid core user, not a proxy for every user |
| Senior or medior developer | builds, reviews, takes over stuck work | trust in what lands, evidence over transcripts, context in the editor | reviewer trust decides adoption of anything automated |
| Junior developer | small changes, learns the codebase | guidance, safe defaults, explanations | may start work they cannot judge in review; access needs limits, not exclusion |
| Tech lead or team lead | decides what gets done by whom, reviews, unblocks | throughput with control, cost before commit, a view of what is moving | usually the person handing work over; often also the reviewer |

## Product and process

| Role | Usually does | Usually needs | Watch for |
|---|---|---|---|
| Product owner | priority, refinement, acceptance, sign-off | readiness feedback, status without jargon | lives in the tracker unless the owner decides otherwise; ask where |
| QA or tester | checks a change against what was asked | a preview, the acceptance conditions, a way to report back | needs a preview environment to exist |
| Scrum master or delivery manager | flow and process health | flow numbers: age, cycle time, work in flight | numbers, not moments; rarely a daily user |
| Account manager | turns client asks into scope and quotes | quote status, what to tell the client | sits between the product and the client |

## Money, platform and oversight

| Role | Usually does | Usually needs | Watch for |
|---|---|---|---|
| Owner, CTO or buyer | buys, sets budgets and policy, answers for cost and quality | cost per delivered outcome, predictability, audit | the buyer; often not the daily user, but the one who judges the product |
| Platform engineer or admin | identity, configuration, integrations, health | SSO, provisioning, secrets handled safely, status | onboarding and offboarding are journeys of their own |
| Auditor or compliance officer | asks who did what, when and why | an export of the decision trail | rare, decisive; drives retention and audit design |
| Finance | invoices, reconciles spend | exports, consistent numbers | a different number in two places breaks trust fast |

## Outside the product's own screens

| Role | Usually does | Usually needs | Watch for |
|---|---|---|---|
| Client or end customer | asks, approves price, gives feedback | a price before work, progress, a preview | usually served by a portal, mail or the tracker, not the internal workbench |

## Splits to make explicit

- **Buyer vs daily user.** The buyer is judged on outcomes; the daily user on friction. A primary
  "user" answer naming the buyer usually means both: say so and confirm.
- **Hands work over vs reviews it.** Same person or not decides whether capacity limits are personal
  and whether review routing is needed.
- **Where each secondary role lives.** "In the product" means it needs screens, roles and
  permissions; "in the tracker" means the tracker must carry what it needs.
