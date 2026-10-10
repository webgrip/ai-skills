# Layering and distribution across levels

## Mechanism per level

| Level | Claude Code | Codex / opencode | Cursor | Copilot |
|---|---|---|---|---|
| Org, behaviour | managed `claudeMd` (server-managed to reach cloud sessions), or a plugin SessionStart hook without MDM | `~/.codex/AGENTS.md` via dotfiles; opencode `instructions` | enforced Team Rule | org instructions (GitHub.com; VS Code needs `organizationInstructions.enabled`) |
| Org, enforcement | managed `permissions.deny`, hooks, `strictKnownMarketplaces` | sandbox / approval config | — | managed settings (enterprise `.github-private` repo, MDM or a root-owned file; permissions, MCP allow/deny lists, sandbox, telemetry), rulesets, CI |
| Platform / stack | plugin in a private marketplace (`extraKnownMarketplaces` + `enabledPlugins`), package guideline, generator source | same skills in `.agents/skills` | plugin | `.github-private/agents` |
| Team | own plugin; `claudeMdExcludes` for other teams' packages | nested `AGENTS.md` | optional Team Rule | `applyTo` instructions |
| Repo | `AGENTS.md` + `CLAUDE.md` = `@AGENTS.md` | `AGENTS.md` | `AGENTS.md` | `AGENTS.md`, `copilot-instructions.md` |
| Package / path | nested file, `.claude/rules` `paths:` | nested `AGENTS.md` | nested / globs | `.instructions.md` `applyTo` |
| Client (agency) | ancestor directory per client (`~/clients/<client>/CLAUDE.md`); client rules stay in the client repo | `CODEX_HOME` per client | separate workspace | client org settings |
| Person | `~/.claude/CLAUDE.md`, `CLAUDE.local.md` | `~/.codex` | User Rules | personal instructions |

Sources: [memory](https://code.claude.com/docs/en/memory),
[large codebases](https://code.claude.com/docs/en/large-codebases),
[plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces),
[Cursor rules](https://cursor.com/docs/context/rules),
[Copilot customization](https://docs.github.com/en/copilot/concepts/prompting/response-customization),
[Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md).

An organisation that runs several agent families needs one managed policy per family. Copilot's
managed settings combine their sources most-restrictively; Claude Code's managed settings outrank
every other layer ([security.md](security.md#sandbox-and-managed-settings)).

## Precedence differs per tool

| Tool | Rule |
|---|---|
| Claude Code | concatenated root → cwd; "Claude may follow either one" on conflict |
| Codex | concatenated, closer wins by position; `AGENTS.override.md` replaces its level (Codex only) |
| Cursor | Team > Project > User |
| Copilot | Personal > path-specific > repo > `AGENTS.md` > Org |

The same rule on two levels resolves differently per tool. One owner per rule, on one level.

## Distribution, in order of preference

1. Managed settings or a plugin/marketplace: updated centrally, no copies.
2. A generator (package guideline, Nx, rulesync) with a CI drift check.
3. A template, submodule or copied file: drifts from day one; needs the drift check most.

A stack's agent material (guidelines, skills, the instruction check and a CI template) ships best
as one package of its own, not as a passenger in a package another team owns; package layout for
Laravel Boost: [generators.md](generators.md#packages-and-boost). Smoke-test every release in a
throwaway app: install the package from a path repository that copies rather than symlinks
(`"options": {"symlink": false}`), allow its plugin, check the plugin output, `boost.json` and the
generated files, then run the check clean and once after a hand edit inside the generated block.
The smoke test catches a generator release that changes its output before any consumer does.

## Pitfalls

- A `CLAUDE.md` at a plugin root is never loaded; a plugin carries always-on text through a
  SessionStart hook or a skill.
- Plugin hooks, user-scope MCP servers and telemetry variables in `~/.claude/settings.json` apply
  in every repo; an ancestor-directory `CLAUDE.md` scopes instructions by directory, but these are
  not scoped by it.
- Project `.claude/settings.json` is not inherited from parent directories (unlike `CLAUDE.md`);
  monorepo packages need their own.
- Marketplaces and `permissions.allow` wait for folder trust; a fresh clone has no plugins until
  trusted.
- On-device managed files do not reach cloud sessions; use server-managed settings there.
- An agency's own rules never go into a client repo; the client's rules never go into the agency
  layer. Scope both by directory.
