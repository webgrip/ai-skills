---
name: guard-secrets
description: The secrets-handling floor for Webgrip repos, and the enforcement hook behind it. Use when writing or wiring secrets, editing SOPS files, handling API keys/tokens/credentials in config or Helm values, or when an edit is blocked with a BLOCKED secret message. Explains why the block fired and the compliant path (SOPS + value wiring).
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
3. **No plaintext secrets in any file.** When `gitleaks` is installed, the
   content is scanned and a positive hit is refused (best-effort — skipped
   silently without gitleaks).

## The compliant path

- A real secret lives **only** in a `*.sops.yaml` (SOPS-encrypted). Wire it
  into workloads by reference — Helm `existingSecret` / `envFromSecret` /
  a k8s `Secret`, never an inline value.
- Provisioning a *new* secret: write the non-secret wiring, and tell the
  human exactly what to `sops --encrypt` and where — a human provisions the
  ciphertext.
- Config templates carry **placeholders**, not values (`API_KEY: ${API_KEY}`
  from the environment, not the literal key).

## When a BLOCKED message appears

Read which rule fired (the message names it), then fix the *cause*, don't
route around it: move the plaintext into SOPS, replace the value with a
secret reference, or hand the provisioning step to a human. The hook is fail-open on its own
errors, so a green write is not proof of compliance; these rules are.
