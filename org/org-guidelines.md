# webgrip org guidelines

These apply to every webgrip repo. Claude Code loads them from `~/projects/webgrip/CLAUDE.md`, a symlink to this file that every repo below that folder inherits as an ancestor, so they never reach other orgs' repos; opencode loads them via the org config's `instructions` array
(installed by `scripts/install_opencode.sh`). A repo's own `AGENTS.md`/`CLAUDE.md`
always wins where it disagrees — this is the baseline, not an override.

## Operating principles

- **GitOps-first.** Desired state lives in Git and is reconciled (Flux/Helm/Kustomize) — not applied imperatively. Prefer a manifest/values edit over `kubectl apply/patch/delete`, `helm install/upgrade`, or any out-of-band mutation. Keep diffs minimal and reversible.
- **Secrets have a level, and the vault is the only original.** Six levels per [homelab-cluster ADR-0055](https://forgejo.webgrip.dev/webgrip/homelab-cluster/src/branch/main/docs/techdocs/docs/adr/adr-0055-one-secrets-model-six-levels.md): floor (SOPS, closed list), vault (OpenBao), cluster (External Secrets), bridge (Forgejo Actions and Worker secrets, repo-scoped by default), short-lived (OIDC, leases), person (a shell export). A provided value enters OpenBao once, by a person over OIDC; an agent writes the manifests and hands over the `bao kv put`, never the value. Pods read `ExternalSecret`s, CI reads a bridge copy or an OIDC-minted token, people read the vault with `just secret-env`. Never a plaintext value in any file, never a new `*.sops.yaml` outside the floor. Placement: the `secrets-levels` skill; enforcement: `guard-secrets`.
- **Trunk-based on `main`.** Owner works directly on `main` (unprotected). Commit scoped, reversible changes straight to `main` — do **not** open feature branches or PRs unless asked. Always validate before committing.
- **Forgejo is de release-autoriteit**, met een paar vaste waarden en twee valkuilen die stil falen (`uses:` als shorthand, `if:` op een `uses:`-job doet niets). Zie [forgejo-ci.md](forgejo-ci.md).
- **Er draaien meerdere sessies tegen dezelfde working tree.** Commit altijd op pathspec en ga ervan uit dat een lokale commit elk moment gepusht kan worden. Zie [shared-working-tree.md](shared-working-tree.md).
- **Run tooling via `mise`** — `mise exec -- <cmd>`. Tool versions are pinned in `.mise.toml`; don't assume binaries are on `PATH`.
- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`…) with an optional scope. Keep commits atomic.

## Conventions

- **Hergebruik bindt aan bestaande machinerie** (workflows-tags, `@webgrip`-packages, sync-PR's) en kent een paar vallen bij een eigen release op dezelfde dag. Zie [reuse-and-releases.md](reuse-and-releases.md).
- **Dependencies are managed by Renovate** (`renovate-config` is the shared preset). Don't hand-bump versions that Renovate owns; review its PRs instead. To force a run, use the `renovate-trigger` agent.
- **Apps follow `application-template`** — the canonical layout for a deployable service. Copy a comparable existing app rather than scaffolding from scratch.
- **Shared Helm building blocks:** `common-charts` and `helm-dependency-values`. Reach for these before hand-rolling chart plumbing.
- **Observability labels matter.** ServiceMonitor/PrometheusRule resources need `release: kube-prometheus-stack` (or the cluster's documented selector) or they're silently not scraped.
- **No comments in code.** Intent is carried by a precise name, a type, a smaller function, or a test that states the case; anything that outlives a single expression goes to `docs/` or an ADR. Machine-read directives stay because the toolchain acts on them as syntax: shebangs, `# syntax=`, `# renovate:`, schema hints, `@ts-*`/`eslint-*`/`prettier-ignore`, `# shellcheck`, `# noqa`, `//go:*`, and doc comments a tool reads. `@webgrip/comment-ban` gates the delta in CI. Per [ai-skills ADR-0001](https://forgejo.webgrip.dev/webgrip/ai-skills/src/branch/main/org/adrs/adr-0001-no-comments-in-code.md).
- **Docs as TechDocs** — MkDocs under `docs/` (see `mkdocs-techdocs-core` / `techdocs-runner`). Update docs alongside behavior changes; don't hardcode environment-specific values that drift.

## Working style

- **Every pointer carries a link.** Anything you ask the reader to look at or act on (a file, ticket, PR, CI run, dashboard, doc, log line) is cited with a working link: repo files as relative markdown links (`[src/foo.ts:42](src/foo.ts#L42)`), everything else as a full URL. Naming a thing without linking it is an unfinished answer.
- **Nooit iets versturen.** Geen mail via SMTP, een MCP-tool of een mailclient, en net zomin een LinkedIn-bericht, contactformulier of Meetup-organisatorbericht. Je levert drafts op en zegt waar ze staan; Ryan verstuurt alles zelf. Outreach gaat onder zijn naam naar echte mensen in een kleine regio die hij jaren blijft tegenkomen, en een bericht dat als AI-geschreven leest laat de waargenomen oprechtheid dalen van 83% naar 40 tot 52% (UF/USC, *Int'l Journal of Business Communication*, aug 2025) — de mens die de zinnen schrijft ís wat outreach laat werken.
- **Grill before planning.** For a design or multi-repo change, first list the open questions and ask them interactively, a few at a time, each with a recommendation and its trade-off; record every answer in the plan as it comes. Write the implementation plan only once no question is open.
- **A stalled subagent gets one resume.** When a background subagent stops making progress (the watchdog kills it after 600 s without output), check what it left on disk, resume it once, and finish the work in the main thread if it stalls again.
- Validate before you commit (each repo documents its gate — flux-local render, `helm template`, typecheck/lint/test). State plainly when something failed or was skipped.
- Don't hardcode secret domains/IPs — they're environment-specific and often SOPS-encrypted. Template them.
- Escape runtime shell vars inside manifests as `$${...}` so the templating layer doesn't eat them.
