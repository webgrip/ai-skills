---
name: harvest-knowledge
description: Mine durable, reusable knowledge out of Claude conversation threads with a three-phase workflow — distill each thread into a self-contained digest, consolidate many digests into one deduplicated truth-checked knowledge set, then synthesize repo docs, CLAUDE.md rules, new-skill candidates, and memory updates from it. Use when distilling/harvesting durable learnings from a Claude thread, extracting a thread digest, consolidating multiple digests into one knowledge set, running the integration thread, or turning collected learnings into docs/skills/memory.
---

# Harvest Knowledge — distill Claude threads into docs + skills

Three phases, each **run in a different context**. Pick by where you are, open the matching
prompt file, and adopt it **VERBATIM** as your task — the output format is load-bearing:
uniform digests are what let Phase 2 consolidate.

| Phase | Run it in | Input | Produces | Prompt (use verbatim) |
|---|---|---|---|---|
| **1 · Distill** | the working thread you want to mine (at its end) | the whole current conversation | one self-contained thread digest | [prompt-1-distill.md](prompt-1-distill.md) |
| **2 · Consolidate** | a fresh "integration" thread | every Phase-1 digest, pasted together | one deduped, truth-checked knowledge set | [prompt-2-consolidate.md](prompt-2-consolidate.md) |
| **3 · Synthesize** | the repo being documented (write access) | the Phase-2 knowledge set | doc / CLAUDE.md / skill / memory updates + new-skill candidates | [prompt-3-synthesize.md](prompt-3-synthesize.md) |

## Run a phase

1. Identify the phase from the table.
2. `Read` the matching prompt file and **execute it exactly as written** — do not paraphrase,
   trim, reorder, or "improve" it. If a prompt genuinely needs changing, edit the prompt file,
   not the run.
3. Honor the phase contract:
   - **1** audits THIS conversation; the digest must stand alone (the integrator can't see this
     thread).
   - **2** operates ONLY on the pasted digests and **modifies no files** — output only.
   - **3** inventories existing docs/skills FIRST, then shows the item→action PLAN table and
     **waits for approval before writing**.

## Where Phase 3 lands things

Phase 3's inventory step discovers the target repo's own conventions — follow them. Typical
homes: long-form knowledge → the repo's docs tree (`docs/`, an mkdocs/techdocs tree, or the
README) · always-on rules → `CLAUDE.md` · repeatable procedure or behavior-changing gotcha → a
skill under `.claude/skills/<name>/` (author it with the `skillsmith` plugin when installed) ·
preferences / incident state → memory (`MEMORY.md` index) · open items → a TODO list, not docs.

## Gotchas

- **Phase 2 is read-only** — "Output only — modify no files." Don't let it touch the repo.
- **Phase 3 never writes before the PLAN is approved.** LOW-confidence / "needs verification"
  items are proposals — verify against the repo or leave them out (deferred); never enshrine
  guesses.
- **Don't collapse the phases into one pass** — skipping the digest step loses the uniform
  structure Phase 2 consolidates on.
