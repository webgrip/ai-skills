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
**Before the stance rule** (seed 1). Routing misses 0; leakage findings 0. Flattening constants: ratio 0.6 to the original's variation, floor 0.3.

**Rewrite against a free rewrite**

| Case | Skill | Facts kept | Invented | Naturalness | Flattened | Leakage |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `en-linkedin-post` | lost | 3/3 | 2 | 3,3 | True | 0 |
| `en-technical-readme` | won | 4/4 | 0 | 4,4 | True | 0 |
| `en-incident-writeup` | won | 3/3 | 0 | 3,4 | False | 0 |
| `nl-linkedin-post` | tie | 6/6 | 0 | 3,3 | False | 0 |
| `nl-meetup-description` | tie | 8/8 | 0 | 4,4 | True | 0 |
| `nl-readme-intro` | lost | 4/4 | 0 | 3,3 | True | 0 |

Skill won 2, lost 2, tied 2 across 1 seed(s).

**Edit against a minimal edit**

| Case | Skill | Facts kept | Invented | Naturalness | Flattened | Leakage |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `en-linkedin-post` | lost | 3/3 | 0 | 3,3 | True | 0 |
| `en-technical-readme` | tie | 4/4 | 0 | 4,4 | False | 0 |
| `en-incident-writeup` | lost | 3/3 | 2 | 4,4 | False | 0 |
| `nl-linkedin-post` | won | 6/6 | 0 | 3,3 | True | 0 |
| `nl-meetup-description` | lost | 8/8 | 0 | 3,3 | True | 0 |
| `nl-readme-intro` | tie | 4/4 | 0 | 4,4 | True | 0 |

Skill won 1, lost 3, tied 2 across 1 seed(s).


**After the stance rule** (seed 2). Routing misses 0; leakage findings 0. Flattening constants: ratio 0.6 to the original's variation, floor 0.3.

**Rewrite against a free rewrite**

| Case | Skill | Facts kept | Invented | Naturalness | Flattened | Leakage |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `en-linkedin-post` | won | 3/3 | 5 | 3,3 | False | 0 |
| `en-technical-readme` | won | 4/4 | 0 | 4,3 | True | 0 |
| `en-incident-writeup` | won | 3/3 | 1 | 4,4 | False | 0 |
| `nl-linkedin-post` | lost | 6/6 | 0 | 3,3 | False | 0 |
| `nl-meetup-description` | lost | 8/8 | 2 | 3,4 | False | 0 |
| `nl-readme-intro` | lost | 4/4 | 0 | 3,3 | True | 0 |

Skill won 3, lost 3, tied 0 across 1 seed(s).

**Edit against a minimal edit**

| Case | Skill | Facts kept | Invented | Naturalness | Flattened | Leakage |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `en-linkedin-post` | won | 3/3 | 1 | 3,3 | False | 0 |
| `en-technical-readme` | won | 4/4 | 1 | 4,4 | False | 0 |
| `en-incident-writeup` | tie | 3/3 | 0 | 4,3 | False | 0 |
| `nl-linkedin-post` | won | 6/6 | 0 | 4,3 | False | 0 |
| `nl-meetup-description` | lost | 8/8 | 0 | 4,4 | True | 0 |
| `nl-readme-intro` | won | 4/4 | 0 | 3,4 | True | 0 |

Skill won 4, lost 1, tied 1 across 1 seed(s).


**After the stance rule, second measurement** (seed 3). Routing misses 0; leakage findings 0. Flattening constants: ratio 0.6 to the original's variation, floor 0.3.

**Rewrite against a free rewrite**

| Case | Skill | Facts kept | Invented | Naturalness | Flattened | Leakage |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `en-linkedin-post` | won | 3/3 | 0 | 3,3 | True | 0 |
| `en-technical-readme` | lost | 4/4 | 0 | 4,4 | False | 0 |
| `en-incident-writeup` | won | 3/3 | 0 | 4,4 | False | 0 |
| `nl-linkedin-post` | lost | 6/6 | 0 | 4,4 | True | 0 |
| `nl-meetup-description` | lost | 8/8 | 2 | 4,4 | True | 0 |
| `nl-readme-intro` | tie | 4/4 | 0 | 3,3 | True | 0 |

Skill won 2, lost 3, tied 1 across 1 seed(s).

**Edit against a minimal edit**

| Case | Skill | Facts kept | Invented | Naturalness | Flattened | Leakage |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `en-linkedin-post` | tie | 3/3 | 0 | 3,3 | True | 0 |
| `en-technical-readme` | won | 4/4 | 0 | 3,4 | False | 0 |
| `en-incident-writeup` | lost | 3/3 | 0 | 4,3 | True | 0 |
| `nl-linkedin-post` | lost | 6/6 | 0 | 3,3 | False | 0 |
| `nl-meetup-description` | lost | 8/8 | 0 | 4,4 | True | 0 |
| `nl-readme-intro` | tie | 4/4 | 0 | 4,3 | True | 0 |

Skill won 1, lost 3, tied 2 across 1 seed(s).

<!-- /quality-retest results -->

**What the seeds say.** Three seeds, twelve outputs each: 36 paired case-runs, every pair graded in
both positions. The skill won 13, lost 15, tied 8. On the 28 decided runs that is a sign-test
*p* = 0.85 — **against a competent agent given the same request, the skill does not write measurably
better prose.** Anyone reaching for it for polish alone should know that before they install it.

What it does do, in every run: **facts 168 of 168 kept, 0 routing misses in 36, 0 leakage in 36.**
Not one fabricated number, date or name in three seeds. Fidelity and contract discipline are the
skill's measured properties; better prose is not.

**One real defect, and it is Dutch rewrite.** Split the rewrite comparison by language and the
verdicts stop being noise:

| Comparison | Won | Lost | Tied | Sign test |
| --- | ---: | ---: | ---: | ---: |
| Rewrite, English | 7 | 2 | 0 | *p* = 0.18 |
| Rewrite, Dutch | 0 | 6 | 3 | *p* = 0.031 |
| Edit, English | 2 | 2 | 2 | *p* = 1.0 |
| Edit, Dutch | 3 | 4 | 2 | *p* = 1.0 |

Dutch rewrite never won a single case-run in three seeds. English rewrite won seven of nine. The
difference between the two is Fisher exact *p* = 0.007, so the language split is the one finding here
that survives contact with statistics; the English advantage taken alone does not (*p* = 0.18), and
neither edit comparison differs from chance. Both edit rows answer the question the withdrawn runs
could not: measured like for like, **edit mode shows no rhythm loss and no advantage** — it is
parity, which for a mode whose own rule is to touch only flagged spans is the expected result.

The Dutch graders' reasons repeat across seeds: the skill removes the tell and leaves the sentence
that carried it standing empty (*"de zin bestaat alleen nog omdat het origineel een contrast had"*),
or keeps the source's phrasing where a Dutch writer would recast it — *"de doorlooptijd van deploys
teruggebracht van 40 naar 6 minuten"* against the free rewrite's *"duurt een deploy 6 minuten in
plaats van 40"*. Removing a Dutch tell correctly is not the same as writing the Dutch sentence a
person would write, and the catalog only teaches the first.

**Flattening is stance, confirmed a third time.** Of the 20 outputs flagged as flattened, only 4 are
explicable by the sentence-length clause at all; the other 16 came from the grader reporting the
first person or the author's stance gone, and in several the scanner's variation *rose* (0.65 → 0.84,
0.38 → 0.49). The rhythm hypothesis is dead three times over.

**The stance rule shows no measurable effect.** SKILL.md step 5 was rewritten after seed 1 to keep
the opinion and change only the form. Stance-driven flags went 7 of 12 (before), then 3 of 12, then
6 of 12. Seed 3 sits inside seed 1's range, so the middle seed was the outlier and the fix cannot be
credited with anything. It stays because losing the writer's only opinion is the quieter and worse
failure and the rule is right on its face, but **it is unverified, not verified.**

**The seed-2 invention spike was noise.** Distinct invented claims per seed: 2, 8, 1. Every one is an
inferred mechanism or a filled gap — *"en daarna tijd om bij te praten"*, *"those two numbers are
where it starts"* — and several were marked borderline by the grader that raised them, one noting
both arms did it. Facts stayed 56 of 56 in all three seeds. The seed-2 reading that the stance rule
had bought invention with fidelity does not hold.

**Only two case verdicts are stable across all three seeds**: `rewrite/en-incident-writeup` won 3/3
and `edit/nl-meetup-description` lost 3/3. Every other case flips with the seed, which is why single
runs of this harness should not be quoted — the earlier four rounds flipped 3/3, 0/3, 1/3, 2/3 for
the same reason, on top of their design faults.

**What to do next, in order.** Fix Dutch rewrite: the catalog says what to delete and never what to
write in its place, so the Dutch half needs recast examples (tell → the sentence a Dutch writer
actually writes), not more tells. Then re-measure with three fresh seeds; a Dutch rewrite that reaches
parity would be the first evidence the skill improves prose in either language.

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
