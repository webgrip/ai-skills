# webgrip org guidelines

These apply to every webgrip repo. Claude Code injects them at session start (the
`webgrip` plugin); opencode loads them via the org config's `instructions` array
(installed by `scripts/install_opencode.sh`). A repo's own `AGENTS.md`/`CLAUDE.md`
always wins where it disagrees — this is the baseline, not an override.

## Operating principles

- **GitOps-first.** Desired state lives in Git and is reconciled (Flux/Helm/Kustomize) — not applied imperatively. Prefer a manifest/values edit over `kubectl apply/patch/delete`, `helm install/upgrade`, or any out-of-band mutation. Keep diffs minimal and reversible.
- **Secrets have a level, and the vault is the only original.** Six levels per [homelab-cluster ADR-0055](https://forgejo.webgrip.dev/webgrip/homelab-cluster/src/branch/main/docs/techdocs/docs/adr/adr-0055-one-secrets-model-six-levels.md): floor (SOPS, closed list), vault (OpenBao), cluster (External Secrets), bridge (Forgejo Actions and Worker secrets, repo-scoped by default), short-lived (OIDC, leases), person (a shell export). A provided value enters OpenBao once, by a person over OIDC; an agent writes the manifests and hands over the `bao kv put`, never the value. Pods read `ExternalSecret`s, CI reads a bridge copy or an OIDC-minted token, people read the vault with `just secret-env`. Never a plaintext value in any file, never a new `*.sops.yaml` outside the floor. Placement: the `secrets-levels` skill; enforcement: `guard-secrets`.
- **Trunk-based on `main`.** Owner works directly on `main` (unprotected). Commit scoped, reversible changes straight to `main` — do **not** open feature branches or PRs unless asked. Always validate before committing.
- **Run tooling via `mise`** — `mise exec -- <cmd>`. Tool versions are pinned in `.mise.toml`; don't assume binaries are on `PATH`.
- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`…) with an optional scope. Keep commits atomic.

## Conventions

- **Dependencies are managed by Renovate** (`renovate-config` is the shared preset). Don't hand-bump versions that Renovate owns; review its PRs instead. To force a run, use the `renovate-trigger` agent.
- **Apps follow `application-template`** — the canonical layout for a deployable service. Copy a comparable existing app rather than scaffolding from scratch.
- **Shared Helm building blocks:** `common-charts` and `helm-dependency-values`. Reach for these before hand-rolling chart plumbing.
- **Observability labels matter.** ServiceMonitor/PrometheusRule resources need `release: kube-prometheus-stack` (or the cluster's documented selector) or they're silently not scraped.
- **Docs as TechDocs** — MkDocs under `docs/` (see `mkdocs-techdocs-core` / `techdocs-runner`). Update docs alongside behavior changes; don't hardcode environment-specific values that drift.

## Working style

- Validate before you commit (each repo documents its gate — flux-local render, `helm template`, typecheck/lint/test). State plainly when something failed or was skipped.
- Don't hardcode secret domains/IPs — they're environment-specific and often SOPS-encrypted. Template them.
- Escape runtime shell vars inside manifests as `$${...}` so the templating layer doesn't eat them.
