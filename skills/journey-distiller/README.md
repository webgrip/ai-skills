# journey-distiller

Decides who a product is for and which user journeys it must support, before anyone designs another
screen. It works with the product owner in rounds and lands the result where a team can use it:
a concept doc, decision records and tickets that pass a Definition of Ready.

What it does:

- **Reads what is already decided** (product docs, decision records, the glossary, the role list in
  code) and never re-asks a settled question.
- **Drafts the cast**: every role around the product, from junior developer to buyer, auditor and
  client, with what each would do, where each works and a guessed classification with evidence.
- **Runs decision rounds** on an answer page that stores the owner's picks and notes where the agent
  can read them back. Round 1 decides who and what; round 2 adds the enterprise layer: organisation
  model, roles and permissions, single sign-on and provisioning, review routing, policies, audit and
  retention, integrations, scale and success measures.
- **Ranks the top journeys** by frequency and by how much they decide trust or adoption, each with
  actors, trigger, done-when, stages per tool, permissions, audit events, states, today's status and
  a success measure.
- **Lands it**: a users-and-journeys concept page, one decision record per structural question, and a
  ticket fan-out (epic, decision spike, doc ticket, ADR spikes, one design ticket per journey) written
  to the `product-owner` skill's standard and linted before anything is marked ready.

The reusable answer page is [assets/decision-page.html](assets/decision-page.html): fill its JSON
block, publish it, read the answers back.

## Install

```text
/plugin install journey-distiller@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s journey-distiller`.

## Example prompts

- "Describe our target audience: junior devs, seniors, leads, POs, clients. Who uses this?"
- "What are the top 10 user journeys we must support, in an enterprise way?"
- "Designs keep getting rejected. Before we go on, who is this actually for?"
- "Turn the journeys we decided into tickets on the board."

## Works with

`product-owner` (tickets and the Definition of Ready), `adr-writer` (decision records),
`domain-language` (glossary terms), `product-ux` (designing each journey once it is decided).
