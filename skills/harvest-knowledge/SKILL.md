---
name: harvest-knowledge
description: Mine durable, reusable knowledge out of Claude conversation threads with a three-phase workflow — distill each thread into a self-contained digest, consolidate many digests into one deduplicated truth-checked knowledge set, then synthesize repo docs, CLAUDE.md rules, new-skill candidates, and memory updates from it. Use when distilling/harvesting durable learnings from a Claude thread or from finished Claude Code sessions and their JSONL transcripts, extracting a thread digest, consolidating multiple digests into one knowledge set, running the integration thread, or turning collected learnings into docs/skills/memory.
---

# Harvest Knowledge — distill Claude threads into docs + skills

Three phases, each **run in a different context**. Pick by where you are, open the matching
prompt file, and adopt it **VERBATIM** as your task — the output format is load-bearing:
uniform digests are what let Phase 2 consolidate.

| Phase | Run it in | Input | Produces | Prompt (use verbatim) |
|---|---|---|---|---|
| **1 · Distill** | the working thread you want to mine (at its end), or a subagent over a finished thread's dump | the whole conversation | one self-contained thread digest | [prompt-1-distill.md](prompt-1-distill.md) |
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

## Phase 1 on finished threads

A closed thread can't audit itself: dump its transcript and hand the dump to a subagent.

1. **Find the transcript:** `~/.claude/projects/<dir>/<session-id>.jsonl`, where `<dir>` is the
   session's working directory with every non-alphanumeric character turned into `-`. From
   inside `~/.claude/projects`, glob as `ls ./*/<id>*.jsonl` — the directory names start with
   `-`, so `ls */…` reads them as options.
2. **Dump it** with this skill's script:
   `python3 <skill dir>/scripts/dump_transcript.py <session>.jsonl -o dumps/<id>.txt`. The dump
   keeps user and assistant text, tool calls, truncated tool results, summaries, and the
   subagent hand-back reports and queued user messages that a naive dump drops (they sit in
   `queue-operation` enqueue entries, `queued_command` attachments and `isMeta` user
   messages). A subagent's own transcript is `<session-id>/subagents/agent-<id>.jsonl`; dump
   it the same way when its hand-back is too thin.
3. **Split a dump one reader can't finish** (a few hundred thousand characters):
   `--split-chars 350000` writes `<id>.part1.txt`, `<id>.part2.txt`, … and cuts only before a
   user turn.
4. **One background subagent per thread or part**, all launched together. Its brief is a
   short input preamble, then [prompt-1-distill.md](prompt-1-distill.md) verbatim, then the
   output handling:
   - *Preamble:* "You are running Phase 1 of harvest-knowledge on a finished session. The
     conversation is dumped at `<path>` as `[timestamp ROLE] text` blocks, tool results
     truncated; the raw JSONL is `<path>` if you must confirm something. Read the whole dump
     in chunks, not just the start. For this run, THIS ENTIRE conversation means that dump."
     For a part, add the other parts' paths: digest only your part, and grep the others to
     learn whether a claim was corrected later. An optional FOCUS line names the topics to
     keep.
   - *Output handling:* "Write the digest to `digests/<id>.md` and modify no other file.
     Final message: the digest's title, its item count and the three most important items,
     one line each — not the digest."
5. **Consolidate in batches:** one fresh subagent per batch of about four digests runs
   [prompt-2-consolidate.md](prompt-2-consolidate.md) verbatim over them and writes
   `consolidated-<n>.md`; a last subagent runs the same prompt over the batch outputs as the
   final merge. They write only these files, in a scratch directory, never the repo.

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
- **A dump that skips `isMeta` messages and queue entries loses every subagent report**, often
  most of a session's research. Dump with `scripts/dump_transcript.py`, not an ad-hoc parser.
