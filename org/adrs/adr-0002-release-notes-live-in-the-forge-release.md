---
status: proposed
date: 2026-09-17
decision-makers: Ryan Grippeling
---

# Release notes live in the forge Release, and CI stops committing CHANGELOG.md

Technical Story: owner request (2026-09-17), after
[twente.dev run 442](https://forgejo.webgrip.dev/webgrip/twente.dev/actions/runs/442) failed the
promotion job for the fourth release candidate in a row. The cause was not the release: it was
`CHANGELOG.md`, the one file both release branches write on a schedule.

## Context and Problem Statement

[`@webgrip/semantic-release-config`](https://forgejo.webgrip.dev/webgrip/semantic-release-config)
states its own position in its header: *"CHANGELOG.md is always written and committed."* It loads
`@semantic-release/changelog` and `@semantic-release/git` on every repository, and the branch
model is `main` = stable, `development` = rc prerelease. So both branches write the same file,
independently, on every release.

The consequences compound:

* **The rc entries are a draft of the stable entry, kept forever beside the finished version.**
  Measured on `twente.dev`'s 0.2.0 cycle: the stable `0.2.0` section holds 53 entries, the
  `0.2.0-rc.*` sections hold 58 between them, and **47 appear in both**. Eleven exist only under
  an rc — changes made and withdrawn inside the cycle, which a reader of the release notes
  should not see.
* **The branches diverge permanently on that file.** The stable release commit lands on `main`
  and never returns to `development`, while `development` keeps appending rc sections. Nothing in
  the release train carries one back to the other.
* **The workaround has been applied twice and still does not hold.** `twente.dev` set
  `CHANGELOG.md merge=union` (`e450e7f`), then set it again for the base side of a promotion
  (`ad8b3a5`, *"git reads merge attributes from the side being merged into"*). Both are correct:
  a real `git merge` resolves cleanly, while the default text driver conflicts — verified with
  `git merge-file`, exit 1, three conflict markers. But Forgejo's mergeability probe does not
  read the tree's `.gitattributes`, falls back to the text driver, sees the conflict, and marks
  the promotion PR unmergeable. The promotion job reads that flag and fails.
* **Each failure is written back as a commit status**, so every subsequent rc fails the same way
  until a human intervenes.

Upstream is unambiguous about the mechanism. The `@semantic-release/git` README opens with a
warning — *"You likely do not need this plugin to accomplish your goals with semantic-release"* —
pointing at the FAQ entry
[making commits during the release process adds significant complexity](https://semantic-release.gitbook.io/semantic-release/support/faq#making-commits-during-the-release-process-adds-significant-complexity),
which states that *"making commits and pushing them back to the repository adds significant
additional complexity to your release process that can be avoided."* It names two costs, and both
are live in this estate:

| Upstream cost | How it shows up here |
| --- | --- |
| Branch protection must let the release account bypass what humans cannot, *"which might require elevating the access level of the release user beyond what would otherwise be desired/considered secure"* | `main` is push-restricted to `webgrip-ci` and the owner precisely so the release commit can land |
| Pre-commit hooks must be accounted for in the release process | `lefthook` runs in several repos |

The failure this record responds to is a third cost upstream does not list, because it only
appears with two release branches: the changelog becomes a file with two writers and no merge
authority.

Upstream's recommendation is to check whether the forge's own release objects already do the job,
and it offers a middle ground: *"having a `CHANGELOG.md` in your repository that only contains a
link to the project's GitHub releases could be an acceptable middle ground."* This estate already
publishes full notes to the forge — `@saithodev/semantic-release-gitea` creates a Forgejo Release
carrying the generated notes on every release, stable and rc alike. The committed file is a second
copy of something that already exists.

Scope: this record covers what CI writes back to a repository at release time. It does not change
the branch model, the conventional-commit vocabulary, or the notes toolchain.

## Decision Drivers

* A release must not be able to block the next release.
* One file, one writer. A file two automated processes append to needs a merge authority, and
  there is none.
* No workaround whose correctness depends on an undocumented forge internal.
* The release account should need as little write access as the job actually requires.
* Release notes stay discoverable, including from a mirror and at a given commit.

## Considered Options

* **Stop committing the changelog where it is the only reason to commit: notes live in the Forgejo
  Release, `CHANGELOG.md` becomes a committed pointer**
* Write the changelog on the stable branch only
* Keep both writers, automate a back-merge from `main` to `development` after every promotion
* Changelog fragments assembled at release time (towncrier / changesets shape)
* Status quo: keep `merge=union` and repair by hand when it fails

## Decision Outcome

Chosen option: **stop committing the changelog in repositories where it is the only git asset**,
because it removes the release commit entirely rather than making the release commit merge better,
and because the content it protects already exists in the forge Release.

* For a repository with no `manifest` option, `makeConfig` resolves `gitAssets` to exactly
  `['CHANGELOG.md']`. `@semantic-release/git` therefore exists solely to commit the changelog.
  Dropping `@semantic-release/changelog` and `@semantic-release/git` for that class means a
  release produces **no commit at all** — only a tag and a Forgejo Release.
* `CHANGELOG.md` is replaced once, by hand, with a short pointer to the repository's Releases
  page, and is never written by CI again. The path keeps meaning for anyone who looks for it.
* **Repositories that publish an npm package or a Helm chart are out of scope.** There
  `gitAssets` also carries `package.json`, `package-lock.json` or `Chart.yaml`, which consumers
  read from the tree, so the commit-back earns its complexity. Those repositories keep the
  current behaviour and take the companion measure below.
* **Companion, for every repository that still commits at release time:** the release workflow
  back-merges `main` into `development` after a promotion, with `--no-ff`, which is also what the
  `@semantic-release/git` README recommends for branches semantic-release owns. Without it the
  two branches never reconverge.
* `merge=union` on `CHANGELOG.md` stays where it is. It becomes belt-and-braces instead of
  load-bearing, and removing it is not worth a second migration.

### Consequences

* Good, because a release stops producing a commit, so it cannot diverge two branches, cannot
  conflict, and cannot block the next release.
* Good, because `webgrip-ci` no longer needs push access to a protected `main` in those
  repositories — the exact elevation upstream warns about, removed rather than managed.
* Good, because the duplication goes with it: no more 47-of-58 entries written twice, and no
  withdrawn-mid-cycle changes preserved in the notes.
* Good, because it removes a workaround that depends on Forgejo reading `.gitattributes` during
  conflict detection, which it does not do and has never promised to.
* Bad, because the notes leave the repository. A clone or the Codeberg mirror carries tags and
  commits but no Release objects, so "what shipped when" is regenerable from conventional commits
  rather than readable directly. This is the real cost of the decision and the reason the pointer
  file exists.
* Bad, because it splits the estate into two behaviours — with and without a release commit —
  which the shared config must express and document rather than hide.
* Bad, because repositories that keep the commit-back keep the underlying divergence; the
  back-merge contains it, it does not remove it.

### Confirmation

1. For a repository with no `manifest`, the resolved plugin list contains neither
   `@semantic-release/changelog` nor `@semantic-release/git`:
   `npx semantic-release --dry-run` prints the plugin chain.
2. A release on such a repository creates a tag and a Forgejo Release whose body is non-empty,
   and `git log <previous-tag>..<tag>` contains no `chore(release):` commit.
3. After a promotion, `git log origin/main ^origin/development --oneline` is empty for every
   repository on the two-branch model.
4. The promotion PR reports mergeable in Forgejo's API without `merge=union` being consulted:
   `curl -s .../api/v1/repos/webgrip/<repo>/pulls/<n> | jq .mergeable` is `true`.
5. `webgrip-ci` is absent from the push allow-list on `main` for in-scope repositories.

## Pros and Cons of the Options

### Notes in the forge Release, changelog becomes a pointer

* Good, because it removes the mechanism rather than the symptom, and it is what upstream
  recommends considering first.
* Good, because it reduces what the release account may write.
* Bad, because the notes are no longer in the tree, and a mirror without the forge loses them.

### Changelog on the stable branch only

* Good, because it keeps the file in the tree and still leaves exactly one writer.
* Good, because it is a smaller change than removing the file's content.
* Bad, because `main` still takes a release commit `development` lacks, so the back-merge is still
  required and the release account still needs protected-branch access — two of the three costs
  survive.
* Bad, because semantic-release has no per-branch plugin configuration; the shared config would
  have to infer the branch from CI environment variables, and a wrong inference silently produces
  either no changelog or an unexpected commit.

### Keep both writers, automate the back-merge

* Good, because it is the smallest possible change and needs no estate-wide coordination.
* Good, because it is required anyway for repositories that keep the commit-back.
* Bad, because it leaves the duplication, the union-merge dependency and the protected-branch
  elevation exactly as they are.
* Bad, because it repairs a divergence the estate creates on purpose, every cycle, forever.

### Changelog fragments assembled at release

* Good, because two changes never touch the same file, so conflicts become structurally
  impossible rather than merged around.
* Good, because it is the answer large multi-contributor projects converge on.
* Bad, because it needs tooling and contributor discipline that a mostly-solo estate does not
  have, to solve a problem the chosen option removes for free.

### Status quo

* Good, because it costs nothing today.
* Bad, because it has already failed three times: `e450e7f`, `ad8b3a5`, and run 442. Each repair
  addressed the merge; none addressed the probe that decides whether the merge is allowed to
  happen.

## More Information

* [ADR-0001](adr-0001-no-comments-in-code.md) — the other estate-wide record
* [`org-guidelines.md`](../org-guidelines.md) · [`forgejo-ci.md`](../forgejo-ci.md) — Forgejo is
  the release authority, and the traps that fail silently
* [`@semantic-release/git` README](https://github.com/semantic-release/git) and the FAQ entry it
  links — the upstream position quoted above
* [twente.dev ADR 0019](https://forgejo.webgrip.dev/webgrip/twente.dev/src/branch/main/docs/adrs/0019-release-driven-deploys.md)
  — the branch model this record leaves untouched
* 2026-09-17 — proposed, after run 442. `twente.dev` took the companion back-merge by hand
  (`c0b4be2`) to unblock the promotion; nothing in the shared config has changed yet.
