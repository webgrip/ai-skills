# dependency-intake

A skill for the question every dependency update raises and almost nobody answers: **what does this release mean for us?** It reads the release notes of every version an update spans, searches the repo for each concrete handle a note names, and gives each note a verdict with evidence. The output is a decision-first report, a PR comment, and ticket drafts for what the update makes possible.

What it teaches the agent:

- **Every version between old and new**: a grouped bump spanning three releases gets three sets of notes read
- **Handles, not package names**: config keys, CLI flags, env vars and defaults are what get searched, and a counted absence is a finding
- **Six verdicts**: breaks us, default shift, workaround retires, adopt, reaches agents or users, noise
- **Workarounds as a source of value**: allowlists, version caps, patches and "until upstream fixes" notes that a release makes removable
- **Cheap probes**: install the new version against a copy of the lockfiles before claiming safe or broken, and compare the PR's CI with the trunk head before blaming the bump
- **0.x minors and automerge**: pre-1.0 minors are breaking candidates, and the breaking-change pass must finish inside the release-age soak

## The consumer-repo contract

The skill carries the *role*; each repo carries its *instance facts*. Add a block like this to the consuming repo's `AGENTS.md` or `CLAUDE.md`:

```markdown
## Dependency intake contract

- Forge: Forgejo at forge.example.dev; update bot login `renovate`; trunk `main`
- Automerge: non-major after a 1-day soak; 0.x minors excluded
- Workarounds live in: `scripts/ci-warnings-allow.json`, `allowedVersions` rules in `renovate.json`, `patches/`
- Board: product-owner contract `.agents/product-owner/board.md`; tickets need the go of the owner
- Reaches agents or users: agent sandboxes run the target repo's package manager; the published container image
- PR comments: drafted, posted after the owner's go
- Last intake: date in `docs/operations/dependency-intake.md`
- Cadence: weekly, Monday
```

Without the block the skill infers these from the bot config, CI and docs, and states each inference in its report.

## Make it recurring

The skill holds the procedure; the cadence lives in your scheduler. A recurring ticket on your board ("Dependency intake") or a scheduled agent that runs *"go over the release notes of our open and recently merged dependency updates"* is enough. The contract's last-intake marker makes each run pick up where the previous one stopped.

## Install

**`npx skills` (recommended — works in every agent, not just Claude):**

```bash
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s dependency-intake -g
```

**Claude Code plugin:**

```
/plugin marketplace add https://forgejo.webgrip.dev/webgrip/ai-skills.git
/plugin install dependency-intake@ai-skills
```

**Claude Code (manual):** copy `skills/dependency-intake/` into your project's `.claude/skills/` (shared with your team via git) or `~/.claude/skills/` (just you).

**Claude app / claude.ai:** grab `dependency-intake.skill` from the [latest release](https://forgejo.webgrip.dev/webgrip/ai-skills/releases/latest), upload it via Settings → Skills (or attach it in a chat), and hit *Save skill*.

## Use

Open your agent in the project and say, for example:

- *"Go over the release notes in this Renovate PR. Does anything in our source need attention?"*
- *"What can we use from the dependency updates merged this week? Draft tickets."*
- *"The grouped update PR is red. Is it the bump?"*
- *"Run the weekly dependency intake."*

## Why

Update bots made bumping free and reading optional. With automerge on, nobody reads the notes at all, so breaking changes in 0.x minors land unnoticed, workarounds outlive the bug they worked around, and the features a team was waiting for arrive without anyone noticing. This skill puts the reading back, with evidence per verdict, and turns what it finds into tickets instead of a chat message.

## Contributing

Issues and PRs welcome. Before submitting: run `npm run check` from the repo root (CI runs the same via `.forgejo/workflows/ci.yml`), and keep the skill generic — instance facts belong in the consumer repo's contract block, never baked into the instructions. Use a release-triggering conventional commit (`fix(dependency-intake): ...`) — the release pipeline bumps the version and rebuilds the dist zip automatically.

## License

MIT
