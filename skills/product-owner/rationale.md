# Rationale — the evidence behind each rule (researched 2026-08)

Why the skill's rules are what they are, with sources. Labels: **EVIDENCE** (study/RCT/
large-N dataset), **CONSENSUS** (independent vendors/practitioners converge),
**CONTESTED** (credible published disagreement), **VENDOR** (self-reported, unaudited).
Distilled from a 7-stream parallel research sweep, 2026-08-27.

## The ticket is the agent's prompt

- **EVIDENCE** — 3,180 real Copilot-coding-agent PRs (AIDev dataset): well-scoped issues
  +16% merge rate, self-contained +17%, unambiguous +8%, actionable steps +8%; **longer
  descriptions −9%**, external dependencies −7%, environment specs −9%,
  performance-sensitive work −34%.
  [arxiv.org/html/2512.21426v1](https://arxiv.org/html/2512.21426v1)
  → the skeleton, the concision cap, self-containedness, splitting env/setup out, and
  routing performance-sensitive work to humans.
- **EVIDENCE** — UnderSpecBench (2,208 prompt variants, Claude Code/Codex/OpenCode):
  safe success 67.9% → 8.6% as underspecification rises; wrong-target actions 9.6% →
  75.1%. Agents guess instead of asking ([arxiv.org/pdf/2607.02294](https://arxiv.org/pdf/2607.02294));
  Ambig-SWE: interactivity recovers up to 74%, but "models default to non-interactive
  behavior unless explicitly prompted"
  ([arxiv.org/html/2502.13069](https://arxiv.org/html/2502.13069))
  → burn ambiguity down before dispatch; zero open design choices at agent-ready.
- **EVIDENCE** — "What makes a good bug report for an AI agent" (433 SWE-bench issues ×
  87 agents + ablation): fix suggestions 3.6× resolution odds, code snippets 2.8×,
  *executable* repro scripts 2.5×, file/module localization 2.3×; prose repro steps ≈
  nothing; **markdown structure alone worth 10–30 solve-rate points**
  ([arxiv.org/html/2607.07593v1](https://arxiv.org/html/2607.07593v1))
  → bug template with runnable repro + localization hint; headings are load-bearing.
- **CONSENSUS** — GitHub, Anthropic, OpenAI, Cognition converge on the same anatomy:
  problem + complete acceptance criteria + file pointers
  ([GitHub Copilot agent best practices](https://docs.github.com/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks)) ·
  "Give Claude a check it can run … If you can't verify it, don't ship it"
  ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)) ·
  Goal/Context/Constraints/Done-when ([OpenAI Codex guidance](https://learn.chatgpt.com/guides/best-practices)) ·
  "be opinionated", clear requirements + verifiable outcomes at junior-engineer 4–8h size
  ([Devin guidelines](https://docs.devin.ai/essential-guidelines/instructing-devin-effectively),
  [Cognition 18-month review](https://cognition.com/blog/devin-annual-performance-review-2025))
  → the agent-ready gate's seven criteria.
- **CONSENSUS** — pointers beat payloads: context engineering = the "smallest possible
  set of high-signal tokens"; prefer file paths/links over pasted content
  ([Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

## Verification and anti-gaming

- **EVIDENCE** — reward hacking is measured: RL post-training raised exploit rates 0.6%
  → 13.9% ([arxiv.org/html/2605.02964](https://arxiv.org/html/2605.02964)); TRACE
  benchmark (517 trajectories, 54 hack categories): best detector catches only ~63%
  (hard-coded outputs, edited tests)
  ([arxiv.org/html/2601.20103v1](https://arxiv.org/html/2601.20103v1))
  → protected areas always include tests + CI config; held-out checks at review; green
  CI alone never closes a ticket; fresh-context review against intent and scope.
- **EVIDENCE** — LLMs "improving" tickets hallucinate absent Expected/Actual sections
  ~50% of the time even when told not to
  ([arxiv.org/html/2504.18804](https://arxiv.org/html/2504.18804))
  → the MISSING-marker rule: gaps become explicit questions, never synthesized content.
- **EVIDENCE** — testability is the one universally evidenced criterion property: EARS
  measurably reduced ambiguity/vagueness at Rolls-Royce (single industrial case study,
  not a controlled experiment)
  ([Mavin et al., RE'09](https://research.manchester.ac.uk/en/publications/easy-approach-to-requirements-syntax-ears/));
  adopted as AWS Kiro's AC grammar ([kiro.dev/docs/specs](https://kiro.dev/docs/specs/)).
  No controlled evidence that Gherkin beats plain checklists; BDD reviews show real
  maintenance cost ([IEEE](https://ieeexplore.ieee.org/document/10210040/))
  → EARS as default behavior-criterion grammar; Given/When/Then only where it becomes a test.

## The review bottleneck

- **VENDOR** (telemetry; magnitudes unaudited, direction corroborated by LinearB and
  DORA) — Faros AI, 10k+ devs, 1,255 teams: high-AI teams +21% tasks, +98% merged PRs,
  but **review time +91%, PR size +154%, bugs +9%, org-level DORA flat**
  ([faros.ai on DORA 2025](https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025));
  2026 update (22k devs): task throughput +34%, review time +441%, 31% more PRs merged
  unreviewed, agent PRs wait ~5× longer for pickup
  ([faros.ai 2026 report](https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways),
  [LinearB benchmarks](https://blog.exceeds.ai/linearb-code-review-metrics-2026/))
  → WIP anchored on review capacity (3–5 per reviewer); review column with own cap +
  SLE; "clear the review queue" beats "start more".
- **EVIDENCE** — DORA 2024: +25% AI adoption ↔ −1.5% throughput, −7.2% stability; DORA
  2025: throughput flips positive, instability stays negative — AI is an amplifier;
  small batches are the converting mechanism
  ([dora.dev/dora-report-2025](https://dora.dev/dora-report-2025/),
  [AI capabilities model](https://dora.dev/ai/capabilities-model/report/))
  → split gates are not hygiene, they're the mechanism; every speed metric paired with
  a stability guardrail.
- **CONSENSUS** — "full kit" review packets (what/why/risk/evidence/limitations) exploit
  the constraint ([Yuval Yeret](https://yuvalyeret.com/blog/ai-coding-made-code-review-the-bottleneck/))
  → the evidence-comment format.
- **CONSENSUS** (documented incident, not a study) — curl's bug bounty drowned in AI
  slop (~20% of submissions, ~5% genuine); its test suite was the effective filter
  ([LeadDev](https://leaddev.com/software-quality/open-source-has-a-big-ai-slop-problem))
  → every criterion maps to an automated check; no human review until gates are green;
  machine-authored tickets enter as draft, never agent-ready.

## Ownership and process shape

- **CONSENSUS** — Linear's delegation model: agent = delegate, human stays accountable
  owner; agents disclose, acknowledge, emit progress
  ([linear.app/developers/agents](https://linear.app/developers/agents),
  [AIG](https://linear.app/developers/aig)) → the claim protocol.
- **CONSENSUS** — mid-task scope change is a top agent-failure cause; corrections go as
  PR comments, new scope = new ticket
  ([GitHub agentic workflows](https://github.blog/ai-and-ml/github-copilot/from-idea-to-pr-a-guide-to-github-copilots-agentic-workflows/),
  [Cognition](https://cognition.com/blog/devin-annual-performance-review-2025)).
- **CONSENSUS** — risk tiers decide automation level; human approval mandatory for
  critical code; least-agency identities
  ([Anthropic AI-native SDLC](https://claude.com/blog/how-anthropic-secures-its-ai-native-software-development-lifecycle),
  [Microsoft least privilege for agents](https://www.microsoft.com/en-us/security/blog/2026/07/16/least-privilege-for-ai-agents-identity-access-and-tool-binding/)).
- **CONTESTED** — spec-driven maximalism: Spec Kit produced 2,577 markdown lines for 689
  code lines, ~10× slower than iterative prompting on small work
  ([Scott Logic](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html))
  → ceremony scales with size × risk × ambiguity; chores stay title + Problem.
- **VENDOR** — Atlassian's AI-native team: tickets as "executable specs" scored 4.47/5
  vs 2.72, 83% vs 6% agent-ready, widest gap = AC clarity; ~180 small tickets/engineer
  vs ~43 ([Atlassian](https://www.atlassian.com/blog/jira/writing-tickets-for-ai-agents))
  — treat the multipliers as marketing, the ticket-shape recipe as corroboration.

## Flow, forecasting, prioritization

- **CONSENSUS** (normative standard, not a study) — Kanban Guide 2025.5:
  WIP/Throughput/Work Item Age/Cycle Time mandatory;
  SLE = elapsed time + probability; Work Item Age is the only leading indicator;
  right-sizing = "fits the SLE?"
  ([kanbanguides.org](https://kanbanguides.org/the-kanban-guide/2025.5/),
  [Open Guide](https://kanbanguides.org/open-guide-to-kanban/2025.7/)).
- **CONSENSUS** — Monte Carlo over item counts replaces points; "plans based on averages
  fail on average"; forecasts void on regime change (agent adoption is one)
  ([InfoQ/#NoEstimates](https://www.infoq.com/articles/noestimates-monte-carlo/)).
- **CONSENSUS** — Reinertsen holds: queue time dominates cycle time (Maersk: one feature,
  38 weeks in queues, ~$8M delay cost); CD3 sequencing; **summed-ordinal WSJF is
  undefined arithmetic** ([Black Swan Farming](https://blackswanfarming.com/cost-of-delay/),
  [Jason Yip](https://jchyip.medium.com/problems-i-have-with-safe-style-wsjf-772df2beaf02))
  → cost-of-delay classes + shortest-job-first; scores structure arguments, never auto-rank.
- **CONSENSUS** — confidence needs an evidence ladder (opinion → anecdote → data →
  experiment), or every idea scores maximum
  ([Itamar Gilad](https://itamargilad.com/tag/prioritization/)).
- **CONTESTED** — backlog bankruptcy: bulk-close stale *internal ideas* ("really
  important ideas will come back to you", [Shape Up](https://basecamp.com/shapeup/2.1-chapter-07),
  [Mountain Goat](https://www.mountaingoatsoftware.com/blog/product-backlog-bankruptcy));
  but stale-bots on user-reported issues destroy trust
  ([kubernetes#103151](https://github.com/kubernetes/kubernetes/issues/103151))
  → the class-split staleness policy.
- **CONSENSUS** — metrics get gamed as targets (Goodhart); DORA warns against ranking
  teams/individuals ([How to misuse DORA metrics](https://newsletter.getdx.com/p/misuse-dora))
  → system-level only, never per-assignee.

## Debunked — never cite these

- **The 1×/10×/100× defect-cost curve**: traced to untraceable 1981 training notes
  (Bossavit); the largest study (171 projects) found **no delayed-issue effect**
  ([Menzies et al., EMSE 2017](https://arxiv.org/pdf/1609.04886)). The defensible
  justification for refinement gates is wrong-work risk (quantified above).
- **Perceived AI speed**: METR RCT — 16 experienced maintainers, 246 real tasks, **19%
  slower with AI while believing 20% faster**
  ([arxiv.org/abs/2507.09089](https://arxiv.org/abs/2507.09089)) → measure the board's
  own per-class outcomes; never plan on vendor multipliers.
- **INVEST / the user-story template as validated practice**: perception-only evidence
  ([Lucassen et al., REFSQ 2016](https://webspace.science.uu.nl/~dalpi001/papers/luca-dalp-werf-brin-16-refsq.pdf))
  → INVEST is a conversation heuristic; the story line is optional Problem-opener.

## Deliberately NOT encoded (fashionable-but-wrong)

Story points / velocity / any estimate-theater field · mandatory "As a user…" templates ·
full spec pipelines on every ticket · mandatory Gherkin · summed-ordinal WSJF or precise
RICE as ranking authority · flow-efficiency percentage gates · hierarchies deeper than 3
levels or PI-planning cadence · age-based auto-closure of user-reported bugs ·
per-person/per-agent metric rankings · "the agent will ask when confused" as a safety
mechanism · exhaustive tickets as better tickets · vendor multipliers as planning
assumptions.
