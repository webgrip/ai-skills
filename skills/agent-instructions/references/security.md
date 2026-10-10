# Security of instruction files and agent config

Instruction files, skills, hooks and MCP config are executable in effect: they steer an agent
that runs commands with your privileges. Review them like code.

## Contents
- [Threat model](#threat-model)
- [Threats](#threats)
- [Sandbox and managed settings](#sandbox-and-managed-settings)
- [Least privilege: an infrastructure repo](#least-privilege-an-infrastructure-repo)
- [Data sent to AI vendors](#data-sent-to-ai-vendors)
- [Review checklist](#review-checklist)
- [Before the first session in an unknown repo](#before-the-first-session-in-an-unknown-repo)

## Threat model

An ordinary developer session holds all three legs of the
[lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/): private data (code,
`.env`, tokens), untrusted content (issues, pull request text, dependencies, a cloned repo's
instruction files) and a way to send data out (web fetch, `curl`, an image URL, an MCP server).
Cut at least one leg per surface, usually the outbound one. Treat skills, MCP servers and editor
extensions as supply chain: pin them, scan them, and re-approve them when their config changes.

## Threats

| Vector | Example | Mitigation |
|---|---|---|
| Invisible Unicode | "Rules File Backdoor": zero-width / bidi characters hide instructions in `.cursorrules` and Copilot files ([Pillar](https://www.pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents)); tag characters U+E0000–E007F ("ASCII smuggling") | reject the whole class in CI (`measure.py` flags it; U+200D inside an emoji sequence passes, and U+00A0 is not in the class) |
| Injection via a cloned repo | an unknown repo's `AGENTS.md`/`CLAUDE.md` loads at launch as trusted context; payloads hide in HTML comments other tools keep | read instruction files before the first session in an unknown repo |
| Untrusted text the agent reads | a public issue read through the GitHub MCP server made an agent leak private repositories (Invariant Labs, 2025); a hidden prompt in a merge request made GitLab Duo leak source through an image URL (2025) | agents triggered only by people with write access; no outbound channel on surfaces that read untrusted text |
| Project settings run code | a `SessionStart` hook ran before the trust dialog (CVE-2025-59536); `ANTHROPIC_BASE_URL` in project `env` leaked the API key (CVE-2026-21852) ([Check Point](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/)) | keep tools current (managed `requiredMinimumVersion`); treat `hooks`/`env` changes as code changes |
| Repo MCP config | `.mcp.json` + `enableAllProjectMcpServers: true`: one Enter starts the attacker's server ([Adversa](https://adversa.ai/blog/trustfall-coding-agent-security-flaw-rce-claude-cursor-gemini-cli-copilot/)); an approved MCP entry swapped for another command afterwards (Cursor, CVE-2025-54136) | never commit that flag; allowlist servers in managed settings; re-approve on any change |
| Unpinned MCP packages | `npx -y @scope/server` fetches latest on every start (9.8 % of 2,660 setups, [arXiv 2609.07360](https://arxiv.org/abs/2609.07360)) | pin `pkg@x.y.z` |
| Broad pre-approval | `Bash(python:*)`, `Bash(node:*)` look narrow and run anything (3.1 %); skills with unrestricted Bash in `allowed-tools` (3.8 %) | no interpreter, shell or `*` in `permissions.allow` |
| Malicious skills | 13.4 % of 3,984 public skills had a critical issue (malware, prompt injection, exposed secrets), 76 with confirmed malicious payloads ([Snyk ToxicSkills](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/)); payloads in example code the agent copies ([arXiv 2605.11418](https://arxiv.org/abs/2605.11418)) | vendor and pin skills; read their scripts, not only `SKILL.md` |
| Installs that drive local agents | a compromised npm package's postinstall ran the installed AI CLIs with permission checks disabled to hunt for secrets (Nx "s1ngularity", 2025) | managed `permissions.disableBypassPermissionsMode`; no long-lived tokens in the shell environment |
| Read-only data tools | a database MCP tool that allows only SELECT still pipes personal data into the model, and accepts any configured connection name | a read-only user on anonymised data; no production connection configured where an agent can name it |
| Dev-tool packages outside local | Laravel Boost runs when the environment is local **or** `APP_DEBUG=true`, and its browser-log route takes unauthenticated POSTs | no dev dependencies in review or debug images that run with debug on; read a dev tool's routes and middleware before installing it |
| External imports and symlinks | an `@import` or symlinked rule leaving the repo widens the trust boundary | review any new external import |
| Secrets in instructions | tokens, internal hostnames, IPs pasted as "context" reach every agent and log | secret scanning in the same gate |
| Headless runs | no trust dialog with `-p`, so CI on fork PRs loads whatever the fork ships ([docs](https://code.claude.com/docs/en/security)) | do not run agents with repo config from untrusted forks |

## Sandbox and managed settings

Source: [sandboxing](https://code.claude.com/docs/en/sandboxing),
[settings](https://code.claude.com/docs/en/settings-reference).

- Claude Code's sandbox covers **Bash only**. Read, Edit, Write, WebFetch and MCP tools follow
  permission rules: a `sandbox.filesystem.denyRead` entry does not stop the Read tool, and
  `sandbox.network.allowedDomains` does not limit WebFetch. Pair each sandbox entry with a
  `permissions.deny` rule.
- If the sandbox cannot start, Claude Code runs commands **unsandboxed** by default. Set
  `sandbox.failIfUnavailable: true` where the sandbox is a security gate, and
  `sandbox.allowUnsandboxedCommands: false` so a command cannot ask to leave it. Native Windows has no
  sandbox; WSL2 does.
- Ship the policy as managed settings (`/Library/Application Support/ClaudeCode/managed-settings.json`,
  `/etc/claude-code/managed-settings.json`, or server-managed); they outrank `--settings`, local,
  project and user settings. Keys worth setting: `permissions.disableBypassPermissionsMode`,
  `allowManagedPermissionRulesOnly`, `allowManagedHooksOnly`, `strictKnownMarketplaces`,
  `requiredMinimumVersion`.
- `allowedMcpServers` entries match by `serverName`, `serverCommand` or `serverUrl`. A name is
  whatever a repo's `.mcp.json` calls its server, so allowlist by command or URL; once the list has
  a `serverCommand` (or `serverUrl`) entry, a name no longer admits that kind of server. Add
  `allowManagedMcpServersOnly`.

## Least privilege: an infrastructure repo

- Allow only read-only subcommands, and leave out the read-only ones that print secrets:

  ```json
  {
    "permissions": {
      "allow": ["Bash(kubectl get pods*)", "Bash(kubectl describe *)", "Bash(kubectl logs *)", "Bash(git diff *)", "Bash(git log *)"],
      "deny": ["Bash(kubectl get secret*)", "Read(**/*.key)", "Read(**/kubeconfig)", "Read(**/.env)"]
    }
  }
  ```

- Hooks for a destructive-command guard and a secret guard, a SessionStart snapshot of repo state,
  and manifest validation. When a hook validates in a relaxed mode, run the check by hand in that
  same mode.
- Keep learnings in `docs/` rather than agent memory; such repos often forbid memory outright.

## Data sent to AI vendors

Client or employer code goes only to commercial plans with a data processing agreement and no
training on your data; consumer plans differ on both. Before sending more (tickets, MCP context,
review bots), confirm in writing the vendor's processing region, retention, sub-processors and fit
with each client contract. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` disables `/feedback`,
which uploads the transcript.

## Review checklist

- CODEOWNERS covers `CLAUDE.md`, `AGENTS.md`, `.claude/**`, `.mcp.json`, `.cursor/**`,
  `.github/copilot-instructions.md`, `.ai/**`, `**/SKILL.md`.
- The diff was checked for hidden characters (`measure.py --security-only` passes).
- No new `hooks`, `env`, `apiKeyHelper`, `*_BASE_URL`, `enableAllProjectMcpServers` without a
  written reason.
- New or changed MCP servers are pinned, their source named, and re-approved.
- No interpreter, shell or `*` in `permissions.allow`; minimal `allowed-tools` in skills.
- No tracked `.claude/settings.local.json`.
- No text telling the agent to fetch and run code (`curl … | sh`, `eval`, base64 blobs).
- No imperatives hidden in HTML comments; no new external `@import` or out-of-repo symlink.
- No secrets, internal hostnames or IPs.

## Before the first session in an unknown repo

```bash
python3 scripts/measure.py --security-only --fail-on warn <repo>
```

Read every flagged file before starting an agent there. Secret handling itself belongs to a
secrets skill or scanner; the regex here is a backstop.
