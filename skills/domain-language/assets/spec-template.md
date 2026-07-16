# Spec: [Feature name]

> Status: draft | Model: docs/domain/model.yaml (version [x.y]) | Author / date

## Summary
One paragraph: what this feature does and for whom, written entirely in canonical domain terms.

## Motivation
Why now. What problem, measured how.

## Behavior
The feature described as scenarios. Use canonical terms with their glossary capitalization; cite business rules by id instead of restating them.

**Scenario: [name]**
- Given [state, in domain terms]
- When [action/event]
- Then [outcome] (must satisfy **R_n**)

## Changes to the domain model
List any new or changed terms, entities, states, rules, or events this feature introduces, and any open ambiguities this spec resolves. These must be added to `docs/domain/model.yaml` before the spec is accepted — the spec is never the only home of a definition, and a spec must not depend on a term that is still flagged ambiguous. Write "None" if the language is untouched.

## Out of scope
What this feature deliberately does not do.

## Open questions
Numbered, each with an owner.

## Language used
Auto-list every glossary term and rule id referenced above, e.g.:
Terms: Order, Shipment, Customer · Rules: R1, R3
(Reviewers use this to spot vocabulary that isn't in the model.)
