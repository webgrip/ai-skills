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

Measured, and the answer is qualified. Three realistic slop texts were rewritten twice — once by an
agent following this skill, once by an agent told only "make it sound human" — and graded blind by
a reader who did not know which was which, weighting fact fidelity above polish.

| | First run | After the fixes |
| --- | ---: | ---: |
| Cases the skill won | 0 of 3 | 2 of 3 |
| Facts invented | 3 | 0 |
| Naturalness (1-5) | 3, 3, 3 | 4, 4, 3 |
| Voice flattened | 3 of 3 | 2 of 3 |

The skill is reliably better on fidelity: it keeps every protected number and invents nothing, where
the naive baseline twice invented product behaviour to make a sentence read well. It is still worse
at rhythm. The remaining loss has one shape, and the graders name it the same way each time: the
skill removes a tell by deletion and leaves a stump where the content was, then returns uniformly
clipped declaratives. Three rounds of fixes moved that (return the text not the notes; rewrite
rather than delete; check the skeleton, not only the surface) without closing it.

The first run is what made the rest of this file honest. It found the skill shipping its own process
notes as the deliverable and quoting scanner counts it had never run — chatbot residue and
fabricated specifics, the two things the catalog exists to catch.

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
