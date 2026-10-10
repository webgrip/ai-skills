# GitLab for bots and coding agents

Sources: [job token](https://docs.gitlab.com/ci/jobs/ci_job_token/),
[service accounts](https://docs.gitlab.com/user/profile/service_accounts/),
[project access tokens](https://docs.gitlab.com/user/project/settings/project_access_tokens/),
[permissions](https://docs.gitlab.com/user/permissions/),
[webhooks](https://docs.gitlab.com/user/project/integrations/webhooks/),
[Claude Code GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd),
[Duo triggers](https://docs.gitlab.com/user/duo_agent_platform/triggers/),
[composite identity](https://docs.gitlab.com/user/duo_agent_platform/composite_identity/).

## Contents

- [Claude Code in GitLab CI](#claude-code-in-gitlab-ci)
- [Pipeline trigger tokens](#pipeline-trigger-tokens)
- [Identities and tokens](#identities-and-tokens)
- [Minimum roles](#minimum-roles)
- [MR, notes and discussions API](#mr-notes-and-discussions-api)
- [Webhooks in full](#webhooks-in-full)
- [Post-release work after a job-token push](#post-release-work-after-a-job-token-push)
- [Duo Agent Platform: the model to copy](#duo-agent-platform-the-model-to-copy)

## Claude Code in GitLab CI

- The integration is beta and maintained by GitLab, not Anthropic. There is no built-in `@claude`
  listener: a "Comments" (notes) webhook calls your listener, which verifies and filters the event
  ([SKILL.md](../SKILL.md#webhook-listener)) and starts a pipeline with `AI_FLOW_INPUT` (the
  request) and `AI_FLOW_CONTEXT` (the MR or issue).
- **Start the pipeline on the protected default branch and pass the MR as data.** A pipeline on the
  MR's source ref runs that branch's `.gitlab-ci.yml`, which its author controls, and the bot token
  would have to be an unprotected variable. The job fetches the MR into a scratch directory and runs
  the agent there with the repo's config neutralised ([untrusted-repos.md](untrusted-repos.md)).
- The job's core, adapted from the docs page, which also runs it on `web` and
  `merge_request_event` pipelines; a job holding the bot token stays off MR pipelines:

  ```yaml
  claude:
    stage: ai
    rules:
      - if: $CI_PIPELINE_SOURCE == "trigger"
    timeout: 30m
    script:
      - claude -p "$AI_FLOW_INPUT" --permission-mode acceptEdits --allowedTools "Bash Read Edit Write mcp__gitlab" --max-turns 30
  ```

  The page installs Claude Code with its native installer on a `node` Alpine image.
- **The token:** the page offers `CI_JOB_TOKEN` or a project access token with `api` scope stored as
  `GITLAB_ACCESS_TOKEN`. The job token can only read MRs and notes, so posting needs the service
  account's PAT or a project access token, held as a protected variable.
- **Model access without a static key:** Bedrock (`CLAUDE_CODE_USE_BEDROCK=1`, `AWS_ROLE_TO_ASSUME`)
  or Vertex (`CLAUDE_CODE_USE_VERTEX=1`) through the job's `id_tokens` and OIDC; the region is
  yours to choose.
- **Cost caps:** `--max-turns`, `--max-budget-usd` and the job `timeout`.
- Headless runs show no workspace-trust or `.mcp.json` prompt; everything the checkout ships loads
  unless the flags in [untrusted-repos.md](untrusted-repos.md) stop it.
- Which forges each cloud agent supports: the `agent-instructions` skill,
  `references/unattended.md`.

## Pipeline trigger tokens

- Creating one needs Maintainer or Owner; the pipeline runs with **the creator's permissions**, so
  create it as the identity the pipeline should act as, never as a person.
- Webhook form: `POST /api/v4/projects/:id/ref/:ref/trigger/pipeline?token=…`; GitLab passes the
  webhook body to the jobs as the file variable `TRIGGER_PAYLOAD`. The token sits in the query
  string, so keep that URL out of logs.
- Gate the agent job on `$CI_PIPELINE_SOURCE == "trigger"` so it never runs in branch or MR
  pipelines.

## Identities and tokens

- **`CI_JOB_TOKEN`:** `GET /projects/:id/merge_requests`, `GET …/merge_requests/:iid`,
  `GET …/merge_requests/:iid/notes`, `GET …/notes/:note_id`; no GraphQL. It can also trigger
  pipelines and use the Releases, Deployments, Environments and Packages APIs and the registries.
- **Job-token push:** the project setting "Allow Git push requests to the repository" is off by
  default (generally available from GitLab 18.4). A push made with the job token starts no pipeline,
  in the target project too.
- **Service accounts:** Free, Premium and Ultimate on GitLab.com, Self-Managed and Dedicated (Free
  from 18.11). Free allows 100 per top-level group on GitLab.com and 100 per instance on
  Self-Managed. No seat; no UI sign-in; authenticate with a PAT; take a role per group or project.
  On GitLab.com top-level group Owners create group service accounts, project Maintainers create
  project service accounts.
- **Service-account PAT expiry:** without a date it is set to 365 days ahead; the maximum is 365
  days unless an administrator raises it to 400 (17.6+); tokens without expiry exist only where the
  instance does not require expiry dates.
- **Project and group access tokens:** Premium or Ultimate on GitLab.com, any licence on
  Self-Managed. Their bot users are named `project_{id}_bot_{random}` and `group_{id}_bot_{random}`.
- Recognise the bot's own notes by a marker in the body, not by its username.

## Minimum roles

| Action | Minimum role |
|---|---|
| Create an issue, comment | Guest (any signed-in user on a public project) |
| Label or assign an existing issue | Planner |
| Label, assign or set reviewers on an MR; mark draft or ready | Developer |
| Create an MR, push to an unprotected branch | Developer |
| Create a pipeline trigger token, configure Duo triggers | Maintainer |

`access_level` values for the role check: 10 Guest, 15 Planner, 20 Reporter, 30 Developer,
40 Maintainer, 50 Owner.

## MR, notes and discussions API

- **Create an MR:** `POST /projects/:id/merge_requests` with `source_branch`, `target_branch`,
  `title`. There is no draft parameter: start the title with `Draft:` (`[Draft]` and `(Draft)` also
  work) or put `/draft` in the description.
- **Closing keywords** (Close, Fix, Resolve, Implement and their forms, case-insensitive, followed by
  `#N` or `group/project#N`) close the issue when the MR merges into the default branch, unless the
  project turned off "Auto-close referenced issues on default branch".
- **Notes:** `POST …/issues/:iid/notes`, `POST …/merge_requests/:iid/notes`,
  `PUT …/notes/:note_id`. Quick actions in an API-written note run: the MR notes endpoint has a
  `merge_request_diff_head_sha` parameter that exists for `/merge`.
- **Discussions:** reply with `POST …/merge_requests/:iid/discussions/:discussion_id/notes`; resolve
  with `PUT …/merge_requests/:iid/discussions/:discussion_id` and `resolved=true`.
- **Acknowledge a trigger:** `POST …/issues/:iid/award_emoji?name=eyes`, then remove or replace it
  when done.

## Webhooks in full

- **Headers:** `X-Gitlab-Event` (`Issue Hook`, `Note Hook`, `Merge Request Hook`, `Pipeline Hook`,
  `Emoji Hook`), `X-Gitlab-Token` (legacy plain secret, sent only when configured),
  `Idempotency-Key` (legacy, equal to `webhook-id`), `webhook-id`, `webhook-timestamp` (Unix
  seconds), `webhook-signature` (only with a signing token), `X-Gitlab-Event-UUID` (shared by
  recursive webhooks), `X-Gitlab-Webhook-UUID` (one per hook).
- **Signing token:** introduced in 19.0, generally available in 19.1, following Standard Webhooks.
  GitLab sends one signature now and may send several; compare each entry.
- **Timeout:** 10 seconds on GitLab.com; Self-Managed sets it with `gitlab_rails['webhook_timeout']`,
  default 10.
- **Auto-disable:** 4 consecutive failures (4xx, 5xx, timeouts) disable a hook temporarily, from 1
  minute up to 24 hours, then it re-enables; 40 disable it for good; a test request answered with
  2xx re-enables it. On Self-Managed, project-hook auto-disable sits behind the feature flag
  `auto_disabling_web_hooks`.
- GitLab.com rate-limits webhook calls per top-level namespace on Free; check the current limits page.

## Post-release work after a job-token push

A release tool that pushes its tag with `CI_JOB_TOKEN` starts no tag pipeline, so a job waiting on
the tag never runs. Run the follow-up in the release pipeline: the release job writes
`tag=<version>` (empty when nothing was released) to `release.env` as a `dotenv` report, and the
next job needs it.

```yaml
publish:
  stage: deploy
  needs: [release]
  script:
    - 'if [ -z "$tag" ]; then echo "No release in this pipeline."; exit 0; fi'
    - 'curl --fail --header "Job-Token: $CI_JOB_TOKEN" --data tag="$tag" "$CI_API_V4_URL/projects/$CI_PROJECT_ID/packages/composer"'
```

## Duo Agent Platform: the model to copy

- **Triggers** (Premium and Ultimate; configured by Maintainers): mention, assign or assign as
  reviewer of the trigger's service account, pipeline events, MR events, work-item events. All of
  them require a human: "a bot user, service account user, or another flow cannot activate a
  trigger". A triggered flow runs as the trigger's service account.
- **Composite identity:** a service account with Developer in the project, combined per run with the
  triggering user; the effective role is whichever is more restrictive. The OAuth token is limited
  to the `ai_workflows` and `mcp` scopes. MRs are attributed to the human; commits show the service
  account acting on the user's behalf.
- **Repo-controlled config:** `.gitlab/duo/agent-config.yml` is read only from the default branch,
  and its `setup_script` runs outside the sandbox with GitLab tokens in the environment; protect it
  with Code Owners (the `agent-instructions` skill lists such files per agent).
- **Network:** flows reach only the GitLab instance by default; external agents do not get the same
  network isolation.
- **Prompt-injection protection** per group: No checks, Log only (the GitLab.com default), Interrupt.
  The value does not cascade to subgroups.
- Billing runs on GitLab Credits; check the current pricing page.
