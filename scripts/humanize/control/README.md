# Control corpora

Human-written prose the merge agents run every candidate regex against. A regex that fires more
than twice per 10,000 words here is too broad and is tightened or dropped, so the scanner stays
quiet on writing a person actually produced.

| File | What | Committed |
| --- | --- | --- |
| `en-strunk-elements-of-style.txt` | Strunk, *The Elements of Style* (1918), public domain | yes |
| `en-twain-innocents-abroad.txt` | Twain, *The Innocents Abroad*, public domain, ~1.1 MB | no — run `./fetch.sh` |
| `nl-wikipedia-rijssen.wikitext` | Dutch Wikipedia, Rijssen, CC BY-SA 4.0 | yes |
| `nl-wikipedia-enschede.wikitext` | Dutch Wikipedia, Enschede, CC BY-SA 4.0 | yes |

Twain stays out of the repo for size; `fetch.sh` pulls it from Project Gutenberg and strips the
licence header. Strip the wikitext markup before matching against the Dutch files (double square
brackets, double braces, `ref` tags, apostrophe emphasis).

Two excerpts are cut from these into `skills/humanize/fixtures/` as the clean-prose test fixtures.
