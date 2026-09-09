# humanize

Detect and remove the tells of AI-generated writing, in English and Dutch, or keep them out
while drafting. One skill consolidates the catalogs of
[blader/humanizer](https://github.com/blader/humanizer),
[petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop),
[conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) and its regex
detector, the method of [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai), the
[Wikipedia field guide](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), and the
published lists of Ossama Badr (tropes.fyi), Ruben Hassid, Ivo Velitchkov, Matthew Vollmer, Will
Francis and Sean Goedecke. Attribution in [NOTICE.md](NOTICE.md).

The Dutch half is not a translation. It was built from Dutch sources, from the German sister
catalogs, from a transfer of every English entry into the form a Dutch model actually produces,
and from a translationese layer: the English-shaped Dutch (comma before *en*, unspaced em dash,
title-case headings, *duiken in*, *aan het eind van de dag*) that no English list can see.

**Install:**

```text
/plugin install humanize@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s humanize`.

## What it does

- **Detect**: report the tells in a text with ids, evidence and density, change nothing.
- **Edit**: minimal surgical pass on a draft the author wrote, voice kept.
- **Rewrite**: full pass on generated text, facts and quotes protected, meaning unchanged.
- **Write**: keep the tells out of a text being drafted now, by substitution rules rather than a
  banned-word list.

Register matters: a tell in a LinkedIn post is fine in a research summary, and the skill carries a
tolerance table per context. It matches the writer's voice from a sample when one exists. It never
adds facts, never bends meaning, and does nothing to fool a detector.

## Files

| File | What |
| --- | --- |
| [SKILL.md](SKILL.md) | The decisions and the eight-step procedure |
| [patterns-en.md](patterns-en.md) | The English catalog, by category, each entry with cues, an example, severity and false positives |
| [patterns-nl.md](patterns-nl.md) | De Nederlandse catalogus, in het Nederlands, met de translationese-laag |
| [method.md](method.md) | Modes, workflow, gates, the register tolerance table, voice matching, false positives, scoring, the substitution table, contested rules |
| [scripts/scan.py](scripts/scan.py) | Dependency-free scanner over its pattern file: matches per line, em-dash density, sentence-length variance; exit 1 on an `always` finding |
| [whats-new.md](whats-new.md) | The entries the consolidation added beyond what the house rule and the blog-writer pass already had |
| [evals/evals.json](evals/evals.json) | Trigger and output evals |

## Scanner

```bash
python3 skills/humanize/scripts/scan.py --lang auto docs/*.md
python3 skills/humanize/scripts/scan.py --json --fail-on cluster draft.md
```

Fenced code and blockquotes are skipped. The scanner finds what a regex can find; the catalogs
carry the structural patterns (uniform paragraphs, listicle prose, the aphoristic ender) that need
a reader. Wire it into a repo's check target to catch the next slogan before a person sees it.

## Example prompts

- "Humanize this. It reads like ChatGPT."
- "Maak dit even normaal, niet zo AI."
- "Is this slop? Don't edit, just tell me."
- "Rewrite the meetup description so it sounds like a person wrote it, keep every fact."
- "Scan the docs folder for AI tells."
