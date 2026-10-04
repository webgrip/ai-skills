# Evidence: what is known about refactoring for agent cost

Strength labels: **Strong** (controlled or large-sample) · **Consistent** (several sources agree) · **Contested** · **Anecdotal** (one run, one team, or vendor data not published).

Contents: the anchor experiment · the controlled study · where agent tokens go · what helps and what hurts · why the problem recurs · claim table

## The anchor experiment

Giles Edwards-Alexander, "The Economic Benefit of Refactoring", martinfowler.com, 30 July 2026 ([article](https://martinfowler.com/articles/exploring-gen-ai/refactoring-economic-benefit.html)).

- **System:** a ~150k-line, mostly Rust application built entirely by agents without code review. Target: one 17,155-line data-access file.
- **Method:** plan the refactoring, write one representative change (add an `ItemWatchStore` trait with three methods on the real and the fake store, "following existing patterns"), run it with a fresh agent, discard it, apply one refactoring step, run the same change again, repeat over 15 Fowler-catalog steps.
- **Result:** input tokens for the change fell from 159,564 to 27,360 (−83 %). Output tokens rose slightly (1,705 → 2,113). Total lines stayed about the same; the largest file went from 17,155 to 3,695 lines.
- **Mechanism:** "the agent must be able to successfully identify the smallest subset of files necessary to read." "Randomly cutting the file into smaller files is unlikely to help as much."
- **Execution findings:** Claude could not choose suitable refactorings unaided; a human had to guide it. Mechanical edits via Python/grep/sed scripts got confused by indentation. The most valuable refactoring was missed on the first pass.

**Weaknesses that the procedure in this skill fixes:**

| Weakness | Why it matters | Fix in this skill |
| --- | --- | --- |
| One run per step | Same task, same code varies ~2.5× typically and up to 30× | ≥ 5 interleaved runs per variant, median and interval |
| Non-monotonic series: step 12 measured 104,080, the state before step 15 measured 131,871, though the file only shrank | Run-to-run noise of tens of percent inside the experiment | Bootstrap interval on the ratio; don't attribute a single cliff to a single step |
| Characters ÷ 4 of content read, not billed tokens | Billing is dominated by cache reads; token cuts can fail to cut dollars | Read the agent's own usage stream; price every token class |
| Refactoring cost not measured (upper bound 5M tokens) | Return on investment can't be computed | Meter the refactoring sessions with the same harness |
| One change type, one greenfield single-developer repo | Pattern-following benefits most from a small exemplar file | Several representative changes from the area's real history |
| Priced at "$3/MTok" for Sonnet 5 | Sonnet 5 is $2 input / $10 output (introductory price made permanent) | Dated price file, recomputed costs |

Re-priced at current rates the saving is about $0.26 per change single-pass; with cache re-reads inside a session more, and with a 5M-token refactoring it breaks even after roughly 17–40 changes depending on how the tokens bill (`scripts/roi.py`). Hacker News discussion: [item 49111176](https://news.ycombinator.com/item?id=49111176). **No independent replication exists** as of October 2026.

## The controlled study

Trivedi & Schmitt (SonarSource), "Does Code Cleanliness Affect Coding Agents? A Controlled Minimal-Pair Study", [arXiv 2605.20049](https://arxiv.org/abs/2605.20049), May 2026. Six behaviourally equivalent repository pairs (clean vs messy), 33 tasks, 660 Claude Code trials.

| Measure | Cleaner vs messier |
| --- | --- |
| Pass rate | unchanged |
| Input tokens | −7.1 % |
| Output tokens | −8.5 % |
| File revisits | −34 % (every repository the same direction) |
| Multi-module tasks | input −10.7 %, revisits −51 % |
| Cognitive-hotspot tasks (extraction inside one hotspot) | input +1.8 %, files read +11 % |
| Per-task spread | −47 % to +44 %; cleaner side cheaper on 16 of 27 tasks |
| Run-to-run spread | max/min typically ~2.5×; one task 1.4M–10.6M input tokens |

**Read this as:** the direction is real, the typical size is single digits to low teens of percent, and the gain sits in **boundaries and cohesion across modules**, not in making every function small. Extraction that spreads one concern over more files is token-neutral. Expect large per-task variation.

## Where agent tokens go

| Finding | Strength | Source |
| --- | --- | --- |
| Read operations are ~76 % of agent tokens; edits ~12 % | Strong | [SWE-Pruner, arXiv 2601.16746](https://arxiv.org/abs/2601.16746) |
| Input drives cost; the same task varies up to 30× in tokens; expensive runs repeat file views; cache reads dominate dollar cost in every phase | Strong | [Bai et al., arXiv 2604.22750](https://arxiv.org/abs/2604.22750) |
| Token reduction is not cost reduction: −38 % tool-output tokens raised billed cost 6.8 % | Strong | [Weinberger & Hozez, arXiv 2607.12161](https://arxiv.org/abs/2607.12161) |
| Agents localise with grep and names; given a language server, they used it 0–6 % of the time | Consistent | [arXiv 2608.13568](https://arxiv.org/abs/2608.13568) |
| Agentless localises via file names and declaration skeletons | Strong | [Xia et al., arXiv 2407.01489](https://arxiv.org/abs/2407.01489) |
| Removing identifier names sharply degrades LLM code performance | Strong | [Le et al., arXiv 2510.03178](https://arxiv.org/abs/2510.03178) |
| Whole-file views hurt agent success versus windowed views; long contexts degrade | Strong | [SWE-agent, arXiv 2405.15793](https://arxiv.org/abs/2405.15793); [Chroma context rot](https://www.trychroma.com/research/context-rot); [Lost in the middle](https://arxiv.org/abs/2307.03172) |
| 60–69 % of agent failures reach the right code and still produce a wrong patch | Strong | [Kim et al., arXiv 2603.24631](https://arxiv.org/abs/2603.24631) |

So a large, multi-concern file forces wide reads and re-reads; small cohesive files with telling names let one grep and one read hit the target. Findability does not fix everything: tests and other sensors still matter.

## What helps and what hurts

**Likely to help, in order of evidence:**

1. **Names that make grep land first time**: descriptive, domain-aligned, unique identifiers and file names. Consistent.
2. **Move behaviour into cohesive, domain-named modules** (per aggregate, per interface, per trait) so a change touches one small file plus its exemplar. The anchor's cliff came here; Sonar's multi-module track is the measured version. Consistent.
3. **Remove duplication before splitting.** Duplicates make agents update one copy and miss others and inflate reading; new code that calls helpers also writes fewer output tokens. Consistent mechanism, little direct measurement.
4. **Contracts in their own file** (interfaces, traits): the agent reads the contract without the implementation. Hypothesis.
5. **Co-locate tests with the code under test.** Anecdotal for tokens, consistent as a feedback practice.
6. **Remove dead code.** Tokens read for nothing. Hypothesis, near-zero risk when nothing reaches it.
7. **Enforced boundaries** (layer rules, file-size and naming lints) to stop re-accretion. Consistent among practitioners ([OpenAI harness engineering](https://openai.com/index/harness-engineering/), [Böckeler](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)).

**Likely to hurt or not help:**

- **Splitting by line count** or "random cutting": more files read, tokens neutral. Consistent.
- **Script-based mechanical splitting** without design intent. Anecdotal.
- **Agent-led refactoring without selection guidance**: agents default to renames and annotation edits ([arXiv 2511.04824](https://arxiv.org/abs/2511.04824), [arXiv 2601.20160](https://arxiv.org/abs/2601.20160)). Consistent.
- **Indirection-heavy designs** (registries, factories, deep inheritance) that scatter one behaviour. Hypothesis, no controlled measurement.
- **Big repository overviews** in AGENTS.md as a substitute for structure: one study found no gain and +20 % cost ([ETH, arXiv 2602.11988](https://arxiv.org/abs/2602.11988)); another found −16.6 % output tokens ([arXiv 2601.20404](https://arxiv.org/abs/2601.20404)). Contested. A short index of non-obvious entry points is the defensible middle.

## Why the problem recurs

- AI-era code duplicates more and refactors less: moved (refactored) lines fell from 21 % of changes in 2022 to 3.8 % in 2026; block duplication rose 81 % ([GitClear 2026](https://www.gitclear.com/the_ai_code_quality_maintainability_gap); vendor, correlational).
- Cursor adoption brought +30 % static-analysis warnings and +41 % complexity, which then slowed velocity ([He et al., arXiv 2511.04427](https://arxiv.org/abs/2511.04427); difference-in-differences, 806 repositories).
- Agents extending their own code erode structure in 77 % of trajectories, and quality prompts don't change the rate of decline ([SlopCodeBench, arXiv 2603.24755](https://arxiv.org/abs/2603.24755)).
- So a one-off refactoring decays. Lock it in with mechanical checks and a recurring cleanup cadence ([refactorings.md](refactorings.md#lock-it-in)).

## Claim table

| Claim | Strength | Use in this skill |
| --- | --- | --- |
| One refactoring cut input tokens 83 % for one change | Anecdotal (n = 1 per step) | Motivation and method, never the expected saving |
| Cleaner code: −7 % input, −34 % revisits, same pass rate | Strong (direction) | Set expectations at single digits to low teens of percent |
| Gains concentrate in multi-module tasks; hotspot extraction is token-neutral | Strong (one study) | Prefer boundary and cohesion refactorings |
| Runs vary ~2.5× typically, up to 30× | Strong | ≥ 5 runs per variant, intervals, safety factor in decisions |
| Cache reads dominate dollar cost; token cuts ≠ dollar cuts | Strong | Price every token class; report cost per passing change |
| Healthy code lowers AI break rates 15–30 % for mid-size models, not for frontier Claude Code | Strong / null | Correctness benefit is model-dependent; don't promise it |
| Unhealthy code costs 35–45 % more tokens | Anecdotal (vendor) | Mention as vendor data only ([CodeScene](https://codescene.com/blog/unhealthy-code-is-burning-your-token-usage-heres-the-data)) |
| IDE refactoring engine instead of text edits: −64 % cost, −83 % time per solved task | Consistent (vendor, clean design) | Prefer tool-driven refactorings ([JetBrains](https://blog.jetbrains.com/dotnet/2026/08/19/rider-refactoring-code-skill/)) |
| Agents can't choose suitable refactorings unaided | Consistent | Human or stronger-model selection, one approved step at a time |
| A few percent of files take a disproportionate share (often 10–25 %, sometimes over half) of changes | Consistent | Target hotspots; payback scales with future changes ([CodeScene docs](https://codescene.io/docs/guides/technical/hotspots.html), [Tornhill 2025](https://techleadjournal.dev/episodes/241/)) |
| Move refactorings raise merge-effort likelihood by over 400 % | Strong | Never refactor a hotspot under parallel branches ([Oliveira et al., arXiv 2608.15384](https://arxiv.org/html/2608.15384)) |
