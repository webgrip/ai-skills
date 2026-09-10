# English catalog, domain-scoped entries (Wikipedia, fiction)

One entry per pattern: what it is, the literal cues, one before/after, the severity tier and when not to flag it. Severity: **always** (one hit is enough), **cluster** (a tell only in density or co-occurrence), **context** (register decides). Regex-detectable cues are also in `scripts/patterns.json` under the same id.

Contents: [Rhetorical moves and tone](#rhetorical-moves-and-tone) (1) · [Paragraph and document structure](#paragraph-and-document-structure) (3) · [Punctuation and formatting](#punctuation-and-formatting) (1) · [Content and evidence](#content-and-evidence) (4) · [Machine residue](#machine-residue) (3)

## Rhetorical moves and tone

### Review-process deflection (defending contested text) `review-process-deflection`

Severity: **cluster** · Scope: universal

When the provenance or quality of a contribution is questioned, the reply argues about the process instead of the text: asking the critic to identify precisely what is wrong ('please point out exactly which parts', 'let me know which parts'), dismissing the concern as unproven ('unsubstantiated speculation', 'without explaining how they are substantively flawed'), redirecting to collaboration ('let's focus on improving the content', 'Let's work together to strengthen the article rather than engage in unnecessary conflict'), and announcing that an edit addressed reviewer feedback ('Addressed reviewer feedback by improving sourcing, formatting, and neutrality'). Answer the substance instead.

Cues: `please point out exactly` · `let me know which parts` · `help me determine what I need to improve` · `unsubstantiated speculation` · `speculation about motive` · `without explaining how they are substantively flawed` · `let's focus on` · `I urge you to focus on constructive dialogue` · `Let's work together to strengthen the article` · `rather than engage in unnecessary conflict` · `Addressing reviewer feedback` · `Addressed reviewer feedback` · `Rewrote from scratch per reviewer feedback`

Before: I urge you to focus on constructive dialogue and respect for all contributors. Let's work together to strengthen the article rather than engage in unnecessary conflict.

After: Two of the three sources do not mention the subject; I have replaced them with the 2019 provincial register.

Do not flag: Asking a reviewer to be specific is reasonable once, especially when the critique was a bare label. A changelog line naming what changed is good practice ('replaced two dead links'); the tell is the announcement with no diff behind it. Outside Wikipedia the same moves show up in pull-request replies.

## Paragraph and document structure

### Canned profile page `canned-profile-page`

Severity: **cluster** · Scope: english

A profile or bio page following a fixed template: headings like 'Welcome To My User Page!', 'About Me', 'My Interests', 'My Contributions', 'Let's Connect!', inline-header bullets with an emoji per item, bold or Markdown-bold counts ('20+ articles'), and a cheerful sign-off ('Happy Editing! 🚀'). The same shape appears on GitHub and LinkedIn bios. Rewrite as two or three plain sentences about what the person actually does.

Cues: `Welcome To My User Page!` · `About Me` · `My Interests` · `Let's Connect!` · `Let's Collaborate` · `My Contributions` · `Feel free to leave a message on my` · `if you have any suggestions, questions, or would like to collaborate` · `Happy Editing! 🚀`

Before: == ✨ About Me ==
* 🖊️ I enjoy writing about Indian cinema, culture, and history.
* 📚 I ensure accuracy by citing reliable sources.

== 🏆 My Contributions ==
* Created and improved '''20+ Wikipedia articles'''

== 💬 Let's Connect! ==
Feel free to leave a message on my **[[User talk:Example|Talk Page]]** if you have any suggestions, questions, or would like to collaborate.

'''Happy Editing! 🚀'''

After: I write about Indian cinema and its history, mostly the Telugu industry of the 1980s. Twenty-odd articles so far; the talk page is open.

Do not flag: A single 'About me' heading on a personal site; the tell is the full template with emoji bullets and the sign-off. Markdown bold inside wikitext is the strongest single giveaway.

### Narrative defaults (POV lock, flat pacing, tidy resolution) `narrative-flatness`

Severity: **cluster** · Scope: universal

Fiction that picks one narrative lane and stays in it with unnatural consistency (no drift between free indirect style, interior monologue and exterior scene), unfolds every scene at the same rate (no elision, selective summary or acceleration), and ties every ending up because the model does not trust the reader with ambiguity unless told to. Let the point of view drift, summarise the dull stretch, and leave one thread open.

Before: (every scene rendered at the same pace from the same fixed distance, ending with every question answered)

After: (the journey summarised in a sentence, the arrival in a page, one question left with the reader)

Do not flag: Genres that require a fixed point of view or a closed ending (procedurals, children's fiction, some romance); a short story that is a single scene.

### Verse form defaults (poetry) `verse-form-defaults`

Severity: **cluster** · Scope: english

Poetry that falls into the model's defaults regardless of the request: rhyme where none was asked for, four-line stanzas across forms, iambic meter by default, and superficial fidelity to a form (a 14-line 'sonnet', a 19-line 'villanelle', a 39-line 'sestina' that honours the line count but not the internal rule). Formal gestures without formal follow-through; generated poetry is far more constrained and uniform than human poetry.

Cues: `sonnet` · `villanelle` · `sestina`

Before: A 39-line 'sestina' whose six end-words never rotate, in rhymed iambic quatrains.

After: Either rotate the end-words through all six stanzas and the envoi, or do not call it a sestina; drop the rhyme unless it was asked for.

Do not flag: Poems that were asked to rhyme, scan or use quatrains; traditional forms where those are the rule. The evidence base is English (Walsh, arxiv 2410.15299); recalibrate per language.

## Punctuation and formatting

### Parenthetical stage directions in dialogue `parenthetical-stage-directions`

Severity: **always** · Scope: universal

Dialogue tagged with a bracketed emotion before the line, script-style ('Bob: (defensive) Why should I?'), in prose that is not a screenplay. Especially GPT-3.5. Carry the emotion in the words or a beat of action instead.

Cues: `(defensive)` · `(frustrated)`

Before: Bob: (defensive) Why should I? / Tony: (frustrated) Look…

After: Bob crossed his arms. "Why should I?" Tony rubbed his eyes. "Look..."

Do not flag: Actual screenplays and stage scripts; interview transcripts that mark (laughs); role-play or table-read formats the user asked for.

## Content and evidence

### Cliche, purple prose, no subtext `cliche-and-purple-prose`

Severity: **cluster** · Scope: universal

Stock phrasing and over-ornamented description with nothing beneath the surface: everything the text means is stated on the page, no layer sits under the dialogue or the image, and the ornament substitutes for observation. Expert readers name this cluster (cliches, purple prose, too much exposition, absent subtext) as how they recognise machine fiction.

Cues: `heart pounded like` · `a single tear` · `traced its way down` · `porcelain cheek` · `she would never be the same again` · `little did she know` · `a mixture of fear and` · `the weight of the moment`

Before: Her heart pounded like a drum as a single tear traced its way down her porcelain cheek, and she knew in that moment that she would never be the same again.

After: She read the message twice, put the phone face down, and went back to loading the dishwasher.

Do not flag: Genre fiction runs on shared convention, and a cliche used knowingly can be exact. Some traditions prize ornament (baroque, gothic, certain lyric essays). Fine-tuned models suppress these tells, so their absence says nothing about authorship, and their presence in a first draft is ordinary human beginner writing.

### Flat dialogue and as-you-know-Bob exposition `flat-dialogue-and-exposition`

Severity: **cluster** · Scope: universal

Characters are interchangeable: no distinct idiolect, verbal tic, dialect or pattern of evasion separates one speaker from another, and speech carries information the speakers already share so the reader can hear it. Mysteries resolve through explanation rather than action. Give each speaker a way of talking, and let events rather than briefings carry the plot.

Before: "As you know, Doctor, the reactor was built in 1974 and has never been serviced," she said.

After: "Nineteen seventy-four," she said. "Nobody's opened it since." He already knew. He let her say it anyway.

Do not flag: Some registers flatten speech on purpose: procedural drama, courtroom transcript, minimalist fiction where the sameness is the point, and translated dialogue that lost its dialect on the way. Expository dialogue is a genre convention in radio drama and in children's writing. Judge across a whole scene rather than a single line.

### Mood-saturated setting (pathetic fallacy) `pathetic-fallacy-mood-setting`

Severity: **cluster** · Scope: universal

Weather, rooms and objects exist only to mirror a character's feeling: rain that matches grief, a room that is cold because the marriage is. The setting carries no independent fact, so it stops being a place. Let the setting be itself and let the emotion come from what happens in it.

Cues: `mirroring her unspoken grief` · `pattered softly against the window`

Before: The rain pattered softly against the window, mirroring her unspoken grief.

After: It rained. She kept the window open anyway, because the room smelled of his tobacco.

Do not flag: Pathetic fallacy is a legitimate literary device with a long history, used deliberately by Hardy, Bronte and most gothic fiction. Poetry uses it as a mode. Flag when it is the only thing the setting does, and when every environmental detail in the piece tracks the emotional beat.

### Pro-authoritarian framing `pro-authoritarian-bias`

Severity: **context** · Scope: universal

On political topics, generated text leans toward state-media framing, criticises the governments of freer countries more readily than repressive ones, and sometimes declines on safety grounds where the safety concern runs one direction. Observed more strongly in Chinese-language responses than English as of 2026. Check political framing against independent reporting before publishing it.

Before: The region has seen significant development and improved stability under the current administration's guidance.

After: Name who reports the development and who reports the stability, and cite the sources behind each claim.

Do not flag: Neutral phrasing about an authoritarian state is often correct encyclopedic tone, and criticism of a democracy is not bias. The pattern is a corpus-level tendency reported in 2026 press coverage, not a verdict on any single sentence. Language-model refusals also have many other causes.

## Machine residue

### Placeholder value in a structured field `placeholder-in-metadata-field`

Severity: **always** · Scope: universal

A citation, infobox or front-matter field holding a stub instead of a value: 'url=URL', 'INSERT_SOURCE_URL_30', 'SOURCE_PUBLISHER', 'PASTE_SPOTIFY_TRACK_URL_HERE', date stubs such as '2025-XX-XX' or '2022-11-XX' (usually in access-date, sometimes in date, and they raise tool errors), and hidden comments that defer content in a field ('<!-- Add if available with citation -->', instructions to upload an image). A numbered stub token means the reference list was generated without the sources, so the whole citation is suspect and not only the field.

Cues: `access-date=2025-XX-XX` · `date=2022-11-XX` · `url=URL` · `INSERT_SOURCE_URL_30` · `SOURCE_PUBLISHER` · `PASTE_SPOTIFY_TRACK_URL_HERE` · `PASTE_YOUTUBE_VIDEO_URL_HERE` · `XX/XX/2025` · `<!-- Add if available with citation -->` · `if/when sources are available` · `upload images to Wikimedia Commons`

Before: {{cite web |url=INSERT_SOURCE_URL_30 |publisher=SOURCE_PUBLISHER |date=2022-11-XX}}

After: (citation deleted; nothing behind it was ever consulted)

Do not flag: Boilerplate comments that ship inside a template ('Add spouse if reliably sourced' in a military-person infobox) belong to the template, so check the template before citing this. A schema field genuinely named URL, and an access date that is old because the work is old, are not stubs. Whoever wrote it, a date with XX in it is an error worth fixing.

### Templated change note (commit message, PR description, edit summary) `templated-change-note`

Severity: **cluster** · Scope: universal

A change description written as exhaustive procedural prose rather than a terse human note. Sub-forms: the full-sentence summary of everything done and how it complies ('Improved clarity, flow, and readability of the plot section; reduced redundancy and refined tone for better encyclopedic style'); the statement of what was deliberately not changed, which echoes the prompt's constraint back ('while preserving the original meaning and technical details', 'while maintaining backward compatibility'); the enumeration of every field, parameter or template touched with its literal syntax ('Corrected infobox parameters (image_size)'); and the older first-person form carrying the same tells as the body text, with AI vocabulary, emoji or Markdown in the summary itself ('**Concise edit summary:** I revised the content to...'). The more rigidly formulaic, the stronger the sign.

Cues: `Improved clarity, flow, and readability` · `reduced redundancy and refined tone for better encyclopedic style` · `Reorganized article per` · `Comprehensive rewrite:` · `Comprehensive formatting update:` · `while preserving the original meaning and technical details` · `preserved existing structure and lead emphasis` · `preserved references and categories` · `while preserving sourced criticisms` · `infobox parameters (image_size)` · `Corrected infobox parameters` · `while maintaining backward compatibility` · `**Concise edit summary:**` · `I revised the content to` · `The tone was adjusted to be more encyclopedic and less promotional` · `for a more neutral tone`

Before: Improved clarity, flow, and readability of the plot section; reduced redundancy and refined tone for better encyclopedic style.

After: ce plot

Do not flag: A long, specific change note that says what changed and why, with links, is good practice: length and formality are not the tell, the formula is. Conventional-commit bodies, changelogs and release notes are meant to enumerate. 'While maintaining backward compatibility' is worth saying once, when it is the point of the change; the tell is the same constraint echoed on every commit. The further a summary deviates from the formula, the less likely it is generated, and a summary written by hand for a generated change is rare enough to ignore. Self-certification-of-compliance covers the neighbouring case, a change note that asserts its own neutrality or rule-conformance; read the two together on one edit summary and report it once.

### Throwaway rewrites to inflate a record `permissions-gaming`

Severity: **context** · Scope: universal

Many benign-looking, unconstructive AI rewrites across unrelated pages in quick succession, made to build an edit count or contribution record before pursuing a different goal. The individual edits look harmless; the volume, the spread and the timing are the signal.

Before: Forty small rewrites across forty unrelated articles in one evening, none changing a fact.

After: Reviewed as a pattern rather than edit by edit, and raised with the contributor before any action.

Do not flag: The inference runs one way only: rapid AI-assisted additions are not evidence of gaming, while a contributor already shown to be gaming permissions may well be using AI for the volume. Gnomes, typo-fixers and bot-assisted cleanup make many small edits legitimately. Newcomer enthusiasm looks the same from outside. This is evidence about a contributor's record rather than about any sentence, so like out-of-text-provenance-signal it never justifies a text edit. The two differ in reach: that entry reads how one document arrived, this one reads a pattern across unrelated pages.
