# PR

## What / why

<!-- One paragraph. For a skill: which workflow it teaches and what prompted it
     (a failure loop, a repeated manual procedure). -->

## Checklist (author)

- [ ] `npm run check && npm test` pass locally
- [ ] Conventional commits; `plugins/**` changes use a release-triggering type (`feat`/`fix`/`perf`/`refactor`/`revert`/breaking)
- [ ] No hand-edits to generated/derived files (`skills/`, `marketplace.json`, any `version`)
- [ ] Skill changes: description states what + "Use when …" triggers (no `when_to_use`, no workflow summary)
- [ ] Skill changes: `evals/evals.json` updated (≥ 3 cases, objective assertions) and README row current
- [ ] Bundled scripts handle their own errors, declare dependencies, no unexplained constants
- [ ] No secrets, customer data, or hardcoded instance facts (ids/hostnames — those live in consumer contract blocks)

## Checklist (reviewer)

- [ ] Read the description as a router: would it fire on real phrasings, and on nothing else?
- [ ] Read every bundled script/MCP config as if it were application code — merging is a trust decision
- [ ] Overlap check: consolidate into an existing skill before accepting a new one
