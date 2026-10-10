# Rewriting history to remove a name or an address

Only after the decision table in the SKILL.md says so. Keep this plan, the mailmap and the
replacements file outside the repo being rewritten. Tool: `git filter-repo` (a separate install,
for example `brew install git-filter-repo` or `pipx install git-filter-repo`).

- [Before](#before)
- [Record the tip trees](#record-the-tip-trees)
- [Rewrite an address](#rewrite-an-address)
- [Rewrite a name](#rewrite-a-name)
- [Prove nothing else changed](#prove-nothing-else-changed)
- [Submodules](#submodules)
- [Push](#push)
- [Purge the forge](#purge-the-forge)
- [After](#after)

## Before

1. Clean HEAD first with ordinary commits until the content scan is clean, functional references
   allow-listed. The rewrite then has a hard proof: every branch tip keeps its tree.
2. Pilot on the smallest affected repo; the rest follow one at a time.
3. Stop other agent sessions and bots that push to the repo. Land or close open MRs/PRs; a rewrite
   disrupts open ones, and closed ones may stop showing their diffs.
4. Write down what breaks and tell its owners: links that cite commit hashes, Go pseudo-versions
   and other pins by hash, commit and tag signatures (filter-repo strips them), submodule pins in
   parent repos, existing clones, CI caches.
5. Back up and work on separate mirrors:

   ```sh
   git clone --mirror URL backup.git
   git clone --mirror URL work.git
   ```

   filter-repo refuses anything but a fresh clone; from a local path clone with `--no-local`
   rather than passing `--force`.

## Record the tip trees

```sh
tips() { git -C "$1" for-each-ref --format='%(refname)' refs/heads refs/tags |
  while read -r ref; do echo "$ref $(git -C "$1" rev-parse "$ref^{tree}")"; done; }
tips backup.git > before.txt
```

## Rewrite an address

`mailmap.txt`, one line per old address:

```text
Pat Example <pat@acme.example> <pat@globex.example>
```

```sh
git -C work.git filter-repo --mailmap ../mailmap.txt
git -C work.git log --all --format='%ae%n%ce' | sort -u
git -C work.git for-each-ref --format='%(taggeremail)' refs/tags | sort -u
```

## Rewrite a name

`replacements.txt`, Python regexes, with a negative lookahead for every functional reference that
must stay byte-identical:

```text
regex:(?i)globex/infra==>an earlier reference deployment
regex:(?i)globex(?!\.example/public/base-image)==>upstream
```

```sh
git -C work.git filter-repo --replace-text ../replacements.txt --replace-message ../replacements.txt
git -C work.git rev-list --all | xargs git -C work.git grep -I -i -P 'globex(?!\.example/public/base-image)' | wc -l
git -C work.git log --all -i --grep=globex --format=%h | wc -l
```

Both counts must be 0 (`git grep -P` needs a git built with PCRE; without it, filter the
`git grep -i globex` lines by hand). Branch and tag names are not rewritten; rename them separately.

The cleanup commits from step 1 of **Before** usually become empty once the same replacement
reaches their parents, and filter-repo drops them; pass `--prune-empty never` to keep them. Rewriting an address and a name together is one run:
`--mailmap ../mailmap.txt --replace-text ../replacements.txt --replace-message ../replacements.txt`.

## Prove nothing else changed

```sh
tips work.git > after.txt
diff before.txt after.txt
```

The diff must be empty. A difference means the rewrite touched HEAD content: stop and fix the
replacements, starting again from a fresh `work.git`.

## Submodules

Rewrite a submodule's repo before its parents. filter-repo does not remap a parent's gitlinks, so
the parent's old commits keep pinning submodule commits that only the backup holds. Either map
the parent's pins through the submodule's `work.git/filter-repo/commit-map` with a
`--commit-callback` tried on the pilot first, or accept that old parent checkouts lose their
submodule.

## Push

1. Lift branch protection for the push only.
2. `git -C work.git push --force --mirror`. Forges reject updates to `refs/pull/*` and
   `refs/merge-requests/*`; that is expected.
3. Restore protection at once, then resume the bots.

## Purge the forge

The old commits stay reachable by hash until the forge drops them.

| Forge | Step |
| --- | --- |
| GitLab | Settings, Repository, Repository maintenance: upload `filter-repo/commit-map` (split it with `split -l 20000` when the upload times out) and start the cleanup. MR commits, pipelines and change details tied to removed internal refs become unavailable. |
| GitHub | PR refs and cached views go only through GitHub Support, which acts on sensitive data only; otherwise assume the old commits stay reachable by hash. Forks belong to their owners. |
| Forgejo, Gitea | Pull requests keep `refs/pull/N/head` on the server; old commits stay reachable through them until those refs go and an admin runs repository garbage collection. |

## After

- Everyone deletes old clones and clones fresh; a push from an old clone brings the old history
  back.
- Clear CI caches that hold old objects.
- Update the hash links and pins listed in step 4 of **Before**.
- Rescan with `scan_boundary.py --all-refs` and record the new clean SHA for the periodic re-check.
