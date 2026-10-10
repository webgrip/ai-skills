# Brief templates

Contents: [Code-changing agent](#code-changing-agent) ·
[Agent that merges trunk into someone else's branch](#agent-that-merges-trunk-into-someone-elses-branch) ·
[Read-only reviewer](#read-only-reviewer) · [Research agent](#research-agent) ·
[Resume prompts](#resume-prompts)

Fill every angle-bracket slot; a slot left vague is where the agent improvises. Each clause is
explained in the SKILL.md section [Brief every agent](../SKILL.md#brief-every-agent).

## Code-changing agent

```text
Goal: <one sentence>. Vocabulary: <term = meaning, ...>.
You own exactly these files: <list>. Other agents are editing other files in parallel; touch nothing else.
Keep byte-identical: <exceptions>. Rewrite rules, with examples: <before> -> <after>.

Setup
1. Work only in <absolute worktree path>. The checkout at <main checkout path> is shared and read-only:
   never run git checkout, switch, stash, reset, clean or restore there.
2. Read AGENTS.md (or CLAUDE.md), <docs for the area>, and every rule whose paths match a file you change.
3. Before the first gate: <git submodule update --init; tool trust; dependency install; own test database>.

Git
- Stage explicit paths only; never git add -A, -u or commit -a.
- COMMIT LOCALLY ONLY. Never push, force-push, comment, approve or merge: the orchestrator reviews your diff first.
- <If the branch belongs to someone else:> bring <base> in with git merge origin/<base>, never a rebase.
- Commit format: <conventional commits, required trailers, ticket trailer>. Extras go in separate commits; report them.
- Let hooks run; never --no-verify. If a hook or a permission check blocks you, stop and report it.
  Never make the same change through another tool.
- Never write to any ~/.claude memory directory.

Gate
Run <formatter, static analysis, lint, tests for the touched areas>, one test process at a time, in the
foreground, output to a log file: <cmd> > "$LOG" 2>&1; echo "exit $?"; tail -n 40 "$LOG".
Never pipe a gate through grep or tail. If a failure looks unrelated, run it alone before believing it.
Done when <done-command> prints nothing.

Report
Your final message is read by the orchestrating agent. Give: the worktree path; each commit SHA and
subject; what you changed as file:line; gate commands with pass counts; how you resolved each conflict
and why; what you left out on purpose and why; anything you are unsure of; a 1-3 sentence draft reply
per review thread. Do not push.
```

## Agent that merges trunk into someone else's branch

Use for a branch far behind trunk with many conflicts, after a trial merge showed which files
conflict ([git-recipes.md](git-recipes.md#update-colleagues-branches-by-merging)).

```text
Merge origin/<trunk> into <branch> (owner: <name>) in <absolute worktree path>. Keep the merge local
until it is reviewed. Resolve conflicts by these rules:
- <trunk> is the truth for everything the branch did not mean to change.
- Port <trunk>'s additions into the branch's new mechanism instead of dropping them.
- Generated files take <trunk>'s version and are regenerated with <command>.
- Instruction and config files take the union, in <trunk>'s wording.
- Renumber records whose numbers collide (ADRs, RFCs, migrations), and every reference the branch wrote to them.
- <old name> may not come back.
Report each conflict with the rule you applied, and every file the merge brought back that <trunk> had deleted.
```

## Read-only reviewer

```text
Review <PR, branch or diff> for <focus>. Read-only: do not comment, approve, merge, close, push or edit
anything, and write files only under <scratch directory>. Never print token or secret values. If an API
call needs credentials you do not have, use the web pages or the .diff/.patch URLs and say what you
could not see. Report each finding as file:line, severity, the evidence, and a suggested fix.
```

## Research agent

```text
Today is <date>. Context: <stack, constraints, what is confidential>. Question: <one question>.
For every claim give the URL and an evidence grade: verified in source or docs, inferred, or weak.
Mark anything you did not check UNCONFIRMED. Write findings to <file> as you go. Rank your
recommendations and name what to avoid. Change no repository files.
```

## Resume prompts

A stalled agent, resumed once with what you found on disk:

```text
You stalled. On disk now: commits <sha subject, ...> on <branch>; uncommitted: <files>; no test process
is running. Continue from <step>. Run gates in the foreground with output to a log file.
Everything else in your brief stands.
```

A fan-out whose children were cut off (`STATUS: PARTIAL`, a NOT DELIVERED list):

```text
Your sub-agents were cut off before they reported. Finish the NOT DELIVERED items yourself, without
spawning sub-agents, and write each finding to <file> as you go.
```

A mid-flight decision, sent with `SendMessage` to the agent that owns the files:

```text
Decision from the user: <decision>. Apply it to <files>. Everything else in your brief stands.
```
