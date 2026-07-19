# Edit sweeps — one dimension per pass

Editing everything at once catches nothing. Run these sweeps in order, each over the full
draft, fixing only that sweep's dimension. After each sweep, spot-check a paragraph or two
against the earlier dimensions — later rewrites regress earlier fixes. Adapted from the
seven-sweep copy-editing framework; tuned for technical posts.

## Contents

1. [The sweeps](#the-sweeps)
2. [De-AI-ify: the anti-pattern catalog](#de-ai-ify-the-anti-pattern-catalog)
3. [False positives — do not flag](#false-positives--do-not-flag)
4. [Personality and soul](#personality-and-soul)
5. [Quantified checks](#quantified-checks)

## The sweeps

1. **Clarity.** Every sentence parses on first read. Break long sentences at each new action or
   dependency. Undefined jargon either gets one clause of definition or gets replaced. Pronouns
   with ambiguous antecedents get named.
2. **So-what.** Each section must advance the one lesson. A paragraph that doesn't change what
   the reader knows, believes, or can do gets cut — especially the paragraph the author is
   proudest of. Kill the treadmill: restating an earlier point without new information.
3. **Prove-it.** Every claim traces to evidence in `research.md`: a number, a log line, a diff,
   a citation. Unverifiable claims get evidence, a caveat, or deletion. Hedge words
   (*seems, might, appears*) either become concrete or disappear.
4. **Specificity.** Replace every abstract quantifier with the real value: "significantly
   faster" → "430 ms → 80 ms"; "a large image" → "2.1 GB". Replace category words with the
   actual name. Specific numbers beat adjectives, everywhere, always.
5. **De-AI-ify.** Grep the draft against the catalog below. Flag clusters, rewrite by hand —
   never by find-and-replace, which produces a different flavor of slop.
6. **Rhythm (read-aloud).** Read the draft aloud (literally). Mark every stumble, every breath
   that runs out, every sequence of same-length sentences. Vary. Check paragraph lengths differ.
   End on the strongest close, not the last thing written.

## De-AI-ify: the anti-pattern catalog

The tell is never one item — it's density. Look for clusters.

**Openings & framing**
- Generic scene-setting: "In today's fast-paced world", "In the ever-evolving landscape of",
  "Imagine a scenario where", "In the realm of".
- Throat-clearing: "In this post, I will…", "Before we dive in…", "Let's explore".
- Conversational-cosplay openers: "Honestly?", "Look,", "Here's the thing:".

**Vocabulary**
- Buzz-verbs: *delve, navigate, unlock, unleash, leverage, harness, empower, elevate, foster,
  streamline, supercharge*.
- Latinate bias: *utilize→use, commence→start, demonstrate→show, facilitate→help,
  numerous→many, additionally→also*.
- Copula avoidance: "serves as", "acts as", "functions as", "features" where *is* or *has* works.
- Vague praise: *powerful, seamless, robust, cutting-edge, game-changing, revolutionary*.

**Structure**
- Symmetric everything: uniform paragraph lengths, rule-of-three lists in every section,
  suspiciously balanced pro/con pairs.
- Inline-header lists: bullet points of `**Term:** fragment` where flowing prose belongs.
- Aphorism formulas: "X is the Y of Z", "It's not about X, it's about Y".
- Em-dash saturation: humans average one per ~500 words; drafts running one per 50–80 words
  read generated. Thin them; keep the ones doing real work.
- Diff-anchored writing: describing things as changes from a previous state the reader never
  saw ("the improved version now handles…") instead of as they are.

**Substance (the biggest tell)**
- Perfect grammar + zero first-hand anecdote, opinion, or number only this author could supply.
- Excessive hedging and both-sides padding where the author plainly has a view.
- "Pull-quote-ready" over-polished lines in every paragraph.
- False agency: inanimate objects performing human actions ("the codebase invites you to…").

**The fix is additive, not just subtractive**: inject a first-hand detail, a real number, an
opinion, an admission of what's unknown — then cut the generic connective tissue around it.

## False positives — do not flag

- Formal vocabulary in genuinely formal contexts; correct grammar.
- A single em-dash, a single rule-of-three, one "delve" — isolated tells are noise.
- Quoted text, cited material, code comments, and examples: never rewrite someone else's words.
- Domain terms of art that look like buzzwords but are precise (e.g. "leverage" in finance).

Flag clusters; judge the whole; leave good prose alone.

## Personality and soul

Stripping tells produces clean prose; clean is not good. A post with uniform sentences, no
opinions, no first person, and no risk reads like documentation — or like an AI told to sound
human. For blog/opinion/essay content, the voice belongs in: stated opinions, humor where the
author would actually joke, first-person stakes ("this cost me an evening"), and the occasional
deliberately broken rule. Do not inject voice into reference material or other people's quoted
text. When in doubt about a colorful line the author wrote: keep it.

## Quantified checks

Light gates, not theater — run after the de-AI-ify sweep:

- **Em-dash density**: > 3 per 500 words → thin.
- **Sentence-length variance**: pick three consecutive paragraphs; if most sentences land
  within ±3 words of the mean, the rhythm is flat → vary.
- **First-hand quotient**: count concrete author-specific details (numbers, timestamps, named
  failures). A technical post with fewer than ~1 per section is running on generalities.
- **Buzz-phrase count**: grep the vocabulary lists above; more than a handful of hits across a
  post → the vocabulary sweep didn't finish.
