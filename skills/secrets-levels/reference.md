# Secrets levels — reference

Contents: the six levels · runbooks per level · example manifests by path · which CI events see a secret · what changed in ADR-0055.

## The six levels

| Level | Holds | Writer | Reader | Promise |
| --- | --- | --- | --- | --- |
| L0 Floor | `bootstrap/sops-age`, `talos/talsecret`, `kubernetes/components/sops/cluster-secrets`, the unseal key in Secret `security/openbao-keys` | a person, by ADR | Flux, Talos, the unsealer | closed list |
| L1 Vault | every provided value, every preserved at-rest key, the engines | a person over OIDC+MFA, or a roller by PushSecret | ESO, bridges, rollers, humans | the single original; nightly raft snapshot to Garage, 14 kept |
| L2 Cluster | Kubernetes Secrets from ESO | ESO | pods | a cache; survives a vault outage; entropy is born here |
| L3 Bridge | copies in Forgejo Actions, Cloudflare Worker secrets | a CronJob | the platform | hourly, verified against the provider, alerts when stale; repo-scoped by default |
| L4 Short-lived | nothing at rest | the vault per request | the requesting job, for its TTL | bound to repository and event |
| L5 Person | a session export | a person, from L1 | that shell | a cache, never the only copy |

## Runbooks per level (homelab-cluster)

Base: `https://forgejo.webgrip.dev/webgrip/homelab-cluster/src/branch/main/docs/techdocs/docs/runbooks/`

- L0 `secrets-level-0-floor.md` · L1 `secrets-level-1-vault.md` · L2 `secrets-level-2-cluster.md`
- L3 `secrets-level-3-bridge.md` · L4 `secrets-level-4-short-lived.md` · L5 `secrets-level-5-person.md`
- Rotation `secret-rotation.md` · compromise `secret-break-glass.md` · ESO ops `external-secrets.md` · restore `openbao-restore.md`

## Example manifests by path (homelab-cluster)

| Shape | Path |
| --- | --- |
| Generator, multi-key, exact lengths | `kubernetes/apps/harbor/harbor/app/harbor-admin.externalsecret.yaml` |
| L1 value into the bridge namespace | `kubernetes/apps/forgejo/forgejo-actions-secrets/app/cloudflare-deploy.externalsecret.yaml` |
| Repo-scoped bridge block, first instance | `BREVO_API_KEY` in `kubernetes/apps/forgejo/forgejo-actions-secrets/app/forgejo-actions-secrets.cronjob.yaml`, fed by `forgejo-brevo.externalsecret.yaml` |
| Roller writing back to L1 | `kubernetes/apps/forgejo/forgejo-actions-secrets/app/cloudflare-deploy-rolled.pushsecret.yaml` |
| Worker bridge | `kubernetes/apps/forgejo/forgejo-actions-secrets/app/counterscale-worker-secrets.cronjob.yaml` |
| OIDC signing role | `kubernetes/apps/security/openbao/bootstrap/config.sh`, the `cosign-signer` JSON |
| Human helpers | `justfile` recipes `bao-login`, `secret-env`, `harbor-s3-cred`, `cloudflare-deploy-cred` |

## Which CI events see a secret

A pipeline that runs branch code runs that branch's workflow file and scripts, so any secret it
can read is readable by anyone who can push a branch, agents included. Masking only hides the
value in job logs. Run token-holding jobs (bridges, ticket mirrors, release and deploy jobs) only
on push to a protected branch, on a schedule, or from a webhook service. A manual dispatch runs
the workflow file of whichever ref it is started on, so it is only as safe as that ref.

| Event | Forgejo Actions |
| --- | --- |
| `pull_request`, head from a fork | `secrets` is empty, the automatic token is read-only, OIDC is off; a read-only user's PR waits for approval before any workflow runs |
| `pull_request`, head from a branch of the same repo | the docs empty `secrets` only for fork heads, so the job **gets the repo's secrets** |
| `pull_request_target` | runs the base repo's default-branch workflow with its secrets and a write token; checking out or running PR code in it hands both to the PR author |
| push to a protected branch, `schedule` | secrets available; only people who may push to that branch change what runs |

Other forges, same rule: on GitHub, write access means read access to every repo secret, fork
PRs get none, and `pull_request_target` plus a checkout of PR code is the classic exfiltration.
On GitLab, an unprotected variable reaches every MR pipeline from a same-project branch; only
"Protect variable" (protected branches and tags) or an environment scope keeps it out.

Sources: [Forgejo Actions reference](https://forgejo.org/docs/latest/user/actions/reference/) ·
[Forgejo pull request security](https://forgejo.org/docs/latest/user/actions/security-pull-request/) ·
[GitHub secure use](https://docs.github.com/en/actions/reference/security/secure-use) ·
[GitLab CI/CD variable security](https://docs.gitlab.com/ci/variables/).

## What ADR-0055 changes

- CI secrets repo-scoped by default; `NPMJS_TOKEN`, `GHCR_TOKEN`, `GH_RELEASE_TOKEN`,
  `CLOUDFLARE_API_TOKEN`, `CODEBERG_TOKEN` move from org to their repos.
- The Forgejo bridge becomes a manifest table; until it lands, one secret is one ExternalSecret
  plus one block.
- People read the vault with `just secret-env`; the Keychain is a cache named after the path.
- The floor closes: `erfbeeld` (3) and `zomboid` SOPS files are migrated or deleted.
- `openbao-push` is a roller store, policy narrowed to the paths rollers write.
- `gitleaks` pinned in every `.mise.toml`; the `guard-secrets` hook warns when it is absent.
