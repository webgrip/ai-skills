# Refinement — raw ticket → Ready (→ agent-ready)

The gates are in [SKILL.md](SKILL.md); the agent-ready specifics in [agents.md](agents.md).
This file is the execution: procedure, criteria craft, templates, splitting, and bulk work.

## Per-ticket procedure

1. **Research before writing.** Read the repo (manifests, source, docs tree, ADRs,
   runbooks) and live state where the premise depends on it. Every Problem claim and
   every criterion cites `file:line`, a command output, or a decision record.
   **Never invent** — information the sources don't contain becomes an explicit
   `MISSING — question for <owner>: …` line, never synthesized content. When refining,
   diff your rewrite against its inputs and strip any factual claim with no provenance.
2. **Ground in the up-to-date project.** Locate the checkout (**ask for the path rather
   than guessing**), `git fetch`, and research against the development branch (else the
   default branch) — never a stale checkout; it reproduces exactly the stale premises
   refinement exists to catch. No checkout available → say so and mark unverified claims
   as open questions. Stamp the report: `researched against <branch> @ <short-sha>`.
3. **A stale premise is a finding.** Already shipped, or the failure no longer
   reproduces? Rewrite Problem as "Premise stale — shipped in <commit/date>", turn the
   criteria into verification checks (verify-and-close), and report it. Never silently close.
4. **Read the current description first**, then write the merged version in one update —
   both adapters **replace** the whole description; anything not carried over is gone.
   Fold decisions buried in comments into the body (agents read the whole thread without
   judging recency) and note which comments are superseded.
5. Set the fields/labels the target gate needs (contract taxonomy); correct drift you
   find and say that you did. On boards with estimation labels (`effort/` `time/`
   `uncertainty/`): set all three **at refinement, not at intake** — they gate
   agent-ready, not Ready; effort L names its first shippable slice or gets split;
   uncertainty high gets a spike or an explicit de-risk step first.
6. Sizing trips (doesn't fit the SLE / above ~a junior-engineer day for agent work)? Split (below).
7. **Report per ticket**: one line what changed + gaps left open. **Close by asking for
   material keyed to the gaps** — not a generic "anything else?": an open question wants
   the answer or the e-mail that settles it; a Problem without evidence wants the support
   ticket or the metric; a bug without reproduction wants a screenshot or recording.
   Supplied material gets worked in, not parked: facts into the description (quotes in
   original language in a code block), files attached to the ticket, the gap list updated.

## What makes a criterion binary

The gate: **two people (or two agents) read it and reach the same conclusion.** A
criterion that asks for a judgement — "works well", "properly documented", "voldoende
beveiligd" — is a discussion booked for the review. Agents are worse: they treat an
unverifiable criterion as automatically satisfied.

| Weak | Binary |
|---|---|
| Pipeline is faster | Median pipeline duration on main < 8 min over 20 consecutive runs |
| Alerts are more useful | Every firing alert links to its runbook and dashboard |
| Backups work | Yesterday's backup restored in staging, checksum equal |

- **A good criterion closes the cheap way out; the Verification closes the second one
  you only see when you think about it.** (Criterion: "no test disabled to hit the
  time"; Verification: "measured on main, not a warm feature branch".)
- **EARS grammar** is the evidence-backed pattern for behavior criteria — one
  trigger→response sentence in fixed order: `When <trigger>, the <system> shall
  <response>` / `If <error condition>, then … shall …`. Use it to rewrite vague
  criteria ("handle errors gracefully" → "If the API returns 5xx, the UI shall show a
  retry action within 2s"). Feature work: **at least one error-path (`If…then`)
  criterion** — happy-path-only is the most common gap.
- **Given/When/Then only where it will become an automated behavior test or the
  precondition state matters** — there is no evidence it beats plain checklists
  elsewhere, and it costs more to maintain.
- Undefined qualifiers are latent wrong decisions: hunt "outdated", "large", "invalid",
  "the users" and force a definition or a glossary pointer.

## The refinement interview

Bad tickets are written from memory by someone who already knows the answer. Ask only
the questions that are actually open — a question answerable from the repo is research,
not an interview. The human holds the domain context (edge cases, settled trade-offs,
non-goals); capturing it is the interview's whole point — missing domain context is the
main predictor of failed agent runs.

- **Problem** — What goes wrong today, concretely? Who notices, how often? What does it
  cost? What happens if we never do this? *(No answer to the last one = a preference —
  fine, label it honestly.)*
- **Outcome** — When finished, what is true that isn't now? A state, not an activity.
- **Criteria** — What is the number? What's the cheapest way to technically pass without
  solving the problem — and which criterion closes that door? What must keep working?
- **Verification** — Where do we read this off, over what window, on which environment?
  Is there a measurement where this would falsely succeed?
- **Scope** — What could someone reasonably assume is included that isn't? One outcome or three?
- **Risk & dependencies** — What must exist first? What breaks if this goes wrong, and
  what is the way back? Security, customer data, production touched?
- **Open questions** — What does nobody here know? Who can find out, by when?

**Bug**, add: exact steps (as a runnable script where possible), expected vs actual,
since when, which environment, how often, who is affected, where the fault likely lives
(a localization hint measurably multiplies agent fix rates). **Spike**, add: what
decision does this unblock, who decides, the options, what would make us pick each,
the timebox.

**Editor's checklist** — before any drafted/generated ticket is published, hunt for:
missing edge cases · cross-team/cross-repo dependencies · rollout and launch risks ·
missing non-goals · stale premises. Surface findings as questions to the human; never
silently fill the gap.

Conversation formats that work: **Three Amigos** (who wants it, who builds it, who
operates it) · **Example Mapping** (25 min; the red unanswerable-question cards ARE the
Open questions section) · **INVEST** as a heuristic earning its keep on one question:
"is this one ticket or three?" — never as a scored gate.

## The teaching pass — human-executed tickets

After the skeleton is filled, one pass for the reader who learns from it (SKILL.md
"Write to teach" has the rule; this is the execution):

1. **`Why it matters` under Problem** — three ingredients: the concrete failure/attack
   story (what goes wrong, for whom), the mechanism (the thing a junior doesn't yet
   know — *why* it goes wrong), and the lesson (what doing this ticket teaches). One
   paragraph; needing three means the mechanism belongs in a doc you link instead.
2. **Links point at the object, not the tool** — the dashboard's own URL/UID, the config
   file path, the ADR. Say in one clause what the reader will see behind each link, and
   note access requirements (VPN, login) so nobody searches for why a link "is broken".
3. **Learn block** — 2–4 external sources max, each with one clause on what it teaches.
   Prefer primary sources; cap total reading ~30 min — a reading list nobody finishes
   teaches nothing.

Per-domain primary sources (pick 2–4, never all):

| Domain | Sources |
| --- | --- |
| Flow & delivery metrics | dora.dev/guides/dora-metrics-four-keys/ · kanbanguides.org · SPACE paper (queue.acm.org/detail.cfm?id=3454124) |
| KPI definition & grooming | the `kpi-groomer` skill carries the full catalog — don't duplicate it here |
| Reliability / SLOs / error budgets | sre.google/sre-book/embracing-risk/ |
| People metrics & measurement ethics | SPACE myths table (same paper) · DevEx (queue.acm.org/detail.cfm?id=3595878) · autoriteitpersoonsgegevens.nl employee-monitoring guidance (NL) |
| Kubernetes & network security | NSA/CISA Kubernetes Hardening Guide v1.2 · docs.cilium.io |
| Admission policy | kyverno.io/policies · Kubernetes Pod Security Standards |

## The templates

English canonical; a board in another language uses its own headings (Dutch mapping:
Probleem · Uitkomst · Acceptatiecriteria · Verificatie · Niet in scope · Open vragen ·
Aanpak · Reproductie · Omgeving · Vraag · Timebox · Waarop we kiezen · Wie beslist ·
Beschermde gebieden · Terugdraaipad — `scripts/ticket_lint.py` reads both). Render per the adapter (markdown on ClickUp,
TipTap HTML on Vikunja — see [adapters/vikunja.md](adapters/vikunja.md)).

### Change / feature — nine out of ten tickets

```markdown
## Problem
What goes wrong today, for whom, what it costs — two sentences, with evidence
(`path/file:12`, metric, support ticket + date). End-user work may open with
"As a <role> I want <x> so that <y>". No solution.

## Outcome
One sentence: the end state. Initiative-sized: also the existing KPI this should
move, or "none — and why". A NEW KPI is a KPI-set change (kpi-groomer), never a
ticket side-effect.

## Acceptance criteria
- [ ] Binary criterion, checkable against real state
- [ ] If <error condition>, then <observable behavior>   (the error path)
- [ ] The criterion that closes the cheap way out

## Verification
Who/what proves it, where, with which concrete case and expected result.

## Not in scope
- What someone would reasonably assume — with where it goes instead

## Context
- Repo / code: · Decision record / runbook: · Dashboard / support ticket:
```

Agent-bound: add `## Approach` (steps + real paths, decisions made), `## Protected
areas` (do-not-touch files/behaviors), and for risk-tiered work `## Rollback` —
[agents.md](agents.md).

### Bug — between Problem and Outcome

```markdown
## Reproduction
1. Step
2. Step → expected X, got Y
(or a runnable script/command — beats prose for humans and agents alike)

## Environment
Where (acceptance/production, which customers), version, since when, how often.

## Impact
Who is affected and how badly.
```

### Spike

```markdown
## Question
The one question. Two questions is two spikes.

## Timebox
E.g. 1 day. Structurally overrunning ⇒ it is not a spike, it is implementation.

## What we decide on
The 3–5 comparison criteria (cost, ops burden, lock-in, offline behavior, …).

## Who decides
Name, at the latest <moment>.

## Acceptance criteria
- [ ] Options tested against the criteria above
- [ ] Decided, and the decision recorded with the trade-off (ADR / doc / comment)
```

**A spike is done when it is decided, not when it is researched** — otherwise the same
investigation repeats in three months. Record architectural outcomes with the
`adr-writer` skill.

### Chore

Version bump, key rotation, node replacement: title + `## Problem`. That's the whole
ticket — that is precisely what makes it a chore.

## Splitting

Split when the ticket carries more than one outcome, doesn't fit the SLE, exceeds ~a
junior-engineer day for agent work, has more than ~7 criteria pulling in different
directions, or wants two theme/area tags — two area tags usually means two tickets.

1. Parent keeps the outcome; children carry the criteria. An epic-typed parent never
   gets acceptance criteria of its own.
2. Each child gets **its own outcome** — "part 1" and "part 2" are not tickets. Where
   the board has a series convention (`<subject> - Part n/m - <sub-outcome>`), follow it.
3. Each child gets **a criterion protecting what already works** — when splitting, the
   cheap way out is always building the child at the expense of the rest of the series.
4. Order as dependency relations (adapter mechanics).
5. Slice vertically (independently valuable), not into horizontal task layers.
   Environment/config prerequisites become their own sequenced tickets — agent tickets
   mentioning unresolved external setup measurably fail more.
6. Re-estimate the parent honestly.

## Triage in a grooming pass — what NOT to groom

Boards carry structure and bookkeeping that only looks like bad tickets: container/hour
tickets (`1. Run`, `2. Change`, `<Customer> - Technical project management`),
milestone-typed date markers, tickets mirroring contract phases. **Skip them — never
rename, never add a skeleton.** When in doubt, skip and report the doubt: a groomed
container is worse than an ungroomed ticket.

More triage heuristics for an ungroomed backlog:

- Where the contract marks a support-intake tag, that set is **the grooming inbox** —
  sweep it first.
- Missing priority means ungroomed planning, not P2.
- **A status the board has but nobody walks is the norm, not an accident** — gate the
  *content*, flag the *flow*; walk tickets through the ladder and say so rather than
  pretending the flow was followed.
- **Rework tickets** (bounced from test/acceptance/review) are a separate lane —
  classification recipe in [playbook.md](playbook.md).

## Bulk refinement (N tickets without flooding one context)

For a whole backlog: themed batches of ~8, or the fan-out (proven on 92 tickets / 11
agents; **60/92 came back flagged** — stale premises, drift, real bugs — that's the
sweep working):

1. **Packets**: theme groups of ~7–10 as JSON files (`packet-<group>.json`).
2. **Shared brief** (`brief.md`): the DoR + template contract, research standard (cite
   `file:line`; stale premises are findings; never invent), output contract — write
   `refined-<group>.json` `[{"n", "body", "flags"}]`, validate it parses, final message
   = one line per ticket, never paste bodies into it.
3. **One agent per packet** (parallel, read-only research).
4. **Central validation** before applying: JSON parses · every ticket covered · format
   matches the adapter (checkbox markup present; no markdown smells in HTML) · cited
   repo paths exist (beware regex false-positives on basename fragments — check context
   before accusing) · spot-read 2–3 drafts for invented claims.
5. **Apply centrally in one session** (sequential writes — parallel sessions stress MCP
   servers; see the adapter's etiquette), swap labels/statuses, report flags grouped:
   stale premises / drift / real bugs / evidence gaps.

Gotcha: a sub-agent that itself spawns children may stall after its children finish
(their notifications bubble to the main loop) — nudge it with a message carrying the
findings summary.
