# Flow metrics and the SLE

What to measure, what it means, and what it is for. The arithmetic lives in
[scripts/flow_metrics.py](scripts/flow_metrics.py) (offline, stdlib-only — feed it
normalized JSON). **Every metric must name the action it triggers** — a metric that
feeds no decision is theater.

## The definitions (Kanban Guide, v2025.5)

Four mandatory flow metrics, quoted:

| Metric | Definition | The action it feeds |
|---|---|---|
| **WIP** | "The number of work items started but not finished" | Refuse pulls over the cap; over-limit explains a bad cycle time by itself |
| **Throughput** | "The number of work items finished per unit of time" | Forecasting (Monte Carlo over item counts); trend vs WIP |
| **Work Item Age** | "The elapsed time between when a work item started and the current date" | **The one leading indicator**: age at/past the SLE ⇒ intervene today — split, swarm, unblock, or drop (and watch items approaching it) |
| **Cycle Time** | "The elapsed time between when a work item started and when a work item finished" | Recalibrating the SLE; right-sizing |

An **SLE** is a forecast with two parts: **an elapsed-time period and a probability**.
"85% within 8 days" is an SLE; "8 days" is a wish. Derive it from the board's own
completed history (default: 85th percentile), state it with its sample size, recompute
every ~10 finished items, and **never** turn it into a target to hold anyone to.

**Right-sizing replaces estimating**: once there's history, the refinement question is
"does this fit inside the SLE?" — if not, split. No story points: item counts forecast
as well as point sums, and pointed velocity collapses under Goodhart pressure the
moment anyone reads it in a review.

## Where start and finish live

"Started" and "finished" are the *contract's* Definition of Workflow (typical: started =
entering doing; finished = the agreement's real done status). Creation time is when
someone *wrote* the ticket — months before anyone started, on real boards. Without a
measured start the script falls back to created→finished and labels it a **lead-time
proxy**; a missing start is "no measured start", never zero. Trackers also lie:
done-*typed* statuses that the agreement treats as intermediate (merged/testing/
carryover) never count as finished — say so when your number disagrees with the tool's
own widgets.

## Running it

Normalize board data to the script's item shape (id, title, state, started, finished,
created, priority — ISO8601 or epoch ms; normalization recipe in your adapter's
time-in-status / timestamps section):

```bash
python3 scripts/flow_metrics.py --items board.json --wip-limit 3 --percentile 85
```

The script's WIP counts everything in its `--started-states` (default: doing **and**
review — the Kanban Guide's started-but-not-finished). A contract whose cap governs
`doing` alone: pass `--started-states doing`, and check the review column against its
own cap separately.

It reports WIP vs cap, Work Item Age oldest-first, weekly Throughput, the Cycle Time
distribution, the SLE — and **refuses to state an SLE under ~10 finished items**,
because a percentile over five tickets is theater. `--json` for machine-readable.

## Reading the result

- **Age above the SLE is the number that produces action today.** Age needs no history
  at all — start with it.
- **WIP over the limit explains a bad cycle time by itself.** Fix WIP before theorizing.
- **Throughput trending down while WIP trends up** is the signature of starting instead
  of finishing.
- **Pair every speed number with a stability guardrail** — rework rate, bounce-backs
  from test/review, reopens. AI-era telemetry shows throughput and instability rising
  *together*; rising throughput with rising rework is net-negative, and merged-without-
  review is a red flag, not velocity.
- **When agents execute, watch the review queue**: time-to-first-review and
  oldest-awaiting-review are the age metrics that matter most (measured: agent PRs wait
  ~5× longer for pickup). The review column gets its own WIP cap and its own SLE.
- **Forecast with ranges, never dates**: "when will it be done" gets a probabilistic
  answer at named confidence levels from recent throughput — and the sample is void
  after a regime change (team change, agent adoption); re-baseline instead of trusting
  stale history.
- **Track agent-ticket classes separately**: acceptance rate and bounce-backs per class
  decide where delegation expands ([agents.md](agents.md)).

## Honest caveats

- These are properties of the **workflow, never of a person** — no per-assignee
  rankings, human or agent; decline the request and offer a system-level view instead.
- Multiple started-intervals (ticket bounced back and forth): measured time in started
  states is closer to truth than first-touch-to-close, but differs from calendar-elapsed —
  report both when they'd differ materially.
- Don't build gates on **flow efficiency** percentages (wait-vs-active classification is
  arbitrary and timestamps too coarse) — use blocked-item count, blocked elapsed time,
  and queue age instead.
- A forecast is conditional on WIP control: without it there is no predictability and
  the Monte Carlo is decoration.
