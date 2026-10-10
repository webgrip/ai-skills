# Pipeline traps: zero jobs, silent gaps, schedules

## A pipeline that failed with zero jobs

The configuration never compiled into jobs, so there is no job log to read. Ask for the error:

```bash
glab api "projects/$P/pipelines/$PIPELINE_ID" | python3 -c 'import json,sys; print(json.load(sys.stdin)["yaml_errors"])'
glab api graphql -f query='{ project(fullPath: "group/app") { pipeline(iid: "123") { errorMessages { nodes { content } } } } }'
```

Typical message: `'pest' job needs 'composer-install' job, but 'composer-install' does not exist in the pipeline. This might be because of the only, except, or rules keywords.` Either give the needed job the same rules, or mark the need `optional: true` when the job may legitimately be absent.

## Jobs that silently skip merge request pipelines (GitLab)

- A job with no `rules` defaults to `except: merge_requests`: it runs in branch pipelines and never in merge request pipelines. A job that `needs:` it then breaks the whole merge request pipeline at config time.
- Merge request pipelines need `rules:` or `workflow: rules` matching `$CI_PIPELINE_SOURCE == "merge_request_event"` in the project's own `.gitlab-ci.yml`; rules that arrive through `include:` (a CI component, a template) do not satisfy it.
- One pipeline per change, merge request pipelines when a merge request is open:

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH
```

- GitLab's security templates (Secret Detection and the other AST jobs) run in merge request pipelines only with `variables: {AST_ENABLE_MR_PIPELINES: "true"}`; without it they run in branch pipelines, which the workflow above suppresses.
- After a rules change, run the pipeline and check that every expected job is listed; a valid config can still drop jobs.

## A library on CI components built for apps

- Components that run tests, static analysis or a formatter inside the application's built testing image have no such image in a library. Run those checks as your own jobs on the language's toolchain image.
- Dependency-audit components need a committed lock file; a library that commits none drops them or audits a resolved install.
- Without a lock file CI resolves newer tool versions than your machine, so a new rule fires only in CI. Reproduce with a fresh dependency update locally before changing the code.

## Schedules run more than the job you meant

- A GitLab schedule is a pipeline on a branch with `$CI_PIPELINE_SOURCE == "schedule"`. Workflow rules such as `$CI_COMMIT_BRANCH && $CI_COMMIT_REF_PROTECTED == "true"` admit it, and then every job admitted for that branch runs, release jobs included.
- Scheduling one job means a `when: never` rule for the schedule on every other job, including jobs that includes and components bring in. Before adding a schedule, list the jobs a scheduled pipeline would create; when that list is long, a manual command or a manual job is safer.
- GitHub and Forgejo Actions run a `schedule` only for workflows that declare it, on the latest commit of the default branch. A release job in such a workflow still runs on the schedule unless it carries `if: github.event_name != 'schedule'`.

## Results that look like passes

- A job skipped because an earlier job failed shows as skipped, and forges count skipped required checks as passed. The merge-gate side of this lives in the product-owner skill.
- A red job marked `allow_failure: true` (GitLab) or `continue-on-error: true` (GitHub) leaves the pipeline green; a check that must gate cannot carry either.
