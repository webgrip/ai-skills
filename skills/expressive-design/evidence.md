# Evidence: truth as material, research as mechanism

Contents: claim ledger · the hero sentence · what the research supports · narrative structures · show, don't tell · reference research · legal floor

## Claim ledger

Every number, quote, logo, badge, benchmark, "live" indicator and maturity word on the page gets a row before it gets a pixel.

| Claim (as worded on page) | Evidence (link, file, run) | Status | Permitted wording | Owner/date |
| --- | --- | --- | --- | --- |
| "Reconciles a month in 4 s" | `bench/README.md`, run 2026-09-14, M2 laptop, public sample | recorded fixture | "4 s on the public sample statement (M2, recorded run)" | … |

- **Status vocabulary:** implemented · planned · experimental · recorded fixture · simulated · supplied (by the requester, unverified) · uncertain. Planned and uncertain claims go in a roadmap voice or stay off the page.
- An accepted architecture is not a finished migration. A deterministic fixture is not a production benchmark. Zero spend in a demo is not a price.
- A comparative number must be "verifiable and representative" (EU 2006/114 art. 4). Link the method, the data, the hardware and the date, and make it reproducible in the way SPEC fair-use and ClickBench are ([SPEC](https://www.spec.org/products/fairuse), [ClickBench](https://github.com/ClickHouse/ClickBench)).
- When evidence is missing, keep designing with an **explicit pending slot** (a labelled placeholder carrying the ledger row id) instead of inventing the artifact.

## The hero sentence

Pair the memorable hook with a plain category line. The hook earns memory and the line earns comprehension.

| Site | Hook | Plain line |
| --- | --- | --- |
| [Zed](https://zed.dev) | "Your last next editor" | "a minimal code editor crafted for speed and collaboration" |
| [Supabase](https://supabase.com) | "Build in a weekend. Scale to millions." | "the Postgres development platform" |
| [Raycast](https://www.raycast.com) | "Your shortcut to everything." | "productivity tools within an extendable launcher" |

Build the plain line from positioning, not taste. Use the shape `X is a [category] for [who] that [unique value versus the real alternative]`. Choose the category as the frame that makes the unique value obvious ([Dunford](https://www.aprildunford.com/post/a-quickstart-guide-to-positioning)). Take the real alternative from the job the visitor is hiring for, which may be a spreadsheet, an intern or doing nothing ([JTBD](https://hbr.org/2016/09/know-your-customers-jobs-to-be-done)). A tagline that does not say what the thing is breeds confusion and mistrust ([NN/g](https://www.nngroup.com/articles/tagline-blues-whats-the-site-about/)).

For a non-product subject (a person, event, project or report), the same pair applies. The plain line states what it is, when, where and for whom.

## What the research supports, and what it doesn't

| Claim | Strength | Use |
| --- | --- | --- |
| Visual appeal is judged in 17–50 ms and is stable ([Lindgaard](https://www.semanticscholar.org/paper/Attention-web-designers:-You-have-50-milliseconds-a-Lindgaard-Fernandes/f9715b117c57d4e7064afe1c1cb95d5bf4cc1831), [Tuch](https://research.google/pubs/the-role-of-visual-complexity-and-prototypicality-regarding-first-impression-of-websites-working-towards-understanding-aesthetic-judgments/)) | Strong, *for appeal ratings only* | The still frame matters. "Users decide to leave in 50 ms" is folklore |
| Low complexity and high prototypicality rate best | Strong | Conventional skeleton, distinctive focal element |
| The first 10–20 s carry the most leaving ([NN/g / Liu](https://www.nngroup.com/articles/how-long-do-users-stay-on-web-pages/)) | Strong | Category line and strongest proof on the first screen |
| 57 % of viewing time above the fold, 74 % in two screens ([NN/g](https://www.nngroup.com/articles/scrolling-and-attention/)) | Strong | People scroll, but the first screen is still prime |
| People scan headings (layer-cake), and F-pattern scanning is a failure mode ([NN/g](https://www.nngroup.com/articles/layer-cake-pattern-scanning/)) | Strong | Information-bearing headings; the page should read as a story from headings alone |
| Auto-advancing carousels hide content and annoy ([NN/g](https://www.nngroup.com/articles/auto-forwarding/)) | Consistent | Reader-controlled stepping |
| Aesthetic-usability effect | Contested ([Tuch 2012](https://researchprofiles.ku.dk/en/publications/is-beautiful-really-usable-toward-understanding-the-relation-betw/)) | No licence to trade usability for looks |
| Distinctive design converts better; hero video converts; interactive demos convert 12 % better | No controlled evidence; vendor data | Argue distinctiveness on memorability and brand, never on promised conversion |

Users cite "design look" most often when judging credibility, and the Stanford guidelines ask for verifiable claims, real people and dated content ([Stanford](https://credibility.stanford.edu/guidelines/index.html)). A credible look plus unverifiable claims is the worst combination.

## Narrative structures

- **Follow one object through cause and consequence.** The same request, document, transaction or part changes state step by step: input → action → output → checks → decision. Bartosz Ciechanowski's [Mechanical Watch](https://ciechanow.ski/mechanical-watch/) builds one object from its parts. Your thesis object should travel the page the same way.
- **Martini glass.** Make the opening author-guided (the claim), then widen into reader exploration (the evidence explorer) ([Segel & Heer](https://www.semanticscholar.org/paper/Narrative-Visualization:-Telling-Stories-with-Data-Segel-Heer/7b2972e2bdd6944338a895c97eecbd12725fdcd8)).
- **Reader-paced.** Scroll or step, never a timer.
- **Predict before reveal.** Ask the reader to guess, then show the consequence ([Distill](https://distill.pub/2020/communicating-with-interactive-articles/)).
- **The message survives zero interaction.** Most readers never touch a tooltip; "assume no one will ever see it" ([Tse, NYT](https://x.com/archietse/status/708323167224406016)). Interaction deepens the message and never gates it.
- **Explorables hold up their end.** A reactive figure sits inside the explanation and lets readers check the author's claims; it is not a bare sandbox ([Bret Victor](https://worrydream.com/ExplorableExplanations/)).

## Show, don't tell: mechanisms worth adapting

| Source | Mechanism | Adapt |
| --- | --- | --- |
| [Vercel product tour](https://vercel.com/blog/designing-the-vercel-virtual-product-tour) | Real UI, self-paced, visible progress, deep link per step; mobile gets tap-through cards and a different goal | Deep-linkable steps; recompose mobile, don't shrink it |
| [Stripe Connect](https://stripe.com/blog/connect-front-end-experience) | CSS 3D metaphors, obviously not screenshots; reduced motion kills decoration; animate only when visible | Metaphor is honest when it can't be mistaken for product UI |
| [Tailwind](https://tailwindcss.com) | Reading the page top to bottom teaches the tool | The page *is* the tutorial |
| [Sentry](https://blog.sentry.io/sentry-has-a-bold-new-look/) | Illustration world becomes the material: buttons lift, inputs sink | Never promise a personality the product lacks |
| [Raycast](https://www.raycast.com) | Interactive keyboard of real UI; named people with a favourite feature | Specific, checkable proof beats logo walls |
| [Supabase launch weeks](https://supabase.com/blog/supabase-how-we-launch) | Ship first, package later; the builders write the posts; maturity labelled | Label beta/GA visibly |
| [Linear](https://linear.app/now/behind-the-latest-design-refresh) | "Don't compete for attention you haven't earned" | Restraint around the one loud moment |

Label every demonstration as recorded, sample or simulated *beside* it, not in a footnote. A dashboard of plausible numbers whose provenance a visitor can't determine is exactly the ambiguity to avoid.

## Reference research

- **Fixation is the main risk.** Designers shown one example reproduce its features even after its flaws are pointed out ([Jansson & Smith](https://www.researchgate.net/publication/222490596_Design_and_Other_Types_of_Fixation)). So collect from many sources, including outside the category: physical products, editorial design, events, signage, instruments, packaging.
- **Mechanism cards, not mood boards of screenshots.** Fill one row per reference and keep 6–12 cards, not an unbounded list.

  | Reference (URL, date seen) | Observed mechanism | Why it fits this subject | Adapt | Do not borrow |
  | --- | --- | --- | --- | --- |

  Separate the observed from the inferred. Visual preference is not evidence of impact. Inspect rendered pages when drawing visual conclusions, because a fetched summary cannot see layout.
- **Diverge in parallel.** Designers who made several directions in parallel before feedback produced better and more varied work than serial iterators ([Dow et al.](https://dl.acm.org/doi/10.1145/1879831.1879836)). People shown one design rate it higher and criticize it less than when they see it among alternatives ([Tohidi, Buxton et al.](https://www.microsoft.com/en-us/research/publication/getting-the-design-right-and-the-right-design-testing-many-is-better-than-one/)). Always show directions side by side.
- **Frame early work as concept cars.** Labelling exploratory work as a concept lowers defensiveness ([Linear](https://linear.app/now/a-design-reset)).
- **Record rationale as QOC.** Write Question → Options → Criteria → choice, because the artifact alone does not preserve the thinking ([MacLean et al.](https://europe.naverlabs.com/history/past-research/design-space-analysis/)).

## Legal floor

These rules block publishing, not just good taste.

- **EU UCPD Annex I** blacklists false "only for a limited time" urgency (item 7). The Omnibus amendments add unverified "from real customers" review claims (23b) and fake or commissioned reviews and endorsements (23c) ([UCPD](https://eur-lex.europa.eu/LexUriServ/LexUriServ.do?uri=OJ%3AL%3A2005%3A149%3A0022%3A0039%3Aen%3APDF), [Omnibus summary](https://www.makeinfluence.com/en/academy/fake-and-manipulated-reviews-what-the-eu-omnibus-directive-bans)).
- **EU 2024/825 (green transition)** has applied since 27 September 2026. It bans generic "eco-friendly"/"green" claims without proven performance, offset-based "climate neutral" product claims, and self-made sustainability labels ([Freshfields](https://www.freshfields.com/en/our-thinking/blogs/sustainability/empco-goes-live-what-businesses-need-to-know-as-the-new-rules-take-effect-102o3sq)).
- **EU 2006/114** covers comparative claims: objective, verifiable, representative.
- **DSA art. 25** forbids deceptive interface design on platforms. Product sites fall mostly under the UCPD instead ([DSA 25](https://www.eu-digital-services-act.com/Digital_Services_Act_Article_25.html)).
- **US FTC 16 CFR 465** (since October 2024) bans fake and AI-generated reviews and testimonials, as well as fake social-influence indicators ([FTC](https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials)). Endorsements need disclosed material connections ([16 CFR 255](https://www.federalregister.gov/documents/2023/07/26/2023-14795/guides-concerning-the-use-of-endorsements-and-testimonials-in-advertising)).
- Fabricated activity messages and stock scarcity are a known dark-pattern genre, sold as a service ([Mathur et al.](https://arxiv.org/abs/1907.07032), [deceptive.design](https://www.deceptive.design/book/contents/chapter-17)).
- Use third-party logos and quotes only with permission and a ledger row.

This is a design floor, not legal advice. Escalate real claims to whoever owns legal review.
