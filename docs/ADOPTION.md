# Introducing the skills to a team — a rollout playbook

How to get a team actually using these skills, distilled from published
playbooks (Anthropic's champion kit, incident.io, Zapier, Ramp, Sanity —
sources at the bottom). The one-line summary of all of them: **adoption
happens because one person uses the tool well in public, not because of an
announcement.**

## The champion model

One person (whoever brings the skills in) plays champion for a month.
Anthropic budgets the role at **~40 minutes a week**: ~15 posting wins,
~20 answering questions, ~5 running a weekly thread. A champion is
"a multiplier for your team, not a help desk" — the goal is making yourself
unnecessary, and the role is handed off after week 4.

## The 30-day sequence

| Week | Do | Success signal |
| --- | --- | --- |
| 1 | Open a `#claude-code`/`#ai-agents` channel. Post 2–3 real wins **with the prompts included**. Share the install one-liner from the README. | Someone asks a question |
| 2 | Weekly "what did Claude help you with this week?" thread. Demo one skill end-to-end (record 2 min or do it live). | Someone other than you posts an example of their own |
| 3 | Offer 2–3 fifteen-minute pairing sessions. Pin a FAQ from the questions so far. | Repeat usage — people coming back, not trying once and stopping |
| 4 | Hand off: recruit a second champion, make the weekly thread theirs. | Questions get answered by people other than you |

## Moves that work

- **Demo skills as copyable artifacts.** A skill is plain markdown — paste a
  `SKILL.md` in the channel and say "this is the whole thing". ~5 minutes per
  skill, and it demystifies the format better than any explanation.
- **Starter tasks: tedious, real, contained.** The ideal first task is "a bug
  or chore the person has been postponing because it is tedious rather than
  difficult" — not their hardest problem. For skeptics: time one tedious task
  both ways and compare.
- **Answer questions with a prompt, not an explanation.** When someone asks
  "how would I do X", reply with the prompt you'd type. It teaches the
  interaction model for free.
- **Set the garbage expectation up front.** First attempts run a high garbage
  rate; attempt three is usually workable (Sanity's staff-engineering write-up
  says budget for a messy first month). Saying this *before* someone's first
  bad session prevents the one-bad-try-then-churn failure mode. Most
  "hallucination" complaints are context problems — the fix is a better
  CLAUDE.md/skill, not giving up.
- **Wire the shared config into real repos.** Committing
  `extraKnownMarketplaces` + `enabledPlugins` to a repo's
  `.claude/settings.json` (see the README) means colleagues get the plugins
  with zero per-person setup, and a checked-in `CLAUDE.md` "compounds in
  value over time".
- **Feed learnings back.** When a session surfaces a durable insight, run the
  `harvest-knowledge` skill and land it as a doc or skill PR — incident.io
  does the same with a `/note_this` command feeding CLAUDE.md "to save a few
  steps for the next new starter".

## Measuring (lightly)

Qualitative signals first — they're the champion kit's own checkpoints:
questions asked, non-champion examples posted, repeat usage, peer-answered
questions. If you later want numbers, Claude Code exports OTel metrics
(sessions, active time, commits, cost; per-skill usage needs
`OTEL_LOG_TOOL_DETAILS=1` since skill names are redacted by default). Prefer
unit economics (cost per resolved issue) over activity metrics — token
leaderboards get gamed, and "the impression of adopting AI" is the failure
state, not the goal.

## Failure modes (all observed in the wild)

1. **Tool dumped without enablement** → shelfware. Only ~15% of people
   naturally embrace new tooling; the sequence above exists for the other 85%.
2. **One bad first try → permanent churn** → set the garbage expectation,
   watch week-3 repeat usage.
3. **Activity metrics become the target** → measure outcomes, never rank
   individuals by tokens.
4. **Bloated always-on context** → procedures belong in on-demand skills,
   only always-true facts in CLAUDE.md. A bloated CLAUDE.md makes the agent
   *ignore* instructions.
5. **Skill sprawl** → curate: consolidate overlapping skills, police names,
   don't merge every idea (CONTRIBUTING.md is the gate).
6. **Skills without evals** → "documenting imagined problems". Every skill
   here ships `evals/evals.json`; keep it that way.
7. **Unreviewed third-party skills** → a skill is an instruction-injection
   surface and can pre-approve its own tool access. Install from reviewed
   sources; treat ad-hoc marketplace skills as untrusted code.
8. **Personal Claude subscriptions in third-party tools** → ToS violation
   (Anthropic made this explicit in Feb 2026; opencode dropped subscription
   auth for exactly this reason). Company work in opencode runs on a metered
   API key — see [auth.md](auth.md).

## Sources

- Champion kit (the 30-day sequence, time budgets, signals):
  <https://code.claude.com/docs/en/champion-kit>
- Team config & skills distribution tiers:
  <https://code.claude.com/docs/en/best-practices>,
  <https://code.claude.com/docs/en/settings>
- incident.io on onboarding with agents:
  <https://incident.io/blog/using-claude-to-power-up-your-onboarding>
- Sanity, "your first attempt will be 95% garbage":
  <https://www.sanity.io/blog/first-attempt-will-be-95-garbage>
- Zapier's rollout (63% → 97% adoption):
  <https://zapier.com/blog/how-zapier-rolled-out-ai/>
- Ramp's enablement stack (skill repos, office hours, evangelists):
  <https://creatoreconomy.so/p/your-new-job-is-to-onboard-ai-agents>
- Monitoring/OTel: <https://code.claude.com/docs/en/monitoring-usage>
- Prompt-injection risk of skills:
  <https://simonwillison.net/2025/Oct/16/claude-skills/>
