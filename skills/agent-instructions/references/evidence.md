# Evidence

What is measured about instruction files, and what is only claimed. Cite the primary source and
the version; several blog posts quote superseded numbers.

## Contents
- [What the studies show](#what-the-studies-show)
- [What developers actually write](#what-developers-actually-write)
- [Vendor guidance](#vendor-guidance)
- [Distortions to avoid repeating](#distortions-to-avoid-repeating)

## What the studies show

| Study | Setup | Finding |
|---|---|---|
| Gloaguen et al., [arXiv 2602.11988](https://arxiv.org/abs/2602.11988) (v2) | SWE-bench Lite + 138 tasks from 12 repos with developer-written files; Claude Code, Codex, Qwen Code | Developer-written files +2.4 %, LLM-generated −2 %, **neither significant**. Cost **+20 %**, 2–4 extra steps. Named tools are followed (`uv` 1.6× more). Overviews did not speed up finding files. Generated files mostly repeat the README. Advice: only minimal, non-standard requirements. |
| McMillan, [arXiv 2605.10039](https://arxiv.org/abs/2605.10039) | 1,650 Claude Code sessions, factorial | **Size (25–500 lines), position and file architecture had no detectable effect** on adherence to a marker rule. Adherence **decays within a session** (≈ −5.6 % odds per generated function; first miss at median function 4). Task mattered more than structure. Advice: re-surface rules (hooks), enforce afterwards (lint, CI). |
| Khatri, [arXiv 2607.27250](https://arxiv.org/html/2607.27250) | Claude Code + Codex, 288 runs | No correctness gain from architecture/style content; the one benefit was an operational warning ("tests are slow": full-suite runs 3.67 → 1.67 per task). Underpowered. |
| Lulla et al., [arXiv 2601.20404](https://arxiv.org/abs/2601.20404) | Codex, 124 small PRs | Median wall time −28.6 %, output tokens −16.6 % with `AGENTS.md`. Correctness not measured. |
| Shepard & Albrecht, [arXiv 2606.20512](https://arxiv.org/abs/2606.20512) | Qwen3.5-35B, SWE-bench Verified | Guidance refined against probe tasks 33.0 % vs static 28.3 % vs none 25.5 %. Gain in coverage, not precision. Tuned guidance did not transfer across models. |
| IFScale, [arXiv 2507.11538](https://arxiv.org/abs/2507.11538) | 500 synthetic keyword instructions | Best model 68 % at 500 instructions; primacy bias. Directional for instruction density, not a line limit. |
| Chroma, [Context Rot](https://www.trychroma.com/research/context-rot) (tech report) | 18 models | Accuracy falls with input length and distractors; a focused ~300-token prompt beat ~113 k tokens. |

**What this means for the skill:**
- Content with measured effect: **commands, tool choices, operational warnings, non-standard
  practices**. Overviews, architecture tours and style prose cost tokens without shown benefit.
- Length is a **cost** lever (tokens, steps, focus), not a proven adherence lever within 500
  lines. Keep files small to keep them cheap and reviewable, and move anything that must hold to a
  hook or CI check, because adherence decays however the file is written.
- Generated files (`/init`, LLM-written) repeat existing docs; write by hand or prune hard.
- Test guidance against the model and tasks it serves; a line whose removal changes nothing goes.

## What developers actually write

- [Agent READMEs, arXiv 2511.12884](https://arxiv.org/abs/2511.12884): 2,303 files. Tests 75.9 %,
  implementation detail 70.8 %, architecture 68.1 %, security 14.8 %. Files grow "like
  configuration code through frequent, small additions" — accretion is the default trajectory.
- [Configuring agentic coding tools, arXiv 2602.14690](https://arxiv.org/abs/2602.14690): ~2.9 k
  repos; context files dominate and are often the only mechanism; skills and hooks rarely used.
- [Scanning the Harness, arXiv 2609.07360](https://arxiv.org/abs/2609.07360): 3,171 repos, 16 % with
  a security defect (unpinned MCP servers 9.8 %, pseudo-scoped grants like `Bash(python:*)` 3.1 %).

## Vendor guidance

- Anthropic: under 200 lines per file; "Would removing this cause Claude to make mistakes? If
  not, cut it"; emphasis on one line only ("If you emphasize many lines, none of them stands
  out"); procedures to skills, guarantees to hooks
  ([best practices](https://code.claude.com/docs/en/best-practices),
  [memory](https://code.claude.com/docs/en/memory)).
- Anthropic prompting for current models: replace "CRITICAL: You MUST…" with plain instructions,
  give the reason, state scope explicitly (literal reading), drop verification boilerplate and
  "show your reasoning" lines (can trigger the `reasoning_extraction` refusal), older prescriptive
  skills can degrade output
  ([prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices),
  [Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5),
  [Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)).
- Anthropic context engineering: "the smallest set of high-signal tokens"
  ([post](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- Copilot: "no longer than 2 pages"; Cursor: rules under 500 lines; Codex: 32 KiB hard stop.

## Distortions to avoid repeating

- "AGENTS.md reduces performance by 3 %": v1 numbers, not significant in v2.
- "Longer files are followed less": not shown within 25–500 lines; the measured decay is over a
  session.
- "Codex falls back to CLAUDE.md": `project_doc_fallback_filenames` defaults to `[]`.
- Tool-generated summaries of PDFs were wrong during research for this skill; quote the paper.
