# Framing: tasks and evidence before pixels

The commonest agent failure is jumping straight to building. An hour of framing makes every later choice checkable: hierarchy ranks against tasks, critique measures against an objective, and the report can say honestly what nobody validated.

Contents: the evidence ledger · job stories · top tasks · task model · assumptions map · hypothesis and signal · the one-hour recipe

## The evidence ledger

You usually have no users, only traces of them. List what you actually have before reasoning about people.

| Source | What it can tell you | What it can't |
| --- | --- | --- |
| Support tickets, issues, chat logs | Where people get stuck, in their own words; frequency by cluster | Who never complained |
| Analytics export, server logs | Route frequency, funnels, drop-off, validation errors that fire most | Why |
| Search logs | Vocabulary mismatch (null-result queries), what people look for | Intent behind the query |
| The code | Every path, branch, limit, permission and error the UI can reach | How often a path is used |
| Docs, README, onboarding copy | The intended model of the product | Whether people share it |
| Existing UI and screenshots | Learned conventions you must not break | Whether they work |
| Session recordings, rage-click reports | Observed behaviour | Representativeness |
| Requester's statements | Context and constraints | Verified facts (mark as supplied) |

Tag every claim later in the work with its source. Anything with no source is an assumption and goes on the map below, not into the design as a fact.

## Job stories

Replace "As a [persona] I want…" with the situation that triggers the need ([Klement](https://jtbd.info/replacing-the-user-story-with-the-job-story-af7cdee10c27)):

```text
When <situation>, I want to <motivation>, so I can <expected outcome>.
When a customer disputes a charge, I want to see the order, payment and messages in one place, so I can decide within the call.   [source: 214 tickets tagged "refund", Q3]
```

The situation, not the demographic, carries the design context ([Christensen et al.](https://hbr.org/2016/09/know-your-customers-jobs-to-be-done)). Write 3–7, each tagged with its evidence. Never invent personas with names, ages and quotes; that is fabricated research.

## Top tasks

A handful of tasks carry most of the use; the long tail matters less ([McGovern](https://alistapart.com/article/what-really-matters-focusing-on-top-tasks/)). The real method needs a vote by a few hundred users. Without that, build a **proxy ranking** from behaviour (route views, ticket volume, search queries) and label it `proxy ranking from <source>, not a top-tasks survey`. Draft the survey for humans to run if the decision is big.

## Task model

For each top task, write a hierarchical task analysis straight from the code: goal → sub-goals → operations, with the plan (order, conditions). Then score:

| Task | Frequency (per user per day/week/month) | Criticality (cost of an error) | Users (novice / expert / both) | Steps | Decisions | Things remembered or re-typed |
| --- | --- | --- | --- | --- | --- | --- |
| Refund partial order | ~40/day per agent | High (money) | Expert | 9 | 3 | Order number re-typed once |

Frequency and criticality decide the design stance:

| | Rare | Frequent |
| --- | --- | --- |
| **Low cost of error** | Discoverable, guided, plain | Fast: defaults, shortcuts, bulk, no confirmations, no animation |
| **High cost of error** | Guided, review step, explicit confirmation | Fast and safe: undo, previews, sensible defaults, confirmation only for the irreversible |

Expert and novice paths can coexist (keyboard shortcuts and visible controls), but the frequent expert task should never pay the novice's tax on every repetition.

## Assumptions map

Plot each assumption on importance × evidence and attack the important, low-evidence quadrant first ([Bland](https://www.slideshare.net/slideshow/introduction-to-assumptions-mapping-agile2017/78675593)). This is the framing tool that fits an agent best, because evidence is exactly what it lacks.

| Assumption | Type (desirable / usable / feasible) | Importance | Evidence we have (source) | Cheapest test | Who runs it |
| --- | --- | --- | --- | --- | --- |
| Agents refund from the order page, not the ticket | Usable | High | None | Ask two agents; check the referrer on `/refunds` | Human |

## Hypothesis and signal

Every non-trivial change gets a falsifiable statement and the signal that would disprove it:

```text
We believe <outcome> will happen if <users> get <benefit> from <change>.
We'll know we're wrong if <signal> does not move within <period>.
```

Pick signals per goal from HEART (happiness, engagement, adoption, retention, task success) via goals → signals → metrics ([Rodden et al.](https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/)), pair a speed metric with a quality metric (load `kpi-groomer` for metric design), and add the instrumentation: `task_started`, `task_completed`, `task_failed{reason}`, validation messages shown. Analytics that need consent need it before they fire.

The agent can design an experiment (hypothesis, primary metric, guardrails, sample size, duration, sample-ratio check) but never declares a winner. Peeking after every observation can turn a 5 % false-positive rate into 26 % ([Miller](https://www.evanmiller.org/how-not-to-run-an-ab-test.html)); about 6 % of Microsoft experiments show a sample ratio mismatch, which invalidates them ([Microsoft](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/)); a surprising result is usually a bug (Twyman's law, [Kohavi et al.](https://experimentguide.com/)). Low-traffic B2B products often can't power an A/B test at all; test qualitatively instead.

## The one-hour recipe

| Minutes | Artefact |
| --- | --- |
| 0–10 | Evidence ledger: read README, routes, existing screens, tickets, any analytics export |
| 10–20 | 3–7 job stories with sources |
| 20–30 | Proxy top-task ranking; task model for the top 1–3 tasks |
| 30–40 | Assumptions map |
| 40–50 | Flow map and state inventory for each top task ([states.md](states.md)) |
| 50–60 | Hypothesis, signal, instrumentation, and the "not validated with users" list |

Keep these artefacts next to the code in the repository's docs convention, so the next person (or agent) starts from them. Durable design decisions go into an ADR via `adr-writer`, with the options, criteria and the validation status.
