# product-ux

Designs, critiques and builds product interfaces that people use repeatedly: apps, dashboards, admin tables, forms, settings, onboarding and AI features. It is the sibling of `expressive-design`, which covers pages that need to look distinctive. Here the goal is the opposite: a task that is fast, safe and obvious for the person doing it for the two-hundredth time.

What it does that the popular UI skills don't:

- **Evidence before pixels.** An evidence ledger built from tickets, analytics, code and existing screens; job stories tagged with their source; a proxy top-task ranking labelled as a proxy; an assumptions map. It never invents personas or user numbers.
- **A task model.** Frequency × cost of error decides the stance: speed for frequent tasks, safety for costly ones, both for frequent and costly.
- **Flows and a state matrix before screens.** Entry, exit and interruption per flow; first use, no results, one, huge, partial, error, offline, no permission, read-only, conflict; a statechart for interacting booleans; a worst-case data fixture built from the real schema.
- **Evidence-tiered rules.** Over 250 sourced rules for forms, actions, navigation, feedback, tables, search, onboarding, settings, touch, platform primitives (October 2026 Baseline), content and AI features. Each is marked standard, empirical or convention, and conflicts between sources are written out.
- **The existing system is the authority.** Ladders for controls and styling, the DTCG 2025.10 token format, component state matrices, and brownfield respect for what users have learned.
- **Floors.** WCAG 2.2 AA with focus management and a keyboard-only gate, the European Accessibility Act status, and a deceptive-pattern floor covering consent, the EU withdrawal button, confirmshaming and AI Act article 50 disclosure.
- **Honest evaluation.**
  - A scorecard of the "laws of UX": Miller, Hick, Doherty and Zeigarnik are corrected.
  - Expert methods: heuristic evaluation, cognitive walkthrough and KLM.
  - A critic protocol built on the published accuracy of LLM evaluators: fresh context, a rubric, grounding, independent passes.
  - No synthetic users as evidence.
  - A validation status block on every deliverable.
- **`scripts/ui_scan.py`.** A dependency-free source scanner with 34 rules. It covers:
  - unlabelled and placeholder-labelled fields
  - clickable divs and unnamed icon buttons
  - blocked paste and zoom
  - pre-ticked consent and confirmshaming
  - disabled submit buttons
  - vague error copy and hand-built date and money formats
  - silent toasts
  - iOS input zoom and small targets

## Install

```text
/plugin install product-ux@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s product-ux`.

## Example prompts

- "Support agents say the orders table is slow to work with. What should change?"
- "Build the account settings area: profile, password, delete account."
- "Review this signup form before we ship."
- "Add an AI suggested reply to the support inbox."
- "Our PM wants the sidebar cut to 7 items because of Miller's law."

## Scanner

```bash
python3 skills/product-ux/scripts/ui_scan.py path/to/src
python3 skills/product-ux/scripts/ui_scan.py --json --fail-on warn path/to/src
```

Exit status 1 when a finding at or above `--fail-on` (default `fail`) exists. It judges native lowercase elements only and assumes a capitalised component owns its semantics, so scan the component library too. `test.sh` runs it against `fixtures/careless` (every rule must fire) and `fixtures/careful` (nothing may fire), and checks every rule is documented in `validation.md`.

## Sources

Each rule links its source:

- **Standards and design systems:** W3C WCAG 2.2 Understanding documents and the WAI-ARIA Authoring Practices; NIST SP 800-63B-4; GOV.UK Design System; the web-features Baseline data; Apple, Material and Fluent guidelines.
- **Research and audits:** Baymard and NN/g research; peer-reviewed HCI from Fitts and Card, Moran and Newell to Hertzum and Jacobsen, Liu et al. on Hick's law, and Ghibellini and Meier on Zeigarnik.
- **AI evaluators and synthetic users:** Duan et al., UICrit, UX-LLM and Kuric et al.
- **AI features:** Microsoft HAX, PAIR, Apple's generative AI guidelines and Microsoft's overreliance framework.
- **EU law:** EDPB, the DSA, the UCPD, Directive 2023/2673 and AI Act article 50.
- **Market survey:** the popular UI skills reviewed for this one (Anthropic frontend-design, Vercel web interface guidelines, impeccable, ui-ux-pro-max, Emil Kowalski's skills, ibelick's ui-skills, OpenAI's playwright-interactive), with what was borrowed credited inline.
