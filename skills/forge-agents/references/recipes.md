# Forge CLI and API recipes

Placeholders: `$P` is the URL-encoded GitLab project path (`group%2Fproject`), `$IID` an MR iid,
`$SHA` a full commit SHA, `$O/$R` a GitHub or Forgejo owner and repo, `$FORGE` a Forgejo base URL.

## Contents

- [Bodies and descriptions](#bodies-and-descriptions)
- [GitLab MR state, threads and pipelines](#gitlab-mr-state-threads-and-pipelines)
- [GitHub](#github)
- [Forgejo and Gitea](#forgejo-and-gitea)

## Bodies and descriptions

Write a long body to a file, pass the file, then read it back: `glab mr update` has printed success
without saving the description.

```sh
glab mr create -R group/project --source-branch "$BRANCH" --target-branch main \
  --title "Draft: $TITLE" --description "$(cat body.md)" --remove-source-branch --yes
glab mr update "$IID" --description "$(cat body.md)"
glab api "projects/$P/merge_requests/$IID" | jq -r .description | diff - body.md
gh pr create -R "$O/$R" --base main --head "$BRANCH" --title "$TITLE" --body-file body.md --draft
gh pr view "$NUMBER" -R "$O/$R" --json body --jq .body | diff - body.md
tea pr create --repo "$O/$R" --head "$BRANCH" --base main --title "WIP: $TITLE" --description "$(cat body.md)"
```

When the CLI drops the write, PUT or PATCH the body through the API with the CLI's stored token. A
prefilled compare URL (`?expand=1&title=…&body=…`) is too long for a full body.

## GitLab MR state, threads and pipelines

- **Merge state:** `detailed_merge_status` (`discussions_not_resolved`, `not_approved`, …),
  `blocking_discussions_resolved`, `has_conflicts`, `head_pipeline`.

  ```sh
  glab api "projects/$P/merge_requests/$IID" \
    | jq '{detailed_merge_status, blocking_discussions_resolved, has_conflicts, pipeline: .head_pipeline.status}'
  ```

- **Watch the MR's pipeline** through `head_pipeline`. `pipelines?sha=` matches only the full SHA, so
  a short SHA loops forever; `glab ci list -b` misreads the branch value. Poll with a bound:

  ```sh
  for attempt in $(seq 1 60); do
    state=$(glab api "projects/$P/merge_requests/$IID" | jq -r '[.head_pipeline.sha, .head_pipeline.status] | @tsv')
    case "$state" in "$SHA"$'\t'success|"$SHA"$'\t'failed|"$SHA"$'\t'canceled) echo "$state"; break;; esac
    sleep 20
  done
  ```

- **Job log without colour codes:** `glab api "projects/$P/jobs/$JOB_ID/trace" | sed 's/\x1b\[[0-9;]*m//g'`
- **Failures that predate the MR:** `glab api "projects/$P/jobs?scope[]=failed&per_page=100"`.
- **Validate CI config against a branch:** `POST projects/$P/ci/lint` with `{"content": …, "ref": "$BRANCH"}`;
  `glab ci lint` agrees with it, and editor warnings on `!reference` are false.

  ```sh
  python3 -c 'import json,sys; print(json.dumps({"content": open(".gitlab-ci.yml").read(), "ref": sys.argv[1]}))' "$BRANCH" > lint.json
  glab api -X POST "projects/$P/ci/lint" --input lint.json -H 'Content-Type: application/json'
  ```

- **A pipeline that failed with zero jobs:** the GraphQL `errorMessages` field says why; the
  `flaky-ci-forensics` skill owns that diagnosis.
- **`--paginate` concatenates JSON arrays** (`[…][…]`); split before parsing:

  ```sh
  glab api --paginate "projects/$P/merge_requests/$IID/discussions" \
    | python3 -c 'import json,re,sys; raw=sys.stdin.read().strip(); print(json.dumps([d for chunk in re.split(r"(?<=\])\s*(?=\[)", raw) for d in json.loads(chunk)]))'
  ```

  `jq -s 'add'` does the same.
- **Reply to a review thread and resolve it:** find the discussion holding the note, reply, resolve.
  Leave threads that carry a review bot's commands to the MR author; some bots act only on the
  author's resolve.

  ```sh
  discussion=$(glab api --paginate "projects/$P/merge_requests/$IID/discussions" \
    | jq -s -r --argjson note "$NOTE_ID" 'add | .[] | select(any(.notes[]; .id == $note)) | .id')
  glab api -X POST "projects/$P/merge_requests/$IID/discussions/$discussion/notes" -f body="$REPLY"
  glab api -X PUT "projects/$P/merge_requests/$IID/discussions/$discussion" -f resolved=true
  ```

  Unresolved threads: `.notes[0].resolvable and (.notes[0].resolved | not)`.
- **Find which projects in a group carry a file:** list the group's projects with their default
  branches, then probe `projects/:id/repository/files/:path/raw?ref=:branch` in parallel; a 404 means
  absent.

## GitHub

- **Check runs, not statuses:** `gh pr checks "$NUMBER" -R "$O/$R"`, or
  `gh api "repos/$O/$R/commits/$SHA/check-runs" --jq '.check_runs[] | {name, status, conclusion}'`.
  The combined `/commits/$SHA/status` lists only commit statuses, which Actions does not post.
- **Pin `gh`** in the repo's tool manager so every agent runs the same version; `gh auth login --web`
  needs the human at the keyboard.
- **Unauthenticated calls** share 60 requests an hour per IP; parallel agents hit it at once.
- **Enterprise Cloud with data residency:** web `<sub>.ghe.com`, API root `https://api.<sub>.ghe.com`
  (no `/api/v3` path), SSH `<sub>@<sub>.ghe.com:OWNER/REPO.git`.

## Forgejo and Gitea

- `tea` has no raw `api` subcommand: call the API with `curl` and the token `tea` stored for the
  login.

  ```sh
  curl --fail -X PATCH -H "Authorization: token $FORGE_TOKEN" -H 'Content-Type: application/json' \
    "$FORGE/api/v1/repos/$O/$R/pulls/$NUMBER" --data @body.json
  ```

- Role check before acting on a mention: `GET $FORGE/api/v1/repos/$O/$R/collaborators/$USER/permission`.
- Draft pull requests are a title prefix: `WIP:` or `[WIP]` by default (`WORK_IN_PROGRESS_PREFIXES`).
- Forgejo's per-job token is refused by the package registry (401 `reqPackageAccess`); publish with
  a bot user's token.
- When an editor's forge connector is not authorised, the CLI with its own login still works.
