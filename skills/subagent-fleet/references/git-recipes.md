# Git recipes for agent fleets

Contents: [Lightweight worktree](#lightweight-worktree) ·
[Set up and remove a full worktree](#set-up-and-remove-a-full-worktree) ·
[Land from a shared checkout](#land-from-a-shared-checkout) ·
[Port and validate from exact revisions](#port-and-validate-from-exact-revisions) ·
[Update colleagues' branches by merging](#update-colleagues-branches-by-merging) ·
[Rescue orphaned work](#rescue-orphaned-work)

`$MAIN` is the main checkout, `$W`, `$S` and `$R` are worktree paths, `<trunk>` the shared
branch.

## Lightweight worktree

For docs, rules or other changes that only need the hooks to run:

```sh
git fetch origin
git worktree add -b <branch> "$W" origin/<trunk>
ln -s "$MAIN/node_modules" "$W/node_modules"
ln -s "$MAIN/vendor" "$W/vendor"
git -C "$W" status --short
```

The last command must not list the links. An ignore pattern with a trailing slash
(`node_modules/`) matches directories only, and git sees a symlink as a file, so the link shows as
untracked and `git add -A` would commit it. Ignore the name without the slash (`/node_modules`),
or add it to `.git/info/exclude`, which every worktree of the clone shares. Stacked follow-up
branches use the same pattern, one worktree per branch.

## Set up and remove a full worktree

```sh
git worktree add -b <branch> "$W" <start point>
git -C "$W" submodule update --init
(cd "$W" && mise trust -q . && <dependency install>)
```

Then give it its own database and env file. `git worktree add` initialises no submodules, a tool
manager refuses an untrusted config, and nothing is installed: a gate run before this reports
setup as a regression.

`git worktree remove` refuses a worktree with untracked files, and installed dependencies are
untracked. Run the inventory first; when it shows nothing but dependencies, delete those
directories or remove with `--force`. A step that needs root (a TLS store, a privileged daemon)
goes to a person with the exact command; finish the setup without it when the tests do not
need it.

## Land from a shared checkout

`git commit` takes the whole index, so a bare commit carries whatever a peer staged.
`git commit -- <paths>` takes the working-tree content of those paths, so it would also carry a
peer's unstaged edit of the same file. The replay in the SKILL.md
([Land the work](../SKILL.md#land-the-work)) is safe against both: `cherry-pick --no-commit`
refuses when the commit touches a file with local changes. That error suggests stashing; in a
shared checkout the stash list is shared too, so land from a clean worktree of your own instead.

Before deleting the agent branch, `git diff --stat <agent-branch> HEAD -- <its files>` prints
nothing.

## Port and validate from exact revisions

A working tree shows whatever happens to be checked out, and other sessions switch it.

- Port a file: `git -C <repo> show <rev>:<path> > <dest>`.
- Validate with the version of a tool that is under review, not the copy in a working tree:
  `git worktree add --detach "$V" <rev>` and run it from `$V`.

## Update colleagues' branches by merging

1. **Trial** in a scratch detached worktree with hooks off, and record which branches conflict:

   ```sh
   git worktree add -q --detach "$S" origin/<trunk>
   git -C "$S" checkout -q --detach origin/<branch>
   git -C "$S" -c core.hooksPath=/dev/null merge -q --no-edit origin/<trunk>
   ```

   A merge rewrites no SHAs, keeps open reviews intact, and usually conflicts less than a rebase
   or a cherry-pick.
2. **Clean merge**: run the gate on the result, then push it normally:
   `git -C "$S" push origin HEAD:refs/heads/<branch>`.
3. **Many conflicts**: hand the merge to an agent with explicit resolution rules
   ([briefs.md](briefs.md#agent-that-merges-trunk-into-someone-elses-branch)) and keep it local.
   Review it before pushing: a merge can quietly bring back files trunk deleted. List what the
   result has that trunk lacks with `git diff --name-only --diff-filter=A origin/<trunk> HEAD` and
   check each against what the branch meant to add.
4. Leave a short note on the merge request saying what was pushed and why.
5. Delete a spent branch, one whose commits are all on trunk, only with its owner's or the user's
   OK; a remote delete cannot be undone.

## Rescue orphaned work

Uncommitted work in a shared checkout exists on no ref.

1. **Prove it is nowhere else**: `git log --all --oneline -S '<identifier from the change>'`
   prints nothing; `fleet_inventory.py` shows every worktree, unpushed commit and stale branch.
   Check other projects' scratch directories too.
2. **Find the author**: `transcript_calls.py --around <one of its files>`. An authoring session
   that asked a question and never got an answer is the usual story.
3. **Save it**: `git diff -- <paths> > wip.patch && git apply --check -R wip.patch`. `git diff`
   leaves out untracked files: list them with `git ls-files --others --exclude-standard -- <paths>`
   and copy them beside the patch.
4. **Rebuild** on a fresh branch from current trunk in its own worktree
   (`git worktree add -b <branch> "$R" origin/<trunk> && git -C "$R" apply <abs path>/wip.patch`),
   finish it there, push the branch and open a pull request.
5. **After the merge**, and only then: confirm the shared copy is unchanged
   (`git diff -- <paths> | diff -q - wip.patch`), restore exactly those paths, remove the copied
   untracked files, and `git merge --ff-only origin/<trunk>`.
