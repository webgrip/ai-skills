# Surfaces outside the scanner

Commands for the surfaces `scan_boundary.py` does not read. `TERMS` is a short alternation of the
strongest markers (`globex|sibling estate|GBX-[0-9]+`); keep it in the shell, not in a file in the
repo. Every list endpoint pages: keep `--paginate` or the page loop.

- [Branches that are not local yet](#branches-that-are-not-local-yet)
- [Worktrees and ignored files](#worktrees-and-ignored-files)
- [Wikis](#wikis)
- [GitHub](#github)
- [GitLab](#gitlab)
- [Forgejo and Gitea](#forgejo-and-gitea)
- [Edit history](#edit-history)

## Branches that are not local yet

`--all-refs` reads local branches, remote-tracking branches and tags. Fetch first, then add the
refs that keep closed and rejected work reachable:

```sh
git fetch --all --prune --tags
git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'
git fetch origin '+refs/merge-requests/*/head:refs/remotes/origin/mr/*'
scan_boundary.py --org globex --all-refs REPO
```

The first refspec is GitHub's and Forgejo's, the second GitLab's.

## Worktrees and ignored files

```sh
git -C REPO worktree list --porcelain | sed -n 's/^worktree //p' | while read -r tree; do
  scan_boundary.py --org globex --untracked "$tree"
done
git -C REPO ls-files -z --others --ignored --exclude-standard | xargs -0 grep -I -l -i -E "$TERMS"
```

Agent worktrees under `.claude/worktrees/` appear in the list. Ignored files include build output
and dependencies; a hit there usually means a cache or a generated file to delete.

## Wikis

A GitHub, GitLab or Forgejo wiki is its own git repository (`REPO.wiki.git`): clone it and run
the scanner on the clone.

## GitHub

```sh
gh pr list --state all --limit 1000 --json number,title,body \
  --jq ".[] | select((.title + \" \" + (.body // \"\")) | test(\"$TERMS\"; \"i\")) | .number"
gh issue list --state all --limit 1000 --json number,title,body \
  --jq ".[] | select((.title + \" \" + (.body // \"\")) | test(\"$TERMS\"; \"i\")) | .number"
gh api --paginate 'repos/{owner}/{repo}/issues/comments?per_page=100' \
  --jq ".[] | select(.body | test(\"$TERMS\"; \"i\")) | .html_url"
gh api --paginate 'repos/{owner}/{repo}/pulls/comments?per_page=100' \
  --jq ".[] | select(.body | test(\"$TERMS\"; \"i\")) | .html_url"
gh api 'repos/{owner}/{repo}/releases' --jq '.[] | .tag_name + " " + .name + " " + (.body // "")'
gh variable list; gh variable list --env ENVIRONMENT; gh variable list --org ORG
gh secret list; gh secret list --org ORG
gh api --paginate 'orgs/ORG/packages?package_type=container' --jq '.[].name'
gh api 'repos/{owner}/{repo}/hooks' --jq '.[].config.url'
```

Secret values are write-only; check secret names and the workflows that read them. Variables,
webhook URLs and package names show hosts and organisation names directly.

## GitLab

```sh
glab api --paginate 'projects/:id/merge_requests?state=all&per_page=100' \
  | jq -r ".[] | select(((.title // \"\") + \" \" + (.description // \"\")) | test(\"$TERMS\"; \"i\")) | .web_url"
for iid in $(glab api --paginate 'projects/:id/merge_requests?state=all&per_page=100' | jq -r '.[].iid'); do
  glab api --paginate "projects/:id/merge_requests/$iid/notes?per_page=100" \
    | jq -r --arg mr "$iid" ".[] | select(.body | test(\"$TERMS\"; \"i\")) | \"MR \(\$mr) note \(.id)\""
done
```

Repeat both for issues (`projects/:id/issues`, `issues/$iid/notes`). The list endpoints' `search=`
parameter matches titles and descriptions only, never notes.

```sh
glab variable list --per-page 100 --output json
glab variable list --group GROUP --per-page 100 --output json
glab api 'projects/:id/registry/repositories' | jq -r '.[].path'
glab api --paginate 'projects/:id/packages?per_page=100' | jq -r '.[].name'
glab api 'projects/:id/releases' | jq -r '.[] | .tag_name + " " + .name + " " + (.description // "")'
glab api 'projects/:id/hooks' | jq -r '.[].url'
```

Project variables include the environment-scoped ones; read names and values.

## Forgejo and Gitea

Same surfaces under `/api/v1`, with a token in `Authorization: token …`:

| Surface | Endpoint |
| --- | --- |
| Issues and pull requests | `repos/OWNER/REPO/issues?state=all&type=pulls` and `type=issues` |
| Every comment in the repo | `repos/OWNER/REPO/issues/comments` |
| Actions variables | `repos/OWNER/REPO/actions/variables`, `orgs/ORG/actions/variables` |
| Packages and container images | `packages/OWNER` |
| Releases | `repos/OWNER/REPO/releases` |
| Webhooks | `repos/OWNER/REPO/hooks` |

Page with `page` and `limit` until a page comes back empty.

## Edit history

Removing a marker from a description or note leaves the earlier revision on forges that keep
edit history. On GitHub anyone with read access sees a comment's earlier revisions until each is
deleted from the history (comment author or anyone with write access, in the comment's edit
history menu). Check the same on every forge in use before calling forge text clean.
