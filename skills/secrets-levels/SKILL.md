---
name: secrets-levels
description: Places a secret at the right level of the Webgrip estate and names the manifest that puts it there, per homelab-cluster ADR-0055 - floor (SOPS), vault (OpenBao), cluster (External Secrets), bridge (Forgejo Actions and Cloudflare Worker secrets), short-lived (OIDC, dynamic credentials, per-run tokens), person (a laptop). Use when adding, wiring, rotating, or asking where to put an API key, token, password, credential, PAT, or client secret; when a CI job, workflow, pod, Worker, or developer machine needs a secret; when someone proposes a new sops.yaml, a Forgejo org secret, a Keychain entry, a .env file, or a bao kv put; when deciding whether a value is entropy, provided, or mintable; when a CI job holding a token runs on pull requests; when a generated password will not regenerate; or when a secret was printed into a session.
---

# Secrets levels — which level, which manifest

Model: [homelab-cluster ADR-0055](https://forgejo.webgrip.dev/webgrip/homelab-cluster/src/branch/main/docs/techdocs/docs/adr/adr-0055-one-secrets-model-six-levels.md).
Plaintext floor and the hook that enforces it: the `guard-secrets` skill. Per-level runbooks
and example manifests by path: [reference.md](reference.md).

## Decide by origin

1. **Entropy** no human needs to know (session key, admin password, CSRF, robot password) →
   **L2 generator**: `ExternalSecret` with `dataFrom.sourceRef.generatorRef` →
   `password-generator` (`-16`/`-32` for exact lengths), `refreshInterval: "0"`,
   `target.deletionPolicy: Retain`. It never enters the vault.
2. **Provided** by the outside world (API token, OIDC client secret, S3 key, webhook secret) →
   **L1 vault** at `secret/<provider>/<purpose>`, keys named as the consumer reads them.
   **Write the manifests, then hand the seed to a person**:
   `mise exec -- just bao-login` and `bao kv put secret/<provider>/<purpose> KEY=<value>`.
   The agent has no vault token; OIDC login is interactive by design.
3. **Mintable** by a vault engine (Postgres role, transit signature, forge token for a run) →
   **L4**: an ExternalSecret against `ClusterSecretStore/openbao-db`, a JWT role at
   `auth/forgejo` in `kubernetes/apps/security/openbao/bootstrap/config.sh`, or ploeg's minter.
4. **Needed before the vault exists** (age key, `talsecret`, `cluster-secrets`, unseal key) →
   **L0 floor**. Closed list. A new entry is an ADR, not a file.

## Then by consumer

| Consumer | Level | Manifest |
| --- | --- | --- |
| A pod | L2 | `ExternalSecret` (store `openbao`, `creationPolicy: Owner`) next to the app, consumed by `existingSecret` / `envFrom`; `reloader.stakater.com/auto: "true"` on rotatable consumers, never on at-rest-key holders |
| A Forgejo workflow | L3 | `ExternalSecret/forgejo-<provider>` in namespace `forgejo` plus a `put_repo_secret "<repo>" <NAME> "$<NAME>"` block with a provider verify `curl` in `forgejo-actions-secrets.cronjob.yaml`; org-wide only with the reason written in the block |
| A Cloudflare Worker | L3 | a bridge CronJob in the `counterscale-worker-secrets` shape |
| A release job signing, a DB client, an agent run | L4 | `bound_claims.repository` in the role JSON, a `database` role, a Lease |
| A person's shell | L5 | `eval "$(mise exec -- just secret-env <provider>/<purpose>)"` from a homelab-cluster checkout; Keychain only as a cache named `<provider>-<purpose>` |

Repo-scoped is the CI default. Forgejo resolves a repo secret over an org secret of the same
name; that is the mechanism, not a collision.

## Naming

- L1: `secret/<provider>/<purpose>`; `remoteRef.key` omits the mount (`<provider>/<purpose>`).
- L3: `<PROVIDER>_<PURPOSE>`; Forgejo rejects the prefixes `FORGEJO_`, `GITHUB_`, `GITEA_`.

## Gotchas

- **Never** create a `*.sops.yaml` outside the floor, and never write a value into a manifest,
  a `.env`, a commit, or a chat message. Ask for the seed; do not perform it.
- **Never print a value into the session, even when asked for it.** Transcripts are kept and
  harvested. Read it into a variable, or hand it over as its vault path or straight to the
  clipboard (`… | base64 -d | pbcopy`). A value that did reach a transcript gets rotated.
- A generator with `refreshInterval: "0"` generates **once**: a changed `spec` (length,
  charset) does nothing to the existing Secret. Rename the `ExternalSecret` and its target, or
  delete the Secret, then follow every copy downstream: the PushSecret into the vault, the
  consumer `ExternalSecret`s on their refresh, the Reloader restart, any IdP or app config
  holding the old value.
- A secret a CI job holds is readable by whoever can push the code that job runs. A
  token-holding Forgejo job triggers on push to a protected branch or on a schedule, never on
  `pull_request` (same-repo branches get the secrets), and under `pull_request_target` it
  never checks out or runs PR code. Events per forge →
  [reference.md](reference.md#which-ci-events-see-a-secret).
- A provided value that already encrypts data is seeded once from its current value; a
  generator in its place corrupts every row the old key touched.
- `workflow_call: secrets:` is rejected by Forgejo's parser; pass secrets from the calling job.
- Forgejo secret values are write-only; the bridge log line `PUT ... 201|204` is the existence
  check.
- `secrets: inherit` is used nowhere in the estate; keep every secret an explicit pass.
