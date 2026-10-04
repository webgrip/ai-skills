---
name: product-ux
description: Designs, critiques and builds product interfaces people use repeatedly (apps, dashboards, admin tables, forms) from evidence, not taste - job stories, a frequency and error-cost task model, a state matrix before screens, evidence-tiered pattern rules, a WCAG 2.2 and EU deceptive-pattern floor, heuristic evaluation and KLM, and a UI source scanner. Use when designing, building or reviewing an app screen, area or flow, such as account settings, profile, password or delete-account pages; improving the usability of a form, table, dashboard, navigation, search, empty or error state or onboarding; adding an AI feature to a product (suggested replies, drafts, an assistant, agent actions); a subscription cancel or churn-reduction flow with retention offers, a consent or checkout flow; design tokens or components; UX copy or error messages; an app accessibility audit; or when asked why a screen is confusing or slow. Not for marketing-page art direction (expressive-design) or chart construction (dataviz).
---

# Product UX

Make the task fast, safe and obvious for the person doing it for the two-hundredth time, and learnable for the person doing it the first time. In product UI, familiarity is a feature, evidence beats taste, and an unexercised state is not a pass.

## Know which rules bind

Every rule in the reference files carries a tier:

| Tier | Meaning | How to apply |
| --- | --- | --- |
| **[S]** standard | WCAG 2.2, NIST, HTML spec, platform guidelines, law, live-service-tested systems (GOV.UK) | Hard floor |
| **[E]** empirical | Studies and large audits (Baymard, NN/g, peer-reviewed HCI) | Apply in context, cite the source |
| **[C]** convention or taste | Expert opinion, design-system habit, numeric defaults | A default with a reason; the project's own system and the brief override it |

Folklore is never cited as evidence: Miller's 7 ± 2 as a menu limit, Hick as "fewer is faster", the 400 ms Doherty threshold, Zeigarnik, the thumb-zone chart. → [evaluation.md](evaluation.md#laws-and-folklore)

## Scale the procedure

| Request | Run |
| --- | --- |
| New feature, flow or screen set | All steps |
| Critique or audit of an existing UI | 1, 3 (states only), 7, 8 |
| Change to one component or screen | 4, 5, 6, then scan and a keyboard check |
| Copy, error messages, empty states | 5 ([content.md](content.md)) and 7 |
| Landing, launch or campaign page | Load `expressive-design` instead |

## Procedure

1. **Ground in evidence.** List what you actually have: tickets, analytics, search logs, code, docs, existing screens, supplied facts. Write 3–7 job stories ("When…, I want to…, so I can…"), each tagged with its source, and a proxy top-task ranking labelled as a proxy. Never invent personas, quotes or user numbers. → [framing.md](framing.md)
2. **Model the tasks.** Write a task analysis per top task from the code. Score frequency and cost of error: frequent tasks get speed (defaults, shortcuts, bulk, no confirmation, no animation), and costly ones get safety (preview, undo, confirmation only when irreversible). Put the unproven beliefs on an assumptions map. → [framing.md](framing.md#task-model)
3. **Map flows and states before screens.** For each flow, cover entry points (including cold deep links), exits (what survives cancel, Back and a closed tab), interruptions (session expiry, conflict, revoked permission) and the result (always a next step). Then work the state matrix:
   - **Rows:** each screen's states (first use, no results, one, huge, loading, slow, partial, error, offline, no permission, read-only, conflict, success).
   - **Columns:** role, device and preference.
   - **Coverage:** render the cells by risk.
   - **Statechart:** model interacting booleans as one state machine.
   - **Fixture:** build a worst-case one from the real schema.

   → [states.md](states.md)
4. **Use what exists.** Read the design contract, tokens, component library and the three most similar screens before writing UI. Choose controls by ladder: native element, then the project's component, then a headless primitive, and hand-roll last. Choose styling by ladder: variant, then semantic token, then new token. Don't break what users have learned. Record new decisions with concrete values. → [visual-system.md](visual-system.md)
5. **Apply the patterns.** Load the matching reference:
   - forms, actions, navigation, feedback, tables, search, onboarding and settings → [patterns.md](patterns.md)
   - touch, responsive layout, platform primitives, performance and keyboard → [platform.md](platform.md)
   - words → [content.md](content.md)
   - assistants, generated content and agent actions → [ai-features.md](ai-features.md)

   Where sources disagree (required marking, validation timing), choose by context and record why.
6. **Hold the floors.** WCAG 2.2 AA, with focus management and the keyboard-only gate: complete each top task by keyboard, error recovery included. The deceptive-pattern floor: symmetry, equal weight, no pre-ticked consent, no fake urgency, no confirmshaming, AI disclosure. Decline a deceptive element, name it, and still deliver the rest with an honest alternative. → [accessibility.md](accessibility.md), [deceptive-patterns.md](deceptive-patterns.md)
7. **Evaluate before claiming.**
   - Run `python3 scripts/ui_scan.py <src>`.
   - Render the risky states.
   - Run three or more independent heuristic passes in fresh subagents, each given only screenshots, state labels and the job story.
   - Run a cognitive walkthrough on new flows and KLM on frequent tasks.
   - Keep a finding only with a rule, proof and one correction, and only if it survives a falsification pass. Rank by task impact (P0–P3), cap the list, and say what held up.

   → [evaluation.md](evaluation.md), [validation.md](validation.md#findings-that-hold-up)
8. **Exercise and report.** Build a QA inventory (tasks, controls, states, visible claims). Sign off only with real input through the final-build matrix. Report environment, a coverage table, findings, defect classes checked and not found, named gaps, and the validation status block. Never claim user validation you don't have. → [validation.md](validation.md)
9. **Retain.** Keep the evidence ledger, task model, state matrix, validation status and a test kit for humans next to the code in the repository's docs convention. Durable decisions go into an ADR (`adr-writer`). Add the instrumentation that would show whether the change worked. Designing does not authorize merging or releasing; follow the repository's process.

## Gotchas

- **Familiar beats novel in tools.** Distinctiveness belongs on entry points and marketing pages, not on controls used daily. If the save button looks different in two places, one is wrong.
- **Four defaults generated UIs get wrong:** placeholder labels, a disabled submit button, toasts for important outcomes, and "Are you sure?" where undo belongs.
- **Confirmations and approval prompts habituate.** Attention drops after the second exposure, and Claude Code users approve 93 % of permission prompts. Reserve them for the irreversible and make them specific.
- **The AI critic is one fallible evaluator**: about a third of real problems found, roughly 0.6 precision, worse across iterations and inside feedback loops. Use a fresh context, a rubric, grounding and independent passes, and never ask the same reviewer "is it fixed now?".
- **Synthetic users are not evidence.** Use simulated walkthroughs to find candidate problems, never to report preferences, success rates or quotes.
- **Source can't prove usability.** Hierarchy, discoverability and comprehension need rendering, and ideally people.
- **axe-clean is not accessible, and Lighthouse 100 is not conformance.** Automation finds about half the issues.
- **Taste constants conflict across sources** (spacing grid, durations, press scale, touch-target size beyond the WCAG floor). Follow the project's system and keep the standards hard.
- **Nothing here needs React.** Server-rendered stacks get the same rules through native elements.

## Example

[case-orders.md](case-orders.md) walks a constructed orders-table request through the procedure: evidence ledger, task model, states that broke, merged findings with proof and KLM, and the validation status. Use it for the reasoning, not as a layout.
