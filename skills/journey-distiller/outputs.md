# Outputs

Everything lands in the repo or on the board. Chat summaries and answer pages are inputs, not records.

## Concept doc

One page in the repo's concepts or product docs, for example `docs/concepts/users-and-journeys.md`:

1. Who the product is for: buyer and daily users, linking the business doc rather than repeating it.
2. The cast: every role with its classification, what it does and where.
3. Needs: job stories per core role, each with its source; the bar sentence quoted.
4. The top journeys, one section each, every template field from [journeys.md](journeys.md).
5. A permission matrix draft: journey actions × roles, pointing at the roles ADR once it exists.
6. Hypotheses marked as hypotheses; no claim of user research that was not done.

Add new role words to the glossary. Link the page from any existing page that uses "journey" for
system flows.

## ADRs — one per structural decision

Typical set for an enterprise product; write only the ones the rounds left open, with the
`adr-writer` skill:

- roles and permissions (built-in and custom roles, scopes, mapping from identity groups)
- review routing and enforceable review policies
- audit trail and retention
- automatic start of ready work (eligibility, limits, stop switch, record of each start)
- organisation model, only when no ADR covers tenancy yet

## Ticket fan-out

| Ticket | Type | Blocked by |
|---|---|---|
| Epic: the product supports its top N journeys | epic, no acceptance criteria of its own | — |
| Decide round K of the user questions | spike, decider: the owner | — |
| Concept doc | change | the open round |
| One per open ADR | spike, decider named, done = decided and recorded | the open round |
| One per journey, in rank order | change (design), human-executed | the ADR it depends on |

Every ticket follows the `product-owner` skill and its `refine.md`, then passes
`ticket_lint.py --gate ready` before it gets the ready marker:

- source line with date and link, the owner's words in a quote block
- functional half in plain language; a rule; `Technical notes` with paths, Approach and a research
  stamp as the last line
- spikes: Question, Timebox, What we decide on, Who decides, criteria that end in "decided and recorded"
- design tickets: an error-path criterion, a criterion that closes the cheap way out, a verification
  the owner performs, owned open questions, a teaching pass (Why it matters, two or three Learn links)
- dependencies as tracker relations; the record of round answers as a comment on the epic

Write ticket bodies as files first, lint them, then write them to the board in one sequential pass.
