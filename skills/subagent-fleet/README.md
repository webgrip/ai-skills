# subagent-fleet

Run several coding agents at once on shared repositories without losing work or trust. The
orchestrator owns isolation, the brief, review and every push; agents edit, test and commit
locally.

- **Isolate:** one worktree and one test database per writing agent; what `isolation: "worktree"`
  really starts from (the remote default branch, unless `worktree.baseRef` is `"head"`); why a
  fresh worktree is not gate-ready; generated churn from a full setup; a lightweight worktree for
  docs-only work.
- **Brief:** scope with exact exceptions, the shared checkout as read-only, local commits only,
  merge never rebase on someone else's branch, stop when a hook blocks, gates in the foreground to
  a log, a done-command and a report contract. Copyable templates for code-changing agents,
  branch-merging agents, read-only reviewers, research agents and resume prompts.
- **Steer and recover:** `SendMessage` to running and finished agents, interim notices, hand-backs
  that carry no user authority, one resume for a stalled agent and then take over.
- **Background tasks:** commands moved to the background at their timeout, exit 144 (killed),
  output saved to files, port-forwards, pattern kills, time limits in unattended runs.
- **Land:** diff size per commit, scope creep parked on a proposal branch, an exact-path replay
  for shared checkouts, fast-forward pushes, a second agent driving the reference client.
- **Recipes:** port and validate from exact revisions, update colleagues' branches by merging,
  rescue orphaned work as a branch and pull request.

Ships two read-only stdlib scripts:

- `scripts/fleet_inventory.py` — per repository, the worktrees, branches, shared stash and
  processes agents left behind (dirty, mid-operation, unpushed, locked, merged, gone), with a
  prune plan that prints commands and never runs them.
- `scripts/transcript_calls.py` — the tool calls in Claude Code transcripts across every
  project, session and subagent, filtered by time window (or a file's birth time), tool and
  pattern; `--handbacks` lists subagent reports.

`test.sh` builds a clean and a careless git fixture (every inventory rule fires on one, none on
the other) and runs the transcript search against synthetic transcripts.

**Install:**

```text
/plugin install subagent-fleet@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s subagent-fleet`.

**Try:** "spin up three agents to fix the review threads on these MRs", "my subagent says stream
watchdog did not recover", "why can't my isolation worktree agents see my local commit?", "a
background task failed with exit 144", "which session replaced this file?", "clean up the
worktree-agent branches in this repo".
