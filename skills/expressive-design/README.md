# expressive-design

Designs, critiques and builds distinctive, memorable web pages from the subject's own evidence, not from a template. It covers landing, product, launch, campaign, portfolio, event, docs-entry and open-source pages, and interactive explainers.

The skill treats "make it pop" as a composition and truth problem first, and an animation problem last:

- **Claim ledger and hero pair.** Every number, quote, logo and "live" indicator traces to evidence, or carries a pending or simulated label. A memorable hook sits beside a plain category line.
- **Thesis object.** One artifact from the subject's own world carries the identity and the evidence, and constrains layout, color, type and motion at once.
- **Parallel directions.** Faithful, amplified and strange directions are critiqued side by side, and the decision is recorded as Question → Options → Criteria → choice.
- **Still composition first.** A flatness ladder, a magazine-style flatplan, a template diff, and screenshot critique tests (blur, grayscale, thumbnail, logo swap, 5-second).
- **Motion contract.** Each effect gets purpose, trigger, end state, interruption, single selection state, alternatives and controls. Motion is reduced, not removed, with October 2026 Baseline status for scroll-driven animations, view transitions and friends.
- **Validation.** A WCAG 2.2 floor, Core Web Vitals, regression traps from shipped work, and an honest reporting format.
- **`scripts/design_scan.py`.** A dependency-free source scanner covering 23 rules: missing reduced-motion branches, removed focus rings, blocked zoom, vw-only type, layout-thrashing keyframes, unsized images, scroll hijacking, the generic template look, and fabricated proof or live activity.

## Install

```text
/plugin install expressive-design@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s expressive-design`.

## Example prompts

- "Our homepage is clean but forgettable. Make it pop."
- "Turn this annual report into an interactive scroll story."
- "Review the motion on this landing page before we ship."
- "Does this look AI-generated? Make it feel like ours."

## Scanner

```bash
python3 skills/expressive-design/scripts/design_scan.py path/to/src
python3 skills/expressive-design/scripts/design_scan.py --json --fail-on warn path/to/src
```

Exit status 1 when a finding at or above `--fail-on` (default `fail`) exists. `test.sh` runs it against `fixtures/template` (every rule must fire) and `fixtures/disciplined` (nothing may fire).

## Sources

Every rule in the reference files links its source: W3C WCAG 2.2 Understanding documents, web.dev and the web-features explorer, NN/g, Tuch et al. and Lindgaard et al. on first impressions, Dow et al. and Tohidi et al. on parallel design, Jansson and Smith on fixation, Segel and Heer on narrative visualization, EU UCPD/Omnibus and 2024/825, and FTC 16 CFR 465.
