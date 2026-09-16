# ai-skills

[![Release](https://forgejo.webgrip.dev/webgrip/ai-skills/actions/workflows/release.yml/badge.svg?branch=main)](https://forgejo.webgrip.dev/webgrip/ai-skills/actions?workflow=release.yml)

Webgrip's open-source Claude skills, shipped as one plugin marketplace hosted on [Forgejo](https://forgejo.webgrip.dev/webgrip/ai-skills). Each skill is its own plugin — install only what you want.

## Skills

| Skill | What it does |
|---|---|
| [adr-writer](skills/adr-writer) | Write, amend, and supersede MADR 4.0.0 Architecture Decision Records: bootstrap or adopt an ADR corpus, registry index kept in lock-step, append-only dated history, and a bundled CI-ready consistency validator. |
| [blog-writer](skills/blog-writer) | Turn project notes into technical blog posts developers read — evidence-first drafting, hook workshop, single-dimension edit sweeps with a de-AI-ify pass, fresh-reader testing, and per-platform syndication recipes (HN, LinkedIn, Substack, dev.to, Reddit, Lobsters). |
| [domain-language](skills/domain-language) | Define a project's ubiquitous language (terms, entities, rules, events) in `domain/model.yaml`; generate glossaries, entity docs with Mermaid diagrams, [Context Mapper](https://contextmapper.org) exports, a 0–10 model health score, and feature specs from it. |
| [guard-secrets](skills/guard-secrets) | A `PreToolUse` hook that blocks plaintext-secret leaks before an edit lands (no decrypted artifacts, SOPS stays ciphertext, gitleaks scan), plus the secrets-floor knowledge behind it — the Claude Code twin of the opencode guard-secrets plugin. |
| [harvest-knowledge](skills/harvest-knowledge) | Mine durable learnings out of Claude threads in three phases (distill → consolidate → synthesize) and land them as repo docs, CLAUDE.md rules, new skills, and memory updates. |
| [humanize](skills/humanize) | Detect, remove or prevent the tells of AI-generated writing in English and Dutch: 229 English and 251 Dutch catalog entries consolidated from the main open-source humanizers, the Wikipedia field guide and the published tell-lists, with a translationese layer for English-shaped Dutch that no upstream tool covers; four modes with fact and voice protection, a register tolerance table, and a dependency-free scanner whose 1,295 regexes are each measured against human prose. |
| [kpi-groomer](skills/kpi-groomer) | Define, groom and facilitate KPI sets that change decisions: complete definitions (formula, source, owner, baseline, the decision it changes), Goodhart speed/quality pairs, timeboxed team-owned KPI workshops, dashboard-as-artifact traceability, review-and-retire cadence, and an ethics gate for person-level metrics (SPACE, GDPR/works council). |
| [linkedin-post](skills/linkedin-post) | Get a LinkedIn post read: the 2026 ranking mechanics (link penalty, comments over likes, dwell time, personal profile over company page), the plain-text formatting the editor will not destroy on paste, accessible emphasis instead of Unicode pseudo-bold, and the posting window. |
| [product-owner](skills/product-owner) | Run any ticket board as product owner (Vikunja + ClickUp adapters, bundled `vikunja` MCP): a research-backed Definition of Ready, an agent-ready gate for AI-executed work, WIP anchored on review capacity, evidence-based closing, flow metrics with an SLE — and **Board contracts** as the extension seam: instance facts layer in from repo/user/org contract layers (template in `contracts.md`, philosophy in [docs/contract-pattern.md](docs/contract-pattern.md)) so orgs extend it without forking. Every major rule sourced in `rationale.md`. |
| [protocol-fit-research](skills/protocol-fit-research) | Answer "does this protocol matter to us?" with a parallel research fan-out (spec crawl, source-repo dig, ecosystem adoption plus explicit absence checks, local seam map), a verdict-led report separating maturity from fit, and a dossier, ledger row and watchlist item landed in the repo with falsifiable re-evaluation triggers. |
| [secrets-levels](skills/secrets-levels) | Place a secret at the right level of the estate and name the manifest that puts it there: floor (SOPS), vault (OpenBao), cluster (External Secrets), bridge (Forgejo Actions and Cloudflare Worker secrets), short-lived (OIDC, dynamic credentials, per-run tokens), person (a laptop). Decision by origin, then by consumer; the placement half of the secrets model, with `guard-secrets` as the enforcement half. |
| [skill-usage](skills/skill-usage) | Local skill-usage telemetry: a `PostToolUse` hook logs every skill invocation to a local JSONL (no network), and the skill reports which skills are used, dead, or undertriggering — the private answer to "which of our skills earn their keep?". |
| [skillsmith](skills/skillsmith) | Author, edit, and audit agent skills for token-efficient, high-trigger-accuracy ingestion: the skill loading/token cost model, description-as-router rules, cross-tool frontmatter portability, progressive disclosure, and eval methodology. |

## Install

**`npx skills` (recommended — every agent, not just Claude):** the flat `skills/` tree is the
vendor-neutral layout the cross-tool installers consume, so one command installs into 70+ agents
(Claude Code, opencode, Cursor, Codex, Copilot, Gemini CLI, …):

```bash
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git            # interactive
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git --all -g   # everything, user-level
npx skills update -g                                                       # pull latest
```

Skills land in `~/.agents/skills/` and are symlinked into each agent's skills dir
(`~/.claude/skills/`, opencode, …). They invoke **unprefixed** — `/domain-language`. Pinning,
lockfiles, and telemetry opt-out: [docs/DISTRIBUTION.md](docs/DISTRIBUTION.md).

> **The CLI ships only the SKILL.md trees.** A skill's bundled `hooks/hooks.json`
> (`guard-secrets`, `skill-usage`) or `.mcp.json` (`product-owner`) is copied but **not**
> auto-wired — register those by hand in your `settings.json` / `.mcp.json`, or use the plugin
> route below, which wires them for you.

**Claude Code plugin (only if you need the bundled hooks/MCP wired automatically):**

```
/plugin marketplace add https://forgejo.webgrip.dev/webgrip/ai-skills.git
/plugin install domain-language@ai-skills
```

**`webgrip` — the whole estate, namespaced.** The repo root is itself a plugin,
so one install loads every skill prefixed `webgrip:<skill>`:

```
/plugin marketplace add https://forgejo.webgrip.dev/webgrip/ai-skills.git
/plugin install webgrip@ai-skills
```

That prefix is the point: it lets this estate sit alongside **another estate
shipping same-named skills** (`adr-writer`, `skillsmith`, …) without the two
competing to trigger — you get `webgrip:adr-writer` next to the other's
`adr-writer`, and the agent can tell them apart. It matters because same-named
skills across estates encode *different org policy*.

The bundle wires the estate's hooks too — the `guard-secrets` PreToolUse block
and the `skill-usage` PostToolUse logger, re-declared in the root
[hooks/hooks.json](hooks/hooks.json) rooted at the repo instead of the skill
dir (a skill's own `hooks.json` resolves `${CLAUDE_PLUGIN_ROOT}` to that skill's
directory, which is wrong under the bundle). `check_manifests.py` fails if a
skill grows a hook the bundle doesn't mirror, so the bundle can't ship an
enforcement hook silently dead.

The bundle carries a repo-wide version that moves whenever *any* skill releases
— it has to, or installs never see the update — but it is deliberately **not
tagged**: `<skill>-v<X.Y.Z>` stays the only release tag and the only unit of
pinning. Take the bundle **or** per-skill plugins, never both; enabling `webgrip`
alongside `domain-language@ai-skills` loads that skill twice.

Updates arrive via `/plugin marketplace update ai-skills` whenever a version is bumped. Plugin
skills load at session start (not `/reload-skills`) and invoke **namespaced**:
`/domain-language:domain-language`. Don't run both routes for the same skill — it double-loads.

For a whole repo/team, commit both keys to the project's `.claude/settings.json` — the
marketplace source must be the git URL, not a local path, so teammates' machines can resolve it:

```json
{
  "extraKnownMarketplaces": {
    "ai-skills": {
      "source": { "source": "git", "url": "https://forgejo.webgrip.dev/webgrip/ai-skills.git" }
    }
  },
  "enabledPlugins": { "domain-language@ai-skills": true }
}
```

**Manual:** copy `skills/<name>/` into a project's `.claude/skills/` or your `~/.claude/skills/`.
opencode natively reads both, so this covers it with zero extra steps.

**Claude app / claude.ai:** grab the matching `<name>.skill` file from the [latest release](https://forgejo.webgrip.dev/webgrip/ai-skills/releases/latest) (or the [package registry](https://forgejo.webgrip.dev/webgrip/-/packages)), upload via Settings → Skills (or attach in a chat), and hit *Save skill*.

Some skills bundle Python scripts requiring PyYAML (`pip install pyyaml`); see each skill's folder for specifics.

## Repo layout

```
.claude-plugin/marketplace.json   # the catalog Claude Code reads — GENERATED, never hand-edited
.forgejo/workflows/               # Forgejo Actions: ci.yml (PRs), release.yml (main)
skills/<name>/                    # one dir per skill — and each dir IS its plugin
  SKILL.md                        #   the skill itself (+ scripts, assets, references, evals/)
  .claude-plugin/plugin.json      #   plugin manifest — the single source of truth
  test.sh                         #   optional plugin-specific tests (generic rules: lint)
scripts/new_skill.py              # scaffold a new skill
scripts/sync_marketplace.py       # regenerate marketplace.json from plugin manifests
scripts/lint_skills.py            # skill-quality rules for every plugin (CI)
scripts/check_manifests.py        # manifest structure checks (CI)
scripts/check_plugin_commits.py   # plugin commits must be release-worthy, no hand-bumps (CI, PRs)
scripts/release_skills.py         # per-skill release trains (versions, changelogs, tags, releases)
scripts/build_dist.py             # build a skill's .skill zip into dist/ (gitignored; used by release)
```

One tree, every consumer: Claude Code installs per-skill plugins through the
marketplace manifest, `npx skills` and other agents walk `skills/` flat, and
opencode symlinks it — no generated mirrors, no duplication.

## Adding a skill

```bash
python3 scripts/new_skill.py my-new-skill "One-line description."
# write skills/my-new-skill/SKILL.md, evals/evals.json (≥ 3 cases), README.md
npm run check && npm test
```

That's the whole job: no version bookkeeping, no zip building, no catalog editing — the release trains derive all of it. The scaffolder registers the plugin in `marketplace.json` via the generator; CI lints every skill against the [skillsmith](skills/skillsmith) quality rules (portable trigger text in the description, char budgets, no TODOs, body size, link integrity, evals present) and runs any plugin-specific `test.sh`. The full standard — what belongs here, review checklist, security model — is [CONTRIBUTING.md](CONTRIBUTING.md); rolling the skills out to a team is [docs/ADOPTION.md](docs/ADOPTION.md).

## CI & releases

CI runs on [Forgejo Actions](https://forgejo.webgrip.dev/webgrip/ai-skills/actions). Every PR gets `ci.yml`: conventional-commit check, plugin-commit guard (`scripts/check_plugin_commits.py` — commits touching a skill must use a release-triggering type, and versions must not be hand-edited), manifest structure (`scripts/check_manifests.py`), catalog sync (`scripts/sync_marketplace.py --check`), skill lint (`scripts/lint_skills.py`), and any plugin `test.sh`. Pushes to `main` run `release.yml`: the same checks, then the **per-skill release trains** (`scripts/release_skills.py`).

## Versioning — per-skill release trains

Each skill is its **own release train**. `scripts/release_skills.py` walks each skill independently: for a skill with conventional commits touching `skills/<skill>/` since its own last `<skill>-v<X.Y.Z>` tag, it bumps that skill's version (breaking → major, `feat` → minor, `fix`/`perf`/`refactor`/`revert` → patch), prepends `skills/<skill>/CHANGELOG.md`, regenerates `marketplace.json`, commits back `chore(release): <skill>-vX.Y.Z, … [skip ci]`, tags each released skill, and publishes its `<skill>.skill` to the [generic package registry](https://forgejo.webgrip.dev/webgrip/-/packages) at `api/packages/webgrip/generic/<skill>/<version>/<skill>.skill` plus a [Forgejo release](https://forgejo.webgrip.dev/webgrip/ai-skills/releases) per tag.

So a `feat:` touching one skill bumps, tags, changelogs, and releases **only that skill** — the others don't move, and there is no repo-wide `vX.Y.Z` tag. Claude Code users are prompted to update only the skills whose version rose. Never edit a version by hand (CI rejects it — use `feat(<plugin>)!:` to force a major); plugin `name` slugs are immutable once published (renames break installs — use `displayName`). A commit touching a skill under a non-releasing type (`docs:`/`chore:`) releases nothing for it — `check_plugin_commits.py` blocks that on PRs. If a release run goes red, fix it promptly — the trains are idempotent (each skill bases off its own tag; re-runs converge), so a fixed re-run resumes cleanly.

## Contributing

Issues and PRs welcome. Use conventional commit messages (release-triggering types for anything under `skills/`), run `npm run check` and `npm test` locally before submitting, and run `claude plugin validate .` if you have Claude Code installed. Versions, the catalog, and dist zips are all derived — don't edit them.

## License

MIT — see [LICENSE](LICENSE).
