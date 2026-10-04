# Deceptive patterns and the legal floor

These rules block shipping, not just good taste. The evidence that deceptive patterns are common is strong: the Commission's 2022 behavioural study found 97 % of popular EU sites and apps used at least one, and fake activity messages are sold as a service ([Mathur et al.](https://arxiv.org/abs/1907.07032)). This page is a design floor, not legal advice; escalate real decisions to whoever owns legal review.

Contents: the floor · taxonomy · consent · cancellation and withdrawal · pricing and urgency · data and settings · when asked to build one

## The floor

1. **Symmetry.** Declining, cancelling, withdrawing or unsubscribing takes no more effort than accepting or signing up, in the same channel (GDPR art. 7(3); DSA art. 25(3)(c); CRD art. 11a).
2. **Equal weight for opposing choices** in consent and consequential decisions: same layer, same size and style class, neutral labels.
3. **No pre-ticked boxes** for consent or paid add-ons (GDPR recital 32; CJEU *Planet49* C-673/17; CRD art. 22).
4. **No nagging** after a choice is made (DSA art. 25(3)(b)).
5. **No fake urgency, scarcity, activity or social proof.** Timers, stock counts and "people viewing" are real or absent (UCPD Annex I).
6. **Full price up front**, mandatory fees included.
7. **No confirmshaming.** Decline options are labelled neutrally ("No thanks"), never "No, I don't want to save money".
8. **AI disclosure** at first interaction ([ai-features.md](ai-features.md#disclosure)).
9. **Accessible floor** for consumer services ([accessibility.md](accessibility.md)).

`scripts/ui_scan.py` flags pre-ticked consent, confirmshaming copy and fake-activity tells; the rest needs judgement.

## Taxonomy

The EDPB groups deceptive patterns into six families ([EDPB Guidelines 03/2022](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-032022-deceptive-design-patterns-social-media_en)). Written for social media, it works as a checklist for any consent, settings, deletion or data-access UI.

| Family | Looks like |
| --- | --- |
| Overloading | Repeated prompts, a privacy maze, too many options to find the real one |
| Skipping | Privacy-invasive defaults, distraction from the important choice |
| Stirring | Emotional steering, guilt, the important option hidden in plain sight |
| Obstructing | Dead ends, flows longer than necessary, misleading action labels |
| Fickle | Inconsistent interface, no clear hierarchy, language switching mid-flow |
| Left in the dark | Conflicting information, ambiguous wording |

The academic ontology unifies these with the Brignull, Mathur and Gray taxonomies ([Gray et al., CHI 2024](https://dl.acm.org/doi/10.1145/3613904.3642436)).

## Consent

From the EDPB cookie-banner taskforce ([report](https://www.edpb.europa.eu/system/files/2023-01/edpb_20230118_report_cookie_banner_taskforce_en.pdf)):

- A reject option sits on **the same layer** as the accept button (often summarised as "on the first layer").
- No pre-ticked purposes; no reject link buried in text or outside the banner.
- A reject button whose contrast makes it unreadable is manifestly misleading.
- Withdrawal is available at any time from a persistent, standard place, and as easy as consenting.
- No tracking before consent; "essential" means essential.

## Cancellation and withdrawal

- **EU withdrawal button**, applying since 19 June 2026 (Directive 2023/2673, new art. 11a of the Consumer Rights Directive): for contracts concluded online, a continuously available, prominent function labelled "withdraw from contract here" (or equally unambiguous), then a confirmation step labelled "confirm withdrawal", then an acknowledgement on a durable medium such as email. No mandatory reason field ([EUR-Lex](https://eur-lex.europa.eu/eli/dir/2023/2673/oj)). This covers the 14-day withdrawal right; general subscription cancellation is the subject of the coming Digital Fairness Act (proposal expected Q4 2026, not law yet, [Legislative Train](https://www.europarl.europa.eu/legislative-train/theme-protecting-our-democracy-upholding-our-values/file-digital-fairness-act)).
- **US:** the FTC click-to-cancel rule was vacated by the 8th Circuit on 8 July 2025 and rulemaking restarted in 2026; ROSCA and state auto-renewal laws still apply ([Cooley](https://www.cooley.com/news/insight/2025/2025-07-11-click-to-cancel-just-got-cancelled-eighth-circuit-vacates-entirety-of-ftcs-negative-option-rule)).
- **Design floor regardless of jurisdiction:** cancel is findable from account settings in the obvious place and completes online; at most one skippable retention offer (a pause or a discount); an optional, skippable survey; a confirmation screen and email receipt; no forced call or chat.

## Pricing and urgency

- Under the UCPD Annex I blacklist, false limited-time claims are banned outright. Omnibus additions cover unverified "real customer" review claims and fake endorsements; US FTC 16 CFR 465 bans fake and AI-generated reviews and fake social-influence indicators ([FTC](https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials)).
- The Dutch ACM's online-consumer guidelines expect businesses to test that their choice architecture doesn't mislead: defaults, scarcity claims, pre-ticked add-ons, price presentation ([ACM](https://www.acm.nl/en/publications/guidelines-protection-online-consumer)).
- Countdown timers reflect a real deadline; stock counts are real inventory; "X people are viewing" is real and recent or not shown.

## Data and settings

- **DSA art. 25** forbids interfaces that deceive or manipulate on online platforms, and names prominence of choices, repeated requests and hard termination as examples ([DSA 25](https://www.eu-digital-services-act.com/Digital_Services_Act_Article_25.html)). Product sites fall mostly under the UCPD and GDPR instead, but the three examples are a sound universal floor.
- **Data Act art. 6(2)(a):** data-sharing interfaces must not make choices "unduly difficult", be non-neutral, or coerce, deceive or manipulate ([Data Act art. 6](https://www.eu-data-act.com/Data_Act_Article_6.html)).
- Account deletion and data export are findable in settings, complete online, and state what is deleted and when.

## When asked to build one

Decline the deceptive element, name it and the law or harm in one or two sentences, and still deliver the rest of the task with an honest alternative:

| Requested | Honest alternative |
| --- | --- |
| "Trusted by 10,000+" with no users | A labelled product demonstration, a named beta tester with consent, or the founders' story |
| Countdown that resets | A real deadline, or no timer |
| Hidden cancel link | One skippable offer, a pause option, cancel in settings |
| Confirmshaming decline label | "No thanks" |
| Pre-ticked newsletter box | Unticked box with a clear benefit statement |
| Reject hidden on the second layer | Accept and Reject side by side, same style |
