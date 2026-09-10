# Control corpus

Human-written prose the scanner is measured against. Provenance is the ground truth: every document
here was written by a person before large models could have written it, so every flag the scanner
raises on it is a false positive by construction. No judge, no labelling step.

`manifest.json` is the source of truth: one row per file with language, register, format, licence,
URL, whether it is committed, and a pinned revision id where the source is a wiki. `fetch.sh` fills
in whatever is missing (`--committed` for the rows the test suite needs, `--all` for everything);
fetched-only files live under `fetched/` and are gitignored.

## Registers

| Language | Register | Sources | Committed |
| --- | --- | --- | --- |
| en | literary | Strunk, *The Elements of Style*; Twain, *The Innocents Abroad* | Strunk |
| en | informal-discussion | English Wikipedia *Village pump (miscellaneous)* archives 58–62, 2018 | 60, 61 |
| en | technical | Six chapters of *The Rust Programming Language* at a December 2019 commit; the 2021 revisions of three English Wikipedia articles | all |
| nl | encyclopedic | Dutch Wikipedia *Rijssen*, *Enschede* | all |
| nl | informal-discussion | Dutch Wikipedia *De kroeg* daily archives, January 2019 | fifteen days |
| nl | technical | Dutch Wikibooks *Programmeren in Python* chapters | all |

Register is the unit of analysis, not language: the same regex can be quiet on encyclopedic prose
and loud on discussion. An `official` Dutch register (government and business copy) is still open;
rijksoverheid.nl renders its pages with JavaScript and could not be fetched with curl.

## How it is measured

`pipeline/fp_measure.py` cleans each file to plain prose with light Markdown (wikitext headings become
`## `, list markers become `- `, templates, references, tables and signatures are removed), then:

- **Regex hit rate**: hits per 10,000 words of the whole cleaned text, per language and per register.
- **Paragraph fraction**: the share of 50–400-word paragraphs with at least one hit, with a Wilson
  95% interval.
- **Structure gates**: the share of 300–700-word windows (sized like a rewrite output) on which a
  gate fires, with the same interval. Gates at `context` severity are reported but never fail: that
  severity means the register decides.

`--fail` turns three rules into an exit status: a regex over **2.0 hits per 10,000 words** in a
language with at least 10,000 words; a regex over **4.0** in a register with at least 5,000 words;
a cluster-severity structure gate whose interval's lower bound exceeds **5%** of windows
(encyclopedic, technical) or **10%** (informal, literary). The output names the id, the register,
the rate and example matches, so a regex can be tightened from the report alone.

`skills/humanize/test.sh` runs `fp_measure.py --committed --fail`; `pipeline/build.sh` runs it with
`--all --fail` after regenerating the pattern file. Two excerpts from these files are the clean-prose
fixtures in `skills/humanize/fixtures/`.

## What the first run found

The measure paid for itself on its first run over the widened corpus. `em-dash-density` fired 18.8
times per 10,000 words of human English (24 on Wikipedia discussion, 15 on the Rust book): a single
em dash is not evidence, so the id moved from a per-line regex to a density gate. A `^###` regex
meant to catch skipped heading levels fired on every third-level heading in the Rust book, because a
line cannot see the heading above it; it is a structure gate now. `paste-whitespace-residue-nl`
flagged `5 km`, which is correct Dutch typography, and `wordy-circumlocution` flagged *in order to*,
which is ordinary English. Each of those is a cue in the catalog and no longer a regex.
