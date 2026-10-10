# CI and pre-commit wiring for `check`

`agent_setup.py check` reads files only: no application dependencies, network or secrets. Run it
in every merge or pull request pipeline and on the default branch, and as a pre-commit hook. A
generator whose drift check needs the application image (Laravel Boost) gets a second job:
[generators.md](generators.md#ci-drift-check).

## Contents
- [Getting the script into CI](#getting-the-script-into-ci)
- [Rules for every forge](#rules-for-every-forge)
- [GitLab CI](#gitlab-ci)
- [GitHub Actions](#github-actions)
- [Forgejo Actions](#forgejo-actions)
- [Bitbucket Pipelines](#bitbucket-pipelines)
- [Azure Pipelines](#azure-pipelines)
- [Pre-commit hooks](#pre-commit-hooks)
- [Prove the gate](#prove-the-gate)

## Getting the script into CI

Vendor `scripts/agent_setup.py` together with `assets/targets.json` from one pinned version of this
skill, and name that version in the commit message. The script finds the registry at
`../assets/targets.json` or next to itself; anywhere else, pass `--registry <path>`. The snippets
below assume `scripts/agent_setup.py` with `scripts/targets.json` beside it and run
`python3 scripts/agent_setup.py check .`. A tool added locally to the vendored `targets.json`
([targets.md](targets.md#adding-a-tool)) goes upstream too, or the next upgrade drops it.

## Rules for every forge

- **Never path-filter a required check.** It costs seconds. A workflow skipped by a path filter
  leaves its required check pending on GitHub and Forgejo, and an MR without a pipeline cannot
  merge on GitLab. Filter only optional jobs.
- **Image**: `python:3-slim` or the runner's own `python3`; the script needs Python 3.9+ and no
  git (without git it walks the tree and approximates `.gitignore`). In a git checkout it also
  fails on agent files git does not track, so check out the repo rather than copying files in.
- **No secrets in this job.** It runs branch code in MR pipelines; a job holding tokens never does
  ([unattended.md](unattended.md#ci-secrets)).
- If you filter an optional job, trigger on: `AGENTS.md` and `CLAUDE.md` at any depth,
  `.coderabbit.yaml`, `.coderabbit/`, `.ai/`, `.agents/`, `.claude/`, `.cursor/rules/`,
  `.github/instructions/`, `.devin/rules/`, `.kiro/steering/`, `.clinerules/`, `docs/`, and the
  script. Write each forge's patterns from this one list, in that forge's glob dialect (below).

## GitLab CI

```yaml
agent-setup-check:
  image: python:3-slim
  needs: []
  script:
    - python3 scripts/agent_setup.py check .
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

- GitLab Free has no per-job required check: "Pipelines must succeed" gates the whole pipeline.
  Never put `changes:` in `workflow:rules`: no pipeline means the MR cannot merge.
- `rules:changes` globs use Ruby `fnmatch` with `FNM_PATHNAME`: **`docs/**` matches only direct
  children; write `docs/**/*`**. Quote a pattern that starts with `*`; at most 50 patterns per
  `changes`.
- Branch pipelines compare with the previous commit only, so a multi-commit push can miss the
  change: add `compare_to: refs/heads/main` (never on the default branch itself, where the diff is
  empty). New branches, tags, schedules and manual pipelines always run the job.
- A `needs:` on a job that rules excluded fails the pipeline unless it is `optional: true`
  ([docs](https://docs.gitlab.com/ci/yaml/#ruleschanges)).

## GitHub Actions

```yaml
on:
  pull_request:
  push:
    branches: [main]
  merge_group:
permissions:
  contents: read
jobs:
  agent-setup-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - run: python3 scripts/agent_setup.py check .
```

- A workflow skipped by `paths:` keeps its required checks "Pending"; a skipped **job** reports
  success. To filter anyway, filter a job and make an always-running aggregate job the required
  check.
- With a merge queue, `merge_group:` is required or the check never reports.
- Pin actions to a commit SHA. Use `pull_request`, never `pull_request_target`.
- `paths` dialect: `docs/**` recurses; quote patterns starting with `*`, `[` or `!`. A push of more
  than 1,000 commits always runs; a matching file beyond the first 3,000 changed files is not seen
  ([docs](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)).

## Forgejo Actions

```yaml
on:
  pull_request:
  push:
    branches: [main]
jobs:
  agent-setup-check:
    runs-on: docker
    container:
      image: node:22-bookworm
    steps:
      - uses: actions/checkout@v4
      - run: python3 scripts/agent_setup.py check .
```

- `actions/checkout` is a JavaScript action and needs node in the container: it breaks in
  `python:3-slim`. `node:22-bookworm` has node, git and python3; or clone with plain git.
- `runs-on` is whatever label the runner was registered with.
- With `paths:`, the first push of a new branch diffs only its head commit, and a diff error skips
  the workflow ([docs](https://forgejo.org/docs/latest/user/actions/reference/)).

## Bitbucket Pipelines

```yaml
pipelines:
  pull-requests:
    '**':
      - step:
          name: agent setup check
          image: python:3-slim
          script:
            - python3 scripts/agent_setup.py check .
  branches:
    main:
      - step:
          name: agent setup check
          image: python:3-slim
          script:
            - python3 scripts/agent_setup.py check .
```

- `condition.changesets` sees every commit only in `pull-requests:`; elsewhere it sees the last
  commit, so a failing step turns green by being skipped on the next push.
- Merge checks count builds, not steps: keep this step unconditional so a build status always
  exists ([docs](https://support.atlassian.com/bitbucket-cloud/docs/step-options/)).

## Azure Pipelines

```yaml
trigger:
  branches:
    include: [main]
pr:
  branches:
    include: ['*']
pool:
  vmImage: ubuntu-latest
steps:
  - script: python3 scripts/agent_setup.py check .
    displayName: agent setup check
```

- `pr:` triggers work only for GitHub and Bitbucket Cloud repositories. On Azure Repos, add a
  build-validation branch policy for this pipeline.
- Policy path filters must start with `/` or a wildcard and are separated by `;`
  (`/AGENTS.md;/.ai/*;/docs/*`); any other entry silently does nothing. YAML `paths:` are
  case-sensitive and take no variables
  ([docs](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies)).

## Pre-commit hooks

A hook is the fast local copy of the CI job, never the guarantee: `--no-verify`, web edits and
clones without the manager installed skip it ([enforcement.md](enforcement.md#ladder)).

- **Install it for `pre-merge-commit` too.** A clean `git merge` runs `pre-merge-commit`, not
  `pre-commit`, and merges are where generated files drift. Never skip merges for this check.
- **Run it on every commit when it is fast**; that avoids every staged-file caveat below.
- `check` reads the working tree, not the index, so a commit can pass on an unstaged fix. Of the
  managers below only pre-commit stashes unstaged changes.

### Shell guard (plain git, husky, simple-git-hooks)

`scripts/agent-setup-guard.sh`:

```sh
#!/bin/sh
pattern='(^|/)(AGENTS|CLAUDE)\.md$|^\.coderabbit\.ya?ml$|^(\.ai|\.agents|\.claude|\.coderabbit|\.cursor/rules|\.github/instructions|\.devin/rules|\.kiro/steering|\.clinerules|docs)/'
if git -c core.quotePath=false diff --cached --name-only --no-renames --diff-filter=ACDMRT | grep -qE "$pattern"; then
  exec python3 scripts/agent_setup.py check .
fi
exit 0
```

`--no-renames` reports a move as delete plus add, so a rule moved out of `.ai/rules` still
triggers; `D` catches deletions, `T` a file turned into a symlink; `core.quotePath=false` keeps
non-ASCII paths matchable; the `if` keeps a non-match from failing under `sh -e`.

- **Plain git**: commit the guard as `.githooks/pre-commit` and
  `.githooks/pre-merge-commit` (`exec "$(dirname "$0")/pre-commit"`), both with
  `git add --chmod=+x`; each clone runs `git config core.hooksPath .githooks` once.
- **simple-git-hooks**: in `package.json`,
  `"simple-git-hooks": {"pre-commit": "sh scripts/agent-setup-guard.sh", "pre-merge-commit": "sh scripts/agent-setup-guard.sh"}`;
  run `npx simple-git-hooks` after every change to it.

### lefthook

```yaml
glob_matcher: doublestar
pre-commit:
  jobs:
    - &agent_setup_check
      name: agent-setup-check
      run: python3 scripts/agent_setup.py check .
      glob:
        - "**/AGENTS.md"
        - "**/CLAUDE.md"
        - ".coderabbit.yaml"
        - ".coderabbit/**"
        - ".ai/**"
        - ".agents/**"
        - ".claude/**"
        - ".cursor/rules/**"
        - ".github/instructions/**"
        - ".devin/rules/**"
        - ".kiro/steering/**"
        - ".clinerules/**"
        - "docs/**"
pre-merge-commit:
  jobs:
    - *agent_setup_check
```

The default matcher lets `*` cross `/`, never matches a root file with `**/x`, and lowercases
`glob`; `doublestar` behaves like the other tools. No `{staged_files}` in `run`, so deletions count.

### husky and lint-staged

Simplest: the shell guard as `.husky/pre-commit` and `.husky/pre-merge-commit`. Where lint-staged
already runs, both files hold `npx lint-staged --diff-filter=ACMRD`, and `lint-staged.config.mjs`
has one key:

```js
export default {
  '{**/AGENTS.md,**/CLAUDE.md,.coderabbit.yaml,.coderabbit/**,.ai/**,.agents/**,.claude/**,.cursor/rules/**,.github/instructions/**,.devin/rules/**,.kiro/steering/**,.clinerules/**,docs/**}':
    () => 'python3 scripts/agent_setup.py check .',
};
```

- One key: every matching key runs its own task. The function form passes no file names.
- The default filter `ACMR` drops deletions, hence `--diff-filter=ACMRD`.
- lint-staged drops symlinks from the staged list, so a change to the `.claude/rules` or
  `.claude/skills` symlink never triggers it; the guard does not have that gap. Confirm matching
  with `npx lint-staged --debug`.

### pre-commit

```yaml
minimum_pre_commit_version: '4.4.0'
default_install_hook_types: [pre-commit, pre-merge-commit]
repos:
  - repo: local
    hooks:
      - id: agent-setup-check
        name: agent setup check
        entry: python3 scripts/agent_setup.py check .
        language: unsupported
        pass_filenames: false
        always_run: true
        stages: [pre-commit, pre-merge-commit]
```

`always_run` because the staged list leaves out deletions and a merge commit checks only
conflicted files. To filter instead, `files:` is a Python regex matched with `re.search`, so
anchor it with `^`. Older than 4.4.0: `language: system`.

### CaptainHook

```json
{
  "pre-commit": {
    "enabled": true,
    "actions": [
      {
        "action": "python3 scripts/agent_setup.py check .",
        "conditions": [
          {
            "exec": "\\CaptainHook\\App\\Hook\\Condition\\FileStaged\\Any",
            "args": [
              ["AGENTS.md", "CLAUDE.md", "*/AGENTS.md", "*/CLAUDE.md", ".coderabbit.yaml", ".coderabbit/*", ".ai/*", ".agents/*", ".claude/*", ".cursor/rules/*", ".github/instructions/*", ".devin/rules/*", ".kiro/steering/*", ".clinerules/*", "docs/*"],
              ["A", "C", "M", "R", "D"]
            ]
          }
        ]
      }
    ]
  }
}
```

- Patterns go through `fnmatch` without flags: `*` crosses `/` (so `docs/*` is recursive), `**`
  acts as `*`, no braces, case-sensitive.
- The second argument is the diff filter; the default leaves out `D`.
- CaptainHook has no `pre-merge-commit` hook: clean merges rely on CI.

## Prove the gate

A check is trusted only after it has failed once on purpose. On a scratch branch, commit each
breakage on its own and expect red from the hook and from CI:

- a rule without `paths:`, and one with an unquoted glob that starts with `*`;
- a glob that matches no file (globs are anchored at the repo root: `*.php` matches root files
  only), and one with a comma outside braces;
- a hand edit in a generated rule copy;
- a broken relative link in `docs/`, and an `@import` in `CLAUDE.md` or `AGENTS.md` that points
  nowhere;
- a commit that only deletes a rule and leaves its generated copies behind;
- a clean `git merge` of a breaking commit made with `--no-verify`.

Then delete the branch. A gate that stayed green is wired wrong: fix it before relying on it.
