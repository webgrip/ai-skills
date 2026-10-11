# A/B testing thumbnails and titles on a small channel: evidence and a programme

Labels: **PEER** peer-reviewed, **OFF** official YouTube/Google doc or staff,
**DATA** large-sample correlational, **VENDOR** tool/agency claim, **ANEC** practitioner opinion,
**GAP** no adequate evidence found. Every URL below was opened. Numbers marked "calc" are my own
arithmetic, not the source's.

## 1. YouTube Test & Compare today

- **OFF** You can test titles only, thumbnails only, or title+thumbnail pairs, with **up to 3 variants**.
  The metric is **watch time share**, not CTR. The variant with the most watch time is shown to everyone
  afterwards. https://support.google.com/youtube/answer/13861714
- **OFF** Duration: "a few days" up to **two weeks**. No minimum number of impressions is published; the page
  only says that videos with fewer impressions are less likely to get a clear winner. (same URL)
- **OFF** There are three outcomes. **Winner** means one variant was statistically significantly better on watch time share.
  **Performed same** means you pick any variant. **Inconclusive** means the *first uploaded* variant becomes the default. A small
  control group may see only the default, and that group's data is excluded. (same URL)
- **OFF** Limits: changing the title or thumbnail during a test stops it. Very similar variants run longer or
  end with no winner. If any thumbnail is under 1280x720, every thumbnail in the test is downscaled to 480p. Setup is desktop Studio only, and
  **advanced features** must be enabled. (same URL)
- **OFF** Not eligible: **Shorts**, scheduled live streams, premieres (eligible once they convert to long-form), made-for-kids videos,
  mature-audience and age-restricted videos, and private videos. If a video becomes a Short, its earlier tests disappear. (same URL)
- **OFF (via press)** Title testing reached all creators with advanced features in Dec 2025, as announced on Creator
  Insider. YouTube staff said the winner is decided on watch time because "we want to ensure that your A/B test experiment gets
  the highest viewer engagement". SEJ describes the metric as watch time per impression.
  https://www.searchenginejournal.com/youtube-title-a-b-testing-rolls-out-globally-to-creators/562571/
- **OFF** An impression counts only when a thumbnail is shown for >1 s with ≥50% of it visible. Impressions from external sites, the mobile web,
  end screens/cards and notifications are not counted. https://support.google.com/youtube/answer/9314486
- **OFF** "Half of all channels and videos" have an impressions CTR **between 2% and 10%**. CTR naturally falls as impressions
  grow, for example from the Home page. Videos under a week old or with <100 views swing more widely. Avoid clickbait: "Clickbait videos tend to
  have low average view duration and therefore are less likely to get recommended." https://support.google.com/youtube/answer/7628154
- **OFF** The recommender has used watch time since 2012 because "clicking on a video doesn't mean you actually watched it".
  It also weighs survey-based **valued watchtime** (only 4–5 star ratings count), likes, dislikes and shares.
  https://blog.youtube/inside-youtube/on-youtubes-recommendation-system/
- **GAP** YouTube does not publish its test statistic, its alpha, how it handles sequential looks, or the size of the control group.
  Treat "Winner" as a black-box decision, and log the per-variant watch time shares yourself.

## 2. Statistics for a small channel

**Worked sample sizes** (calc). Two-sided α=0.05, power 0.80, equal split, two-proportion z-test.
"Per arm" counts the impressions each variant needs. With 3 arms, multiply by 3, and add about 20% if you correct for 2 comparisons.

| Baseline CTR → variant | Relative lift | Impressions per arm | Total, 2 arms | Total, 3 arms |
|---|---|---|---|---|
| 2.0% → 3.0% | +50% | 3,826 | 7,652 | 11,478 |
| 2.0% → 2.5% | +25% | 13,809 | 27,618 | 41,427 |
| 2.0% → 2.2% | +10% | 80,682 | 161,364 | 242,046 |
| 3.0% → 4.5% | +50% | 2,518 | 5,036 | 7,554 |
| 4.0% → 5.0% | +25% | 6,745 | 13,490 | 20,235 |
| 4.0% → 6.0% | +50% | 1,863 | 3,726 | 5,589 |

**Watch time per impression** is the metric Test & Compare uses. Model: click ~ Bernoulli(p) × watch duration with
coefficient of variation c. For a +50% relative lift at p=2%, about **6,200 impressions per arm** are needed at c=1, and
about **10,100 at c=1.5**. For +20%, the figures are 39k and 63k per arm (calc). Watch-time tests therefore need roughly 1.6–2.6× the
impressions of a pure-CTR test of the same relative size, because viewing durations add variance. The Evan Miller rule of thumb
n ≈ 16σ²/δ² per arm gives the same numbers. https://www.evanmiller.org/how-not-to-run-an-ab-test.html (ANEC, practitioner; standard formula)

- **PEER** Realistic effect sizes are small. In 22,743 Upworthy RCTs (370M impressions, mean CTR 1.39%), each extra
  negative word raised CTR by ~**2.3%** relative, and each positive word lowered it by ~1.0%. Robertson et al. 2023, *Nat Hum Behav* 7:812–822,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10202797/
- **PEER** Concreteness effects in 8,977 Upworthy tests: the paper's worked examples are 0.91% vs 0.86% and 1.17% vs 1.06%, a relative difference of
  ~5–10%. Aubin Le Quéré & Matias 2025, *Sci Rep* 15:994, https://pmc.ncbi.nlm.nih.gov/articles/PMC11704130/
  → Typical *single-cue* changes move CTR by single-digit percentages. A few-hundred-impression channel can only detect
  **very large, promise-level** differences (≥50% relative), and even those need thousands of impressions.
- **PEER** Effect sizes have fat tails. Across Bing experiments most ideas do little and a few do a lot. When tails are
  very heavy, testing **many ideas with smaller samples** beats a few high-powered tests. Azevedo et al. 2020, *J Polit Econ*
  128(12), https://ideas.repec.org/a/ucp/jpolec/doi10.1086-710607.html
- **ANEC** Peeking: stopping the first time p<0.05 gave a **26.1%** false-positive rate in Miller's example. With 10 looks, a reported 1% level
  behaves like a real 5% level. Fix the sample size in advance, or use sequential/Bayesian designs.
  https://www.evanmiller.org/how-not-to-run-an-ab-test.html
- **PEER-adjacent (preprint)** Continuous monitoring makes standard p-values "wholly unreliable". Always-valid p-values
  (mSPRT) solve this. Johari, Pekelis & Walsh, arXiv:1512.04922, https://arxiv.org/abs/1512.04922
- **PEER** Multiple variants and multiple tests: hierarchical (multilevel) models with partial pooling replace
  Bonferroni-style corrections and give more efficient estimates. Gelman, Hill & Yajima (*J Res Educ Eff* 2012; arXiv
  version opened) https://arxiv.org/abs/0907.2478
- **ANEC/GAP** Novelty effects: no thumbnail-specific evidence found. One mechanism is plausible for a small channel: early impressions come mostly from
  subscribers and browse traffic, later ones from suggested and search traffic, so the audience mix shifts over the test window. Keep each test
  running across whole weeks, and never compare variants shown in different weeks (no sequential "before/after" swaps).
- **OFF** Upworthy's own editors peeked, stopped tests when they chose, and ran no power analysis. Its "significance" field was
  "NOT an estimate of statistical significance". Randomisation was broken in ~22% of tests from Jun 2013 to Jan 2014 (flagged in the 2024
  correction). This is a cautionary example for informal testing. Matias et al. 2021, *Sci Data* 8:195,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC8329003

### Pre-testing when impressions are scarce
- **OFF** Google Ads video experiments: a basic two-arm creative A/B test (Video Reach/View campaigns only) or Custom with up to
  10 arms. The success metric can be CTR, view rate, CPV and others. Google calls 70–80% confidence "directional" and recommends waiting for 95%.
  The help page does not mention thumbnails. https://support.google.com/google-ads/answer/10436762
  Validity caveat (**GAP**): ad audiences, placements and the ad label all differ from organic browse, and no study found
  shows that ad-CTR rankings transfer to organic thumbnails. Use ads to compare *promises* (which hook makes developers stop), not styling.
- **PEER** Stated choices on a survey panel track real behaviour only moderately. MTurk willingness to share correlated
  **r=.44** with actual Twitter sharing across 67 headlines (n=993). Mosleh, Pennycook & Rand 2020, *PLOS ONE* 15(2):e0228882,
  https://dspace.mit.edu/handle/1721.1/128754 → A panel can screen out losers but cannot pick a winner when the effects are small.
- **VENDOR** PickFu-type panels: no published validity study against live CTR was found (**GAP**). Panels are general-population
  respondents, not Kubernetes engineers, unless you pay for targeting.
- **DATA/VENDOR** Humans predict A/B winners only modestly above chance. 70,149 guesses on GuessTheTest were right about 59% of the time
  (chance 50%), and Kohavi's class got about 48% (chance 33%). Run by GoodUI, which sells test data.
  https://goodui.org/blog/beyond-opinions-about-opinions-real-a-b-test-prediction-rates-from-70-000-guesses/
  → Your own or a panel's gut feeling is weak evidence, though better than nothing.

## 3. What gets clicked and watched

- **PEER** Negativity: negative words raise CTR slightly and positive words lower it. Sadness helps, while joy *and fear* hurt, and anger has no
  effect. Caveats: the data is 2013–15 Upworthy news (a clickbait-style outlet), the dictionary-based emotion measures are noisy, and the
  study looked at headlines only, not images. Robertson et al. 2023 (above).
- **PEER** Curiosity gap vs clarity: the relationship is curvilinear. Making vague headlines more concrete helps, and making
  already-concrete headlines more concrete hurts. 50.9% of tests sat in the "too concrete" region, where curiosity paid off.
  Results are audience-specific. Aubin Le Quéré & Matias 2025 (above). Cambridge talk abstract: studies "do not consistently show"
  that clickbait raises engagement. https://talks.cam.ac.uk/talk/index/210730/
- **OFF** Clickbait penalty: low average view duration means fewer recommendations (answer/7628154). Test & Compare scores
  watch time, so a variant that wins on CTR but loses on retention loses the test (answer/13861714). The recommender adds
  satisfaction surveys on top (YouTube blog, above).
- **DATA (vendor-run)** Faces: in 300k+ 2025 "viral" videos, thumbnails with and without faces performed about the same. Faces helped only above
  an unstated subscriber threshold. Multiple faces did better than one. In the **Business niche faces did worse**, and in Finance they did better.
  Run by 1of10 Media and reported by SEJ (Dec 2025). The sample was selected on success (outlier score vs channel median), so survivorship applies.
  https://www.searchenginejournal.com/do-faces-help-youtube-thumbnails-heres-what-the-data-says/563944/
- **GAP** Peer-reviewed evidence on thumbnail *visuals* (amount of text, contrast, colour, emotional faces) for YouTube CTR:
  none with usable effect sizes was found. A Springer chapter (Weismueller & Harrigan) studied 50k thumbnails, but its findings could
  not be read. Vendor figures such as "faces +38%" or "high contrast 6.5% vs 4.7%" cite no study, so treat them as **VENDOR/unsupported**.
- **GAP** Numbers in titles: no YouTube-specific peer-reviewed result was found. Upworthy-based work does not isolate this cue.
- **VENDOR** vidIQ, TubeBuddy, 1of10 and Eden publish breakout-video "studies". Their samples are selected on outcome (survivorship),
  they publish no randomised comparisons, and they sell tools. Use them as a source of **hypotheses**, never as evidence of an effect.
- **GAP** Developer audiences: no evidence was found on how engineers respond to title and thumbnail cues. Robertson's and Upworthy's
  audiences were general news readers. Lean on your own pooled test log.

## 4. A testing programme for a small channel

1. **Promise before styling.** Expected effects scale with how different the variants are (fat tails, PEER). Styling changes
   (colour, font, contrast) are single-cue changes, and in the literature single cues move CTR by ~2–10% (PEER), which your
   traffic cannot detect. Different *promises* (what the viewer will get: "agents open PRs you review" vs "run an agent
   team on your own cluster" vs a concrete result such as "12 PRs overnight, 3 merged") are the large-effect bets.
2. **One hypothesis per test.** All variants in a test differ on one named dimension (promise, concreteness, face/no face,
   negative/neutral framing), while everything else stays fixed. If title and thumbnail differ together, the hypothesis is "this
   package", and you log it as such.
3. **Use all 3 arms** only when they span the dimension (vague / medium / concrete). Otherwise use 2 arms to keep power up.
4. **Pool across videos.** Each test yields a log-odds-ratio of CTR and a ratio of watch time per impression, with standard errors.
   Fit a random-effects meta-analysis or Bayesian hierarchical model per hypothesis tag (partial pooling, PEER Gelman).
   Ten inconclusive tests on the same hypothesis can together show a clear effect.
5. **Beta-binomial quick read** per arm: posterior Beta(1+clicks, 1+impressions−clicks). Report P(B>A) and the
   credible interval, not "winner". Watch time comes from Studio's exported per-variant watch time share.

## Decisions

1. **Turn on advanced features and run Test & Compare on every long-form upload**, using title+thumbnail packages. It costs
   nothing and randomises properly, and a "Winner" result is optimised for watch time, not clicks. [OFF answer/13861714]
2. **Expect "Inconclusive" below roughly 5–10k impressions per video, and accept it.** Read the per-variant numbers anyway and log
   them for pooling. [OFF; calc table; PEER Gelman]
3. **Upload your best guess first.** An inconclusive test falls back to the *first* uploaded variant. [OFF answer/13861714]
4. **Test promises, not pixels,** until a pooled hypothesis is settled. Styling tweaks are typically ≤10% effects and need
   80k+ impressions per arm. [PEER Robertson, Aubin Le Quéré; PEER Azevedo; calc]
5. **Each test varies exactly one named hypothesis,** written down before upload. Do not use near-duplicate variants, which YouTube says
   run long and end without a winner. [OFF; ANEC]
6. **Never edit the title or thumbnail mid-test, and never "fix" a video by swapping its thumbnail in week 2 and comparing weeks.** The edit
   kills the test, and the week-to-week comparison is confounded by changes in the traffic mix. [OFF; ANEC/GAP novelty]
7. **No peeking-based calls in your own analyses.** Fix the decision point (end of test, or 14 days) before looking, or use the
   Bayesian P(B>A) with a pre-set threshold such as 0.9. [ANEC Miller; PEER-adjacent Johari]
8. **Make the title concrete enough to be understood and keep one open question for the video to answer.** Avoid both extremes.
   [PEER Aubin Le Quéré & Matias 2025]
9. **Allow negative or problem framing ("agents that break prod", "why review is the bottleneck") as a hypothesis to test, not a default.**
   The evidence comes from news, the effect is about 2% per word, and fear-type words lowered CTR. [PEER Robertson 2023]
10. **Never promise what the video doesn't show in the first 30 s.** CTR gained through clickbait is lost on watch time, and watch time
    is what wins the test and earns recommendations. [OFF 7628154, 13861714, YouTube blog]
11. **Treat faces as an open question for this niche.** A vendor dataset shows no average lift and a negative one in Business. Test face
    vs product-UI only after the promise is settled. [DATA/VENDOR 1of10; GAP peer]
12. **Pre-test promises with paid ads only in a pinch, and only to rank hooks.** Ad CTR at 95% confidence is "directional" for
    organic, and no transfer evidence exists. Budget is your call. [OFF Google Ads 10436762; GAP]
13. **Use survey panels (PickFu-type) only to eliminate obvious losers,** and target developers. Stated preference tracks
    behaviour only at r≈.44. [PEER Mosleh 2020; VENDOR; GAP validity]
14. **Shorts cannot use Test & Compare.** For Shorts, test hook *promises* by posting different Shorts cut from the same source and
    comparing them in the log. Treat these comparisons as weak, because they are not randomised. [OFF 13861714; ANEC]
15. **Ignore vendor "X% more clicks" numbers as evidence.** Mine them for hypotheses to put in your own log. [VENDOR; GAP]

## Test log (one row per arm; a tab-separated file or sheet)

| Field | Example | Why |
|---|---|---|
| test_id | T2026-07 | Groups the arms of one test |
| video_id, publish_date | abc123, 2026-10-14 | Lets you join to Studio exports |
| format | long / short | Shorts aren't randomised |
| method | yt_test_compare / ads / panel / sequential | Weights evidence quality |
| hypothesis_tag | promise:outcome-vs-mechanism; concreteness; face; negativity | The key you pool on |
| hypothesis_text | "Concrete outcome beats mechanism" | Written before upload |
| arm, is_first_uploaded | B, false | Tells you the inconclusive default |
| title, thumbnail_file | text, path | The stimulus |
| arm_level | vague / medium / concrete; face=yes | The value on the hypothesis dimension |
| start, end, days | dates, 14 | Records the window |
| impressions, ctr, clicks | 1,840, 3.1%, 57 | Feeds the CTR estimate |
| watch_time_share, watch_hours | 41%, 6.2 | Test & Compare's metric |
| avg_view_duration | 1:52 | Clickbait check |
| yt_outcome | winner / same / inconclusive | YouTube's verdict |
| p_better, ci_low, ci_high | 0.78, −0.1, 0.6 | Your own Bayesian read (log-odds) |
| traffic_mix_note | 60% browse / 25% suggested | Context for novelty and audience mix |
| decision, learned | kept B; "outcome promise +" | Closes the loop |

Pooling recipe: per hypothesis_tag, compute log(CTR_B/CTR_A) or the log ratio of watch hours per impression and its SE for each test.
Then run a random-effects meta-analysis (or a Bayesian hierarchical model with a normal prior on the effect, sd ≈ 0.2 on the log scale,
matching the PEER effect sizes). Re-run after every 3 new tests, and retire a hypothesis once its 90% interval excludes zero
or sits tightly around it.
