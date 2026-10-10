---
name: flaky-ci-forensics
description: Diagnoses flaky tests and red CI jobs with evidence instead of retries - counts how often the same assertion failed across pipelines and merge requests through the GitLab or GitHub API, proves or rules out the CI image by digest and layer content, fixes timing, ordering and shared-state flakes, and proves each fix with a repeat loop plus a break-check. Use when a test or CI job fails intermittently, only in CI, or only under load; when asked whether a red pipeline is my change or a flake, or whether to retry or rerun it; when a flaky-test fix, a new test or a new CI check needs proof that it can fail and actually runs; when a skipped job looks green; when a GitLab pipeline fails with zero jobs or a scheduled pipeline would also run releases; when two builds of one Docker image differ in size or digest; when commits vanished or a branch was force-pushed and someone asks who rewrote it; or when a pre-commit or lint hook is slow.
---

# Flaky CI forensics — evidence before retries

Retry once to learn something, never to get green. Every verdict below rests on a count, a digest or
a run you watched fail.

## Pick the move

| Symptom | Go to |
| --- | --- |
| Red job on a change, "is it mine?" | [Triage a red job](#triage-a-red-job) |
| Test fails sometimes, or only in CI | [Count recurrence](#count-recurrence), then [Fix the flake](#fix-the-flake) |
| Passes locally, fails in CI; image or runner suspected | [Prove or rule out the environment](#prove-or-rule-out-the-environment) |
| A flake fix, a new test or a new CI check to land | [Prove it can fail](#prove-it-can-fail) |
| Pipeline failed with zero jobs, a job never ran, a schedule to add | [Pipeline traps](#pipeline-traps) |
| Commits vanished, branch rewritten, "who force-pushed?" | [Who rewrote the branch](#who-rewrote-the-branch) |
| Pre-commit or lint hook is slow | [Slow hooks](#slow-hooks) |

## Triage a red job

Work down the list; stop when one step settles it.

1. **Does the change touch the failing code?** `git diff --stat origin/main...HEAD -- <failing test> <code it covers>`. Is trunk's latest pipeline green?
2. **Which job blocks?** A red job marked `allow_failure: true` (GitLab) or `continue-on-error` (GitHub) did not fail the pipeline; find the one that did.
3. **Reproduce locally**: the test alone in a loop (`scripts/repeat_run.py`), then the suite the way CI runs it (same parallelism, same database setup).
4. **Retry the job once** (GitLab `POST /projects/:id/jobs/:job_id/retry`; GitHub `gh run rerun <run-id> --failed`), then start a **new pipeline on the same commit** (GitLab `POST /projects/:id/merge_requests/:iid/pipelines`; GitHub `gh workflow run <file> --ref <branch>` for a `workflow_dispatch` workflow, or close and reopen the pull request). A retry reuses the pipeline; a new one re-evaluates rules, variables and image pulls.
5. **Run the same job on trunk's last pipeline.** Red there too means it predates the change.
6. **Count recurrence** of the exact assertion across other changes (next section).
7. **Compare the image digest** of a failing and a passing run.

Pre-existing flake = the same assertion failed on other changes or on trunk, or a fresh pipeline on
the same commit passes with the same image. Then unblock with one rerun and file a flake ticket that
carries the count; the merge-gate rules (skipped counts as passed, one bounded rerun) live in the
product-owner skill. Otherwise the change broke it.

## Count recurrence

`scripts/ci_recurrence.py` lists every failed job of one name whose log contains the text, with the
spread across pipelines, merge requests and branches. Read-only GETs; token from the environment.

```bash
GITLAB_TOKEN=... python3 scripts/ci_recurrence.py gitlab --project group/app \
  --job phpunit --grep 'CurrencyConversionTest > converts every order line' --since YYYY-MM-DD
GITHUB_TOKEN=... python3 scripts/ci_recurrence.py github --repo owner/app --workflow ci.yml \
  --job 'test \(.*\)' --grep 'AssertionError: expected 3 retries' --log-dir /tmp/ci-logs
```

- **Grep the test name or the assertion**, never the job's last line; `exit code 1` matches every failure.
- `--job` is a regular expression matched in full (matrix jobs: `'test \(.*\)'`). `--regex` makes `--grep` one too.
- GitLab needs `read_api`; GitHub job logs need a token even on public repos. Self-hosted: `--api-url`.
- It counts failed attempts that a green re-run hides (`attempt 1/2` on GitHub; GitLab lists retried jobs).
- `--log-dir` keeps every scanned log, so the next question (top offenders, a second assertion) costs no API calls.
- Exit 0 = found, 1 = none, 2 = API or argument error. `--json` for the full record.

"3 of 9 failed `phpunit` jobs, on 3 merge requests and trunk" is a pre-existing flake. One hit on your
change alone, with a green fresh pipeline, still gets the local loop before you call it noise.

## Prove or rule out the environment

- **Same digest rules the image out.** GitLab's docker executor logs `Using docker image sha256:... for IMAGE with digest REPO@sha256:...`; `docker pull` prints `Digest: sha256:...`. `ci_recurrence.py` shows the digest per match; grep one passing job's log for the same line. The Kubernetes executor prints none, so pin images by digest or print it in the job.
- **Different digests: compare content, never size.** BuildKit puts a file with unchanged content back into a later `COPY . .` layer when only its mtime changed, so two builds of one commit from different checkouts differ in size and digest. `python3 scripts/layer_diff.py A-LAYERS... --against B-LAYERS...` flattens both images and answers `equivalent` when only mtimes differ. Fetching manifests and blobs, and the mechanism → [references/images.md](references/images.md).
- **Load is environment too.** A busy runner stretches every timing; reproduce with parallel runs (`repeat_run.py -j 4`) or the suite in parallel, and record `uptime`.

## Fix the flake

| Mechanism | Tell | Fix |
| --- | --- | --- |
| Timing | `sleep`, a fixed wait, a stop after N ms; fails under load | Wait for a signal |
| Order | values land on the wrong row ("expected 1143, got 2287") | Fake answers from the request; order the query |
| Shared state | fails only in parallel or after another test | Isolate per worker; fix cleanup order |
| Environment | follows a runner or an image | Pin it and prove it by digest |

- **Force the race before fixing it.** Make the window deterministic: shrink the interval (a 1 ms heartbeat), pin the input that picks the code path (a fixed commit date gives a fixed hash prefix), add load. A fix for a race you never forced is a guess.
- **Signals, not timers.** A fake process prints a fixed line once its work is written; the test waits for that line under an overall deadline instead of sleeping or stopping the fake after N ms. Mock only the timer under test; faking every timer can hang the runner. Bound "fast enough" by CPU time (`process.threadCpuUsage()`, `time.process_time()`), not wall clock.
- **Order.** Without `ORDER BY` row order is unspecified and can flip between runs. A fake that replays a fixed list by position then writes answers onto the wrong rows. Make the fake compute each answer from the request it receives; ordering the query is the second fix. Random-order flags that expose order dependence → [references/loops.md](references/loops.md).
- **Cleanup order.** node:test runs `t.after` hooks in registration order: register "close the server" before "delete its data directory".

## Prove it can fail

A check you have not seen fail proves nothing.

1. **Loop with a per-run timeout**: `python3 scripts/repeat_run.py -n 50 -j 4 --timeout 300 --require 'tests 39\b' -- node --test test/x.test.mjs`. `--require` turns a green run that executed fewer tests into `missing`; `-j` only when each run isolates its state (`REPEAT_RUN_INDEX` names its database or temp dir). Runner-specific loops → [references/loops.md](references/loops.md).
2. **Break-check**: revert the fix or mutate the guarded behaviour (shift an index, `git stash push <fixed file>`, swap in the pre-change script); the test must go red. Restore, rerun, green.
3. **New CI check**: push a probe commit (`--no-verify`) that breaks only the checked property, watch the job fail and name the file, then drop the probe from your own branch (`git reset --hard HEAD~1 && git push --force-with-lease`). If the probe broke an earlier job, the new one shows `skipped`: a separate outcome, never a pass.
4. **Before blaming the change**, run the same gate on unmodified trunk.

A flake ticket is done when CI is green N times in a row (20 is a good default), a deliberate mutation
turns the test red, and nothing is skipped, quarantined or retried-on-failure.

**Tests that never run:**

- A test file outside every configured suite, or not named for discovery (PHPUnit `suffix="Test.php"`, pytest `python_files`, Jest `testMatch`), never runs and never fails. Generators and agents write to default directories. Guard with a test that asserts every test file sits in a suite and matches the pattern, or diff the runner's own listing (`pytest --collect-only -q`, `jest --listTests`) against `git ls-files`.
- A rule over nothing passes forever: an architecture test whose selector matches no class stays green. Prove it with a probe violation.
- Assert the count. A passing run that reports fewer tests than the files hold hid the rest (seen with node `--test-force-exit`).

## Pipeline traps

- **Zero jobs, status failed**: the config never compiled. Read `yaml_errors` (`GET /projects/:id/pipelines/:id`) or GraphQL `errorMessages`; the jobs list is empty.
- **GitLab jobs without `rules` skip merge request pipelines**, and any job that `needs:` one fails the config. Rules inside `include:` do not count.
- **A schedule runs every job its branch admits**, releases included. Prefer a manual command, or exclude the schedule from every other job.

Library pipelines on app components, security templates in MR pipelines, unlocked tool drift, and the
GitHub equivalents → [references/pipelines.md](references/pipelines.md).

## Who rewrote the branch

Merge into one UTC timeline: the forge's activity feed (force pushes, before and after SHAs), the
SHA each CI run fetched, any mirror's activity log, the remote-tracking reflog of every clone
(`update by push`, `forced-update`), and every agent session's `git push` commands. A ref change with
no feed entry, no CI run and no client push points inside the forge: a mirror sync, a server job or
an admin. Commands per source → [references/branch-forensics.md](references/branch-forensics.md).

## Slow hooks

1. **Time each step alone** before changing anything or writing a performance claim, and record the load; parallel agent sessions inflate every number.
   ```bash
   bash -c 'for c in "vendor/bin/phpstan analyse" "pnpm format:check" "pnpm lint"; do s=$(date +%s); $c >/dev/null 2>&1; e=$?; echo "$(( $(date +%s)-s ))s exit $e  $c"; done; uptime'
   ```
2. **Cache the slow linters, keyed on the lockfile.** Prettier keys its cache on its own version, options, Node version and the file; ESLint on the file and the config. Neither sees a plugin upgrade, so put the lockfile hash in the cache path:
   ```json
   "format:check": "prettier --check --cache --cache-location node_modules/.cache/prettier/$(git hash-object pnpm-lock.yaml) .",
   "lint": "eslint --cache --cache-location node_modules/.cache/eslint/$(git hash-object pnpm-lock.yaml) ."
   ```
3. **Keep the CI job uncached.** ESLint's cache ignores cross-file dependencies, so type-aware and import rules can report stale results; the hook is the fast path, CI the gate (the agent-instructions skill covers gates).

## Gotchas

- **Retry-until-green** destroys the evidence; the failed attempt still counts, so count it.
- **A pipe reports its last command's status**: `test | tail -1` in a loop counts `tail`. Count the test command's exit, or `set -o pipefail`.
- **Go's `-count` loops** die at the 10-minute default `-timeout`; set one that fits the loop.
- **A single hung run** stalls a whole proof loop for hours; every loop gets a per-run timeout.
