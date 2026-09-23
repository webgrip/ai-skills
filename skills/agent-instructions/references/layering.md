# Layering and distribution across levels

## Mechanism per level

| Level | Claude Code | Codex / opencode | Cursor | Copilot |
|---|---|---|---|---|
| Org, behaviour | managed `claudeMd` (server-managed to reach cloud sessions), or a plugin SessionStart hook without MDM | `~/.codex/AGENTS.md` via dotfiles; opencode `instructions` | enforced Team Rule | org instructions (GitHub.com; VS Code needs `organizationInstructions.enabled`) |
| Org, enforcement | managed `permissions.deny`, hooks, `strictKnownMarketplaces` | sandbox / approval config | — | rulesets, CI |
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

## Pitfalls

- A `CLAUDE.md` at a plugin root is never loaded; a plugin carries always-on text through a
  SessionStart hook or a skill.
- Project `.claude/settings.json` is not inherited from parent directories (unlike `CLAUDE.md`);
  monorepo packages need their own.
- Marketplaces and `permissions.allow` wait for folder trust; a fresh clone has no plugins until
  trusted.
- On-device managed files do not reach cloud sessions; use server-managed settings there.
- An agency's own rules never go into a client repo; the client's rules never go into the agency
  layer. Scope both by directory.
