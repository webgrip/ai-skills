# renovate-pins

Pin container images, Helm charts and operator-managed versions so Renovate keeps updating them,
and find the pins it silently stopped seeing. Covers the pin shape per location (glued
`tag@sha256` versus separate keys), a tag-plus-digest regex manager for Helm values, the blind
spots that freeze a pin while the dependency dashboard stays green (stranded digests, unmatched or
renamed paths, discontinued tag lines, registry moves, versions an operator fills in by default,
rule order), fixing red Renovate PRs without losing commits to a rebase, unsticking piles of bot
PRs with a stale base, dropping approval ticks that add no check, and proving a shared preset
refactor changes no behaviour with Renovate's own rule engine.

Ships:

- `scripts/pin_coverage.py` — stdlib check that compares every digest, image, repository/tag pair
  and operator version field in a repository with what Renovate's own `--dry-run=extract` report
  says it extracted, and lists each pin no manager owns.
- `scripts/registry_digest.py` — stdlib anonymous registry client: whether a tag exists, its
  multi-arch index digest, and whether a `tag@sha256` pin still matches the tag.

**Install:**

```text
/plugin install renovate-pins@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s renovate-pins`.

**Try:** "pin this Helm image by digest without breaking Renovate", "why is Grafana still on an old
version when Renovate bumps the operator?", "the Renovate PR fails on the pnpm lockfile", "go
through our stuck Renovate MRs", "does this tag exist yet and what digest should I pin?", "prove my
preset refactor changes nothing".
