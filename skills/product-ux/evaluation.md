# Evaluation: evidence strength, expert methods, and the limits of an AI critic

Contents: laws and folklore · heuristic evaluation · cognitive walkthrough · KLM estimates · the AI critic · synthetic users · tests for humans to run · claims an agent must not make · validation status

## Laws and folklore

"Laws of UX" lists mix perception science with aphorisms. Cite the strong ones within their scope; never cite folklore as evidence.

| Claim | Strength | Use it as | Source |
| --- | --- | --- | --- |
| Pointing time grows with log₂(distance/width + 1) (Fitts) | Strong, within scope | Big, near targets for frequent actions; destructive targets far from frequent ones. Not a model of search or decisions | [Fitts 1954](https://doi.org/10.1037/h0055392), [MacKenzie 1992](https://doi.org/10.1207/s15327051hci0701_3) |
| Long, narrow hover paths follow the steering law | Strong | Hover intent or delay on submenus | [Accot & Zhai 1997](https://doi.org/10.1145/258549.258760) |
| "Fewer choices are faster" (Hick) | Misapplied | Its log curve means each extra option costs *less* than the last; Hick's setup rarely matches UI tasks. Optimise scanning: order, grouping, labels | [Liu et al. 2020](https://doi.org/10.1145/3313831.3376878), [Proctor & Schneider 2018](https://doi.org/10.1080/17470218.2017.1322622) |
| Novices search menus visually (≈ linear); experts decide (≈ Hick) | Strong | Keep item positions stable so people become experts; don't reorder adaptively | [Cockburn et al. 2007](https://doi.org/10.1145/1240624.1240723) |
| Broad, shallow menus beat deep ones, up to a point | Consistent | 2–3 levels of well-grouped, scannable breadth; medium beats both extremes on the web | [Kiger 1984](https://doi.org/10.1016/s0020-7373%2884%2980018-8), [Landauer & Nachbar 1985](https://doi.org/10.1145/1165385.317470), [Larson & Czerwinski 1998](https://doi.org/10.1145/274644.274649) |
| "7 ± 2 items maximum" (Miller) | Folklore as a UI rule | Limits what must be *remembered* (about 4 chunks, Cowan), not what can be *seen*. A visible list is a scanning problem | [Miller 1956](https://doi.org/10.1037/h0043158), [Cowan 2001](https://doi.org/10.1017/s0140525x01003922) |
| Doherty threshold: under 400 ms makes users "addicted" | Folklore numbers | Uncontrolled IBM mainframe field data; neither "400 ms" nor "addicting" appears in the text. Keep only: sub-second response matters in tight loops | [Thadhani 1981](https://doi.org/10.1147/sj.204.0407) |
| 0.1 / 1 / 10 s response bands | Consistent (expert synthesis) | Under 100 ms for direct manipulation, under 1 s without an indicator, progress from 1–10 s, percent-done and an escape beyond | [Miller 1968](https://doi.org/10.1145/1476589.1476628), [Card et al. 1991](https://doi.org/10.1145/108844.108874) |
| Proximity, similarity, common region group things | Strong | Inner gaps smaller than outer gaps; same look means same behaviour; a border or card overrides spacing | [Wagemans et al. 2012](https://doi.org/10.1037/a0029333) |
| Recognition beats recall | Strong | Show options, recents and context; avoid blank command boxes | [Shepard 1967](https://doi.org/10.1016/s0022-5371%2867%2980067-7) |
| Distinct items stand out (von Restorff) | Strong | One primary action per view; distinctiveness is relative | [Hunt 1995](https://doi.org/10.3758/bf03214414) |
| Peak–end rule | Strong in psychology | Fix the worst moment and the ending, without neglecting the average | [Cockburn et al. 2015](https://doi.org/10.1145/2702123.2702139) |
| Unfinished tasks are remembered better (Zeigarnik) | Failed meta-analysis | Don't cite it. People do tend to *resume* unfinished tasks: support drafts and "continue where you left off" | [Ghibellini & Meier 2025](https://doi.org/10.1057/s41599-025-05000-w) |
| Beautiful is perceived as usable | Contested | Polish raises first-impression ratings; poor usability lowers perceived beauty after use. Discount ratings of polished prototypes | [Kurosu & Kashimura 1995](https://doi.org/10.1145/223355.223680), [Tuch et al. 2012](https://doi.org/10.1016/j.chb.2012.03.024) |
| Choice overload | Conditional | Appears with complex options, uncertain preferences or time pressure; otherwise organise large sets with filters | [Chernev et al. 2015](https://doi.org/10.1016/j.jcps.2014.08.002) |
| Defaults steer choices | Strong | Default to the user's likely interest, visibly and changeably; never pre-check consent or upsells | [Johnson & Goldstein 2003](https://doi.org/10.1126/science.1091721) |
| Confirmation dialogs habituate | Strong | Attention to a warning drops sharply after the second exposure; undo by default | [Anderson et al. 2015](https://doi.org/10.1145/2702123.2702322), [Vance et al. 2018](https://doi.org/10.25300/misq/2018/14124) |
| Slips need constraints and undo; mistakes need a better model | Strong | Diagnose the error type before choosing the fix | [Norman 1981](https://doi.org/10.1037/0033-295x.88.1.1) |
| "Design for the F-pattern" | Folklore (misreading) | The F is a failure mode of unformatted text; headings and front-loading produce layer-cake scanning | [NN/g](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/) |
| All caps is unreadable because of word shape | Folklore | Uppercase is fine for short labels; avoid it for paragraphs | [Arditi & Cho 2007](https://doi.org/10.1016/j.visres.2007.06.010) |
| Skeleton screens feel faster than spinners | Contested | Use only when they match the real layout; determinate progress for long waits | [Mejtoft et al. 2018](https://doi.org/10.1145/3232078.3232086) |
| Percent-done indicators reduce anxiety | Consistent | Progress for waits over a few seconds; never fake it; avoid stalls at the end | [Myers 1985](https://doi.org/10.1145/1165385.317459), [Harrison et al. 2007](https://doi.org/10.1145/1294211.1294231) |
| Jakob's, Tesler's, Postel's laws | Aphorisms | Prompts, not evidence. Even the IETF has walked back Postel ([RFC 9413](https://www.rfc-editor.org/rfc/rfc9413.html)) | — |

## Heuristic evaluation

Use Nielsen's ten heuristics as an inspection vocabulary and cite one per finding ([NN/g](https://www.nngroup.com/articles/ten-usability-heuristics/); [Nielsen & Molich 1990](https://doi.org/10.1145/97243.97281)). For AI features add the 18 human-AI guidelines ([ai-features.md](ai-features.md)); for consent and settings add the deceptive-pattern families ([deceptive-patterns.md](deceptive-patterns.md)).

1. Visibility of system status
2. Match between system and the real world
3. User control and freedom
4. Consistency and standards
5. Error prevention
6. Recognition rather than recall
7. Flexibility and efficiency of use
8. Aesthetic and minimalist design
9. Help users recognise, diagnose and recover from errors
10. Help and documentation

**Evaluators disagree a lot.** Two evaluators on the same system agreed on 5–65 % of problems ([Hertzum & Jacobsen 2001](https://doi.org/10.1207/s15327590ijhc1304_05)); in CUE-4, 17 professional teams reported 340 issues and 60 % came from a single team ([Molich & Dumas 2008](https://doi.org/10.1080/01449290600959062)). A single evaluator's severity ratings are unreliable; average at least three ([NN/g severity](https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/)). So one pass is a sample, not a verdict: run independent passes and merge them.

Rate severity from frequency × impact × persistence, and map it to the P0–P3 scale in [validation.md](validation.md#findings-that-hold-up).

## Cognitive walkthrough

Best for learnability of new or unfamiliar flows, and well suited to an agent because it is step-by-step and grounded ([NN/g](https://www.nngroup.com/articles/cognitive-walkthroughs/); [Lewis et al. 1990](https://doi.org/10.1145/97243.97279)). For a stated user and goal, at each step of the task analysis, on the rendered screen, answer:

1. Will users try to achieve the right result?
2. Will they notice the correct action is available?
3. Will they associate the action with the result they want?
4. After acting, will they see progress toward the goal?

Record pass or fail per question per step, with the screenshot. A "no" is a finding.

## KLM estimates

The Keystroke-Level Model predicts skilled, error-free execution time and is the cheapest objective way to compare two designs of a frequent task ([Card, Moran & Newell 1980](https://doi.org/10.1145/358886.358895)).

| Operator | Time |
| --- | --- |
| K keystroke | 0.2 s (0.28 s for an average typist) |
| P point with a mouse | 1.1 s |
| B mouse button press or release | 0.1 s |
| H move hand between keyboard and mouse | 0.4 s |
| M mental preparation | 1.35 s |
| R system response | measured |

Example: refunding one line of an order.

- Design A: open order (M P B = 2.55), open menu (P B = 1.2), choose Refund (P B = 1.2), type the amount (H M K×5 = 2.75), confirm (H P B = 1.6) ≈ 9.3 s.
- Design B, an inline refund field confirmed with Enter: focus the field (M P B = 2.55), type (H M K×5 = 2.75), Enter (K = 0.2) ≈ 5.5 s.

At 40 refunds a day per agent, B saves about 2.5 minutes a day each. Label it a model estimate; it says nothing about learnability or errors.

## The AI critic

An agent reviewing its own interface is one fallible evaluator, and the evidence says how fallible:

| Study | Result |
| --- | --- |
| GPT-4 on 51 UI mock-ups ([Duan et al., CHI 2024](https://doi.org/10.1145/3613904.3642782)) | Precision 0.60 vs 0.83 for a human expert; recall 0.38 vs 0.34; only 52 % of suggestions rated accurate; accuracy *fell* across design iterations |
| GPT-4o on web systems ([Guerino et al. 2025](https://arxiv.org/abs/2506.16345)) | Found 21 % of expert issues; many extras were hallucinated; weak on user control, flexibility and efficiency |
| UX-LLM on iOS apps ([Ebrahimi Pourasad & Maalej, ICSE 2025](https://arxiv.org/abs/2411.00634)) | Precision 0.61–0.66, recall 0.35–0.38; source access found some uncommon paths |
| Three models on two apps ([Zhong et al. 2025](https://arxiv.org/abs/2507.02306)) | 73–77 % of issues vs 57–63 % for five experts, but weak on conventions and cross-screen issues |
| Few-shot real critiques with visual grounding ([UICrit, UIST 2024](https://doi.org/10.1145/3654777.3676381)) | +55 % feedback quality |
| Agentic loops ([arXiv 2608.21377](https://arxiv.org/abs/2608.21377)) | Feedback and reconsideration loops increase sycophancy; worse in more capable models |

Make the critic as honest as it can be:

- **Fresh context.** A reviewer subagent gets the screenshots, the state labels and the job story, never the author's rationale or "I improved X".
- **Fixed rubric and grounding.** Each finding names the heuristic and points at the element and location.
- **Independent passes.** Run at least three (different heuristic sets or seeds), merge them, and report how much they overlap.
- **No "is it fixed now?" loop.** Use a new reviewer instance per round.
- **Lean on its strengths, discount its weaknesses.** It is good at local consistency, alignment, copy and label mismatches; weak at flow-level problems, efficiency for experts, conventions and taste.
- **Interaction beats screenshots.** Drive the running UI, so state and flow problems surface.

## Synthetic users

Don't use AI personas as evidence. They did far better than real people at tree testing, claimed to finish everything, rated every need equally and praised features real users disliked ([NN/g](https://www.nngroup.com/articles/synthetic-users/)). GPT's first clicks differed significantly from 3,431 real participants in 53 % of tasks, and adding personas or chain of thought only made the answers sound more believable ([Kuric et al. 2026](https://arxiv.org/abs/2605.18302)). LLM stand-ins flatten groups and show too little variance ([Wang et al. 2025](https://www.nature.com/articles/s42256-025-00986-z)), and agents take shortest paths that people don't ([UXAgent](https://doi.org/10.1145/3706599.3719729)). Simulated walkthroughs are fine for finding candidate problems and piloting a test script, never for preferences, success rates, scores or quotes.

## Tests for humans to run

Draft the kit; a person runs it.

- **Task scenarios** in the user's words with no UI terms ("your accountant needs last quarter's invoices", not "click Export"), a clear end state, five to eight tasks per 30–45 minute session.
- **Five users per distinct group, per round, in an iterative series.** That finds the big problems. It never measures rates: five-user samples found anywhere from 55 % to 99 % of problems ([Faulkner 2003](https://doi.org/10.3758/bf03195514)), and on complex sites the first five found about 35 % ([Spool & Schroeder 2001](https://doi.org/10.1145/634067.634236)).
- **Think-aloud with neutral prompts;** "why" probes mid-task change behaviour ([Boren & Ramey 2000](https://doi.org/10.1109/47.867942)).
- **Questionnaires:**
  - SEQ after each task, 7-point, average about 5.5 ([MeasuringU](https://measuringu.com/seq10/)).
  - SUS after the session, average 68, reported as a percentile or grade and never as "% usable" ([Bangor et al. 2008](https://doi.org/10.1080/10447310802205776)).
  - UMUX-Lite where SUS is too long; NASA-TLX for demanding operational screens.
- **First-click and five-second tests** in an unmoderated tool for navigation and labelling questions. Recordings of faces and voices are personal data: consent, and a processing agreement with the vendor.

## Claims an agent must not make

- "Users will find this intuitive" or "users will love this": no users were observed.
- "Validated", "tested" or "user-approved" for anything reviewed only by models.
- Success rates, SUS, SEQ or NPS numbers, quotes or personas presented as research, unless they come from a real dataset in the repository (cite the file).
- "Accessible" or "WCAG compliant" from automated checks: say "passes the axe rules run; manual checks pending: …".
- "This will increase conversion by N %": at most a hypothesis with a metric.
- "Compliant with" a named law: the floor is a design floor, not legal advice.
- A severity score as a fact: it is one evaluator's estimate unless several passes agree.

## Validation status

Attach this to every design deliverable:

```text
Validation status
- Evidence used: <tickets, analytics export, docs, existing UI, supplied facts>
- Checked by agent: scan (rules, result) · heuristic passes (n, overlap) · cognitive walkthrough (tasks) ·
  KLM (tasks) · keyboard-only gate (flows) · states rendered (list) · axe (pages)
- NOT validated with users: <riskiest assumptions from the map>
- Recommended human test: <groups, scenarios, measures>
- Instrumented to learn: <events and metrics added>
```
