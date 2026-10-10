# flaky-ci-forensics

Diagnose flaky tests and red CI jobs with evidence instead of retries: triage "is it my change?",
count how often the same assertion failed across pipelines and merge requests before calling it a
one-off, prove or rule out the CI image by digest and layer content (BuildKit re-adds same-content
files whose mtime changed, so sizes and digests drift without any content change), fix timing,
ordering and shared-state flakes, and prove each fix with a repeat loop plus a break-check. Also
covers tests that never run, skipped-is-not-passed, GitLab zero-job pipelines and schedules that run
releases, "who rewrote this branch?" timelines, and slow lint hooks.

Ships three stdlib Python scripts, tested offline by `test.sh`:

- `scripts/ci_recurrence.py` — lists every failed job of one name whose log contains a test name or
  assertion, on GitLab or GitHub, with the spread across pipelines, merge requests, branches and
  image digests. Read-only API calls; the token comes from `GITLAB_TOKEN`, `GITHUB_TOKEN` or
  `GH_TOKEN`.
- `scripts/repeat_run.py` — runs one command N times with a per-run timeout that kills the whole
  process group, optional parallelism, and a required-output check that catches green runs which
  executed fewer tests.
- `scripts/layer_diff.py` — flattens two images' layer tarballs and says whether their file trees
  differ in content or only in mtimes, and which layers re-add unchanged files.

**Install:**

```text
/plugin install flaky-ci-forensics@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s flaky-ci-forensics`.

**Try:** "the phpunit job on my MR is red but I only touched docs, can I just retry it?", "this test
fails maybe one in ten runs in CI, find out why", "I fixed the flaky test, prove it", "our testing
image grew 500 KB but nothing changed", "the pipeline failed with zero jobs", "two commits vanished
from main, who force-pushed?", "the pre-commit hook takes 45 seconds".
