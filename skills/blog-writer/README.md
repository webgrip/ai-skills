# blog-writer

A Claude skill for **technical blog posts that developers actually read** — the full pipeline
from raw project notes to published, syndicated post:

- **Frame before drafting** — post type (incident, how-we-built-X, opinion, tutorial, TIL),
  one specific reader, the one concrete lesson, and a realistic distribution path, locked
  before a word is written.
- **Evidence-first drafting** — first-hand specifics (numbers, logs, diffs, rejected
  alternatives) collected into `research.md`; every claim in the post traces back to it, and
  every code example is tested.
- **Hook workshop + skimmability** — 2–3 scored opening alternatives; headers that assert
  claims; the payoff in the first three sentences.
- **Single-dimension edit sweeps** — clarity → so-what → prove-it → specificity → de-AI-ify →
  read-aloud rhythm, with an anti-pattern catalog for AI tells that flags *clusters* without
  lobotomizing the author's voice.
- **Fresh-reader testing** — predict the cold reader's questions and objections before they
  show up in the comments.
- **Per-platform adaptation** — POSSE syndication with canonical URLs; native recipes and hard
  constraints for Hacker News, LinkedIn, Substack, dev.to, Hashnode, Medium, Reddit, and
  Lobsters, plus a publish checklist.

Distilled from the writers technical audiences cite (Julia Evans, Dan Luu, Simon Willison,
Michael Lynch, Patrick McKenzie, gwern, Scott Alexander…), engineering-org blog practice
(Oxide, Cloudflare), and the strongest published writing/humanizer skills. Sources are linked
in the reference files.

## Install

**`npx skills` (recommended — works in every agent, not just Claude):**

```bash
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git --skill blog-writer
```

**Claude Code plugin:**

```
/plugin marketplace add https://forgejo.webgrip.dev/webgrip/ai-skills.git
/plugin install blog-writer@webgrip-ai-skills
```

## Example prompts

- "I finally fixed that Longhorn rebuild wedge — help me turn my notes into a blog post."
- "Edit this draft so it doesn't sound AI-written, but keep my voice."
- "The post is live on Substack — get it ready for Hacker News, LinkedIn, and dev.to."
- "Which title and opening should I use for this incident writeup?"

## Files

| File | Contents |
| --- | --- |
| `SKILL.md` | The pipeline: frame → evidence → outline → draft → edit sweeps → reader test → adapt & publish |
| `craft.md` | Distilled craft rules with attribution, arc templates per post type, credibility levers |
| `edit-passes.md` | The sweep engine, the AI-anti-pattern catalog, false-positive guards, quantified checks |
| `platforms.md` | Per-platform constraints, community rules, canonical-URL mechanics, adaptation recipes, publish checklist |
