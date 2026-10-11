---
name: journey-distiller
description: Distills who a product is for and which user journeys it must support, before any screen is designed. Classifies the roles around a product (developers by level, leads, product owners, QA, buyers, admins, auditors, clients), runs owner decision rounds on an answer page, writes job stories and needs, ranks the top journeys with actors, stages, permissions, audit events and success measures, then lands it as a concept doc, ADRs and Definition-of-Ready tickets. Use when asked who the users or target audience are, to define personas, roles or user journeys, map a user journey, find the top N journeys to support, think about it in an enterprise way (SSO, RBAC, review routing, audit), when designs keep being rejected because nobody agreed who they are for, or before redesigning a flow such as a hand-off, review or onboarding. Dutch - doelgroep, gebruikers, user journeys, klantreis, wie gebruikt dit.
---

# Journey distiller — users, needs and top journeys before screens

Screens come last. A design judged without agreed users gets rejected for reasons nobody can name;
fix that by deciding the cast, their needs and the top journeys with the owner, in writing.

## Where to start

| Situation | Start at |
|---|---|
| Designs keep getting rejected, or "who is this for?" has no written answer | step 1 |
| Roles exist in docs or ADRs but no journeys | step 1 (read), then step 4 |
| Journeys exist, an enterprise layer is missing (SSO, roles, routing, audit) | step 3, round 2 only |
| One flow to redesign, users already decided | skip this skill; use `product-ux` with the decided journey |

## Procedure

1. **Read what is decided.** Product and pricing docs, ADRs (grep `role`, `tenant`, `SSO`, `group`,
   `permission`, `audit`), the glossary, the role enum in code, the tracker. List each fact with its
   source. A question an accepted ADR answers is never asked again; ask only what it leaves open.
2. **Draft the cast.** For every candidate role: who, what they would do with the product, where they
   mostly work (tracker, forge, editor, portal, this product), your guess (core, secondary, edge,
   outside the product) and the evidence. Separate the **buyer** from the **daily user**.
   Catalog → [cast.md](cast.md).
3. **Run decision rounds with the owner** on an answer page that stores answers where you can read
   them back ([decision-page.md](decision-page.md)). Round 1 classifies roles, checks needs and draft
   journeys, and asks the product questions; round 2 asks the enterprise questions. Question banks
   with defaults → [rounds.md](rounds.md). After each round: read every answer back, quote the owner
   verbatim, list contradictions and ambiguous notes as next-round questions.
4. **Rank the top journeys** by how often they happen and how much they decide trust or adoption,
   with the owner's first pick on top. Fill the journey template for each → [journeys.md](journeys.md).
5. **Write the bar sentence.** Ask the owner how the primary user should feel after a day with the
   product; quote it as the acceptance test for every later screen.
6. **Land it** → [outputs.md](outputs.md): a concept doc, an ADR per structural decision, glossary
   terms, and tickets: an epic, a decision ticket per open round, a doc ticket, ADR spikes, and one
   design ticket per journey in rank order, with dependencies as relations.
7. **Tickets follow the `product-owner` skill in full**, including its `refine.md`: source line with
   the owner's words in a quote block, two readers split by a rule, the spike template for every
   decision, the teaching pass on human-executed work, owned open questions. Run its
   `ticket_lint.py --gate ready` on every body; only a passing body gets the board's ready marker.

## Gotchas

- **Never design or build screens for a flow before its roles are classified by the owner.**
  Polishing one flow first gets rejected however good it looks.
- **"Journey" already means something** in many repos (a system or request flow). Name the new page
  so each page uses the word one way, and cross-link.
- **Entities the customer configures** (teams, roles, workflows) stay variables in every journey; a
  journey that names one installation's teams breaks for the next customer.
- **Ambiguous owner notes are questions, not interpretations.** Offer both readings as options in the
  next round.
- **Private context stays off the page and the tickets**: time budgets, contracts, employer or deal
  details, even when they shaped a recommendation.
- An answer page that only keeps answers in the viewer's browser loses them; read the store back
  before telling the owner where their answers live.

## Additional resources

- Role catalog with typical needs and where each role works → [cast.md](cast.md)
- Round 1 and round 2 question banks, defaults and why each matters → [rounds.md](rounds.md)
- Journey template, ranking rubric and the enterprise fields → [journeys.md](journeys.md)
- Concept doc outline, ADR list and ticket fan-out → [outputs.md](outputs.md)
- Building the answer page and reading answers back → [decision-page.md](decision-page.md)
