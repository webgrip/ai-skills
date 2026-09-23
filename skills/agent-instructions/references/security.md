# Security of instruction files and agent config

Instruction files, skills, hooks and MCP config are executable in effect: they steer an agent
that runs commands with your privileges. Review them like code.

## Threats

| Vector | Example | Mitigation |
|---|---|---|
| Invisible Unicode | "Rules File Backdoor": zero-width / bidi characters hide instructions in `.cursorrules` and Copilot files ([Pillar](https://www.pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents)); tag characters U+E0000–E007F ("ASCII smuggling") | reject the whole class in CI (`measure.py` flags it) |
| Injection via a cloned repo | an unknown repo's `AGENTS.md`/`CLAUDE.md` loads at launch as trusted context; payloads hide in HTML comments other tools keep | read instruction files before the first session in an unknown repo |
| Project settings run code | a `SessionStart` hook ran before the trust dialog (CVE-2025-59536); `ANTHROPIC_BASE_URL` in project `env` leaked the API key (CVE-2026-21852) ([Check Point](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/)) | keep tools current; treat `hooks`/`env` changes as code changes |
| Repo MCP config | `.mcp.json` + `enableAllProjectMcpServers: true`: one Enter starts the attacker's server ([Adversa](https://adversa.ai/blog/trustfall-coding-agent-security-flaw-rce-claude-cursor-gemini-cli-copilot/)) | never commit that flag; allowlist servers in managed settings |
| Unpinned MCP packages | `npx -y @scope/server` fetches latest on every start (9.8 % of 2,660 setups, [arXiv 2609.07360](https://arxiv.org/abs/2609.07360)) | pin `pkg@x.y.z` |
| Broad pre-approval | `Bash(python:*)`, `Bash(node:*)` look narrow and run anything (3.1 %); skills with unrestricted Bash in `allowed-tools` (3.8 %) | no interpreter, shell or `*` in `permissions.allow` |
| Malicious skills | prompt injection in 36 % of scanned public skills ([Snyk](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/)); payloads in example code the agent copies ([arXiv 2605.11418](https://arxiv.org/abs/2605.11418)) | vendor and pin skills; read their scripts, not only `SKILL.md` |
| External imports and symlinks | an `@import` or symlinked rule leaving the repo widens the trust boundary | review any new external import |
| Secrets in instructions | tokens, internal hostnames, IPs pasted as "context" reach every agent and log | secret scanning in the same gate |
| Headless runs | no trust dialog with `-p`, so CI on fork PRs loads whatever the fork ships ([docs](https://code.claude.com/docs/en/security)) | do not run agents with repo config from untrusted forks |

## Review checklist

- CODEOWNERS covers `CLAUDE.md`, `AGENTS.md`, `.claude/**`, `.mcp.json`, `.cursor/**`,
  `.github/copilot-instructions.md`, `.ai/**`, `**/SKILL.md`.
- The diff was checked for hidden characters (`measure.py --security-only` passes).
- No new `hooks`, `env`, `apiKeyHelper`, `*_BASE_URL`, `enableAllProjectMcpServers` without a
  written reason.
- New MCP servers are pinned and their source named.
- No interpreter, shell or `*` in `permissions.allow`.
- No text telling the agent to fetch and run code (`curl … | sh`, `eval`, base64 blobs).
- No imperatives hidden in HTML comments; no new external `@import` or out-of-repo symlink.
- No secrets, internal hostnames or IPs.

## Before the first session in an unknown repo

```bash
python3 scripts/measure.py --security-only --fail-on warn <repo>
```

Read every flagged file before starting an agent there. Secret handling itself belongs to a
secrets skill or scanner; the regex here is a backstop.
