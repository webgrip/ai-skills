# How this compares to the tools it was built from

Measured, not claimed. Every number below comes from the committed extracts and the source repos
at the commits recorded in [`sources/README.md`](sources/README.md). Attribution and licences are
in [`skills/humanize/NOTICE.md`](../../skills/humanize/NOTICE.md).

## Coverage

For each source: how many distinct patterns we extracted from it, how many of our catalog entries
carry it, how many entries **only** it had, and how many entries our catalog has that it does not.

| Source | Extracted | In our catalog | Only it had | We add beyond it |
| --- | ---: | ---: | ---: | ---: |
| avoid-ai-writing (skill + detector) | 267 | 114 | 28 | **92** |
| im-not-ai | 160 | 76 | 36 | 149 |
| Wikipedia, Signs of AI writing | 144 | 71 | 27 | 139 |
| Vollmer, field guide | 83 | 65 | 13 | 141 |
| blader/humanizer | 48 | 44 | 1 | **162** |
| tropes.fyi | 41 | 36 | 2 | 170 |
| no-ai-slop | 36 | 35 | 1 | 171 |
| our own prior house rule | 40 | 34 | 1 | 172 |
| Will Francis | 33 | 27 | 1 | 179 |
| Velitchkov, 22 Claude clichés | 26 | 22 | 3 | 184 |
| Hassid, the new em-dash | 13 | 13 | 1 | 193 |
| Goedecke, on em-dashes | 9 | 6 | 0 | 200 |

Reading it: the broadest single source still leaves 92 entries on the table, and the most-installed
one leaves 162. **Sixty of our 229 English entries came from exactly one source** — those are what
picking any single tool silently costs you. im-not-ai alone contributed 36 that nobody else had.

The core is corroborated rather than invented: em-dash density appears in 15 of the 17 extracted
sources, negative parallelism in 14, meta-signposting and signposted conclusions in 11 each.

## Dutch

No source repo covers Dutch. There are humanizers for Korean, Chinese, Japanese, Russian and
German; the single occurrence of "Dutch" in blader/humanizer is the word inside an English example
sentence. Our Dutch catalog holds **306 entries, 219 mapped onto an English counterpart and 87 with
no English equivalent at all**, because they describe things that can only go wrong in Dutch:

| Entry | What it catches |
| --- | --- |
| `missing-inversion-after-fronting-nl` | V2 word order lost after a fronted phrase: *In dit artikel, we bespreken…* |
| `die-dat-confusion-nl` | Relative pronoun picked as if it were English *that* |
| `english-stem-dutch-inflection-nl` | English verb stem with Dutch inflection |
| `oxford-comma-nl` | Serial comma before *en*, which Dutch does not take |
| `periphrastic-superlative-nl` | *meest snelle* where Dutch inflects to *snelste* |
| `english-number-date-format-nl` | `3.5` where Dutch writes `3,5`; American date order |
| `american-quote-and-genitive-nl` | Punctuation inside the closing quote, and *Peter's* for *Peters* |
| `language-switch-mid-text-nl` | An untranslated English chunk mid-paragraph |

Another 79 of the same kind. A translated English catalog cannot produce these, which is why
the Dutch half was built from Dutch sources, the German sister catalogs, and a transfer step that
asked what form each English pattern actually takes in Dutch rather than what it translates to.

## Architecture

**Context cost.** The catalog is a file the model opens when it needs it, not prose it carries all
session.

| Skill | Always-on SKILL.md |
| --- | ---: |
| avoid-ai-writing | 872 lines, 108 KB |
| blader/humanizer | 456 lines, 30 KB |
| im-not-ai (Korean) | 331 lines, 29 KB |
| humanizer-de | 177 lines, 21 KB |
| no-ai-slop | 97 lines, 11 KB |
| **ours** | **56 lines, 7 KB** |

Ours defers 535 entries across two languages to `patterns-en.md`, `patterns-nl.md` and
`method.md`, which cost nothing until opened.

**Measurement.** Every regex is run against human-written prose before it ships: Strunk and Twain
for English, two Dutch Wikipedia articles for Dutch. Over two hits per 10,000 words means the regex
is too broad, and it is tightened or dropped with the cue kept as prose. That discipline removed 26
Dutch regexes during the merge — the generic tricolon matcher alone fired 25.2 times per 10,000
words of ordinary Dutch.

The idea is not ours. **avoid-ai-writing did it first**, and its `corpus/` makes the same argument:
a flag raised on human writing is a false positive by construction, so provenance is the ground
truth and no judge is needed. It keeps hashes only; we commit public-domain text so the check runs
offline.

**Self-consistency.** The catalogs' own 511 rewritten examples are scanned with the catalogs' own
scanner on every test run. Zero stray tells, zero em dashes. An entry is allowed to contain the
surface it demonstrates, and three sibling pairs are allowlisted by name; everything else fails the
build. No source repo tests its own prose this way.

## Does it actually write better?

The earlier runs compared the skill's `edit` mode, which by its own rule touches only flagged spans,
against an agent given a free rewrite, and graded rhythm with an undefined "flattened" flag at a
fixed A/B position. Those numbers measured the comparison's design as much as the skill, so they are
withdrawn. What survived them and the three seeds since: the skill has never fabricated a number, a
date or a name. Whether it loses on rhythm is measured below, like for like.

The measurement now (`workflows/quality-retest.js`): six slop texts, three English and three Dutch,
each carrying protected facts. Two comparisons, each giving both arms the identical user request:
*rewrite* ("Rewrite this so it reads like a person wrote it. Keep every fact.") and *edit* ("Fix only
what reads as AI-written and leave everything else exactly as I wrote it."). The skill arm reads
SKILL.md and routes its own mode; a routing miss is counted. A native-reader grader per language,
blind to which arm is which, grades each pair twice with the positions swapped; a win needs both
orders to agree. Rhythm loss is not a grader opinion: `flattened` is true when the scanner's
sentence-length variation on the output falls under 0.6 of the original's or under 0.30, or the
grader reports the first person or an author's stance gone. Any register label, pattern count or
scan output inside the returned text is counted as leakage and reported regardless of grade.

<!-- quality-retest results -->
**Before the recast rule** (seeds 1, 2, 3). Routing misses 0; leakage findings 0. Flattening constants: ratio 0.6 to the original's variation, floor 0.3. Cells read one value per seed, in seed order.

**Rewrite against a free rewrite**

| Case | Skill | Facts kept | Invented | Naturalness | Flattened | Leakage |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `en-linkedin-post` | lost / won / won | 3/3 / 3/3 / 3/3 | 2 / 5 / 0 | 3,3 / 3,3 / 3,3 | True / False / True | 0 / 0 / 0 |
| `en-technical-readme` | won / won / lost | 4/4 / 4/4 / 4/4 | 0 / 0 / 0 | 4,4 / 4,3 / 4,4 | True / True / False | 0 / 0 / 0 |
| `en-incident-writeup` | won / won / won | 3/3 / 3/3 / 3/3 | 0 / 1 / 0 | 3,4 / 4,4 / 4,4 | False / False / False | 0 / 0 / 0 |
| `nl-linkedin-post` | tie / lost / lost | 6/6 / 6/6 / 6/6 | 0 / 0 / 0 | 3,3 / 3,3 / 4,4 | False / False / True | 0 / 0 / 0 |
| `nl-meetup-description` | tie / lost / lost | 8/8 / 8/8 / 8/8 | 0 / 2 / 2 | 4,4 / 3,4 / 4,4 | True / False / True | 0 / 0 / 0 |
| `nl-readme-intro` | lost / lost / tie | 4/4 / 4/4 / 4/4 | 0 / 0 / 0 | 3,3 / 3,3 / 3,3 | True / True / True | 0 / 0 / 0 |

Skill won 7, lost 8, tied 3 across 3 seed(s).

**Edit against a minimal edit**

| Case | Skill | Facts kept | Invented | Naturalness | Flattened | Leakage |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `en-linkedin-post` | lost / won / tie | 3/3 / 3/3 / 3/3 | 0 / 1 / 0 | 3,3 / 3,3 / 3,3 | True / False / True | 0 / 0 / 0 |
| `en-technical-readme` | tie / won / won | 4/4 / 4/4 / 4/4 | 0 / 1 / 0 | 4,4 / 4,4 / 3,4 | False / False / False | 0 / 0 / 0 |
| `en-incident-writeup` | lost / tie / lost | 3/3 / 3/3 / 3/3 | 2 / 0 / 0 | 4,4 / 4,3 / 4,3 | False / False / True | 0 / 0 / 0 |
| `nl-linkedin-post` | won / won / lost | 6/6 / 6/6 / 6/6 | 0 / 0 / 0 | 3,3 / 4,3 / 3,3 | True / False / False | 0 / 0 / 0 |
| `nl-meetup-description` | lost / lost / lost | 8/8 / 8/8 / 8/8 | 0 / 0 / 0 | 3,3 / 4,4 / 4,4 | True / True / True | 0 / 0 / 0 |
| `nl-readme-intro` | tie / won / tie | 4/4 / 4/4 / 4/4 | 0 / 0 / 0 | 4,4 / 3,4 / 4,3 | True / True / True | 0 / 0 / 0 |

Skill won 6, lost 7, tied 5 across 3 seed(s).


**After the recast rule** (seeds 4, 5, 6). Routing misses 0; leakage findings 0. Flattening constants: ratio 0.6 to the original's variation, floor 0.3. Cells read one value per seed, in seed order.

**Rewrite against a free rewrite**

| Case | Skill | Facts kept | Invented | Naturalness | Flattened | Leakage |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `en-linkedin-post` | lost / tie / won | 3/3 / 3/3 / 3/3 | 5 / 4 / 4 | 3,3 / 4,4 / 4,4 | False / True / True | 0 / 0 / 0 |
| `en-technical-readme` | tie / lost / won | 4/4 / 4/4 / 4/4 | 3 / 5 / 0 | 4,4 / 4,4 / 4,4 | True / False / True | 0 / 0 / 0 |
| `en-incident-writeup` | won / lost / won | 3/3 / 3/3 / 3/3 | 4 / 0 / 0 | 4,4 / 3,3 / 4,3 | False / False / False | 0 / 0 / 0 |
| `nl-linkedin-post` | tie / won / lost | 6/6 / 6/6 / 6/6 | 0 / 0 / 0 | 4,4 / 4,4 / 4,4 | True / False / True | 0 / 0 / 0 |
| `nl-meetup-description` | lost / won / tie | 8/8 / 8/8 / 8/8 | 2 / 0 / 0 | 4,4 / 4,4 / 4,3 | True / False / False | 0 / 0 / 0 |
| `nl-readme-intro` | tie / won / tie | 4/4 / 4/4 / 4/4 | 0 / 0 / 2 | 4,4 / 4,4 / 4,4 | True / True / True | 0 / 0 / 0 |

Skill won 7, lost 5, tied 6 across 3 seed(s).

**Edit against a minimal edit**

| Case | Skill | Facts kept | Invented | Naturalness | Flattened | Leakage |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `en-linkedin-post` | lost / lost / tie | 3/3 / 3/3 / 3/3 | 0 / 0 / 0 | 3,2 / 3,2 / 3,3 | True / True / True | 0 / 0 / 0 |
| `en-technical-readme` | tie / won / won | 4/4 / 4/4 / 4/4 | 1 / 0 / 0 | 4,3 / 4,4 / 4,4 | False / False / False | 0 / 0 / 0 |
| `en-incident-writeup` | lost / lost / lost | 3/3 / 3/3 / 3/3 | 0 / 0 / 0 | 3,3 / 3,4 / 3,3 | False / False / False | 0 / 0 / 0 |
| `nl-linkedin-post` | won / lost / lost | 6/6 / 6/6 / 6/6 | 0 / 0 / 0 | 4,4 / 3,3 / 3,3 | True / False / True | 0 / 0 / 0 |
| `nl-meetup-description` | lost / won / lost | 8/8 / 8/8 / 8/8 | 0 / 0 / 0 | 4,4 / 4,4 / 3,3 | True / True / False | 0 / 0 / 0 |
| `nl-readme-intro` | won / tie / lost | 4/4 / 4/4 / 4/4 | 0 / 0 / 3 | 4,3 / 4,4 / 3,4 | True / True / True | 0 / 0 / 0 |

Skill won 5, lost 10, tied 3 across 3 seed(s).

<!-- /quality-retest results -->

**What the seeds say.** Six seeds, twelve outputs each: 72 paired case-runs, every pair graded in
both positions. Seeds 1 to 3 measure the skill before the recast rule, seeds 4 to 6 after it. Across
all six the skill won 25, lost 30 and tied 17, and **336 of 336 protected facts survived, with 0
routing misses and 0 leakage in 72 runs.** Prose quality against a competent agent given the same
request is, overall, parity — anyone reaching for the skill for polish alone should know that before
installing it.

**Read the fidelity numbers as absolutes, not as an advantage.** The grader scores only the skill arm
(`Grade the rewrite labelled "${gradeLabel}"`), so `facts_kept`, `facts_invented` and `naturalness`
describe the skill and nothing else; the baseline is compared on `better_arm` alone. The skill keeping
every fact in 72 runs is therefore a property of the skill, not evidence it beats a plain agent at
fidelity — the plain agent may do as well, and this harness cannot say. Scoring both arms on those
axes is the single highest-value change to make to it.

**The one measured defect was Dutch rewrite, and the recast rule moved it.**

| Comparison | Before (seeds 1-3) | After (seeds 4-6) |
| --- | --- | --- |
| Rewrite, Dutch | 0 W / 6 L / 3 T — *p* = 0.031 | 3 W / 2 L / 4 T — *p* = 1.0 |
| Rewrite, English | 7 W / 2 L / 0 T | 4 W / 3 L / 2 T |
| Edit, English | 3 W / 3 L / 3 T | 2 W / 5 L / 2 T |
| Edit, Dutch | 3 W / 4 L / 2 T | 3 W / 5 L / 1 T |

The rule exists because every Dutch case fires the translationese layer, so the source's clause order
came out of English, and two rules in the always-on body protected exactly that — *"Sentence lengths
vary as the original's did"* and *"Split or join only at a real new action"*. The skill stripped the
calqued vocabulary and left the English skeleton standing while the unconstrained baseline rebuilt
the sentence the way a Dutch writer builds it. SKILL.md now says a construction carried over from
another language is a tell rather than a voice, and recasting it is the fix.

Dutch rewrite had never won a case-run in nine tries; after the rule it wins three and the arm is
statistically indistinguishable from parity. The change itself is Fisher exact *p* = 0.061 on decided
outcomes, so it is a strong direction on a pre-registered target rather than a settled result. The
mechanism is confirmed directly, not inferred: on `nl-linkedin-post` the skill arm now returns *"Een
deploy duurde 40 minuten en is nu in 6 minuten klaar"* where the baseline keeps the calqued *"de
doorlooptijd van deploys teruggebracht van 40 naar 6 minuten"*, and the grader names it — *"echt
Nederlands geschreven in plaats van vertaald"*. English rewrite did not pay for it: 7-2-0 to 4-3-2 is
Fisher *p* = 0.60.

**A warning about reading these tables mid-flight.** After seeds 4 and 5 the English rewrite arm sat
at 1 W / 3 L / 2 T with tripled invention counts, and the obvious conclusion was that the new rule
had leaked into English and broken it. Seed 6 returned 3 W / 0 L / 0 T and dissolved the effect. Ten
of twelve case verdicts flip with the seed; two thirds of a group is still not a result.

**What did move is invented framing in English, and it is the open cost.** Added-claim spans in the
English rewrite arm went from 8 before to 25 after. No fact was ever lost or altered — every cell of
the table reads 30/30 and 54/54 — so these are claims the source did not make rather than corrupted
data: *"given engineers back the time they were spending on alerts"*, *"the workflow is the same at
any scale"* where the original said startup or enterprise. The trend across the after-seeds is 12, 9,
4 and the before-range reached 6, so this is a signal worth watching and not yet a finding. It is the
first thing to measure on the next change.

**Two structural findings the seeds surfaced, both worth fixing next.** First, the recast rule and
the stance rule pull against each other: recasting a construction tends to shed the opinion the
construction carried. On seed 4's `nl-linkedin-post` the skill recast the sentence well and dropped
*"Wij vinden dit een belangrijke stap"*, the author's only opinion, which the baseline kept; the case
graded a tie for exactly that reason. Second, the most reproducible defect in the whole dataset is
neither rhythm nor stance but gap-filling: on `nl-meetup-description` the skill invented *"Daarna is
er tijd om bij te praten"* in three separate seeds. The mechanism is visible in the source — it
deletes the vague tricolon *"inspiratie, kennis, en verbinding"* and supplies a plausible concrete
programme item in its place, which is precisely what the "flag the gap instead" gotcha exists to
prevent and does not achieve.

**Three explanations were measured and killed along the way.** Flattening is not rhythm: of the 20
flattened verdicts in seeds 1 to 3, only 4 are explicable by the sentence-length clause, and in
several the scanner's variation rose. The Dutch catalog does not teach deletion over recasting; its
own examples are the better half on that axis (13% pure deletions against English's 19%, new-word
share 0.62 against 0.55). And the Dutch arm is not drowning in findings: the scanner fires 12.3 to
16.9 times per 100 words on the Dutch cases against 6.2 to 18.6 on the English ones. Each of these
was a confident diagnosis before it was measured.

**The stance rule from seed 1 remains unverified.** Stance-driven flattening flags went 7 of 12, then
3 of 12, then 6 of 12 across seeds 1 to 3. Seed 3 sits inside seed 1's range, so the middle seed was
the outlier and the rule cannot be credited with the improvement it appeared to buy. It stays because
losing the writer's only opinion is the quieter failure, not because it is proven.

## What we did not take

- **Numeric authorship scores.** avoid-ai-writing scores 0 to 100 and labels a text
  HUMAN_ONLY / MIXED / AI_ONLY; im-not-ai grades A to D. We score internally to route effort and
  report named patterns with quoted spans instead. Detectors misclassify second-language,
  neurodivergent and heavily-edited writers wholesale, so a number invites a decision the evidence
  cannot support.
- **The bypass-normalisation pre-pass.** avoid-ai-writing strips zero-width characters and Cyrillic
  lookalikes before matching, and treats their presence as corroborating evidence. We keep the
  pattern in the catalog as a tell and refuse the inverse capability entirely.
- **Korean-specific machinery.** im-not-ai's morphological gates do not transfer. Its *method* —
  translationese as its own layer with its own severity scale — is the part we took, and it is what
  the Dutch layer is built on.

## Shipped size

6 KB always-on, the rest opened on demand. 1390 regexes across 430 scanner rows,
169 English and 261 Dutch.

## What review changed

The catalogs were reviewed after they were built, and the review is the reason to trust them. Seven
adversarial readers found 180 problems in 208 English entries; sixteen Dutch judges, two per
category, found 282 in 251. What both reviews kept finding was the same class of defect: a cue list
that named the *correction* as the tell, a severity of "always" over words the entry's own
false-positive note excuses, and a rewritten example that fixed vagueness by inventing a number.
660 English cues and 102 Dutch ones came out; 55 Dutch entries went in for registers no transfer
could reach. The catalog now practises what it documents, and `test.sh` keeps it that way.
