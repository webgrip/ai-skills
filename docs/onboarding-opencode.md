# opencode at webgrip — onboarding

Welcome. We use [opencode](https://opencode.ai) as the standard coding agent,
with the org's skills, guardrails, and conventions installed by one script.
Fifteen minutes from zero to a working session.

## 1. What changed and why (one paragraph)

We migrated from Claude Code to opencode as the team harness: same
Claude models, same skills (the SKILL.md format is portable), but an open
tool we can configure org-wide — shared agents, permission profiles, a
secrets guard, and MCP servers — from one repo. Delivery discipline is
unchanged: repos keep their `AGENTS.md`, and spec-driven work still runs
through OpenSpec (`/opsx-propose` → `/opsx-apply`). Auth routes through the
webgrip **LiteLLM plane** (metered, per-person virtual key, VPN required) —
**do [docs/auth.md](auth.md) §1 before your first session** (mint your key).

## 2. Install

```bash
# opencode v2 beta — EXACT pin, the binary is `opencode2` until GA.
# Never install @next: the beta churns daily and self-updates unless the
# org config's autoupdate:false is in place (the bootstrap installs it).
npm i -g @opencode-ai/cli@0.0.0-next-15495

# the webgrip estate: skills + agents + guardrails + org config
git clone https://forgejo.webgrip.dev/webgrip/ai-skills.git
bash ai-skills/scripts/install_opencode.sh --profile junior   # or senior

# auth: mint a personal LiteLLM virtual key + export it (docs/auth.md §1)
export WEBGRIP_LLM_KEY="sk-..."     # VPN/LAN required; the org default routes here
```

(mise still pins per-repo toolchains — repos carry `"npm:@opencode-ai/cli"`
in `mise.toml`; the global install above is for everywhere else.)

Re-run the script any time to update. It's idempotent and never overwrites
config keys you added yourself.

## 3. Your first session

```bash
cd <a migrated repo, e.g. erfbeeld>
mise install        # repo-pinned toolchain, incl. opencode2 + openspec
opencode2
```

Why v2 is worth the beta label: every session **snapshots your workspace —
`/revert` undoes a bad edit run in one command** (juniors: experiment
freely, this is your net); `/connect` manages credentials; there's a VS
Code extension (`sst-dev.opencode-v2`) and a desktop app if terminals
aren't your thing.

Try, in order:

1. `what skills do you have available?` — you should see the org five
   (adr-writer, domain-language, harvest-knowledge, skillsmith,
   product-owner) plus the repo's own.
2. `what should we work on next?` — the product-owner skill reads the team
   board (LAN/VPN required).
3. A real change: `/opsx-propose` a small idea → review the artifacts under
   `openspec/changes/` → `/opsx-apply`.

## 4. The guardrails (and why they'll sometimes say no)

- Your **junior profile** asks before edits and most shell commands, and
  refuses `git push`, `sudo`, `kubectl`, `sops`. That's a safety net for
  *accidents*, not a verdict on you — ask a senior to switch your profile
  when the training wheels start slowing you down.
- Permissions are an **ordered rule list — the last matching rule wins**.
  The org deny floor (sops/sudo) is always last, so nothing you add above
  it can unlock those. File *reads* never prompt (explicit read-tier
  allows). The agent asking before leaving the repo (`external_directory`)
  is expected — answer honestly.
- The **starter agent** (`starter`) enforces the golden path: plan first,
  small diffs, verify before done. Use it until the flow is second nature.
- **guard-secrets** blocks plaintext-secret writes org-wide (decrypted
  artifacts, unencrypted `*.sops.yaml`, gitleaks hits) — for everyone,
  seniors included.

## 5. Local / free model (Ollama)

No Anthropic quota, no cost, fully offline — the fallback lane and a fine
retest/scratch driver:

```bash
brew install ollama && brew services start ollama
ollama pull qwen3:8b            # ~5GB; good on 16GB+ Apple Silicon
```

The org config ships an `ollama` provider (baseURL `http://localhost:11434/v1`).
Use it per-run — `opencode2 run -m ollama/qwen3:8b "…"` — or pick it in the
TUI model switcher. Local models are weaker at multi-step tool use; treat
them as a floor, not a replacement for the Claude lane.

> **⚠ Open item — guard-secrets on v2 is NOT yet confirmed to block.** In v1
> the hook threw and the tool aborted; v2's plugin docs don't document a
> block mechanism for `tool.hook("execute.before")`, and an empirical write
> to a `*.sops.yaml` was NOT prevented on 0.0.0-next-15495. The arg-shape
> fix landed (probe-verified `{path, content}` at `input.input`), but until
> the block path is confirmed, **do not rely on guard-secrets as a control
> on v2** — treat SOPS/secret discipline as human-enforced. Tracked for the
> next bump.

## 6. Hard rules

- **Never** point work repos at the personal Max bridge alternative configs —
  auth policy lives in [docs/auth.md](auth.md).
- **Never** paste secrets, tokens, or customer data into a prompt.
- **Never** force-push or bypass review because "the agent said it's fine".
- Repo conventions (`AGENTS.md`) always win over your own preferences.

## 7. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `vikunja` MCP fails to attach ("SSE error … 400") | Known gateway quirk (returns 400 where MCP wants 405) — instance-ops fix pending. The PO skill still works: it falls back to its bundled protocol client. Also: are you on LAN/VPN? |
| MCP `401/403` | Instance token expired/under-scoped — ping ops (runbook), not a local problem. |
| Bridge errors / model refuses to auth | `claude auth` logged in? Bridge broken org-wide? Flip to the API-key fallback (auth.md §2) and report it. |
| A skill is missing | Re-run `install_opencode.sh`; check `ls ~/.config/opencode/skills`. |
| `opencode2`/`openspec` not found in a repo | `mise install` in the repo; `mise trust` if prompted. |
| `opencode2` version ≠ the estate pin | The beta self-updates unless `autoupdate:false` is merged — re-run the installer, then `npm i -g @opencode-ai/cli@<pin>` (the installer prints the pin). |
| guard-secrets didn't block | Re-run the installer (plugin symlink + `@opencode-ai/plugin` dep must match the binary generation). |
| Blocked writing a `*.sops.yaml` | Working as intended — edit plaintext elsewhere, `sops --encrypt`, or leave a `*.template.yaml` for a human. |

## 8. Version bumps (Ryan-only runbook)

The estate pins an EXACT beta build (`OPENCODE_VERSION` in
`scripts/install_opencode.sh` is the single source). To bump:

1. `npm view @opencode-ai/cli@next version` + read the release notes
   (breaking-change scan: config keys, plugin API, permission actions).
2. Canary on Ryan's machine: `npm i -g @opencode-ai/cli@<new>` → run the
   30-min gauntlet checklist (bridge round-trip, guard blocks, skills
   count, vikunja MCP, one opsx command, `opencode2 debug agents` rule
   dump for the floor).
3. Bump the estate in one commit each: this repo (`OPENCODE_VERSION` +
   org `_comment` + docs), erfbeeld `mise.toml`+`mise.lock`, and every other repo that pins opencode.
   One-line announcement in the team channel.
4. Gauntlet fails → stay pinned, file/watch upstream, retry next beta.

## 9. Where things live

| Thing | Place |
|---|---|
| Org skills/agents/guardrails/config | this repo, installed to `~/.config/opencode/` |
| Your personal overrides | `~/.config/opencode/opencode.json` (yours survive re-runs) |
| Per-repo config (MCP, permissions) | `<repo>/opencode.json` + `.opencode/` |
| Auth story | [docs/auth.md](auth.md) |
| Board workflow (tickets, DoR, claims) | the `product-owner` skill |
