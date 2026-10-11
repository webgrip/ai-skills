# Journeys

A user journey is one person's path from a trigger to an outcome they care about, across every tool
they touch. It is not a system flow, a screen list or a feature.

## Ranking

Score each candidate on two axes and rank by the product; the owner's first pick goes on top.

| Axis | High when |
|---|---|
| Frequency | daily or several times a day per user |
| Decisiveness | it decides whether people trust, adopt, pay for or can audit the product |

Rare but decisive journeys (prove what happened, set up an organisation) stay in the top list for an
enterprise product; they gate sales, not daily use. A typical top 10 for a work-delivery product:
review a change to a decision · start my day · hand work over · let ready work start itself ·
resolve work that needs a person · make work ready · accept and sign off · steer cost and quality ·
set up and govern an organisation · prove what happened.

## Template — every field, every journey

| Field | Contents |
|---|---|
| Name | verb phrase from the user's side: "review an agent pull request to a decision" |
| Actors | who acts, who is responsible, who is informed |
| Starts when | the trigger, as the user experiences it |
| Done when | the outcome the user cares about, not a system state |
| How often | per user per day or week |
| Stages | 3 to 8 stages, each with the tool used (tracker, product, forge, editor, mail) |
| Enterprise requirements | the permission each action needs, the audit event it writes, the policies that apply |
| States | first time, empty, too many, no permission, conflict, failure, and the journey-specific ones |
| Today | per stage: works, partly, missing, with the evidence |
| Success measure | one number with a formula and today's baseline (time from trigger to done, first-time rate) |
| Open questions | each with an owner |

## Writing rules

- Stages use the words the user sees, not component names.
- A stage that leaves the product (to the tracker or forge) is marked; leaving to finish is a finding.
- Configurable entities (teams, roles, workflows) stay variables: "a team", never one installation's team.
- A journey's design ticket ends in build tickets; designing and building are separate tickets.
