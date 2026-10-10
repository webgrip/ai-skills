# Unattended agents: cloud, CI and headless

Agentic runs (cloud agents, CI, headless) change what the instruction file can promise. Split the
work three ways: a **setup file** builds the machine, the **instruction file** says how to verify,
a **Stop hook or CI** enforces it. Machine building never goes in the instruction file. Which
cloud agents to enable: [targets.md](targets.md#cloud-agents).

## Contents
- [Setup, instructions, enforcement](#setup-instructions-enforcement)
- [Triggers, identity, network, forges](#triggers-identity-network-forges)
- [Repo files that change the security posture](#repo-files-that-change-the-security-posture)
- [What changes without a human](#what-changes-without-a-human)
- [What the instruction file adds for them](#what-the-instruction-file-adds-for-them)
- [CI secrets](#ci-secrets)
- [Traps](#traps)

## Setup, instructions, enforcement

| Agent | Setup | Instructions from the repo | Enforcement |
|---|---|---|---|
| Claude Code cloud sessions and routines ([docs](https://code.claude.com/docs/en/cloud-environments)) | setup script in the UI environment, run as root, must exit 0; a snapshot is reused when it finishes in about five minutes; plus repo `SessionStart` hooks gated on `CLAUDE_CODE_REMOTE=true` | `CLAUDE.md`, `.claude/rules`, `.claude/settings.json`, `.mcp.json`, `.claude/skills`; not plugins from repo settings or `settings.local.json` | Stop hook, repo hooks |
| Claude Code Action, GitLab CI/CD, `-p`, SDK ([Action](https://code.claude.com/docs/en/github-actions), [headless](https://code.claude.com/docs/en/headless)) | workflow steps before the call | `CLAUDE.md`, **not with `--bare`** or SDK `settingSources: []` | Stop hook (not with `--bare`), CI |
| Cursor cloud agents ([docs](https://cursor.com/docs/cloud-agent/setup)) | `.cursor/environment.json` from the default branch: `install` (idempotent), `start`, `terminals`, `build.dockerfile` or `snapshot`, egress and MCP allowlists | `.cursor/rules/*.mdc`, `AGENTS.md` | `.cursor/hooks.json` command hooks; `sessionStart` and user hooks do not run |
| Copilot cloud agent ([docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment)) | `.github/workflows/copilot-setup-steps.yml`, job `copilot-setup-steps`, default branch, ≤ 59 min; secrets under Settings → Agents, `COPILOT_MCP_*` ones only for MCP servers; MCP in repo settings, not a file | `copilot-instructions.md`, `.github/instructions` (`applyTo`), nearest `AGENTS.md`, root `CLAUDE.md`, `.github/agents/`, skills | `.github/hooks/*.json` on the default branch (`preToolUse` fails closed, `agentStop`), PR CI |
| Codex cloud ([docs](https://learn.chatgpt.com/docs/environments/cloud-environments)) | install script and start skill in the ChatGPT environment, not in the repo | `AGENTS.md`, repo skills | none from the repo; the agent runs the checks `AGENTS.md` lists |
| Devin ([docs](https://docs.devin.ai/onboard-devin/environment/git-backed-blueprints)) | `.devin/blueprint.yaml` (`initialize`, `maintenance`, `knowledge`), read on repo add and on push only with the sync toggle, built into a snapshot | `AGENTS.md`, first 16 KiB of each; `.agents/skills` | blueprint lint and test commands |
| OpenHands ([docs](https://docs.openhands.dev/openhands/usage/customization/repository)) | `.openhands/setup.sh`, every session | `AGENTS.md`, `.agents/skills` | `.openhands/hooks.json` Stop hook (exit 2) |
| Jules ([docs](https://jules.google/docs/environment/)) | setup script and snapshot in the UI | root `AGENTS.md` only | none documented |
| Amp orbs ([docs](https://ampcode.com/docs/orbs/customizing)) | executable `.agents/setup` (20 min), `.agents/resume`, `.amp/services.yaml` | `AGENTS.md`, falling back to `AGENT.md`, `CLAUDE.md` | plugins |
| GitLab Duo Agent Platform ([docs](https://docs.gitlab.com/user/duo_agent_platform/flows/execution/agent-config-yaml/)) | `.gitlab/duo/agent-config.yml` (`image`, `setup_script`, `cache`, `network_policy`) on the default branch | root `AGENTS.md`, `.gitlab/duo/chat-rules.md`, skills | MR pipeline |

Factory (Droids) reads `AGENTS.md`, `CLAUDE.md` and `.factory/`, and sets up worktrees from
`.factory/worktree-setups/*.yaml` ([docs](https://docs.factory.com/droid-computers/overview)).

## Triggers, identity, network, forges

| Agent | Triggered by | Acts as | Network default | Forges |
|---|---|---|---|---|
| Claude Code cloud | web, mobile, desktop, `claude --cloud`, routines (schedule, API, GitHub events), Slack | Claude GitHub App; credentials stay outside the VM behind a GitHub proxy that refuses tag pushes and branch deletions | Trusted allowlist (None, Trusted, Full, Custom) | GitHub; Enterprise Server on Team/Enterprise |
| Claude Code Action | `@claude`, assignee, label, or any event with a `prompt` | `claude[bot]` through OIDC; triggering needs write access | the runner's | GitHub; GitLab CI/CD beta maintained by GitLab |
| Cursor cloud agents | web, desktop, mobile, `@cursor` in Slack, GitHub, Bitbucket and Linear, API, automations | Cursor GitHub App, signed commits | internet on, "Default + allowlist" | GitHub, Enterprise Server, GitLab Premium+, Bitbucket Cloud (beta), Azure DevOps Services |
| Copilot cloud agent | issue assignment, `@copilot`, agents tab, API, automations, Jira, Slack, Teams, Linear | `copilot-swe-agent`, pushes only `copilot/` branches; workflows wait for approval; only write-access users trigger it | firewall with recommended allowlist, for the agent's Bash only (not MCP servers or setup steps) | GitHub only |
| Codex cloud | web, desktop, mobile, `@codex` on GitHub, `@ChatGPT` in Slack and Teams, Linear, `codex cloud exec` | ChatGPT Codex Connector app; the user opens the PR | "Package managers" preset or custom; legacy environments block the agent phase | GitHub; GitLab beta |
| Devin | Slack, Teams, Linear, Jira, `/devin` on PRs, API, automations | `devin-ai-integration[bot]`, or a service user on other forges | unrestricted unless a security profile applies | GitHub, GitLab, Bitbucket, Azure DevOps |

- **Forgejo and Gitea have no native cloud agent.** Run a headless CLI (`claude -p`, `codex exec`,
  the OpenHands SDK) in a Forgejo Actions runner with the repo's own token, under the
  [CI secrets](#ci-secrets) rule.
- Let only people with write access trigger an agent; an issue-triggered workflow runs for anyone
  who can open an issue.

## Repo files that change the security posture

Put these under CODEOWNERS and review a change to them as a code change
([security.md](security.md#review-checklist)):

- **Claude Code**: `.claude/settings.json` (hooks, `env`, permissions), `.mcp.json`, skills with
  `allowed-tools`. **Cloud sessions, `-p` runs, the Agent SDK and the GitHub Action load the
  repo's `.mcp.json` servers without asking** (the Action forces `enableAllProjectMcpServers`),
  and `-p` runs repo hooks, `env` and `apiKeyHelper` in a never-trusted checkout. On code from an
  untrusted branch run with `--bare`, `--setting-sources user` or `--strict-mcp-config`
  ([MCP](https://code.claude.com/docs/en/mcp), [permissions](https://code.claude.com/docs/en/permissions)).
  The Action restores `.claude/`, `.mcp.json` and `CLAUDE.md` from the base branch on PR events.
- **Copilot cloud agent**: `copilot-setup-steps.yml` (runs outside the firewall),
  `.github/hooks/*.json`, `.github/agents/*.md` (can declare MCP servers).
- **Cursor**: `.cursor/environment.json` can widen egress (`egressMode: allow_all`) and set the MCP
  allowlist; `.cursor/hooks.json`.
- **Devin**: `.devin/blueprint.yaml` build steps; skills that inject command output; `.envrc`,
  which its shell loads through direnv.
- **OpenHands**: `.openhands/setup.sh` and `.openhands/hooks.json` run without an approval step.
- **Amp**: `.agents/setup` is trusted code; `.amp/plugins/` load without a documented prompt.
- **GitLab Duo**: `setup_script` in `agent-config.yml` runs outside the sandbox with GitLab tokens in
  the environment.
- **Codex cloud and Jules**: only instruction files and skills come from the repo.

## What changes without a human

- Nobody answers a question or a permission prompt; a denied step fails or loops.
- Exports in a setup script do not reach the agent. Secrets may exist only during setup (Codex
  legacy environments) or reach programs as placeholders a proxy fills in (Codex and Claude Code
  network secrets).
- The network is allowlisted (Copilot firewall, Claude Code "Trusted", Cursor "Default +
  allowlist"): a fetch from an unlisted host fails mid-task.
- Snapshots keep files, not processes: databases and `docker compose` stacks start each session.
- A failed setup step can go unnoticed: Copilot skips the rest and starts anyway.
- Setup files are read from the default branch (Copilot, Cursor, Devin, GitLab Duo): a branch that
  changes them is tested only after it merges.
- The instruction file may not load at all (`claude -p --bare`, SDK `settingSources: []`), so a
  must-hold check lives in a Stop hook or CI, never only in prose.

## What the instruction file adds for them

1. **Definition of done**: the exact commands, narrowest first, with expected runtime
   ("`php artisan test --filter=Checkout` ~2 min; the full suite is CI's job"). Codex treats
   listed checks as mandatory, so list only what should always run.
2. **Environment facts an agent cannot guess**, one line each: which services must run and the
   command that starts them (or "not available here: skip browser tests"), known flaky or
   network-bound tests, the variable that marks a sandbox (`CLAUDE_CODE_REMOTE=true`).
3. **Where secrets come from**, never their values.

## CI secrets

A job that holds a token (a bot posting comments, an issue mirror, an agent with an API key, a
deploy key) never runs in a merge or pull request pipeline that executes branch code: whoever can
push a branch can edit the job and read the token. Run such jobs on protected branches, tags or
schedules; the `check` job holds no secret, so it can run on every change ([ci.md](ci.md)).

- **GitLab**: an unprotected variable reaches every pipeline in the project, MR pipelines and
  unprotected branches included. Masking only hides the value in job logs, and a hidden variable is
  only hidden in the settings UI; job code reads both. Mark tokens **protected**. MR pipelines get
  protected variables only through the project's opt-in, when both branches are protected. "Run
  pipeline" on a fork's MR in the parent project runs the fork's `.gitlab-ci.yml` with the parent's
  variables ([variables](https://docs.gitlab.com/ci/variables/),
  [MR pipelines](https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/)).
- **GitHub**: pull requests from branches of the same repository get its secrets, since write access
  means read access to every secret; fork pull requests get none. `pull_request_target` runs with
  the base repository's secrets and a write token: never check out or run pull request code in it
  ([secure use](https://docs.github.com/en/actions/reference/security/secure-use)).
- **Forgejo**: the same split (no secrets for fork heads, secrets for same-repository branches), and
  `pull_request_target` likewise carries the base secrets and a write token
  ([security](https://forgejo.org/docs/latest/user/actions/security-pull-request/)).
- **Bots and webhook listeners on the forge** (which token may write MR notes, labels and edits;
  signed, deduplicated webhooks; untrusted text written through the API): the forge-agents skill.

## Traps

- Generator output that depends on the developer's machine (Boost's Herd section) is false in a
  sandbox.
- OpenHands `pre-commit.sh` is deprecated for quality gates; use its Stop hooks.
- A Copilot or Cursor setup change merged without a run proves nothing: trigger one task after
  merging and read its setup log.
- Verify by running one probe task headless in a clean container: did the agent run the
  done-commands, and did it stall on a prompt or a blocked host?
