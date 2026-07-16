# harvest-knowledge

A Claude skill that turns finished conversation threads into **durable repo knowledge** —
docs, CLAUDE.md rules, new skills, and memory — instead of letting the learnings evaporate
when the context closes. Three tuned prompts, each run in a deliberately separate context:

1. **Distill** — at the end of a working thread, extract one self-contained, uniformly
   structured digest: facts, gotchas (with causes), decisions and their trade-offs, reusable
   procedures, verbatim commands/paths, and your explicit preferences — each item tagged
   VERIFIED / ASSERTED / OPEN, corrections recorded instead of the original mistakes.
2. **Consolidate** — in a fresh "integration" thread, merge many digests into one deduplicated
   knowledge set: confidence-scored, contradictions surfaced (never silently resolved), prunes
   listed, preferences and TODOs split out. Read-only by contract.
3. **Synthesize** — in the target repo, inventory what already exists, present an item→action
   PLAN table, and only after approval fold the knowledge into docs / CLAUDE.md / skills /
   memory — merging with what's there, never blindly appending, never enshrining guesses.

The phase separation is the design: the distiller sees one thread, the consolidator sees only
digests, the synthesizer sees only the knowledge set and the repo. That is what keeps the
result deduplicated and truth-checked instead of a pile of pasted transcripts.

## Install

**Claude Code (as a plugin, recommended):**

```
/plugin marketplace add https://forgejo.webgrip.dev/webgrip/webgrip-ai-skills.git
/plugin install harvest-knowledge@webgrip-ai-skills
```

**Claude Code (manual):** copy `skills/harvest-knowledge/` into your
project's `.claude/skills/` (shared with your team via git) or `~/.claude/skills/` (just you).

**Claude app / claude.ai:** grab `harvest-knowledge.skill` from the
[latest release](https://forgejo.webgrip.dev/webgrip/webgrip-ai-skills/releases/latest),
upload it via Settings → Skills (or attach it in a chat), and hit *Save skill*.

## Use

- At the end of a productive thread: *"harvest this thread"* / *"distill this conversation
  into a digest"*
- With digests collected from several threads: *"consolidate these digests"* (paste them into
  a fresh thread)
- In the repo, with the knowledge set: *"synthesize this into our docs and skills"*

## Why

Long working threads routinely produce knowledge worth keeping — the gotcha that cost an hour,
the decision rationale, the exact command that worked — and almost all of it dies with the
context window. Ad-hoc "write down what we learned" prompts produce inconsistent, unmergeable
notes. This skill fixes the pipeline: uniform digests that consolidate cleanly, confidence
tags so guesses never masquerade as facts, and a plan-approval gate so the repo only absorbs
what survived verification.

## Contents

```
skills/harvest-knowledge/
  SKILL.md                  # phase table, contracts, landing map, gotchas
  prompt-1-distill.md       # the thread-digest prompt (use verbatim)
  prompt-2-consolidate.md   # the integration-thread prompt (use verbatim)
  prompt-3-synthesize.md    # the repo-writing prompt (use verbatim)
```
