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
| Gloaguen et al., [arXiv 2602.11988](https://arxiv.org/abs/2602.11988) (v2) | SWE-bench Lite + 138 tasks from 12 repos with developer-written files; Claude Code, Codex, Qwen Code | Developer-written files +2.4 %, LLM-generated −2 % on CTXbench (−0.5 % on SWE-bench Lite), **neither significant against no file**; developer-written did beat LLM-generated significantly (p = 0.038) and helped every agent except Claude Code. Cost **+20 %**, 2–4 extra steps. Named tools are followed (`uv` 1.6× more). Overviews did not speed up finding files. Generated files mostly repeat the README. Advice: only minimal, non-standard requirements. |
| McMillan, [arXiv 2605.10039](https://arxiv.org/abs/2605.10039) | 1,650 Claude Code sessions, factorial | **Size (25–500 lines), position and file architecture had no detectable effect** on adherence to a marker rule. Adherence **decays within a session** (OR ≈ 0.944 per generated function, non-monotonic; first miss at median function 4). Task mattered more than structure. Advice: re-surface rules (hooks), enforce afterwards (lint, CI). |
| Khatri, [arXiv 2607.27250](https://arxiv.org/html/2607.27250) | Claude Code + Codex, 288 runs | No correctness gain from architecture/style content; the one benefit was an operational warning ("tests are slow": full-suite runs 3.67 → 1.67 per task, Claude Code on one repo, p = 0.25). Underpowered. |
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

### Instruction count, conflicts, skills and self-written rules

Figures below were read from arXiv abstract/HTML pages; spot-check a decimal before quoting it.

| Study | Finding |
|---|---|
| Instruction Stacking Collapse, [arXiv 2608.02639](https://arxiv.org/abs/2608.02639) | Follow rate ~96 % → as low as 20 % as 1–20 instructions stack; non-linear, driven by **pairwise conflicts** |
| Paradoxical Interference, [arXiv 2601.22047](https://arxiv.org/html/2601.22047) | Adding self-evident constraints lowers task success; most loss from the first ~5 |
| MTAC-IFBench, [arXiv 2609.14992](https://arxiv.org/abs/2609.14992) | In the Claude Code harness: path/encoding constraints ~95 %, repo-wide style and orchestration ~50–55 %; compliance falls over turns |
| HANDBOOK.md, [arXiv 2607.25398](https://arxiv.org/html/2607.25398v1) | Long standing policies (median 15 k tokens): best strict pass 36 %; an in-task request overrides the standing file; agents claim compliance they did not deliver |
| Many-Tier Instruction Hierarchy, [arXiv 2604.09443](https://arxiv.org/html/2604.09443v3) | With up to 12 privilege tiers the best model scores 42.7 %; style compliance in code 7.7–68 % while correctness stays > 86 % |
| SkillsBench, [arXiv 2602.12670](https://arxiv.org/abs/2602.12670) | Curated skills 33.9 % → 50.5 %; **self-generated skills −8 to −11.5 pp**; 1–3 skills best, compact beats comprehensive |
| More Skills, Worse Agents?, [arXiv 2605.24050](https://arxiv.org/html/2605.24050v1) | 52 / 102 / 202 skills: −8 / −14 / −21 %, mostly distractor skills shadowing the right one |
| VibeMemBench, [arXiv 2609.23570](https://arxiv.org/html/2609.23570) | 11 of 12 automatic memory systems do not beat memory-off; memory hurt in 25.7 % of cases the model already solved |
| Rule taxonomy in AI IDEs, [arXiv 2606.12231](https://arxiv.org/html/2606.12231) (TOSEM) | Compliance 49 % → 72 % after rules were revised against observed errors; 36 % of rule files ever edited |
| Context engineering in OSS, [arXiv 2510.21413](https://arxiv.org/html/2510.21413) (MSR '26) | Mean `CLAUDE.md` 287 lines, `AGENTS.md` 142; half of `AGENTS.md` files never change; edits ~3:1 additions to removals |

**Consequences:**
- Check a file for rules that contradict each other or the task, not only for length.
- Checkable rules stick, style prose does not: push style to linters.
- A request in the task beats the standing file; critical rules need enforcement.
- Agents may **propose** rules and memory; a human reviews before they are committed.
- Keep skills few, compact and non-overlapping; prune near-duplicates.
- Revise rules against observed errors, deletions included.

## What developers actually write

- [Agent READMEs, arXiv 2511.12884](https://arxiv.org/abs/2511.12884): 2,303 files. Tests 75.9 %,
  implementation detail 70.8 %, architecture 68.1 %, security 14.8 %. Files grow "like
  configuration code through frequent, small additions" — accretion is the default trajectory.
- [Harness Engineering for Agentic AI Coding Tools, arXiv 2602.14690](https://arxiv.org/abs/2602.14690)
  (v1: "Configuring agentic coding tools"): 2,853 repos; context files dominate and are often the only mechanism; skills and hooks rarely used.
- [Scanning the Harness, arXiv 2609.07360](https://arxiv.org/abs/2609.07360): 3,171 repos; of 2,660
  multi-component setups 16 % had a security defect (unpinned MCP servers 9.8 %, pseudo-scoped grants
  like `Bash(python:*)` 3.1 % of setups).

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
- Anthropic, context engineering for Claude 5 models (Shihipar, Jul 2026): "We removed over 80%
  of Claude Code's system prompt for models like Claude Opus 5 and Claude Fable 5 with no
  measurable loss on our coding evaluations"; keep `CLAUDE.md` lightweight and "spend most of the
  tokens on gotchas"; examples "constrain them to a certain exploration space"; several ways to
  verify work belong in a verification skill referenced from `CLAUDE.md`
  ([post](https://claude.dev/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models/)).
  Their own clash ("leave documentation as appropriate" vs "DO NOT add comments") was fixed with
  "Write code that reads like the surrounding code".
- Anthropic, Opus 5.5 (Sep 2026): one short rule on when to stop and ask versus keep going; remove
  "think carefully" and "think step by step" from saved instructions
  ([post](https://claude.dev/blog/getting-the-most-out-of-opus-5-5/)).
- Anthropic context engineering: "the smallest set of high-signal tokens"
  ([post](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- Cursor: rules under 500 lines; Codex: 32 KiB combined by default (`project_doc_max_bytes`,
  configurable), then it stops reading.

## Distortions to avoid repeating

- "AGENTS.md reduces performance by 3 %": v1 numbers, not significant in v2.
- "Longer files are followed less": not shown within 25–500 lines; the measured decay is over a
  session.
- "Codex falls back to CLAUDE.md": `project_doc_fallback_filenames` defaults to `[]`.
- "Copilot: no longer than 2 pages": the phrase sits in an example prompt, not a stated limit.
- Vercel's "53 %" for skills equals its no-docs baseline; a skill with an explicit instruction to
  use it scored 79 %.
- Tool-generated summaries of PDFs were wrong during research for this skill; quote the paper.
