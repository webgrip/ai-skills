---
name: renovate-pins
description: Pins container images, Helm charts and operator-managed versions so Renovate keeps updating them, and finds the pins it silently stopped seeing - tag-plus-digest regex managers for Helm values, blind spots (stranded digests, unmatched paths, discontinued tag lines, registry moves, versions an operator fills in by default), red or stuck Renovate PRs, approval backlogs and behaviour-neutral preset refactors, with a pin coverage script and an anonymous registry digest check. Use when pinning an image by digest, writing a Renovate custom or regex manager, asking why Renovate does not update an image, chart or version, a pin is months behind while the dependency dashboard looks fine, a Renovate or dependency-bot PR fails CI on a lockfile, test or generated file, bot MRs pile up or sit unmerged, the dashboard is full of updates awaiting approval, refactoring a shared Renovate preset, or checking whether a tag or digest exists in a registry.
---

# Renovate pins — pins the bot can still move

A pin no manager extracts is a freeze: the dependency dashboard stays green and the version never
moves. Every pin gets a manager, and the proof is Renovate's own extraction, not the config.

## Choose the pin shape

| Where the version lives | Pin shape | Manager |
| --- | --- | --- |
| Dockerfile `FROM`, compose, Kubernetes `image:` | `repo:tag@sha256:…` in one string | built-in `dockerfile`, `docker-compose`, `kubernetes` (the last has no default `managerFilePatterns`; add them) |
| Helm values: `repository` plus one `tag` or `version` under a key ending in `image` | `tag: v1.2.3@sha256:…` glued | built-in `helm-values`: extracts both and rewrites the whole string |
| Helm values whose chart wants separate `tag:` and `digest:` keys | two keys | regex custom manager capturing both, `helm-values` disabled for that dependency |
| Helm values under a key path not ending in `image` (`images.api.tag`) | any | regex custom manager; `helm-values` never sees it |
| A version an operator fills in when the field is empty (grafana-operator `Grafana.spec.version`, prometheus-operator `spec.version`, CloudNativePG `imageName`) | set the field explicitly | `# renovate: datasource=… depName=…` comment plus a regex custom manager |
| A shell line in CI or a script (`docker run img:tag@sha256:…`) | move it into a file a manager reads, or annotate it | `# renovate:` comment plus a regex custom manager |

`pinDigests` is off by default: Renovate adds no digest by itself, it only moves digests it extracted.

## Pin a Helm-values image with separate tag and digest

1. Read the multi-arch index digest of the tag: `python3 scripts/registry_digest.py ghcr.io/owner/app:v1.2.3`
   (anonymous; exit 0 published, 1 absent, 3 when a given `@sha256:` pin differs from the tag).
2. Write the values with `tag:` and `digest:` as adjacent keys under `repository:`.
3. Disable the built-in manager for that dependency, because it would move the tag and strand the
   digest while the container keeps running the old one. Add a regex manager that moves both:

   ```json5
   {
     packageRules: [
       { matchManagers: ["helm-values"], matchDepNames: ["ghcr.io/owner/app"], enabled: false },
     ],
     customManagers: [
       {
         customType: "regex",
         managerFilePatterns: ["/(^|/)deploy/app/values\\.ya?ml$/"],
         matchStrings: [
           'repository: (?<depName>ghcr\\.io/owner/app)\\n(?:[ \\t]*#.*\\n)*[ \\t]*tag: "?(?<currentValue>[^"\\s]+)"?\\n[ \\t]*digest: "?(?<currentDigest>sha256:[a-f0-9]{64})"?',
         ],
         datasourceTemplate: "docker",
       },
     ],
   }
   ```

4. Validate with `npx --yes --package renovate@<version the bot runs> renovate-config-validator <config file>`,
   then run the coverage check below and confirm no `unowned-digest` for that file.
5. After the rollout, the rendered container image reads `repo:tag@sha256:…` and the pod's `imageID`
   carries the same digest.

## Prove Renovate still sees every pin

Run this after adding a component, renaming or moving a directory, or changing a preset, and on a
schedule. From the repository root, with the report written to a scratch path:

```bash
npx --yes renovate@<version the bot runs> --platform=local --dry-run=extract \
  --report-type=file --report-path=/path/to/scratch/renovate-report.json
python3 scripts/pin_coverage.py --report /path/to/scratch/renovate-report.json --root .
```

- The local platform cannot resolve `local>` presets. Run in a scratch copy whose `extends` points at
  a readable copy of the preset (`github>`, `gitlab>` or another source the run can reach); never commit that edit.
- Self-hosted global config (host rules, extra managers) is not in the repository; the report shows
  what the repository and its presets extract.
- `tests`, `test`, `testdata` and `fixtures` directories and Markdown are skipped (`--include-tests`
  scans them), placeholder digests such as `sha256:000…` are ignored, and `--exclude GLOB` skips a
  file that a `postUpgradeTasks` script regenerates.

| Finding | Meaning | Fix |
| --- | --- | --- |
| `unowned-digest` | a `sha256:` digest no extracted dependency in that file carries | regex manager capturing tag and digest, or glue the digest into the tag |
| `unowned-image` | an `image:`/`imageName:` value or `FROM` line with a tag nothing extracted from that file | add the file to the manager's `managerFilePatterns` (renamed paths land here) |
| `unowned-tag` | a `repository:` plus `tag:`/`version:` pair nothing extracted | matching `managerFilePatterns`, or a regex manager when the key path does not end in `image` |
| `operator-default-version` | an operator resource without its version field runs the operator's default, so an operator bump silently changes it | set the field with a `# renovate:` comment and a regex manager |
| `unowned-operator-version` | the version field is set but no manager extracts it | regex manager for the annotated line |
| `skipped-dependency` | extracted with a `skipReason` such as `unknown-registry`, `contains-variable` or `invalid-value` | fix the source reference, registry alias or variable; a missing GitHub token is a local-run artefact (`GITHUB_COM_TOKEN`) |

Blind spots a static check cannot see; look them up with `--dry-run=lookup` or at the registry:

- **Discontinued tag line.** Docker versioning treats the text after the first hyphen as a
  compatibility suffix, so a `v1.2.3-stable` pin only moves to newer `-stable` tags. When upstream stops
  publishing that suffix the pin freezes with no error. Compare the pin with upstream's latest release.
- **Registry move that restarts the version numbers.** The old name's tags outrank the new ones. Point
  the dependency at the new repository, drop the old name from rules, and pin repository and tag as a pair.
- **Rule order.** All matching `packageRules` merge and the last one wins: an `automerge: false`
  exception placed before a blanket automerge rule is overridden. Put exceptions last.

## Fix a red Renovate PR

1. Lockfile metadata the bot did not regenerate, such as a `packageManager` bump that leaves pnpm's
   own version in the lockfile (`ERR_PNPM_FROZEN_LOCKFILE_WITH_OUTDATED_LOCKFILE`): run
   `corepack pnpm install --lockfile-only` under the new version.
2. A test that hard-codes a version the bot owns: assert the shape (`@v\d+\.\d+\.\d+$`), not the value.
3. Generated files derived from the bumped dependency (hash manifests, vendored bundles): rerun the generator.
4. Once anyone pushes to the bot's branch, Renovate stops updating it. Ticking its rebase box or adding
   the `rebase` label regenerates the branch and drops those commits, so merge it by hand once green.

## Unstick a pile of bot PRs

With the default `rebaseWhen: auto`, Renovate rebases only conflicted branches unless automerge is on
or the base requires up-to-date branches, so a quiet PR keeps a pipeline from an old base. Per open PR:

1. Check whether the base branch already has the change; close it if so.
2. Read the merge status and the head pipeline, and open the failed jobs' logs.
3. A failure unrelated to the bump that the base has since fixed means a stale base. Tick the bot's
   own box by changing ` - [ ] <!-- rebase-check -->` to ` - [x] <!-- rebase-check -->` in the PR
   description through the forge API, or add the `rebase` label. Skip branches someone pushed to.
4. Leave majors to a person.

## Approval backlogs

When every update waits for a Dependency Dashboard tick that adds no check beyond CI, the ticks
become a backlog. Where CI gates every update:

```json5
{
  prConcurrentLimit: 5,
  packageRules: [
    { matchUpdateTypes: ["patch", "minor", "pin", "digest", "pinDigest", "bump"], dependencyDashboardApproval: false },
  ],
}
```

Majors, rollbacks and replacements keep the tick, and a person still merges. Prefer this over an
automerge overlay where every merge cuts a release.

## Refactor a shared preset

A preset change reaches every consumer, so measure "no behaviour change" with Renovate's own rule
engine at the version the bot runs: [references/preset-refactor.md](references/preset-refactor.md).

## Registry facts without credentials

`scripts/registry_digest.py` follows the registry's anonymous bearer challenge (Docker Hub, GHCR,
Quay and most OCI registries) and HEADs the manifest with OCI and Docker Accept headers, so the
printed digest is the multi-arch index when one exists. It reads OCI Helm charts the same way:
`helm pull oci://…` can answer 403 for a public chart that the anonymous manifest request reads
fine, so check with the script before calling a chart private or missing.
