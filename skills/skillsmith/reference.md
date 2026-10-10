# Skillsmith reference — full frontmatter catalog, substitutions, advanced levers

Contents: [Frontmatter fields](#frontmatter-fields) · [Command name & discovery](#command-name--discovery)
· [String substitutions](#string-substitutions) · [Advanced levers + when each fits](#advanced-levers--when-each-fits)
· [Measure trigger accuracy & cost](#measure-trigger-accuracy--cost)
· [Evaluate an installed skill](#evaluate-an-installed-skill)
· [Eval cases](#eval-cases)
· [Research-backed skills](#research-backed-skills)
· [Bundled scripts](#bundled-scripts)
· [Skills that ship executables](#skills-that-ship-executables)
· [Skills that wrap risky operations](#skills-that-wrap-risky-operations)
· [Skills that ship a scanner](#skills-that-ship-a-scanner)

## Frontmatter fields

In Claude Code all fields are optional (only `description` recommended). The agentskills.io open spec
and opencode treat `name` + `description` as **required** — `name` must equal the directory name
(1–64 chars, `[a-z0-9]` + single hyphens), `description` ≤ **1,024 chars**. Set both, always, so the
skill stays portable. Accepts space-separated string OR YAML list where noted.

| Field | Type | Meaning / notes |
|---|---|---|
| `name` | string | Display label in listings. Defaults to dir name. Does **not** set the `/command` (dir name does), except a plugin-root `SKILL.md`. |
| `description` | string | What it does + when to use. Used for discovery. Falls back to first body paragraph. Combined with `when_to_use`, capped **1,536 chars** in the listing (`skillListingMaxDescChars`). |
| `when_to_use` | string | Extra trigger phrases / example requests. Appended to `description`; counts toward the 1,536 cap. **Claude Code extension** — not in the agentskills.io spec; opencode ignores it (fold into `description` for cross-tool skills). |
| `argument-hint` | string | Autocomplete hint, e.g. `[issue-number]`. UI only. |
| `arguments` | string\|list | Named positional args for `$name` substitution; map to positions in order. |
| `disable-model-invocation` | bool | `true` → only the user can invoke; removes description from Claude's context; also blocks subagent preload. Default `false`. |
| `user-invocable` | bool | `false` → hide from `/` menu (Claude-only background knowledge). Default `true`. Does NOT block Skill-tool access — use `disable-model-invocation` for that. |
| `allowed-tools` | string\|list | Pre-approve tools while active (no per-use prompt). **Additive, not restrictive.** Project skills need workspace-trust accepted. E.g. `Bash(git add *) Read`. |
| `disallowed-tools` | string\|list | Remove tools from the pool while active; clears on next user message. |
| `model` | string | Model while active (same values as `/model`, or `inherit`). Resets next prompt. |
| `effort` | enum | `low\|medium\|high\|xhigh\|max` while active. |
| `context` | `fork` | Run skill in a forked subagent; skill body becomes the subagent prompt. |
| `agent` | string | Subagent type when `context: fork` (`Explore`/`Plan`/`general-purpose`/custom). |
| `hooks` | map | Hooks scoped to the skill lifecycle (same format as settings hooks). |
| `paths` | string\|list | Globs that **limit auto-activation to matching file edits** (path-specific-rules format). |
| `shell` | enum | `bash` (default) / `powershell` for `` !`cmd` `` blocks. |
| `license` | string | Spec field. Claude Code accepts it and ignores it. |
| `compatibility` | string | Spec field: environment requirements, ≤ 500 chars. Claude Code ignores it. |
| `metadata` | map | Spec field: free-form keys for your own tooling. Claude Code ignores it. |

**Portable frontmatter.** claude.ai uploads, the Skills API and `package_skill.py` accept only the
spec's six fields — `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` —
and fail on anything else with `Unexpected key(s) in SKILL.md frontmatter`. A skill that ships
there keeps to those six. Quote a `description` that contains `: `: strict YAML parsers reject the
unquoted scalar, and some installers then skip the whole skill.

## Command name & discovery

- `/command` = **directory name** (`.claude/skills/deploy-staging/` → `/deploy-staging`).
- Precedence: enterprise > personal (`~/.claude/skills/`) > project (`.claude/skills/`); any overrides a
  bundled skill of the same name. Plugin skills are namespaced `plugin:skill` (no clash).
- **Precedence is silent.** With the same name in `~/.claude/skills` and the repo, only the personal
  copy is listed and runs — a global install of one variant wins in every repo on the machine.
- Project skills load from `.claude/skills/` in the start directory and each parent **up to the
  repository root, never above it**: a skills folder in a parent directory outside the repo (one per
  organisation or client) is never read. In a linked worktree the walk stops at the worktree root;
  from v2.1.277 a worktree without `.claude/skills` loads the main checkout's project skills.
- Nested `.claude/skills/` below cwd load on demand; on name clash the nested one becomes `path:name`.
- **Live change detection:** adding, editing or removing a skill applies within the session. A
  top-level skills dir created mid-session needs `/reload-skills`. (Project-skill
  `allowed-tools`/plugin bits need trust / `/reload-plugins`.)

## String substitutions

Expanded before Claude sees the body (preprocessing):

| Variable | Expands to |
|---|---|
| `$ARGUMENTS` | full arg string as typed (if absent in body, appended as `ARGUMENTS: <value>`) |
| `$ARGUMENTS[N]` / `$N` | 0-based positional arg (`$0` first). Shell-quote multi-word args. |
| `$name` | named arg declared in `arguments:` |
| `${CLAUDE_SESSION_ID}` | current session id (logging, session files) |
| `${CLAUDE_EFFORT}` | `low…max` (ultracode reports `xhigh`) |
| `${CLAUDE_SKILL_DIR}` | the skill's own dir — use to call bundled `scripts/` regardless of cwd |

> **Caveat:** the exact spelling of the skill-dir variable (`${CLAUDE_SKILL_DIR}` vs `${CLAUDE_PLUGIN_ROOT}`)
> is harness-version-dependent — **verify it against the deployed harness before relying on it**; don't
> treat either as canonical without checking.

Escape a literal `$` before a digit/`ARGUMENTS`/declared name with one backslash: `\$1.00`.

## Advanced levers + when each fits

- **`paths:`** — auto-activate only when editing matching files. Fits a skill tied to a file type/tree
  (e.g. a linter for `*.tsx`). **Limits** triggering — wrong for skills that must fire on conversational
  intent with no file open.
- **`context: fork` + `agent:`** — run the skill as an isolated subagent; body is the prompt, no
  conversation history. Fits a self-contained task (research, a one-shot generator). Wrong for inline
  reference/guidance, or a skill that must write back into the main conversation.
- **Dynamic injection `` !`cmd` ``** (or fenced ` ```! `) — runs a shell command at invocation and
  inlines its output before Claude reads the body. Fits state-grounded skills (summarize *this* diff,
  show *current* cluster state). Cost: runs every invocation + adds the output's tokens. Wrong for
  how-to skills that only sometimes need the state. Disable globally via `disableSkillShellExecution`.
- **`disable-model-invocation` / `user-invocable`** — invocation control for side-effecting `/commands`
  or pure background knowledge. Most procedure skills want neither (let Claude auto-load).

## Measure trigger accuracy & cost

- **`skill-creator` plugin** (`/plugin install skill-creator@claude-plugins-official`) — writes
  `evals/evals.json`, runs each prompt in an isolated subagent **with vs without** the skill, grades
  assertions, and reports pass-rate + token/time overhead + a blind A/B between two versions. Use it to
  prove an edit is an improvement and to tune a description that mis-triggers.
- **`/doctor`** — shows how many skill descriptions are being shortened/dropped from the listing budget,
  and which. Run after adding/editing skills to confirm none you rely on got squeezed out.
- Budget knobs: `skillListingBudgetFraction` (default 1% of context window), `skillListingMaxDescChars`
  (1,536), `SLASH_COMMAND_TOOL_CHAR_BUDGET`; demote low-priority skills to `"name-only"` via
  `skillOverrides` to free budget.
- **Count every installed skill.** Skills a framework or generator installs into the repo compete for
  the same budget as your own; `/skill-doctor` lists each skill's context cost and use.

## Evaluate an installed skill

Full pass = qualitative audit → triggering eval → output-quality benchmark.

- **Triggering: faithful probe, not `run_eval.py`.** The `skill-creator` harness injects each description as
  a *duplicate command twin* and only counts that twin firing — it **systematically undercounts an
  already-installed skill** (the real skill wins the match, twin never fires). Instead run `claude -p <query>`,
  parse stream-json for the `Skill` tool call, compare to expected. Probe *symptom* phrasings, not just
  canonical ones — under-triggering hides there.
- **Two probes, two questions.** *Is the description good?* — isolate: empty temp cwd,
  `--plugin-dir <skill> --setting-sources "" --strict-mcp-config --tools Skill --no-session-persistence`,
  on a capable model. That drops installed plugins, `~/.claude/CLAUDE.md`, MCP servers and every tool
  the agent could wander off with; a default session loads all of them, and a sibling skill steals
  triggers. *Does it fire for me?* — then one pass in the real repo with everything installed, to catch
  siblings competing for the same prompts:

  ```bash
  claude -p "$prompt" --output-format stream-json --verbose --max-turns 3 \
    --disallowedTools "Bash" "Edit" "Write" "NotebookEdit" "Agent" < /dev/null \
    | jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use" and .name=="Skill") | .input.skill'
  ```

  A hit is a `Skill` call naming the skill, plain or `plugin:skill`; the `system` `init` event's
  `skills` list confirms the skill was loaded at all. Close stdin (`< /dev/null`): `claude -p` appends
  piped stdin to the prompt. The repo's own context moves hit rates — a prompt about a bloated
  CLAUDE.md rarely fires in a repo whose CLAUDE.md is short.
- **Contention reads as misses.** Probes run beside other sessions time out, and a timeout grades as
  a FAIL. Probe on an otherwise idle machine at low parallelism, and re-run each failure alone before
  touching a description. A runner that exits non-zero on any FLAKY or FAIL means at least one miss,
  not a crash.
- **Runs and verdicts.** ≥ 3 runs per prompt: all as expected = pass, none = fail, mixed = flaky. Re-run a
  flaky prompt at 5 before tuning; a 2-in-3 case often reads as a miss on one run.
- **Read a consistent miss before tuning.** A case the description itself excludes is a mislabelled
  should-not-fire probe. A prompt that makes the model stop and ask first (an ethical snag, missing
  facts) never fires on turn one: that case tests output quality, so mark it as such and keep a plain
  version of the request as the trigger case.
- **Calibrate the probe model** on a skill known to fire before trusting a miss. Small models under-trigger
  on good descriptions (haiku missed cases that sonnet fires on reliably), so a cheap probe can be a
  broken one. A timeout or session error is a probe problem, never a description verdict.
- **When the benchmark ties, the value is the gotchas, not the scaffolding.** On greenfield scaffolding a
  skill-on/skill-off benchmark can tie 9/9 — enforcing hooks + strong reference apps already carry the happy
  path; the skill's measurable win is speed/economy. Read that as: invest the skill's body in
  **debugging/gotcha knowledge and symptom-triggering**, not more happy-path prose.
- **Baseline isolation:** `claude -p --disable-slash-commands --disallowed-tools Skill` (skills off, same
  repo/CLAUDE.md/hooks).
- **Grade output quality from frozen, isolated runs.** Snapshot the skill folder (`cp -R`), then run
  each case in an empty temp dir with only the snapshot: `--plugin-dir <snapshot> --setting-sources ""
  --output-format stream-json --verbose --max-turns 15`, stdin closed. Parse the `Skill` calls and the
  final `result`, write one file per case (prompt, skill calls, assertions, answer), and read every
  answer against its assertions. Run at most 3–4 cases in parallel. The snapshot keeps edits you make
  during the run out of the graded answers.
- **Sensitive-path / worktree traps:** benchmark worktrees MUST live **outside `.claude/`** — anything under
  it trips built-in sensitive-path protection (auto-denies every write under headless `acceptEdits`); put them
  in `/tmp`. A `claude -p` run *inside* a worktree can still write into the MAIN checkout (worktree `.git` is a
  gitfile → project-root resolves to main) — capture outputs, then `git checkout`/`rm` the pollution.

## Eval cases

`evals/evals.json` follows the skill-creator format: `skill_name`, then `evals[]` of `id`, `prompt`,
`expect_trigger`, `assertions[]`. `expect_trigger: false` marks a should-not case; `null` marks a
quality-only case the trigger probe skips.

- **Should-not prompts come from the neighbouring skills' territory**, so the probe measures
  discrimination, not only recall.
- **Prompts in the user's words**, symptom phrasings included, each standing on its own.
- **Assert what must not happen** as well as what must: "Does not run the upgrade itself; hands the
  command to the human".

```json
{"id": "not-neighbour", "prompt": "a request the neighbouring skill owns", "expect_trigger": false,
 "assertions": ["Handled as the neighbouring skill's task; this skill's procedure is not started"]}
```

## Research-backed skills

For a skill distilled from an article, a talk or a literature search.

- **Survey what exists first.** `npx skills find <topic>` and the top repositories show what people
  already ship: take the best ideas, avoid the name, and know what the new skill must beat.
- **Parallel research tracks**, one read-only subagent each, angles that do not overlap (prior art
  and published skills, academic work, practitioner and vendor guidance, tooling, upstream facts with
  a URL per answer), each writing full notes to a scratch file and returning a short summary. The main
  context stays small; notes stay greppable. Subagents share a web-search budget — give each a quota.
- **Briefs:** each agent reads the current skill first, writes no memory, and is told about the
  repo's hooks.
- **A repo-history track** for a skill that encodes existing practice: `git log -p` on the files the
  draft cites, with TRUE / FALSE / UNCLEAR per draft claim.
- **One adversarial fact-checker** against primary sources: it finds the median read as a mean, the
  default that is really configurable, the dead link.
- **Same-direction errors.** Two agents that each saw one slice can be wrong the same way. Cross-check
  the reports against each other, and settle a shared or contested claim at the upstream source.
- **One-command checks** beat reading. A dead project:
  `curl -s https://api.github.com/repos/<owner>/<repo> | jq '{archived, pushed_at}'`. Whether an
  image tag exists: an anonymous registry manifest request (200 or 404). Versions: the release list.
- **One track audits evidence**, with no other job: for every headline claim, find the controlled study,
  the replication or the absence of one, and label strength — **Strong** (controlled or large-sample) ·
  **Consistent** (several sources agree) · **Contested** · **Anecdotal** (one run, one team, unpublished
  vendor data). Expect headlines to shrink: a single-run 83 % token cut met a controlled ~7 %; popular
  UX "laws" turned out to be misquoted (Miller's 7±2 is about memory span, not menu length).
- **Carry the labels into the skill**: a legend once, a tag per claim in the reference files, the
  replicated size in any number the agent will act on, the headline only as motivation.
- **Every number from its primary source.** Summaries by tools and subagents get figures wrong (a fetched
  summary invents them); open the paper's own tables or the docs before a number enters the skill.
  A claim seen only in a search snippet is labelled UNVERIFIED.
- **Writing the skill audits the procedure.** Encoding a runbook re-checks it against the live system;
  expect steps to be overturned and inventories to be stale, and fix them in the source too.
- **Save notes as reports arrive**, so a compaction loses nothing; merge in one pass, then run lint,
  tests and the probe.
- **Volatile facts in a dated data file** (prices, model limits) that the scripts read, and recompute
  derived numbers instead of trusting a tool's own: a CLI's reported cost can price a model at last
  quarter's rate.

## Bundled scripts

Scripts run on whatever machine loads the skill, not the one they were written on.

- **macOS `/bin/bash` is 3.2.** It has no `mapfile`: read into an array with
  `while read -r item; do items+=("$item"); done < <(command)`. A failing `[[ … ]]` does not stop a
  script under `set -e` (a failing `[ … ]` does), so end each check with `|| exit 1` or a `fail`
  call. Under `set -euo pipefail`, a `grep` that matches nothing inside `$(…)` kills the script:
  write `{ grep … || true; }`.
- **Slim CI images** lack what a laptop has (`node:22-slim` has no `python3` and no `ps`). Run the
  skill's `test.sh` inside the CI image, installing what the job installs:
  `docker run --rm -v "$PWD":/w -w /w <ci-image> bash -c '<install step>; bash skills/<name>/test.sh'`.
- **Baseline first.** A local failure is the change's only if main passes: run main's version in a
  clean detached worktree (`git worktree add --detach <dir> origin/main`) before blaming the diff.
- **Clear the host environment a test reads** (editor and terminal variables), so it behaves as in CI.

## Skills that ship executables

- **An update never reruns the install script.** `npx skills update` and plugin updates replace files
  only, so a command a release adds stays unlinked. Call bundled scripts by quoted absolute path
  (generated config included), or let the skill's normal entry point link any missing command itself,
  never overwriting a link that points into another folder.
- **Test from a checkout by path.** Running the install or setup step from a development checkout
  points the user's global commands, and any config it writes, at that checkout: they run whatever
  branch is checked out, and later updates never reach them. If you must, re-run the install from the
  installed copy before you finish; setup should warn when it runs from a git work tree.

## Skills that wrap risky operations

When a mistake is expensive (a node drain, a database failover, a release), the skill prepares and
verifies, and the human runs the mutation. The agent runs only read-only and `--dry-run` commands.

1. Change the pins in git and regenerate the derived config in the same change.
2. Run the bundled read-only planner and the repo's own preflight.
3. Hand off paste-ready commands in order, one row per target:
   `| # | Target | You run | Then tell me, I verify |`.
4. Verify after every human step; stop on any anomaly.

The planner is a gate script. Without arguments it judges what is pinned; with arguments, a proposed
change's targets. It prints `== section` headers, one `ok` / `WARN` / `BLOCK` line per check and a
verdict (`PLAN: BLOCKED — resolve every BLOCK line before handing off`), and exits 0 only when no
BLOCK fired. Exercise every branch with hypothetical targets, a nonexistent version included, and let
it compare its hand-maintained lists (nodes, hosts, versions) with the live inventory.

## Skills that ship a scanner

A shipped scanner or linter is only useful while agents trust its findings.

- **Fixture pair**: `fixtures/careless/` where every rule must fire, with an expect file listing them, and
  `fixtures/careful/` where nothing may fire. `test.sh` asserts both; a new rule lands with its careless
  case and its careful counterpart.
- **False-positive pass on real code** before release: run it on two or three real repositories, read
  every hit, and turn each false positive into an exemption plus a careful-fixture case. Every false
  positive teaches the agent to ignore the tool.
- **Severity and a pointer per finding**: the rule name, `file:line`, and the reference section that says
  what to do instead.
- **Markdown-aware matching.** Agent-written text is Markdown: strip fenced blocks and code spans before
  matching, treat a heading inside a fence as text, and join wrapped continuation lines before reading
  a field. Each false positive gets a regression test; reword prose rather than weaken the rule.

  ~~~python
  plain = re.sub(r"(?ms)^\s{0,3}(```|~~~).*?^\s{0,3}\1", "", text)
  plain = re.sub(r"`[^`\n]*`", "", plain)
  ~~~

- **One bar for every team.** When a shared check must accept one team's format (an alias for a
  required section), accept it and print a MANUAL line whenever the alias stands in, instead of
  relaxing the rule for everyone.

Source of truth: <https://code.claude.com/docs/en/skills>. Re-verify here before changing the SKILL.md guide.
