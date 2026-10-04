# refactoring-economics

Refactor agent-maintained code where it measurably lowers what coding agents spend on future changes, and prove it.

Giles Edwards-Alexander's [experiment on martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/refactoring-economic-benefit.html) (30 July 2026) cut the input tokens an agent spent on one change by 83 % after fifteen Fowler-catalog refactorings. It measured one run per step with a characters ÷ 4 estimate and left the refactoring's own cost unmeasured. This skill turns the idea into a repeatable procedure and fixes those gaps:

- **Decide first.** Classic refactoring economics (Beck's tidy-first inequality and first/after/later/never, Fowler on hot versus stable cruft), plus a break-even model priced per token class (cache reads, 5-minute and 1-hour cache writes, output at 5×), with human review in the cost and a safety factor for run-to-run noise.
- **Target by history.** `scripts/hotspots.py` ranks files by commits × estimated tokens from `git log`. It reports the share of commits made with an agent and code-maat-style change coupling, and leaves out release-bot commits, lockfiles and generated files.
- **Measure honestly.** `scripts/measure.py` runs the same representative change on several git refs, at least five interleaved times each.
  - Every trial gets a fresh headless agent in a throwaway worktree, with a pinned environment and an acceptance check.
  - It reads the agent's own usage stream: the last `result` event, `modelUsage` including subagents, and the per-step cache-write split.
  - It recomputes cost from a dated price file, because the CLI's bundled table can be stale.
  - The report gives medians, a bootstrap interval on the ratio, pass rate, cost per passing change and break-even.
  - It supports Claude Code and Codex, plus any CLI through a command template.
- **Refactor what shrinks the read set.** Fowler-catalog moves in an evidence-based order: tests, dead code, duplication, grep-able names, extract classes, move into cohesive domain-named modules, co-locate tests, then split. Every new file needs a cohesion reason, and splitting by line count is forbidden.
- **Execute safely.** A tool ladder: semantic engines, then AST codemods, then ast-grep, never sed. Characterisation tests come first. Each step passes a gate (compile, tests, zero stale references, moves shown as moves) and is one refactoring per commit. Moves land quickly to avoid merge conflicts.
- **Be honest about size.** The only controlled study (Sonar, 660 Claude Code trials) found about 7 % fewer input tokens and 34 % fewer file revisits on cleaner code, concentrated in multi-module work. Token savings alone rarely pay for human review, so the skill counts the benefits beyond tokens and targets real hotspots.

## Install

```text
/plugin install refactoring-economics@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s refactoring-economics`.

## Example prompts

- "Our agents keep re-reading src/data/store.rs. Is it worth refactoring for token cost?"
- "Measure what adding a new store trait costs Claude Code before and after this refactoring branch."
- "Which files in this repo should we refactor so agents spend less?"
- "Reproduce the Fowler refactoring-economics experiment on our Laravel app."

## Scripts

```bash
python3 skills/refactoring-economics/scripts/hotspots.py --agent-pattern "Co-Authored-By: Claude" --coupling .
python3 skills/refactoring-economics/scripts/measure.py run --repo . --refs main,refactor/step-5 \
    --prompt bench/change.md --check "make test" --repeats 5 --out token-runs/
python3 skills/refactoring-economics/scripts/measure.py report token-runs/ --refactor-cost-usd 7.40 --changes-per-month 20
python3 skills/refactoring-economics/scripts/roi.py --model claude-sonnet-5-5 --baseline-input 150000 \
    --baseline-output 1700 --refactor-input 4000000 --changes-per-month 20
```

All Python standard library. `measure.py run` spends real money: one agent run per trial. `test.sh` exercises every script against sanitised real Claude Code captures, a synthetic git history and a fake agent, with no paid calls.

## Sources

Each reference file links its sources. Among them:

- **The anchor:** Edwards-Alexander 2026 and its Hacker News discussion.
- **Agent cost and code structure:** Trivedi & Schmitt (Sonar) 2026, Bai et al. 2026, Weinberger & Hozez 2026, SWE-Pruner, Borg et al. 2026, GitClear 2025/2026, SlopCodeBench.
- **Agents refactoring:** Liu et al. 2024, CodeTaste, SWE-Refactor, RefactorBench, SWE-Bench ProMax, JetBrains' Rider refactoring skill.
- **Merge effort:** Oliveira et al. 2026.
- **Refactoring practice:** Fowler's *Refactoring* catalog, Beck's *Tidy First?*, Tornhill's hotspots and code-maat.
- **Pricing:** Anthropic's pricing page, fetched 4 October 2026.
