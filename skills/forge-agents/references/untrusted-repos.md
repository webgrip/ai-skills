# Agents on repos you do not control

A customer repo, a fork, a third-party dependency, an MR branch anyone can push: its instruction
files, settings, hooks, MCP config and plugin directories are input to your run, not instructions
for it. Before the first run, scan it with the `agent-instructions` skill's
`measure.py --security-only`; which repo files change each cloud agent's posture is in that skill's
`references/unattended.md`.

## Contents

- [Claude Code: what loads and what each flag removes](#claude-code-what-loads-and-what-each-flag-removes)
- [Other harnesses](#other-harnesses)
- [Runner hygiene](#runner-hygiene)
- [Sandboxes compared](#sandboxes-compared)

## Claude Code: what loads and what each flag removes

Source: [permissions, "What runs before you trust a folder"](https://code.claude.com/docs/en/permissions),
[CLI reference](https://code.claude.com/docs/en/cli-reference),
[setting sources](https://code.claude.com/docs/en/agent-sdk/claude-code-features).

`claude -p` and the Agent SDK never show the workspace-trust dialog. From the repo they:

| Repo content | Used in `-p` |
|---|---|
| hooks in settings files, the `env` block, helpers such as `apiKeyHelper`, a project skill's hooks and `allowed-tools` | yes |
| `.mcp.json` servers, approved or not | connected without asking |
| `permissions.allow` and `additionalDirectories` in `.claude/settings.json` | no (a stderr warning) |
| subagent frontmatter hooks and inline `mcpServers`, project `@skills-dir` plugins, `extraKnownMarketplaces` | no |
| `CLAUDE.md`, `.claude/rules`, project skills, commands and subagents | yes, while the project setting source loads |

| Flag | Removes | Leaves |
|---|---|---|
| `--setting-sources user` | the project source: settings files and their hooks, `.mcp.json`, `CLAUDE.md` in the checkout and its parents, `.claude/rules`, project skills, commands and subagents | user settings, `~/.claude.json`, auto memory, claude.ai connectors |
| `--bare` | hooks, skills, commands, subagents, plugins, `.mcp.json`, auto memory, `CLAUDE.md` | the project's `env` block and helpers such as `awsAuthRefresh`; `apiKeyHelper` is read only from `--settings` |
| `--settings '{"disableAllHooks":true}'` | hooks for this run; command-line settings outrank project settings, so the repo cannot switch them back on | `env`, helpers, MCP |
| `--strict-mcp-config --mcp-config f.json` | every MCP server not in `f.json`, claude.ai connectors included | settings |
| `disabledMcpjsonServers` (settings key) | the named `.mcp.json` servers in every session type | everything else |
| `--restricted` | user and project settings (only managed settings and `--settings` load); command-running tools and WebFetch unless named in `--tools`; `bypassPermissions` | file tools inside the working directories |

- Use `--setting-sources user` plus the hooks-off `--settings` plus `--strict-mcp-config` for an
  agent that edits and runs code. Use `--restricted` for a review or evaluation pass that must not
  execute anything from the repo.
- Give each run its own configuration directory (`CLAUDE_CONFIG_DIR` or a dedicated `HOME`) so
  "user" settings are the runner's, not a person's, and set `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`:
  auto memory and `~/.claude.json` load regardless of the setting sources. Several tenants on one
  host each get their own filesystem; the SDK form is `settingSources: []`.
- `--permission-mode bypassPermissions` only where the sandbox is disposable and every credential
  in it is already scoped to this run. Elsewhere pass `--allowedTools` with the minimum, and
  `--permission-prompts none` where the installed version has it, so a prompt is denied rather
  than waited on.
- Turn off what you are not paying for: a gateway may price the advisor tool at the executor
  model's rate (`CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`).
- Return the outcome through a file the runner names (a drop-box path in an environment
  variable), not by parsing the transcript.

## Other harnesses

- **ACP (Agent Client Protocol) agents:** an empty `mcpServers` list on `session/new` withholds
  only the client's servers. The agent can still load the repo's own config: goose reads
  `.agents/plugins/`, qwen-code reads `.qwen/settings.json`. Check each agent's docs for a flag
  that ignores project config.
- **Cursor:** a workspace `.cursor/sandbox.json` outranks `~/.cursor/sandbox.json` and can set
  `"type": "insecure_none"` or widen `networkPolicy`; `.cursor/hooks.json` and
  `.cursor/environment.json` also come from the repo
  ([sandbox reference](https://cursor.com/docs/reference/sandbox)).
- **No ignore flag:** move the harness's repo config out of the checkout before the run and
  restore it before the diff is taken, and send a diff that touches agent config or CI files to a
  human.

## Runner hygiene

- **Environment:** an allowlist of variables, never the runner's whole environment.
- **Credentials:** the harness sees placeholders; a forge-token proxy and a model-key proxy outside
  the sandbox swap in the real values. The worker refuses to start while it could be debugged by a
  co-tenant (on Linux, while `CAP_SYS_PTRACE` is held) and is not dumpable.
- **Leaks:** a run whose output contains a credential is refused, not published, and raises an
  alert.
- **Pushes:** the forge proxy accepts pushes to the run's own branch only.
- **Checks belong to the operator:** verification commands come from operator config, never from
  the repo, and re-run after the agent finishes, without credentials.
- **Instruction files are flagged:** hash the repo's `AGENTS.md`, `CLAUDE.md`, `.mcp.json`,
  `.claude/` and `.agents/`, and name them in the prompt as repo content the agent must not obey
  over the task.

## Sandboxes compared

The table answers the four questions in [SKILL.md](../SKILL.md#untrusted-repos) as far as each
vendor documents them. An editor-level sandbox can cover only one of the harnesses it hosts.

| Harness | Mechanism | Network | Gaps to check |
|---|---|---|---|
| Claude Code ([docs](https://code.claude.com/docs/en/sandboxing)) | Seatbelt on macOS, bubblewrap on Linux and WSL2 | allowlist proxy for sandboxed Bash | covers Bash only (file tools and MCP follow permission rules); runs unsandboxed when the sandbox cannot start unless `sandbox.failIfUnavailable` is set (the `agent-instructions` skill, `references/security.md`) |
| Codex ([docs](https://learn.chatgpt.com/docs/sandboxing)) | Seatbelt on macOS, bubblewrap on Linux and WSL2, a native Windows sandbox | per sandbox mode | modes `read-only`, `workspace-write` (local default), `danger-full-access`; full access is `danger-full-access` with approval policy `never` |
| Cursor ([docs](https://cursor.com/docs/reference/sandbox)) | OS sandbox configured by `sandbox.json` | `networkPolicy.default: "deny"` | the repo's `.cursor/sandbox.json` outranks the user's and can switch the sandbox off |
| Gemini CLI ([docs](https://geminicli.com/docs/cli/sandbox/)) | opt-in: `--sandbox`, `GEMINI_SANDBOX`, or `tools.sandbox`; Seatbelt, Docker or Podman, gVisor, LXC | the default Seatbelt profile `permissive-open` allows network | `security.toolSandboxing` isolates individual tool runs and can be turned off in settings |
| VS Code Agent Host ([docs](https://code.visualstudio.com/docs/agents/run/agent-sandboxing)) | `chat.agent.sandbox.enabled`, off by default | allowed even when on (`allowNetwork: true`); local network blocked | applies to the Agent Host's default Copilot SDK tools only, not the Local chat harness; `allowUnsandboxedCommands` defaults to true; "not a virtual machine or user-account boundary" |

For unattended runs on foreign code, put the harness inside a boundary you own (a disposable VM or
a container under a runtime sandbox such as gVisor) and treat the harness's own sandbox as a second
layer.
