# session-tldr

A TL;DR of the current agent session that the person can act on in one reply: what is done and how it was verified, what is left, what they need to know, and numbered decisions with a recommendation. Every PR, commit, ticket, file and CI run comes as a link, and every piece of state is checked against the live repository before it is reported.

## Install

Claude Code:

```text
/plugin marketplace add https://forgejo.webgrip.dev/webgrip/ai-skills.git
/plugin install session-tldr@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s session-tldr`.

Then type `/session-tldr`, or ask "where are we?" or "what do you need from me?".

## Repository contract (optional)

Add this to the consuming repository's `AGENTS.md` or `CLAUDE.md` when its links or approvals are not obvious from the git remote:

```markdown
## Session TL;DR

- Forge web host: https://git.example.com (SSH remote is git-ssh.example.com)
- Tickets: https://tracker.example.com/tasks/ID
- Also ask before: running paid evaluations, changing the staging cluster
```

## Example prompts

- `/session-tldr`
- "tldr - what do you need from me?"
- "I'm stepping away, give me the state of this session"
- "/session-tldr PR 42 only"
