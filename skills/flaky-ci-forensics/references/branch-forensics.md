# Who rewrote the branch?

Collect every ref change from every source into one UTC timeline, then explain each change by an
actor. Read-only throughout; nothing here needs server access.

## Sources

| Source | Command | What it gives |
| --- | --- | --- |
| GitHub activity | `gh api 'repos/OWNER/REPO/activity?ref=refs/heads/main&per_page=100'` (`&activity_type=force_push` to narrow) | `before`, `after`, `actor.login`, `activity_type`, `timestamp` per ref change |
| GitLab project events | `glab api 'projects/:id/events?action=pushed&per_page=100'` | `push_data.ref`, `commit_from`, `commit_to`, `author`, `created_at`; bulk pushes carry no commit details |
| Forgejo or Gitea feed | `GET /api/v1/repos/OWNER/REPO/activities/feeds?date=YYYY-MM-DD` | pushes with actor and time; public repos answer without a token |
| CI runs | GitHub runs `head_sha`; GitLab pipelines `sha` and `before_sha`; the checkout step in each job log | which SHA each run fetched, so when the branch pointed where |
| Mirrors | the mirror's own activity API (same commands, mirror repo) | pushes the mirror received and when |
| Every local clone | `git -C CLONE reflog show --date=iso-strict refs/remotes/origin/main` | `update by push` = this clone pushed; `fetch: forced-update` = it arrived rewritten |
| Agent sessions | `grep -l '"git push' ~/.claude/projects/*/*.jsonl`, then read the matching commands and their times | pushes agents made, including `--force`, `--force-with-lease` and `+refs/...` refspecs |

- Worktrees share their clone's remote-tracking reflog; separate clones each have their own, so check every clone on every machine that pushes.
- GitLab events do not flag force pushes: a rewrite is a push whose `commit_from` is not an ancestor of its `commit_to` (`git merge-base --is-ancestor FROM TO` exits 1).
- Normalise every time to UTC before sorting; forge APIs answer in UTC, reflogs and transcripts in local time unless told otherwise (`TZ=UTC git reflog show --date=iso-strict-local`).

## Reading the timeline

- A ref change with a feed entry names its actor; match it to a CI job (release bots push from CI) or to a clone's `update by push` and an agent transcript.
- A ref change with **no feed entry, no CI run and no client push** happened inside the forge: a push mirror or other server-side sync writing an older ref set back, a server hook, or an admin. Look at the forge's mirror configuration and its version's known issues next.
- A release that skipped a commit points at a job that reset to the remote head; the release job should fail when its triggering commit is no longer an ancestor of the branch (`git merge-base --is-ancestor "$SHA" "origin/$BRANCH"`).

## Recover

The lost commit is the `before` of the rewrite, a reflog entry, or a CI run's SHA. Pin it before
anything else (`git branch rescue/BRANCH-SHORTSHA SHA && git push origin rescue/BRANCH-SHORTSHA`),
then restore it with an ordinary merge or cherry-pick; a force-push back is a decision for the
branch owners.
