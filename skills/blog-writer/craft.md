# Craft — the rules that recur across the best technical-writing sources

Distilled from the writers technical audiences actually cite: Julia Evans, Simon Willison,
Dan Luu, Michael Lynch (*Refactoring English*), Patrick McKenzie, Steve Yegge, Gergely Orosz,
Hillel Wayne, gwern, Scott Alexander, plus engineering-org blogs (Oxide, Cloudflare, fly.io,
Tailscale) and postmortem practice. Source list at bottom.

## Contents

1. [Core rules](#core-rules)
2. [Arc templates by post type](#arc-templates-by-post-type)
3. [Titles, hooks, endings](#titles-hooks-endings)
4. [Credibility levers (the eng-blog test)](#credibility-levers)
5. [Length](#length)
6. [Sources](#sources)

## Core rules

1. **Answer "is this for me?" and "what do I get?" in the title + first three sentences.**
   The #1 failure mode is meandering — seven paragraphs of backstory before the point; the
   reader closed the tab at paragraph two. (Lynch)
2. **Payoff/TL;DR at the top; depth below.** gwern's iceberg: terse main line, detail pushed
   into asides, footnotes, appendices. Skimmers reading only headings + images must still get
   the whole arc. (gwern, Lynch)
3. **Write what you just struggled with, once solved.** Recent confusion is a map of what's
   worth explaining. Extract the concrete lesson — not "Rust is hard" but "what is a
   reference in Rust?". The "too obvious" post is usually the most useful one. (Evans, Dan Luu)
4. **More concrete examples than feels natural.** Examples stop readers from filling gaps with
   wrong interpretations — Dan Luu calls adding them his single biggest deliberate improvement.
   Concrete instance *before* abstract principle. (Dan Luu, Alexander, McKenzie)
5. **Evidence and caveats, not clean assertions.** Give readers the reasoning to evaluate,
   not conclusions to accept. Numbers with methodology beat adjectives every time:
   "cut reporting from 4 hours to 15 minutes" > "saves time". (Dan Luu, eng-org blogs)
6. **Say what you don't know.** "I don't know why X" builds trust and invites correction.
   Name the alternatives you considered and rejected — it preempts every "you should just
   use Y" comment. (Evans)
7. **One specific reader, your honest voice.** Write to a person (Vonnegut via Yegge), in the
   voice you'd use explaining it to them — not the sanitized school-essay register. Signal the
   audience through terminology they recognize; one swapped term can widen reach "one degree
   bigger" without diluting the post. (Yegge, Lynch)
8. **Headers assert claims, not topics.** "Engineers are hired to create business value, not
   to program things" — then the section defends its header. (McKenzie)
9. **Coin a concept handle.** A memorable name for the post's core idea ("trivial
   inconveniences", "dark factory") makes it portable — it's what readers quote. (Alexander)
10. **Short paragraphs, engineered variety.** End paragraphs early; alternate prose, code,
    tables, images; vary sentence length deliberately — rhythm is a feature, monotony a tell.
    (Alexander, Lynch)
11. **Minimal, runnable code.** Show the key lines or the diff, not the file. Every snippet
    tested in a clean setup before publishing. Every image earns its place by advancing
    understanding. (technical-writing practice)
12. **Ship before it's perfect.** Publish while still slightly unhappy — the flaws you see are
    invisible to readers; the post that never ships helps no one. Fix errors in place, fast.
    (Willison, Yegge, Evans)

## Arc templates by post type

**Incident / postmortem** — blameless, systems not people:
executive summary (what, why it matters, severity, duration) → timestamped timeline (readers'
eyes jump here first) → root cause + contributing factors → quantified impact → what changes.

**How-we-built-X** — what separates it from marketing is the honesty:
problem + constraints → what was tried and *rejected*, and why → the approach → concrete
implementation with numbers → what broke / what it cost → results and open trade-offs.

**Opinion / persuasion**:
claim up front → concrete grounding (anecdotes, numbers only this author could supply) →
steelman the counterargument, then answer it → memorable takeaway line.

**Tutorial** — optimize the learner's journey, not reference completeness:
audience + prerequisites + end state first → one clear path (don't branch) → runnable steps
with checkpoints ("you should now see…") → where to go next.

**TIL** — the lowest-friction format; publishing beats polish:
the problem (2–3 sentences) → the fix → one or two sentences of why it works. Often <300 words,
and that's the point — "here are my notes" framing lowers the bar enough to actually ship.

## Titles, hooks, endings

- **Titles state the payoff or the specific thing learned.** Honest framings ("How I…",
  "What is X?", "TIL: …", "Why we did X") set expectations and lower reader risk. Cute or vague
  titles hide the topic; save cleverness for a subtitle.
- **Hook patterns that work**: a bold-but-defensible claim · in-media-res (drop the reader into
  the moment: "At 07:39 UTC this morning, a bot opened PR #1…") · a surprising specific number.
  Score candidates on curiosity, value-promise, specificity.
- **Endings reinforce the one idea.** Close on the takeaway or an open technical question that
  invites reader *experience* ("what have you seen?" beats "what do you think?"). A soft pointer
  to RSS/newsletter is enough; manipulative CTAs undo the credibility the post just built.

## Credibility levers

Why Oxide/Cloudflare/fly.io/Tailscale posts read as engineering and not marketing — the test to
hold any draft against:

- Real implementation detail: versions, architectures, benchmarks *with methodology*, and the
  alternatives they rejected. Specificity is unfakeable.
- Written by the person who did the work, first person, willing to answer hard questions.
- Admits failure and cost. Willingness to look imperfect signals you're not selling.
- Useful to a reader who will never buy/use the author's product.
- No product pitch interrupting the technical thread — the depth *is* the marketing.

Marketing smell = abstract benefit language, superlatives without evidence, no rejected
alternatives, no author on the hook.

## Length

Two valid poles: **short and shipped** (half of Julia Evans' posts are under 500 words) and
**long and definitive** (Dan Luu, gwern) — when the goal is the exhaustive treatment of a hard
topic. Match length to goal; when in doubt, cut scope rather than delay. Wanting to include
everything is why posts never ship.

## Sources

- Julia Evans — [tactics for writing in public](https://jvns.ca/blog/2023/08/07/tactics-for-writing-in-public/) · [blog about what you've struggled with](https://jvns.ca/blog/2021/05/24/blog-about-what-you-ve-struggled-with/) · [blogging myths](https://jvns.ca/blog/2023/06/05/some-blogging-myths/)
- Simon Willison — [What to blog about](https://simonwillison.net/2022/Nov/6/what-to-blog-about/)
- Dan Luu — [Some thoughts on writing](https://danluu.com/writing-non-advice/)
- Michael Lynch — [Write blog posts developers read](https://refactoringenglish.com/chapters/write-blog-posts-developers-read/)
- Steve Yegge — [You Should Write Blogs](https://sites.google.com/site/steveyegge2/you-should-write-blogs)
- Patrick McKenzie — [Don't Call Yourself a Programmer](https://www.kalzumeus.com/2011/10/28/dont-call-yourself-a-programmer/) (structure exemplar)
- Gergely Orosz — [Postmortem best practices](https://blog.pragmaticengineer.com/postmortem-best-practices/)
- Hillel Wayne — [Problems with the four-document model](https://www.hillelwayne.com/post/problems-with-the-4doc-model/)
- gwern — [Style guide](https://gwern.net/style-guide)
- Scott Alexander — [Nonfiction writing advice](https://slatestarcodex.com/2016/02/20/writing-advice/)
- Oxide — [RFD 1: Requests for Discussion](https://oxide.computer/blog/rfd-1-requests-for-discussion) (writing-first eng culture)
