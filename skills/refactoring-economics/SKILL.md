---
name: refactoring-economics
description: Refactors and splits agent-maintained code so coding agents spend fewer tokens on future changes, and proves it - git-hotspot targeting with agent share, a repeated-run harness that measures the same change before and after from the agent's own usage stream, Fowler-catalog refactorings ordered by what shrinks the agent's read set, tool-driven execution with a per-step gate, and a break-even model per token class. Use when agents burn tokens or keep re-reading a large file; when asked to split a big file or class so agents spend less; whether refactoring will cut agent token cost or pay for itself; to measure what a change costs an agent before and after a refactoring; which files or modules to refactor first so AI agents spend fewer tokens; to reproduce the martinfowler.com refactoring-economic-benefit experiment; or to plan refactoring an AI-built codebase. Not for behaviour changes or general code review.
---

# Refactoring economics

Spend tokens now on refactoring only where it lowers what future agent changes cost, and prove it with measurement. The mechanism is real: an agent that can find and read a smaller relevant part of the code spends less. The size is not what the headline suggests. One experiment cut input tokens 83 % for one change; the only controlled study found about 7 % on average, with gains concentrated across module boundaries and per-task swings from −47 % to +44 %. → [evidence.md](evidence.md)

## Procedure

1. **Decide whether to look at all.** The code must be changed by agents often, now and on the roadmap. Skip it if the code is cold, about to be deleted, generated, has no tests and none can be added, or has parallel branches editing it. Default to *preparatory* refactoring (just before a change that needs it) when there is no forecast. → [economics.md](economics.md#decision-rules)
2. **Target by change history.**
   - Run `python3 scripts/hotspots.py --agent-pattern "Co-Authored-By: Claude" --coupling REPO`.
   - Exclude data and generated files.
   - Cross-check the roadmap.
   - Write the **target card**: file, commits and agent share, coupling, expected future changes, 1–3 representative changes taken from real commits, and an acceptance check.

   → [targeting.md](targeting.md)
3. **Measure the baseline.** Get the budget approved first: runs × variants × one run's cost. Then run `python3 scripts/measure.py run --refs baseline --prompt CHANGE.md --check "TESTS" --repeats 5`. Every run is a fresh agent in a fresh worktree; the token classes come from the agent's own usage stream, priced from `scripts/prices.json`. Check which files the runs read and re-read. → [measurement.md](measurement.md)
4. **Estimate before refactoring.**
   - Run `python3 scripts/roi.py` with the baseline. Without a measured after-state it models the published range (7 %, 25 %, 83 %) against expected changes per month and the refactoring's cost, human review included.
   - If even the optimistic scenario says *wait*, stop and report that.
   - If the verdict flips between scenarios, continue with milestone measurement.

   → [economics.md](economics.md#the-return-on-investment-model)
5. **Plan in a fresh context.**
   - Plan with the whole target visible, a stronger model if available, and a human approving.
   - Each row has: a Fowler catalog name, the target, a **cohesion reason** (what changes together here), the tool, the verify command, and the expected value.
   - Order: tests, dead code, duplication, names, extract classes, move into cohesive domain-named modules, co-locate tests, then split what is still large.
   - Never split by line count.

   → [refactorings.md](refactorings.md)
6. **Execute one refactoring per commit.**
   - Characterisation tests come first, in their own commit, green on the old code.
   - Prefer a semantic engine or AST tool over text edits, and never use sed or regex on multi-line code.
   - Each step passes the gate: compile clean, targeted tests pass, zero stale references, the diff shows moves as moves, no behaviour change.
   - Commit with `refactor(scope): <Refactoring> <symbol>`.
   - Keep a ledger of moves and renames.
   - Meter the refactoring sessions.

   → [execution.md](execution.md)
7. **Measure milestones and decide again.**
   - Re-run the same changes on milestone refs, interleaved, then run `measure.py report --refactor-cost-usd X --changes-per-month N`.
   - Continue while the interval on the input ratio excludes 1.0 and break-even stays within the safety factor of expected changes.
   - Stop when the curve flattens, files read rises without tokens falling (fragmentation), or pass rate drops.
8. **Lock it in.** Add a file-size or function-length budget, layer and dependency rules, and duplicate detection for the refactored area. Add a short entry-point map in AGENTS.md or CLAUDE.md, not an overview (the agent-instructions skill covers how). Re-run the representative changes every few months. → [refactorings.md](refactorings.md#lock-it-in)
9. **Report and retain.** Keep the target card, plan, ledger, run directory, report and the decision next to the code. Give medians with intervals and the pass rate. State the refactoring cost and break-even, the benefits beyond tokens, and what was not measured. A refactoring plan does not authorise merging; follow the repository's process.

## Gotchas

- **Token savings alone rarely pay for human review.** At 7 % a 5M-token refactoring needs hundreds of changes to break even; add 1.5 hours of review and even the 83 % case needs over a thousand. Count the benefits beyond tokens (fewer revisits, predictability, speed, code people can review) and target real hotspots. → [case-article.md](case-article.md)
- **One run proves nothing.** Same task, same code varies ~2.5× typically and up to 30×. Compare medians of at least five interleaved runs with an interval.
- **Tokens are not dollars.** Cache reads dominate agent bills; output is 5× input; a token read early is re-read every turn. Recompute cost per token class from a dated price file. The CLI's own `total_cost_usd` was stale for Sonnet 5 in 2.1.208.
- **Take the last `result` event and `modelUsage`.** Background subagents emit two results; `result.usage` excludes subagents; per-step output tokens are placeholders.
- **Smaller files are not the goal.** Extraction inside one hotspot was token-neutral and raised files read. Move what changes together into cohesive, grep-findable, domain-named modules.
- **Agents can't pick refactorings.** Unguided they rename and annotate. Name the catalog refactoring, narrow the region, plan with a stronger model, and have a human approve.
- **Move refactorings collide.** They raise the likelihood of merge effort by over 400 %. Land them as a quick batch with no parallel work on the area, and rebase other branches straight after.
- **Structure erodes again** under agent edits, and prompts don't stop it. Without enforcement the saving decays.

## Example

[case-article.md](case-article.md) replays the anchor experiment through this procedure. It covers what it got right, the noise in its single-run series, its numbers re-priced at current rates with and without caching and review, and what to do differently.
