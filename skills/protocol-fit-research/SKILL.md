---
name: protocol-fit-research
description: Evaluates an external protocol, standard, or ecosystem tool (MCP, A2A, ACP, AG-UI, AHP, an emerging spec, a competing product) against a project's own architecture seams using a parallel research fan-out, then lands a verdict-led report in the project's survey docs with adoption recommendations and named re-evaluation triggers. Use when asked how a protocol relates to our stack or components, whether a spec, standard or tool matters to us or is worth adopting, to do deep or exhaustive research on a spec URL, to compare a new protocol against the one we already bet on, or for a protocol or market-landscape survey.
---

# Protocol-fit research — landscape question to verdict-led report

## Scope first

| Ask | Do |
|---|---|
| Single fact ("what transport does X use?") | One fetch, answer inline. No fan-out. |
| "Does X matter to **us**", "how does X fit our design", "deep research on X" | Full sweep below |
| Field survey ("what exists for X") or "what did version N change" | [Landscape fan-out](reference.md#landscape-fan-out) or [release-notes research](reference.md#release-notes-research), then land it as in step 4 |

## 1. Resolve the landing contract

Findings land in the repo, so learn where before researching. Read the consumer repo's `AGENTS.md`/`CLAUDE.md` for a **Protocol research contract** block (template in [README.md](README.md)) naming its ledger, watchlist, and dossier dir.

No block? Infer, and state the inference in the report: ledger = the design/RFC doc's "alternatives considered" table; watchlist = the backlog/roadmap doc; dossier dir = `docs/research/`.

## 2. Fan out (launch all agents in one parallel block)

1. **Spec/docs crawl** — exact abstraction names, full method/transport inventory, lifecycle states, discovery mechanism, verbatim quotes positioning it against other protocols, stated anti-goals, maturity/versioning statements.
2. **Source repo dig** — normative schema location, release cadence, contributor concentration (single vendor or genuinely cross-org?), governance, load-bearing open issues, real dependents, SDK maturity **in the consumer project's language**.
3. **Ecosystem + absence checks** — announcement timeline, positioning vs adjacent protocols, shipped-vs-press-release adoption, strongest critiques, and explicit **absence checks naming each of the project's own components**. A confirmed zero-mentions is a finding; say so in the prompt.
4. **Local seam map** — read-only agent over the project repo: components, who calls whom over what transport, existing protocol seams, aspirational-vs-implemented contracts, roadmap and watchlist items. File path for every claim.

Prompt discipline for all four (full templates → [reference.md](reference.md)): final message is consumed as raw data; exact names and links; report absences; no padding.

**Read the project's own architecture docs yourself while they run** — the seam mapping is your synthesis, never an agent's.

## 3. Synthesize

Verdict sentence first, then: what it actually is (mechanics condensed, self-description quoted) → **layer-map table** marking seams nobody claims → component-by-component fit (orthogonal, competing or complementary, each citing the project's own files) → the one honest scenario where it could matter, with the architectural tension named → numbered recommendations → re-evaluation triggers. Anatomy and worked shape → [reference.md](reference.md).

## 4. Land it in the repo, same session

Write all three, in the same session, without waiting to be asked:

- **Dossier** — the full evidence trail, dated filename, in the dossier dir.
- **Ledger row** — dated verdict row matching neighboring rows' density; link the dossier.
- **Watchlist item** — only when adoption is conditional: prerequisites (existing backlog ids) plus the flip triggers, linked both ways with the ledger.

Re-confirm or amend any **existing** entry the sweep touches (a rejected alternative, a protocol the project already bet on) — new evidence for a standing bet is a finding worth recording.

## Gotchas

- **Never park the verdict in agent memory or a per-user store** — it must be readable by anyone cloning the repo. Memory is invisible to the team and to every other machine.
- **Never answer from prior knowledge of a young protocol.** Names lie; crawl first. (AHP sounds like orchestration; it is client-facing session sync.)
- **A dated record is a claim about its date.** Before building on an earlier dossier, ledger row or a ticket marked done, check what landed since: `git log --since=<record date> --format='%h %ci %s' -- <paths>`, and for a done ticket `git log --all --grep='<ticket id>'`. Parallel sessions can fix half a dossier's findings minutes after it is committed, and a closed ticket can have no code on the trunk.
- **Maturity is not fit.** A 1.0 spec with cross-org governance and a GA SDK still loses if it claims a seam the project does not have. Say which of the two killed it.
- **Adoption claims need a shipped artifact** — docs, an endpoint, merged code. Partner-logo press releases and governance seats are not adoption.
- Pre-1.0 + single vendor + sole reference implementation defaults to "watchlist, adopt nothing" — and the recommendation must name the trigger that flips it, never "keep an eye on it".
- A rejection that names no trigger gets re-litigated in six months. Triggers are the deliverable.
- Background agents killed by a session restart are resumable — message each to resume instead of relaunching.
