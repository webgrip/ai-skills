---
name: org-boundaries
description: Keeps each organisation's knowledge and identity out of the others' repos when one person works for several on one machine (an own company, an employer, clients) - what to remove and what stays, tell-tale references, a stdlib scanner over file content, commit authors and committers, messages, branches and tags, rewrite rules for neutral prose, a pre-commit guard, per-directory git identity, and user-level agent config that crosses organisations. Use when publishing or copying work from one organisation's repo into another's or a public repo, scrubbing a company, client or employer name out of a repo, checking whether a repo, branch or MR still mentions another organisation, a commit went out under the wrong work email, an agent's scratch clone committed with the employer's identity, deciding whether to rewrite git history to remove a name or email, an MCP server, rule or hook from one organisation acts in another's repo, or before a subagent writes across an organisation line.
---

# Org boundaries: one person, several organisations, nothing crosses

Examples use two fictional organisations: **acme** (the person's own company) and **globex**
(the employer). Every rule holds in both directions and for every client.

## The rule: remove the organisation, keep the person

| Remove: the other organisation as an entity | Keep |
| --- | --- |
| its name, domains, forge, registry and internal hosts, cluster and node names | the person: name, the address and handle this organisation knows them by, CODEOWNERS and owner entries, home path in editor settings |
| its clients, colleagues, workspace and account ids, ticket keys, decision-record numbers | functional references byte for byte: image, chart and package paths that tooling pulls (allow-list them, neutralise only the prose around them) |
| its clients' domain words, internal component names, tiers, experiments | product and tool names as plain names; generic words |
| comparisons with it, parity reasoning, "inspired by" lines | the engineering lesson, its numbers and its reason |

- Removing the person revokes real access and rewrites who did what; an anonymising pass is wrong.
- **Counts:** everything in the repo or on its forge: files, repo-local skills and hooks, CI
  config, commit metadata, branches, tags, MR/PR and issue text, CI variables, registry names.
  **Does not count:** what the person installs for themselves (user-level skills, plugins, memory).
- Reading another organisation's repos for context is fine; writing its facts or identity is not.
  A generic version of one organisation's lesson goes into another's repo only when the person
  asks for it, and then through **Publish across a boundary**.
- Decide which organisation owns a piece of knowledge before choosing where it is written. When
  delegating, give the subagent its target repo and this rule before it writes anything.
- **The record of a boundary respects the boundary.** Notes, reports, harvests, pattern lists and
  memory about acme live in acme's space or the person's user space, never in a globex repo.
  Inside globex write "an external organisation"; a cleanup commit reads
  `docs: drop references to an external organisation`.

## Tell-tales: a clean name grep proves nothing

Put these in the patterns file, not only the name:

- **Identifiers:** domains, forge and registry hosts, internal hostnames, cluster, node and workload
  labels, org-qualified repo refs (`globex/infra#47`), the person's address at that organisation,
  workspace and account ids, ticket key prefixes (`GBX-123`).
- **People:** colleagues' and client contacts' names and handles.
- **A client's domain words:** product names, internal jargon, component names only that client uses.
- **Implicit phrases:** "the homelab", "the sibling estate", "the other estate", "both estates",
  "two clusters", "their ADR-0042", "the twin record", "parity with …", "as it does in …".
- **Implicit structures** no regex finds; read the diff for them: decision drivers that exist only
  for parity, "inspired by / modelled on / reference implementation" lines, numeric comparisons
  with the other setup, documents that compare the two side by side.

## The patterns file

One file per organisation whose markers must stay out, outside every repo:
`~/.config/org-boundaries/globex.txt` (`$ORG_BOUNDARIES_DIR` or `$XDG_CONFIG_HOME` move it). A guard
that names the organisation inside the repo is itself the leak; the scanner refuses a patterns
file inside the repo it scans.

```text
globex
@globex\.example
\bGBX-[0-9]+\b
\bsibling estate\b
\bparity with\b
\bJordan Lee\b
allow:registry\.globex\.example/public/base-image
```

- One Python regex per line, matched case-insensitively; blank lines and lines starting with `#`
  are skipped.
- `allow:` lines exempt functional references: a match that lies inside an allow match on the same
  line is not reported.
- Name the files that apply to a directory tree once, in the per-directory git config that also
  sets the identity (**Identity per directory**). In `~/.gitconfig-acme`:

  ```ini
  [org-boundaries]
      exclude = globex
  ```

  Repeat `exclude` for every other organisation, clients included. Without `--org` or `--patterns`, the scanner reads
  `git config --get-all org-boundaries.exclude` in the repo.

## Scan

[scripts/scan_boundary.py](scripts/scan_boundary.py), Python 3.9+ stdlib. Exit 0 clean, 1 on any
finding, 2 on a usage or git error.

| When | Command |
| --- | --- |
| Before pushing into another organisation's or a public repo | `scan_boundary.py --org globex --range origin/main..HEAD REPO` |
| After a cleanup, and as the periodic re-check | `scan_boundary.py --org globex --all-refs --untracked REPO` |
| Old history accepted as it stands | add `--since-commit CLEAN_SHA`: identities and messages only after it |
| Hooks | `--staged` (pre-commit) and `--message-file FILE` (commit-msg), see **Guard** |

What it reads:

- **content:** tracked files in the working tree (binaries as raw bytes); `--all-refs` adds every
  branch and tag tip without a checkout; `--untracked` adds untracked files that are not ignored.
  Files over `--max-bytes` (default 10 MiB) are listed on stderr as not scanned.
- **path:** tracked paths, and with the flags above the paths at other tips and untracked ones.
- **identity:** author and committer name and email across all refs (or the range), plus taggers.
- **message:** commit messages including trailers (`Signed-off-by`, `Co-authored-by`), and
  annotated tag messages.
- **ref:** local and remote-tracking branch names and tag names.

Output is one tab-separated line per finding: surface, location, `rule F:L` (patterns file F, line
L, so a log never spells out the pattern list), excerpt. Token-like strings are masked to their
first four characters. The summary on stderr names no organisation.

Surfaces the scanner does not reach, each with its command in
[references/surfaces.md](references/surfaces.md): MR/PR titles, descriptions and **every note**
(API `search=` covers only titles and descriptions), issues, CI/CD variables at project, group and
environment level, container and package registry names, wikis and release notes, ignored files,
other worktrees, and earlier revisions in the forge's edit history.

## Publish across a boundary

When the person asks for a generic version of one organisation's work in another's or a public
repo:

1. Write it fresh for the target: strip clients, organisation paths and hosts, internal decision
   records, components, tiers and experiments; keep the lesson.
2. Run the target repo's own boundary checks and confirm its relative links resolve.
3. `git pull --ff-only`, then commit only that file, with the identity the target expects.
4. **Before the push:** `scan_boundary.py --org globex --range origin/main..HEAD REPO`, then read the
   diff for tell-tale structures. Once pushed to a public repo, forks and PR refs keep it.
5. Scrub the MR/PR title and body the same way before opening it.

## Neutralise

- Keep the substance and drop the attribution: "Inherited hardening from globex/edge incidents"
  becomes "Hardening from earlier production incidents".
- Delete reasoning that exists only for parity, or restate it on its own merits. Never invent a
  fact to fill the gap.
- Delete references to the other organisation's records; delete a bullet that held nothing else.
- A product link becomes the product's name; an image path in prose becomes "the upstream image".
- Rewrite a comparison document to cover one side; keep its filename and check inbound links.
- Keep layout: wrapping, table padding, heading anchors, and the ids of steps referenced from
  elsewhere, gaps included.
- Re-read sentences that leaned on a deleted one; replace rather than leave a dangling lead-in.
- YAML comments are safe to reword; a string value may flow into generated output, so rerun the
  generator's check.
- When a file already fails the formatter, compare the formatter's proposals before and after
  the edit to prove the edit added none.
- Validate each file type touched (`yq`, `bash -n`, `python3 -m py_compile`, a json5 parse, the
  formatter, generator checks), then rescan.
- Cleanup commit messages and MR titles never name the organisation.

## Guard: leaks come back with new work

Following an upstream change pulls the upstream's provenance back into comments and links, so a
one-off scrub decays within days. Install the local guard once per machine, from this skill's
directory:

```sh
mkdir -p ~/.config/org-boundaries
cp scripts/scan_boundary.py assets/hooks/pre-commit assets/hooks/commit-msg ~/.config/org-boundaries/
chmod +x ~/.config/org-boundaries/pre-commit ~/.config/org-boundaries/commit-msg
```

Then per repo, where no hook manager owns the hooks (`git config core.hooksPath` prints nothing):

```sh
hooks="$(git rev-parse --git-path hooks)"
for hook in pre-commit commit-msg; do
  [ -e "$hooks/$hook" ] || ln -s ~/.config/org-boundaries/$hook "$hooks/$hook"
done
```

The loop leaves an existing hook alone. Where a hook manager (CaptainHook, husky, pre-commit)
generated the hook git runs, put `~/.config/org-boundaries/pre-commit || exit 1` on its second
line, right after the shebang (some generated hooks end in `exec`), and
`~/.config/org-boundaries/commit-msg "$1" || exit 1` in `commit-msg`; a reinstall by the manager
removes them, so repeat after one. The hooks do nothing in a repo without
`org-boundaries.exclude`. They block added lines, new paths, the next commit's author and
committer, the branch name and the message; a leak already in an untouched line does not block
unrelated work.

Re-check periodically from the clean SHA, and find the commit that brought a term back:

```sh
scan_boundary.py --org globex --all-refs --since-commit CLEAN_SHA REPO
git log --format='%h %an %ad %s' --date=short -i -S globex CLEAN_SHA..origin/main
```

A CI guard fits only where the organisation running the CI owns every pattern, such as a company
keeping its own client names out of its public repos. Between the person's own organisations the
guard stays local: patterns stored in globex's CI variables are knowledge of acme inside globex.

## Identity per directory

A gitdir-scoped identity covers only repos under that directory. A clone an agent makes in a
temp or scratch directory falls back to the global identity, usually the employer's. In
`~/.gitconfig`:

```ini
[user]
    name = Pat Example
    useConfigOnly = true
[includeIf "gitdir:~/projects/acme/"]
    path = ~/.gitconfig-acme
[includeIf "gitdir:~/projects/globex/"]
    path = ~/.gitconfig-globex
```

Each included file sets `user.email` and the `org-boundaries` block. With no global email and
`useConfigOnly`, a commit outside both trees fails instead of guessing. A linked worktree placed
elsewhere still matches, because its git directory lives in the main repo; a fresh clone does not.

- **Agent scratch clone:** before the first commit run `git -C CLONE config user.email ADDRESS`,
  or clone under the organisation's tree.
- **Wrong identity, not pushed:** set the repo-local email, then
  `git -C CLONE commit --amend --reset-author --no-edit`; for several commits
  `git rebase --exec 'git commit --amend --reset-author --no-edit' BASE`.
- **Wrong identity, already pushed:** see **Rewriting history**.
- Audit a tree in one pass:
  `for d in ~/projects/acme/*/; do printf '%s %s\n' "$(git -C "$d" config user.email)" "$d"; done`.

## User-level agent config crosses organisations

Anything configured for the user reaches every repo on the machine, so one organisation's
config acts in the other's repos. Scope each at a boundary that follows the organisation:

| User-level config | Scope it by |
| --- | --- |
| `~/.claude/CLAUDE.md`, `~/.claude/rules/` | an ancestor-directory `~/projects/acme/CLAUDE.md`; levels and layering are the agent-instructions skill's |
| User-scope MCP servers | `claude mcp add --scope local` or `--scope project`, or a plugin installed per project |
| Plugin hooks | `claude plugin install --scope project` for a plugin whose hooks name, block or post anything organisation-specific |
| Telemetry env in `~/.claude/settings.json` | a filter on the repository owner in the collector; the agent-platform skill has it |

- **Same-named MCP servers** for two organisations (a `tracker` per board) send writes to the
  wrong tenant, where the same ids mean unrelated items. Name servers per organisation
  (`tracker-acme`, `tracker-globex`) and before the first write confirm the tenant with an
  identity call (`whoami`, current workspace) or the server's command or URL in
  `claude mcp get NAME`.
- A running session keeps the instructions and environment it started with; restart it after
  moving config.

## Rewriting history

A rewrite costs every collaborator (force-pushes, rebased MRs, fresh clones, paused bots, broken
hash links, lost signatures), and the forge keeps the old commits until its own cleanup runs.

| Situation | Do |
| --- | --- |
| Organisation name in a private repo's history | leave it: every viewer shows HEAD; clean HEAD and guard |
| The person's other address in a private repo's history | `.mailmap` entry `Pat Example <pat@acme.example> <pat@globex.example>`: git log and shortlog show the mapped address, the objects keep the old one, so scan with `--since-commit` |
| A legal or contractual reason, an outside party getting read access, or a public repo whose owner decides to rewrite | the plan in [references/history-rewrite.md](references/history-rewrite.md), one repo at a time after a pilot |
| A credential | rotate it first; a rewrite does not un-leak it |

Keep the rewrite plan outside the repo it rewrites.

## Gotchas

- Scan commit metadata **before** the push. A scan after a push to a public repo only measures
  the damage.
- A global `core.hooksPath` set to install the guard makes git ignore every repo's own
  `.git/hooks`, so hooks a manager installed there stop running.
- The forge keeps edit history: GitHub shows a comment's earlier revisions to anyone with read
  access until each revision is deleted from the history. Check every edited note.
- Bot-generated text (dependency-bot MR titles, changelogs) names a functional reference for as
  long as the reference exists; it stays.
