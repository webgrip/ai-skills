# Testing and maintaining instruction files

## Contents
- [Test a change](#test-a-change)
- [Measure what a session loads](#measure-what-a-session-loads)
- [Replay evals for a whole setup](#replay-evals-for-a-whole-setup)
- [When to add a line](#when-to-add-a-line)
- [Agent-proposed rules](#agent-proposed-rules)
- [When to remove a line](#when-to-remove-a-line)
- [Moving knowledge out of the file](#moving-knowledge-out-of-the-file)
- [Ownership](#ownership)
- [Patterns from mature repos](#patterns-from-mature-repos)
- [Linters](#linters)

## Test a change

An instruction file is code with no compiler. Test it by behaviour, not by reading it.

1. Write 4–8 **probe tasks**, each exercising one rule or pointer, on work the model cannot solve
   from prior knowledge. Phrase them as a user would, without naming the rule.
2. Two arms (HEAD and the change), each run in a **fresh detached worktree** because runs edit
   files. Run with `scripts/probe.py`, or by hand:
   `claude -p "$PROMPT" --output-format stream-json --verbose --no-session-persistence --setting-sources project,local --model <pinned> --max-turns 25 --max-budget-usd 1 < /dev/null`.
   `--setting-sources project,local` keeps user plugins and rules out; never `--bare`, which skips
   the `CLAUDE.md` under test. `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` gives a no-file arm. The probes
   run the `claude` on PATH, which may not be the version your users run
   ([claude-code.md](claude-code.md#which-binary-runs)).
3. Grade deterministically, in this order: regex over tool-call inputs (did it read the doc, run
   the command), a command run afterwards in the worktree (exit 0 = pass), regex over the final
   message. An LLM judge only for short output with concrete PASS/FAIL conditions.
4. Metrics from the final `result` event: `total_cost_usd`, `num_turns`; tokens from
   `modelUsage` (summed), not `usage`, which covers only the last call. Parse stream-json: plain
   `--output-format json` changes shape with the settings loaded (an array with user settings, a
   single object under `--setting-sources project`).
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

**Knowledge the agent must find**: keep a compact index of pointers in the always-loaded file.
A skill alone is not enough for broad knowledge, because skills often never fire.

## Measure what a session loads

- `claude -p "/context"` lists the real load per category: system prompt, system tools, MCP tools
  (loaded and deferred), memory files one by one, and skills. Skills and MCP servers from
  `~/.claude` and plugins often outweigh the repo's own file; measure the whole session before
  trimming the repo file.
- Budget checks on instruction files (`measure.py`, the drift check) count `AGENTS.md`,
  `CLAUDE.md` and pathless rules, not skill descriptions or MCP definitions.
- Cheaper checks: `scripts/measure.py` for sizes, the CLAUDE.md/AGENTS.md relation, emphasis, dead
  links and duplicate skills; an `InstructionsLoaded` hook for why each file loaded.

## Replay evals for a whole setup

For a change to the whole setup (a new layout, a skill set, a model switch) rather than one rule:

- Take 15–30 merged changes and run each from its parent commit with the future sealed (later
  refs, reflog, network).
- Use the original ticket text as the prompt.
- Score with hidden tests, static analysis, lint, architecture tests and diff scope; run mutation
  testing on tests the agent wrote.
- Repeat each 3–5 times and report **cost per passing task**.
- Harnesses: Harbor, Inspect AI with inspect_swe, promptfoo (above), skill-creator's benchmark mode.

## When to add a line

Add only when all hold:
- the agent made the mistake **twice**, a review caught it, or you typed the same correction in
  two sessions;
- it cannot be derived from the code, and no linter, hook, test or CI job can enforce it (if one
  can, build that instead);
- it is not already in a doc (if it is, add a pointer with its trigger, not a copy).

Write it as the rule plus its reason, scoped explicitly ("in `src/Billing/**`"), in the file that
owns that scope.

Before writing, keeping or migrating a rule, count what the code does and find where the rule came
from. A naming rule that half the files break, or an "always do X" that most of the codebase never
does, is worse than no rule: agents follow it into new inconsistency, and review bots trained on
the code contradict it. Count with `git ls-files` plus `grep -c`, find the origin with
`git log -S '<rule text>'`, carry or add the reason, and then fix either the rule or the code.

## Agent-proposed rules

An agent may **propose** a line; a human reviews it before it is committed. Self-generated skills
underperformed curated ones in SkillsBench, automatic memory rarely beat none, and agents follow a
stale or conflicting memory anyway ([evidence.md](evidence.md)).

A mining pass that holds up:

- **Sources**: a convention sweep of the code (Boost's `infer-conventions`,
  [generators.md](generators.md#project-rules-airules)), human review comments on merged changes,
  and a review bot's learnings. A Stop hook can also read `transcript_path` and draft a line.
- **Bar per source**: from comments and learnings, it went wrong twice or a reviewer caught it;
  from the code sweep, the next agent would plausibly write it differently.
- **Evidence with every candidate**: links to the changes or comments and the follow-versus-deviate
  counts. A single occurrence is asked as a question, not proposed as a rule.
- **Cheapest home first**: visible to a parser → a test or ast-grep rule
  ([enforcement.md](enforcement.md#checks-over-prose)); judgement tied to paths → a path rule;
  product behaviour → `docs/`; already covered → nothing.
- **Delivery**: a branch and a merge request. The agent drafts; it never decides.

How tools treat agent-written rules and memory (most write without per-item approval):

| Tool | Behaviour |
|---|---|
| Claude Code | `/init` writes once; `CLAUDE_CODE_NEW_INIT=1` proposes first; auto memory writes without approval |
| Cursor | Memories and `/Generate Cursor Rules` removed; rules are versioned files |
| Windsurf Cascade | writes memories without approval; docs steer to versioned rules |
| Devin | per-item suggestions the user approves |
| Kiro | generates steering docs in one shot |
| Copilot coding agent | offers instruction changes as a pull request |
| CodeRabbit learnings | apply at once by default (`approval_delay: 0`); with a delay, chat-sourced learnings are approved at the deadline unless rejected |

Prefer settings that propose items for review and keep them versioned; an approval delay is a
review window, not a gate.

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

Trim by eval, not by taste: Laravel Boost slimmed its always-loaded guidelines by removing only
lines whose removal changed no eval outcome, kept the ones whose removal regressed (named routes,
`artisan list`, the docs-search examples), and moved a tool's usage text into that tool's MCP
description, where it is read only when the tool is in play
([laravel/boost#1042](https://github.com/laravel/boost/pull/1042)).

`/doctor` in Claude Code proposes cuts for content derivable from the codebase. Revisit the file
after every major model release: workarounds for an older model become overhead
([Anthropic](https://code.claude.com/docs/en/large-codebases)).

## Moving knowledge out of the file

Moving content from an instruction file into `docs/` breaks branches that still write to the old
place.

- **Keep the migration branch in sync**: merge the base in, resolve the instruction files to the
  branch side, list the bullets the base added since the merge base
  (`git diff "$(git merge-base HEAD origin/<base>)" origin/<base> -- AGENTS.md | grep '^[-+]- '`),
  route each to the doc that owns its subject, and fix statements the base made stale.
- **After it merges**, for each open change that conflicts: take the base's instruction files
  whole, move the change's lines into the owning doc, and grep each bullet's key terms before
  dropping it.
- **Prove nothing was lost**: grep each old bullet's backticked identifiers (4+ characters) across
  `docs/`, rules, skills and `AGENTS.md`; read every bullet with low coverage.
- **Audit the open changes** after any repo-wide structural change: fetch each head into a detached
  scratch worktree, trial-merge it into its target and record conflicts, test pairs with
  `git merge-tree --write-tree --name-only --merge-base=<base> <a> <b>`, find commits already in
  the base with `git cherry`, then delete the trial refs. Report by category with links, a merge
  order and an explicit "not verified" line; scripted scans are triage, never findings.
- Schedule a whole-file rewrite (translation, restructure) after the open branches touching that
  file have merged.
- Across several repos, run the audit steps in [SKILL.md](../SKILL.md) per repo, each from a
  fresh worktree with its own install, and keep a learnings log (what was
  seen, where, what it changes). Strike a wrong entry through instead of deleting it.

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
