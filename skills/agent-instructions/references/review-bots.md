# Review bots

An AI review bot reads the repo's instruction files plus its own config, and its comments are
input to human review, never the approval. Set it up in step 7 of
[Set up a repo](../SKILL.md#set-up-a-repo); which bot to enable is in [targets.md](targets.md#review-bots).

## Contents
- [Any review bot](#any-review-bot)
- [CodeRabbit](#coderabbit)
  - [Config files and precedence](#config-files-and-precedence)
  - [Map rules to the bot](#map-rules-to-the-bot)
  - [Profile per change risk](#profile-per-change-risk)
  - [Learnings and other context](#learnings-and-other-context)
  - [Noise and quota](#noise-and-quota)
  - [Gates](#gates)
  - [Validate the config](#validate-the-config)
  - [The coding agent's review loop](#the-coding-agents-review-loop)
  - [Plans and limits](#plans-and-limits)
- [Other review bots](#other-review-bots)
  - [At a glance](#at-a-glance)
  - [GitHub Copilot code review](#github-copilot-code-review)
  - [OpenAI Codex code review](#openai-codex-code-review)
  - [Cursor Bugbot](#cursor-bugbot)
  - [Greptile](#greptile)
  - [REVIEW.md, the shared review file](#reviewmd-the-shared-review-file)
  - [Forges](#forges)
- [Measuring value](#measuring-value)

## Any review bot

- **A PR can rewrite the rules it is reviewed against.** Copilot code review, CodeRabbit and
  Greptile read instructions and config from the PR's head branch. Put rule files and bot configs
  under CODEOWNERS, let `check` fail on drift, and read a rule change before the review it got.
- **One bot reviews every change.** A second AI reviewer belongs only on high-risk changes and
  comes from a different model vendor than the code's author.
- **Skip drafts.** Every bot below except Gemini Code Assist skips them by default; keep it so and
  ask for a review on demand.
- **Map each rule to its paths explicitly.** Bots ignore rule frontmatter and may scope a guideline
  file to its own folder. Generate the mapping from `.ai/rules`, then read the review summary to see
  which guidelines it applied.
- **Check what it auto-loads.** Bots pick up every agent's instruction files, skills and generated
  rule copies; prune what does not belong in review.
- **Keep one config format** when the bot reads two with a silent precedence, and assert it in CI.
- **Validate the config for unknown keys**, not only against the schema, and confirm the resolved
  config with the bot's own "show configuration" command.
- **Strictness per change**: strict on high-risk paths, quiet elsewhere and when paths are unknown.
- **Scope its memory to the repo** in an organisation with many clients, and treat bot learnings as
  an inbox that empties into reviewed rules, checks and docs.
- **Tell it what tools decide** (format, types, docstrings, style) and to stay silent on those. Add
  a review instruction only after the same gap shows in several reviews, measurable and scoped.
- **Gates are CI tests.** A rule a parser can check is a test the bot then explains; prompts and
  guidelines are advice ([enforcement.md](enforcement.md#checks-over-prose)).
- **Humans keep** intent, domain fit, cross-module impact, migrations and money paths, test
  adequacy and sign-off. Keep changes small.

## CodeRabbit

Sources: [docs](https://docs.coderabbit.ai), [schema](https://coderabbit.ai/integrations/schema.v2.json),
[review commands](https://docs.coderabbit.ai/reference/review-commands).

### Config files and precedence

- `.coderabbit.yaml` (or `.yml`) at the root, or `.coderabbit.config.ts`. **A committed root YAML
  wins and the TS file is ignored entirely, with no warning**: keep one, and fail CI when both
  exist. With TS, keep static settings in a YAML under `.coderabbit/` and import it
  ([TS config](https://docs.coderabbit.ai/configuration/typescript-configuration)).
- The config on the PR's head branch reviews that PR ([Any review bot](#any-review-bot)); fork PRs
  use the target branch's.
- The TS sandbox has no network, filesystem, `.md` reading or npm packages: it cannot read rule
  frontmatter, so the mapping is still generated. Type-check against `@coderabbitai/config`; a
  local stub typed `Record<string, unknown>` catches nothing.
- Order: global overrides (top plan) > repo file > central `coderabbit` repo > repo UI > org UI >
  schema defaults. **Without `inheritance: true` nothing merges**: the highest source wins whole and
  unset keys fall to schema defaults, not to your organisation's values. The central repo applies
  only to repos without a file of their own, and the bot must be installed on it
  ([inheritance](https://docs.coderabbit.ai/configuration/configuration-inheritance)).
- `remote_config` is documented, but the schema and the validator reject it.
- Proof of what is in effect: `@coderabbitai configuration` on a PR shows every resolved value with
  its source.

### Map rules to the bot

- It auto-loads `**/AGENTS.md`, `**/CLAUDE.md`, `**/GEMINI.md`, `**/AGENT.md`,
  `.github/copilot-instructions.md`, `**/.cursor/rules/*`, `**/.clinerules/*`, `**/.cursorrules`,
  `**/.windsurfrules`, `**/.rules/*` (plus `.github/instructions/*.instructions.md` or
  `**/REVIEW.md`, depending on the page you read), and every `SKILL.md` under `skills/<name>/` or
  `.<tool>/skills/<name>/` as an "Agent Skill". `.ai/rules` and `.claude/rules` are not defaults.
- A plain glob in `knowledge_base.code_guidelines.filePatterns` scopes each file to **its own
  folder** and ignores its frontmatter: `.ai/rules/billing.md` listed that way governs only
  `.ai/rules/**`. Map each rule with an object whose `files` and `applyTo` are comma-separated
  strings (a YAML list fails the schema)
  ([code guidelines](https://docs.coderabbit.ai/knowledge-base/code-guidelines)):

  ```yaml
  knowledge_base:
    code_guidelines:
      enabled: true
      filePatterns:
        - files: ".ai/rules/billing.md"
          applyTo: "src/Billing/**, tests/Billing/**"
  ```

- `agent_setup.py generate` writes one such entry per rule between its markers and `check` fails
  when they are stale; hand-written entries outside the markers stay. It looks for the markers in
  `.coderabbit.yaml`, `.coderabbit.yml` and `.coderabbit/*.yaml` (under `filePatterns` in the root
  file; a TS config imports the `.coderabbit/` YAML that holds them). With no markers anywhere,
  `generate` prints the block to paste and exits 1. `applyTo` splits on commas, so `generate`
  expands braces and `check` fails on a comma outside braces in a rule glob.
- Generated `.cursor/rules/*.mdc` copies are auto-loaded too, scoped to `.cursor/rules/`, and
  irrelevant skills (a cloud-VM setup skill) steer reviews. No key drops one file: trash it on the
  Code Guidelines page.
- Never list guideline files in `reviews.path_instructions`: they get reviewed, not used.
- Check the first review after a change: its "Code guidelines" list marks each file `configured`,
  `auto-discovered` or `Agent Skill`.

### Profile per change risk

`reviews.profile` is `quiet` (only critical and major findings inline), `chill` (default) or
`assertive`; it also sets the strictness of the bundled linters. Choose it per PR in the TS config:

```ts
import { defineConfig, mergeConfig } from "@coderabbitai/config";
import base from "./.coderabbit/base.yaml";

const highRiskPaths = [/^src\/Billing\//, /^database\/migrations\//];

export default defineConfig((context) => {
  const changedFiles = context.pr?.changedFiles;
  const touchesHighRisk =
    changedFiles?.status === "resolved" &&
    changedFiles.paths.some((path) => highRiskPaths.some((pattern) => pattern.test(path)));
  return mergeConfig(base, { reviews: { profile: touchesHighRisk ? "assertive" : "chill" } });
});
```

A conditional reminder in `path_instructions` ("billing code changed but no doc") shows only when
its `path` matches: the glob must cover every file that should trigger it.

### Learnings and other context

- `knowledge_base.learnings.scope`, `issues.scope` and `pull_requests.scope` default to `auto`,
  which is **organisation-wide on private repos**: one client's learnings and PRs surface in
  another client's review. An agency sets all three to `local` in every repo's own file; an org UI
  default never reaches a repo that has a file (above).
- `learnings.approval_delay` (1–30 days) holds chat-sourced learnings as requests that are
  **approved automatically at the deadline unless rejected**: a review window, not a gate. Learnings
  the review itself infers apply at once to their PR
  ([learnings](https://docs.coderabbit.ai/knowledge-base/learnings)).
- Learnings are invisible to people and other agents. Each quarter, verify each against the code,
  move durable ones into a rule, check or doc through review
  ([maintenance.md](maintenance.md#agent-proposed-rules)), then delete them in the bot (needs the
  admin role). `knowledge_base.opt_out: true` deletes all of them irreversibly.
- An MCP connection gives the bot everything its authorising user can see. Never connect a
  workspace shared by several clients; otherwise a read-only, least-privilege account attached to
  one repo's review scope.
- The linked-issue check (`issue_assessment`) reads only native trackers (GitHub, GitLab, Azure
  Boards, Jira, Linear); with tickets elsewhere it silently never runs. Mirroring tickets into
  native issues works only from a trusted pipeline ([unattended.md](unattended.md#ci-secrets)).

### Noise and quota

- Keep `reviews.auto_review.drafts: false`; ask for a review with `@coderabbitai review`.
- Opt-outs: `auto_review.labels: ["!no-review"]` and `ignore_title_keywords` (substring,
  case-insensitive).
- `auto_review.auto_pause_after_reviewed_commits` (default 5): 1–2 on busy branches, since every
  re-review counts against the hourly limit.
- `reviews.path_filters`: exclusions (`!`) only; a single include turns the list into an allowlist.
- Bundled linters (`reviews.tools.*`) run without your includes, plugins or private registries and
  contradict your CI. Turning off the ones CI runs with your config is a team choice, not vendor
  guidance; keep the scanners nothing else runs (secrets, dependency advisories, shell, Dockerfile).
  The `gitleaks` key runs Betterleaks; dotenv-linter's key is `dotenvLint`
  ([tools](https://docs.coderabbit.ai/tools/index)).

### Gates

- Pre-merge checks `title`, `description`, `docstrings` and `issue_assessment` take `off`,
  `warning` or `error`. **`error` blocks only with `reviews.request_changes_workflow: true`**, and on
  GitLab only when an approval rule requires the bot's approval
  ([pre-merge checks](https://docs.coderabbit.ai/pr-reviews/pre-merge-checks)).
- With squash merges the PR title becomes the commit message: a `title` check with pass and fail
  examples enforces the commit format no commit hook sees.
- Bypasses exist ("Ignore failed checks", `@coderabbitai ignore pre-merge checks`, `approve`,
  `resolve`); restrict them with `reviews.allow_author_approval: false` and
  `override_requested_reviewers_only: true`.

### Validate the config

- The schema rejects unknown keys only at the root and on a few objects: a misspelled key under
  `reviews`, or an invented one such as `reviews.instructions`, validates and silently does
  nothing. Repo-wide review text goes in `path_instructions` with `path: "**"`.
- Run `coderabbit config validate <file>`, then walk the config against the schema's `properties`
  and fail on any key the schema does not define. For a TS config, validate the merged result per
  branch of the factory, and run `tsc --noEmit` against `@coderabbitai/config`.

### The coding agent's review loop

- Install: the install script provides `coderabbit` and `cr`; the Homebrew cask only `coderabbit`.
  Write `coderabbit` in docs and instructions. Login opens a browser with a localhost callback, so
  a person runs `coderabbit auth login`; headless runs use `--api-key` (there is no env var).
  `coderabbit doctor` exits 1 when a check fails ([CLI](https://docs.coderabbit.ai/cli/index)).
- One `AGENTS.md` line: "Before opening a merge request, run
  `coderabbit review --agent --fresh --base main` in the background, at most twice; fix critical
  and major findings and reject the rest with a one-line reason."
- In the background: a review takes 7–30+ minutes.
- At most two rounds: later rounds mostly review the earlier fixes, and about half of AI review
  comments are wrong or misaligned.
- Exit 0 means the review ran, not that the code is clean: parse the findings. Without `--fresh` a
  reused checkpoint can report zero findings; check `reused` and `unreviewedFileCount`
  ([agent mode](https://docs.coderabbit.ai/cli/agent-mode)).
- Never pass `--use-credits`: over the limit, agent mode answers `action_required` instead of
  charging.
- Plugin command names differ between plugin versions; name the one present in all
  (`/coderabbit:code-review` in Claude Code). Autofix needs `gh` and so works on GitHub only.
  Check each integration for quota use and transcript uploads.
- Re-fetch thread state right before replying: the bot resolves its own threads after a
  re-review. Answer each open thread with the fixing commit or a one-line reason.
- When the bot cites a "standard", ask for the file and line; unsourced findings get withdrawn.

### Plans and limits

- Review limits are per developer identity per hour: one bot or agent account that opens every PR
  gets one developer's capacity. Agent-run reviews bill twice: the bot's quota and the coding
  agent's tokens fixing the findings.
- Plan features (custom pre-merge checks, linked repositories, MCP connections, global overrides,
  the metrics API) and limits change often: check the current
  [plans page](https://docs.coderabbit.ai/management/plans) and
  [rate limits](https://docs.coderabbit.ai/management/rate-limits) before relying on one. Turn
  usage-based billing off or cap it.
- On GitLab many features are GitHub-only (autofix skills, CLI `--remote`, Fix CI, review
  progress): check the platform notes for each feature you plan to use.

## Other review bots

Which bot to pick: [targets.md](targets.md#review-bots). The rules under
[Any review bot](#any-review-bot) apply to each.

### At a glance

| Bot | Reads from the repo | Path scope | Config read from | Learning and isolation |
|---|---|---|---|---|
| GitHub Copilot code review | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, root `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `REVIEW.md`, skills | `applyTo` globs | head branch; settings in rulesets | Copilot Memory per repo; organisation custom instructions reach every repo |
| OpenAI Codex code review | `AGENTS.md` only, its `## Code Review Rules` section | nearest `AGENTS.md` | settings in ChatGPT | none |
| Cursor Bugbot | `.cursor/BUGBOT.md`, root and nested; not `.cursor/rules` | nested files on the changed file's path; dashboard rules with globs | `.cursor/config/bugbot.yaml` from the base branch | learned rules per repo; Team Rules reach every repo |
| Greptile | `.greptile/` at any depth; auto-detects `CLAUDE.md` and `.cursor/rules` | `rules[].scope` globs, relative to the `.greptile/` folder | PR source branch (`autoApprove` from the base) | context and memories at org or team scope |
| Claude Code Review (managed) | root `REVIEW.md`, `CLAUDE.md` at every level | nested `CLAUDE.md`; paths in `REVIEW.md` as prose | the base branch's `CLAUDE.md` when a PR edits it | none in the org |
| Qodo, PR-Agent | `.pr_agent.toml`, org `pr-agent-settings` repo; Qodo imports `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, skills; PR-Agent reads `AGENTS.md` | folder of the imported file; portal path patterns | default branch | Qodo rule scope defaults to Global: set Repository |
| Devin Review | `**/REVIEW.md`, `**/AGENTS.md`, `**/CLAUDE.md`, `**/CONTRIBUTING.md`, Cursor, Windsurf and CodeRabbit files | directory of the file | settings in Devin | not documented |
| cubic | `cubic.yaml`, org `cubic-config` repo | `custom_rules[]` `include`/`exclude` globs | default branch | per team |
| Gemini Code Assist | `.gemini/config.yaml`, `.gemini/styleguide.md` | none (`ignore_patterns` only) | — | memory per repo; **reviews drafts by default** |
| GitLab Duo Code Review | `.gitlab/duo/mr-review-instructions.yaml`; not `AGENTS.md` | `fileFilters` globs with `!` | exclusions from the default branch | none |

Sources for the rows without a section below:
[Claude Code Review](https://code.claude.com/docs/en/code-review),
[Qodo](https://docs.qodo.ai/governance/rule-enforcement/building-review-standards),
[PR-Agent](https://docs.pr-agent.ai/usage-guide/additional_configurations/),
[Devin Review](https://docs.devin.ai/work-with-devin/devin-review),
[cubic](https://docs.cubic.dev/configure/cubic-yaml),
[Gemini Code Assist](https://docs.cloud.google.com/gemini/docs/code-review/customize-repo-review),
[GitLab Duo](https://docs.gitlab.com/user/duo_agent_platform/customize/review_instructions/).

### GitHub Copilot code review

- No config file: a branch ruleset ("Automatically request Copilot code review", repo, org or
  enterprise) turns it on, with options "Review new pushes" and "Review draft pull requests"
  ([setup](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-code-review)).
- Path rules are the generated `.github/instructions/<rule>.instructions.md`; review ignores a file
  without `applyTo`. `excludeAgent: "cloud-agent"` makes a file review-only, `"code-review"` hides
  it from review. Keep a file under about 1,000 lines
  ([instructions](https://docs.github.com/en/copilot/reference/custom-instructions-support)).
- Only the root `AGENTS.md` is documented for review. In VS Code and Visual Studio, review reads
  only `.github/copilot-instructions.md`.
- Organisation custom instructions reach every repo in the organisation: client rules stay in repo
  files. Copilot Memory facts stay in their repo.
- Reviews spend AI credits and, on private repos, Actions minutes; the review environment is
  `.github/workflows/copilot-code-review.yml`, else `copilot-setup-steps.yml`.

### OpenAI Codex code review

- Settings live in ChatGPT (automatic review per repo or per person), not in the repo
  ([docs](https://learn.chatgpt.com/docs/third-party/github)).
- Rules go in a `## Code Review Rules` section (`###` subheadings allowed) of the `AGENTS.md`
  closest to the code; Codex applies the root and every more specific file covering a changed file.
- A nested `AGENTS.md` written for review rules is loaded by every coding agent too, and in
  Copilot's cloud agent the nearest file wins over the root. Keep review rules in the root under
  per-path headings, or open a nested file with "Also follow the root `AGENTS.md`".
- On GitHub it posts only P0 and P1 findings, so a style rule never shows: that is a linter's job.
- Triggers: a PR opened for review, a draft marked ready, `@codex review`. Any other `@codex`
  comment starts a cloud task on the PR.

### Cursor Bugbot

- Rules come from `.cursor/BUGBOT.md` at the root (always) and every `<dir>/.cursor/BUGBOT.md` on the
  path of a changed file. **`.cursor/rules/*.mdc` do not apply**, so the generated Cursor rules never
  reach it: a `BUGBOT.md` beside the code holds what Bugbot must check there
  ([docs](https://cursor.com/docs/bugbot)).
- Each rule is cut at 30,000 characters and all rules at 100,000; `bugbot run verbose=true` lists
  the rules used and what was cut.
- `.cursor/config/bugbot.yaml` (base branch, under 64 KB): `triggers.drafts`, `triggers.frequency`,
  `review.effort`, `autofix.mode`, which can lower the dashboard setting but never raise it. A PR
  author's personal overrides beat it.
- Learned rules (from reactions, replies and human review comments) stay per repo; dashboard Team
  Rules reach every repo in the team, so client rules never go there.

### Greptile

- `.greptile/config.json` holds `rules[]` (`id`, `rule`, `scope`, `severity`), `ignorePatterns`,
  `autoReview`, `strictness`; `.greptile/rules.md` applies to its directory; `.greptile/files.json`
  lists context files. Nested `.greptile/` folders cascade: settings replace, rules accumulate, and
  `disabledRules` turns off an inherited rule by `id`. A legacy `greptile.json` beside a `.greptile/`
  is ignored ([docs](https://www.greptile.com/docs/code-review/greptile-config)).
- `scope` globs are relative to the `.greptile/` folder; filter globs are case-insensitive and
  cannot negate.
- It auto-detects `CLAUDE.md` and `.cursor/rules` at review time, with no documented switch.
  `greptile onboard` imports every `CLAUDE.md`, `.claude/rules`, `AGENTS.md`, `.cursorrules` and
  `.cursor/rules` it finds as **organisation-wide** context, without a picker: re-scope each to its
  repository afterwards.
- "Teach Greptile" (whose feedback becomes memory) defaults to everyone, people outside the
  organisation included: restrict it in the organisation settings.
- `autoReview` defaults to `["open"]`: pushes are reviewed only with `push` listed.

### REVIEW.md, the shared review file

- Copilot code review, Claude Code Review (root file), Devin Review (`**/REVIEW.md`) and Qodo (root,
  with `[review_agent] enable_review_md = true`) read `REVIEW.md`; CodeRabbit's schema lists it
  among its defaults. Codex, Bugbot and Greptile do not.
- Put repo-wide, review-only text there: which topics tools decide, which paths and finding
  categories to skip, the severity bar. In `AGENTS.md` the same lines cost every coding agent's
  context.
- Keep it a short regular file: Claude Code Review reports when it was cut for size or skipped
  because it is a symlink.

### Forges

| Forge | Bots |
|---|---|
| GitHub | all of the above |
| GitLab | CodeRabbit, Codex (beta), Bugbot (GitLab Premium+), Greptile, Qodo, Devin Review, GitLab Duo |
| Bitbucket | CodeRabbit, Bugbot, Greptile, Qodo, Devin Review (Data Center only) |
| Azure DevOps | CodeRabbit, Copilot (preview), Bugbot, Qodo, Devin Review |
| Forgejo, Gitea | only Greptile Enterprise (Gitea) and the open-source PR-Agent |

## Measuring value

- A comment counts as accepted when it carries the bot's "addressed in commit" marker, or when the
  lines around its position changed between the reviewed head and the merged head. Resolved-thread
  rates say nothing where resolving is required.
- Count comments inside review bodies too (GitLab rejects some inline comments and the bot moves
  them there), identify the bot by its comment markers rather than its username, cut stored text
  by characters, and use read-only API calls.
- Read acceptance together with time-to-merge and a noise rate (comments on topics tools decide).
  Expect a third to a half accepted: 36 % of 31,073 comments in
  [arXiv 2607.03316](https://arxiv.org/abs/2607.03316). An industrial reviewer with 74 % of
  comments acted on also lengthened time to close ([arXiv 2412.18531](https://arxiv.org/abs/2412.18531)).
- Vendor dashboards count reviewed-and-merged PRs only, and API access sits on top plans; a monthly
  run of your own script is enough.
- Classifying review comments with an LLM is unreliable without labels on several axes (cause,
  topic, severity), definitions, and an agreement check against two people. Reviewer-written
  labels (Conventional Comments) and a regex counter are cheaper.
