# Instructions for unattended agents

Agentic runs (cloud agents, CI, headless) change what the instruction file can promise. Split the
work three ways: a **setup file** builds the machine, the **instruction file** says how to verify,
a **Stop hook or CI** enforces it. Machine building never goes in the instruction file.

## Per tool

| Tool | Setup | Instructions | Enforcement |
|---|---|---|---|
| Codex cloud ([docs](https://learn.chatgpt.com/docs/environments/cloud-environment)) | setup + maintenance script (UI) | `AGENTS.md`, 32 KiB | none; the agent runs the "programmatic checks" listed in `AGENTS.md` |
| Copilot cloud agent ([docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment)) | `.github/workflows/copilot-setup-steps.yml`, job `copilot-setup-steps`, default branch, ≤ 59 min | `copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md` | PR CI |
| OpenHands ([docs](https://docs.openhands.dev/openhands/usage/customization/repository)) | `.openhands/setup.sh`, every session | `AGENTS.md`, skills | `.openhands/hooks.json` Stop hook (exit 2) |
| Claude Code cloud ([docs](https://code.claude.com/docs/en/cloud-environments)) | setup script (must exit 0, ~5 min) + repo SessionStart hook | `CLAUDE.md` → `@AGENTS.md` | Stop hook |
| Claude Code `-p`, Action, SDK ([headless](https://code.claude.com/docs/en/headless)) | workflow steps before the call | `CLAUDE.md` — **not with `--bare`**, not with SDK `settingSources: []` | Stop hook (not with `--bare`), CI |
| Cursor cloud ([docs](https://cursor.com/docs/cloud-agent/setup)) | `.cursor/environment.json` (`install`, `start`, `terminals`) | `.cursor/rules`, `AGENTS.md` | none documented |
| Jules ([docs](https://jules.google/docs/environment/)) | setup script + snapshot (UI) | `AGENTS.md` | none documented |
| Devin ([docs](https://docs.devin.ai/onboard-devin/repo-setup)) | blueprint → snapshot, incl. lint/test commands | knowledge, `AGENTS.md` | blueprint commands |

## What changes without a human

- Nobody answers a question or a permission prompt; a denied step fails or loops.
- Secrets are often removed before the agent phase (Codex) and exports in setup do not reach the
  agent; the network is allowlisted (Copilot firewall, Codex off by default).
- Snapshots keep files, not processes: databases and `docker compose` stacks start each session.
- A failed setup step can go unnoticed: Copilot skips the rest and starts anyway.
- The instruction file may not load at all (`claude -p --bare`, SDK `settingSources: []`), so a
  must-hold check lives in a Stop hook or CI, never only in prose.

## What the instruction file adds for them

1. **Definition of done**: the exact commands, narrowest first, with expected runtime
   ("`php artisan test --filter=Quotation` ~2 min; the full suite is CI's job"). Codex treats
   listed checks as mandatory, so list only what should always run.
2. **Environment facts an agent cannot guess**, one line each: which services must run and the
   command that starts them (or "not available here: skip browser tests"), known flaky or
   network-bound tests, the variable that marks a sandbox (`CLAUDE_CODE_REMOTE=true`).
3. **Where secrets come from**, never their values.

## Traps

- Generator output that depends on the developer's machine (Boost's Herd section) is false in a
  sandbox.
- OpenHands `pre-commit.sh` is deprecated for quality gates; use its Stop hooks.
- Verify by running one probe task headless in a clean container: did the agent run the
  done-commands, and did it stall on a prompt or a blocked host?
