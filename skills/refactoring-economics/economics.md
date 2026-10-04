# Economics: when a refactoring pays

Contents: decision rules · prices and token classes · the return-on-investment model · worked example · benefits beyond tokens · when not to refactor

## Decision rules

These come from classic refactoring economics and still hold when the reader is an agent.

1. **Refactor only when expected future savings exceed today's cost.** Kent Beck's test: tidy first when `cost(tidying) + cost(change after tidying) < cost(change without tidying)`, and accept a slightly worse trade now when the same area will change again ([Options versus Cash Flows](https://newsletter.kentbeck.com/p/options-versus-cash-flows)).
2. **Timing** (Beck, *Tidy First?*, ch. 21): **first** when the current change gets cheaper; **after** when the same area changes again soon; **later** goes on a list; **never** when the code won't be touched again.
3. **Zero tolerance in hot areas, leave stable cruft alone** ([Fowler, Technical Debt](https://martinfowler.com/bliki/TechnicalDebt.html)). Payback scales with how often the code changes, so the target comes from change history ([targeting.md](targeting.md)).
4. **Coupling drives cost** (Constantine's equivalence, via Beck): prefer refactorings that shrink what must be read and changed together.
5. **Default to preparatory refactoring** ("make the change easy, then make the easy change") when there is no forecast; then the inequality in rule 1 can be checked inside the same session ([Fowler, Workflows of Refactoring](https://martinfowler.com/articles/workflowsOfRefactoring/)). Big planned sweeps are the exception, for the worst hotspots.

## Prices and token classes

An agent's bill has five token classes. Current Anthropic list prices are in `scripts/prices.json` (source and fetch date inside; re-check before quoting).

| Class | Multiplier of base input | What it is |
| --- | --- | --- |
| Uncached input | 1× | New tokens not written to cache |
| Cache write, 5 minutes | 1.25× | Most fresh input in an agent loop (API key default) |
| Cache write, 1 hour | 2× | Subscription default for the main conversation |
| Cache read | 0.1× (0.05× Opus 5.5, 0.025× Fable 5.1) | Every later turn re-reads the transcript from cache |
| Output | 5× on every current Anthropic model | What the agent writes |

Consequences:

- **A token read early costs more than its face value.** It is written once and re-read from cache on every later turn: `m_eff ≈ 1.25 + r × (turns remaining)`. A file read early in a 20-turn Sonnet session costs about 1.25 + 0.1 × 19 ≈ 3.15× its face value ([Bai et al.](https://arxiv.org/abs/2604.22750): cache reads dominate dollar cost). Measured `processed_input` already includes these re-reads; a static count of the files an agent needs does not.
- **Fewer tokens is not automatically fewer dollars.** A change that adds turns re-sends the fixed prefix (system prompt, tools, CLAUDE.md: 12–24k tokens in Claude Code) each time. Report cost per passing change, not just tokens.
- **Billing mode changes the same run's cost.** Subscription sessions write 1-hour cache entries at 2×; API keys write 5-minute entries at 1.25×. Pin it during measurement (`measure.py` sets both TTLs to 5 minutes).
- **The CLI's own cost figure can be stale.** Claude Code 2.1.208 still priced Sonnet 5 at $3/$15 after the price stayed at $2/$10; `measure.py` recomputes from tokens with the dated price file and reports both.
- **Tokenizers differ.** Claude 4.7 and later produce about 30 % more tokens than earlier models for the same text, so characters ÷ 4 is a rough proxy at best.

## The return-on-investment model

Per future change touching the refactored area:

```text
S = Δcost_tokens            measured: median cost per passing change, before minus after
  + Δp_fail × C_attempt     fewer failed or redone attempts
  + Δt_human × rate         less steering and review per change
```

One-off cost of the refactoring:

```text
C = C_tokens                 metered refactoring sessions (the article's missing number)
  + t_review × rate          human review of the refactoring commits
  + p_regress × C_incident   expected cost of a regression
  + C_merge                  rebase and conflict cost for parallel work
```

Expected future changes over the horizon H (usually 12 months):

```text
F = commits to the area in the last 12 months × agent share × trend
```

Decision: break-even `F* = C / S`. **Refactor when F ≥ k × F\***, with a safety factor k ≈ 2–3, because one representative change measured a few times is a noisy estimate of every future change, and hotspots cool over time. `scripts/roi.py` computes this with `--safety-factor` (default 2.5); `measure.py report --refactor-cost-usd` does it from measured runs.

Without measurements, model scenarios from the published range: 7 % (the controlled study's median), 25 %, and 83 % (the anchor's single-run best case). If the decision flips between scenarios, measure before refactoring.

## Worked example

The anchor's numbers on Claude Sonnet 5 ($2 input, $10 output per MTok, 75 % of input as cache reads, 20 agent changes a month to the area, 5M tokens to refactor):

| Scenario | Saving per change | Break-even changes | Payback | Verdict at k = 2.5 |
| --- | --- | --- | --- | --- |
| 7 % input saving | $0.009 | ~680 | ~34 months | wait |
| 25 % input saving | $0.031 | ~190 | ~9.5 months | wait |
| 83 % input saving | $0.103 | ~57 | ~2.9 months | refactor |

Add 1.5 hours of human review at €90/hour and even the best case needs well over a thousand changes (about 1,370) on token savings alone. **Token savings alone rarely pay for human review time.** The case for refactoring rests on one or more of:

- a genuine hotspot that agents change hundreds of times a year;
- cheap, mechanical, tool-verified refactorings that need little review;
- the benefits beyond tokens below.

## Benefits beyond tokens

Count them explicitly; they usually dominate.

| Benefit | Evidence | Measure |
| --- | --- | --- |
| Fewer file revisits and more predictable runs | Strong ([Sonar](https://arxiv.org/abs/2605.20049): revisits −34 %) | Files read and spread across runs, from `measure.py` |
| Lower failure and break rate for mid-size models | Strong for mid-size, null for frontier Claude Code ([Borg et al.](https://arxiv.org/abs/2601.02200)) | Pass rate per variant |
| Faster turns | Expected, unquantified | Wall time per run |
| Less context rot on long sessions | Strong in general ([Chroma](https://www.trychroma.com/research/context-rot)) | Session length before quality drops |
| Code people can still review and own | Strong for humans ([Code Red, arXiv 2203.04374](https://arxiv.org/abs/2203.04374)) | Review time, a reviewer can explain the module |
| Rate-limit headroom on subscriptions | Direct: fewer tokens per change | Changes per usage window |

Pair every token metric with guard metrics (pass rate, files touched, review burden, revert rate). When a measure becomes the target it stops measuring: over-splitting, deleting tests or hiding needed context can lower tokens on the benchmark while other changes get worse.

## When not to refactor

1. The code is about to be deleted or replaced (Beck's "never").
2. Cold code: rarely changed, even if ugly. Crufty but stable areas can be left alone.
3. Stable code the agent rarely opens.
4. No safety net: add characterisation tests first, or don't refactor ([execution.md](execution.md#safety-nets)).
5. Parallel branches or agents are editing the same hotspot: move refactorings raise merge-effort likelihood by over 400 % ([arXiv 2608.15384](https://arxiv.org/html/2608.15384)).
6. Generated, vendored or data files: regenerate or exclude them.
7. `F < k × F*` after pricing human review.
8. A rabbit hole: more than about an hour of tidying without a behaviour change means the minimum structural change has been lost (Beck). Stop and re-scope.
