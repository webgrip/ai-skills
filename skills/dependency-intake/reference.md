# Dependency intake — reference

- [Where usage hides](#where-usage-hides)
- [Fetching notes the PR body lacks](#fetching-notes-the-pr-body-lacks)
- [Questions per update](#questions-per-update)
- [Report shape](#report-shape)
- [PR comment shape](#pr-comment-shape)
- [Ticket draft shape](#ticket-draft-shape)

## Where usage hides

Search these besides the source tree. A handle that only appears in a lockfile is still in use.

| Ecosystem | Config and pins | Usage outside config |
|---|---|---|
| npm / pnpm / yarn | `package.json` (`packageManager`, `engines`, `devEngines`), `.npmrc`, `pnpm-workspace.yaml`, lockfile | `scripts`, CI steps, Dockerfiles, `corepack` calls |
| Python / uv / pip | `pyproject.toml` (`requires-python`, `[tool.uv]`, `[build-system]`), `.python-version`, `uv.lock`, `requirements*.txt`, constraints files | `uv run`/`uv sync` flags in task runners and CI, `UV_*` env |
| Go | `go.mod` (`go`, `toolchain`), `go.sum` | build tags, `GOFLAGS`, `//go:` directives |
| Tool managers (mise, asdf, aqua) | `mise.toml`, `.tool-versions`, `mise.lock`, nested per-app configs | CI action `version:` inputs, task definitions |
| Containers | `Dockerfile` `FROM`/`ARG`, compose files | build flags, `--platform`, runtime env |
| Helm / Kubernetes | `Chart.yaml` dependencies, `values*.yaml` | templates using a renamed value, CRD versions |
| CI actions | `uses:` pins and their `with:` inputs | shell steps that parse the tool's output |

Also search every place a team records a workaround, since those turn into **Workaround retires** verdicts:

- warning or lint allowlists (`*-allow.json`, `.eslintrc` overrides, `# noqa`, `--ignore` flags),
- bot rules with `allowedVersions`, `enabled: false` or a description naming an upstream issue,
- docs and runbooks saying "until", "upstream bug", "pinned because", "works around",
- patch files (`patches/`, `patchedDependencies`, `pnpm patch`, `go.mod` `replace`).

Output-parsing gates (warning scanners, log checks) break on wording changes nobody calls breaking: a new `WARN` line, a colour code, a renamed message.

## Fetching notes the PR body lacks

- GitHub release: `gh release view <tag> -R <owner>/<repo>`, or the releases API.
- npm: the package's `CHANGELOG.md` at the tag, or `npm view <pkg>@<version> repository` to find it.
- PyPI: the project URLs on `pypi.org/pypi/<pkg>/json` point at the changelog.
- Docker image: the source repo's release for the tag; a digest-only bump has no notes, so say so.
- A forge the bot cannot reach often yields a body with only a compare link; open the compare and read the commit subjects.

## Questions per update

1. Is it a 0.x minor, or does any note say breaking, removed, renamed or deprecated?
2. Did a default change (runtime version, colour, concurrency, cache format, strictness) for something we leave unpinned?
3. Does it fix something we carry a workaround, allowlist entry, version cap or patch for?
4. Does a new capability replace one of our own scripts, checks or wrappers?
5. Does it add supply-chain hardening we could switch on (permissions, hash checking, provenance, release-age policy)?
6. Does it change what an AI agent working in the repo loads or writes (instruction files, skill directories, agent-detecting env vars, generated files in the working tree)?
7. Does it reach our users: projects our product installs, builds or runs tools in, images we ship, SDKs we publish?
8. Does it invalidate a CI cache or change install or build time?
9. Does a doc, runbook or example name the old version or behaviour?
10. Is the grouped PR coherent, or should one update leave the group?
11. Did upstream ship several patch releases within days? Then the soak deserves to be longer.

## Report shape

1. **TL;DR**: per PR, mergeable or not and why, in one or two lines.
2. **Decisions**: numbered, each with its consequence, the case for and against, and a recommendation.
3. **Per update**: version range, then every non-noise verdict with its evidence (`path:line` or the counted absence) and any probe command with its exit code. End with the noise count.
4. **Ticket drafts**: title, problem, acceptance criteria and the release note they come from.
5. **Not verified**: what was inferred, skipped or unreachable, such as CI logs behind a login.

## PR comment shape

```markdown
**Dependency intake**: <holds the merge | safe to merge | safe to merge, follow-ups drafted>

| Update | Verdict | Evidence |
|---|---|---|
| uv 0.12.24 → 0.13.0 | Default shift: Python 3.15 | not reached: `.python-version` pins 3.12 |

Probes: `uv sync --frozen` with 0.13.0 on the locked tree, exit 0.
Follow-ups: <ticket links once created>
```

## Ticket draft shape

- **Title**: the outcome, not the dependency ("Agents in a Run see skills linked by the package manager").
- **Problem**: the release note quoted, and the `path:line` where it meets our code.
- **Acceptance criteria**: observable checks, including the probe that proves it.
- **Kind**: workaround removal, adoption, default pin, or product.
