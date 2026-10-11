# Measuring demand with audience videos: evidence and a plan

Labels: **PEER** peer-reviewed, **OFF** official/legal text, **DATA** numbers I pulled
myself (n, source), **VENDOR** a vendor's own claim or benchmark, **ANEC** practitioner story, **GAP** no
good evidence found. Every URL below was opened in this session unless marked "(search result only)".

## 1. What the research says about experimenting as a founder

- **F1 PEER — a scientific approach changes decisions, mostly by stopping bad ideas sooner.** Camuffo,
  Cordova, Gambardella & Spina, *Management Science* 2020 (doi 10.1287/mnsc.2018.3249): RCT with
  116 Italian startups, 16 data points over about a year. Both arms got 10 training sessions. The treated arm was
  taught to state hypotheses and test them rigorously. Treated founders "perform better, are more likely to
  pivot … and are not more likely to drop out". Caveat from the paper itself: only 17 of 116 firms earned any
  revenue (9 treated, 8 control), so revenue effects rest on very few firms. Preprint read at
  https://Www.Gwern.net/doc/economics/2019-camuffo.pdf (Articles-in-Advance version).
- **F2 PEER — replication at scale: more termination, fewer random pivots.** Camuffo et al., *Strategic
  Management Journal* 45(6) 2024, doi 10.1002/smj.3580: 759 firms, four RCTs. The approach raised idea
  termination and had a non-linear effect on radical pivots (treated firms made few, rather than none or many).
  https://openaccess.city.ac.uk/id/eprint/32437. **Implication:** the value is pre-committed kill criteria,
  not more experiments.
- **F3 PEER — A/B-testing startups learn faster and fail faster.** Koning, Hasan & Chatterji, *Management
  Science* 68(9) 2022, doi 10.1287/mnsc.2021.4209 (NBER w26278): few startups adopt A/B testing; adopters
  improve page views and ship more features; outcomes get more extreme (young firms fail faster, older ones
  scale). Search summary reports 30–100 % performance gains after a year. https://www.nber.org/papers/w26278.
  Caveat: observational (staggered adoption), not randomized; the sample is web firms with traffic.
- **F4 PEER — experimentation is costly and investors decide early.** Kerr, Nanda & Rhodes-Kropf, *Journal of
  Economic Perspectives* 28(3) 2014: success odds are "low, extremely skewed, and unknowable until an investment
  is made"; the cost of experimenting shapes what gets tried. https://www.nber.org/papers/w20358. For a founder with
  little time, the cheapest test that can change a decision wins.

## 2. Stated versus revealed preference

- **F5 PEER — hypothetical answers overstate real payment, less than folklore says.** Murphy, Allen, Stevens &
  Weatherhead, *Environmental & Resource Economics* 30(3) 2005: 28 studies, 83 observations; median
  hypothetical/actual ratio **1.35**, strongly right-skewed (some studies far higher); choice-based elicitation
  reduces the bias. https://ideas.repec.org/a/kap/enreec/v30y2005i3p313-325.html. Domain is mostly
  environmental goods, not B2B software, so treat the number as direction, not calibration.
- **F6 GAP — purchase intent → purchase for B2B dev tools.** Morwitz, Steckel & Gupta, *Int. J. Forecasting*
  23(3) 2007 "When do purchase intentions predict sales?" exists (ideas.repec record, no abstract;
  https://ideas.repec.org/a/eee/intfor/v23y2007i3p347-364.html) but I could not read its findings. I found no
  peer-reviewed waitlist-to-paid or waitlist-to-activation rate for developer tools. Any number you see quoted
  for that is unsourced; build your own baseline.
- **F7 ANEC/VENDOR — the "very disappointed" test.** First Round Review on Superhuman
  (https://review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit/): Ellis' rule is
  that companies that struggled "almost always had less than 40 % of users respond 'very disappointed'";
  Superhuman went from 22 % to 58 % in three quarters; directionally useful from about **40 respondents**;
  survey people who "used the product at least twice in the last two weeks". It is a practitioner heuristic
  from Ellis' own benchmarking (sample never published), not peer-reviewed, and it **needs real users** — it
  cannot measure pre-launch demand.
- **F8 OFF/ANEC — Van Westendorp.** Four price questions (too cheap / bargain / getting expensive / too
  expensive), plotted as cumulative curves; gives an acceptable price range, **not a demand curve** unless you add
  the Newton–Miller–Smith purchase-likelihood questions. https://en.wikipedia.org/wiki/Van_Westendorp%27s_Price_Sensitivity_Meter.
  Stated-preference, so F5 applies. Gabor-Granger and conjoint: **GAP** in this pass (no source opened);
  conjoint needs hundreds of respondents, which you will not have from five audience videos.

## 3. Benchmarks you can compare against (and why they mostly don't fit)

- **F9 VENDOR — landing-page conversion.** Unbounce 2024 Conversion Benchmark Report, SaaS: median **3.8 %**
  (all industries 6.6 %); data & infrastructure pages **3.3 %**; email traffic converts at a 16.9 % median,
  paid social 2.9 %; 79 % of SaaS landing visits are mobile; plain copy (5th–7th grade) 12.9 % vs professional
  copy 2.1 %. https://unbounce.com/conversion-benchmark-report/saas-conversion-rate/. "Conversion" mixes demo
  requests, trials and downloads, from paid traffic; YouTube organic traffic is not a row. Use as a sanity
  floor only.
- **F10 VENDOR — cold-email replies.** Belkins 2025 report on 16.5 M cold emails (with Reply.io, Expandi, Nooks);
  page gives no rate or reply definition. https://belkins.io/resources/b2b-cold-outreach-benchmarks-2025-report.
  Secondary summaries (search result only) quote 5.8 % (2024) and 3–6 % "good". Reply ≠ positive reply ≠ call.
- **F11 GAP — waitlist → activation, calls booked per signup, LOI rates for dev tools.** No credible source found.

## 4. Market-level signals (context, not demand for *you*)

- **F12 DATA — HN vocabulary, stories since 2025-10-01** (HN Algolia API, queried 2026-10-11, exact-phrase
  unless noted): "coding agents" **2,271**; "agentic engineering" **128** (top: "Agentic Engineering Patterns",
  543 pts); "AI code review" **105** (top: "There is an AI code review bubble", 351 pts); "background agents" 33;
  "self-hosted coding agent" **0**; "Devin alternative" **0**. Unquoted "self-hosted agent" 354 (top: "Building an
  (almost) fully self-hosted, sandboxed, agentic software factory", 119 pts); "Show HN agents kubernetes" 88
  (top: "Klaw.sh – Kubernetes for AI agents", 60 pts). Reading: people say *coding agents* and *agentic
  engineering*; nobody searches by your category name; "AI code review" carries a scepticism thread.
- **F13 GAP — Google Trends / keyword volume.** trends.google.com returned HTTP 429 to me; no keyword-volume
  tool opened. Owner can check Trends by hand (NL + worldwide, 5 y) for the F12 terms; record screenshots.
- **F14 DATA — comparable OSS stars** (`gh api`, 2026-10-11): OpenHands 90,558; Aider 49,467;
  anomalyco/opencode (was sst/opencode) 212,647; Cline 70,154; Continue 36,180; SWE-agent 20,521;
  openai/codex 128,617; anthropics/claude-code 150,133; gemini-cli 107,282. Proves the *category* has
  attention, not that self-hosted team orchestration does.
- **F15 PEER(preprint) — stars are gameable.** He et al., arXiv 2412.13459: StarScout found ~4.5 M suspected fake
  stars (3.1 M after filtering) across GitHub 2019–2024, surging in 2024; fake stars boost for under two
  months. https://arxiv.org/abs/2412.13459. Don't use stars as your own success metric.
- **F16 VENDOR/press — money is flowing in.** Cognition raised $400 M at $10.2 B post-money (2025-09-08); Devin
  ARR ~$1 M (Sep 2024) → $73 M (Jun 2025), roughly doubled after the Windsurf acquisition.
  https://www.maginative.com/article/cognition-ai-raises-400-million-at-a-10-2-billion-valuation/. Company-reported
  figures. Evidence the *category* sells; says nothing about self-hosted buyers or agencies.

## 5. Platform constraint that shapes the design

- **F17 ANEC/press — Shorts links aren't clickable.** Since 31 Aug 2023 links in Shorts descriptions and
  comments are not clickable (creator and commenter); YouTube offered channel-header links and a
  Shorts-to-long-form link. https://tubefilter.com/2023/08/10/youtube-shorts-comments-spam/. So a Short cannot
  carry a per-audience UTM link. Per-audience attribution must come from (a) a spoken/on-screen vanity path
  (`example.com/lead`), (b) the related long video's description link, or (c) a "how did you hear" field.

## 6. EU / NL ethics and law

- **F18 OFF — tracking links fall under ePrivacy Art. 5(3).** EDPB Guidelines 2/2023 v2.0 (adopted 2024-10-07),
  §3.1 paras 49–51: an identifier appended to a URL "not relevant in terms of resource identification" is a
  tracking link; distributing it "does constitute storage", collecting it is "gaining access", so Art. 5(3)
  applies; para 56: applicability "does not systematically mean that consent needs to be collected" (exemptions
  are out of the guidelines' scope). §3.3: IP-only tracking can also fall under it.
  https://edpb.europa.eu/system/files/2024-10/edpb_guidelines_202302_technical_scope_art_53_eprivacydirective_v2_en_0.pdf.
  **My reading (not legal advice):** campaign-level UTMs (same string for everyone who watches a video) are
  weaker than per-person IDs but the text does not exempt them; vanity *paths* (`/lead`) identify a resource, not a
  visitor, so they are the cleanest option.
- **F19 VENDOR — cookieless analytics.** Plausible: no cookies, a random daily-reset identifier, "built and hosted
  in the EU", claims no banner needed under GDPR "in most" regimes. https://plausible.io/cookieless-web-analytics.
  Vendor's own legal reading; Dutch AP guidance on the analytics exemption (search result only) requires
  minimal privacy impact and a processor agreement. Self-hosting Plausible/Umami on your cluster keeps data
  in-house.
- **F20 OFF — waitlist email consent.** ACM (NL regulator for spam): commercial email only with prior,
  deliberate consent (no pre-ticked box), clearly about promotional messages; **keep proof of consent for 5
  years**; sender identifiable; free one-click unsubscribe in every mail; existing-customer exception only for
  related products. https://www.acm.nl/nl/onderwerpen/telecommunicatie/internet/spam. GDPR Art. 7: be able to
  demonstrate consent; withdrawing "as easy … as to give". https://gdpr-info.eu/art-7-gdpr/. A waitlist
  signup where the person asks to be told about access is consent for *that*; a newsletter needs its own box.
- **F21 OFF — fake doors and misleading advertising.** Directive 2006/114/EC (B2B misleading advertising) Art.
  2(b): advertising "which in any way, including its presentation, deceives or is likely to deceive" and is
  likely to affect economic behaviour. https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32006L0114. A
  fake door that implies the hosted service exists, or takes money for it, risks this; one that says
  "planned — join to get it first" does not deceive. **GAP:** no peer-reviewed study on fake-door effects on
  trust; industry guidance (ProdPad, search result only) says disclose immediately after the click.
- **F22 OFF — pre-registration can stay private.** AsPredicted keeps a pre-registration private until an author
  publishes it; once public it cannot be changed and is archived. https://aspredicted.org/. Fine for a founder
  who doesn't want strategy public (a dated private git commit also works).

## 7. Statistics for small numbers

- **F23 ANEC/expert — don't peek.** Evan Miller: stopping when it "looks significant" raised false positives
  to 26.1 % for a no-effect change; rule of thumb per arm n = 16 σ²/δ², σ² = p(1−p); fixing n in advance
  "completely mitigates" it. https://www.evanmiller.org/how-not-to-run-an-ab-test.html.
- **F24 DATA (computed, Wilson 95 % interval):** 5/100 signups → 2.2–11.2 %; 15/300 → 3.1–8.1 %; 30/600 →
  3.5–7.0 %; 8/40 → 10.5–34.8 %; 16/40 → 26.3–55.4 %. A/B per arm: baseline 4 %, detect +2 pp → **1,536**;
  detect +4 pp → 384; baseline 10 %, +5 pp → 576. **Implication:** you cannot A/B landing variants at your
  traffic. Compare audiences against a pre-set *threshold*, and treat differences under ~2× as noise.

## Decisions — demand-measurement plan driven by the videos

**D1. Measure behaviour on a ladder, not opinions** (F1, F2, F5, F6). Each rung costs the visitor more:
`view → visit (vanity path) → early-access signup (+1 qualifying question) → call booked → design-partner
LOI or paid pilot`. Views, likes, stars and HN points are context only (F14, F15).

**D2. One vanity path per audience, spoken and on screen** (F17, F18): for example `/dev`, `/lead`,
`/founder`, `/biz`, `/exec`. Each path serves the same page structure with that audience's pain and promise
in the hero (message test). Long-form descriptions link the same path. Signup form adds "Where did you see
us?" as a cross-check. No per-person IDs in links.

**D3. Cookieless, self-hosted analytics; consent only at signup** (F18–F20): Plausible/Umami on your cluster,
pageviews + one `signup` and one `call_booked` goal. Signup form: explicit unticked box for "email me
when access opens", separate optional box for updates, double opt-in, consent log retained 5 years, one-click
unsubscribe. State on the page that features that do not exist yet are **planned** (F21).

**D4. Pre-register before the first video ships** (F1, F2, F22, F23): a dated, private file (AsPredicted or a
commit) holding the table below, the measurement window (6 weeks per video, fixed), and the rule "no threshold
edits after launch; new ideas go into the next round". Proposed thresholds are **founder priors, not benchmarks**
(F9–F11 are the only external anchors and they don't match organic video traffic).

| Audience | Hypothesis (pain → promise) | Primary metric | Continue if (after ≥300 visits or 6 wk) | Kill / rework if |
|---|---|---|---|---|
| Developers | <their pain> → <the promise> | visit→signup | e.g. signup ≥ 5 % *and* lower Wilson bound ≥ 3 % (F24, F9) | e.g. < 2 % → rework the message once, then drop the angle |
| Buyers who decide | <their pain> → <the promise> | signup→call booked | e.g. ≥ 3 calls from the first 30 qualified signups | 0 calls from 30 → this audience is not the buyer |
| Partners or resellers | <their pain> → <the promise> | calls + written LOIs | e.g. ≥ 2 LOIs (named person, price range, start date) in 12 weeks | 0 LOIs after ≥ 8 calls → do not build for them yet |

The numbers are examples of founder priors; set your own before launch.

**D5. Pricing only after calls, with choice-based questions** (F5, F8): on calls, ask Van Westendorp's four
questions plus "would you sign a pilot at €X now?" (a choice, which F5 says reduces bias). Record the
answer, then count who actually signs. Skip conjoint/Gabor-Granger (sample too small).

**D6. Sean Ellis survey only for pilot users** (F7): once ≥ 10 teams have used the product at least twice in two
weeks; read it as directional below 40 responses; target ≥ 40 % "very disappointed" within the best segment.

**D7. Guards against fooling yourself** (F1–F3, F23, F24): fixed window per video, no peeking-based stops;
count only *qualified* signups (answered the qualifying question, not a friend/colleague, not a bot); log
every confounder (a Show HN post, a newsletter mention) in the sheet with its date; compare audiences only when
the gap is ≥ 2× and both intervals don't overlap; one reviewer outside your head (a co-founder or a peer) reads the
result before you act on it.

**D8. Market context, refresh quarterly, never as a go signal** (F12–F16): HN counts for the F12 terms,
Trends screenshots (F13), stars for the F14 list, notable funding. Use the words people use ("coding agents",
"agentic engineering") in titles; avoid leading with "AI code review" (scepticism thread).

## Tracking sheet — one row per video × week

`week_start` · `video_id` · `audience` · `format` (short/long) · `hook_variant` · `pain_promise` · `vanity_path`
· `publish_date` · `platform` · `views` · `avg_view_duration_s` · `ctr_impressions_%` · `visits` (analytics,
path) · `signups` · `qualified_signups` · `self_reported_source` · `k8s_yes` · `team_size_bucket` ·
`calls_booked` · `calls_held` · `buyer_role_on_call` · `vw_too_cheap/bargain/expensive/too_expensive` (median, €) ·
`pilot_asked` · `loi_signed` · `loi_value_€` (nl-NL, 2 decimals) · `signup_rate_%` · `wilson_low_%` ·
`wilson_high_%` · `threshold` (from pre-reg) · `verdict` (continue/rework/kill/pending) · `confounders`
(dated free text) · `hours_spent` · `notes`.

Plus a separate **consent log** (email, timestamp, form version, boxes ticked, double-opt-in confirmed at,
unsubscribed at), kept 5 years (F20), stored apart from the analytics sheet.
