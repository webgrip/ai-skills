# Case: the anchor experiment, run through this procedure

Giles Edwards-Alexander's experiment ([martinfowler.com, 30 July 2026](https://martinfowler.com/articles/exploring-gen-ai/refactoring-economic-benefit.html)) is the reason this skill exists. This file replays it step by step to show where the procedure adds rigour. The numbers are his; the re-pricing and the counterfactuals are ours and labelled as such.

## What he did, mapped to the procedure

| Step | His experiment | What the procedure adds |
| --- | --- | --- |
| Decide | Hunch that the 17,155-line data-access file was expensive | Expected future changes from history and roadmap; a refactor/wait decision with a safety factor |
| Target | The obviously large file | Hotspot ranking (commits × tokens, agent share), coupling, exclusions |
| Baseline | One fresh-agent run of one invented change, characters ÷ 4 | 1–3 real changes, ≥ 5 interleaved runs each, billed token classes, pass/fail check |
| Plan | Comprehensive plan; Claude.ai planned better than Claude Code; best step missed at first | Plan in a fresh context, value column per step, human approval, cohesion reason per new file |
| Execute | 15 steps; Python/grep/sed scripts tripped over indentation | Tool ladder, characterisation tests, per-step gate, one refactoring per commit |
| Measure | Same change after every step, single runs | Milestone measurement with intervals; meter the refactoring sessions |
| Decide again | "This is just the beginning" | Break-even from measured costs; stop when the interval includes 1.0 or the curve flattens |
| Retain | Article | Plan, ledger, measurements and decision in the repository; enforcement against re-accretion |

## His numbers, re-priced

Input tokens for the change: 159,564 → 27,360 (−83 %); output 1,705 → 2,113. Refactoring cost not measured; upper bound 5M tokens.

He priced the saving at about $0.40 per change ("Sonnet 5, $3 per million"). Sonnet 5 is $2 input and $10 output per million as of October 2026 (the introductory price became the standard one). Re-priced with `scripts/roi.py`:

| Assumption | Saving per change | Break-even (5M tokens) |
| --- | --- | --- |
| All input billed as fresh 5-minute cache writes (his single-pass view) | $0.33 | ~38 changes |
| 75 % of input as cache reads (typical agent loop) | $0.10 | ~57 changes |
| The controlled study's typical 7 % instead of 83 % | $0.01 | ~680 changes |
| Best case plus 1.5 hours of human review at €90/hour | $0.10 | ~1,370 changes |

The direction holds; the size depends on how the tokens bill, on whether 83 % survives repeated runs, and above all on whether a person has to review the steps.

## What the series itself says about noise

His per-step table is not monotonic: 104,080 tokens at step 12, then 131,871 just before step 15, although the largest file only shrank. Step 15 alone carries most of the drop (131,871 → 27,360). Either a real threshold (the agent could finally read one small per-domain file) or run-to-run noise of tens of percent; with one run per step there is no way to tell. With five runs per step and a bootstrap interval, there would be.

## What he got right

- **The mechanism.** Savings come from the agent finding and reading a smaller relevant subset, not from fewer lines (total lines barely moved). The controlled study later measured the same thing in a different way: fewer revisits, gains concentrated across module boundaries.
- **The warning against random cutting**, later measured as token-neutral fragmentation.
- **Naming the catalog refactorings** in the plan, which is what makes agents execute them correctly.
- **Honesty about the gaps**: the unmeasured refactoring cost, one experiment, one greenfield repository.

## What to do differently next time

1. Pull the target and the representative changes from git history, and confirm the roadmap keeps that area hot.
2. Write characterisation tests around the store before step 1.
3. Plan with the whole file visible in a fresh, stronger context, with a value column, so the per-domain split is planned up front, not discovered late.
4. Execute moves with the compiler as completeness oracle instead of sed scripts; commit each step.
5. Measure the baseline and milestones (say after steps 5, 10 and 15) with five runs each, and meter every refactoring session.
6. Compute break-even from measured numbers, including review time.
7. Add a file-size budget and layer rules for `store/` so the next hundred agent changes don't rebuild the 17,000-line file.
