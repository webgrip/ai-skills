# humanize build pipeline

Everything the [`humanize`](../../skills/humanize) skill is generated from. None of this ships:
`build_dist.py` zips the skill directory, and this tree lives outside it.

[`HANDOFF.md`](HANDOFF.md) carries the decisions and the open ends; [`COMPARISON.md`](COMPARISON.md)
measures the result against the tools it was built from.

`skills/humanize/patterns-en.md`, `patterns-nl.md` and `scripts/patterns.json` are **generated**.
Edit `catalog/catalog-<lang>.json` (or `pipeline/additions.json`) and rebuild; never hand-edit the
generated files, they are overwritten.

## Rebuild

```bash
bash scripts/humanize/pipeline/build.sh en
bash scripts/humanize/pipeline/build.sh nl
cd skills/humanize && ./test.sh
```

The build cleans the catalog, applies hand-verified additions, renders the markdown and merges the
scanner's pattern file for that language, leaving the other language untouched.

## Layout

| Path | What |
| --- | --- |
| `catalog/catalog-en.json` | 229 canonical English entries. The source of truth for `patterns-en.md`. |
| `catalog/catalog-nl.json` | 251 canonical Dutch entries, 218 mapped onto an English id. |
| `catalog/nl-verified-<category>.json` | Per-category Dutch merge output, before cross-category dedup. |
| `catalog/methodology-raw.md` | The synthesised procedure with its per-source provenance brackets, before they were stripped into `skills/humanize/method.md`. |
| `pipeline/clean.py` | Drops junk cues (bare function words, foreign script, over-long), house-specific references and duplicate ids. |
| `pipeline/apply_additions.py` | Merges `additions.json` and dedupes ids across categories. |
| `pipeline/render.py` | Catalog JSON to markdown, and to the scanner's pattern rows. |
| `pipeline/split_nl.py` | Regenerates `extracts/nl/nl-raw-<category>.json` from the Dutch extracts. |
| `pipeline/additions.json` | Hand-verified extra cues, regexes and per-entry flags. The only place to add a pattern by hand. |
| `extracts/en/`, `extracts/nl/` | The structured output of every extraction agent. Irreplaceable: regenerating cost about 4M subagent tokens. |
| `control/` | Human-written prose every candidate regex is measured against. See its README. |
| `baseline/house-copy-rule.md` | What the estate already banned, so `in_baseline` and `whats-new.md` mean something. |
| `sources/` | Manifest and fetch script for the upstream repos and articles. Fetched content is gitignored. |
| `workflows/` | The Workflow scripts that produced the extracts. |

## Adding or changing a pattern

1. A new cue or regex on an existing entry, or a per-entry flag: `pipeline/additions.json`. The id
   must already exist or the build fails loudly.
2. A new entry, or a changed definition, example, severity or false-positive note:
   `catalog/catalog-<lang>.json`.
3. Rebuild and run `skills/humanize/test.sh`.

Every regex is measured against `control/` before it lands: more than two hits per 10,000 words of
human prose means it is too broad, and it gets tightened or dropped with the cue kept as prose.
The test suite enforces the other half — the catalog's own rewritten examples must stay free of
the tells the catalog names.

## Re-running an extraction

`workflows/extract-consolidate-en.js` and `workflows/extract-transfer-nl.js` read fetched sources,
so run `sources/fetch.sh` first. `workflows/merge-consolidate-nl.js` reads only committed files and
runs as is. All three are Workflow-tool scripts, not standalone node programs.

## Output-quality gate (on demand, costs tokens)

`workflows/quality-retest.js` is the with/without head-to-head: English and Dutch slop texts, each
rewritten by an agent with the skill and by an agent given only the user's request, graded blind by a
native-reader persona per language, with rhythm loss measured by the scanner rather than judged.
Run it after any change to `SKILL.md`, `method.md`, a severity in the catalog, or the scanner
metrics, from the Workflow tool with `args: { seed: N }` (the seed sets A/B order; use a new one per
run, and run three seeds before believing a number). It is not in CI: one run is 54 agent calls.

**A single case verdict is not a signal.** Measured over three seeds, ten of the twelve case verdicts
flip with the seed, so a case that was won and is now lost is the expected behaviour of the harness,
not a regression. Judge on the invariants and the per-language split instead. A regression is any of:
a protected fact lost or invented, `leakage` non-zero for any skill-arm output, a routing miss, or a
per-language comparison (rewrite/edit × en/nl) moving against the skill across three seeds. Record
the seed's result JSON in `quality/seed<N>.json`, render the tables with
`workflows/render_results.py`, and revise the interpretation in `COMPARISON.md` against every seed
you have, not only the newest.
