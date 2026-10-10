---
name: guard-secrets
description: The secrets-handling floor for Webgrip repos, and the enforcement hook behind it. Use when writing or wiring secrets, editing SOPS files, handling API keys/tokens/credentials in config or Helm values, or when an edit is blocked with a BLOCKED secret message. Explains why the block fired and the compliant path (a vault or SOPS reference, never an inline value).
user-invocable: false
---

# Guard secrets — the floor, and why your write was blocked

A PreToolUse hook (`scripts/guard_secrets.py`, opencode twin
`opencode/plugins/guard-secrets.js`) **blocks an edit/write before it lands**
when it would leak a plaintext secret. Same rule set in both tools.

## The three hard rules (the hook denies on all three)

1. **No decrypted secret artifacts.** A path containing `decrypted`
   (`*.decrypted*`, `foo~decrypted`) is refused outright. Never write the
   plaintext of a secret to disk, even transiently.
2. **SOPS files stay ciphertext.** A write to `*.sops.yaml` / `*.sops.yml`
   whose content lacks `ENC[` is refused — that means you're about to commit
   plaintext into an encrypted file. Edit plaintext *elsewhere*, then
   `sops --encrypt`.
3. **No plaintext secrets in any file.** `gitleaks` scans the new content and
   a finding is refused. Only a finding blocks: gitleaks missing, timing out,
   or exiting with anything but its findings code is a scanner failure, so the
   hook warns on stderr and allows the write.

## The compliant path

- **The repo's own convention comes first.** Where a repo documents how it
  handles secrets (its `AGENTS.md`, a project hook), follow that; the three
  rules above still hold.
- Which level a value belongs at (floor, vault, cluster, bridge, short-lived,
  person) and the manifest that puts it there: the `secrets-levels` skill.
  Almost every value is a vault (OpenBao) original read by an `ExternalSecret`;
  a new `*.sops.yaml` is only ever the floor, by ADR.
- Wire by reference — Helm `existingSecret` / `envFromSecret` / a k8s `Secret`,
  never an inline value.
- Provisioning a *new* value: write the non-secret wiring, then hand the seed
  to a human (`just bao-login` + `bao kv put`, or `sops --encrypt` for the
  floor). A human enters the value; the agent never does.
- Config templates carry **placeholders**, not values (`API_KEY: ${API_KEY}`
  from the environment, not the literal key).
- Rule 3 needs a working `gitleaks` on `PATH`; pin it in the repo's
  `.mise.toml`. A `guard-secrets: gitleaks …` warning means the scan did not
  run: `gitleaks version` by hand shows why (a mise shim with no version set
  for the repo exits 1 without scanning).

## When a BLOCKED message appears

Read which rule fired (the message names it), then fix the *cause*, don't
route around it: replace the value with a reference to where it lives (the
vault, or SOPS at the floor), or hand the provisioning step to a human. The
hook fails open on its own errors, so a green write is not proof of
compliance; these rules are.

Check the hook itself by piping a fake event into it and reading the exit code
(2 = blocked, 0 = allowed):

```bash
echo '{"tool_input":{"file_path":"/tmp/app.sops.yaml","content":"password: hunter2"}}' \
  | python3 scripts/guard_secrets.py; echo "exit=$?"
```
