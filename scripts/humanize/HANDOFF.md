# Handoff: the humanize skill

Both halves are finished and the gates are green. Read [`README.md`](README.md) for the layout,
[`COMPARISON.md`](COMPARISON.md) for how it measures against the tools it was built from, and this
file for the decisions and the open ends.

## Where it stands

| Part | State |
| --- | --- |
| `skills/humanize/SKILL.md`, `method.md`, `README.md`, `NOTICE.md`, manifest | Done |
| `patterns-en.md` — 229 entries, 167 in the scanner as 716 regexes | Done, generated |
| `patterns-nl.md` — 251 entries, 209 in the scanner as 579 regexes | Done, generated |
| `whats-new.md` — the 168 entries the house did not already have | Done, generated |
| `scripts/scan.py`, `scripts/patterns.json` — 376 rows, 1,295 regexes | Done |
| `fixtures/` — 2 clean, 2 slop, both `.expect` files | Done |
| `evals/evals.json` — 6 cases, one should-not-trigger | Written, never run |
| `test.sh` | Passes |
| `npm run check && npm test`, `claude plugin validate` | Green |

Rebuild either half with `bash scripts/humanize/pipeline/build.sh <en|nl>`; the pipeline reproduces
the shipped files byte for byte from `catalog/`.

## If you pick this up

Two things are worth doing and neither blocks anything: run the evals, and give the Dutch catalog a
native-speaker read. Both are described under "Known gaps".

To rebuild or extend, see [`README.md`](README.md). One rule that is not obvious: **a `.expect`
file is written by hand, never from scanner output.** List the tells you deliberately put in the
fixture, then check the scanner finds each. An id it misses is a coverage gap worth fixing, and
that is how `Let's dive into`, the adjectival triad and the Dutch inflected adjectives were all
found.

## Decisions a successor should know

- **One skill, two catalogs.** Not two skills. The procedure is identical for both languages and
  belongs in one place, and the repo prefers merging over adding.
- **The Dutch catalog is not a translation.** It comes from 22 Dutch sources, the German sister
  catalogs, a transfer of every English entry into the form a Dutch model actually produces, and a
  translationese layer for English-shaped Dutch (comma before *en*, unspaced em dash, title-case
  headings, *duiken in*, *aan het eind van de dag*). No English list can see that layer.
- **Korean and Wikipedia-only entries stay in the catalog data and out of the rendered English
  markdown** (`scope: language-specific`). They are the template the Dutch translationese layer was
  built from, so deleting them costs the method.
- **Regexes are measured, not guessed.** Over two hits per 10,000 words of human prose is too
  broad. Structural patterns get no regex at all and rely on a reader.
- **Severity is three-valued** — `always`, `cluster`, `context` — and the register table in
  `method.md §4` decides how hard each is enforced. A tell in a LinkedIn post is fine in a report.
- **The skill never states an authorship verdict or probability.** It names patterns with quoted
  spans. Detectors misclassify second-language and neurodivergent writers wholesale.
- **No detector-bypass behaviour**, ever. Not zero-width characters, not deliberate typos.

## Known gaps and judgment calls

- **`false-range` only fires on three-part ranges.** A two-part *from X to Y* is not reliably
  separable from a legitimate range, so it is documented as a reader-judgment pattern.
- **`rule-of-three` regex coverage is deliberately narrow.** A general *X, Y, and Z* matcher hits
  ordinary prose constantly. It catches the padded adjectival form and leaves the rest to a reader.
- **The consolidation agent flagged five judgment calls** it wants a human to look at, including a
  negotiated split between `staccato-fragments` and `short-fragment-runs` that it overrode. Its
  full report is in the workflow result; the merges it made are listed per entry in `merged_from`.
- **The extracts contain Wikipedia-specific and fiction-specific entries** (`canned-profile-page`,
  `verse-form-defaults`, `pro-authoritarian-bias`). They are harmless but noisy for our use; nobody
  has decided whether to prune them.
- **`evals/evals.json` has never been run.** `python3 scripts/run_evals.py humanize` costs tokens
  and needs a headless Claude Code. The trigger phrasings in the description are untested. This is
  the largest open end.
- **The Dutch catalog has not had a native-speaker read.** A three-editor judge panel was cut for
  cost. The failure mode to hunt is a *Na:* example that is translated English or civil-service
  Dutch, and a cue no Dutch model actually writes. Roughly 30 entries spread across the categories
  would be a fair sample; start with `translationese` and `punctuation-format`.
- **The Dutch control corpus is two Wikipedia articles**, about 9,100 words of encyclopedic prose.
  The top Dutch AI adjectives score zero hits there, which is why they are in the scanner at cluster
  severity; a wider corpus (opinion, business, forum) would justify or refute that.
- **`whats-new.md` is a one-shot artifact**, not regenerated by `build.sh`. If the catalog changes
  substantially it goes stale; the generator is a dozen lines and lives only in this session's
  history.

## What this cost

About 4M subagent tokens across three workflows: 17 English extractions and 8 category merges, then
5 Dutch extractions and transfers, then 8 Dutch merges. Two runs died on a session limit and one on
oversized prompts, which is why the merge agents now read their input from files instead of having
it inlined. The `extracts/` tree is the expensive part; treat it as irreplaceable.
