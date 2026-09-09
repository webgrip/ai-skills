# Handoff: finishing the humanize skill

Written 2026-09-09, mid-build. The English half is finished and shipped; the Dutch half is
mid-merge. Everything needed to finish it is committed. Read
[`README.md`](README.md) for the layout, this file for what is done, what is not, and what to run.

## Where it stands

| Part | State |
| --- | --- |
| `skills/humanize/SKILL.md`, `method.md`, `README.md`, `NOTICE.md`, manifest | Done |
| `patterns-en.md` — 229 entries, 167 in the scanner as 716 regexes | Done, generated |
| `whats-new.md` — the 168 entries the house did not already have | Done, generated |
| `scripts/scan.py`, `scripts/patterns.json` | Done, English rows only |
| `fixtures/` — 2 clean, 2 slop, `en-slop.expect` | Done except `nl-slop.expect` |
| `evals/evals.json` — 6 cases, one should-not-trigger | Done |
| `test.sh` | Written; **cannot pass until the Dutch half lands** (it scans both catalogs) |
| `patterns-nl.md`, `catalog/catalog-nl.json` | **Not yet** — the merge was running when this was written |

The repo lint fails on exactly one thing: three links to `patterns-nl.md` that does not exist yet.
Nothing else is outstanding.

## Finish the Dutch half

1. **Check what the merge produced.** Per-category output lands in
   `catalog/nl-verified-<category>.json`, the consolidated catalog in `catalog/catalog-nl.json`.

2. **If the merge did not finish**, re-run it. It reads only committed files:

   ```
   Workflow({scriptPath: "scripts/humanize/workflows/merge-consolidate-nl.js"})
   ```

   Eight agents, one per category, each reading its own `extracts/nl/nl-raw-<category>.json`, then
   one consolidation agent. Regenerate the raw files with `python3 pipeline/split_nl.py` if you
   change the extracts.

3. **Build and test:**

   ```bash
   bash scripts/humanize/pipeline/build.sh nl
   cd skills/humanize && ./test.sh
   ```

4. **Write `fixtures/nl-slop.expect`** — the ids the Dutch slop fixture must trigger. Do it by
   hand from the tells deliberately written into `fixtures/nl-slop.md` (the *in de snel
   veranderende wereld* opener, *niet zomaar X, het is Y*, *laten we erin duiken*, the bold-stem
   bullets, *Experts zijn het erover eens*, *cruciaal*/*baanbrekend*/*benutten*, *Kortom*, the
   engagement question, the hashtags), then check the scanner finds each. An id it misses is a
   real coverage gap, not a reason to weaken the file: that is how the two English gaps were
   found.

5. **Sanity-read 30 entries as a native speaker.** The failure mode to hunt is a *Na:* example
   that is translated English or civil-service Dutch, and a cue that no Dutch model actually
   writes. This was originally a three-editor judge panel; it was cut for cost, so it is now a
   human read.

6. `npm run check && npm test`, then commit.

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
  and needs a headless Claude Code. The trigger phrasings in the description are untested.
- **`whats-new.md` is a one-shot artifact**, not regenerated by `build.sh`. If the catalog changes
  substantially it goes stale; the generator is a dozen lines and lives only in this session's
  history.

## What this cost

About 4M subagent tokens across three workflows: 17 English extractions and 8 category merges, then
5 Dutch extractions and transfers, then 8 Dutch merges. Two runs died on a session limit and one on
oversized prompts, which is why the merge agents now read their input from files instead of having
it inlined. The `extracts/` tree is the expensive part; treat it as irreplaceable.
