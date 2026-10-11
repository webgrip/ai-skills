# Decision rounds

Each question on the answer page has: the question, why it matters (one sentence), a recommendation
with its trade-off, a few options, and a free note. Never ask by id or label alone. Questions an
accepted ADR already answers are left out or reduced to their open part.

## Round 1 — who and what

Per role: the classification (core, secondary, edge, outside the product, not a user) plus a note.
Per core role: "do these needs match?" (yes, mostly, no) plus a note. Per draft journey: "is this
the journey?" plus a note. Then:

| Id | Question | Why it matters | Common default |
|---|---|---|---|
| Q1 | Who is the one primary user for the next few months? | every screen gets optimised for someone | the person who hands work over and reviews it |
| Q2 | Who may start or hand over work? | decides who sees the controls and how much guarding they need | leads and seniors in the product, anyone through the tracker |
| Q3 | Where does the product owner live? | product owners in the product need their own views and roles | the tracker |
| Q4 | Is the person who hands work over always its reviewer? | if not, the product needs review routing | yes at first, routing later |
| Q5 | Do junior developers get access, and how much? | juniors may start work they cannot judge | read and ask only |
| Q6 | Should Ready work start by itself? | the fastest hand-off is none, and it spends without a click | not yet; first make the manual path fast |
| Q7 | Which journey gets designed first? | the next design pass follows this order | the one that decides trust (often review) |
| Q8 | How should the primary user feel after a day with the product? | becomes the test for every screen | free text, quoted verbatim |

Defaults are starting points to argue with. Record the owner's answer even where it overrides one.

## Round 2 — the enterprise layer

| Id | Question | Why it matters |
|---|---|---|
| R1 | Buyer and daily user: is the reading of Q1 right? | journeys split into user journeys and buyer journeys |
| R2 | Clarify any ambiguous round-1 note, with both readings as options | an interpretation written into a doc becomes a false decision |
| R3 | How is a customer organised (organisation, clients, projects)? | every role scope, budget and rule hangs off it |
| R4 | What decides who reviews a change? | code owners, reviewer pools, risk, client policy, load, availability |
| R5 | Which roles ship built in, and can customers define their own? | granular access needs a permission model, not a role list |
| R6 | Which identity providers and provisioning must work? | onboarding and offboarding at enterprise scale |
| R7 | Which policies must customers be able to enforce? | four-eyes, separation of duties, budget caps, allowed models, data region |
| R8 | What has to be provable, and for how long? | audit trail, retention (Dutch fiscal records: seven years), export |
| R9 | Which tools must the top journeys work with? | trackers, forges, chat and editors decide where people are notified |
| R10 | What scale should the design hold at? | a list that works for 5 items breaks at 500 |
| R11 | How do we know each journey works? | each journey needs a measure with a baseline |
| R12 | Anything missing from the top journeys? | candidates you left out, named |

## After a round

1. Read every stored answer back (ids and notes), never summarise from memory.
2. Quote the owner's own words for every decision you record.
3. List conflicts between answers (for example a role ranked secondary but named primary) and every
   note that has two readings; they open the next round.
4. Record the answers as a comment on the epic or decision ticket, by id.
