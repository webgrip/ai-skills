# humanize build pipeline

Everything the [`humanize`](../../skills/humanize) skill is generated from. None of this ships:
`build_dist.py` zips the skill directory, and this tree lives outside it.

**Mid-build:** the Dutch catalog is unfinished. [`HANDOFF.md`](HANDOFF.md) says what is done, what
is not, and what to run.

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
| `catalog/catalog-nl.json` | The Dutch equivalent. |
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
