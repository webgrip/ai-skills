# forge-agents

Wire bots and coding agents into GitLab, GitHub and Forgejo or Gitea without handing them more than
they need: which identity and token a CI or bot agent gets (GitLab service accounts and access
tokens, GitHub Apps, bot users, what `CI_JOB_TOKEN` and `GITHUB_TOKEN` cannot do), label and
assignment triggers with a role check, webhook listeners that verify signatures, dedupe and answer
within 10 seconds, untrusted ticket text written through the API without running quick actions or
pinging people, retries that never duplicate a creating POST, Claude Code in GitLab CI, and headless
agents on repositories you do not control (neutralising the repo's agent config, runner hygiene,
sandboxes compared). Forge CLI and API recipes for `glab`, `gh` and `tea` sit in a reference.

Secret placement belongs to `secrets-levels`; instruction files, cloud-agent setup files and the
CI secrets rule to `agent-instructions`; merge policy for agent work to `product-owner`.

Ships:

- `scripts/forge_safety.py` — stdlib; `neutralise` escapes GitLab quick-action lines and breaks
  @mentions and closing keywords outside code fences before a forge write; `verify` checks a captured
  GitLab (Standard Webhooks), GitHub or Forgejo/Gitea delivery's signature and prints its delivery id.
  `test.sh` covers both with fixtures.

**Install:**

```text
/plugin install forge-agents@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s forge-agents`.

**Try:** "our CI bot gets 403 posting an MR comment with CI_JOB_TOKEN", "write a GitLab webhook
receiver that starts the agent when an issue gets the agent label", "which flags make claude -p safe
on customer repos?", "our ticket mirror created duplicate issues", "the tag pipeline never runs after
semantic-release", "why did GitHub accept a push that skipped the required check?".
