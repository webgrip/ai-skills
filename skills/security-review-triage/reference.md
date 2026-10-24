# Security review and triage: reference

Contents: [Review exclusions](#review-exclusions) · [Dismissal tests](#dismissal-tests) · [Infrastructure checklist](#infrastructure-checklist) · [Advisory lookup](#advisory-lookup) · [CVSS](#cvss) · [Report template](#report-template)

## Review exclusions

Drop these from a code review unless the change itself introduces the risk:

- Denial of service, missing rate limits, resource exhaustion.
- Outdated dependencies (handle them under advisories and versions instead).
- Test files, fixtures, documentation.
- Log spoofing; SSRF that controls only the path; regular-expression injection or ReDoS.
- Framework-escaped output (template autoescaping, ORM parameters) unless the code uses the framework's explicit bypass.
- Values the server controls: environment variables and CLI flags in application code, unguessable identifiers, server-side config stores.

These exclusions are for application code. In infrastructure review, config and environment **are** the attack surface.

## Dismissal tests

Run in order; stop at the first one that dismisses, unless a full evaluation is asked for:

1. **No threat model, no vulnerability.** Name who attacks and what they gain.
2. **The required capability already covers the impact.** If the attacker must already hold what the finding gives them, dismiss.
3. **Outside real use.** A configuration or call path nobody uses is not a vulnerability in this deployment.
4. **Standard or documented behavior.** If it behaves as specified or documented, the issue may belong to whoever chose to use it that way.
5. **The cure is worse than the disease.** Weigh the fix's own risk and blast radius.
6. **A CVE ID is neither necessary nor sufficient.** Judge the technical claim with the ID and score removed.

Two-sided caution: do not dismiss merely because something is "debug only" or "needs local access", and do not accept merely because it "has a CVE" or "a high CVSS score".

## Infrastructure checklist

| Area | Check |
| --- | --- |
| Pods | Pod Security level; `securityContext` (non-root, no privilege escalation, dropped capabilities, read-only root); `hostPath`, `hostNetwork`, `hostPID`, `privileged`; user namespaces |
| Runtime sandboxes | RuntimeClass handler config; annotations a pod can pass to the runtime (e.g. `io.katacontainers.*` for Kata); sandbox debug consoles |
| RBAC | Verbs × resources, especially Secrets, `pods/exec`, `escalate`, `bind`, `impersonate`, wildcard rules; who can create pods in a sensitive namespace |
| Network | Default-deny ingress and egress plus a DNS allow; egress by name rather than open to the world |
| Images | Pinned by digest; allowed registries; signature verification |
| Admission | Policies in Enforce, not Audit; failure policy; namespace exclusions that are wider than needed |
| CI | Trigger × permissions × untrusted code (e.g. `pull_request_target` checking out a PR head); explicit `permissions:` block; actions pinned by commit SHA, not tag |
| Secrets | Where each secret lives, who can read it, whether it is mounted into untrusted workloads or logged |

## Advisory lookup

```bash
curl -s -X POST https://api.osv.dev/v1/query \
  -d '{"package":{"name":"<package>","ecosystem":"<ecosystem>"},"version":"<version>"}'
gh api '/advisories?affects=<package>@<version>&ecosystem=<ecosystem>'
gh api repos/<owner>/<repo>/security-advisories
```

Record which sources answered and which returned nothing; OSV and GitHub often list different advisories for the same version.

## CVSS

- **v3.1** metrics: AV, AC, PR, UI, S, C, I, A. Bands: 0.1–3.9 Low, 4.0–6.9 Medium (GitHub calls it Moderate), 7.0–8.9 High, 9.0–10 Critical.
- **v4.0** groups: Base, Threat, Environmental, Supplemental (Supplemental never changes the score). New: Attack Requirements (AT); User Interaction is None, Passive or Active; Scope is replaced by impacts on the vulnerable system (VC, VI, VA) and on subsequent systems (SC, SI, SA).
- **The maintainer owns the Base score.** A reporter proposes a vector with a one-line reason per non-obvious metric. Your own environment's score is consumer-side (Threat and Environmental) and is labelled as such.

## Report template

Fields match GitHub's private vulnerability report form.

- **Title:** component: what the flaw allows, in one line.
- **Summary:** affected component and versions, the class of flaw, who can trigger it, the impact, and any upstream advisory it matches.
- **Details:** each finding with `file:line` at a named commit or tag, and the suggested fixes.
- **Proof of concept:** read-only checks that show the precondition holds. Say plainly what was not run or not tested.
- **Impact:** who is exposed and who is not, using the blast-radius card.
- **Affected products:** ecosystem, package, affected range, patched version if known.
- **Severity:** a proposed level or vector, marked as a proposal.
- **Workaround:** what users can do now, such as an admission policy or a config change.
- **AI assistance:** tick the form's box when a model helped find or write the report.
