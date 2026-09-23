# Testing and maintaining instruction files

## Contents
- [Test a change](#test-a-change)
- [When to add a line](#when-to-add-a-line)
- [When to remove a line](#when-to-remove-a-line)
- [Ownership](#ownership)
- [Patterns from mature repos](#patterns-from-mature-repos)
- [Linters](#linters)

## Test a change

An instruction file is code with no compiler. Test it by behaviour, not by reading it.

1. Write 4–8 **probe tasks**, each exercising one rule or pointer, on work the model cannot solve
   from prior knowledge. Phrase them as a user would, without naming the rule.
2. Two arms (HEAD and the change), each run in a **fresh detached worktree** because runs edit
   files. Run with `scripts/probe.py`, or by hand:
   `claude -p "$PROMPT" --output-format stream-json --verbose --no-session-persistence --setting-sources project,local --model <pinned> --max-turns 25 --max-budget-usd 1`.
   `--setting-sources project,local` keeps user plugins and rules out; never `--bare`, which skips
   the `CLAUDE.md` under test. `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` gives a no-file arm.
3. Grade deterministically, in this order: regex over tool-call inputs (did it read the doc, run
   the command), a command run afterwards in the worktree (exit 0 = pass), regex over the final
   message. An LLM judge only for short output with concrete PASS/FAIL conditions.
4. Metrics from the final `result` event: `total_cost_usd`, `num_turns`; tokens from
   `modelUsage` (summed), not `usage`, which covers only the last call.
5. Keep a line only if a probe changes with it.

**How many runs** (two-sided α 0.05, power 0.8):

| Shift to detect | Runs per arm |
|---|---|
| 50 % → 100 % | ~8 |
| 30 % → 70 % | ~21 |
| 50 % → 80 % | ~36 |
| 80 % → 90 % | ~196 |

Default to **10 per arm per probe**: it catches the large swing a single rule usually causes.
Three runs prove nothing (0/3 vs 3/3 is p = 0.10). Structural edits (layout, size) do not show at
this scale — the large studies found none — so probe rules, not layout. Cost differences under
~15 % are noise at 10 runs.

`claude plugin eval` runs in an empty workspace with `CLAUDE.md` stripped: right for skills and
plugins, wrong for a repo's own file. For real repos use `scripts/probe.py` or promptfoo's
[claude-agent-sdk provider](https://www.promptfoo.dev/docs/providers/claude-agent-sdk/) with
`setting_sources: ['project']`.

References for the method: Vercel's eval, where a compact docs index in `AGENTS.md` scored 100 %
against 53 % for the same knowledge as a skill that was never invoked in 56 % of runs
([post](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)); ETH's
no-file / generated / human comparison on success, steps and cost
([paper](https://arxiv.org/abs/2602.11988)); Arize's train/test split over real issues
([post](https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/)).

Cheap checks without probes: `/context` shows what loaded and what it costs;
`scripts/measure.py` gives sizes, the CLAUDE.md/AGENTS.md relation, emphasis, dead links and
duplicate skills; an `InstructionsLoaded` hook logs why each file loaded.

**Knowledge the agent must find**: keep a compact index of pointers in the always-loaded file.
A skill alone is not enough for broad knowledge, because skills often never fire.

## When to add a line

Add only when all hold:
- the agent made the mistake **twice**, a review caught it, or you typed the same correction in
  two sessions;
- it cannot be derived from the code, and no linter, hook, test or CI job can enforce it (if one
  can, build that instead);
- it is not already in a doc (if it is, add a pointer with its trigger, not a copy).

Write it as the rule plus its reason, scoped explicitly ("in `app/Domains/*/Pdf`"), in the file
that owns that scope.

An agent may **propose** a line (a Stop hook can read `transcript_path` and draft one), but a
human reviews it before it is committed: self-generated skills scored below no skill at all in
SkillsBench, and automatic memory rarely beat none ([evidence.md](evidence.md)).

## When to remove a line

Files accrete: in 2,303 studied files a Claude Code commit added a median 57 words and deleted under 15
([arXiv 2511.12884](https://arxiv.org/abs/2511.12884)). Pruning has to be a scheduled act.

Remove or move a line when:
- the model does it right without the line (test it);
- a tool now enforces it;
- the command, path or file it names is gone;
- it applies to one subtree or task (→ path-scoped rule, nested file, or skill);
- it was written against an older model's weakness, especially emphatic wording;
- it restates a doc (→ pointer).

`/doctor` in Claude Code proposes cuts for content derivable from the codebase. Revisit the file
after every major model release: workarounds for an older model become overhead
([Anthropic](https://code.claude.com/docs/en/large-codebases)).

## Ownership

- The team file lives in git and changes through review, like code. Personal preferences go to
  `~/.claude/CLAUDE.md`, an ancestor-directory file, or `CLAUDE.local.md` (which disables native
  `AGENTS.md` loading in Claude Code, so `CLAUDE.md` must import it).
- Rules shared by several repos live one level up (a package, a plugin, a template) and are
  removed from each repo, so each rule has one owner.
- A CI job keeps generated output equal to the generator and the hand-written part within budget
  ([generators.md](generators.md#ci-drift-check)).

## Patterns from mature repos

Seen in `openai/codex`, `vercel/next.js`, `astral-sh/uv` and `ruff`, `oven-sh/bun`,
`microsoft/vscode`, `pydantic/pydantic-ai`:
- commands and verification first;
- one canonical file, the other reached by symlink or `@AGENTS.md` (ruff);
- situational depth behind explicit triggers: "read `.claude/docs/landing-prs.md` when landing a
  PR" (bun), skills for deep workflows with baseline policy kept in the file (next.js);
- a pointer instead of a copy: uv's `AGENTS.md` starts with "Read CONTRIBUTING.md";
- an error log section ("Learnings", "Common mistakes") that needs pruning like the rest.

Large repos often run far past 200 lines and use emphatic words heavily; that is common, not
shown to work. Persona lines ("You are an experienced developer") and generic mandates copied from
system prompts cost tokens and say nothing the model lacks.

GitHub's observation over 2,500 Copilot custom-agent files (`.github/agents/*.md`, not
`AGENTS.md`): most fail by vagueness; name commands with flags, versions, and boundaries as
Always / Ask first / Never. Its advice to give the agent a persona does not carry over to
instruction files
([post](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)).

## Linters

Small tools, unproven, useful as a start for CI: [ctxlint](https://github.com/YawLabs/ctxlint)
(paths, commands, staleness, budget), [agents-lint](https://github.com/giacomo/agents-lint),
[agents-md-check](https://github.com/duke5am/agents-md-check). GitHub Next's curator bot estimated
stale paths, broken links and duplication at about 12.7 % of tokens in one repo
([issue](https://github.com/githubnext/gh-aw-cao/issues/12620)).
