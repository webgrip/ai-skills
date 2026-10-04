# Generic tells: the template look and how to leave it

Generated and template-built pages converge on a narrow set of designs. Safe choices dominate web training data, so a model drifts toward them unless something pulls it away ([Anthropic](https://claude.com/blog/improving-frontend-design-through-skills)). One measured study of 73 sites built with a single AI builder found the inputs spread across about 21 business domains, but the outputs collapsed to 6–12 effective designs. The builders' sense of authorship barely tracked measured originality ([arXiv 2609.38183](https://arxiv.org/html/2609.38183); one tool, a student sample). Treat the list below as a set of defaults to consciously accept or replace, not a list of things that are always wrong.

## The method that beats the list

1. Before writing code, write a **token plan**: 4–6 named colors with their roles, type roles, an ASCII sketch of the hero and flatplan, and three principles.
2. Write the **default answer** you would give any similar prompt. Diff the plan against it. Every match must survive a "why this, for this subject?" question.
3. Derive replacements from the **subject's own world**: its material, artifacts, industry vernacular, hardware and history. Never derive them from an anti-slop list. Avoiding a list just produces a second-order template.

## Catalog

| Tell | Why it reads generic | Replace with |
| --- | --- | --- |
| Indigo/violet-to-blue gradient on white | The Tailwind UI `indigo-500` default became every generated UI's color ([Wathan](https://x.com/adamwathan/status/1953510802159219096)) | One accent taken from the subject's world |
| Inter/Roboto/system sans at one weight | No voice; display and body indistinguishable | A display face with real weight and size contrast, or a neutral face given true display treatment |
| Centered hero, three icon cards, CTA, repeat | Identical density in every chapter; no focal object | An asymmetric hero built on the thesis object; a flatplan with alternating states |
| Big number + small label stat row as the hero | Borrowed authority; usually not the story | Use only when the number *is* the claim, with a claim-ledger row |
| Identical rounded cards, one radius, `rgba(0,0,0,.1)` shadow | A card kit, not a composition | Vary containers by hierarchy; let content sit directly on the ground |
| ALL-CAPS eyebrow over every heading, "→" on every link, `01/02/03` on non-sequences | Structure that encodes nothing | Markers only where they carry information |
| One word in the headline set in italic, color or gradient | Leans on the headline instead of composing it | Let scale and the face carry it |
| Fade-and-slide-up on every section, hover lift on every card | Motion as texture, not explanation | One orchestrated moment tied to the thesis; motion that answers an action |
| Frosted glass on every surface | Contrast breaks per background ([NN/g](https://www.nngroup.com/articles/glassmorphism/)) and it costs paint | Solid surfaces; translucency only over a controlled ground |
| Equal-tile bento grid | Bento only *expresses* priority that already exists ([deck.gallery](https://www.deck.gallery/blog/apple-bento-grid-decks-roundup/)) | Unequal tiles sized by importance, with one dominant fact |
| Floating 3D blobs, mesh gradients, abstract hero render | Stands in for the absent product | The real artifact, or a material metaphor derived from it |
| Emoji as feature icons | Placeholder iconography | The subject's own marks, diagrams or none |
| Visible blueprint grid with mono labels | Vercel's honest engineering voice, now widely copied | Use it only if the subject is literally about structure |
| **Second-order:** cream paper, serif and terracotta; near-black with acid green; hairline broadsheet with zero radius | Yesterday's escape from the template is today's template | Whatever the subject's material dictates, even if it is "plain" |
| `#0B0B0B`/`#111` standing in for black in a dark mode | A default, not a decision | An inverted ramp from the page's own neutral |
| Stock testimonials, "trusted by thousands", logos without permission | Unverifiable; often unlawful (see [evidence.md](evidence.md)) | Named, sourced proof, or none |

Most of these leave a mark in the source. `scripts/design_scan.py` flags them; the rule names are in [validation.md](validation.md). A scan finding is a prompt to justify the choice, not a verdict.

## Where neutral is right

Documentation, dense tools and forms gain from prototypical structure. Expressiveness belongs in their *entry points* (landing, onboarding, empty states, release pages) and in one signature detail, not in every control. Linear's identity comes from subtraction, alignment and density "felt after a few minutes", not from spectacle ([Linear](https://linear.app/now/how-we-redesigned-the-linear-ui)).
