# ai-skills

[![Release](https://forgejo.webgrip.dev/webgrip/ai-skills/actions/workflows/release.yml/badge.svg?branch=main)](https://forgejo.webgrip.dev/webgrip/ai-skills/actions?workflow=release.yml)

Webgrip's open-source Claude skills, shipped as one plugin marketplace hosted on [Forgejo](https://forgejo.webgrip.dev/webgrip/ai-skills). Each skill is its own plugin — install only what you want.

## Skills

| Skill | What it does |
|---|---|
| [adr-writer](skills/adr-writer) | Write, amend, and supersede MADR 4.0.0 Architecture Decision Records: bootstrap or adopt an ADR corpus, registry index kept in lock-step, append-only dated history, and a bundled CI-ready consistency validator. |
| [agent-instructions](skills/agent-instructions) | Set up any repo for AI coding agents end to end and keep it right: inventory, a plan you approve, then one canonical `AGENTS.md` (with `CLAUDE.md` importing it), knowledge moved to `docs/`, one path-rule source generated for every tool from a registry of the top tools per category (interactive agents, cloud agents, review bots, generators, CI forges, hook managers), skills, MCP, cloud-agent and review-bot setup, and a stdlib CI check; plus audits, slimming, probe tests and generator-safe layouts for Laravel Boost and friends. |
| [agent-platform](skills/agent-platform) | Run coding agents for a team behind boundaries they cannot move: an LLM gateway (LiteLLM teams as code, budgets, deny-by-default MCP grants minted with the team id, Claude Code routed without breaking prompt caching), scoped read-only agent tools enforced in the data proxy (one MCP server per scope, vmauth `extra_label`, proven by replay and attack), and Claude Code usage telemetry with the organisation boundary in the collector (Alloy OTTL filter, identifiers stripped, query-first dashboards, team attribution); a stdlib MCP grant probe and a synthetic-OTLP collector-filter tester. |
| [blog-writer](skills/blog-writer) | Turn project notes into technical blog posts developers read — evidence-first drafting, hook workshop, single-dimension edit sweeps with a de-AI-ify pass, fresh-reader testing, and per-platform syndication recipes (HN, LinkedIn, Substack, dev.to, Reddit, Lobsters). |
| [domain-language](skills/domain-language) | Define a project's ubiquitous language (terms, entities, rules, events) in `domain/model.yaml`; generate glossaries, entity docs with Mermaid diagrams, [Context Mapper](https://contextmapper.org) exports, a 0–10 model health score, and feature specs from it. |
| [edge-hosting](skills/edge-hosting) | Ship static sites, Workers and private pages on Cloudflare's free edge tier so they stay up: assets-only Workers over Pages, a claimant for every hostname (the 522 trap), routes vs custom domains, www→apex, DNS as code, Worker- and hostname-level Access, release-driven staging and previews, least-privilege CI tokens; a stdlib wrangler-config linter and live-site prober, a tested private-pages Worker + `share.py` for expiring per-recipient pages, and when an EU or other free host wins instead. |
| [expressive-design](skills/expressive-design) | Design and build distinctive, memorable web pages from the subject's own evidence: a claim ledger and hero pair, one thesis object carrying the identity, parallel faithful/amplified/strange directions, a still composition judged with motion off (flatness ladder, flatplan, template diff, screenshot critique tests), a motion contract per effect with October 2026 Baseline status and the WCAG 2.2 floor, and a 23-rule source scanner for reduced-motion, zoom, focus, layout-shift, template-look and fabricated-proof failures. |
| [flaky-ci-forensics](skills/flaky-ci-forensics) | Diagnose flaky tests and red CI jobs with evidence instead of retries: triage "is it my change?", count how often one assertion failed across pipelines and merge requests before calling it a one-off, rule the CI image in or out by digest and layer content (BuildKit re-adds same-content files whose mtime changed), fix timing, ordering and shared-state flakes, and prove fixes with repeat loops and break-checks; also tests that never run, zero-job GitLab pipelines, schedules that run releases, branch-rewrite forensics and slow lint hooks. Stdlib scripts: a GitLab/GitHub failed-job log recurrence counter, a repeat runner with per-run timeouts, and an image layer differ. |
| [forge-agents](skills/forge-agents) | Wire bots and coding agents into GitLab, GitHub and Forgejo or Gitea without over-privileging them: the identity and token a CI or bot agent needs (service accounts, access tokens, GitHub Apps; what `CI_JOB_TOKEN` and `GITHUB_TOKEN` cannot do), label and assignment triggers with a role check, signed and deduplicated webhook listeners, untrusted ticket text written through the API, retries that never duplicate a creating POST, Claude Code in GitLab CI, headless agents on repos you do not control with sandboxes compared, and glab/gh/tea recipes; a stdlib text neutraliser and webhook-signature checker. |
| [grafana-access](skills/grafana-access) | Decide and enforce who sees which data in Grafana OSS: confidentiality or noise first, one org per scope because the org is the only data boundary, generic OAuth `org_mapping` semantics with the marker-group pattern that keeps staff in the default org while a wall-screen kiosk sees only its scope, per-scope orgs from git with grafana-operator, snapshots and public dashboards off, major upgrades proven through the API (including the Grafana 13 read-only plugin trap), wall dashboards readable across the room, and a stdlib read-only access audit tested against fixtures recorded from Grafana 13. |
| [guard-secrets](skills/guard-secrets) | A `PreToolUse` hook that blocks plaintext-secret leaks before an edit lands (no decrypted artifacts, SOPS stays ciphertext, gitleaks scan), plus the secrets-floor knowledge behind it — the Claude Code twin of the opencode guard-secrets plugin. |
| [harvest-knowledge](skills/harvest-knowledge) | Mine durable learnings out of Claude threads in three phases (distill → consolidate → synthesize) and land them as repo docs, CLAUDE.md rules, new skills, and memory updates. |
| [humanize](skills/humanize) | Detect, remove or prevent the tells of AI-generated writing in English and Dutch: 229 English and 251 Dutch catalog entries consolidated from the main open-source humanizers, the Wikipedia field guide and the published tell-lists, with a translationese layer for English-shaped Dutch that no upstream tool covers; four modes with fact and voice protection, a register tolerance table, and a dependency-free scanner whose 1,295 regexes are each measured against human prose. |
| [kpi-groomer](skills/kpi-groomer) | Define, groom and facilitate KPI sets that change decisions: complete definitions (formula, source, owner, baseline, the decision it changes), Goodhart speed/quality pairs, timeboxed team-owned KPI workshops, dashboard-as-artifact traceability, review-and-retire cadence, and an ethics gate for person-level metrics (SPACE, GDPR/works council). |
| [linkedin-post](skills/linkedin-post) | Get a LinkedIn post read: the 2026 ranking mechanics (link penalty, comments over likes, dwell time, personal profile over company page), the plain-text formatting the editor will not destroy on paste, accessible emphasis instead of Unicode pseudo-bold, and the posting window. |
| [org-boundaries](skills/org-boundaries) | Keep each organisation's knowledge and identity out of the others' repos when one person works for several on one machine: remove the organisation, keep the person; tell-tale references; a stdlib scanner over file content, paths, commit identities and messages, branches and tags, with a local pre-commit and commit-msg guard; neutral rewrites; per-directory git identity for agent scratch clones; user-level MCP servers, hooks, telemetry and rules that cross organisations; and a filter-repo plan for when history must be rewritten. |
| [product-owner](skills/product-owner) | Run any ticket board as product owner (Vikunja + ClickUp adapters, bundled `vikunja` MCP): a research-backed Definition of Ready, an agent-ready gate for AI-executed work, WIP anchored on review capacity, a Definition of Mergeable with a git-only merge check, evidence-based closing, flow metrics with an SLE — and **Board contracts** as the extension seam: instance facts layer in from repo/user/org contract layers (template in `contracts.md`, philosophy in [docs/contract-pattern.md](docs/contract-pattern.md)) so orgs extend it without forking. Every major rule sourced in `rationale.md`. |
| [product-ux](skills/product-ux) | Design, critique and build product interfaces people use repeatedly (apps, dashboards, admin tables, forms, settings, AI features) from evidence: an evidence ledger and job stories, a frequency × error-cost task model, flows and a state matrix before screens, 250+ evidence-tiered pattern rules with October 2026 Baseline status, the existing design system as authority, a WCAG 2.2 and EU deceptive-pattern floor, heuristic evaluation, cognitive walkthrough and KLM with a protocol built on the published accuracy of LLM critics, and a 34-rule source scanner for unlabelled fields, fake buttons, blocked paste, pre-ticked consent, confirmshaming and vague errors. |
| [protocol-fit-research](skills/protocol-fit-research) | Answer "does this protocol matter to us?" with a parallel research fan-out (spec crawl, source-repo dig, ecosystem adoption plus explicit absence checks, local seam map), a verdict-led report separating maturity from fit, and a dossier, ledger row and watchlist item landed in the repo with falsifiable re-evaluation triggers. |
| [refactoring-economics](skills/refactoring-economics) | Refactor agent-maintained code where it measurably lowers what coding agents spend on future changes, operationalising the martinfowler.com refactoring-economic-benefit experiment and fixing its gaps: git-hotspot targeting with agent share and change coupling, a stdlib harness that runs the same representative change on several refs at least five interleaved times and reads billed token classes from the agent's own stream (Claude Code, Codex), Fowler-catalog refactorings ordered by what shrinks the read set with a cohesion rule against line-count splitting, tool-driven execution with a per-step gate, and a break-even model priced per token class with human review and a safety factor. |
| [renovate-pins](skills/renovate-pins) | Pin images, Helm charts and operator-managed versions so Renovate keeps moving them: the pin shape per location, a tag-plus-digest regex manager for Helm values, the blind spots that freeze a pin behind a green dashboard, fixing red and stuck bot PRs without losing commits to a rebase, approval backlogs, behaviour-neutral preset refactors measured with Renovate's own rule engine, a stdlib coverage check over Renovate's extract report, and an anonymous registry digest check. |
| [search-visibility](skills/search-visibility) | Get static sites on Cloudflare's edge found in Google and Bing and cited by ChatGPT, Claude, Perplexity and AI Overviews, with every claim graded by evidence: crawler access by role (search, user fetch, training) and Cloudflare's AI bot policies including the 2026-09-15 change that makes Training = Block also block Googlebot, one canonical URL per page under wrangler `html_handling`, robots.txt, sitemaps, hreflang, structured data Google still uses and link previews, answer-first content, a corrected verdict on GEO (the 40 % did not replicate) and llms.txt, a repeated-run protocol for measuring AI citations, and a 78-rule scanner for the build and the live edge. |
| [secrets-levels](skills/secrets-levels) | Place a secret at the right level of the estate and name the manifest that puts it there: floor (SOPS), vault (OpenBao), cluster (External Secrets), bridge (Forgejo Actions and Cloudflare Worker secrets), short-lived (OIDC, dynamic credentials, per-run tokens), person (a laptop). Decision by origin, then by consumer; the placement half of the secrets model, with `guard-secrets` as the enforcement half. |
| [site-performance](skills/site-performance) | Make static sites on Cloudflare's edge fast for real users and prove it with field data, every claim graded by evidence: Core Web Vitals diagnosed by LCP subpart, INP phase and largest shift, fixes ranked by measured impact with Astro, Hugo and Eleventy specifics, Cloudflare delivery traps (revalidated hashed assets, trailing-slash 307s, Early Hints, Speed Brain), RUM chosen by site size with EU and Dutch privacy rules (Cloudflare Web Analytics, RUMvision, a DIY web-vitals beacon into Workers Analytics Engine), Lighthouse CI budgets that survive the Lighthouse 13 rename, and a 35-rule scanner for the build and the live edge with CrUX field data. |
| [skill-usage](skills/skill-usage) | Local skill-usage telemetry: a `PostToolUse` hook logs every skill invocation to a local JSONL (no network), and the skill reports which skills are used, dead, or undertriggering — the private answer to "which of our skills earn their keep?". |
| [skillsmith](skills/skillsmith) | Author, edit, and audit agent skills for token-efficient, high-trigger-accuracy ingestion: the skill loading/token cost model, description-as-router rules, cross-tool frontmatter portability, progressive disclosure, and eval methodology. |
| [subagent-fleet](skills/subagent-fleet) | Run several coding agents at once on shared repositories without losing work or trust: one worktree and test database per agent (and what `isolation: "worktree"` really starts from), a brief contract with local-only commits, stop-on-block and gates to a log, steering, resuming and recovering stalled background subagents, background tasks, timeouts and exit 144, landing agent commits by exact paths and fast-forward only, transcripts as the record, and read-only stdlib scripts that inventory leftover worktrees, branches and processes (with a print-only prune plan) and search session transcripts and subagent hand-backs. |

## Install

**`npx skills` (recommended — every agent, not just Claude):** the flat `skills/` tree is the
vendor-neutral layout the cross-tool installers consume, so one command installs into 70+ agents
(Claude Code, opencode, Cursor, Codex, Copilot, Gemini CLI, …):

```bash
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git            # interactive
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -g -y -s '*' -a claude-code -a opencode   # everything, user-level, for the agents you use
npx skills update -g                                                       # pull latest
```

Skills land in `~/.agents/skills/` and are symlinked into each agent's skills dir
(`~/.claude/skills/`, opencode, …). They invoke **unprefixed** — `/domain-language`. Pinning,
lockfiles, and telemetry opt-out: [docs/DISTRIBUTION.md](docs/DISTRIBUTION.md).

> **The CLI copies hooks and MCP config but wires neither.** A skill's `hooks/hooks.json` (`guard-secrets`, `skill-usage`) or `.mcp.json` (`product-owner`) lands in `~/.agents/skills/<name>/` and nothing registers it: the skill looks installed and enforces nothing. Register each hook yourself in `~/.claude/settings.json` with `$HOME/.agents/skills/<name>/…` paths (`${CLAUDE_PLUGIN_ROOT}` exists only under the plugin loader; the snippets are in each skill's README), or take the plugin route below. Either way, prove each hook once in a live session: for `guard-secrets`, write `password: x` to a `*.sops.yaml` file and watch it block.

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

Two estates that ship same-named skills on one machine are solved on that machine, not with prefixes: install both globally through `npx skills`, one source per shared name. Install this estate first with `-s '*'`, then the other with `-s` limited to the names you want from it. The last install of a name wins its folder, and `~/.agents/.skill-lock.json` records which source each name came from. Adding the bundle or per-skill plugins on top loads skills twice; see [docs/DISTRIBUTION.md](docs/DISTRIBUTION.md#one-channel-per-skill-per-machine).

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
