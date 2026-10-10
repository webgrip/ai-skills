# org-boundaries

Keep each organisation's knowledge and identity out of the others' repos when one person works
for several on one machine: an own company, an employer, clients. The rule (remove the
organisation, keep the person, leave functional references byte for byte), the tell-tale
references a name grep misses, a scan of every surface before publishing and after cleaning,
rewrite rules for neutral prose, a local guard against leaks that come back with new work,
per-directory git identity for agent scratch clones, the user-level agent config (MCP servers,
plugin hooks, telemetry, rules) that crosses organisations, and when and how to rewrite published
history.

Ships:

- `scripts/scan_boundary.py`: stdlib scanner that reads one regex per line from a patterns file
  kept outside the repo (`~/.config/org-boundaries/ORG.txt`) and reports matches in tracked file
  content, paths, commit author and committer names and emails, commit and tag messages, and
  branch and tag names; `--all-refs` and `--untracked` widen it, `--range` and `--since-commit`
  narrow history, `--staged` and `--message-file` serve the hooks. Exit 1 on any finding;
  token-like values are masked.
- `assets/hooks/pre-commit` and `assets/hooks/commit-msg`: the local guard, active in every repo
  whose git config names a boundary (`org-boundaries.exclude`).
- `references/surfaces.md` (forge text, CI variables, registries, wikis, worktrees) and
  `references/history-rewrite.md` (a git filter-repo plan with tree-hash proof and forge purge).

**Install:**

```text
/plugin install org-boundaries@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s org-boundaries`.

**Try:** "copy our retry lessons from my day-job repo into my open-source project", "does this
repo still mention my old employer anywhere?", "my agent pushed a commit with my work email to my
public repo", "should I rewrite history to get a client's name out?", "the tracker MCP in my side
project wrote to my employer's board".
