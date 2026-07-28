# protocol-fit-research — reference

Contents: [agent prompt templates](#agent-prompt-templates) · [report anatomy](#report-anatomy) ·
[verdict archetypes](#verdict-archetypes) · [landing conventions](#landing-conventions) ·
[re-evaluation triggers](#re-evaluation-triggers) · [failure modes](#failure-modes-seen-in-practice)

## Agent prompt templates

Open every prompt with the same discipline line, then the role block:

> You are a research agent. Your final message is consumed as raw data by another agent — no
> padding, no pleasantries, exact names and links throughout. Report absences explicitly; a
> confirmed "no support anywhere" is a finding, not a gap in your work.

**1 — Spec/docs crawl.** Name the canonical docs site and spec repo. Demand: current version and
its exact date, verbatim versioning/stability statements; every core abstraction spelled exactly
as the spec spells it, one line each; the complete method/operation inventory with transports
(and which are required vs optional); lifecycle states as exact enum names; the discovery
mechanism including exact well-known paths; verbatim quotes with URLs about its relationship to
adjacent protocols; explicit anti-goals; the security/auth model; maturity markers and what broke
between versions. Add whichever axis the consuming project lives on (long-running tasks,
human-in-the-loop, streaming, multi-tenancy).

**2 — Source repo dig.** Canonical org and repos. Demand: repo inventory with stars, language,
last-commit recency; where the normative schema lives and its exact path; release cadence with
dated tags for spec and SDKs; contributor concentration by affiliation and the governance body
with named seats; the most load-bearing open issues with one-line summaries; real dependents
distinguished from announced partners; **SDK maturity in the consuming project's language**, named
as such (API surface, release status, maintainer count).

**3 — Ecosystem + absence checks.** Two parts. Part 1: dated announcement timeline with links;
positioning vs each adjacent protocol, disambiguating name collisions; adoption split into shipped
(documented feature, endpoint, merged code) vs press release; the strongest three to five
critiques with links. Part 2: an explicit absence check per component — **list the consuming
project's actual components by name** and require a verdict line for each, with URL and date.

**4 — Local seam map.** Read-only, over the consuming repo. Demand: component inventory with file
paths; each pluggable seam as its interface name, path, implementations, and how a new one
registers; who calls whom over what transport; existing protocol mentions anywhere in code or
docs, including zero-hit greps; the task/state lifecycle; roadmap, backlog and watchlist items
about the relevant layer. File path for every claim.

## Report anatomy

Lead with the verdict sentence — adopt / adopt-narrowly / watchlist / reject, plus the one reason.
A reader who stops there must still be correctly informed.

1. **What it actually is** — mechanics condensed to what changes a decision, self-description
   quoted verbatim with a link. Include governance and SDK-in-our-language as facts, not comfort.
2. **Layer map table** — one row per seam of the project: what implements it today, what the
   project has already bet on, what this protocol claims. Mark seams **nobody** claims; that empty
   row is usually where the honest scenario lives.
3. **Component-by-component fit** — orthogonal, competing, or complementary, each citing the
   project's own files. An absence belongs here as evidence.
4. **The one honest scenario** — the single place it could earn its keep, with the architectural
   tension named out loud (which invariant or non-goal it strains, and the shape that survives it).
5. **Implementation path** — phased cheapest-first, ending with an explicit *never* list.
6. **Numbered recommendations** and **re-evaluation triggers**.

## Verdict archetypes

| Archetype | Signature | Verdict |
|---|---|---|
| Wrong layer | Mature, well-governed, but claims a seam the project does not have | Reject for internals; watchlist a facade at the unclaimed seam |
| Right layer, immature | Fits a real seam; pre-1.0, single vendor, one implementation | Watchlist with a version/second-implementation trigger |
| Right layer, competing bet | Fits a seam the project already bet on | Compare head-to-head; re-confirm or switch the bet explicitly |
| Adjacent product, not protocol | Overlaps the roadmap, owns its own control plane | Reject as dependency; mine its design and fold specifics into the backlog |

Mining a rejected option's design is a legitimate outcome — record what was folded in and where.

## Landing conventions

The **Protocol research contract** block in the consumer repo's `AGENTS.md`/`CLAUDE.md` names the
three destinations (template in [README.md](README.md)). Absent the block, infer and say so.

- **Dossier** — dated filename, e.g. `docs/research/2026-07-28-a2a-fit.md`. Opens with a blockquote
  stating the survey date, the method (how many agents, which angles), and where the condensed
  verdict lives. Then verdict, then sections 1–6 of the anatomy, every claim carrying its URL.
- **Ledger row** — one row in the alternatives table, matching neighbors' density. Pattern:
  what it is and its maturity → the seam it claims → why that does or does not fit, with the
  project's own file references → the conditional fit → flip triggers → dossier link.
- **Watchlist item** — prerequisites as existing backlog ids, the blocked-until condition, named
  repos/issues to watch, and an explicit rejected-shape line so the item is not re-argued from
  scratch. Link the ledger row; link back from it.

Write all three in the same session. Owner approval gates *acting on* a verdict, never *recording*
one.

## Re-evaluation triggers

A trigger is falsifiable and observable without re-running the sweep. Good ones name a version
milestone, a specific repo or issue to watch, a component landing in the stack, or a dated review
gate the project already has. "Keep an eye on it", "if adoption grows", and "revisit next year"
are not triggers.

State them as "any one of these reopens this": the reader should be able to check each in minutes.

## Failure modes seen in practice

- **Answering from prior knowledge.** Young protocols rename and re-layer between minor versions,
  and names mislead. Crawl, then answer.
- **Maturity theater.** Spec 1.0, foundation governance, and eight vendor logos say nothing about
  fit. Separate the two verdict axes explicitly.
- **Press-release adoption.** Governance seats and partner lists are not shipped code. A founding
  member with no GA integration is evidence *against* momentum.
- **Name collisions.** Two unrelated protocols sharing an acronym is common; establish which one
  the question is about, and note the other so the reader is not confused later.
- **Burying the absence.** "Zero mentions across every component we run" is often the single most
  decision-relevant sentence in the sweep. Put it in the verdict, not an appendix.
- **Verdict in the wrong place.** A finding parked outside the repo is invisible to the team and
  gets re-researched. The repo is the record.
