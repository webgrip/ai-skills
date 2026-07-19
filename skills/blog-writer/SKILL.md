---
name: blog-writer
description: Write, edit, and syndicate technical blog posts through a full pipeline — evidence gathering, outline and hook workshop, drafting, single-dimension edit sweeps including a de-AI-ify pass, fresh-reader testing, and per-platform adaptation (Substack, LinkedIn, Hacker News, dev.to, Reddit, Lobsters, Medium, Hashnode). Use when writing or drafting a blog post, article, or writeup; turning project notes, an incident, a build log, or a TIL into a post; editing a draft to sound human and land with developers; picking a title or opening hook; adapting or cross-posting a post for LinkedIn, Hacker News, Substack, dev.to, or Reddit; planning where and when to publish; or reviewing a post before it ships.
---

# Blog writer — technical posts that developers actually read

Pipeline: **frame → evidence → outline → draft → edit sweeps → reader test → adapt & publish.**
Steps are sequential but re-entrant — a user arriving with a finished draft starts at edit sweeps;
one arriving with "help me post this to HN" starts at adapt. Work products live next to the draft:
`research.md`, `outline.md`, `draft-v1..vN.md`, per-platform variants.

## 1. Frame (before writing a word)

Lock these with the user; refuse to draft until they're concrete:

- **Post type** → arc template (all in [craft.md](craft.md)): incident/postmortem ·
  how-we-built-X · opinion · tutorial · TIL. Type drives structure and length.
- **One specific reader** — a person, not a demographic ("a platform engineer who runs Flux at
  work"), and the terminology that signals *this is for you*.
- **The one concrete lesson** — not "my experience with X" but the specific solved thing.
  If the user just struggled with something and solved it, that struggle IS the post.
- **Distribution path** — where will readers come from? Pick target platforms now
  ([platforms.md](platforms.md)); a post with no realistic route to readers needs reframing,
  not polish. Default flow: canonical home first, syndicate 2–10 days later, never verbatim.

## 2. Evidence

Collect first-hand specifics into `research.md` before outlining: numbers, timestamps, log
lines, diffs, benchmarks, screenshots, rejected alternatives and why, costs, "what I still
don't know". Every claim in the final post must trace to something here — evidence and caveats,
not bare assertions. Test every code example in a clean setup; a broken snippet costs more
credibility than no snippet. The unfakeable first-hand detail is what separates an engineer's
post from marketing — and from AI slop.

## 3. Outline + hook workshop

- Build the outline from the type's arc template. **Headers assert claims, not topics**
  ("The network said no — three times", not "Networking issues").
- **Skimmability test**: reading only headings + images must convey the whole arc and make the
  target reader curious. Restructure until it does.
- **TL;DR / payoff at the top.** Title + first three sentences must answer "is this for me?"
  and "what do I get?" — no throat-clearing, no scene-setting.
- **Hook workshop**: write 2–3 opening alternatives (bold claim · in-media-res moment ·
  surprising number), score each on curiosity / value-promise / specificity, present to the
  user with a recommendation.

## 4. Draft

Draft section by section against the outline, voice rules from [craft.md](craft.md) in force:
specifics over adjectives ("cut the image 2.1 GB → 1.12 GB", never "significantly smaller");
concrete example before abstract principle; say what you don't know; name the alternatives you
rejected; short varied paragraphs; minimal runnable code — key lines and diffs, not dumps.
Write in the *user's* voice: if a writing sample or prior post exists, read it first and match
register; periodically ask "does this sound like you?" — suggest, don't dictate. Match length
to goal: default short, cut scope rather than stall.

## 5. Edit sweeps — one dimension per pass

Run the sweeps in [edit-passes.md](edit-passes.md) in order: clarity → so-what → prove-it →
specificity → **de-AI-ify** (against the anti-pattern catalog — flag *clusters* of tells, never
lobotomize voice) → rhythm (read-aloud). After each sweep, spot-check that earlier sweeps
survived. **The user is never the first reviewer**: finish all sweeps before presenting a draft,
and present it with a short list of the judgment calls made, not a change log.

## 6. Reader test

Simulate the target reader meeting the post cold: list the questions they'd ask, the "you
should just do X" objections they'd raise, and where they'd stop reading. Fix gaps; preempt the
top objections in the text (one clause each, not a defensive essay). For high-stakes posts,
probe a genuinely fresh context (subagent that has only the draft) and harvest its confusions.

## 7. Adapt & publish

Per-platform recipes, constraints, canonical-URL mechanics, timing, and self-promo ratios →
[platforms.md](platforms.md). The invariants:

- **Canonical first.** Publish at the user's home platform; syndicate later with
  `rel=canonical` back. Every aggregator submission points at the canonical URL, never a rehost.
- **Adapt, never paste.** Each platform gets a native reframe (LinkedIn: standalone-value hook
  post; dev.to: dev-depth with `canonical_url` frontmatter; Reddit: context comment + author
  disclosure). Verbatim cross-posts read as spam and split SEO.
- Produce each variant as its own file next to the draft, plus a publish checklist with
  platform order and timing.

## Gotchas

- **HN and Lobsters ban AI-generated/AI-edited text** — submissions and comments; "AI-generated"
  is an HN flag reason. The de-AI-ify sweep is not cosmetic; a post that reads generated poisons
  the whole distribution chain. Disclose AI assistance where the author's norms call for it.
- **Never solicit votes** (HN/Reddit/Lobsters) — not in the post, not in DMs, not in a newsletter.
  Detection is automated and the penalty is the account, not the post.
- **LinkedIn depresses external links** (~25–35% reach; the link-in-comments workaround is dying).
  The LinkedIn variant must deliver value with no click; link via comment or post-distribution edit.
- **Titles for aggregators stay de-hyped** — HN mods retitle editorialized submissions; keep the
  original title, drop gratuitous numbers and superlatives.
- **No SEO ceremony.** Keyword density, E-E-A-T theater, schema blocks, "ultimate guide" framing —
  all push toward the formulaic content this skill exists to avoid. Write for the one reader.
