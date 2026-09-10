# English catalog: the tells, by category

One entry per pattern: what it is, the literal cues, one before/after, the severity tier and when not to flag it. Severity: **always** (one hit is enough), **cluster** (a tell only in density or co-occurrence), **context** (register decides). Regex-detectable cues are also in `scripts/patterns.json` under the same id.

Entries that only make sense on Wikipedia or in fiction are held in the catalog data and rendered separately in the domains file next to this one; the scanner loads them only with --domain.

Contents: [Sentence constructions](#sentence-constructions) (26) · [Rhetorical moves and tone](#rhetorical-moves-and-tone) (39) · [Vocabulary](#vocabulary) (35) · [Paragraph and document structure](#paragraph-and-document-structure) (24) · [Punctuation and formatting](#punctuation-and-formatting) (21) · [Content and evidence](#content-and-evidence) (27) · [Machine residue](#machine-residue) (20)

## Sentence constructions

### False range (from X to Y) `false-range`

Severity: **always** · Scope: universal

'From X to Y' is used where X and Y are not endpoints of any real scale, so the phrase implies a span with a meaningful middle that does not exist ('from the Big Bang to dark matter', 'from ancient civilizations to modern startups', 'From innovation to implementation to cultural transformation'). The Korean paradigm-shift formula 'X에서 Y로 / X을 넘어 Y로' is the same move. Ask what sits between X and Y; if nothing does, list the actual topics or pick the one that matters.

Cues: `from X to Y` · `From ... to ... to ...` · `from the singularity of the Big Bang to the grand cosmic web` · `from the Big Bang to dark matter` · `from ancient civilizations to modern startups`

Before: Our journey has taken us from the singularity of the Big Bang to the grand cosmic web, from the birth and death of stars to the enigmatic dance of dark matter.

After: The book covers the Big Bang and star formation, and ends with current theories about dark matter.

Do not flag: A genuine range with a real scale is not this pattern: 'from 1990 to 2005', 'from beginner to expert', 'from Paris to Rome'. Legitimate 'from X to Y' implies a spectrum with a meaningful middle; the test is whether anything sits between the endpoints.

### Inanimate agent doing a human verb (false agency, personified abstraction) `inanimate-agent`

Severity: **always** · Scope: universal

An abstraction or object is made the grammatical subject of a verb only people perform: 'the data tells us', 'the codebase invites you to', Korean '기술이 묻는다' (technology asks), '시대가 부른다' (the era calls). Rewrite with the person or organisation that acted, or weaken the personifying verb.

Cues: `the data tells us` · `the research argues` · `the algorithm decides` · `the market demands` · `the technology asks` · `history reminds us` · `the code wants` · `the codebase invites you to`

Before: The data tells us the launch failed.

After: The data shows the launch failed.

Do not flag: Conventional metaphors with a fixed technical meaning stay ('the function returns', 'the server listens', 'the study shows'). The milder 'abstract subject + generic verb' form is a separate, weaker signal; the tell is a human act (asks, calls, invites, decides) performed by a concept. 'The decision emerged after weeks of discussion' is the weaker abstract-subject form and is not a hit: decisions, patterns and consensus emerge in ordinary English.

### Negation countdown and negation chains (No X. No Y. Just Z.) `negation-countdown`

Severity: **always** · Scope: universal

Two or more negated items are stacked before the affirmed answer, performing decisiveness by clearing away options nobody proposed. Sub-forms: the fragment countdown ('Not a bug. Not a feature. A fundamental design flaw.', 'No X. No Y. Just Z.', Dutch 'Geen X. Geen Y. Gewoon Z.'), the sentence-initial 'no' chain ('No fluff, no filler, no jargon.'), the full-sentence countdown ('It's not the price. It's not the features. It's the trust.'), elided-subject 'didn't X, didn't Y' chains, the negated-then-repeated verb ('Don't call it a pivot. Call it a correction.'), and the negation-tricolon armature ('not A, not B, not C; but X, Y, and Z'). Say what the thing is; one negation earns its place only when the reader would otherwise assume the opposite.

Cues: `Not a X. Not a Y. A Z.` · `Not X. Not Y. Just Z.` · `Not ... Not ... A ...` · `not ..., not ..., but ...` · `No X. No Y. Just Z.` · `No ... No ... Just` · `Geen X. Geen Y. Gewoon Z.` · `no ..., no ..., just ...` · `It's not the price. It's not the features. It's the trust.` · `No fluff, no filler, no jargon.` · `It didn't ask. It didn't wait.` · `It didn't ask, didn't wait.` · `Don't call it a pivot. Call it a correction.` · `Don't call it X. Call it Y.` · `no X, no Y` · `not A — not B — not C; but X, Y, and Z` · `Not X. Not Y. Z.` · `No fluff. No filler. No stress.`

Before: No fluff, no filler, no jargon.

After: Every section states a fact you can check.

Do not flag: Mid-sentence factual inventories are content, not a reveal ('the endpoint takes no arguments, no headers, and no body'; 'no dependencies, no telemetry' in a spec list). Sequential narration with the subject restated is ordinary prose ('I did not sleep well. I did not eat breakfast.'). Idiomatic pairs stay ('no more, no less', 'no matter what'). Two-item chains are a judgment call; the detector fires only on sentence-initial chains of three or more short items and on comma-joined elided-subject 'didn't' chains. On hard-wrapped source files a line break can put a mid-sentence clause at what looks like a line start, so check that a line-start match really begins a sentence. A negated triad set as fragments ('No fluff. No filler. No stress.') is this pattern and is reported here only, not again under rule-of-three or staccato-fragments.

### Participial tail (superficial -ing analysis) `participial-tail`

Severity: **always** · Scope: universal

A trailing present-participle clause is bolted onto a plain fact to supply an interpretation the source does not provide: significance ('underscoring the importance of', 'highlighting the need for'), a trend ('reflecting a broader trend toward', 'marking a significant shift in'), legacy or symbolism ('symbolizing', 'showcasing', 'contributing to the region's rich cultural heritage'), or a purpose ('ensuring', 'fostering'). Finite-verb forms ('This highlights the enduring legacy of') are the same move. The construction survives explicit neutrality prompts. Cut the clause, or turn its claim into a separate sentence with a source and a concrete effect. The concrete effect must come from the source; where the source supplies none, cutting the clause is the whole fix.

Cues: `, emphasising` · `, emphasizing` · `, symbolising` · `, symbolizing` · `, showcasing` · `, contributing to` · `, ensuring` · `, fostering` · `, cultivating` · `, encompassing` · `, enhancing` · `, cementing` · `, solidifying` · `, demonstrating` · `, illustrating` · `, signalling` · `, reinforcing` · `, embodying` (+9)

Before: The launch adds file search, highlighting the team's commitment to better workflows.

After: The launch adds file search.

Do not flag: Participle clauses that describe a real, concurrent action are not this pattern ('running the tests, she found the leak'; 'reflecting the light off the water'). The tell is interpretive content in the -ing clause: an evaluation, a trend, a legacy or an unsourced purpose. An attributed, sourced statement of significance in its own sentence is fine. The lexical tells that travel with this construction ('valuable insights', 'align with', 'resonate with', 'transformative power', 'rich cultural heritage', 'dynamic hub') are vocabulary-category items and are reported there, not here.

### Rhetorical self-question (The result? Devastating.) `rhetorical-self-question`

Severity: **always** · Scope: universal

The writer poses a question to themself and answers it, or fires questions as a stalling device. Sub-forms: the answered self-question ('The result? Devastating.', 'Would I go back? Absolutely.', 'And the food? Simply divine.'), the transition opener ('So why should you care?', 'But what does this mean for developers?', 'One might wonder:'), the fake-casual self-QA volley ('Is it fast? Yes. Is it cheap? Also yes.'), and the stacked question chain ('Do I know how it works? Where it breaks? Which corners it cut?'). Convert to a direct statement; if you know the answer, say it, and keep at most one question that a strong setup has earned.

Cues: `Would I go back? Absolutely.` · `And the food? Simply divine.` · `Is it worth the price? Honestly?` · `Is it fast? Yes. Is it cheap? Also yes.` · `But what does this mean for developers?` · `So why should you care?` · `What's next? answered in the same paragraph, rather than used as a heading` · `Do I know how it works? Where it breaks? Which corners it cut?` · `One might wonder:` · `One might ask` · `Why would a human fight you on this?` · `Have a suggestion, correction, or just want to say hi?` · `The result?` · `The worst part?` · `The scary part?` · `The X? A Y.` · `But what does this mean for you?` · `What if I told you...` (+2)

Before: The result? Devastating.

After: The outage cost the company two days of sales.

Do not flag: Interviews, FAQs, dialogue and essays stack and answer questions legitimately, and a regex cannot read register. One question as a hook is fine on LinkedIn; a rhetorical question is earned by a strong setup in any genre. An established fake-casual voice that already talks this way is exempt. The tell is the device recurring between listicle items or as the transition into every section. A question that the text then investigates over several paragraphs is a thesis, not a pivot, and a question a reader actually asked is worth quoting.

### Staccato fragments and manufactured punchlines `staccato-fragments`

Severity: **always** · Scope: universal

Two or more short verbless fragments are set back to back as dramatic beats: the paired fragment ('Fast. Simple.', 'No fluff. Just answers.'), the fragment run ('It had no preference for symmetry. No aesthetic prior. No nostalgia for human taste.'), the polysyndetic chain ('X. And Y. And Z.') and the mic-drop pair ('That's it. That's the whole thing.'). One short sentence can carry emphasis; a row of fragments each engineered to land like a quotable closer is the tell. Keep the one fragment that earns emphasis and fold the rest into full sentences with the claim stated. At length it becomes a run of four-word-or-shorter sentences set as their own paragraphs ('He published this. Openly. In a book. As a priest.'), one thought per sentence with no state kept for the reader.

Cues: `Fast. Simple.` · `No fluff. Just answers.` · `No X. Just Y.` · `X. And Y. And Z.` · `That's it. That's the whole thing.` · `two or more consecutive verbless sentences` · `Openly.` · `Platforms do.`

Before: Fast. Simple.

After: It is fast and easy to set up.

Do not flag: One short sentence for emphasis is rhythm, not a tell; flag fragments only when several appear in a row. Keep fragments, longer spoken sentences and changes of pace that are clear and characteristic of the writer's voice. Dialogue ('No. Never.') and short-form registers such as LinkedIn posts, where the fragment is the register, get relaxed treatment. Abbreviations ('e.g. the') can fool the regex, and exclamatory roll-calls of names or places in travel writing hit it once per book; treat a hit as a candidate. Short sentences that are complete clauses, including sentence-initial 'And', 'So' and 'But', are the hypotactic-smoothness counter-indicator and not this tell, which needs verbless fragments. A negated triad ('No fluff. No filler. No stress.') is negation-countdown and is reported there.

### Template phrase and slot-fill construction (Whether you're X or Y, the X of Y) `template-phrase`

Severity: **always** · Scope: universal

A fill-in-the-blank sentence frame with the nouns swapped in: the false-breadth audience pair 'Whether you're a startup founder or an enterprise architect', 'a significant step towards ...', 'I recently had the pleasure of ...', and the aphorism formula 'X is the Y of Z' ('the Uber of dog-walking'). Pick the audience you are actually addressing, state the concrete change, or cut.

Cues: `Whether you're [X] or [Y]` · `whether you're a beginner or an expert` · `a significant step towards ...` · `I recently had the pleasure of ...` · `X is the Y of Z` · `a [adjective] step towards [adjective] AI infrastructure` · `a [adjective] step forward for [noun]`

Before: Whether you're a startup founder or an enterprise architect, this guide is for you.

After: This guide is for engineers who run their own deployment pipeline.

Do not flag: 'Whether you are X or Y' followed by two genuinely different instructions for the two audiences is content. An analogy that the text then unpacks with specifics is not the formula. The gerund pair ('whether you're building or buying') is the same construction; the regex only reaches the 'a/an' noun form, so read the sentence rather than trusting a miss. A literal step ('a short step forward for balance') and cases where the step is quantified in the same sentence are exempt.

### Abstract subject + all-purpose verb; literal causatives and non-human cognition verbs `abstract-subject-all-purpose-verb`

Severity: **cluster** · Scope: universal

Three sub-mechanisms the sources file together: an abstract or inanimate subject with a colourless verb, 'X shows / provides / brings' (보여준다 / 제공한다 / 가져온다); English analytic causatives ('X made Y happen', 'X led Y to') rendered literally instead of as an adverbial cause (X 때문에 / 덕분에 / 로 인해); and cognition or speech verbs with a non-human subject ('the data suggests', 'the report tells us') where the native form attributes with '~에 따르면 ~이다'. Restore a concrete human or institutional actor, or name the source.

Cues: `suggest` · `show` · `indicate`

Before: 이 연구는 새로운 가능성을 보여준다

After: 연구진은 새로운 가능성을 확인했다

Do not flag: An institution or a document can be the subject when a person did the acting and the reader can recover who (보고서는 ...라고 밝혔다 with a named author; 'the committee recommends'). A genuinely inanimate actor keeps its verb: 서버가 응답한다, 'the sensor reports'. In English the fix is naming the source, not banning the verb, so do not flag 'the study shows' where the study is cited with author and date in the same sentence. This entry carries the translation-side instance of the house baseline's False agency; score a given sentence once, here or there, not twice.

### Agentive by-passive (~에 의해 / ~에 의하여 + passive verb) `agentive-by-passive`

Severity: **cluster** · Scope: universal

The English agentive passive with a named agent ('generated by AI', 'published by the ministry') rendered as X에 의해/에 의하여 plus a passive verb, or adnominally as X에 의한. The agent is present, so it can simply be the subject of an active verb. The same slot exists in any language that prefers the active and puts the actor first.

Before: AI에 의해 생성된 이미지

After: AI가 만든 이미지

Do not flag: Legal and administrative Korean uses ~에 의하여 as a fixed citation formula (법 제3조에 의하여, 규정에 의한) and there it stands. The passive is also right when the agent is genuinely unknown, when the patient is the topic of the paragraph, or when naming the actor would be an accusation the text cannot support. 김혜영 (2009) measured -에 의하여 as discriminative for translated Korean, so the count matters more than any single instance; three or more in a paragraph is the trigger.

### Cleft and dummy-noun emphasis (what matters is, the point is that, which is to say) `cleft-dummy-noun`

Severity: **cluster** · Scope: universal

A claim is foregrounded through a cleft or a dummy noun instead of being stated: 'What matters is X', 'What's important here is', 'The key is that', Korean '주목할 점은' (the point to note is), 'X은 ~라는 점에 있다' (X lies in the point that), '필요한/중요한 것은 X이다', '문제는 / 핵심은 / 관건은'; the wrap-up ending '~다는 것이다 / ~다는 뜻이다' (the thing is that / which is to say); the bound nouns 점·바·수·데 ('나아갈 바는', '할 수가 있다', '하는 데에'); and the inverted this-is-why closer '~하는 이유다'. Rewrite as the direct statement, and cap the wrap-up endings at two per document.

Cues: `What matters is` · `What's important here is` · `The key is that` · `The point is that` · `The thing is` · `It is X that (cleft on a plain subject)` · `which is to say` · `the real question is whether`

Before: What's important here is that the cache is warm. The key is that nobody warms it by hand.

After: The cache is warm, and nobody warms it by hand.

Do not flag: One cleft that genuinely shifts focus after a list of alternatives is ordinary emphasis. Korean '할 수 있다' as the plain ability modal is not the bound-noun tell; the tell is 점/바/데 used to stage a claim, or the wrap-up ending recurring beyond two per document. 'Which is to say' that introduces a genuine restatement carrying new information is ordinary English and appears in human prose at about 0.1 per 10,000 words.

### Copula avoidance (serves as, stands as, boasts, refers to) `copula-avoidance`

Severity: **cluster** · Scope: english

Plain 'is', 'are' or 'has' is replaced by a longer stand-in: 'serves as', 'stands as', 'marks', 'functions as', 'operates as', 'acts as', 'represents', the marketing verbs 'boasts', 'features', 'offers', 'maintains', the lead-sentence dodge 'X refers to', 'holds the distinction of being', and in newer output whole detours such as 'ventured into politics as a candidate' for 'was a candidate' or 'began his career as' for 'was'. Plain existential and possessive phrases ('there is a', 'it has a') are the human counter-indicator that models suppress. Restore the copula or 'has' unless a more specific verb genuinely adds meaning.

Cues: `serves as/stands as/marks/represents [a]` · `boasts/features/offers [a]` · `represents a` · `boasts a` · `features a` · `offers a` · `maintains a` · `functions as` · `operates as` · `acts as` · `refers to` · `ventured into politics as a candidate` · `began his career as` · `holds the distinction of being` · `stands as a testament to` · `centralized hub` · `The building serves as a reminder of the city's heritage.` · `The station marks a pivotal moment in the evolution of regional transit.`

Before: Gallery 825 serves as LAAA's exhibition space for contemporary art. The gallery features four separate spaces and boasts over 3,000 square feet.

After: Gallery 825 is LAAA's exhibition space for contemporary art. It has four rooms totalling 3,000 square feet.

Do not flag: 'marks', 'represents', 'features' and 'serves' have literal uses (a lawyer represents a client, a soldier served as a scout, a face's features) that are not hits. Do not confuse 'has' with the past-perfect auxiliary in 'has been featured'. 'X refers to' is legitimate when the article really is about a term. Tolerance: skip on LinkedIn, in docs and in casual writing; strict in blogs and investor email; relaxed in technical blogs, though a technical voice still prefers plain 'X is Y'. Wikipedia lead paragraphs are formulaic '[subject] is ...' and skew any count. Counter-indicators, keep them and never flag them: 'there is a', 'it has a', and plain 'is', 'are', 'has' — restoring these is the fix.

### Mirrored-clause symmetry and same-skeleton sentence runs `mirrored-clause-symmetry`

Severity: **cluster** · Scope: universal

Two or more clauses or sentences are built on one grammatical frame with only a couple of slots swapped, set side by side to convey contrast or a second case: 'High-metadiscourse prose runs the channel at high redundancy; thinned prose runs it at high density', 'A cart is an object in the system. A chat room is an object in the system.', or three antithetical pairs run in a row ('Products impress people; platforms empower them.'). One mirrored pair can be effective; recurrence is the tell. Merge the cases into one sentence, or let the two halves differ in length and shape.

Cues: `A is an X. B is an X.` · `X do A; Y do B.` · `three antithetical pairs in consecutive sentences`

Before: A cart is an object in the system. A chat room is an object in the system.

After: Carts and chat rooms are both objects in the system.

Do not flag: Judgment only: a single mirrored pair is a normal rhetorical device, and deliberate parallelism in a definition list or a comparison table is the correct form. Flag when the frame recurs across a piece without doing persuasive work.

### Modality flattening (every hedge rendered as ~수 있다 / can) `modal-flattening`

Severity: **cluster** · Scope: universal

Every shade of epistemic uncertainty ('might', 'may well', 'could possibly', 'there is a chance') is rendered with the same modal, Korean ~수 있다, so the modality of a text is monotone. The fix is to diversify the hedge, not remove it: ~을지 모른다, ~을 가능성도 있다, ~을 수도 있겠다, and in English 'is likely to', 'may well', 'is an open question'.

Cues: `three or more 'could' in one paragraph` · `could ... could ... could` · `can ... can ... can` · `may ... may ... may` · `has the potential to` · `there is a chance that`

Before: 이 접근은 실패할 수 있다. 비용이 늘 수 있다. 일정이 밀릴 수 있다.

After: 이 접근은 실패할지 모른다. 비용이 늘 가능성도 있고, 일정은 밀릴 수도 있겠다.

Do not flag: A single ~수 있다 or 'could' is the normal modal. The tell is uniformity across a passage that expresses different degrees of confidence. Distinct from the removal-fix for hedging: here the hedges are kept and varied. Counter-indicators and repair inventory, never flag them: the varied hedges '~을지 모른다', '~을 가능성도 있다', '~을 수도 있겠다', 'may well', 'is likely to' and 'is an open question' are what the fix reaches for.

### Negative parallelism (not X but Y, in every form) `negative-parallelism`

Severity: **cluster** · Scope: universal

A point is staged as the correction of a claim nobody made: a weaker or literal framing is denied and the real one asserted in the same breath. Sub-forms: the joined pivot ('it's not X, it's Y' on a comma, dash or semicolon), the additive correlative ('not just / not only X but (also) Y'), the split-sentence reframe ('The question isn't X. The question is Y.', 'That's not X. That's Y.', 'This isn't about X. It's about Y.'), the causal variant ('not because X but because Y'), the reversed and diplomatic forms ('X, not Y', 'X rather than Y', 'X — not Y'), the cross-sentence 'however' turn, the alternative-question antithesis ('Is it A, or is it B?', Korean 'A인가, B인가'), Korean 'A가 아니라 B' / 'A라기보다 B다', Dutch 'het is niet x, het is y' / 'niet omdat x maar omdat y', and the poetry line pair ('Not an ending / but a beginning'). The joined pivot and the split-sentence reframe fail on a single hit; the reversed and diplomatic forms ('X, not Y', 'X rather than Y') fail at two or more per 1,000 words. Delete the denied half and state Y directly, optionally as a plain comparative ('Y matters more than X').

Cues: `It's not X, it's Y` · `It's not X — it's Y` · `It's not X. It's Y.` · `This is not X. It's Y.` · `It's not just X, it's Y` · `It's not just X — it's Y` · `It's not just X but Y.` · `It's not merely X, it's Y` · `isn't just X — it's Y` · `doesn't just X; it Y` · `The question isn't X, it's Y.` · `The question isn't X. The question is Y.` · `The problem isn't X. The problem is Y.` · `The headline isn't X. The real story is Y.` · `That's not X. That's Y.` · `This isn't about X. It's about Y.` · `This isn't about X, it's about Y` · `It's not about X, it's about Y` (+12)

Before: It's not just about efficiency — it's about transformation.

After: The main gain is a different way of working; the speed is a side effect.

Do not flag: One genuine contrast that corrects a belief the reader actually holds is legitimate, and 'common misconceptions' or 'myths busted' pieces use the form on purpose; density is the tell, so one per piece at most and only where the denied half does work. A plain 'not only X but also Y' listing two real things can stay in flowing prose where the reader would otherwise assume only X. Ordinary 'rather than' with two concrete options is common in human prose; flag it only when the first half is an abstract inflation and the second an invented opposite. Do not remove every antithesis from a text: the im-not-ai gate treats 'antithesis annihilation' as over-editing. A consuming repo may ban the template outright in its own copy; read its AGENTS.md. See invented-contrast-pair for the 'false X rather than genuine Y' variant, where the invented mirror noun is the tell; bare 'rather than' is a cue in neither entry.

### Nominalization and verb periphrasis (made a decision, has the ability to, N 능력) `nominalization-inflation`

Severity: **cluster** · Scope: universal

A single direct verb or adjective is replaced by a verb plus abstract noun or a modal periphrasis: 'made a decision' for 'decided', 'has the ability to' for 'can', 'the implementation of' for 'implementing', 'X capability' or 'ability to X' rendered as noun + 능력 in Korean. Korean sub-forms: Sino-Korean nominalisers -성/-적/-화 and literal renderings of English -tion/-ment/-ness/-ity at twelve or more per document (F-4), and -적 + abstract noun compounds ('전략적 함의', '실천적 기반') at three or more (F-5). Restore the verb or adjective root and name who does what.

Cues: `made a decision` · `has the ability to` · `the implementation of the policy` · `provides support for` · `conducts an analysis of` · `is reflective of` · `performs an evaluation of` · `the <noun>tion of the <noun>ment of (two nominalizations chained by 'of')`

Before: The team made a decision to delay the launch.

After: The team decided to delay the launch.

Do not flag: A nominalisation that names a thing under discussion ('the implementation shipped late') is a noun, not periphrasis. Legal, academic and policy registers carry nominalised style by convention; apply the Korean thresholds (12+ per document, 3+ chains, cap of two 능력) and an English equivalent of density, never a single hit. Many -tion and -ment nouns are the only available word (information, government, management, environment) and carry no inflation. The chained form is the tell, not the suffix, which is why the English regex requires two nominalizations joined by 'of' rather than matching the suffix alone.

### Orphaned demonstrative and bad-subject sentence `orphaned-demonstrative`

Severity: **cluster** · Scope: universal

'This', 'that' or 'these' opens a sentence as its subject with no clear referent, typically 'This highlights ...' or 'This underscores ...' after a paragraph of mixed claims; more generally the grammatical subject is not the topic of the sentence and the real agent or idea sits in an object or modifier ('Readers are better guided when the subject matches the main idea'). Korean shows the same as demonstrative meta-entries '이는 ~을 의미한다', '이 점에서', '이 관점에서' three or more times in a paragraph. Name the referent, or make the actual topic the subject.

Cues: `This highlights` · `This underscores` · `This reflects` · `This speaks to` · `This means that` · `These findings suggest`

Before: Readers are better guided when the subject matches the main idea. This highlights the importance of subject choice.

After: Choosing the right subject keeps the writing clear and focused.

Do not flag: A demonstrative whose antecedent is the single claim of the previous sentence is ordinary cohesion. Flag when the referent is a whole paragraph of mixed claims, or when the demonstrative meta-entry recurs three or more times in one paragraph.

### Agentless prescription (must be addressed, X is needed) `prescriptive-agentless-necessity`

Severity: **cluster** · Scope: universal

Deontic statements pile up with no actor named: Korean ~해야 한다 (must) / ~할 필요가 있다 (there is a need to) five or more times, and the abstract-noun necessity '혁신이 필요하다' (innovation is needed), '변화가 필요하다' (change is needed). English shows the same as 'there is a need to', 'must be addressed', 'it is essential that'. Say who must do what: name the actor and the action as subject and verb, and vary with conditionals. The fix supplies the actor from the surrounding text or the source; where no actor is recoverable the sentence is a question for the author, not a rewrite.

Cues: `innovation is needed` · `change is needed` · `there is a need to` · `must be addressed` · `it is essential that` · `steps must be taken` · `greater X is needed`

Before: 개발팀은 배포에 반나절을 쓴다. 혁신이 필요하다.

After: 개발팀이 배포 절차를 바꿔야 한다.

Do not flag: Policy and standards documents are prescriptive by genre; a single 'must' with a named actor is a requirement, not a tell. The Korean threshold is five or more per document. A concrete subject makes the predicate fine (두 번째 서버가 필요하다, 'a second server is needed'); the defect is the abstract subject. In a requirements document 'X is needed' is the genre's own phrasing and the actor is established elsewhere.

### Rule of three (tricolon, colon into a triple) `rule-of-three`

Severity: **cluster** · Scope: universal

Ideas are padded or trimmed to exactly three items so the sentence sounds complete: three adjectives ('faster, cheaper, smarter'), three abstract nouns ('innovation, inspiration, and industry insights'), three parallel phrases, a colon opening onto exactly three comma-separated items, a catch-all third item ('and other ...'), three one-word fragments each closed with a period ('Fast. Simple. Effective.'), or antithetical pairs run three times. The tell is the constancy of the count across a text, not any single triplet. Use the number of items the meaning has: two, four, or a full sentence.

Cues: `innovation, inspiration, and industry insights` · `keynote sessions, panel discussions, and networking opportunities` · `adjective, adjective, and adjective` · `adjective, adjective, adjective` · `short phrase, short phrase, and short phrase` · `separate ports, processes, and local state.` · `tiles, metals, and plastics` · `drywall, plywood, and other construction materials` · `electrical outlets, switches, and plumbing fixtures` · `model making, woodworking, and other craft projects` · `identity, payments, compute, distribution` · `workflows, decisions, and interactions` · `Faster, cheaper, smarter.` · `Fast. Simple. Effective.` · `Dream big. Start small. Scale fast.` · `Learn it. Own it. Live it.` · `a triad whose third item is a catch-all ('and other ...')` · `a triad of three abstract nouns with no supporting detail`

Before: The event features keynote sessions, panel discussions, and networking opportunities. Attendees can expect innovation, inspiration, and industry insights.

After: The event has talks and panels, with time between sessions for meeting other attendees.

Do not flag: A real three-item list is not a tell, and in technical writing three-item lists are often simply true; weigh by genre and by recurrence, never per hit. A single rule-of-three in a piece is noise; flag when every section or paragraph closes on a triad, when the third item is a catch-all, or when the items are abstract nouns with no supporting detail. Classical tricolon used once for emphasis is legitimate rhetoric. The same line-wrap caveat applies: a three-item tail of a longer sentence can land at the start of a wrapped line. A negated triad ('No fluff. No filler. No stress.') belongs to negation-countdown; do not count it a second time here.

### Stranded auxiliary contrast (the data didn't.) `stranded-auxiliary-contrast`

Severity: **cluster** · Scope: english

A reversal lands on a bare auxiliary: 'The tool died; the data didn't.', 'Reading mostly passed. Writing didn't.', 'It does.' One is fine; as a recurring rhythm it is a signature move in which the clipped contrast poses as earned insight. If the piece already has one, write the next contrast out in full.

Cues: `The tool died; the data didn't.` · `Reading mostly passed. Writing didn't.`

Before: The tool died; the data didn't.

After: The tool died, and the data survived it.

Do not flag: The single instance is legitimate style; only density across a piece distinguishes voice from tic. Dialogue answers ('I don't.') are speech.

### Synonym doubling (role and function, new and innovative) `synonym-doubling`

Severity: **cluster** · Scope: universal

Two near-synonymous modifiers or abstract nouns are coordinated on one head so the phrase says the same thing twice: Korean '중요하고 핵심적인 역할' (important and core role), '새롭고 혁신적인 접근' (new and innovative approach), '지속적이고 꾸준한 노력' (continuous and steady effort), and the noun-pair variant '~로서의 역할과 기능' (role and function as ...), '~의 의미와 가치' (meaning and value of ...). Keep one of the two. Where you know what the role or property actually is, name it instead of keeping either word.

Cues: `role and function` · `important and central` · `new and innovative` · `clear and concise` · `safe and secure` · `quick and easy` · `robust and reliable` · `tools and technologies` · `vital and essential`

Before: 중요하고 핵심적인 역할

After: 핵심 역할

Do not flag: Legal doublets ('terms and conditions', 'null and void') and pairs whose members genuinely differ ('cost and schedule') are not doubling. The tell is two words that mean the same thing modifying one noun.

### Tailing negation fragment and deflating tail clause `tailing-negation`

Severity: **cluster** · Scope: english

A sentence ends with a comma and a terse negative tail in place of a full clause. Sub-forms: the bare negation fragment (', no guessing', ', no setup', ', no strings attached') and the deflating qualifier that theatrically narrows the claim just made (', and no more', ', and nothing more', ', and no evidence of anything finer'). Write the constraint as a real clause or cut it.

Cues: `, no guessing` · `, no setup` · `, no strings attached` · `, no surprises` · `, no exceptions` · `, and no more` · `, and nothing more` · `, and no evidence of anything finer`

Before: The options come from the selected item, no guessing.

After: The options come from the selected item, so the user never has to guess.

Do not flag: Negations enumerating spec constraints in a list ('no dependencies, no telemetry') are list content. A single 'and no more' that sets a real bound in measured prose is fine; the tell is the tail as a recurring flourish.

### Agentless passive and subjectless fragment `agentless-passive-subjectless-fragment`

Severity: **context** · Scope: universal

The actor is hidden or the subject dropped in the clipped shape models use to compress feature descriptions: agentless passives ('The results are preserved automatically.', 'Support for nested queries was added.') and verbless or subjectless fragments ('No configuration file needed.'). Name the actor when it makes the sentence clearer and prefer active voice with a human subject; restore the subject and verb in flowing prose.

Cues: `was added` · `has been added` · `are preserved automatically` · `is handled automatically` · `has been improved` · `can be configured` · `it is recommended that` · `No X needed.` · `No configuration file needed.`

Before: No configuration file needed. The results are preserved automatically.

After: You do not need a configuration file. The CLI preserves results automatically.

Do not flag: A passive with an irrelevant or unknown actor stays; use active voice only where it makes the actor and action clearer. Terse reference registers are the correct form for fragments: README feature lists, changelog entries, parameter docs, commit subjects ('No breaking changes'). Tolerance: skip in docs and casual writing, relaxed on LinkedIn and in technical blogs, strict in blogs and investor email. A single deliberate fragment for emphasis is rhythm.

### Hypotactic smoothness (suspiciously clean grammar) `hypotactic-smoothness`

Severity: **context** · Scope: universal

Every sentence resolves grammatically: no fragments, no sentences starting with 'And' or 'But', no comma splices for effect, no anacoluthon or broken-off constructions, and no occasional wordy phrasing ('as a result of', 'in order to', 'the fact that'), which are the human fingerprints that models sand away. This is a preserve-rule: keep those features where the natural voice would use them, and do not cure the flatness by injecting typos.

Cues: `no sentence-initial 'And' or 'But' in 1,000 words or more` · `no fragments anywhere in a long text` · `no comma splice used for effect` · `every sentence a complete subject-verb-object` · `uniform sentence length with no change of pace`

Before: The build failed; therefore, we reverted the commit, after which it passed.

After: The build failed. So we reverted the commit. And it passed.

Do not flag: Preserve, do not flag: 'And', 'But', 'as a result of', 'in order to', 'all of the', 'a part of', 'the fact that'. These are the human fingerprints this entry exists to keep, and this entry cues their absence, not their presence. Counter-indicator: an isolated wordy construction or a sentence-initial 'And' is a sign of a human hand, not a flaw to fix. Formal registers (legal, academic) are clean by convention. Never add deliberate typos or fake errors; that is the paranoia-spiral anti-goal. The rewritten after ('The build failed. So we reverted the commit. And it passed.') is short complete clauses, not the verbless fragments staccato-fragments fires on; see that entry's false_positives.

### Invented contrast-pair mirroring `invented-contrast-pair`

Severity: **context** · Scope: universal

A contrast is forced into symmetry where one half is a legitimate term of art and the other a phantom counterpart invented to balance the sentence ('false precision rather than genuine accuracy'). The parallelism exists only for rhythm and is invisible unless the reader knows which half is real. Reach for an actual opposite, or drop the contrast frame and state the positive claim.

Cues: `<term of art> rather than <adjective + abstract noun>` · `false/apparent/surface X rather than genuine/true/real Y` · `false precision rather than genuine accuracy`

Before: The model gives false precision rather than genuine accuracy.

After: The model gives a number that looks more exact than it is.

Do not flag: Pairs where both halves are real ('real data rather than theoretical models', 'practical results rather than abstract speculation') are ordinary contrast, and ordinary 'rather than' is everywhere in human prose. Tolerance: strict for LinkedIn, blog and investor email; relaxed for technical blogs and docs; skip in casual writing. The 'X rather than Y' family in general belongs to negative-parallelism; here the tell is the invented mirror noun, so bare 'rather than' is a cue in neither entry.

### Confidence by litotes `litotes-confidence`

Severity: **context** · Scope: english

A claim is made by negating its opposite ('not difficult', 'not optional') so that it is presupposed rather than asserted or argued, which puts it beyond questioning. Where a plain positive exists ('easy', 'mandatory'), use it and give the reason.

Cues: `not un- (not uncommon, not unlike, not unreasonable, not unimportant)` · `not difficult to` · `not optional` · `not accidental` · `not without` · `no small` · `hardly surprising`

Before: Blind tagging is not optional.

After: Every tagger must work blind, because sighted tagging skews the sample.

Do not flag: Litotes is a legitimate understatement in measured prose; the tell is its uniform use as a confidence device, several per piece, with no argument behind the presupposition.

### Same-opener sentence runs (anaphora) `same-opener-runs`

Severity: **context** · Scope: universal

Three or more consecutive sentences open on the same word or words ('They assume that ... They assume that ... They assume that ...', 'Maybe nobody needed it. Maybe it solved the wrong problem. Maybe the timing was off.'). Deliberate anaphora is a rhetorical device; a run that is not doing persuasive work is a tell. Keep the first, then merge sentences, change the subject, or begin with the action; do not ban the repeated word.

Cues: `three or more consecutive sentences opening on the same one to three words` · `They assume that ... They assume that ... They assume that ...` · `She noted... She noted... She filed...` · `It's ... It's ... It's ...`

Before: They assume that users will pay. They assume that developers will build. They assume that ecosystems will emerge.

After: Their plan rests on two assumptions: users will pay and developers will build. An ecosystem, they expect, will follow.

Do not flag: Deliberate repeated openings for effect stay ('She came. She saw. She conquered.'); change them only when the repetition adds nothing. Pronoun-opener runs ('He ... He ... He ...') are ordinary narration. Whether the repetition is earned is what a pattern cannot read, so the regex is a prompt for judgment, not a verdict.

## Rhetorical moves and tone

### Announced interest and claimed emotion `announced-interest`

Severity: **always** · Scope: english

A cue pre-interprets importance or claims a reaction the writing has not earned: 'Here's what's interesting', 'Here's the interesting part', 'What surprised me most', 'What struck me was', 'I was fascinated to discover', 'The most interesting part', and the bare section-header form ('Interesting aspect:'). It works only when genuinely surprising data follows; the default failure is a restatement of the obvious behind a promise of surprise. Cut the cue and present the thing, or make the lead-in specific to why it matters.

Cues: `Here's what's interesting` · `Here's what caught my eye` · `Here's what stood out` · `Here's the interesting part` · `Here are the parts I found interesting` · `What surprised me most` · `I was fascinated to discover` · `What struck me was` · `I was excited to learn` · `The most interesting part` · `Interesting part of the project:` · `Interesting thing here:` · `Interesting aspect:`

Before: Here's the interesting part.

After: Revenue fell 8 percent while headcount rose 20 percent.

Do not flag: A first-person account may report a real reaction when the surrounding writing earns it ('I expected 40 minutes; it took 90 seconds'). The fix is not to ban the word surprised, it is to make the surprise visible. Interview and diary registers carry more of this legitimately. Boundary with false-suspense-hook: that entry owns the withheld-payoff fragment ('The catch?', "Here's where it gets interesting"), this one owns the frame that names the interest or the reaction ("Here's the interesting part", 'What surprised me most'). Report a sentence under one of the two, never both.

### Aphorism formula (X is the Y of Z) `aphorism-formula`

Severity: **always** · Scope: universal

An ordinary claim is recast as a quotable general law by a slot-fill metaphor: 'X is the language of Y', 'the currency of Z', 'the architecture of trust', 'X becomes a trap', 'X is not a tool but a mirror', 'It's the Excel of AI agents', and the transformation frame that dramatises a shift ('from X to Y', 'beyond X toward Y', Korean X에서 Y로 / X을 넘어 Y로). The shape does the persuading in place of evidence, and the comparison only communicates if the reader already knows both sides of the mapping. Replace with the concrete claim.

Cues: `the architecture of trust` · `becomes a trap` · `not a tool but a mirror` · `is the language of` · `is the currency of` · `It's the Excel of AI agents.`

Before: Symmetry is the language of trust. Efficiency becomes a trap when teams forget the human layer.

After: Symmetric layouts feel more predictable to users. Teams can over-optimise a workflow and miss how people actually use it.

Do not flag: Quotations and established idioms are attributed speech or common coin ('time is money'). An ordinary genitive copula is not an aphorism ('Paris is the capital of France', 'HTTP is the protocol of the web'), which is why a general 'X is the Y of Z' regex cannot be used. A comparison stays when both referents are certain to be known by the audience and the mapping is spelled out. Cap the transformation frame at one per document.

### Aphoristic ender (quotable closing line) `aphoristic-ender`

Severity: **always** · Scope: universal

A paragraph, section or piece lands on a compact epigram that restates the point as a maxim instead of adding information: 'The future isn't coming. It's already here.', 'a stance, not its absence', 'evidence of training, not of virtue', 'Because in the end, the real question isn't what AI can do.' Frequent sub-forms are the ender built as a contrastive binary ('X, not Y') and the hortatory call-to-action ender (Korean ~할 때입니다 / ~시점입니다, 'now is the time to'). Delete it rather than rewriting it into a better metaphor, and end on the clearest concrete sentence already in the draft.

Cues: `a stance, not its absence` · `leaves fingerprints, and fingerprints can be counted` · `the dense version is the courtesy` · `it is relocated to the writer` · `not a property of the prose` · `evidence of training, not of virtue` · `Because in the end,` · `the real question isn't` · `En dat telt.`

Before: The future isn't coming. It's already here.

After: Three of the five teams already run it in production.

Do not flag: One earned closing line in a whole piece is fine, and a quotation used as an ender belongs to its author. The tell is every paragraph landing this way, or a closer that would survive being pasted under a different article. Cap the hortatory 'now is the time' ender at one per document at most. 'And that matters.' is reported under self-ranking-claim. The category names ('aphorism', 'mic-drop') are what this entry is about, not text to match.

### 'Beyond mere X' escalation (단순한 X를 넘어 Y / more than just X) `beyond-mere-escalation`

Severity: **always** · Scope: universal

Mid-sentence escalation that upgrades a thing by dismissing a smaller version of it: '단순한 X를 넘어 Y', a calque of English 'beyond mere X' and 'more than just X'. It asserts significance instead of showing it, and the second term is usually vaguer than the first. Delete the escalation and state what the thing does.

Before: 이것은 단순한 도구를 넘어 새로운 인프라다

After: 이것은 인프라다

Do not flag: The source recorded zero occurrences of the Korean frame in the human corpus, which is why it fires on one instance; the English and Dutch surface forms are commoner in human prose, so read them before flagging. A literal spatial or temporal 넘어 ('over the hill', 'past midnight') is not this pattern. 'More than just' is fine when the sentence goes on to say concretely what the second term is, and inside a quotation it stands. Its English surface overlaps the syntax category's negative-parallelism and false-range family: score the sentence once.

### Candor flag and fake-candid opener `candor-flag-opener`

Severity: **always** · Scope: universal

A staged pause or claim of frankness precedes an ordinary point: 'Honestly?', 'Look,', 'Here's the thing', 'Let's be honest', 'Real talk', 'Let me be clear', 'I'll be honest', 'The uncomfortable truth is', 'the honest answer is'. The frame implies the surrounding text was less honest and delays the answer by one beat. The tell is the standalone theatrical opener, not the word; state the point directly.

Cues: `Honestly?` · `Look,` · `The thing is` · `Real talk:` · `Let's be honest —` · `Here's what I mean` · `Let me be clear` · `I'll be honest` · `The uncomfortable truth is` · `the honest answer` · `Here's the thing:`

Before: Is it worth the price? Honestly? It depends on how often you'll use it.

After: Whether it is worth the price depends on how often you use it.

Do not flag: 'Honestly' or 'look' mid-sentence is ordinary in casual writing and in dialogue. Keep 'to be honest' where it marks real uncertainty, self-correction or spoken rhythm in a voice that already runs that way. Quoted speech stays. This entry owns "Here's the thing"; false-suspense-hook no longer lists it.

### Contrast slogan as opener or heading `contrast-slogan-opener`

Severity: **always** · Scope: universal

A two-part contrast slogan stands as the first line or heading of a text, defining the thing by what it is not: 'Eén avond, geen verkooppraatje.', 'One evening, no sales pitch.' The opener should say what happens; what the thing is not belongs further down in its own block, if anywhere. The contrastive construction itself is catalogued under syntax; this entry is about its use in the headline position.

Cues: `X, geen Y` · `X, no Y` · `geen verkooppraatje`

Before: Eén avond, geen verkooppraatje.

After: Twee talks, wat te eten, en daarna tijd om bij te praten.

Do not flag: A list heading that happens to contain a negation is not a slogan ('Toegang, geen registratie vereist' inside a table of practical details). Deeper in the body, one contrast line may be the honest summary of a real difference; the rule is about the first line and the heading.

### False profundity (insight shape, no claim) `false-profundity-truism`

Severity: **always** · Scope: universal

A sentence carries the shape of insight, a contrast, a reversal or an epigram, but contains nothing a reader could act on or disagree with: 'Everyone has moments of doubt.', 'Change is the only constant.', 'At the end of the day, we are all human.' These are the safest possible sentences, true of everyone and so of no one. The related regression is ornamental phrasing chosen over the plain statement, which returns in long sessions even after the model has been told to write plainly. Replace with the concrete claim, or delete.

Cues: `Everyone has moments of doubt.` · `Change is the only constant.` · `At the end of the day, we are all human.` · `pretty sentences` · `sentences that sound profound but say absolutely nothing`

Before: At the end of the day, we are all human, and change is the only constant.

After: The team missed the deadline twice, and both times the cause was the same undocumented dependency.

Do not flag: A proverb quoted and then argued with is doing work. Ceremonial registers (a eulogy, a toast, a preface) tolerate the general statement. The test is whether a reader could disagree with the sentence; if not, it is filler.

### False suspense hook (teaser before an ordinary point) `false-suspense-hook`

Severity: **always** · Scope: english

A short fragment or clause manufactures suspense around information that needed none: 'The catch?', 'The kicker?', 'Here's the kicker', 'Here's where it gets interesting', 'The best part?', 'The result?', 'This is where X comes in', and the withheld-term beat ('has a name', 'the cleanest organizing idea is this.'). Mid-flow teasers pad the rhythm and promise a revelation the next sentence cannot pay for. Delete the hook and state the thing.

Cues: `The catch?` · `The kicker?` · `But here's the kicker:` · `The best part?` · `Plot twist:` · `The result?` · `Here's where it gets interesting` · `Here's what most people miss` · `Here's the starting point` · `Here's the deal` · `has a name` · `the cleanest organizing idea is this.` · `Here's where it gets clever`

Before: The catch? It only works on weekends.

After: It only works on weekends.

Do not flag: A genuine reveal that the reader has been set up to want, in a narrative or a mystery, is craft. Quoted speech and comedy where a punchline is literal stay. A one-line paragraph is only a hook when the sentence after it does not repay the build-up. "Here's the thing" belongs to candor-flag-opener and 'what nobody tells you' to scarcity-of-knowledge-claim; report such a sentence once, under the owning entry. 'This is where X comes in' is a shape, not a string, so it lives in the regex. 'Has a name' is this pattern only when the name is withheld across a sentence or paragraph break; on its own it is an ordinary predicate. Boundary with announced-interest: the frame that names the interest or a reaction is that entry's, the withheld payoff is this one's.

### Generic conclusion and future-narrative closer `generic-conclusion`

Severity: **always** · Scope: universal

A closing line gestures at the future or at certainty without a claim anyone could check: 'The future looks bright', 'Only time will tell', 'One thing is certain', 'As we move forward'. The future-narrative form is a fixed shape, modal plus 'become' plus a vague head noun ('may become one of the most important narratives of the next market cycle', 'is poised to become the defining trend of the coming decade'), and the Korean variant opens the last paragraphs with a bare time adverb (향후, 앞으로, 중장기적으로) and no date or condition. Replace with a falsifiable version or cut. The inspirational send-off ('exciting times lie ahead', 'a major step in the right direction', 'memories to last a lifetime') is the same closer; end on the last concrete fact instead.

Cues: `The future looks bright` · `Only time will tell` · `One thing is certain` · `As we move forward` · `May become one of the most important narratives of the next market cycle` · `could become the defining trend of the coming decade` · `is poised to become the next major chapter in` · `Exciting times lie ahead` · `continue their journey toward excellence` · `a major step in the right direction` · `promises memories to last a lifetime`

Before: The intersection of AI and DePIN may become one of the most important narratives of the next market cycle. Only time will tell.

After: DePIN compute may undercut AWS spot pricing for parallel workloads by 2027.

Do not flag: A forecast with a number, a date or a named condition is a claim, not a closer ('the contract expires in March, and the council has not scheduled a tender'). Documentation and reference registers skip this pattern entirely because they rarely close on prediction. LinkedIn and casual registers tolerate a warm closer; flag it in reports, articles, encyclopaedic and investor prose. Quoted marketing copy under discussion is exempt.

### Importance labelling (telling the reader what weight to give) `importance-labelling`

Severity: **always** · Scope: universal

An adjective, superlative or gloss asserts that something is important, crucial, significant, surprising, subtle or obvious in place of showing why: 'plays a crucial role in', 'it cannot be overstated', 'one of the most important', 'this represents a broader shift', 'the decision symbolizes a commitment to excellence', 'it speaks to a larger trend in the industry'. The hedged-superlative form ranks the subject against an unnamed field, and the concessive form concedes the subject is minor and then claims broader significance anyway. Delete the label, keep the fact and the consequence that makes it matter.

Cues: `Plays a crucial role in...` · `It cannot be overstated...` · `One of the most important` · `One of the most significant` · `One of the most crucial` · `this represents a broader shift` · `the decision symbolizes a commitment to excellence` · `it speaks to a larger trend in the industry` · `Though it saw only limited application` · `contributes to the broader history` · `reflects the influence of`

Before: The station plays a crucial role in the regional network, and its significance cannot be overstated.

After: Four of the five regional lines terminate at the station.

Do not flag: A sourced ranking with the ranker named stays ('the largest of the four by tonnage, per the 2024 port register'). Statistical 'significant' with a test behind it is a term of art. In a summary or an abstract, naming which finding the paper treats as primary is reporting, not labelling.

### Meta-signposting (announcing the text instead of writing it) `meta-signposting`

Severity: **always** · Scope: universal

The text narrates its own moves rather than making them: opening announcements ('In this article, we will explore', 'In this section, we will discuss', 'First, we'll look at... Second, we'll examine...'), collaborative transitions ('Let's dive in', 'Let's break this down', 'Now let's turn to'), in-body structure talk ('Four caveats belong at the front', 'as discussed above', 'below I try to specify'), sentence-level meta lead-ins that comment on the previous sentence (Korean 이는 ~, 이 점에서, 이 관점에서), and the enumeration preamble that announces a list before giving it ('This can be broadly divided into three parts', 'Below is a detailed overview based on available information:', 'Key highlights:'). Delete the announcement and deliver the content.

Cues: `let's explore` · `let's break this down` · `here's what you need to know` · `now let's look at` · `without further ado` · `In this article, we will explore…` · `Let's dive in!` · `Let's take a look` · `Let's examine` · `Let's unpack this` · `step by step` · `Now let's turn to` · `Let's break it down` · `First, we'll look at…` · `Second, we'll examine…` · `Finally, we'll conclude by…` · `Four caveats belong at the front` · `below I try to specify` (+17)

Before: Let's dive into how caching works in Next.js. Here's what you need to know.

After: Next.js caches data at multiple layers, including request memoization, the data cache, and the router cache.

Do not flag: A long technical document, a thesis chapter or a spec may genuinely need a road map, and a cross-reference that saves the reader a search ('the token format is in section 4') is navigation, not signposting. 'Let's' is fine as a real invitation to act ('let's run the migration on staging first'). Flag the announcement that is followed immediately by the thing it announced. 'This matters because' is a framing clause, not a structural announcement: it belongs to significance-signaling, and one sentence is reported under one entry, not both.

### Scarcity-of-knowledge claim (nobody talks about this) `scarcity-of-knowledge-claim`

Severity: **always** · Scope: english

The text claims that its point is unnoticed, hidden or suppressed, where no such scarcity exists: 'what nobody tells you about', 'the failure mode nobody's naming', 'a problem nobody talks about', 'the insight everyone's missing', 'This is the part most people skip', 'What most people get wrong'. It flatters the writer as the lone expert and inflates novelty. Drop the framing and let the claim stand on its own.

Cues: `the failure mode nobody's naming` · `a problem nobody talks about` · `the insight everyone's missing` · `what nobody tells you about` · `This is the part most people skip` · `What most people get wrong` · `Here's what nobody tells you` · `The part everyone misses` · `What nobody tells you is…`

Before: The part everyone misses: distribution is the real moat. The three competitors license the same model, and only one has shelf space in the carrier stores.

After: The three competitors license the same model, and only one has shelf space in the carrier stores.

Do not flag: A documented gap is a claim with evidence ('the manual does not mention this, and neither does the changelog'). Teaching material may legitimately flag a common misconception when it then names it. Invented concept labels used the same way are judgement calls; no regex can catch a coinage. This entry owns 'what nobody tells you'; false-suspense-hook no longer lists it.

### Self-ranking and self-applause about one's own point `self-ranking-claim`

Severity: **always** · Scope: english

The writer tells the reader which of their own points is the deep, clever, contrarian or overlooked one instead of letting the reader judge: 'the deepest point is', 'the cleanest organizing idea', 'That last move is the contrarian one', 'That's the part everyone misses', 'And that matters.', 'Which is exactly the point.'. The contribution-framing variant claims the point completes what earlier accounts left open ('supplies the other half', 'pins down something the earlier explanations left open'). Cut the labelling sentence, or restructure so the highlighted item comes first and is expanded with specifics.

Cues: `cleanest organizing idea` · `The deepest point in the usual comparison is` · `a deflationary point` · `the deepest point is` · `That last move is the contrarian one` · `This is the interesting part` · `That third bullet is the real story` · `The last bit is the counterintuitive one` · `And that matters.` · `That's the part everyone misses.` · `Which is exactly the point.` · `supplies the other half` · `it pins down something the earlier explanations left open`

Before: Two separate indexes for tiered storage. That last move is the contrarian one.

After: Two separate indexes for tiered storage. Co-locating related data usually helps cache locality, and splitting the indexes is what keeps the hot path cheap.

Do not flag: An abstract or an executive summary may legitimately say which result the work treats as primary. A review that ranks options is doing the reader's work for them on purpose. The deletion test settles it: if cutting the sentence loses no information, it was applause. 'Here's where it gets clever' is reported under false-suspense-hook, whose regex already covers the whole 'here's where it gets ...' family.

### Stacked hedges on one claim `stacked-hedges`

Severity: **always** · Scope: universal

Two or more qualifiers piled on a single predicate until it says nothing: 'could potentially possibly be argued that ... might', 'there may be a possibility that ... could', 'While this may vary, generally speaking, in most cases, it's worth noting that'. Sub-forms: hedge-stacked predictions ('may eventually', 'could potentially'), hedge-and-reassure (a qualifier followed at once by a reassurance), the parenthetical nuance aside ('(and, increasingly, Z)', '(or, more precisely, Y)', '(and perhaps more importantly, W)'), and the epistemic label 'this is an inference'. Keep exactly one hedge that the source supports; if a parenthetical matters, give it its own sentence.

Cues: `it's also possible` · `might arguably` · `in some cases it may` · `this is an inference` · `While this may vary` · `generally speaking` · `in most cases` · `it's worth noting that` · `In many cases` · `(and, increasingly, Z)` · `(or, more precisely, Y)` · `(and perhaps more importantly, W)` · `could potentially create` · `may eventually unlock` · `might ultimately transform` · `(and increasingly, X)` · `(or more precisely, Y)` · `(though to be fair, Z)` (+1)

Before: It could potentially possibly be argued that the policy might have some effect on outcomes.

After: The policy may affect outcomes.

Do not flag: One hedge marking a real limit stays. Scope statements, legal and safety notices, real corrections and named objections are not hedges. In technical writing 'may' and 'could' are often the accurate word; the tell is the stack, never a single modal. A casual voice keeps warm hedges ('honestly', 'I think') and cuts the corporate ones. A negated modal is not a stack ('could not possibly'), so the gap between modal and hedge is one non-negating word. 'may possibly' / 'could possibly' in the sense of physical possibility is ordinary English and predates models, so in expository prose weigh the stack by density and by whether the sentence is a prediction. A genuine tangent or a parenthetical that carries a fact (a date, a number, a name) is not this pattern.

### Stakes inflation (world-historical framing of an ordinary subject) `stakes-inflation`

Severity: **always** · Scope: english

The importance of the subject or of what is about to be said is raised beyond anything the content supports: 'This will fundamentally reshape how we think about everything', 'will define the next era', 'the stakes have never been higher', 'now more than ever', 'because they shape everything that follows'. A post about API pricing becomes a meditation on the fate of civilisation, and the payoff never matches the build-up. Cut the inflation and let the specific claim carry its own size.

Cues: `fundamentally reshape` · `how we think about everything` · `will define the next era` · `something entirely new` · `In a world where` · `now more than ever` · `the stakes have never been higher` · `because they shape everything that follows`

Before: This will fundamentally reshape how we think about everything, and the stakes have never been higher.

After: The price change adds about 40 euro a month for a team of ten.

Do not flag: Subjects whose stakes are genuinely large (a safety recall, a fatality, a systemic outage) may be described plainly in strong terms; the tell is scale asserted without a mechanism. Marketing copy in a genre where hyperbole is the convention still reads as this pattern to anyone outside it.

### Sycophancy (validating the reader before answering) `sycophancy`

Severity: **always** · Scope: english

Praise of the requester, their question or their feelings precedes the answer: 'Great question!', 'You're absolutely right', 'That's an excellent point', 'What a thoughtful observation'. Sub-forms: the performative-empathy opener ('I completely understand how you feel'), the warm-up preamble before a reply, and the validate-then-promise stamp that ratifies a correction and announces a better version in the same sentence ('is correct, and it can be made precise'). Cut the praise and answer; where acknowledgement is warranted, keep the source's own rather than adding one.

Cues: `Great question!` · `That's an excellent point` · `Excellent point!` · `You're absolutely right!` · `That's a really insightful observation` · `That's a great question` · `Excellent question` · `What a thoughtful question!` · `You're absolutely right to push back on this` · `That's a brilliant observation.` · `What a thoughtful observation!` · `I completely understand how you feel` · `is correct, and it can be made precise` · `is right, and this is its exact form`

Before: Great question! You're absolutely right that this is a complex topic. That's an excellent point about the economic factors. Fuel cost rose 40 percent while ticket prices stayed flat.

After: Fuel cost rose 40 percent while ticket prices stayed flat.

Do not flag: A short, specific thank-you that then moves on is not sycophancy. Agreement with a stated reason ('you're right that the index is missing, because the migration never ran') is an argument, not flattery. Quoted dialogue and transcribed speech stay.

### Both-sides padding (performed balance) `both-sides-hedge`

Severity: **cluster** · Scope: universal

A symmetrical 'critics say X, supporters say Y, the truth lies somewhere in between' move performs nuance while asserting nothing, alongside the safe-balance lexicon of non-commitment (both sides, both, has advantages but, carefully, balance) at four or more occurrences per document. Commit to one side, give a concrete comparison, or make the claim conditional on something the reader can check. It also shows as pro and con pairs padded to equal length regardless of the real weighting; where the evidence is lopsided, say so.

Cues: `While critics argue` · `supporters maintain` · `The truth, as is often the case, lies somewhere in between` · `pros and cons` · `advantages and disadvantages`

Before: While critics argue the tax is regressive, supporters maintain it funds essential services. The truth, as is often the case, lies somewhere in between.

After: The tax takes a larger share from low incomes, and the revenue funds the bus network. Whether that trade is worth it depends on who rides the bus.

Do not flag: A genuine two-sided comparison that names the sides, their evidence and a criterion for choosing is analysis, not padding. Policy and report genres carry more balance vocabulary by nature, so count against the genre's norm. Neutral-point-of-view encyclopedia writing is required to present both sides. A trade-off table is a form, not a hedge. Flag when the balance is manufactured, when one side is padded to match the other, or when the author plainly holds a view the text refuses to state.

### Reader-directed closer (endorsement, CTA, obligation) `call-to-action-closer`

Severity: **cluster** · Scope: universal

A closing line instructs the reader instead of saying anything: the social endorsement sign-off ('This one is worth your time:', 'Bookmark this.', 'Do yourself a favor and read this.', 'Thank me later.'), the landing-page invitation ('Let's Connect!', 'Drop me a message', 'I'm always happy to hear from fellow Wikimedians!'), and the policy-report obligation ending where paragraph after paragraph closes on 'there is a need to' (Korean ~할 필요가 있다). It is generic and demonstrative-anchored, so it would sit under any link. Say what the thing is and who it is for, then drop the call to action.

Cues: `This one is worth your time:` · `This one's a must-read:` · `I highly recommend giving this a read.` · `Do yourself a favor and read this.` · `You won't want to miss this one.` · `Save this for later.` · `Bookmark this.` · `Don't sleep on this one.` · `Trust me, you'll want to read this.` · `Thank me later.` · `Let's Connect!` · `Drop me a message` · `Have a suggestion, correction, or just want to say hi?` · `I'm always happy to hear from fellow Wikimedians!` · `Gratitude`

Before: This one is worth your time:

After: Sarah's write-up of why context windows leak, the clearest version I have found for anyone debugging a RAG pipeline.

Do not flag: A newsletter, a landing page or a campaign email is allowed one real call to action, and a recommendation carrying a reason is a review ('read the appendix if you run Postgres 14; the lock behaviour changed'). One obligation sentence in a policy report is normal, the tell is two or more paragraphs in a row ending that way. Encyclopedic, technical and documentation prose should carry none.

### Clean-consequence connector (unearned inevitability) `clean-consequence-connector`

Severity: **cluster** · Scope: universal

A connector asserts that the conclusion follows automatically from what came before, lending inevitability the argument has not earned: 'comes straight out of this', 'falls out of', 'follows directly', and the paragraph closer that declares a consequence with no path (Korean 결국 ~로 이어진다, '(ultimately) leads to'). Show the inference, or replace the connector with the step that produces it.

Cues: `The cost the essay described comes straight out of this` · `falls out of` · `follows directly`

Before: The cost the essay described comes straight out of this.

After: Each retry re-reads the manifest, which is where the extra 200 milliseconds come from.

Do not flag: In mathematics and formal proofs 'follows directly' is a precise claim about a derivation and stays. A connector is fine when the inference is actually shown in the same paragraph; the defect is inevitability asserted over a gap.

### Colon reveal (staged payoff after a colon) `colon-reveal`

Severity: **cluster** · Scope: universal

A setup clause, a colon, then a tidy payload in lower case: the colon is used for suspense rather than to introduce a list, a label or a quote ('The detail that makes it work: a separate agent grades it', 'not a style but an attractor: the center of gravity of a distribution'). Rewrite as a plain sentence. In Dutch house copy the same shape is the aanloop-dubbelepunt-clou.

Cues: `The detail that makes it work:` · `The best part:` · `not a style but an attractor: the center of gravity of a distribution` · `a measurable claim: markers per thousand words`

Before: The detail that makes it work: a separate agent grades it.

After: A separate agent does the grading, which is what makes it work.

Do not flag: Colons introducing a list, a definition, a label, a quotation, a ratio or a time are ordinary. Headings, table cells and code do not count. One colon reveal in a piece is a stylistic choice; the tell is the shape recurring, especially alongside a contrastive binary before the colon. The shape is left to the regex and to a reader; a bare colon is not a cue, because it also carries every list, label, ratio and heading in the document.

### Deeper-truth framing and the reframe `deeper-truth-framing`

Severity: **cluster** · Scope: english

A stock phrase presents an ordinary point as a hidden or fundamental insight, or asserts that the matter is obvious instead of showing it: 'the real question is', 'at its core', 'what really matters', 'the heart of the matter', 'make no mistake', 'the truth is', 'The reality is simpler', 'History is unambiguous on this point', and the reveal that waves away everything said so far ('but none of them is the real story. The real story is...'). The reframe variant repositions the question as a setup for the writer's preferred version ('Better posed:', 'the harder skill is usually'). Drop the frame and state the point.

Cues: `The real question is` · `at its core` · `but in reality` · `what really matters` · `the deeper issue` · `the heart of the matter` · `make no mistake` · `The truth is simple` · `The reality is simpler` · `History is unambiguous` · `the metrics are clear` · `the examples are clear` · `but none of them is the real story` · `The real story is` · `Better posed:` · `the harder skill is usually`

Before: The real question is whether teams can adapt. At its core, what really matters is organisational readiness.

After: Whether teams adapt depends on whether the organisation changes its habits.

Do not flag: A genuine reframing that names what the first question missed and then answers the better one is argument. 'In reality' contrasting with a stated appearance is ordinary. If you have to tell the reader the point is clear, it usually is not, but a summary of evidence already laid out may legitimately say so.

### Fake-casual register (props instead of a voice) `fake-casual-register`

Severity: **cluster** · Scope: english

The costume a model puts on when asked for a lowercase-casual social voice: a kit of props that outsource drama to the prop instead of the content. Six recurring props are the one-word verdict closer ('wild.', 'insane.', 'unhinged.'), asterisk stage directions ('*checks notes*', '*chef's kiss*', '*mic drop*', '*sips coffee*'), wink asides ('(yes, really)', '(no, seriously)'), label-prefix openers ('hot take', 'fun fact', 'pro tip', 'PSA', 'unpopular opinion'), the resigned-irony tag 'because of course it does', and the self-QA volley ('Is it fast? Yes. Is it cheap? Also yes.'). A post can clear every vocabulary check and still wear this costume. Replace the prop with the specific surprise.

Cues: `wild.` · `insane.` · `unhinged.` · `*checks notes*` · `*chef's kiss*` · `*mic drop*` · `*takes a deep breath*` · `*sips coffee*` · `*sips tea*` · `*nervous laughter*` · `(yes, really)` · `(no, seriously)` · `(yes, seriously)` · `(no, really)` · `hot take` · `fun fact` · `pro tip` · `unpopular opinion` (+2)

Before: Ships in 40ms. *checks notes* yes, really. wild.

After: It answers in 40 milliseconds, measured over 10,000 requests on a cold cache.

Do not flag: A writer whose established voice already runs on these props keeps them; the register is a tell for imposed casualness, not a ban on playfulness. The ordinary grumble uses the same words as the wink ('the build failed because of course it did'), and a human can deploy a wink aside on purpose. The asterisk stage directions and the four (yes|no) x (really|seriously) winks are the deterministic half; verdict closers, label prefixes and the self-QA volley need register judgement. '*checks calendar*' and '(yes, honestly)' are disclosed misses.

### Flat affect (one tone, no engagement) `flat-affect`

Severity: **cluster** · Scope: universal

A single tone is held for a whole piece with no drift from analytical to angry to tender, the cadence never varies, and the interactional markers of an argumentative voice thin out: fewer questions, fewer asides, less direct address to the reader. Measured against human writing in the same genre, the prose reads evenly warm and evenly distant at once. Let the register move where the subject moves.

Cues: `no register shift` · `cadence never varies` · `fewer engagement markers`

Before: The outage lasted six hours. The team responded promptly. Customers were informed. The postmortem was completed.

After: The outage ran six hours. A customer emailed us before our own alerting did, which still stings.

Do not flag: Reference documentation, standards, legal text and academic abstracts hold one register on purpose. Long-form fiction from a model holds voice consistently too, which makes this weak evidence at paragraph level; judge across a whole piece and against the genre.

### Historical analogy stacking `historical-analogy-stacking`

Severity: **cluster** · Scope: universal

A rapid-fire list of past technologies, companies or revolutions is invoked to borrow their weight: 'like the printing press, the telegraph, and the internet before it', 'Apple didn't build Uber. Facebook didn't build Spotify. Stripe didn't build Shopify.', 'Take Spotify... Or consider Uber... Airbnb followed a similar path...'. The montage substitutes for the argument, and no single parallel is examined. Name the one parallel that does analytical work and say what it explains, or cut.

Cues: `like the printing press, the telegraph, and the internet before it` · `Apple didn't build Uber` · `the web, mobile, social, cloud` · `Every major technological shift` · `followed the same pattern` · `Take Spotify` · `Or consider Uber` · `followed a similar path` · `is another example` · `Even Discord`

Before: Like the printing press, the telegraph, and the internet before it, this changes distribution.

After: Like the telegraph, it separates the message from the messenger, so newsrooms can file from anywhere.

Do not flag: A history piece comparing several cases in depth is doing the work. One analogy developed over a paragraph is argument. Especially common in technical writing, where a single well-chosen precedent is often exactly right; the tell is the list with nothing examined. A single named precedent is a cue of nothing: the entry's own repair keeps one ('Like the telegraph, it separates the message from the messenger'), so only the stacked list is listed.

### Metaphor overuse (dead metaphor, generative metaphor) `metaphor-overuse`

Severity: **cluster** · Scope: universal

One figure is introduced and then never dropped: the same figurative noun recurs five to ten times across a piece ('the ecosystem needs ecosystems to build ecosystem value', 'walls and doors' thirty times, 'primitives' in every paragraph), where a human writer would use it once and move on. The related form layers non-idiomatic conceptual metaphors onto argument or report prose, especially sensory predicates evaluating abstractions (Korean 진단은 서늘하다, 'the diagnosis is cool to the touch'). Use the figure once, then say the thing plainly.

Cues: `ecosystem` · `walls and doors` · `primitives` · `same figurative noun recurring`

Before: The ecosystem needs ecosystems to build ecosystem value across the ecosystem.

After: Third-party tools need an API stable enough to build against, which is what we are shipping.

Do not flag: A sustained metaphor can be a deliberate structural device in an essay or a lecture, and domain terms that only look figurative ('tree', 'pipeline', 'garbage collection', 'ecosystem' in ecology) are literal vocabulary. Count recurrence across paragraphs before flagging, not per sentence.

### Narrated candor and performed vulnerability `narrated-candor`

Severity: **cluster** · Scope: english

Announcing one's own disclosure instead of disclosing, or performing self-awareness that costs nothing: 'I want to be upfront:', 'To be fully transparent:', 'in the interest of full disclosure', 'Two caveats I would rather flag than let you discover later:', 'And yes, I'm openly in love with the platform model'. The frame is separable from the content; cut it and the sentence loses no information. Real vulnerability is specific and uncomfortable, this version is polished and risk-free.

Cues: `Two caveats I would rather flag than let you discover later:` · `I want to be upfront:` · `To be fully transparent:` · `Rather than bury this, I'll say it plainly:` · `I could have left this out, but:` · `Being honest about the limitations here:` · `I would rather flag this than let you discover it later` · `in the interest of full disclosure` · `I'd rather ... than` · `And yes,` · `I'm openly` · `since we're being honest` · `I'm looking at you` · `This is not a rant; it's a diagnosis`

Before: Two caveats I would rather flag than let you discover later: the sample is small and the runs were not randomised.

After: Two caveats: the sample is small and the runs were not randomised.

Do not flag: The disclosure itself always stays ('I haven't tested this on Windows', 'the numbers don't reproduce on my hardware', 'this is a mitigation, not a fix'), and a real conflict-of-interest note stays with its frame ('In the interest of full disclosure, I own shares in the company discussed here'). The ordinary comparative is not this pattern ('I'd rather fix it than let you inherit the mess'). Every regex tight enough to spare those carve-outs stops matching the tell, so treat detection as judgement.

### Performed-insight phrase `performed-insight-phrase`

Severity: **cluster** · Scope: english

Essayist tics that announce profundity instead of delivering it: 'sit with that for a moment', 'that's not nothing', 'you already know the answer', 'the punchline is', 'don't take my word for it', 'that's the whole point', 'that's the part nobody mentions', 'the only metric that matters', 'X is dead; long live X'. Each stages a reveal and adds no fact. State the claim the phrase gestures at: 'that's not nothing' becomes the actual size of the thing.

Cues: `sit with that for a moment` · `that's not nothing` · `you already know the answer` · `the punchline is` · `don't take my word for it` · `that's the whole point` · `is the entire business model` · `that's the part nobody mentions` · `the only metric that matters` · `X is dead; long live X` · `that's why it mattered`

Before: That's not nothing.

After: That is four hours a week per engineer.

Do not flag: One hit can be a stylistic choice; several in one piece is the tell. Quoted speech and genuinely comedic writing where a punchline is literal stay. 'The punchline', 'worth naming' and 'batteries included' are kept out of the cues: they have common literal senses that no regex separates ('batteries included' is how the Python docs describe the standard library), so they remain judgement calls. Sentence-initial 'Turns out' is ordinary spoken-register English and is not a cue.

### Phantom rebuttal, straw option and corrective pivot `phantom-rebuttal`

Severity: **cluster** · Scope: english

The text argues with an interlocutor it invented. Sub-forms: the disclaimer of a position nobody put forward ('This isn't mainly about X', 'I'm not arguing that Y doesn't matter', 'To be clear', 'Don't get me wrong'), the straw option raised and dismissed in one clause and never mentioned again ('A tempting approach would be to..., but that would...'), the staged self-debate ('It would be wrong, though, to call the difference padding'), and the anticipate-and-rebut reversal that voices a reading and knocks it down in a two-word sentence ('as though it carried no stance. It carries one'). Usually residue of an earlier draft. Remove the invented objection and state the real constraint.

Cues: `This isn't (mainly/really) about` · `I'm not saying/arguing/trying to` · `To be clear` · `Don't get me wrong` · `This is not to say` · `You could argue/frame this differently but` · `Some might say... but` · `A tempting option/approach would be` · `One might be tempted to` · `An obvious approach would be` · `You might think... but` · `It would be easy to just` · `Some would suggest` · `It would be wrong, though, to call the difference padding` · `as though it carried no stance. It carries one`

Before: This isn't mainly about prompt length, and I'm not arguing that documentation doesn't matter. The issue is whether the agent can use the instruction when it acts.

After: The issue is whether the agent can use the instruction when it acts.

Do not flag: An objection whose source is named, or which the text then answers in full, is argument. A design document, tutorial or RFC should record the alternatives a reader would actually consider, with the reason each was rejected. A direct factual negation is not this pattern ('the API is not thread-safe'). One rejected option may be real; several short unrelated rejections are the sign.

### Pull-quote density (every line engineered to land) `pull-quote-density`

Severity: **cluster** · Scope: universal

Line after line is written to be extractable: over-polished quotable sentences in every paragraph, stacked aphorisms with no connective tissue between them, and short one-line paragraphs or fragments placed for dramatic effect. The tell is the density, not one good line. Keep the strongest one and let the rest be ordinary sentences that carry argument.

Cues: `pull-quote-ready lines` · `every line a pull-quote` · `staccato drama` · `one-line paragraph for effect`

Before: Speed is a choice.

So is silence.

And silence is expensive.

After: We chose to ship weekly. That meant telling customers about outages within the hour, which costs about two hours of support time per release.

Do not flag: Poetry, aphorism collections and deliberately staccato voices (columns, stand-up, some fiction) run on this by design. A single colourful line the author wrote themselves stays; when in doubt, keep it. Count across paragraphs before flagging.

### Reflexive AI-humility move `reflexive-ai-humility`

Severity: **cluster** · Scope: english

The writer flags that it is itself a language model, or that its own claims may be wrong, as a gesture of modesty rather than as a limit on a specific claim: 'this essay is written by one of the systems under examination', 'Most of the above is structured impression, and could be wrong'. Self-identification is a chatbot leftover in any human-voiced text and always comes out; the 'could be wrong' variant should be replaced by naming which claim is uncertain and why.

Cues: `this essay is written by one of the systems under examination …` · `Most of the above is structured impression, and could be wrong` · `is a small instance of that, and no evidence of anything finer`

Before: Most of the above is structured impression, and could be wrong.

After: The timing numbers come from one machine and one run; the ordering held across three repeats, the absolute values did not.

Do not flag: A real limitation attached to a named claim stays ('I could not test this on Windows'). A methods section stating the confidence of a measurement is doing the same job properly. Disclosure of AI assistance where a venue requires it is policy, not a tell.

### Reflexive hedging (uniform hedge density) `reflexive-hedging`

Severity: **cluster** · Scope: universal

Calibration words ('almost', 'tends to', 'roughly', 'largely', 'with few exceptions') and evidential endings ('appears to', 'is judged to', 'is considered', 'seems', Korean ~로 보인다 / ~로 판단된다) are applied to every claim, so they read as a verbal reflex instead of tracking real uncertainty, and unsolicited caveats accumulate around claims that did not need them. Detect hedge density per sentence and repetition of the same hedge rather than any single hedge. The mirror image is a human counter-indicator: committed superlatives and definitive statements ('one of the best', 'is the only', 'was the first') appear more in human writing, so do not hedge those away.

Cues: `almost` · `tends to` · `with few exceptions` · `roughly` · `largely`

Before: The index almost always tends to be roughly the bottleneck, and it largely seems that the cache is, with few exceptions, the second.

After: The index is the bottleneck. The cache comes second.

Do not flag: A hedge covering an unverified claim stays until the claim is verified, and rewriting a source's 'judged low' into 'low' is a modality violation. Technical and documentation registers tolerate 'may' as accuracy. A committed superlative is evidence of a human hand, not a fault to be softened, though a house style guide may still ask for attribution. The committed forms 'one of the best', 'is the only' and 'was the first' are counter-indicators, not cues: they point at a human hand and are never flagged by this entry.

### Significance signaling (framing before the content lands) `significance-signaling`

Severity: **cluster** · Scope: english

A clause tells the reader that what follows is significant, or how to read it, instead of letting it be: 'This matters because', 'That reduction is useful, because', 'That last part matters more than it sounds', 'The key point is', 'As you can see', 'In other words' restating what was just said. The justification is placed before the assertion it serves, so the claim arrives inside a frame telling the reader how to take it. Put the claim first and let the explanation follow, or drop it.

Cues: `That last part matters more than it sounds` · `The key point is` · `As you can see` · `This distinction matters` · `That reduction is useful, because` · `This matters for the comparison, because.` · `this matters because…` · `what's going on here is…`

Before: This matters because it changes how the scheduler behaves under load.

After: Under load the scheduler drops the lowest-priority queue first.

Do not flag: A causal explanation that adds a fact is not signposting ('this matters because the certificate expires on Friday'). 'In other words' earning a genuinely new formulation, and reader guidance in teaching material aimed at beginners, both stay. The tell is a frame that could be deleted without losing information. 'In other words' is left out of the cues because the restating use and the reformulating use share one string; it stays a reader's judgement. This entry owns 'This matters because', which meta-signposting no longer lists.

### Speculative scenario opener (Imagine a world where) `speculative-scenario-opener`

Severity: **cluster** · Scope: english

An argument opens with a hypothetical world that lists desirable outcomes instead of making a claim: 'Imagine a world where every deploy is instant', 'Picture a future in which', 'Envision a world where'. The scenario does the persuading and no evidence follows; the payoff is always that the reader has accepted the premise. Cut the hypothetical and state the real claim.

Cues: `Imagine a world where…` · `Picture a future in which…` · `Envision a world where…`

Before: Imagine a world where every deploy is instant.

After: Instant deploys would cut our release cycle from a day to minutes.

Do not flag: Fiction, and a thought experiment with a stated payoff, are the form working as intended. Instructional 'imagine you have a sorted array' points at a concrete example and is a teaching device. 'Consider a scenario where' is deliberately excluded because it reads as ordinary analytic prose. Bare 'imagine' is not a cue; it fires on the teaching device this note already exempts and on ordinary prose ('I cannot imagine Lincoln refusing his assent'). This entry is about the opening move, so a continuation such as 'in that world' is not it either.

### Didactic disclaimers and unsolicited caveats `didactic-disclaimers`

Severity: **context** · Scope: english

Advice-to-the-reader disclaimers in text that should simply state facts: 'it's important to note', 'it's crucial to remember', 'always check before you use something', jurisdiction-varies warnings ('may vary'), 'to prevent confusion' disambiguation, and the closing recommendation that the reader go consult a source themselves ('For deeper insights, listening to tracks on platforms like Spotify or Deezer is recommended, as lyrics and production details aren't fully documented'). Remove caveats the reader did not ask for and the claim does not need; keep one only when it changes what the reader should do.

Cues: `it's critical to note` · `it's crucial to note` · `important to consider` · `worth noting` · `may vary` · `It is crucial to differentiate` · `to prevent confusion` · `However, it's important to note` · `It's important to remember` · `For deeper insights` · `listening to tracks on platforms like Spotify or Deezer is recommended`

Before: However, it's important to note that these caucuses operate outside the formal ANC structure and their influence on policy decisions may vary.

After: These caucuses operate outside the formal ANC structure.

Do not flag: Requested caveats, material safety and legal notices, and any warning that changes what the reader will do all stay. A real citation is not a recommendation to go look. Largely a historical tell from 2022-2024 models and much rarer in newer output, but still useful on older text.

### Invented crowd contrast (forced contrarianism) `invented-crowd-contrast`

Severity: **context** · Scope: english

A claim is propped on an implied lagging crowd nobody named: 'Everyone says X, but they're wrong', 'the conventional wisdom is backwards', and the date-stamped trailing clause 'while everyone else was still debating timelines', 'while the industry wrote thinkpieces', 'while everyone else played catch-up'. The foil is invented, so the contrast costs nothing and the writer wins for free. State the fact and cut the crowd clause, or name the actual competitor and what they did.

Cues: `Everyone says X, but they're wrong` · `the conventional wisdom is backwards` · `while everyone else was still debating timelines` · `while the industry wrote thinkpieces` · `while everyone else wrote think-pieces` · `while everyone else played catch-up`

Before: We shipped it in 2022, while everyone else was still debating timelines.

After: We shipped in 2022. The next vendor to ship a comparable feature was Acme, in late 2023.

Do not flag: Literal simultaneity is ordinary narrative ('she read while everyone else watched the movie'). A contrarian claim is legitimate when the source actually argued it and the crowd position is quoted or cited. 'While the market was still speculating about the price' can be literally true; accept that residue rather than loosening the crowd list.

### Launch-copy dramatic introduction (Meet X, your new favorite Y) `launch-copy-introduction`

Severity: **context** · Scope: english

A product is introduced like a game-show contestant instead of described: 'Enter Flowdesk.', 'Meet Flowdesk, your new favorite treasury dashboard', 'Say hello to Flowdesk', 'Think Notion meets Figma'. Near-deterministic in short launch and announcement copy. Say what the thing does and for whom.

Cues: `Enter Flowdesk.` · `Meet Flowdesk, your new favorite treasury dashboard` · `Say hello to Flowdesk` · `Think Notion meets Figma` · `your new go-to` · `the new home of` · `the new way to` · `the new standard in` · `the new standard for` · `Enter X.` · `Say hello to X` · `Meet X, your new [role]`

Before: Meet Flowdesk, your new favorite treasury dashboard.

After: Flowdesk shows a fund's full treasury position on one screen.

Do not flag: Bare 'Enter X.' is a UI instruction ('Enter Password.'), a stage direction ('Enter Hamlet.') or column narrative ('Enter Rashford.'). 'Say hello to Grandma.' and 'Meet Sarah, your new account manager' are how people introduce colleagues, pets and babies; flag those only in launch or announcement copy, by judgement. Two-token product names ('Meet North Star') are a deliberate miss rather than a looser pattern.

### Lingering-attention claim (the line I keep coming back to) `lingering-attention-claim`

Severity: **context** · Scope: english

A share post opens by claiming the thing has occupied the writer's mind for a duration, before the reader has any reason to care: 'the line I keep coming back to', 'I can't stop thinking about this', 'still thinking about this one', 'this has been rattling around in my head all week'. Unfalsifiable and self-flattering; the frame implies the quote earned repeat visits without showing what it earned them with. Open on the thing itself.

Cues: `the line I keep coming back to` · `I can't stop thinking about this` · `still thinking about this one` · `this has been rattling around in my head all week` · `I've been chewing on this since Tuesday`

Before: The line I keep coming back to: agents are teenagers.

After: Jeetu describes AI agents as teenagers.

Do not flag: The frame stays when the sentence says why the thing recurred ('I keep coming back to Hirschman's exit-voice framing because it predicts which engineers quit and which file the RFC'). Bare 'I keep coming back to X' with a reason clause after it is legitimate, which is why the noun-anchored form is the detectable one.

### Patronizing analogy (Think of it as, less a hammer more a scalpel) `patronizing-analogy`

Severity: **context** · Scope: english

An unrequested analogy is offered in place of the claim or the instruction: 'Think of it as a Swiss Army knife for your workflow', 'Think of it like a highway system for data', 'It's like asking someone to buy a car they are only allowed to sit in', and the paired-image form 'Less a hammer, more a scalpel', which hands the reader two pictures and no advice. The model defaults to teacher mode even for expert readers. Say what the thing does, or what to do.

Cues: `Think of it as` · `Think of it like` · `It's like asking` · `Less a hammer, more a scalpel.` · `Less X, more Y`

Before: Think of it as a Swiss Army knife for your workflow.

After: It runs shell tasks and posts the results to Slack from one config file.

Do not flag: Genuinely introductory material for a lay audience is where analogy earns its place, and an analogy followed by the concrete instruction is a lesser offence than one standing in for it. Flag when the audience is expert, or when the analogy is murkier than the thing it explains.

### Register mismatch (press-release voice by default) `register-mismatch`

Severity: **context** · Scope: universal

The register is chosen by habit rather than by context: a polished corporate answer to a casual question, sentences that read like a press release when spoken aloud, and the friendly-helpful conversational default that reinforcement training rewards. Read it out loud; where a sentence sounds like communications rather than a person talking, rewrite it in the words you would say, and match the tone and stakes of the prompt.

Cues: `press release` · `polished, lifeless, AI-sounding prose` · `Match tone to context. Casual question, casual answer.`

Before: We are pleased to announce that we have identified an opportunity to enhance the deployment experience for our users.

After: Deploys are about a minute faster now.

Do not flag: An actual press release, an investor update or a legal notice is written in that register on purpose. A chatty, helpful tone is part of the trained-in style and is not by itself evidence of a human author, nor of an AI one; judge it against what the context asks for.

## Vocabulary

### Canned stock sentence (I hope this email finds you well) `canned-stock-sentence`

Severity: **always** · Scope: english

A whole prefabricated sentence that acknowledges nothing specific: I hope this email finds you well; I recently had the pleasure of X-ing; the subject maintains an active social media presence / a strong digital presence and actively shares the latest updates. Say what happened, or open on the actual reason for writing.

Cues: `I hope this email finds you well` · `I recently had the pleasure of` · `maintain an active social media presence` · `maintains an active social media presence` · `maintains a strong digital presence` · `actively shares the latest updates and events` · `demonstrated excellence in digital promotions`

Before: I recently had the pleasure of attending their meetup.

After: I went to their meetup on Thursday.

Do not flag: 'Had the pleasure of' is sincere in a genuine thank-you or a tribute where the pleasure is the point. A social-media presence is worth documenting when the article cites follower counts, a controversy or a source; the tell is the empty assertion of activity followed by praise of the posting. The social-presence wording in particular is idiosyncratic to machine text and was uncommon before 2024.

### Generic scene-setting opener (In today's fast-paced world) `generic-scene-setting-opener`

Severity: **always** · Scope: english

An opening phrase that situates the topic in a generic present or an unnamed trend instead of naming the specific occasion: In today's X, In an era where, In the age of, In the ever-evolving landscape of, In the rapidly evolving world of, Imagine a scenario where. Cut it, or state the actual context that made this worth writing. The full formula pairs the opener with an inflated head noun ('In the rapidly evolving world of X, Y has emerged as a leading force') or the 'has become increasingly important' tail; it is interchangeable across topics, which is what makes it a tell.

Cues: `In today's fast-paced world` · `In the ever-evolving landscape of` · `Imagine a scenario where` · `In the realm of` · `In an era where` · `In today's rapidly evolving digital landscape…` · `In an ever-evolving landscape…` · `In the age of` · `In the world of` · `In the rapidly evolving world of...` · `In the rapidly evolving world of…` · `In an age where` · `has emerged as a leading force` · `has become increasingly important`

Before: In today's fast-paced world, teams need better tooling.

After: Our release took four hours last Friday, so we rebuilt the pipeline.

Do not flag: 'In today's' is legitimate when followed by something genuinely dated and specific ('in today's build', 'in today's release notes'). A historical essay may need 'in the age of Napoleon'. The tell is a broad present tense standing in for a reason to write, not the words alone. Bare 'has emerged as a' is ordinary English ('Rust has emerged as a serious systems language'), so the inflated head noun is what carries the flag.

### Hollow intensifier (genuinely, truly, to be honest) `hollow-intensifier`

Severity: **always** · Scope: universal

Sincerity and emphasis markers that assert conviction instead of supplying a fact: genuinely, truly, quite frankly, to be honest, let's be clear. Dutch does the same with echt and gewoon used as filler. Cut the word and state the fact; the default fix is deletion.

Cues: `genuinely` · `truly` · `quite frankly` · `to be honest` · `let's be clear` · `it's worth noting that` · `echt` · `gewoon`

Before: Quite frankly, the API is slower than the old one.

After: The API is slower than the old one.

Do not flag: Keep any of these inside a quotation, and keep a warm hedge that belongs to the writer's spoken voice in a deliberately casual register. Dutch 'echt' and 'gewoon' are ordinary words and are only a tell as filler that carries no meaning, which is why they stay prose cues rather than regex. 'Actually', 'very' and 'incredibly' are scored by degree-adverb-padding at its context tier, and 'real', 'genuine' and 'true' bolted to an abstract noun by real-actual-adjective-inflation; score each once, there.

### Announcement frame ('it's worth noting that') `it-is-worth-noting-frame`

Severity: **always** · Scope: english

A clause that announces that the next statement matters instead of making it: it's worth noting that, it's important to note that, it bears mentioning, the reality is that. Delete the frame and keep the content; if the sentence loses nothing, the frame carried nothing.

Cues: `It's important to note that` · `It is important to note that` · `It's worth mentioning that…` · `It bears mentioning` · `it's worth noting that…` · `It's important/worth noting that...` · `The reality is that`

Before: It's worth noting that the build time dropped by half.

After: The build time dropped by half.

Do not flag: Legitimate where the note really is an aside that would otherwise read as part of the main claim, and in legal or technical writing where 'note that' flags a genuine exception the reader will otherwise miss. A single instance in a long piece is noise; the fix is still deletion, because the sentence almost always survives it intact.

### 'Let's' invitation opener (let's dive in, let's unpack this) `lets-invitation-opener`

Severity: **always** · Scope: english

A section or paragraph opened with a 'Let's …' invitation: let's dive in, let's delve into, let's unpack this, let's break it down, let's explore, let's take a look. It stages a shared journey and postpones the point by one sentence. Delete the opener and begin at the claim.

Cues: `let's dive in` · `Let's break it down` · `Let's unpack this` · `Let's delve into` · `Sit with that for a moment` · `Let's explore how ...` · `Let's break this down.` · `let's take a look` · `let's examine` · `let's walk through` · `Let's dive into` · `Let's dive in` · `Let's jump in` · `Let's get into it` · `Let's start with the basics`

Before: Let's dive into how the scheduler works.

After: The scheduler polls every 200ms and drops anything older than a minute.

Do not flag: A genuine first-person-plural invitation in a workshop script, a talk transcript or teaching material is the right register there. 'Let's be clear' is a candor flag handled with the hollow intensifiers, not here. 'Let's dive in' as a pasted chat opener is also catalogued with the chatbot artifacts; score it once.

### Literal light-verb constructions (have / make / take / give + noun) `light-verb-literalism`

Severity: **always** · Scope: universal

An English light-verb construction ('have strong competitiveness', 'make a decision', 'take action', 'give support') is carried over word for word as verb + noun, where the target language says the same thing with a single predicate or a double-subject construction. In Korean this surfaces as 가지고 있다 for every 'have'; in Dutch it surfaces as the maken/make calque ('een beslissing maken' for 'een besluit nemen', 'impact maken'). Reduce the pair to the predicate the noun is hiding.

Cues: `have + noun` · `make + noun` · `take + noun` · `give + noun`

Before: 강한 경쟁력을 가지고 있다

After: 경쟁력이 강하다

Do not flag: 가지고 있다 for physical possession of a concrete object is native Korean (나는 그 책을 가지고 있다), as is 가지고 가다/오다 ('take along'); the tell is an abstract quality as object: 경쟁력, 가능성, 중요성, 의미. In Dutch, 'een besluit nemen' and 'een keuze maken' are correct idiom and must not be flagged; only the maken-for-nemen calque and 'impact maken' are. An English light verb inside English prose is wordiness, not translationese, and belongs to the syntax and vocabulary categories; the English cues here name what is being calqued from, which is why this entry carries no English regex.

### Topic-framing filler (when it comes to, at its core, at the end of the day) `topic-framing-filler`

Severity: **always** · Scope: english

Idioms that introduce a topic or announce a summary while carrying no information: when it comes to, at its core, at the heart of, at the end of the day, the reality is, the truth is, here's the thing, let me be clear, going forward, in this article, in the world of. Cut the phrase and start the sentence at its subject; with a warm-up opener, start one sentence later.

Cues: `in today's world` · `in the age of` · `in the world of` · `the reality is` · `in terms of` · `with regard to` · `going forward` · `in this article` · `let's dive in` · `At its core...` · `At the heart of…` · `When it comes to...` · `At the end of the day...` · `Here's the thing.` · `Let me be clear.` · `The truth is.` · `A deeper understanding of…` · `That said` (+1)

Before: When it comes to caching, the main risk is staleness.

After: The main caching risk is staleness.

Do not flag: Keep an occasional one where it is part of the writer's recognisable voice and the sentence still earns its place; the defect is delay, not the words themselves. 'The truth is' can be a real correction of something just claimed. 'That said' is a legitimate concessive pivot when the concession is real, though 'but' or 'yet' usually does the same work; do not overuse any one of those replacements either. 'At the heart of' is fine when describing a literal centre. 'Sit with that for a moment' is scored by lets-invitation-opener, and the testament, delve, dive-deep and nuanced openers by ai-vocabulary-lexicon; score each once, there. Score 'that said' and 'that being said' at density, roughly two or more per thousand words, rather than on every occurrence, since one concessive pivot is ordinary English.

### Trendy colloquialism ('hits different') `trendy-colloquialism`

Severity: **always** · Scope: english

A borrowed trend phrase used as a shortcut to sound relatable without earning the emotional beat: hits different, hit differently. Describe what actually changed, or cut.

Cues: `hit differently` · `hits different`

Before: Reading that changelog hits different.

After: That changelog named the exact bug I spent Tuesday on.

Do not flag: Literal use is exempt ('the second dose hit differently than the first'). Inside quoted speech, or in writing whose register genuinely is that of the phrase's community, it can be the writer's own voice; the tell is a formal piece reaching for it once.

### Circumlocution for a single word (in order to, due to the fact that) `wordy-circumlocution`

Severity: **always** · Scope: english

Multi-word constructions standing in for one word: in order to (to), due to the fact that (because), at this point in time (now), in the event that (if), has the ability to (can), in terms of and with regard to (rewrite). The fix is mechanical substitution; a hit is a wordiness defect, not evidence of machine authorship.

Cues: `In order to` · `Due to the fact that` · `At this point in time` · `In the event that` · `has the ability to` · `It is important to note that` · `in terms of` · `with regard to` · `going forward`

Before: In order to achieve this goal

After: To achieve this

Do not flag: 'In order to' is sometimes needed to prevent a misreading where a bare 'to' would attach to the wrong verb, and legal or contractual drafting uses 'in the event that' as settled language. The edit is good writing regardless of who wrote the sentence, so never present a hit here as authorship evidence.

### Additive-transition pile-up (Moreover, Furthermore, Additionally) `additive-transition-pileup`

Severity: **cluster** · Scope: universal

Formal additive connectives used as paragraph glue, stacked across consecutive sentences: Moreover, Furthermore, Additionally, Consequently. Korean shows the same habit with sentence-initial 또한/따라서/즉/나아가/아울러/게다가/더욱이 and with 하지만/그러나 opening a sentence in every paragraph. Restructure so the connection is obvious, or use and, also, on top of that; delete more than half of the adversatives. The unit is the paragraph: several connective openers inside one paragraph, or an adversative opening every paragraph.

Cues: `Additionally` · `moreover` · `consequently` · `Furthermore`

Before: Additionally, camel meat is common. Moreover, pasta arrived with the Italians. Furthermore, coffee was exported early.

After: Camel meat is common. Pasta arrived with the Italians, and coffee was exported early.

Do not flag: Common transition words in isolation are not a tell: one 'however' is not a finding, and a well-placed 'moreover' in an argument that really is adding a second reason is correct. Flag on density. The Korean rule fires at five or more sentence-initial connectives per document, and the adversative rule only when nearly every paragraph opens with one. Academic and legal writing use these connectives structurally; weigh the register before flagging. Short-form social copy skips the check entirely. One connective that marks a real turn in the argument is fine; the signature is per paragraph.

### Machine-poetry register (whisper, echo, ache, hollow) `ai-poetry-register`

Severity: **cluster** · Scope: english

The narrow lexicon generated verse returns to compulsively: a signature set (heart, embrace, echo, echoes, whisper, whispers) and an emotive abstract-fragile set piled up in place of image (ache, hollow, tether, linger, fragile, fractured, ember, bloom, cradle, ruin, veil, threadbare). Two registers collapsed into one: Instagram poetry and the most-shared anthology pages.

Cues: `heart` · `embrace` · `echoes` · `whispers` · `ache` · `hollow` · `tether` · `linger` · `fragile` · `fractured` · `ember` · `bloom` · `cradle` · `ruin` · `veil` · `threadbare`

Before: a hollow ache lingers in the fragile veil of morning

After: the kettle ticks as it cools, and the window is still cold

Do not flag: Every one of these words is a legitimate poetic word; the tell is accumulation in place of image, not any single use. Literal senses are common in prose (an echo in a canyon, a hollow log, a fragile package, a veil at a wedding), which is why the mood-word regex requires two of them close together. Compare against human-authored poems of the same length before concluding anything; the pronoun over-representation is measured in the flat-lexical-statistics entry.

### AI vocabulary lexicon (delve / tapestry / pivotal) `ai-vocabulary-lexicon`

Severity: **cluster** · Scope: english

A closed list of words whose corpus frequency jumped abruptly after November 2022 and which LLMs reach for regardless of fit. It spans three families that behave identically: figurative verbs used where a concrete one belongs (delve, showcase, underscore, leverage, embark, unpack, garner, shed light on, pave the way), grand abstract nouns borrowed for prestige (tapestry, realm, beacon, landscape, paradigm, mosaic, labyrinth, symphony, bedrock, odyssey, testament), and stock compounds (cutting-edge, game-changer, ever-evolving, deep dive, best practices, thought leadership, at its core, watershed moment, only time will tell). Replace each with the plain word the sentence needs, or cut the clause when it carried no claim. Within the list a small always tier holds regardless of density, the words the register exceptions below refuse to excuse: delve, tapestry, rich tapestry, beacon, testament to, stands as a testament to, embark, game-changer, ever-evolving landscape and navigating the complex landscape. Every other word here is a finding at density, two or more distinct ones in a paragraph, the threshold elevated-vocabulary-cluster carries.

Cues: `delve into` · `delves` · `delving` · `rich tapestry` · `in the realm of` · `beacon` · `stands as a testament to` · `ever-evolving landscape` · `navigating the complex landscape` · `paradigm` · `marking a pivotal moment` · `meticulously` · `seamlessly` · `showcases` · `showcasing` · `underscores` · `underscoring` · `embarks` (+77)

Before: Somali cuisine is an intricate fusion drawing from the rich tapestry of Arab, Indian and Italian flavours, showcasing a pivotal role in global trade.

After: Somali cuisine mixes Arab, Indian and Italian influences. Somali merchants were among the first exporters of coffee beans.

Do not flag: Take each word in the sense listed: highlight and underscore as verbs, key as an adjective, landscape and tapestry as abstract nouns, boasts meaning 'has', gate/gated/gating only in the figurative sense (feature gating and CI quality gates are established technical usage). Literal senses are not hits: an underscore is a typed mark and can be incidental music, a realm is a kingdom, embark is boarding a ship, a symphony is an orchestral work, intricate designs are literally intricate, a landscape is scenery, a mosaic is tiles, foster can be a family arrangement. Robust, comprehensive, seamless, ecosystem, leverage (of actual platform leverage or APIs), facilitate, underpin and streamline pass in technical writing; still flag delve, tapestry, beacon, embark, testament to and game-changer there. A word being overused does not condemn its synonyms. One or two hits are coincidence and prove nothing about authorship; many of them many times in one post-2022 text is among the strongest available tells, and where there is one there are usually others. Native speakers of Nigerian, Indian and other post-colonial Englishes use delve and other formal diction natively, so a single hit from such a writer is not evidence. Preserve any of these words inside a quotation or when discussing the word itself. Load-bearing, hit differently, hits different, quietly, genuine and genuinely are scored by load-bearing-metaphor, trendy-colloquialism, understated-significance-adverb and hollow-intensifier; score them once, there.

### Stock multi-word boilerplate (repeated or stacked) `boilerplate-phrase-stack`

Severity: **cluster** · Scope: english

Two- and three-word phrases that are individually unobjectionable but stack heavily in generated content, worst in crypto, web3, DePIN and AI-infrastructure writing: emerging sector/space/category, the integration of, the intersection of, community-driven, long-term sustainability, user engagement, decentralized compute, (sustainable) reward emissions, tokenized incentive structures, designed for long-term X. Flag one phrase used twice, or three distinct phrases from the family anywhere in one piece even if each appears once.

Cues: `emerging sector` · `emerging space` · `emerging category` · `the integration of` · `the intersection of` · `community-driven` · `long-term sustainability` · `user engagement` · `decentralized compute` · `sustainable reward emissions` · `tokenized incentive structures` · `designed for long-term`

Before: A community-driven project at the intersection of decentralized compute and user engagement, designed for long-term sustainability.

After: Node operators vote on the fee split, and rewards come from the 0.3% swap fee rather than from emissions.

Do not flag: The per-phrase threshold (two uses) is lower than for single words because repeating the same two-word boilerplate is stronger evidence than re-using 'significant'. Overlapping spans count once, so 'designed for long-term sustainability' is one hit rather than two. In a paper actually about system integration or about a named sector, these phrases can be the accurate technical description; weigh whether the sentence names anything specific. Three or more distinct phrases in one short piece is near-dispositive on social-length posts and should outweigh a low per-phrase count.

### Confidence-calibration adverbs (Notably, Importantly, Interestingly) `confidence-calibration-adverb`

Severity: **cluster** · Scope: english

Sentence adverbs that tell the reader how to feel about a fact instead of letting the fact carry itself: Notably, Importantly, Interestingly, Surprisingly, Significantly, Crucially, Certainly, Undoubtedly, Without a doubt. The tell is stacking, not the individual word.

Cues: `Interestingly` · `Surprisingly` · `Importantly` · `Significantly` · `Notably` · `Certainly` · `Undoubtedly` · `Without a doubt` · `Crucially` · `inherently` · `inevitably`

Before: Notably, the build time dropped by half. Importantly, memory use fell too.

After: The build time dropped by half and memory use fell with it.

Do not flag: One 'notably' in a two-thousand-word piece is fine; three in five hundred words is emphasis stacking. The detector gates on three or more raw hits before deduplication, because the stacking is the signal rather than the vocabulary. 'Significantly' in a statistical sense and 'certainly' inside reported speech or a concessive ('it is certainly true that, but') are not hits. Warm hedges in a casual voice ('honestly', 'I think') are kept while the corporate ones are cut. 'Inherently' and 'inevitably' are also cues of degree-adverb-padding at its context tier; score them there unless they open a sentence with a comma inside a stack of these adverbs.

### Dense AI vocabulary composite (corroborator) `dense-ai-vocabulary-composite`

Severity: **cluster** · Scope: english

A composite threshold rather than a phrase: at least 150 words, at least five distinct hits from the always-flag lexicon, at least two paragraphs carrying an elevated-vocabulary cluster, and at least one stock transition, all in the same text. The combination is treated as a strong corroborator on its own; no single tier is enough, because each overlaps with legitimate technical idiom. It is a detector threshold rather than a phrase to rewrite, so it carries no before-and-after pair; the repair is the one its component entries prescribe, rebuilding the piece around the two or three things it actually reports.

Cues: `wordCount >= 150 && tier1Distinct >= 5 && tier2Clusters >= 2 && hasTransition`

Do not flag: The 150-word gate exists so a short ESL sentence or an adversarial fragment cannot trip it. Systems-programming prose legitimately carries robust, comprehensive, leverage and ecosystem, which is exactly why one tier alone is never enough. Note the implementation discrepancy in the source: its comment says four distinct lexicon hits while its code requires five; prefer the stricter five.

### Elevated vocabulary cluster (2+ buzz words in one paragraph) `elevated-vocabulary-cluster`

Severity: **cluster** · Scope: english

Words that are legitimate alone but become a strong signal when two or more appear in one paragraph: inflated verbs (harness, foster, navigate, empower, elevate, unleash, streamline, bolster, spearhead, facilitate, catalyze, cultivate, illuminate, elucidate, augment, unlock, optimize) and their noun and adjective company (ecosystem, cornerstone, myriad, plethora, nuanced, crucial, multifaceted, paramount, poised, burgeoning, nascent, quintessential, overarching, transformative). The paragraph, not the word, is the unit: rewrite it around the concrete action.

Cues: `harness` · `navigate` · `navigating` · `foster` · `elevate` · `unleash` · `streamline` · `empower` · `bolster` · `spearhead` · `resonates with` · `revolutionize` · `facilitates` · `underpinnings` · `nuanced` · `crucial` · `multifaceted` · `myriad` (+35)

Before: The platform empowers teams to harness a thriving ecosystem and foster nuanced collaboration.

After: The platform lets teams reuse plugins other teams publish, and two people can edit one document at once.

Do not flag: One of these words on its own is ordinary English and is not a finding; the threshold is two or more distinct entries in the same paragraph. Ecosystem flags only as a metaphor, never for an actual biological or package ecosystem. Leverage in finance is a term of art. Navigate is exempt when it means literal navigation. Deeply counts only in significance collocations (deeply integrated, deeply committed, deeply rooted); deeply nested and cares deeply never count. Crucial and cultivate in a paragraph that otherwise reads as the writer's own is noise. The replacement suggestions are defaults, not mandates: if the flagged word is clearly the right one, keep it.

### Flat lexical statistics (low TTR, low perplexity, uniform n-grams) `flat-lexical-statistics`

Severity: **cluster** · Scope: universal

Measured rather than read. The text is statistically flatter than human prose on five axes: type-token ratio (distinct words over total), lexical density, sentence-ending diversity, n-gram transition uniformity, and per-token perplexity. Human English prose of 200+ words usually lands around 0.50 to 0.65 TTR; machine text trends flatter and can fall under 0.40 when locked on a small vocabulary loop, and its next word is consistently the expected one. Being a measurement, it carries no before-and-after pair either; the repair is the one described below, broadening what is being said.

Cues: `low TTR` · `low lexical density` · `low ending diversity` · `type-token ratio below 0.40` · `uniform word-triplet transitions` · `low and uniform perplexity` · `tokens >= 200 && ttr < 0.4`

Do not flag: A very low TTR is not proof of machine authorship: narrow topics, technical reference material, controlled vocabularies and second-language writing all legitimately compress vocabulary, and the numeric thresholds are calibrated for English only. Under about 200 words the measure is noise. The post-editese simplification finding is flagged speculative by its own source (the underlying study covered en-de, de-en, es-de, en-fr and zh-en, not Korean). The fix is rarely to run a thesaurus over the text; broaden what is being said instead, naming specific things, citing specific cases, and replacing a reused abstract noun with the concrete instance. The first-person-plural over-representation found in machine poetry (we/us/our) belongs here as a countable signal; the bare pronouns match roughly 150 times per ten thousand words in ordinary prose, so no regex is offered. Detector weight for the TTR axis alone is deliberately low.

### Latinate inflation (utilize, commence, serves as) `latinate-inflation`

Severity: **cluster** · Scope: english

Choosing the longer Latinate or euphemistic word where a short Anglo-Saxon one says the same thing: utilize for use, commence for start, ascertain for find out, endeavor for try, demonstrate for show, numerous for many, boasts and features and serves as for has and is, authored for wrote, relocated for moved, attempted for tried, passed away for died. The counter-indicator is the tell in reverse: human writers reach for the plain verb.

Cues: `in order to` · `due to the fact that` · `serves as` · `features` · `boasts` · `presents` · `commence` · `ascertain` · `endeavor` · `demonstrate` · `numerous` · `additionally` · `authored` · `relocated` · `utilized` · `attempted` · `passed away`

Before: The team utilized the new pipeline and commenced testing.

After: The team used the new pipeline and started testing.

Do not flag: Formal vocabulary in a genuinely formal register is not a defect, and these words fire on ordinary professional and academic prose at a meaningful rate; report them separately from the AI-frequency lexicon and never let a wordiness fix push a document toward an authorship claim. 'Passed away' is the right register in an obituary or a condolence. 'Features' is correct where a product genuinely has features, 'presents' where something is literally presented, 'serves as' where a thing substitutes for another. Attempted has a specific legal and medical sense.

### Model-era vocabulary drift (which words are the tell) `model-era-vocabulary-drift`

Severity: **cluster** · Scope: english

Which overused words co-occur shifts by model generation, so the absent word proves nothing and the present cluster roughly dates the text. 2023 to mid-2024 (GPT-4 era): delve, boasts, bolstered, crucial, intricate, interplay, meticulous, pivotal, tapestry, testament, underscore, vibrant. Mid-2024 to mid-2025 (GPT-4o): align with, enhance, fostering, highlighting, showcasing, underscore, vibrant. Mid-2025 on (GPT-5): emphasizing, enhance, highlighting, showcasing plus canned notability vocabulary. Grok output keeps its own fingerprint: superficially scientific words (causal, empirical, correlate) and continued heavy use of underscore. Delve itself peaked between 2023 and early 2024 and dropped sharply through 2025.

Cues: `causal` · `empirical` · `correlate` · `underscore`

Before: Chiang's strategy emphasized military suppression, prioritizing empirical consolidation of power amid fragmented loyalties, which underscores the fragility of the alliance.

After: Chiang put down the holdouts by force to secure their obedience, since their loyalty was already split.

Do not flag: These are not hard cutoffs and give only a rough sense of earlier versus later output. A text with no delve and no tapestry can still be 2025-or-later machine prose, where the tell has moved to highlighting, showcasing and emphasizing plus coverage claims; treat the absence of an old word as no evidence at all. Empirical, causal and correlate are ordinary in genuine scientific writing and only count where the subject matter does not call for them. GPT-4o output (May 2024 to August 2025) deviates further from human writing than other models of the same period, so era matters when calibrating.

### Restatement gloss ('in other words', 즉) `restatement-gloss`

Severity: **cluster** · Scope: universal

A stock phrase announces a paraphrase of what was just said, so the point is delivered twice: in other words, put differently, to put it another way, Korean 즉 (and its variants 곧, 말하자면). Check whether the second version adds anything; if not, delete one of the two.

Cues: `in other words` · `put differently`

Before: The queue drains slowly. In other words, messages pile up.

After: The queue drains slower than it fills, so messages pile up.

Do not flag: A genuine gloss that translates jargon for a lay reader, or restates a formula in words, earns its place. The problem is overuse: the Korean cap is two 즉 per document, and the English equivalent should be about as rare. If the paraphrase is clearer than the original, delete the original instead of the gloss.

### Synonym cycling (elegant variation) `synonym-cycling`

Severity: **cluster** · Scope: universal

The same referent is renamed with a fresh synonym on each recurrence to avoid repeating a word (protagonist / main character / central figure / hero, agent / assistant / tool, developers / engineers / practitioners / builders), a footprint of the repetition penalty rather than a choice. It also shows as whole noun phrases being re-worded ('the constraints of socialist realism' / 'state-imposed artistic norms' / 'the constraints imposed by the Soviet regime'). If the clear word is right, repeat it.

Cues: `same referent renamed on three or more consecutive mentions` · `protagonist... main character... central figure... hero` · `agent / assistant / tool rotation` · `developers… engineers… practitioners… builders`

Before: The protagonist faces many challenges. The main character must overcome obstacles. The central figure eventually triumphs. The hero returns home.

After: The protagonist faces many challenges but eventually triumphs and returns home.

Do not flag: Does not apply when the pieces were generated or written in isolation across separate edits, so a long collaboratively edited article can vary its terms innocently. Non-native writers trained to avoid repetition (Italian schooling teaches it explicitly) do this naturally. Genuine variation for rhythm is normal human writing; the tell is systematic renaming of the same referent on every recurrence. Human writers repeat when the word is right and vary when it feels natural; there is no formula, so do not enforce the opposite rule either.

### Understated-significance adverb (quietly, deeply) `understated-significance-adverb`

Severity: **cluster** · Scope: english

An adverb or its adjective form that asserts subtle importance instead of showing it, making a mundane description feel weighty: quietly (quietly building, a quiet revolution), deeply in significance collocations (deeply integrated, deeply committed, deeply rooted, deeply human), and the neighbouring fundamentally, remarkably, arguably. Cut it, or name the concrete contrast that makes the thing quiet or deep.

Cues: `fundamentally` · `remarkably` · `arguably` · `deeply integrated` · `deeply committed` · `deeply rooted` · `quietly orchestrating workflows, decisions, and interactions` · `the one that quietly suffocates everything else` · `a quiet intelligence behind it`

Before: It has been quietly reshaping how teams ship.

After: Four of the six teams switched to it last quarter without announcing it.

Do not flag: A literal 'quietly' describing sound level is never a hit ('she closed the door quietly'). 'Deeply' counts only in the significance collocations listed; deeply nested, deeply buried and cares deeply are literal and never count, and the bare word fires far too often in innocent prose to match unconditionally. Match the stem, since the adjective form ('a quiet intelligence') does the same work as the adverb.

### Vague praise and hype adjectives (flag at density) `vague-praise-adjectives`

Severity: **cluster** · Scope: universal

Evaluative adjectives and adverbs that assert quality, novelty, scale or importance without a measurable referent: significant, innovative, effective, dynamic, scalable, compelling, unprecedented, exceptional, remarkable, sophisticated, instrumental, plus the marketing superlatives (world-class, state-of-the-art, best-in-class, groundbreaking, unparalleled, revolutionary, transformative) and the performative-enthusiasm set (exciting, incredible, powerful). Korean carries the same set as the hype lexicon 혁신적/획기적/압도적/파격적/폭발적/전례 없는/괄목할 만한. Flag when the text is saturated with them, then replace with a number, a comparison, an example or the concrete property.

Cues: `significantly` · `innovative` · `innovation` · `effectively` · `dynamics` · `scalable` · `scalability` · `compelling` · `unprecedented` · `exceptionally` · `remarkable` · `remarkably` · `sophisticated` · `instrumental` · `world-class` · `state-of-the-art` · `best-in-class` · `groundbreaking` (+17)

Before: An innovative, world-class platform delivering exceptional results and remarkable scalability.

After: The platform handled 40,000 requests a second in the March load test, four times what the old one managed.

Do not flag: These are ordinary words; a single use is not a finding. Detector threshold: one word repeating at or above roughly 3% of the word count with a floor of three occurrences, or three or more distinct hype adjectives in a short piece (the Korean rule is 3+ per document). A significant result in a statistics context, a dynamic in physics or group dynamics, an effective date, and scalable in a capacity discussion are all literal. Nuanced is fine when the nuance is actually argued. Do not simplify a formal word merely for being formal.

### Degree-adverb padding (very, really, just, simply) `degree-adverb-padding`

Severity: **context** · Scope: universal

Intensifying degree adverbs bolted onto predicates that do not need them: very, really, just, literally, simply, incredibly, fundamentally, importantly, crucially, inherently, inevitably; Korean 매우, 정말, 진짜로, 대단히, 극히. Mostly delete, and use a concrete figure or a stronger verb where emphasis is genuinely wanted.

Cues: `just` · `literally` · `honestly` · `simply` · `actually` · `truly` · `fundamentally` · `importantly` · `crucially` · `inherently` · `inevitably` · `very` · `incredibly`

Before: It's really very simple, honestly.

After: It takes one command.

Do not flag: Cut them when they add nothing; keep them when they carry emphasis, uncertainty, contrast, or the writer's natural spoken rhythm. Where the source text is colloquial and the adverb is part of the voice, preserve it; the rule targets adverbs the machine added, not the ones the writer speaks with. These words are ubiquitous in ordinary human prose (they fire many times per ten thousand words on Strunk and Twain), which is why only the stacked form is matched by regex and the single words stay prose cues. Keep 'actually' where it marks a specific correction or an expectation gap the sentence names ('we expected a cache hit; it was actually a miss'), though a direct contrast is usually clearer still.

### Dev-blog boilerplate slogans (it just works, zero config) `dev-blog-boilerplate`

Severity: **context** · Scope: english

Stock simplicity slogans borrowed from developer marketing that stand in for a property you could demonstrate: batteries included, it just works, zero config, sane defaults, small enough to fit in your head. Name the concrete behaviour instead.

Cues: `batteries included` · `it just works` · `zero config` · `sane defaults` · `small enough to fit in your head` · `fits in your head`

Before: Zero config, sane defaults, and it just works.

After: It installs with no config file, and the whole API is six functions.

Do not flag: Quoting a product's own tagline, or discussing the phrase itself, is exempt. 'Batteries included' is deliberately left out of automatic matching because a software slogan and literal package contents share the surface form; judge it by hand. 'It just works out of the box' in a genuine comparison against a tool that needs setup can be the accurate report. Adapted from Simon Willison's LLM cliché highlighter.

### Sudden shift in English variety `english-variety-drift`

Severity: **context** · Scope: english

A mismatch between the author's location, the topic's national ties and the spelling convention used. Several models default to American English unless prompted otherwise, so American spellings in an article about an Indian university written by an Indian editor are a cue, as is a variety switch mid-document. Check the author, the topic and the rest of the article before treating it as anything.

Cues: `American English spelling on non-American topics` · `-ize / -ise mismatch` · `color / colour mismatch`

Before: An article on a British institution that switches from 'organisation' to 'organization' halfway through.

After: One variety throughout, matching the topic's national ties.

Do not flag: Non-native speakers routinely mix varieties, and so do multi-author documents, so treat this only as corroboration and never on its own. Oxford spelling uses -ize in British English legitimately. No regex is offered because a bare -ize match fires roughly five to ten times per ten thousand words on ordinary English prose; the signal is the mismatch with author and topic, which a pattern match cannot see.

### Empty hedging (perhaps, could potentially, seems) `hedging`

Severity: **context** · Scope: english

Softening words and clauses that dilute a claim without expressing real uncertainty: perhaps, could potentially, seems, might, appears, tends to, to be clear, I think, maybe. Each either becomes a concrete claim or disappears. Note the counter-indicator: small hedges are more frequent in human prose than in machine prose, so their presence is weak evidence of a human hand.

Cues: `perhaps` · `could potentially` · `it's important to note that` · `to be clear` · `seems` · `might` · `appears` · `tends to` · `I think` · `maybe` · `to be honest` · `very`

Before: This could potentially improve throughput somewhat.

After: This raised throughput by about 15% in the staging test.

Do not flag: Keep every hedge that expresses real uncertainty, self-awareness or the writer's spoken rhythm: 'I think', 'maybe' and 'to be honest' are on the keep list when they are genuine, and a measurement that really is uncertain must stay hedged. Bare 'seems', 'might', 'appears' and 'tends to' are everywhere in ordinary human prose, so only the stacked and doubled forms are matched by regex. Do not strip hedges when humanising a text, because you would be removing a human signal. Sentence-opening candor flags ('I'll be honest') are cut; genuine mid-sentence hedges stay.

### load-bearing (figurative) `load-bearing-metaphor`

Severity: **context** · Scope: english

The hyphenated compound load-bearing applied to something that carries no load: an argument, an assumption, a component, a sentence. Say what breaks when it is removed.

Cues: `the load-bearing structure of his argument` · `the load-bearing assumption`

Before: That clause is the load-bearing part of the argument.

After: Remove that clause and the argument does not stand.

Do not flag: The hyphen is required: unhyphenated 'load bearing' is ordinary English ('the load bearing down on the bridge'). Attributive use before a literal structural noun, optionally with one material or position adjective in between ('load-bearing structural wall'), is building terminology and is exempt. Abstract-capable nouns (structure, element, frame, foundation) are deliberately outside the exemption, so 'the load-bearing structure of his argument' still flags. Known gap: predicative use ('the wall is load-bearing') still flags and must be dismissed by hand. Figurative load-bearing is settled usage in engineering and analytic-philosophy prose, where it says precisely that removing the thing collapses the structure; it is a finding only where the writer reaches for weight the sentence has not earned, and 'essential' or 'critical' is vaguer than the word it would replace.

### Moral adjective on a non-agentic noun (an honest shape) `moral-adjective-category-error`

Severity: **context** · Scope: english

A moral or character adjective (honest, genuine, faithful, truthful) attached to something that cannot hold a moral quality (a shape, a number, a representation, an accuracy, a curve, an output), or the adverb form hidden in a passive ('described honestly', 'flagged honestly'), where the passive conceals that there is no subject capable of honesty. State the concrete property instead, and cut moral adverbs from passives.

Cues: `honest shape` · `honest number` · `faithful representation` · `truthful output` · `genuine accuracy` · `honest curve` · `described honestly` · `flagged honestly`

Before: An honest shape for the data.

After: A more realistic curve.

Do not flag: A faithful representation is settled technical vocabulary in graphics, serialization and translation, and 'a faithful reproduction' is idiomatic; flag only where the moral reading is the intended one. 'An honest mistake' and 'honest work' are idioms about people. Tolerance is relaxed in technical writing and documentation and skipped in casual registers. Let the evidence carry the honesty claim rather than the adjective.

### Assumption "stops being true" `ontological-slop-assumptions`

Severity: **context** · Scope: english

Prefer 'no longer holds' or 'breaks down' for a model, premise or assumption that has stopped fitting the world. 'Stops being true' is grammatical and sometimes exact; it is the flatter phrasing, and the flatness is what reads as machine prose.

Cues: `The assumption stops being true`

Before: At scale, the assumption stops being true.

After: At scale, the assumption no longer holds.

Do not flag: This is a register preference rather than a logical correction. An assumption is a proposition held true, so it can stop being true and a writer who says so has made no mistake; flag only where the flat phrasing stands in for the idiom a specialist reader expects ('the assumption no longer holds', 'the model breaks down'). One hit proves nothing about authorship.

### Real / actual adjective inflation `real-actual-adjective-inflation`

Severity: **context** · Scope: english

real, actual, genuine or true used as an empty intensifier on an abstract noun (real tokenomics, actual reward sustainability, genuine utility, true product-market fit), implying the rest of the field is fake without ever naming what makes this one the real version. Drop the adjective and add the specific claim.

Cues: `Real on-chain tokenomics` · `actual reward sustainability` · `genuine utility` · `true product-market fit` · `genuine insight` · `a real improvement`

Before: Real reward sustainability, at last.

After: Rewards are funded from about $40k a month in fees rather than from emissions.

Do not flag: Named-contrast carve-out: if the sentence explicitly names the fake or superficial version it is honest contrastive writing and stays ('real on-chain settlement, not bridged IOUs', 'actual revenue from paying customers, not grants'). The tell is the unsaid contrast. Literal senses are exempt: real numbers, real time, actual size, true north, a genuine antique, 'lessons of real value'. Common in crypto, AI and web3 copy; tolerance is strictest in investor communication and relaxed in documentation and casual writing. This entry owns the empty real, actual, genuine or true bolted to an abstract noun; hollow-intensifier keeps only the sincerity adverbs (genuinely, truly, quite frankly, to be honest, let's be clear). Score the phrase once, here.

### Stale social-ad vocabulary (unlock, elevate, link in bio) `social-ad-boilerplate`

Severity: **context** · Scope: english

Worn social-media advertising diction imported into ordinary writing: unlock the potential, elevate your X, link in bio. Say what the reader gets and where.

Cues: `unlock` · `elevate` · `link in bio`

Before: Unlock the potential of your data. Link in bio.

After: The export lives at /reports/csv.

Do not flag: 'Link in bio' is the correct and only instruction on platforms that strip links from post bodies, so it is not a defect there. 'Unlock' is literal for doors, phones and feature flags. Judge by whether the surrounding piece is advertising.

### Uncontracted forms in speech-register copy `uncontracted-forms`

Severity: **context** · Scope: english

Writing it is, do not, will not, cannot where speech would contract, producing an over-formal register in marketing, social and newsletter copy. Use the contraction.

Cues: `do not` · `will not` · `cannot`

Before: It is not ready, and we will not ship it.

After: It isn't ready, and we won't ship it.

Do not flag: Formal, academic, legal and specification registers legitimately avoid contractions, and an uncontracted form can carry deliberate emphasis ('we will not ship it'). The uncontracted words are ordinary English at very high frequency in human prose (over 35 hits per ten thousand words in the controls), so no regex is offered; judge the register by hand. Contractions have no equivalent in many languages, so the mechanism (drop the over-formal register marker) transfers but the cues do not.

### Undefined jargon `undefined-jargon`

Severity: **context** · Scope: universal

A term of art used without definition where the reader cannot be assumed to know it, or corporate vocabulary that makes the text harder to read without adding precision. Give the term one clause of definition, or replace it. Strip only what obstructs reading: jargon, long sentences, abstract nouns and tangled structure, never the substance, nuance or precision.

Before: We moved the reconciliation loop behind the CRD.

After: We moved the reconciliation loop (the controller that keeps live state matching the config) behind a custom Kubernetes resource.

Do not flag: Writing for a specialist audience that shares the vocabulary needs no definitions, and defining a term the reader already knows is condescending. This is a general editing defect rather than an AI tell, so never count it toward an authorship judgment. Open the text up without dumbing it down: keep the substance, the nuance and the precision.

### Vague endorsement (worth reading, worth a look) `vague-endorsement-worth-verbing`

Severity: **context** · Scope: english

A generic thumbs-up built on 'worth' that substitutes for a specific reason: worth reading, worth paying attention to, worth a look, worth exploring, worth checking out, worth your time. Cut it, or say what the thing gives the reader. The tell is the bare form with no reason attached in the same sentence; 'worth reading for the appendix on retry budgets' is a recommendation and stays.

Cues: `worth reading` · `worth paying attention to` · `worth a look` · `worth exploring` · `worth checking out` · `worth your time`

Before: Their changelog is worth a look.

After: Their changelog lists the exact flags that changed defaults in v3.

Do not flag: Legitimate where the reason is given in the same breath ('worth reading for the appendix on retry budgets'), and in a link roundup whose whole purpose is a short recommendation. 'Not worth reading' as a judgment with a stated reason is fine, and Strunk's own 'his books are not worth reading' is ordinary English.

## Paragraph and document structure

### Despite-its-challenges outlook formula `despite-challenges-outlook`

Severity: **always** · Scope: english

A stock closing block, often under a heading like 'Challenges and Future Directions' or 'Future Outlook', shaped as two beats: 'Despite its [positive words], [subject] faces challenges...' followed by 'Despite these challenges, [it] continues to thrive' or speculation about initiatives that could benefit the subject. It acknowledges problems only to dismiss them and adds no fact. Keep the concrete facts and cut the pitch; add dates or actions only when the source or the user supplies them.

Cues: `Despite its... faces several challenges...` · `Despite these challenges` · `faces several challenges, including` · `faces new challenges and opportunities` · `presents numerous challenges, including` · `must be addressed for broader adoption` · `continues to thrive` · `continue to provide a vital service` · `continues to evolve in response to these challenges` · `strategic location and ongoing initiatives` · `positions them as critical components` · `adapt to these emerging trends` · `Future investments in technology ... could enhance` · `Challenges and Legacy` · `Challenges and Future Directions` · `Future Outlook` · `Future Prospects` · `Despite its industrial and residential prosperity, Korattur faces challenges` (+1)

Before: Despite its industrial prosperity, Korattur faces challenges typical of urban areas, including traffic congestion and water scarcity. Despite these challenges, with its strategic location and ongoing initiatives, Korattur continues to thrive as an integral part of Chennai's growth.

After: Korattur has recurring traffic congestion and water shortages.

Do not flag: The formula, not the word: this is about the rigid two-beat shape, not any mention of challenges or challenging. A sentence naming a specific problem with a number, date or named actor is content. A 'Challenges' heading over a section of concrete, sourced problems is fine. Quoted text and reported speech are exempt.

### Heading restated in the first line `heading-restated-below`

Severity: **always** · Scope: universal

A heading is followed by a one-line paragraph that only restates it ('## Performance' then 'Speed matters.') before the real content begins. The warm-up line does the heading's job a second time; the loudest sub-form repeats the heading's own word as the line's first word ('## Performance' then 'Performance is important...'). Delete the line and start with the first sentence that says something.

Cues: `heading word repeated as the first word of the line below it` · `one-line paragraph under a heading that adds no fact`

Before: ## Performance

Speed matters.

When users hit a slow page, they leave.

After: ## Performance

When users hit a slow page, they leave.

Do not flag: A one-line paragraph under a heading that states the section's claim or bottom line ('Cache hits fell 40% after the migration.') is a lede, not a restatement. Glossary, reference and API documents where a heading is the term and the line under it is its definition; the regex cannot tell those apart, so treat a hit as a candidate.

### Preamble before the point (sweeping opener) `preamble-before-the-point`

Severity: **always** · Scope: universal

The piece opens with broad context before it says anything specific: a sweeping scene-setting sentence ('In today's fast-paced world...', 'In the rapidly evolving world of...'), background paragraphs that add nothing, or support placed ahead of the point it supports. Delete the sweeping sentence and start with the second; lead with the news or the insight and let context come second. Keep an opening aside, story or admission only when it creates context, tension or character.

Cues: `generic throat-clearing` · `setup adds nothing`

Before: In today's fast-paced digital world, teams need faster builds. We cut ours from forty minutes to six.

After: We cut our build from forty minutes to six.

Do not flag: Narrative and argumentative forms that earn a delayed point (a story whose setup pays off, a mystery structure). Do not force every section into the same point-detail-background shape; the instruction is to cut setup that adds nothing, not all setup. The stock phrases are always cut; the structural form is a judgment. The stock opening phrases themselves belong to vocabulary/generic-scene-setting-opener, which carries the same regexes; this entry owns the structural form, support placed ahead of the point it supports.

### Signposted conclusion (summary-recap ending) `signposted-conclusion`

Severity: **always** · Scope: universal

A closing paragraph announced by a stock summarising marker ('In conclusion', 'In summary', 'To sum up', 'In short', 'Kortom', 'Overall', 'Ultimately', 'At the end of the day') or a section literally titled 'Conclusion' that restates what the body already said, sometimes with an inspirational wrap-up bolted on. The reader was just there. Delete the recap and end on the last substantive point, takeaway or next action. Korean uses 결론적으로 / 요약하면 / 종합하면 / 정리하자면 / 이를 통해, and the exhortation forms ('Remember, when doing X…', 'As we navigate X…', 'The journey doesn't end here') close the same way.

Cues: `To summarize` · `To sum up` · `In short…` · `Kortom` · `At the end of the day…` · `Conclusion:` · `In conclusion…` · `In summary…` · `Overall…` · `Ultimately…` · `Remember, when doing X it's important to consider…` · `As we navigate [X], it's essential that we…` · `The journey doesn't end here…`

Before: In summary, the educational and training trajectory for nurse scientists typically involves a progression from a master's degree in nursing to a Doctor of Philosophy in Nursing, followed by postdoctoral training in nursing research. This structured pathway ensures that nurse scientists acquire the necessary knowledge and skills to engage in rigorous research.

After: (Deleted. The section already walked the reader from the master's to the postdoc; it ends there.)

Do not flag: Academic papers, theses and formal reports where a marked Conclusion section is required by the genre; keep the section but make it add implications, limits or next steps rather than restate. 'In short' or 'kortom' once, introducing a compressed restatement mid-argument, is ordinary prose; the tell is the ending. 'Overall' and 'ultimately' inside a sentence ('the overall cost') are not the marker. A 'Conclusion' section heading itself is carried by formulaic-section-headers; this entry owns the inline 'Conclusion:' lead and the summarising markers. The Korean trigger is three or more of the summation lexicon combined, not the first one. 따라서 and 그러므로 are ordinary mid-argument connectives and are never the trigger on their own.

### Bullet lists of bare noun phrases `bare-noun-phrase-bullets`

Severity: **cluster** · Scope: universal

Five or more consecutive bullet items that are each a short (six words or fewer) adjective-plus-noun phrase with no finite verb, all the same grammatical shape and length, none asserting anything checkable ('Stable mining efficiency', 'Reliable pool connectivity'). The symmetry is the tell: a genuine list of observations varies in length, has occasional verbs, and has at least one item that breaks the pattern. Detector gate: run of 5+, item word count at most 6, no auxiliary or modal token, 75% or more of the run bare. Convert to prose or rewrite each item as a full claim with a number. Take the numbers from the source; if the source has none, cut the list rather than invent them.

Cues: `Stable mining efficiency` · `Reliable pool connectivity` · `Optimized RandomX performance` · `Low failed share rates` · `Effective hardware utilization` · `Consistent thermal stability` · `bullet line: ^\s*(?:\*|-|•|\+)\s+(.+)$` · `run >= 5, item wc <= 6, bareNP/run >= 0.75`

Before: - Stable mining efficiency
- Reliable pool connectivity
- Optimized RandomX performance
- Low failed share rates
- Effective hardware utilization
- Consistent thermal stability

After: (Cut. Not one item carries a measurement. Get the hashrate variance and the failed-share rate off the run log, then write the two sentences they support.)

Do not flag: List content that is a list: changelog entries, todo lists, parameter and option docs, ingredient lists, tag lists, tables of contents. Numbered lists are excluded (they belong to numbered-list inflation). Short two-word action items ('fixed bug') pass the gate, an accepted trade-off. Bullets inside code fences are skipped; two blank lines break a run. Technical blogs and docs relax this rule for option and parameter lists. The three sources split one apiece on severity (detector always, skill-b cluster, skill-a context) with no majority; cluster is the median and matches the detector's own run-of-five gate, which is already a cluster test.

### Bullets where prose belongs `bullets-instead-of-prose`

Severity: **cluster** · Scope: universal

Bulleted, especially nested, lists imposed on ideas that are connected or need context and would read better as a paragraph: eight or more bullets in under 200 words, three or more bullet blocks in a row in an essay, column or report, or any bullet list where two sentences of prose would do. Lists help when items are parallel and independent; convert the rest to prose and keep a list only where enumeration carries meaning. The same judgment covers formatting as a whole: default to prose and add structure only where it makes the text clearer.

Cues: `bullet lists where two sentences of prose would read better` · `bullet blocks` · `3+ consecutive`

Before: - Latency dropped
  - Because we cached the token
    - Which also fixed the 401s

After: Latency dropped once we cached the token, which also fixed the 401s.

Do not flag: List-like content: feature comparisons, step-by-step instructions, API parameters, checklists, changelogs. Docs and LinkedIn skip this rule; technical blogs tolerate technical lists. Genre guard from im-not-ai: essay, column and report only. Reference docs, runbooks, API docs and checklists where scannability is the point are exempt; the sibling headers-over-short-text carries the heading half of the judgment.

### Circular return ending `circular-return-ending`

Severity: **cluster** · Scope: universal

A closing sentence that loops back to the opening image or question ('And so we return to where we began') as a substitute for an ending that lands on something new. It is the bookend cousin of the signposted conclusion: symmetry standing in for a point. The detector is the echo of the opening sentence's key noun in the final sentence, not any single phrase; the listed phrases are only the loudest surface forms.

Cues: `And so we return to where we began` · `Which brings us back to` · `So we come full circle` · `Back to the question we started with` · `And that is where we began`

Before: And so we return to where we began: is the tool worth it?

After: The tool pays off for teams over ten people; below that, the setup cost eats the gain.

Do not flag: A deliberate frame in a personal essay or story where the return pays off the setup with new meaning. A single instance in a long piece whose final paragraph is substantive.

### Colon-subtitle headings (X: Y) `colon-subtitle-headings`

Severity: **cluster** · Scope: universal

Every heading takes the 'Noun: subtitle' shape, or its transformation variant 'X: from A to B' ('X: A에서 B로'). The colon subtitle is the model's default heading generator. Compress each to a single noun phrase that names the content; preserve genuine academic and report section titles.

Cues: `X: Y` · `colon-subtitle heading`

Before: ## Observability: From Logs to Traces

After: ## Traces replace logs

Do not flag: One colon heading in a document is ordinary; the tell is the shape on every heading. Academic titles, 'Step 1: ...' procedure headings, and headings whose colon introduces a proper name or a code identifier. Severity tie between the two Korean sources was broken toward cluster because the taxonomy runs it as a quick, density-based check.

### Concede-salvage-rebut reply template `concede-salvage-rebut-template`

Severity: **cluster** · Scope: english

When a user points to an error and the model agrees, the first paragraph of the reply follows a fixed three-beat shape: admit the user is right, point out what is still valid, then close with a variant of 'But that's not all it's doing, and the surplus is what you're pointing at'. Detect the concede / salvage / rebut-and-binary sequence; answer the correction directly instead.

Before: You're right that the cache helps. It still cuts p95 in half. But that's not all it's doing, and the surplus is what you're pointing at.

After: You're right, the cache also masks the retry bug. I'll fix the retry first.

Do not flag: A genuine concession followed by a substantive correction is not the template; the tell is the fixed beat order and the binary close. The compliment sandwich in the rhetoric category is the neighbouring shape.

### Headings that only contain other headings `empty-parent-headings`

Severity: **cluster** · Scope: universal

A heading whose entire content is lower-level headings, with no prose of its own: an outline node rendered as a section ('= Main Characters =' followed directly by '== Pixy =='). Either give the parent a sentence that earns it or promote the children.

Cues: `heading directly followed by a sub-heading` · `= Section =
== Subsection ==`

Before: = Programming =
== Pixy's Adventure Club ==
[...]
= Main Characters =
== Pixy ==
[...]

After: == Pixy's Adventure Club ==
[...]
== Pixy ==
[...]

Do not flag: Long reference documents with a deliberate table-of-contents hierarchy; a document title (H1) directly followed by its first section (H2).

### Five-paragraph essay and rule-of-three scaffolding `five-paragraph-essay`

Severity: **cluster** · Scope: universal

Intro plus three body sections plus closing recap, imposed at any length, even on a 100-word answer. Sub-forms: a three-item list in every section whatever the real count; three consecutive paragraphs opened with the fixed thesis-antithesis-synthesis connectives 먼저 / 반면 / 결국 (first / on the other hand / in the end). Let the count of things to say decide the count of sections, and cut the connectives to one or none.

Cues: `There are three reasons` · `There are three key` · `Taken together, these` · `three main takeaways` · `intro plus three body sections plus recap`

Before: Static hosting was the right call for this site.

It costs nothing at our traffic, because a static bundle is served from the CDN cache.

It is fast, because every page is already built when the request arrives.

It is low-maintenance, because there is no runtime to patch.

For all these reasons, static hosting was the right call.

After: Static hosting costs nothing at our traffic, and every page is already built by the time a request arrives.

There is also no runtime to patch.

Do not flag: A single rule-of-three is fine; the tell is the triplet in every section or the same shape on every answer. School essays and exam answers where the form is the assignment. The ordinal run inside one paragraph is listicle-in-prose and the triad inside one sentence is syntax/rule-of-three; this entry is the document skeleton.

### Formulaic section headers (slot names and study-guide titles) `formulaic-section-headers`

Severity: **cluster** · Scope: universal

Headings that name a template slot rather than the content: 'Introduction', 'Overview', 'Body', 'Summary', 'Conclusion' (Korean 도입 / 본론 / 결론), slide-deck and study-guide titles ('Key Takeaways', 'Key Points', 'Key highlights', 'Key Statistics', 'Key Figures', 'Questions to Consider'), and the default 'X and Y' encyclopaedic headers, of which 'Awards and recognition' is nearly ubiquitous in generated articles. In prose genres remove the heading; in reports make it say something specific about what follows.

Cues: `Overview` · `Key Points` · `Summary` · `Conclusion` · `Introduction` · `Key Takeaways` · `Questions to Consider` · `Key highlights:` · `Key Statistics` · `Key Figures` · `three key layers` · `Awards and recognition` · `Challenges and Legacy` · `Challenges and Future Directions` · `Legacy & Interpretation` · `Sociology, sustainability, and future challenges`

Before: ## Key Points

After: ## What the migration cost

Do not flag: Genuine numbered section titles in academic and report writing (II., (3), chapter titles) are structure and must never be removed or absorbed. README conventions ('Overview', 'Installation') and journal-mandated 'Introduction' / 'Conclusion' headings. Human editors also write legacy and impact sections; the 'X and Y' shape alone is weak, the exact wording 'Awards and recognition' and the study-guide titles are the tell. 'Conclusion' as a heading is flagged here; the inline 'Conclusion:' lead and 'In conclusion' belong to signposted-conclusion. 'Key management personnel' is a mandated IAS 24 related-party disclosure heading and 'Recognition' is ordinary technical English (revenue recognition, pattern recognition); neither is a cue here.

### Fractal summaries (section preview and recap) `fractal-summaries`

Severity: **cluster** · Scope: universal

'Tell them what you will tell them, tell them, tell them what you told them' applied at every level: a preview sentence under each heading ('In this section, we'll explore...', '이 섹션에서는 ~를 다룬다'), a mini-summary closing every section ('In summary', 'as we've seen in this section'), and sections that open by recapping the previous one. Delete the previews and recaps; start each section with its substance and let the heading do the announcing.

Cues: `In this section, we'll explore` · `as we've seen in this section`

Before: In this section, we'll explore how caching works. [...] As we've seen in this section, caching cuts latency.

After: Caching cuts p95 latency because the token is fetched once per hour instead of once per request. [...]

Do not flag: Long reference manuals, textbooks and formal reports whose genre requires section abstracts; there the tell is the recursion at every level, not one abstract. A one-sentence orientation at the top of a long section that tells the reader what to skip is navigation, not a preview. The opening announcement on its own is rhetoric/meta-signposting and the document's closing recap is signposted-conclusion; this entry fires only on the recursion, a preview and a recap at more than one level.

### Headers over short text `headers-over-short-text`

Severity: **cluster** · Scope: universal

Section headings imposed on text too short to need navigation: a heading over a section of two sentences or fewer, more than three headings in under 300 words, H2/H3s in a short piece, or a discussion reply or comment split into titled sections (Markdown, plain-text titles or wiki subheadings, sometimes emoji-decorated). Remove the headings, merge the text and use prose transitions.

Cues: `heading over a section of two sentences or fewer` · `more than three headings in under 300 words` · `headers over tiny sections` · `#### 📌 Key facts needing addition or correction:`

Before: ## Context

We saw a spike.

## Analysis

It came from the cron job.

## Conclusion

We'll move it.

After: We saw a spike; it came from the cron job, so we're moving it to 03:00.

Do not flag: Reference docs, API references and runbooks where every subsection is meant to be linkable; READMEs with conventional short sections ('License'). Flag on the ratio of headings to body, not on any single short section.

### Inline-header lists (bold-first bullets) `inline-header-lists`

Severity: **cluster** · Scope: universal

A vertical list where every item opens with a short bold (or wiki-bold) label, a colon, then a sentence that often restates the label ('**Performance:** Performance improved by...'). Sub-forms: the same shape without separating punctuation (a bold run followed directly by a capitalised sentence), numbered variants ('1. Header: text'), and a colon lead-in line before the list ('Key highlights:', 'consists of three key layers:'). The detector treats this, headers on every topic and padded numbered lists as one skill-only over-scaffolding judgment. Fold into prose, or keep a plain list of full sentences when the items are parallel and short.

Cues: `- **User Experience:**` · `- **Performance:**` · `- **Security:**` · `**Performance:** Performance improved by...` · `**Word**:` · `**Security**:` · `**Performance**:` · `**Stem:** elaboration` · `**Term:** explanation` · `**Term:** fragment` · `Bold term: explanation sentence` · `* '''Header:''' text` · `1. Header: text` · `'''SEO (Search Engine Optimization):'''` · `'''Route Details''':` · `'''Bypasses and Improvements''':` · `'''Timeline and Impact''':` · `Key highlights:` (+10)

Before: - **User Experience:** The user experience has been significantly improved with a new interface.
- **Performance:** Performance has been enhanced through optimized algorithms.
- **Security:** Security has been strengthened with end-to-end encryption.

After: The update ships a new interface and end-to-end encryption, and pages load faster because the sort was rewritten.

Do not flag: XfD-style votes where a single bolded 'Keep' or 'Delete' sets the verdict apart from the argument. Glossaries, definition lists, API parameter and CLI flag references, changelogs keyed by component, and any list whose bold term is the item's actual name (a product, a person, a field). One or two bold-labelled items in an otherwise prose document; the tell is three or more in a row and the restatement of the label in the item text.

### Listicle in prose (ordinal scaffolding) `listicle-in-prose`

Severity: **cluster** · Scope: universal

Numbered points disguised as running prose: consecutive paragraphs or sentences each opened with an ordinal ('The first wall is... The second wall is...', 'First, ... Second, ... Third, ... Fourth, ...', Korean 첫째, 둘째, 셋째), or inline 1) 2) 3) markers inside a paragraph. Often the result of telling the model to stop generating lists. Default is to preserve up to three items; at four or more, prose-ify one or two items or vary the signposts (우선 / 다음으로 / 마지막으로), and vary item length and structure when the list stays. The parenthesised '(1) … (2) … (3)' form is the weaker variant of the same inline indexing.

Cues: `The first ... The second ... The third ...` · `The first wall is` · `The second takeaway is that` · `The third takeaway is that` · `The fourth takeaway is that`

Before: The first wall is the absence of a free, scoped API. The second wall is the lack of delegated access. The third wall is the absence of scoped permissions.

After: The missing scoped permissions are the real wall; a free API and delegated access would be useless without them.

Do not flag: Three-item enumerations are ordinary human prose and must be kept: removing them unconditionally drew real user complaints and the rule was demoted for it. Act at four or more. Academic, manual and expository genres enumerate constantly. Legal clauses and procedure steps that use 1) 2) 3) by convention. The inline 1) 2) 3) form is flagged from three items because its source rule carries no threshold; the ordinal-sentence form waits for four. Legal, mathematical and academic text enumerates conditions inline by convention, and a real list rendered as list items (one item per line) does not match.

### Repeated sentence and paragraph shapes (robotic symmetry) `repeated-sentence-shapes`

Severity: **cluster** · Scope: universal

Mechanical symmetry beyond length: the same sentence construction recurring, identical paragraph templates (same order of moves, same closing sentence) within a piece or across unrelated pieces, every paragraph carrying the same internal cadence, punctuation density flat from paragraph to paragraph, and every sentence complete, balanced and tidy with no roughness or aside. Detector gates: function-word trigram entropy below 0.82 on 150+ words, per-paragraph sentence-length CV with standard deviation below 0.08 and mean below 0.45, punctuation-density CV below 0.25. Vary the shape only where it helps the point; forced variation is the same failure from the other side.

Cues: `repeated sentence shapes` · `identical paragraph structures` · `stacked punchy fragments` · `robotic symmetry` · `perfectly structured sentences` · `cvStd < 0.08 && cvMean < 0.45` · `[,;:—()] per \S+` · `cv < 0.25 && mean >= 0.04` · `normalized < 0.82 && total >= 50; degenerate distinctCount === 1 flagged high`

Before: We tried Redis. It was fast, but it cost more, so we kept it. We tried Memcached. It was fast, but it lost data, so we dropped it. We tried Postgres. It was slow, but it was already there, so we stayed.

After: Redis was fast enough to keep, even at the price. Memcached matched it and then lost data. We stayed on Postgres, which was already running and slow in a way we could live with.

Do not flag: Stylometric corroborators only; none is proof alone and human prose swings 0.15-0.40 in per-paragraph CV. Controlled-language docs, legal text, liturgical or deliberately incantatory prose. Do not over-tidy in the other direction: making every paragraph equally rough is the same symmetry. Overlapping neighbours: plain sentence-length variance is sentence-rhythm-uniformity and paragraph length is uniform-paragraph-length. This entry owns the grammar-repetition, punctuation-flatness and paragraph-template signals, and its per-paragraph CV gate measures the spread of that variance across paragraphs, which neither neighbour looks at.

### Sentence rhythm uniformity (low burstiness, all-simple or all-tangled) `sentence-rhythm-uniformity`

Severity: **cluster** · Scope: universal

Sentence length and shape cluster around one setting with no variation: either a metronomic median of 14 to 22 words with no short declaratives, or nothing but single-clause simple sentences (common after 'be concise'), or long stacked-subordination sentences with dashes mid-sentence and verbose, flat rhythm. Korean metrics: mean eojeol per comma-delimited clause above 7 (human 4.35 vs AI 8.56) and inflated part-of-speech diversity around commas. Vary the rhythm: bind adjacent simple sentences with connectives, split genuinely tangled ones, and keep short sentences for emphasis and turns. Detector gate: coefficient of variation below 0.25 with an average above 10 words over at least five sentences; the Korean evidence puts the real signal in the absence of long sentences (100+ characters: AI 8 vs human 91 per thousand).

Cues: `long sentences` · `tangled structure` · `clause length between commas > 7 eojeol` · `no sentence over 100 characters` · `uniform sentence length` · `cv < 0.25 && avg > 10 && sentences >= 5`

Before: The service starts. It loads the config. It opens a socket. It waits for requests.

After: After loading its config, the service opens a socket and waits for requests.

Do not flag: Do not split long spoken sentences that are clear and characteristic of the writer, and do not flatten cadence while untangling. Non-native writers naturally produce lower-burstiness text, so the metric alone is not evidence of a model. The eojeol thresholds are Korean and need recalibration per language. Texts under five sentences are out of scope, and genres that mandate uniform sentences (legal boilerplate, safety instructions, controlled language) are exempt. Personal blogs narrow the gap, so treat it as a corroborator, not proof. The spread of sentence-length variance across paragraphs, and the repeated paragraph template, are repeated-sentence-shapes; this entry is the variance within the text.

### Topic sentence opening every paragraph `topic-sentence-every-paragraph`

Severity: **cluster** · Scope: universal

Every paragraph opens with a thesis-style topic sentence that summarises the paragraph, the English composition-textbook shape imported wholesale. Let some paragraphs open with a case, a scene, a number or a quotation and let the point arrive second.

Cues: `topic sentence` · `paragraph opening`

Before: Caching reduces latency. When we added the token cache, p95 fell from 800 ms to 120 ms.

Monitoring caught the regression quickly. The on-call engineer said the dashboard went red before the first support ticket arrived.

Cache invalidation remains the hard part. We still flush the whole namespace on every deploy because nobody has scoped the keys.

After: When we added the token cache, p95 fell from 800 ms to 120 ms.

'The dashboard went red before the first support ticket,' the on-call engineer said.

Cache invalidation remains the hard part. We still flush the whole namespace on every deploy because nobody has scoped the keys.

Do not flag: Technical documentation, abstracts and executive summaries where a leading summary sentence per paragraph is the convention; single paragraphs.

### Uniform paragraph length `uniform-paragraph-length`

Severity: **cluster** · Scope: universal

Every paragraph is roughly the same size, typically three to five sentences or 30-50 words, so the document has no rhythm at paragraph level. Detector gate: every paragraph within one sentence of the average, average at least 3 sentences, over at least 4 paragraphs. Vary deliberately: some one-sentence paragraphs, some six-sentence ones.

Cues: `3–4 sentences per paragraph`

Before: The deploy went out at nine on Tuesday. Error rates were flat for the first twenty minutes. Then the checkout endpoint started returning 500s. Support saw the first ticket at 09:31.

We rolled back four minutes after the page. The 500s stopped as soon as the old image was serving. No paid order was lost. The queue drained by ten.

The cause was a migration that dropped a column the old code still read. It passed review because the column looked unused. Nothing in staging exercised that path. The test suite had no case for it.

The build now fails when a migration drops a column that is still referenced in the codebase. It runs in the same job as the type check. It caught one more case the following week. That case was a renamed column.

After: The deploy went out at nine on Tuesday. Error rates were flat for the first twenty minutes. Then the checkout endpoint started returning 500s. Support saw the first ticket at 09:31.

We rolled back four minutes after the page, and the 500s stopped as soon as the old image was serving again. No paid order was lost and the queue drained by ten. The cause was a migration that dropped a column the old code still read; it passed review because the column looked unused, and neither staging nor the test suite exercised that path.

That was the whole bug.

The build now fails when a migration drops a column that is still referenced in the codebase, in the same job as the type check. It caught one more case the following week, a renamed column.

Do not flag: Texts under four paragraphs. Short-form registers (LinkedIn, chat, casual) skip; docs relaxed. Distinct from the wall-of-text reply, which is zero breaks in a short text. Paragraph templates and grammar repetition are repeated-sentence-shapes; sentence length is sentence-rhythm-uniformity. This entry measures paragraph length only.

### Numbered list inflation `numbered-list-inflation`

Severity: **context** · Scope: universal

A count-headlined list ('Three key takeaways', 'Five things to know', 'Here are the top seven') chosen because numbered lists are structurally safe, then padded to reach the number rather than reflecting that many discrete parallel items. Use a numbered list only when the content has that many independent, parallel items; otherwise cut to the real items or write prose.

Cues: `Three key takeaways` · `Five things to know` · `Here are the top seven`

Before: Here are the top seven reasons to switch: 1. Faster builds. 2. Per-seat licence. 3. Faster builds on CI. 4. Cheaper. 5. Better docs. 6. Faster incremental builds. 7. Lower cost per seat.

After: We switched because the build is 40% faster and the licence is per seat instead of per core.

Do not flag: Step-by-step instructions, ranked results, and lists whose count is a fact ('the three EU directives that apply'). Tolerance by register: docs and casual skip, LinkedIn and technical blogs relaxed, blog and investor email strict.

### Paragraph-reshuffle immunity (missing bridges) `paragraph-reshuffle-immunity`

Severity: **context** · Scope: universal

Body paragraphs that can be swapped without the reader noticing: each is a self-contained module with no load-bearing link to its neighbours, so the piece is a list of points rather than an argument that builds. Fix structurally: establish a through-line where each paragraph depends on the one before, add connective tissue, or, if the paragraphs are independent, make the piece an explicit list or find its missing thesis.

Before: Paragraph on cost. Paragraph on speed. Paragraph on trust. (any order reads the same)

After: Paragraph on cost ends on the number that sent us looking. Paragraph on speed opens on what we found instead. Paragraph on trust opens on the cache the speed depends on. (reorder them and the second paragraph loses its opening)

Do not flag: Reference material, FAQs, glossaries and any form meant to be dipped into rather than read through.

### Title heading repeated above the content `title-heading-duplicate`

Severity: **context** · Scope: universal

The output opens with a level-1 heading (often bold or linked) that repeats the document or article title before any body text, because the model does not assume the surface already renders the title. On a wiki page, a CMS, a blog with a title field, an issue or a PR description this is a duplicate H1; delete it.

Cues: `a top-level heading equal to the article name before any content` · `= '''Title''' =` · `# <article name> as the first line` · `level-1 heading equal to the page name`

Before: = '''[https://www.youtube.com/@Pixaroo-kid Pixaroo]''' =
Pixaroo is an animated series [...]

After: Pixaroo is an animated series [...]

Do not flag: A standalone Markdown file whose only title is that heading (a README, a note, a doc page rendered from the file) is correct. Flag only where the surface renders the title itself. The regex covers just the wikitext bold-title form at the top of a document; a plain '# Title' first line is left alone because it is right in most Markdown files. Severity tie (wikipedia-a always, wikipedia-b context) broken toward context because the later treatment adds the surface dependence.

### Wall-of-text replies `wall-of-text-replies`

Severity: **context** · Scope: universal

In conversational registers (issue and PR comments, chat, DMs, casual email), a reply-length text of roughly under 150 words with four or more sentences delivered as one unbroken paragraph. Humans break replies at thought boundaries; the model defaults to a single dense block. Break at the thought boundaries.

Before: Thanks for the patch. The backoff looks right, but the jitter is applied after the cap, so every capped delay comes out at exactly 30s and all the clients wake up together. Moving the jitter inside the cap fixes it. I would also rather not add a fourth timeout knob. We have connect, read and total already, and nobody sets them independently in practice, so can this one be derived from total? The new test passes locally for me and fails on CI, and I think that is because the fake clock starts at zero while the code compares against Date.now, so pinning the clock in the fixture should sort it. None of this is blocking except the jitter. Happy to pair on the timeout question tomorrow if that beats another round of comments.

After: Thanks for the patch. The backoff looks right, but the jitter is applied after the cap, so every capped delay comes out at exactly 30s and all the clients wake up together. Moving the jitter inside the cap fixes it.

I would also rather not add a fourth timeout knob. We have connect, read and total already, and nobody sets them independently in practice, so can this one be derived from total?

The new test passes locally for me and fails on CI, and I think that is because the fake clock starts at zero while the code compares against Date.now, so pinning the clock in the fixture should sort it. None of this is blocking except the jitter. Happy to pair on the timeout question tomorrow if that beats another round of comments.

Do not flag: Formal long-form registers (a blog intro, a docs paragraph, a tight one-paragraph email) where a single dense paragraph is the correct shape; never flag continuous long-form prose for lacking internal breaks. Requires knowing the register: the structural detector for this was reverted because it fired on any ordinary short paragraph, and a plain issue comment auto-detects to the blog profile.

## Punctuation and formatting

### Em and en dashes as clause splice `em-dash-density`

Severity: **always** · Scope: universal

The em dash, a spaced en dash or a spaced double hyphen used as the default clause splice: a pair bracketing an aside, a single dash tacking on a punchy final clause or afterthought, additive dashes attaching qualifiers sentence after sentence, or a dash staging the second half of a 'not X, but Y' turn. Sub-forms: the spaced em dash (' — '), an en dash doing em-dash work, the ' -- ' substitute, a line-initial '**Bold lead** — sentence' outside a list, and a dash-aside in every sentence. Most sources measure density (human prose runs about one per 500 words, generated drafts one per 50 to 80, detectors cap at one per 1,000 and count headings too), but the the consuming repo house rule bans the mark outright in copy and in the agent's own replies. Rewrite with a full stop, comma, colon or parentheses, spell out the connective the dash was hiding, and use the house separators '//' or '·' in fact lines.

Cues: `— not because` · `— but because` · `— and` · `— like` · `— which` · `— something that` · `This isn't X — it's Y` · `doesn't grow from silence — it grows from` · `**Bold lead** — full sentence` · `— … —` · `is not the neutral midpoint – it is one option among three`

Before: The term is primarily promoted by Dutch institutions—not by the people themselves. You don't say "Netherlands, Europe" as an address—yet this mislabeling continues—even in official documents.

After: The term is promoted mainly by Dutch institutions. The people themselves rarely use it. You don't say "Netherlands, Europe" as an address, yet this mislabeling continues in official documents.

Do not flag: A writer's sample that uses dashes keeps them at the sample's rate (humanizer: do not apply as a ban when the sample has them); a house style guide that keeps deliberate em dashes (CMOS, or AP with spaced dashes) is flagged only for stacking. An en dash in a numeric or date range (2019–2024, pp. 12–15) is a range, not a dash; the regex only counts a spaced en dash. An unspaced 'word--word' is typewriter and 19th-century print convention and is not counted; ' -- ' as a CLI flag, SQL comment or code token is code. The detector carves out the separator in a list item that opens with a bolded term or a link ('- **Term** — description') and changelog version headings ('## v1.2.0 — 2026-01-01') as typography, but the the consuming repo house rule still replaces those with '//' or '·'. The approved the consuming repo banners that carry an em dash in data form ('/001 — 7 OKT', 'the consuming repo/001 — reconnect', "KOM D'R IN — EVERYONE'S WELCOME") were visually ratified and change only when the owner asks. Quoted text and dashes already present in a human source are preserved during a rewrite: only dashes the model added are targets. On the density reading a single dash in a long draft is noise, though not under the house ban. Models since GPT-5.1 are tuned away from the mark, so its absence proves nothing. Never add a dash during a rewrite. A spaced en dash is the ordinary clause splice in British and Commonwealth house style (Oxford, Guardian, Cambridge), so there it is judged on density the way the em dash is and never read as machine residue on sight. The metavocabulary of dashes ('em dash', 'em-dash aside') was dropped from the cues because it fires on every text that discusses punctuation, this catalog included.

### Emoji as decoration `emoji-decoration`

Severity: **always** · Scope: universal

Emoji placed in front of headings, list items or bold labels as visual icons, one per heading or bullet and often thematically matched to the text ('🚀 **Launch Phase:**'), used as bullet markers or for emphasis, or a lone sparkle closing a paragraph. Residue of training on marketing blogs. Remove them from headings and body text; a social post may keep one or two at the end of a line.

Cues: `🚀 **Launch Phase:**` · `💡 **Key Insight:**` · `✅ **Next Steps:**` · `## 🚀 What This Means` · `emoji in headings` · `Emoji headings` · `emoji list heads` · `emoji emphasis` · `emoji before a heading` · `emoji before a bullet` · `emojis`

Before: 🚀 **Launch Phase:** The product launches in Q3
💡 **Key Insight:** Users prefer simplicity
✅ **Next Steps:** Schedule follow-up meeting

After: The product launches in Q3. Users prefer simplicity. We still need to schedule a follow-up meeting.

Do not flag: Social posts may carry one or two emoji at the end of a line, never mid-sentence (LinkedIn relaxed); chat and casual registers and the docs profile skip the check; im-not-ai guards it to column and report genres. A check mark or status glyph in a status table, emoji that is the content (an emoji-picker doc, a Unicode reference) and the plain ✓/✔ checklist ticks are outside the regex ranges on purpose. Never acceptable in encyclopedic or formal prose.

### Math-bold letters and bullet glyphs `unicode-math-bold-and-bullets`

Severity: **always** · Scope: universal

Bold faked with Unicode Mathematical Alphanumeric Symbols (𝗯𝗼𝗹𝗱) instead of markup, and list items marked with the Unicode bullet character (•) on a surface that has real list syntax. Wikipedia's cleanup project flags both as strong tells. Replace with the surface's own markup or plain sentences.

Cues: `𝗯𝗼𝗹𝗱`

Before: 𝗦𝗵𝗶𝗽 𝘄𝗲𝗲𝗸𝗹𝘆
• smaller batches
• fewer rollbacks

After: Ship weekly. Smaller batches mean fewer rollbacks.

Do not flag: Text pasted from Word or a PDF where the bullet glyph is the export's doing (a Gutenberg licence block carries them, which is why the regex needs two bullet lines in a row); LinkedIn posts, where math-bold is the only way to fake bold (still a provenance tell, but the surface explains it); mathematical notation that genuinely uses the block.

### Boldface density `bold-overuse`

Severity: **cluster** · Scope: universal

Boldface applied mechanically instead of marking one real emphasis point: every term or acronym in a sentence, a bolded key phrase in every sentence, every instance of a chosen word, 'key takeaways' bold on ordinary noun phrases, or decorative bold sprinkled mid-sentence. Sub-forms include bold spans that break mid-phrase and bold fused to an emoji or a dash-led label. Strip bold from most phrases; if a thing is important enough to bold, restructure the sentence to lead with it. Ceiling: about one bolded phrase per major section, or none; the detector flags more than three spans in a text.

Cues: `**OKRs (Objectives and Key Results)**` · `**KPIs (Key Performance Indicators)**` · `**Business Model Canvas (BMC)**` · `multiple '''bold''' spans in one sentence` · `bold on every instance of a chosen word or phrase` · `key-takeaways style bold` · `decorative bold` · `bold sprinkled mid-sentence for emphasis` · `**bold** in every sentence` · `count > 3` · `'''leveraged buyout (LBO)'''` · `'''debt financing'''` · `'''private equity firms'''` · `'''financial sponsors'''` · `'''assets and future cash flows'''` · `'''Productive Years'''` · `'''P(doom)'''`

Before: It blends **OKRs (Objectives and Key Results)**, **KPIs (Key Performance Indicators)**, and visual strategy tools such as the **Business Model Canvas (BMC)** and **Balanced Scorecard (BSC)**.

After: It blends OKRs and KPIs with visual strategy tools such as the Business Model Canvas and the Balanced Scorecard.

Do not flag: A single bold on the article subject or on a defined term at first mention is normal. Bold labels opening list items in scannable reference docs (docs profile relaxed) and one bold hook in a LinkedIn post (linkedin relaxed) are tolerated; casual registers skip the check. UI element names in how-tos are conventionally bold. im-not-ai applies the rule to column and report genres only. Markdown bold leaking into wikitext or plain text belongs to the artifacts category, not here; a bold-first bullet list is a structure pattern. A bolded acronym expansion ('**KPIs (Key Performance Indicators)**') carries two patterns at once; the bold is the finding here and the expansion is redundant-acronym-expansion, and one sentence is reported once.

### Comma density `comma-density`

Severity: **cluster** · Scope: universal

Document-level comma excess: commas inserted at every kind of syntactic boundary, so the part-of-speech variety on either side of commas runs far above the human norm (KatFish: human 24.4 vs AI 59.4), and the share of sentences carrying at least one comma runs above the baseline for the language. The thresholds are per language and do not transfer. Korean sits at about 26 to 33% of sentences and is flagged above 50%; English has no validated ceiling, so judge an English text by whether its commas fall anywhere other than main-clause joins and clear appositives. Convert some sentences by splitting them, absorbing the comma into a connective, or plain deletion.

Cues: `comma share > 50% (Korean baseline)` · `comma at every boundary`

Before: The team, which had grown quickly, met on Monday, reviewed the plan, and, after some discussion, agreed, in principle, to proceed.

After: The team had grown quickly. On Monday it reviewed the plan and agreed in principle to proceed.

Do not flag: The 26 to 33% baseline is Korean; recalibrate per language (English literary and legal prose runs far higher). In poetry and fiction the signal disappears (1.03x); the guard covers essays, news, blogs, QA and reports only. A single comma-heavy sentence is not a document-level signal. Measured by script, never by regex. English essay, report and legal prose routinely puts a comma in well over half its sentences, so the Korean share figure must never be applied to English as a ceiling.

### Curly quotation marks on a straight-quote surface `curly-quotes`

Severity: **cluster** · Scope: universal

Typographic quotes (U+201C, U+201D, U+2018) and the right-single-quote apostrophe (U+2019) on a surface whose convention is straight quotes: code, commit messages, Markdown, Reddit, plain email. Curly and straight forms mixed inside one text or one sentence is the stronger signal, because auto-curling software is consistent and a paste from a chat window is not. Convert to straight quotes only where the target uses them; never flag a curly apostrophe on its own.

Cues: `U+201C` · `U+201D` · `U+2018` · `U+2019` · `smart quotes` · `curly quotes` · `curly apostrophe in contractions (don’t, it’s)` · `curly apostrophe in possessives` · `mixed curly and straight quotes in one response`

Before: He said “the project is on track” but others disagreed.

After: He said "the project is on track" but others disagreed.

Do not flag: Word, Google Docs, macOS and iOS, most CMSes, LanguageTool and Chicago-style typesetting auto-curl, so finished publications, professionally typeset work and any Word-edited prose are exempt, as is a citation tool copying a page title. Only a tell on plain-text, Markdown, code and commit-message surfaces, and only when stacked with other tells. Never flag a curly apostrophe (U+2019) on its own. Locale-correct glyphs (French « », German „ “, Dutch „ ”) are not this pattern. Some fonts render curly as straight, so the distinction can be invisible to the reader. Gemini and Claude typically emit straight quotes; ChatGPT and DeepSeek curly. A bare curly-quote regex fired 13 to 100 times per 10,000 words on typeset human prose, so only the mixed form is scanned; the plain glyphs stay as cues for judgment.

### Immaculate typography in a rough register `immaculate-typography`

Severity: **cluster** · Scope: universal

Perfect spacing, punctuation and capitalization where humans type fast: issue and PR comments, chat, DMs, Reddit, quick email replies. The composite signature is curly quotes plus a non-separator em dash plus a serial (Oxford) comma plus machine cleanliness (no double spaces, no dropped apostrophes, no contractions, no odd fragment) in 80 or more words; any one alone means nothing and the stack is a weak corroborator only. The inverse rule when editing a human's casual text: preserve their typos, contractions and idiosyncratic capitalization, because smoothing them away erases what marks the text as theirs.

Cues: `no contractions` · `no double spaces` · `curly-quotes + em-dash + Oxford comma + zero typos` · `signals >= 4 && wordCount >= 80`

Before: I appreciate the thorough analysis, the clear documentation, and the prompt response. It is a well-considered proposal — one that I am glad to support.

After: Thanks for the writeup and the clear docs. Nice to get a reply that fast. It's a well-considered proposal and I'm glad to support it.

Do not flag: Formal academic and published prose legitimately has all of these; a careful human can type a flawless comment and a rushed one a sloppy one; Word-edited human prose matches the whole signature. Register-scoped: only weigh it on casual surfaces, and never as a conclusion on its own. The Oxford-comma and contraction sub-cues are English-specific. No regex: an Oxford-comma pattern fired 7 to 10 times per 10,000 words on human prose. The fix is contractions and a plain register, never manufactured sloppiness: lowercasing sentences or adding a comma splice on purpose is its own tell, and the entry's inverse rule only says to leave a human's own typos alone.

### List-label periods `list-label-periods`

Severity: **cluster** · Scope: universal

In a bulleted list whose items lead with a short label, the label ends with a period and the gloss runs on as a separate sentence ('- **Intros.** Years of conferences and operator network.') where a person would use a colon. Strongest with bold labels, weaker but still a tell without bold. Change the period to a colon and lowercase the gloss, or drop the label and write a plain sentence.

Cues: `**Intros.**` · `**Content distribution.**` · `**Developer GTM.**` · `- Intros. Years of conferences and operator network.`

Before: - **Intros.** Years of conferences and operator network.

After: - **Intros:** years of conferences and operator network.

Do not flag: When the label span is a full sentence on its own the period is correct. For the unbolded form flag only when the leading fragment is clearly a label (a one-to-four-word noun phrase with no verb); a short complete sentence opening a bullet is fine, which is why the regex covers the bold form only. A bold run-in sidehead closed with a period is an edited-prose convention (Chicago run-in heads; APA level 4 and 5 headings end with a period), so one hit proves nothing and the severity is a cluster reading. Inside a bulleted list the convention is weaker, and the flag holds where house style specifies the colon form or the surrounding text carries other tells.

### Parenthetical gloss overload `parenthetical-gloss-overload`

Severity: **cluster** · Scope: universal

Explanatory parentheses of the form '(this means ...)' or '(이는 ~을 의미한다)' tacked onto claim after claim in dense succession. Move most into the body or delete. The tell is the formulaic gloss, not parentheses as such: AI prose overall uses far fewer parenthetical asides than human prose, so parentheses are a human sign to observe and never to prescribe away.

Cues: `(this means` · `(which means` · `(that means` · `(this implies` · `(it indicates`

Before: Revenue grew 40% (this means the strategy is working). Churn fell (this means customers are happier).

After: Revenue grew 40% and churn fell, which points to the strategy working.

Do not flag: A single parenthetical aside is normal and human (AI 1.2 vs human 10.6 per 1k in the Korean corpus, a magnitude possibly inflated by the human corpus being edited professional prose); definitions in reference text; the missing-parentheses observation is observe-only and never a rewrite instruction. '(that is, ', '(i.e., ' and '(in other words, ' are ordinary human glosses and are deliberately not cues; the tell is the '(this means ...)' family repeated claim after claim, which is what the regex asks for. The Korean meta-label '괄호 부재' was dropped from the cues because it is a note about missing parentheses, not a string anything writes.

### Scare-quote excess `scare-quotes`

Severity: **cluster** · Scope: universal

Quotation marks around ordinary words for emphasis or ironic distance ('a "seamless" experience'), five or more per document. Keep real quotations; write everything else as plain text.

Cues: `a "seamless" experience` · `real" results` · `so-called "best practices` · `the "right" way` · `called the result a "win`

Before: The "innovative" platform offers "seamless" onboarding for "modern" teams with "real" results.

After: The platform offers onboarding for teams.

Do not flag: Direct speech inside double quotes is never touched; titles of works; a word mentioned as a word ('the term "cloud"'), which is why usage guides and grammar books light up; code identifiers; fewer than five in a document. The regex needs three single-word quoted spans on one line, so it catches the cluster, not the single case.

### Semicolon and colon rate skew `semicolon-colon-skew`

Severity: **cluster** · Scope: universal

The semicolon and colon repertoire deviates from human prose in a direction that depends on the model generation, and only one direction is flaggable. Overuse (GPT-5, a brevity bias) is the operational trigger: three or more semicolons splicing independent clauses inside one paragraph, measured by script against the genre baseline rather than a fixed ceiling. Substitute a full stop, or a comma plus a conjunction. The other direction, where the marks never appear and commas and dashes do their work, is observe-only. A scanner cannot flag an absence; it is something for the rewriter to know.

Cues: `three or more semicolons splicing independent clauses in one paragraph` · `The build failed; the logs were empty; nobody had been paged`

Before: The build failed; the logs were empty; nobody had been paged; the on-call rotation had lapsed.

After: The build failed and the logs were empty. Nobody had been paged because the on-call rotation had lapsed.

Do not flag: Lists whose items contain commas legitimately use semicolons; formal, legal and literary registers (the two controls run 72 and 75 semicolons per 10,000 words, and a two-semicolons-in-one-sentence pattern still fired 5.9 and 8.9 per 10,000, so both were dropped); absence of a mark cannot be flagged by a scanner and is an observation for the rewriter; which direction the skew runs depends on the model generation, so measure against the genre baseline, never a fixed ceiling. The bare ';' and ':' were dropped from the cues: every colon and semicolon in the language is not a cue, and an editor reading cues had no way to tell a legitimate mark from a spliced one.

### Thematic breaks between every section `thematic-breaks`

Severity: **cluster** · Scope: universal

A horizontal rule (---- in wikitext, --- or *** in Markdown, <hr>) inserted before every section or sub-section, common in Markdown output. A single rule marking a genuine shift is normal; the tell is one before each heading. Remove them and let the headings carry the structure.

Cues: `----` · `<hr>` · `horizontal rule before each heading`

Before: Early lexicographic records do not support this interpretation.

----

== History ==
Headwrapping practices are documented in historical sources.

----

== Form and construction ==

After: Early lexicographic records do not support this interpretation.

== History ==
Headwrapping practices are documented in historical sources.

== Form and construction ==

Do not flag: A single rule marking a genuine shift (before an appendix, a footer, a change of voice); YAML front matter delimiters at document start; a rule separating a table of contents; Markdown setext underlines (a text line directly followed by --- is a heading, not a rule, which is why the regex demands a blank line first); slide separators in Marp or reveal.js decks.

### Unnecessary hyphenation `unnecessary-hyphenation`

Severity: **cluster** · Scope: english

Hyphens where English does not want them: attributive-only forms used adverbially or as nouns ('in real-time', 'over the long-term', 'works out-of-the-box'); an -ly adverb hyphenated to its participle ('fully-automated'); a temporary compound modifier kept hyphenated after a linking verb ('the report is well-written'); compounds whose standard form is one word ('code-base', 'data-set', 'time-frame', 'road-map'); open noun phrases welded with a hyphen ('research-impact aggregator', 'data-source strategy'); and several hyphenated modifiers stacked before one noun. Keep the hyphen before a noun, and keep permanent compounds ('cross-functional', 'high-quality', 'third-party') hyphenated in every position, predicate included. The density of these particular corporate compounds is itself a vocabulary tell.

Cues: `the report is well-written` · `fully-automated` · `research-impact aggregator` · `data-source strategy` · `Python-package usage` · `Rust-crate usage` · `single-Project Manifest` · `total-downloads figures` · `life-sciences-native citation count` · `code-base` · `data-set` · `time-frame` · `road-map` · `in real-time` · `over the long-term` · `for the long-term` · `works out-of-the-box` · `a high-quality, well-architected, future-proof solution`

Before: The cross-functional team delivered a high-quality, data-driven report. The team is cross-functional and the report is well-written.

After: The cross-functional team delivered a high-quality, data-driven report. The team is cross-functional and the report is well written.

Do not flag: Keep the same compounds before a noun ('real-time analytics', 'long-term plan', 'out-of-the-box support'), and keep permanent compounds hyphenated wherever they sit, predicate position included: 'cross-functional', 'high-quality', 'data-driven', 'client-facing', 'decision-making', 'end-to-end', 'third-party', 'well-known', 'open-access', 'machine-readable', 'server-side', 'field-normalized', 'family-owned'. Those correct forms are not cues and 'the team is cross-functional' is not a finding; only a temporary modifier opens up after a linking verb ('the report is well written'). Spelling varies by dialect and house style, so ambiguous pairs are judgment calls; older prose hyphenates 'to-day' and 'to-morrow' by convention. Code, quoted material, URLs, paths, filenames, command flags, tables, YAML and blockquotes are masked first. A clear hit is P2 copyediting (detector weight 0), never evidence of machine authorship. Two stacked compounds that each carry a fact ('a 32-bit, little-endian value') are spec content, and a deliberate literary triple in a description is voice. Stripping a buzzword stack is a vocabulary edit; this entry only rules on the hyphens inside it.

### Capital letter after a colon `capitalized-after-colon`

Severity: **context** · Scope: english

The clause after a colon starts with a capital letter where grammar, a proper noun, a title or code does not require it ('Two options remain: We ship now'). Usually a by-product of the colon-reveal habit. Use sentence case after colons.

Cues: `colon followed by capital letter`

Before: Two options remain: We ship now or we wait for the fix.

After: Two options remain: we ship now or we wait for the fix.

Do not flag: Proper nouns, titles and code after the colon; AP and Chicago style capitalize a complete sentence after a colon, so a house style can make it legitimate; a colon that introduces quoted speech; a label line ('Note: The ...') in documentation. The rule is a sub-tell of the colon reveal (rhetoric) and only worth raising when that pattern is present. Capitalization rules after a colon are language-specific in detail, so the regex is English-shaped and carries a scoped case-sensitive group.

### Hashtag stuffing `hashtag-stuffing`

Severity: **context** · Scope: universal

A long trailing block of hashtags on a short post (six or more, typically one project-specific tag plus broad category tags such as #AI #Innovation #Technology). Human posts past five tags are usually launch posts; LLM posts default to 10 to 15. Reduce to two or three specific tags or none; if a tag would not help a reader find related work, it is filler.

Cues: `#Crypto` · `#Web3` · `#Innovation` · `#FutureTech` · `#Technology` · `(?:^|\W)#(\w[\w-]*)`

Before: #AI #Crypto #Web3 #Innovation #FutureTech #Technology

After: #devmeetup #meetup

Do not flag: Not counted: issue and PR references (#88, owner/repo#88), CSS hex colours with a digit (#1a2b3c), C preprocessor directives, URL fragments, Markdown headings, anything inside a code span or fence. Still counted: short hex-shaped words (#fff, #dad) and channel names (#general). Severity is profile-bound: P0 on LinkedIn and investor email, P2 on a blog where a launch post may stack tags, skipped on docs and casual surfaces. Five tags is a soft tell on social profiles; six is the hard flag.

### Skipped heading levels `heading-level-skipping`

Severity: **context** · Scope: universal

Sections begin at the third heading level (### or ===) with no second-level heading above them, or any heading sits more than one level below its parent. Against accessibility and style conventions on every surface, and on Wikipedia, where section hierarchies are edited to house style, a manually formatted page very rarely has this quirk. Renumber the hierarchy so each level is one deeper than its parent.

Cues: `=== as the first section heading with no ==` · `### with no ## above` · `heading level jumps by two`

Before: ### Background
The project started in 2024.
### Method
We interviewed twelve teams.

After: ## Background
The project started in 2024.
## Method
We interviewed twelve teams.

Do not flag: A fragment excerpted from a longer document; comment lines in shell or Python code fences ('# comment') the scanner has not masked; a surface that renders the page title as H1 so body sections correctly start at ##; a deliberate H1 title followed by ## sections. Hand-written READMEs and notes commonly start body sections at ### under a single H1, and an excerpt or an unmasked code fence produces the same shape, so treat a skip as a formatting fix rather than evidence of machine authorship unless other tells sit around it. The 'very rarely' reading comes from the Wikipedia source and holds on encyclopedic surfaces.

### Level-1 headings for body sections `level-1-heading-overuse`

Severity: **context** · Scope: universal

Level-1 headings (# or = H1 =) used for ordinary body sections on a surface that reserves level 1 for the page title (Wikipedia, most CMSs, HTML documents with a rendered title). Usually produced by translating Markdown '#' headings one-to-one into the target markup. Demote body headings by one level.

Cues: `= Heading =` · `multiple # H1 headings in one document` · `= History =` · `= External Links =`

Before: = History =
[...]
= Programming =
[...]
= Main Characters =
[...]
= External Links =

After: == History ==
[...]
== Programming ==
[...]
== Main characters ==
[...]
== External links ==

Do not flag: A standalone Markdown file or README with one H1; shell comments in code fences; a surface where the H1 is the document's own title. A tell only where the surface renders the title itself and the body carries several H1s.

### Redundant acronym expansion `redundant-acronym-expansion`

Severity: **context** · Scope: universal

Every acronym is spelled out in parentheses at first use even when the audience owns the term, often in the reversed 'KPIs (Key Performance Indicators)' order, wrapped in bold, and done for every term in the sentence. Drop the expansion where the reader plainly knows the term; keep expansion-then-acronym only for a term the audience may not know.

Cues: `OKRs (Objectives and Key Results)` · `KPIs (Key Performance Indicators)` · `Balanced Scorecard (BSC)` · `CRM (Customer Relationship Management)` · `**Business Model Canvas (BMC)**`

Before: The team tracked KPIs (Key Performance Indicators) against OKRs (Objectives and Key Results) in the CRM (Customer Relationship Management) system.

After: The team tracked KPIs against OKRs in the CRM.

Do not flag: Legitimate in reference, onboarding and regulatory text, at a genuine first mention of a term the audience does not know, and under house styles that require expansion at first use. The tell is expanding terms the reader plainly owns, and doing it for every term in a sentence; a single expansion is never a finding. Implied only by the humanizer §15 after-example. The example is deliberately bold-free: when the expansion arrives in bold the bold half belongs to bold-overuse, and one sentence is reported once.

### Title case headings `title-case-headings`

Severity: **context** · Scope: english

Every main word of a section heading is capitalized ('Strategic Negotiations And Global Partnerships'), sometimes conjunctions included, where the surface's house style, medium or language uses sentence case. A capitalized function word mid-title (And, Or, Of) and a length of four or more tokens are the stronger signs. Use sentence case for subheadings; title case only for the piece's main title, if at all.

Cues: `## Strategic Negotiations And Global Partnerships` · `Strategic Negotiations And Key Partnerships` · `## Benefits And Strategic Considerations` · `Impact of Technology and Digitalization` · `Sustainable Development and Environmental Law` · `Human Rights and Economic Law` · `capitalized And/Or/Of/The/In/For/To/A/An mid-title`

Before: ## Strategic Negotiations And Global Partnerships

After: ## Strategic negotiations and global partnerships

Do not flag: Publications whose house style is title case (many US newspapers, some journals), API docs, ML papers and headlines; the piece's main title; headings of three or fewer tokens ('Terms Of Service'); headings opening with 'The', 'A' or 'An' (a bare 'The' check gave 13 false positives across 81 pre-LLM files, so the regexes exclude a leading article); proper nouns and product names; code fences; technical mode skips it. The regexes carry a scoped case-sensitive group because the scanner runs case-insensitive, and they only look at marked-up headings ('#', '=='), so a plain-text heading is judgment. In Dutch, German and most non-English languages title case does not exist, so there it is a stronger tell and belongs with translationese. Two- and three-token headings ('Target Audience', 'External Links') were dropped from the cues because the same false_positives exempts them, and 'Title Case' because it is the name of the phenomenon rather than text a model writes.

### Arrows as prose connectives `unicode-arrows`

Severity: **context** · Scope: universal

Typographic arrows (→, ⇒) or their ASCII forms (->, =>) used in running prose where a writer would say 'leads to', 'then' or write a sentence ('Input → Processing → Output', 'better outcomes → higher engagement'). Claude in particular favors ->. Spell the relation out.

Cues: `Input → Processing → Output`

Before: This leads to better outcomes → which means higher engagement

After: This leads to better outcomes, and better outcomes mean higher engagement.

Do not flag: Diagrams, code, CLI output, type signatures, commit messages and migration notes describing a rename (a -> b), mathematics, and technical docs where the arrow is notation; the tell is the arrow doing the job of a verb in prose.

### Unnecessary small tables `unnecessary-tables`

Severity: **context** · Scope: universal

Small tables (a handful of rows) holding facts that read better as a sentence or an infobox: a two-column Metric/Figure or Name/Designation table, or a Feature/A/B comparison with a 'Comparison of X and Y' or 'Key Statistics' caption. The tell is the mismatch between table form and small, prose-shaped content. Fold the facts into prose.

Cues: `| Metric | Figure |` · `! Metric !! Figure` · `| Feature | Option A | Option B |` · `Key Statistics` · `Name !! Designation` · `Comparison of` · `Key management personnel ... include:` · `The structural similarity between ... is striking:`

Before: {| class="wikitable"
|+Key Statistics of Indian Biobanking (2024-2025)
!Metric
!Figure
|-
|Market Valuation (2024)
|~USD 2.1 billion
|-
|Major Accredited Facilities
|NLDB, CBR Biobank, THSTI, Karkinos
|}

After: The Indian biobanking market was valued at about USD 2.1 billion in 2024; the major accredited facilities are NLDB, CBR Biobank, THSTI and Karkinos.

Do not flag: Genuinely tabular data (many rows, numeric columns, comparison matrices with more than a few cells); infobox-style data on a surface that has no infobox; API reference and configuration tables. The source labels this 'rare'. The bare words 'Metric', 'Figure' and 'Feature' were dropped from the cues: they carry signal only as a header row, which is what the regexes match.

## Content and evidence

### Empty caveat slot `empty-caveat-slot`

Severity: **always** · Scope: universal

A concession sentence that names no concession: an unnamed challenge paired with an unnamed response ('Despite challenges, the organisation continues to thrive', 'While facing headwinds, it remains resilient'), or a stand-alone 'limits remain' line after a run of positive claims. It performs balance and adds no information. Name the actual challenge and the actual response, or cut the sentence. The pivot form is the same defect in a clause: 'While X is impressive, Y remains a challenge', 'Although X has made strides, Y is still an open question', a vague compliment granted only in order to turn.

Cues: `Despite challenges, [subject] continues to thrive` · `While facing headwinds, the organization remains resilient` · `While X is impressive, Y remains a challenge` · `Although X has made strides, Y is still an open question` · `While X is impressive, ...` · `Despite its challenges, ...`

Before: Despite challenges, the cooperative continues to thrive.

After: The cooperative lost its largest buyer in 2024 and replaced the volume with three regional wholesalers.

Do not flag: A concession that names the thing conceded is good writing: 'despite losing its export licence in March, the plant kept two shifts'. The closing-block form of this, a whole 'Challenges and Future Directions' section, is owned by the structure category; here the unit is the contentless sentence or the concessive clause inside one. Do not flag a caveat that is elaborated in the following sentence. A concession with named specifics on both sides is argument, not padding.

### Fabricated bylines and datelines `fabricated-bylines-and-datelines`

Severity: **always** · Scope: universal

Publishing metadata that does not correspond to anyone or anywhere: author bios and headshots for reporters who do not exist, and date or place lines that contradict the events described. Distinct from the prose tells, this is fabricated provenance attached to the piece, and it is checkable against staff directories, image marketplaces and the event record.

Before: By Drew Ortiz. Drew has always had a passion for the outdoors and lives in the countryside with his dog.

After: Byline removed: no such staff member exists and the portrait comes from a stock AI-face marketplace.

Do not flag: Pen names, house bylines ('By the Economist'), and staff writers who keep a low online presence are all legitimate. Wire copy carries the originating dateline, which can look wrong beside a later local event. Verify against the masthead and the event record rather than assuming.

### Invented concept labels and novelty inflation `invented-concept-labels`

Severity: **always** · Scope: universal

A pseudo-analytical compound is coined mid-sentence and never defined ('the supervision paradox', 'the context-collapse problem', 'a coordination tax', 'workload creep'), or an established concept is credited to the subject as a discovery ('he introduced a term', 'she coined the phrase'). A related header form wraps the coinage in scare quotes to make it look canonical. Naming a thing is not explaining it: define the term on first use, describe the mechanism instead of branding it, and assume a concept is not novel unless you can show it is. The noun counts only inside the frame 'the <abstract modifier> <noun>' where the compound is never defined; paradox, tax, trap and creep on their own are ordinary vocabulary.

Cues: `the supervision paradox` · `the context-collapse problem` · `a coordination tax` · `the acceleration trap` · `workload creep` · `He introduced a term` · `She coined the phrase` · `a concept nobody's naming` · `a failure mode nobody talks about` · `Portability and the "Pocket Meal` · `The "Cold" Factor` · `The Sephardic "Home Factory` · `Portuguese Sailors as "Early Adopters` · `The Iberian Potato "Infrastructure`

Before: This is the supervision paradox: the more you automate, the more you must watch.

After: Automating the checks moved the work: someone now reads 200 diff summaries a week instead of writing 20 diffs.

Do not flag: Established terms with literature behind them stay: scope creep, the digital divide, technical debt, the tragedy of the commons. A writer may coin a term deliberately, define it, and use it consistently; that is theory-building, and the definition is what separates it from slop. One defined coinage may be deliberate theory-building; several undefined ones in a piece is strong evidence of slop. Verify novelty claims against the record before rewriting them.

### Analysis misattributed to a named source `misattributed-source-analysis`

Severity: **always** · Scope: universal

A retrieval-augmented model attaches its own interpretive gloss to a real named source or citation, whether or not that source says anything of the kind: 'Roger Ebert highlighted the lasting influence', 'Fridrichova highlights that ... emphasizing their critical view', 'This citation demonstrates the enduring relevance'. The citation is real, the claim about it is generated. Only reading the cited source settles it.

Cues: `Roger Ebert highlighted the lasting influence` · `Fridrichová highlights that` · `emphasizing their critical view` · `This citation demonstrates the` · `demonstrating his influence`

Before: Fridrichova analyzes the distinction made by Blois and Bar, emphasizing their critical view on truncations. This citation demonstrates the enduring relevance of Blois's work.

After: Fridrichova (2019, p. 44) compares Blois and Bar's treatment of truncation.

Do not flag: A gloss the cited source actually supports is normal scholarship, so verify before flagging rather than deleting on sight. Review essays and historiography legitimately characterise what a body of work emphasises. The tell is an interpretive claim about a source that the source does not make, usually in participial form and usually about influence or legacy.

### Promotional and brochure register `promotional-language`

Severity: **always** · Scope: universal

Prose meant to inform drifts into advertisement: evaluative adjectives, travel-guide framing, and press-release verbs applied to places, communities, people, companies or products. Sub-forms: the cultural-heritage travel guide ('nestled', 'breathtaking', 'rich cultural heritage', 'a town worth visiting'), the corporate press release ('commitment to sustainability', 'communicates a powerful emotional presence'), and the product round-up built from generic praise ('durable construction', 'excellent value') with no test behind it. Replace with plain description and a checkable fact.

Cues: `boasts a` · `rich (figurative)` · `profound` · `enhancing its` · `in the heart of` · `groundbreaking (figurative)` · `renowned` · `must-visit` · `nestled within the breathtaking foothills` · `a vibrant hub of innovation` · `a thriving ecosystem` · `diverse array` · `From its scenic landscapes to its historical landmarks` · `offers visitors a fascinating glimpse into the diverse tapestry` · `unique characteristics` · `a town worth visiting` · `its significance` · `acts as the gateway` (+21)

Before: Nestled within the breathtaking region of Gonder in Ethiopia, Alamata Raya Kobo stands as a vibrant town with a rich cultural heritage and stunning natural beauty.

After: Alamata Raya Kobo is a town in the Gonder region of Ethiopia.

Do not flag: Deliberately promotional registers are governed by the voice rules: marketing copy, a tourism board's own site, a launch announcement. Tolerance is relaxed for LinkedIn, strict for reporting and docs, extra strict for investor mail. 'rich' and 'groundbreaking' count only in figurative use ('rich in iron' is fine). Not all spammy writing is AI, and newer models are subtly positive rather than superlative, so the absence of 'the best' proves nothing either way. 'exemplifies' is ordinary academic register ('the graph exemplifies the trend'); count it only where the subject is a brand, a product or a place.

### Significance and legacy inflation `significance-inflation`

Severity: **always** · Scope: universal

An ordinary fact is framed as a turning point, a legacy, a symbol, or evidence of a broad trend, using a small recognisable set of significance verbs and nouns: 'marks a pivotal moment', 'stands as a testament', 'plays a vital role', 'underscores its significance', 'enduring legacy', 'evolving landscape'. Sub-forms: self-labelling significance ('this is a crucial insight'), significance bolted onto mundane facts such as an etymology or a census figure, an abstract that stresses implications while naming no result, and regression to the mean, where the concrete detail disappears and the importance claim gets louder in its place. State the fact and let the reader judge; if the sentence still works with the significance clause deleted, delete it. Korean carries the same move as 시사하는 바가 크다 / 주목할 만하다 / 매우 중요하다 / 의미가 크다, with the stock評 forms 기록적인 성과를 거두었다, ~로 평가된다 and 주목받았다.

Cues: `is a testament/reminder` · `a vital/significant/crucial/pivotal/key role/moment` · `underscores/highlights its importance/significance` · `reflects broader` · `symbolizing its ongoing/enduring/lasting` · `setting the stage for` · `marking/shaping the` · `represents/marks a shift` · `key turning point` · `evolving landscape` · `indelible mark` · `Stands as a testament` · `marks a pivotal moment` · `plays a vital role` · `solidifies its position` · `underscores its significance` · `a testament to` · `marking a pivotal moment in the evolution of...` (+19)

Before: The Statistical Institute of Catalonia was officially established in 1989, marking a pivotal moment in the evolution of regional statistics in Spain. This initiative was part of a broader movement across Spain to decentralize administrative functions.

After: The Statistical Institute of Catalonia was established in 1989, during a wider decentralization of administrative functions in Spain.

Do not flag: A genuinely pivotal event described with a sourced reason stays: the tell is the claim standing in for the reason, not the word. Obituaries, award citations, anniversary pieces and marketing copy the writer intends are register-appropriate; tolerance is strict for reporting, technical writing and investor mail, relaxed for docs, skipped for casual chat. 'stands as' and 'serves as' also belong to copula avoidance under syntax; flag under whichever mechanism the sentence actually shows. Do not flag a summary sentence that names a specific measured result. A significance claim that names what follows from it is not inflation ('the implications are significant: every client must re-key before March'). In academic abstracts the significance sentence is a genre requirement, though it should still carry content. Overlap here is owned rather than shared. The unmeasured comparative ('significantly improves') counts under abstraction-over-specifics, the interpretive gloss on a named source ('highlights the lasting influence') under misattributed-source-analysis, and the trailing participle under participial-tail in syntax. Count a sentence once, under the mechanism it shows.

### Speculative gap-fill dressed as fact `speculative-gap-fill`

Severity: **always** · Scope: universal

Where the model found nothing it asserts that nothing exists ('details are not widely documented') and then fills the hole with hedged invention introduced by 'likely', 'may', 'appears to have'. A frequent sub-form attributes deliberate privacy to a living person ('maintains a low profile', 'keeps personal details private') when the real situation is that the model has no data. Both the absence claim and the guess are unverified. Delete both, or state plainly what the sources do not show.

Cues: `maintains a low profile` · `keeps personal details private` · `prefers to stay out of the spotlight` · `likely [grew up/studied/began]` · `it is believed that` · `maintains a relatively low public profile` · `is believed to have` · `likely began his career in` · `appears to have studied` · `While specific details are limited` · `While specific details are scarce` · `While specific information about` · `not widely available` · `not widely documented` · `not widely disclosed` · `not widely transcribed` · `aren't widely documented` · `are not extensively documented in readily available sources` (+7)

Before: Information about her early life is not publicly available, suggesting she maintains a low profile. She likely grew up in a middle-class household.

After: Her early life is not covered by the sources used here.

Do not flag: A sourced statement that a person declines interviews, or a documented archival gap ('the 1911 census returns for this district were destroyed'), is a fact and stays. Scientific hedging over evidence the writer has read and cites is normal ('the isotope ratios suggest a volcanic origin'). The tell is a hedge covering an absence of looking rather than an absence in the record. 'in the provided search results' additionally leaks the retrieval prompt and should always go.

### Treadmill (restating without advancing) `treadmill-redundancy`

Severity: **always** · Scope: universal

Paragraphs restate the premise in fresh words instead of advancing it: motion without distance. Signs are a passage that loses no information when cut by 40 to 60 percent, connections between paragraphs asserted rather than made, and filler that spends words without adding a claim. For each paragraph name the one fact, claim or turn it contributes; if there is none, cut it, and if there is one, lead with it. It also shows as one thesis restated with a fresh metaphor in every section until an 800-word argument fills 4,000, and as a model repeating itself late in a long session. Say it once and delete the rest, especially the paragraph the author is proudest of.

Before: Testing matters. Without tests, teams cannot be confident in their changes. This lack of confidence slows delivery, because engineers hesitate to change code they cannot verify.

After: Without tests, engineers hesitate to change code, and our median PR sat for three days.

Do not flag: Deliberate repetition for teaching, liturgy, speeches and children's writing is a device, not slop. Summaries and abstracts restate by design, and a recap after a long technical section helps. Newer, terser models waffle less, so low density is weaker evidence than it was. Measure by information added per paragraph rather than by length. A restatement that adds a new consequence, condition or example is not a treadmill, and the remedy for session repetition is procedural (a fresh context), not a rewrite rule.

### Vague attribution to unnamed authority `vague-attribution`

Severity: **always** · Scope: universal

A claim is credited to an authority the text never identifies: experts, studies, research, observers, critics, analysts, industry reports, scholarship. Sub-forms: vague third-party validation, where an unnamed outside party supplies a generic superlative ('independent testing confirms', 'widely regarded as'), and the agentless verdict, where the judgement is stated as 'the analysis is that X' with no one judging. Name the source, the test and the result, or cut the claim; if the writer has no source, ask rather than invent one.

Cues: `Observers have cited` · `Experts argue` · `Some critics argue` · `several sources/publications (when few cited)` · `Experts agree` · `industry reports suggest` · `many argue` · `widely regarded as` · `studies show` · `Experts believe` · `Research suggests` · `Industry leaders agree` · `independent testing confirms` · `third-party benchmarks show we lead` · `analysts agree` · `studies consistently show` · `an outside party` · `experts say` (+5)

Before: Experts believe it plays a crucial role in the regional ecosystem.

After: Researchers at Wageningen University measured its share of the local sediment budget at 11 percent (Kok, 2021).

Do not flag: Specifically attributed, checkable validation stays: a named benchmark, a linked report, a dated audit ('SOC 2 Type II, audited by Prescient Assurance'). A field's genuine consensus, cited, is fine ('the 2019 IPCC report concludes'). The absence of a footnote is not itself the tell; the vague attribution phrase is. In review-of-literature registers 'studies show' followed immediately by the citations it summarises is normal. Never invent a source to satisfy this rule.

### Tenuous ecosystem, heritage and conservation padding `ecosystem-heritage-padding`

Severity: **cluster** · Scope: universal

Writing about a species, place or artefact is padded with generic ties to the wider ecosystem, environment or cultural heritage even where the tie is unsupported, and dwells on conservation status, threats and preservation effort where no assessment and no effort exist. The give-away shape is conceding the absence of an assessment and then speculating about threats anyway. Keep sourced ecology and cut the rest.

Cues: `plays a role in the ecosystem` · `contributes to Hawaii's rich cultural heritage` · `crucial for the survival of this and other endemic species` · `the general health of the ... ecosystem` · `there is no specific conservation assessment` · `Preserving this endemic species is vital` · `could potentially impact their populations` · `Factors such as overfishing, pollution, and habitat destruction` · `conservation status`

Before: It plays a role in the ecosystem and contributes to Hawaii's rich cultural heritage. Preserving this endemic species is vital for ecological diversity.

After: The species is endemic to Kauai and grows only above 900 metres.

Do not flag: A cited IUCN category, a documented recovery programme, or a named study of the species' ecological function is content, not padding. Conservation-focused publications are expected to lead with status. The tell is a status section that admits there is no status, or an ecological role asserted with no source.

### Hallucinated or unverifiable citations `hallucinated-citations`

Severity: **cluster** · Scope: universal

References that cannot carry the claim: URLs to sites that never existed or 404 with no archive copy, ISBNs that fail their checksum, DOIs that do not resolve or resolve to an unrelated paper, real journals with invented volumes, pages or author lists, books cited with no page number or link, placeholder identifiers built from a tiny number (pubmed.ncbi.nlm.nih.gov/3), and invented rules, policies or shortcut links that say something other than claimed. Resolve every identifier, compare the title and authors, and check the cited page actually contains the claim. A real journal name, a DOI, an ISBN or a page number is a locator to resolve, never a tell on its own.

Cues: `https://pubmed.ncbi.nlm.nih.gov/3` · `pmid=3` · `per policy` · `guidelines state`

Before: M. E. Van Valkenburg, "The validity and limitations of Ohm's law in non-linear circuits," Proceedings of the IEEE, vol. 62, no. 6, 1974. doi:10.1109/PROC.1974.9547

After: Citation removed: the DOI resolves to an unrelated paper and the article does not appear in that volume.

Do not flag: Link rot is ordinary: a dead URL with an archive copy, a paywalled journal that works through a library, or a link mangled by a bot or a copy-paste is a human error, not a hallucination. One broken reference proves nothing; several in one new passage, none archived, is the signal. A 2018 to 2023 VisualEditor bug inserted low-numbered PubMed ids that look fabricated and are not. Page-number-free book citations are common in older articles written by people. The regexes here only locate identifiers to check, they do not by themselves indicate a problem.

### Lost prior-thread context `lost-thread-context`

Severity: **cluster** · Scope: universal

A reply does not answer what the earlier message asked: it responds to the topic rather than the question, drops the specifics raised upthread, and reintroduces information already settled. In correspondence this is the clearest sign that the text was generated from a summary rather than from the thread.

Before: Thanks for reaching out about the invoice. Our billing team is happy to help with any questions you may have.

After: Invoice 2214 was raised against the old PO. I have credited it and reissued against PO 8871 as you asked on Tuesday.

Do not flag: People also skim, forward threads to colleagues who lack the history, and answer from a phone. Long threads legitimately restate context for new recipients. Flag when the reply cannot be reconciled with a question that was asked plainly and recently.

### No concrete particular (portable sentence) `missing-concrete-detail`

Severity: **cluster** · Scope: universal

The text stays at the level of the generic and the widely applicable, with no proper noun, no brand, no street, no month, no odd quote, nothing that could only be here. The test is portability, if a sentence could move unchanged to another person, company, country or product, it is filler. This works as a signal over a whole passage rather than as an edit on one line. When no sentence in a passage carries a particular, flag the passage and ask the writer for the detail; cut what stays generic, keep the details the writer already supplied, and never manufacture one. Where the draft does supply the specific and an abstraction stands in for it, the entry to use is abstraction-over-specifics, whose fix is a direct replacement.

Before: Wander a few steps off the main squares and you'll discover a quieter, more authentic side: sun-drenched alleys, charming tiled facades, and friendly locals going about their daily lives.

After: Cut, and ask the writer what stands two blocks uphill from the plaza before the sentence goes back in.

Do not flag: Abstracts, definitions, glossary entries, policy text and executive summaries are meant to generalise, and short transitional sentences carry structure rather than fact; leave those alone. Elsewhere run the portability test sentence by sentence. As a detection signal rather than an editing rule it needs a whole passage of portable sentences, since one generic line proves nothing. The fix is additive, so flag the gap for the writer rather than inventing a detail to fill it. Where the specific is present in the draft and an abstraction stands in for it, flag abstraction-over-specifics instead and count once.

### Missing first-hand detail and stated view `missing-first-hand-detail`

Severity: **cluster** · Scope: universal

In a piece whose register invites a voice, nothing appears that only this author could supply: no anecdote, no measured number from their own run, no named failure, no preference, no 'I think'. The prose is relentlessly neutral where a position was expected, or generic where a prompt asked for reflection. A useful check is roughly one author-specific detail per section, such as a named failure or a number from the writer's own run; at zero, flag the gap and ask the writer rather than supplying the detail yourself.

Before: There are several approaches to on-call, each with trade-offs, and teams should choose what fits them.

After: We ran follow-the-sun for eight months and it cost us two engineers; a one-week rota with a hard handover note works better for a team of six.

Do not flag: Encyclopedic, technical, legal and news registers are correctly neutral, and their neutrality is not a defect. Never inject an 'I' the source does not have: flag the gap and ask the writer for the detail rather than fabricating presence, since a fabricated anecdote is a worse failure than a flat paragraph. The string 'in my experience' is a cue on fake-first-person, where its presence is the tell; here the signal is its absence, so no phrase match belongs to this entry.

### Notability name-dropping and over-attribution `notability-name-dropping`

Severity: **cluster** · Scope: universal

Importance is argued by cataloguing where the subject appeared rather than what was said: a roll-call of prestigious outlets, a classification of those outlets ('independent coverage', 'regional media outlets', 'trade publications'), or a follower count. A related change-note form praises an edit for being 'sourced' or 'verified' instead of saying what it added. Keep one citation with context; cut the roll-call, the classification and the count.

Cues: `independent coverage` · `local/regional/national media outlets` · `written by a leading expert` · `active social media presence` · `cited in The New York Times, BBC, Financial Times, and The Hindu` · `local media outlets` · `regional media outlets` · `music outlets` · `business outlets` · `tech outlets` · `trade publications` · `other prominent media outlets` · `documented in archived school event programs and regional press coverage` · `has also been mentioned in ... coverage relating to` · `profiled in multiple high-quality, independent, and widely-read outlets` · `appearing in platforms` · `significant, substantial, secondary coverage` · `Repeated national media coverage` (+11)

Before: Her views have been cited in The New York Times, BBC, Financial Times, and The Hindu. She maintains an active social media presence with over 500,000 followers.

After: In a 2024 New York Times interview she argued that regional statistics offices should publish raw microdata.

Do not flag: Where the source explains what was said and where, that is a useful citation; keep it and do not invent context to shorten it. Press kits, bios and grant applications have listed clippings for decades and are not AI by that fact; the distinguishing marks are the classification of the outlets and the focus on their availability rather than their content. Deletion-discussion arguments legitimately count sources. This form is more common in tools released from 2025 on, and often travels with a fabricated citation, so check that the references exist.

### Situating the subject in an unnamed debate `unnamed-debate-situating`

Severity: **cluster** · Scope: universal

The subject is said to have generated, sparked, shaped, or prompted debate, discussion, or reflection, or to raise questions, with no debate, participant, venue or date ever named. It reads as context while adding none. Name the debate and who is in it, or cut the sentence.

Cues: `generated debate` · `debates` · `participated in public discussions` · `shaped emerging policy discussions` · `prompted broader reflection` · `raising philosophical questions`

Before: The phenomenon has generated debate about authenticity, consent, and the psychological effects of digitally extending personhood.

After: In a 2025 paper in AI & Society, Hollanek and Nowaczyk-Basinska argue that griefbots need consent from the person being simulated.

Do not flag: A named, cited controversy is normal encyclopedic content: 'the 2023 exchange between Marcus and LeCun over scaling' is a debate with participants. Flag only when the debate has no name, no party and no source. Opinion columns that describe a live public argument they then quote are also fine.

### Vague expression of connection `vague-association`

Severity: **cluster** · Scope: universal

A concrete relationship (was CEO of, taught at, composed for, received) is replaced by an unspecified link: 'associated with', 'in connection with', 'connected to', 'particularly associated'. The sentence looks sourced while saying nothing checkable. Recover the actual relation from the source and state it. Where the source is itself vague, keep the vagueness and name who is being vague.

Cues: `in connection with` · `in connection to` · `connected with` · `connected to` · `in association with` · `particularly associated` · `widely associated` · `has been associated with` · `associated principally with` · `is associated with` · `became associated with`

Before: In 2017, sources identified John Doe as being associated with leadership of ExampleCorp. The cited Reuters piece calls him chairman of the board.

After: Reuters reported in 2017 that John Doe chaired ExampleCorp's board.

Do not flag: Some relations really are vague and the vagueness is the fact: an arrest 'in connection with' an investigation, a school of thought 'associated with' a city, a name 'associated with' a brand in the public mind. Legal and police reporting uses the phrase precisely. The indirection alone does not prove AI authorship; its abundance alongside other signs does.

### Absent human friction (asides, quotes, era markers) `absent-human-friction`

Severity: **context** · Scope: universal

Corroborating absences rather than phrases: the text never interrupts itself with a parenthetical self-correction or a real aside, never admits an unresolved mixed feeling, quotes nobody, and carries no era-bound slang, meme or in-joke, or carries one that is a year or more stale. Published human prose quotes freely and contradicts itself in passing. Treat these as weak corroboration and preserve them wherever a human wrote them.

Before: The migration went well and the team was pleased with the outcome.

After: Ask who was on the bridge that night and whether anyone said anything worth quoting; the sentence stays as it is until they answer.

Do not flag: Observe only, never prescribe: inventing a quotation is unacceptable, and manufactured asides read worse than none. Reference documentation, standards, legal text and abstracts have no place for asides or slang. Measured Korean-corpus rates (AI 0.0 versus human 8.7 quotations per 1,000 words) are corpus-level evidence and do not convict a single short piece.

### Abstraction where a specific exists `abstraction-over-specifics`

Severity: **context** · Scope: universal

A claim is stated in abstract terms where a name, number, date, mechanism or example the draft already supplies would do the work: 'improved efficiency', 'significantly faster', 'a large image', 'a database' for the product's actual name. Sub-forms: abstract quantifiers standing in for a measured value, category words standing in for the thing's name, and abstraction drift, where well-formed sentences carry generic nouns and hypothetical examples and no one has a last name. Replace each abstraction with the concrete detail the draft already supports. Where no specific exists anywhere in the passage, the signal is missing-concrete-detail and the move is to flag the gap for the writer.

Cues: `improved efficiency` · `significantly improves` · `significantly faster` · `a large image` · `a database and a tool` · `boosted productivity` · `enhanced performance`

Before: The integration improved efficiency.

After: The integration cut deploy time from 40 minutes to 4.

Do not flag: Two of the four sources rate this always; the context reading is kept because the fix needs a concrete detail the draft already supplies. Only flag when that detail is available: the editor must not invent a number, and 'significantly' is correct where it reports a statistical test. Abstract nouns are the subject matter in philosophy, law and poetry. A category word is right when the category is the point ('pick a database with MVCC'), or when the specific name is confidential. This entry owns the missing-measurement case, so 'significantly improves' counts here and not under significance-inflation.

### Diff-anchored writing `diff-anchored-writing`

Severity: **context** · Scope: universal

Documentation, comments or prose describe the thing as a change from a state the reader never saw: 'This function was added to replace the previous approach', 'the improved version now handles'. A reader without the commit history gets archaeology instead of behaviour. Describe what it does now, and put the history in the changelog or the commit message.

Cues: `was added to replace` · `the previous approach` · `the old implementation` · `the improved version now` · `replaces the old logic` · `unlike the previous version`

Before: This function was added to replace the previous approach of iterating through all items, which caused O(n^2) performance.

After: This function looks items up in a hash map, so a lookup costs O(1).

Do not flag: Version-scoped documents narrate change correctly and stay unflagged: changelogs, release notes, migration guides, upgrade notes, decision records, postmortems, and any document whose subject is the change. A comparison that helps a reader migrating from the old API is content. Flag only where a standalone description of current behaviour was expected.

### Fabricated first-person experience `fake-first-person`

Severity: **context** · Scope: universal

First-person experience claims appear in prose that had no author behind them: 'I've seen this a hundred times', 'in my experience', 'I'll admit', or a lyric 'I' with no body, situation, history or place. On the rewriting side any added 'I' is a failure, since provenance is the whole question and no phrase can show it. If the source has no first person, the rewrite has none.

Cues: `I've seen this a hundred times` · `in my experience` · `I'll admit`

Before: I've seen this a hundred times: teams ship the migration and skip the rollback.

After: Teams commonly ship the migration and skip the rollback.

Do not flag: A first-person aside the author actually wrote is not a flag; the same sentence is fine or fatal depending on who wrote it, which no pattern can see. Memoir, essay, field report and any interview transcript live in the first person by design. Judge on provenance, and where you cannot know it, flag rather than delete.

### Gratuitous universals and category errors `gratuitous-universals-and-category-errors`

Severity: **context** · Scope: universal

Authority borrowed from a scope the writer cannot check ('taught in every first-year biochemistry course', 'every engineer knows'), and moral or evaluative adjectives attached to things that cannot carry them, including assumptions and abstractions treated as if they had intentions or virtues. Replace the quantifier with the real scope, and the moral adjective with the property you actually mean.

Cues: `every engineer knows` · `Taught in every first-year biochemistry course` · `a brave architecture` · `an honest abstraction` · `the assumption is dishonest`

Before: Taught in every first-year biochemistry course.

After: Taught in introductory biochemistry.

Do not flag: A universal that is true and checkable stays: 'every EU member state has ratified it' is a fact with a register behind it. Mathematics, logic and law quantify universally by nature. Rhetorical 'we all know' in a speech is a device. Flag when the writer plainly cannot have checked the scope they claim.

### Descriptive title treated as a named thing `list-title-as-entity`

Severity: **context** · Scope: universal

The opening sentence defines a working or descriptive title as though it were a real-world entity: 'X refers to', 'X is the chronological list of', 'The "List of ..." is a curated compilation of'. The article becomes about its own title rather than its subject. Introduce the subject directly instead. The mechanism carries to any CMS where the title is a separate field from the body, in any language.

Cues: `is a curated compilation of` · `is the chronological list of` · `The "List of ..." is` · `refers to the collection of`

Before: The "List of songs about Mexico" is a curated compilation of musical works that reference Mexico.

After: Songs about Mexico range from corridos of the revolution to Ry Cooder's Chavez Ravine.

Do not flag: Style guides do allow a descriptive title at the start of a lead when it reads naturally, and 'refers to' is correct when the article really is about a term or a usage ('Gaslighting refers to a pattern of manipulation'). Dictionaries and glossaries define words for a living. The mechanism carries to any CMS where the title is a separate field from the body.

### Mixed or subtly off metaphor `off-metaphor`

Severity: **context** · Scope: universal

Images in the right semantic ballpark with the wrong physics: figures that fall apart the moment you picture them, or two incompatible figures welded into one sentence. The model reaches for the associated word rather than the working image. Picture the metaphor literally; if the picture is impossible or silly, rebuild it from one source domain.

Before: The algorithm whispered through the circuits, a river of logic that bloomed in the garden of her mind.

After: The algorithm ran the way water finds a crack: it took the cheapest path and widened it.

Do not flag: Deliberate catachresis and surrealism break physics on purpose, and comic writing mixes metaphors for the joke. Idioms that are technically mixed have often lexicalised ('nip it in the bud'). AI editing tools flag strong human metaphors as confusing because those resist categorical mapping, so a strange image alone is not evidence. Judge whether the image does work in the sentence.

### Source-count and consensus inflation `source-count-inflation`

Severity: **context** · Scope: universal

Sources are cited, but their number or breadth is overstated: one person's view is presented as widely held, plural 'reviewers', 'scholars' or 'publications' stand for a single cited name, 'several sources' appears where two are listed, and 'such as' implies a longer list the sources give no sign exists. Match the plural to the citation count, or name the one source you have.

Cues: `several publications have cited` · `several sources reported` · `publications such as` · `widely interpreted as` · `a widely held view` · `according to Indian sources`

Before: Several publications have cited the device as a STEM platform.

After: The Toy Insider called the device a STEM platform (March 2024).

Do not flag: Check the citation count before flagging: 'several publications' with six footnotes is accurate. 'such as' is legitimate when the list really is a sample and the source says so. A genuinely broad consensus, with a survey or meta-analysis behind it, may be described as widely held.

### Sudden polish above the writer's baseline `sudden-polish-jump`

Severity: **context** · Scope: universal

Diction and syntax leap above the writer's demonstrated level inside one piece or between consecutive pieces: clause structures, vocabulary and punctuation that no earlier work by this author shows. Requires a prior corpus to read against, and points at the boundary between what the person wrote and what a tool produced. The vocabulary-level form is the same tell measured on words alone: register-elevated diction (ubiquitous, paradigm, juxtapose) appearing out of proportion to the surrounding prose or to the writer's own history.

Cues: `ubiquitous` · `paradigm` · `juxtapose`

Before: we got the thing working, and the paradigm is now ubiquitous across our juxtaposed services

After: we got it working, and every service uses it now

Do not flag: People improve, edit, and get help from copy-editors, Grammarly, autocorrect and friends; cyborg writing is not fraud. Teachers in controlled studies flagged the better-written essays as AI, which is exactly the bias this pattern invites. Never use it alone or as an accusation, and treat register change between an email and an essay as normal. Requires a baseline: an academic or a writer with a large vocabulary uses those words natively, and a piece written for a specialist audience may legitimately sit at that register throughout. No regex, because the pattern is a comparison between the text and a reference sample rather than a matchable string. The elevated words also appear in the always-flag lexicon; count once. Ask the writer about the shift and compare against three earlier pieces before drawing any conclusion.

### Estimated range standing in for a measurement `vague-numeric-range`

Severity: **context** · Scope: universal

A numeric range is given where a single observed number would exist if the writer had done the thing: 'takes 5 to 10 minutes', 'between 20 and 30 requests'. The range advertises that the figure was guessed. State the number you measured, or say that you did not measure it.

Cues: `5 to 10 minutes` · `X to Y minutes` · `between X and Y`

Before: Setup takes 5 to 10 minutes.

After: Setup took 7 minutes on a clean machine.

Do not flag: A range from genuine, documented variance is honest and often more truthful than a single number: measurement spreads, confidence intervals, published tolerances, cooking times that depend on the oven, and forecasts. Regulatory and safety text specifies ranges deliberately. The tell is a round range where one measurement would exist and none was taken.

## Machine residue

### Text that stops mid-sentence `abrupt-cutoff`

Severity: **always** · Scope: universal

The piece ends in the middle of a sentence or a section because generation hit a token limit and nobody continued it, or because the copy was truncated: 'Final important tip: The ~~~~ at the very end is Wikipedia markup that automatically'. Detect a final sentence with no terminal punctuation, ending on a function word or an auxiliary. Finish the sentence or cut back to the last complete one.

Before: The ~~~~ at the very end is Wikipedia markup that automatically

After: Four tildes at the end sign the post with your username and a timestamp.

Do not flag: Deliberate aposiopesis in fiction or quoted speech, a heading as the last line, a table or code block at the end, and a list whose items carry no terminal punctuation are all normal. A malformed local copy-paste and a partial copy from another document produce the same shape, so this shows the text is unfinished and says nothing about who wrote it.

### Restating the question before answering `acknowledgment-loop`

Severity: **always** · Scope: universal

The text opens by paraphrasing the request back to the person who made it: 'To answer your question...', 'You're asking about...', 'The question of whether...', 'That's a great question. The...', or the Korean 'to summarise what you asked'. In standalone text the reader never asked anything, so the restatement carries no information. Delete the paraphrase and lead with the answer. The recap-flattery variant summarises the other person's own work back at them with praise before the point ('Thanks for all the legwork here, the migration script and the rollback plan you worked through are what made this possible'), repeating specifics the reader already knows.

Cues: `You're asking about` · `The question of whether` · `To answer your question` · `That's a great question. The...`

Before: To answer your question, the cache is invalidated on write.

After: The cache is invalidated on write.

Do not flag: An FAQ, an interview transcript or a Q&A post quotes the question on purpose, and that is the format working. Restating a stakeholder's question in a decision record or a ticket so the record stands alone is context, not filler. 'The question of whether' inside an argument that then answers it is ordinary English and is kept as a cue only, without a regex. A one-line thank-you that adds nothing else is ordinary courtesy, and a review that summarises a change to show what was understood is doing work.

### AI-tool tracking parameter on a URL `ai-url-tracking-parameter`

Severity: **always** · Scope: universal

A query parameter that an AI tool appends to the links it writes: 'utm_source=chatgpt.com', 'utm_source=openai', 'utm_source=copilot.com', 'utm_source=claude.ai', 'utm_source=perplexity.ai', 'referrer=grok.com'. The parameter is the signature whatever the surrounding text says. Strip the AI referrer from the URL and leave the rest of the query string alone.

Cues: `utm_source=chatgpt.com` · `utm_source=copilot.com` · `utm_source=openai` · `utm_source=claude.ai` · `utm_source=perplexity.ai` · `referrer=grok.com`

Before: https://www.theguardian.com/sport/2025/feb/11/sam-burgess-interview?utm_source=chatgpt.com

After: https://www.theguardian.com/sport/2025/feb/11/sam-burgess-interview

Do not flag: A functional parameter (?page=2, ?v=4) and a campaign parameter the destination set itself (utm_source=newsletter) are evidence of nothing; keep the link and keep those. The parameter proves a chat tool produced the link, and not that it wrote the prose: people use AI to find sources for text they wrote themselves, which the edit history often shows. Google has occasionally indexed URLs that already carried the parameter.

### The brief's vocabulary and the destination named inside the deliverable `brief-vocabulary-and-destination-naming`

Severity: **always** · Scope: universal

The output echoes the wording of the criteria it was asked to satisfy, or names the venue it was written for, from inside the text. Sub-forms: guideline vocabulary collapsed into the product ('These sources provide significant, substantial, secondary coverage, not trivial mentions or press releases'); the destination named with a possessive and a rule noun ('adheres to Wikipedia's guidelines on verifiability and neutrality', 'the Animal Cruelty Controversy section of Foshan's Wikipedia page'); rule shortcodes glossed for the reader ('Submit via WP:AFC (Articles for Creation)'). Somebody writing in place does not spell out where they are or which rulebook they read. Cut the frame; the text already sits where it sits. The rubric form is the same move in schoolwork and grant writing: the prompt's checklist reappears as the piece's structure and vocabulary, showing the generator was handed the criteria and optimised against them instead of doing the work.

Cues: `independent coverage` · `significant, substantial, secondary coverage` · `not trivial mentions or press releases` · `meeting both WP:BIOSIG and WP:SIGCOV` · `verifiable coverage` · `Wikipedia's guidelines on verifiability and neutrality` · `adheres to Wikipedia's` · `Foshan's Wikipedia page` · `is Wikipedia markup that` · `Submit via WP:AFC (Articles for Creation)` · `Post to WP:COIN (Conflict of Interest Noticeboard)` · `Before creating a real Wikipedia page`

Before: These sources provide significant, substantial, secondary coverage, not trivial mentions or press releases.

After: (deleted from the article; the sources are cited where they support a sentence)

Do not flag: A discussion about whether a subject qualifies is exactly where guideline vocabulary belongs, and citing one rule with a link in a review or a change note is normal; the tell is that vocabulary inside the deliverable. Documentation that names its own platform because the platform is the subject is fine, as is a style guide quoting its own criteria. The Wikipedia instances are the reported case, and the mechanism transfers to any brief, so a blog post that says 'for this blog' or a PR that recites the contributing guidelines is the same move. Students are taught to signpost against the rubric, and grant applications and tender responses are required to mirror the criteria section by section; flag when the criteria vocabulary appears in place of the content it was meant to measure. 'Independent coverage' is two words of ordinary editorial English that any sourcing review will use correctly, so it is kept as a cue with no regex behind it.

### Zero-width and homoglyph bypass characters `bypass-trick-characters`

Severity: **always** · Scope: universal

Invisible or lookalike characters inserted to defeat AI detectors: zero-width space, non-joiner, joiner, word joiner and byte-order mark (U+200B, U+200C, U+200D, U+2060, U+FEFF), and Cyrillic or Greek letters swapped in for Latin lookalikes (а е о р с х у к м н в т, ο Ο α Α ρ Ρ). Their presence means the text went through a humanizer or prompt-injection bypass tool. Strip the characters and retype the affected words from your own keyboard.

Cues: `U+200B ZWSP` · `U+200C ZWNJ` · `U+200D ZWJ` · `U+FEFF BOM` · `U+2060 word joiner`

Before: dеlve (the e is Cyrillic U+0435, inside an otherwise Latin word)

After: delve, retyped from your own keyboard

Do not flag: A single stray zero-width character or a byte-order mark can come from Word, Notion, a CMS export or a file's own encoding, which is why the detector wants two or more before it counts; one ZWSP should never flip a verdict on its own. Genuine Cyrillic or Greek text, transliteration tables and linguistics examples contain those letters legitimately, and so does any multilingual document; the tell is a Cyrillic letter sitting inside an otherwise Latin word.

### Chatbot opener, preamble and helper self-reference `chatbot-opener`

Severity: **always** · Scope: universal

The assistant's framing before the content survives into the finished text. Sub-forms: a one-word acknowledgement ('Certainly!', 'Of course!', 'Absolutely!', 'Great question!', 'You're absolutely right!'); a lead-in that announces the deliverable ('Here is an overview of...', 'here's a professional encyclopedia-style draft:'); a preamble caveat about what the model can and cannot do, pasted along with the content it introduces; and first-person helper register in the body ('I'd be happy to help', 'Let me explain', 'I can help draft a...'). The article-framing variant ('In this article, we will explore...', 'Let's dive in!') is the same move dressed as an introduction. Delete the frame and open on the first real fact.

Cues: `Of course!` · `Certainly!` · `Absolutely!` · `Great question!` · `Excellent point!` · `You're absolutely right!` · `here is a...` · `Here is an overview of` · `here's a...` · `I can help draft a` · `but I should be clear:` · `Based only on the information you've shared with me, here's a` · `here's a professional encyclopedia-style draft:` · `I'd be happy to help` · `Let me explain` · `I think it's worth considering…` · `In this article, we will explore` · `Let's dive in!` (+2)

Before: Certainly! Here is an overview of the French Revolution. The revolution began in 1789 after years of financial crisis.

After: The French Revolution began in 1789, after years of financial crisis.

Do not flag: 'Of course' inside an argument ('Of course the number moved, the sample doubled') is ordinary emphasis, and 'certainly' as an adverb is fine; the tell is the standalone acknowledgement that opens the text. A real introduction that says what the piece covers and then covers it is not a chatbot lead-in, the tell is a frame that addresses the requester or presents the text as a deliverable. Letter-style openings on actual correspondence predate chatbots by centuries and stay. Similar phrasing woven into the body, rather than sitting in front of it, is left alone.

### Chat-tool citation markup left in the text `citation-markup-leak`

Severity: **always** · Scope: universal

Internal citation tokens from a chat interface that survive copy-paste, in place of real references. Known forms: ChatGPT's ':contentReference[oaicite:N]{index=N}', '[oai_citation:N‡domain]', 'citeturn0search0' / 'turn0news' / 'turn0file' and the image run 'iturn0image0turn0image1', the bare trailing numeral left when the private-use wrappers are stripped ('...adaptation.5'), the per-sentence '^[sentence] ({"attribution":{"attributableIndex":"1009-1"}})' payload, and the source-count chips flattened to text ('Wikipedia+1', 'IT Governance+3ISO+3ISO+3'); Gemini's '[cite: 3, 12, 13]' and '[span_1] (start_span)' / '(end_span)' grounding markers; Grok's '<grok-card data-id=... data-type="citation_card">' and '[] (grok_render_citation_card_json={"cardIds":[...]})'; DeepSeek's lenticular dagger form '【85†L261-269】'; Perplexity's '[attached_file:1]' / '[web:1]' and 'ppl-ai-file-upload' S3 URLs; plus flattened chips that glue a source domain onto the last word of a sentence, and the '↩' jump-back arrow copied out of a footnote list. Delete every token and replace anything that was meant to be a citation with a real reference.

Cues: `citeturn0search0` · `turn0search1` · `turn0search2` · `citeturn0news0` · `citeturn1file0` · `cite<generated-reference-identifier>` · `<ref name="0search12">` · `iturn0image0turn0image1turn0image4turn0image5` · `:contentReference[oaicite:0]{index=0}` · `[oai_citation:0‡` · `({"attribution":{"attributableIndex":` · `Wikipedia+1` · `IT Governance+3ISO+3ISO+3` · `Ignyte+3Microsoft Learn+3Google Cloud+3` · `Example+1` · `[cite: 1]` · `[cite: 3, 12, 13]` · `[cite: 17]` (+20)

Before: Ibbetson's Panjab Castes classifies Sial as Rajputs :contentReference[oaicite:20]{index=20}.

After: Ibbetson's Panjab Castes classifies Sial as Rajputs (Ibbetson 1883, p. 143).

Do not flag: A real citation, footnote or reference marker produced by the destination's own system stays. Genuine footnote superscripts carry markup, so a numeral that is marked up is a footnote; only a bare digit glued to a full stop, in a run that climbs through the document, is the stripped artifact, and the same goes for a domain glued to a word: both sub-forms want a second instance before they are safe to call. A URL that legitimately contains 'turn' or a data field named 'web:1' is not a token. The token proves a specific tool touched the text; it does not by itself prove the prose was generated, since people also use chatbots only to find sources. An abbreviated cross-reference such as Fig.2 or Vol.3 is a numbered reference, and the stripped citation artifact sits after a whole word, which is why the pattern wants four letters and skips the abbreviation set. The ↩ jump-back arrow is what GitHub Flavored Markdown, pandoc and Obsidian render at the end of a footnote, so a rendered footnote section copied out of any of them carries it honestly; it counts when it turns up beside another leaked token or with no footnote list behind it, and it is kept as a cue with no regex.

### Collaborative closer and offer of further help `collaborative-closer`

Severity: **always** · Scope: universal

The chat sign-off addressed to the requester survives into the text. Sub-forms: the helpfulness closer ('I hope this helps', 'Let me know if you need anything else', 'Feel free to reach out'); the follow-up offer as a question ('Would you like me to...?', 'Want me to give examples?', 'Should I continue?', 'Is there anything else...'); the offer to convert the output into the destination's own format ('Would you like me to turn this into wikitext?'); and usage instructions for the text itself ('You can copy and paste this onto your page and customize it further'). End on the last useful fact and delete the rest.

Cues: `I hope this helps!` · `Let me know if you'd like me to expand on any section` · `Let me know if you need anything else` · `Let me know if you'd like me to go deeper!` · `Please let me know if there's anything else I can help with!` · `Feel free to reach out` · `is there anything else` · `Would you like...` · `Would you like me to` · `Want me to...?` · `Want me to give examples?` · `Should I continue?` · `Would you like a more detailed breakdown?` · `I can guide you step-by-step through that too.` · `Here's a template for your` · `You can copy and paste this` · `customize it further`

Before: The migration runs in two phases. I hope this helps! Let me know if you'd like me to expand on any section.

After: The migration runs in two phases.

Do not flag: A genuine sign-off in real correspondence (an email, a Slack message, a cover letter) is not a leftover; salutations and valedictions predate ChatGPT by centuries. The tell is an offer of further assistance on a surface where nobody is being served: an article, a report, a commit message, a documentation page. A question that advances the argument is fine; the tell is a question offering the writer's further labour. Support and service copy ('reach out if the invoice is wrong') is doing its job.

### Duplicated section or paragraph `content-duplication`

Severity: **always** · Scope: universal

A section or paragraph repeats verbatim or near-verbatim inside the same piece, because the generator lost track of what it had already written: the same section emitted twice word for word, or paragraph 3 restated as paragraph 17 with the wording shuffled. Detect by paragraph hashing or n-gram overlap. Delete the copy, and check first whether one half carries a fact the other lost.

Before: The plant closed in 1998 after the parent group withdrew funding. [...] After the parent group withdrew funding, the plant closed in 1998.

After: The plant closed in 1998 after the parent group withdrew funding.

Do not flag: A deliberate refrain, a summary that restates the lead, a legal notice repeated by requirement, and boilerplate that appears in every section by design are not duplication. Reference material where each entry repeats a stock sentence is the format. The tell is an exact or near-exact repeat that neither position needs, and it is less common in recent output than it was.

### Knowledge-cutoff disclaimer and AI self-identification `cutoff-disclaimer-and-ai-self-identification`

Severity: **always** · Scope: english

The model's own limits stated in the first person and left in the text: a knowledge-cutoff caveat ('As of my last update', 'my training data goes up to', 'I don't have access to real-time data', 'my knowledge is current to ...'), self-identification as a model ('As an AI language model...', 'I am an AI assistant'), and the canned refusal of professional advice ('I cannot provide legal advice, but I can...'). The refusal sub-form usually arrives as a whole declined turn pasted in, apology and offered alternative included. Delete it; where a real date limit applies, name the date and the source.

Cues: `As of my last update` · `as of my knowledge cutoff` · `I don't have access to real-time data` · `based on available information` · `As an AI language model` · `as a large language model` · `I am an AI assistant` · `I cannot provide legal advice` · `I cannot offer medical advice, but I can...` · `my training data only goes up to` · `I'm sorry, but I can't` · `Up to my last training update` · `As of my last knowledge update in January 2022` · `I don't have specific information about the current status or developments`

Before: As of my last update, the council had not published the 2026 budget.

After: The council had not published the 2026 budget as of 4 September 2026 (council minutes, 3 September).

Do not flag: A dated scope statement ('figures are current to March 2026') is honest and stays. A human declining to give legal advice in their own voice, with a reason, is a real disclaimer. Writing about AI models in the third person is subject matter, not self-identification. 'Based on available information' is ordinary in modern business prose, so it is kept as a cue with no regex behind it. Release notes, datasets and reports properly say when their data was pulled; the tell is the writer disclaiming their own reach, not the presence of a date.

### Generator wrapper and speaker label around the deliverable `generation-wrapper-and-speaker-label`

Severity: **always** · Scope: universal

The transport envelope around the answer gets pasted with the payload. Sub-forms: a container directive opening the deliverable, ':::writing{variant="document" id="68427"}' with a random five-digit id, localised as ':::écriture{variante="document"}' and often closed by a bare ':::'; and a transcript speaker label naming the model ('Claude responded:', 'ChatGPT I revised the content to...') followed by the assistant's own commentary about the text it just produced. Delete the wrapper and the commentary and keep the payload.

Cues: `:::writing{variant="document" id=` · `:::écriture{variante="document` · `ChatGPT I revised` · `Claude responded:` · `That last sentence is the killer` · `you're speaking their language and daring them to argue with it`

Before: :::writing{variant="document" id="68427"}
AK7 is a Belgian rapper.

After: AK7 is a Belgian rapper.

Do not flag: Triple-colon container directives are real syntax in MyST, Docusaurus, pandoc and several static-site generators, so on those surfaces they are the format; the tell is the wrapper on a surface with no such syntax, carrying a random numeric id. Quoting a model by name in a piece about models ('ChatGPT said it could not answer') is reporting, and a transcript that is presented as a transcript keeps its speaker labels.

### Instructions and notes to the person publishing the text `instructions-to-the-handler`

Severity: **always** · Scope: universal

Text addressed to whoever will paste, submit or review the document, published inside it. Sub-forms: numbered submission notes ('Submit via WP:AFC, not directly to mainspace', 'Declare COI in the edit summary'), a line telling the handler to remove the note ('Delete this section before submission'), coaching on what to say if a reviewer objects, a checklist of what the subject should have 'before creating a real page', a cover letter arguing the document's merits to a reviewer ('Reviewer note: this draft is neutral and well-sourced ... Thank you for your review'), and editorial suggestions about the document written in its own register ('Including photos of the forge would enrich the article's section on culture', 'a map could be added to orient readers', 'could further engage readers'). Often hidden inside HTML comments, so scan comment blocks as well. None of it is content.

Cues: `Delete this section before submission` · `After pasting the article` · `SUBMISSION NOTES` · `Final important tip:` · `Before creating a real Wikipedia page` · `To have a good chance of acceptance, your` · `This article should be created at` · `If a reviewer questions` · `convert as many items as possible in the citation list into inline references` · `would enrich the article's section` · `could be added to orient readers` · `could be illustrated with an image` · `Several such photographs are available (e.g., on Wikimedia Commons)` · `would also add depth to the article` · `could further engage readers` · `By leveraging these visual aids` · `the expanded article can provide a richer, more immersive picture` · `Reviewer note (for AfC):` (+3)

Before: Delete this section before submission. After pasting the article, convert the citation list into inline references.

After: (deleted; the article starts at its first line)

Do not flag: A style guide, a contributing guide, a runbook or a README is instructions on purpose. An editorial note in something explicitly marked as a draft, or in a review thread, a ticket or a PR description, is doing its job; the tell is process instruction inside the finished artefact, addressed to its handler rather than its reader. Note also that advice of this kind is often wrong on the facts, so removing it loses nothing.

### Markdown leaking into a surface that does not render it `markdown-in-non-markdown-surface`

Severity: **always** · Scope: universal

Markdown syntax lands on a surface with its own markup or none at all (wikitext, plain-text email, a CMS field, a ticket, a code comment): '**bold**', '*italic*', '_italic_', '# Heading', '[text] (url)', fenced code blocks and '---' / '***' / '___' breaks. Chatbots emit Markdown by default because their system prompts ask for it, and copy-to-clipboard keeps it. Sub-forms: the whole deliverable wrapped in a fenced block ('```wikitext'); a link pasted as '[URL] (URL)' with the address duplicated as its own label; hash headings that the destination renders as numbered list items; and list items pasted as literal markers (•, -, –, #, emoji, or explicit '1.') where the surface has its own list syntax, sometimes run together in one paragraph because the copy lost the line breaks.

Cues: `**bold**` · `**...**` · `**Computing & Open Source Technology**` · `*italic*` · `_italic_` · `# Header 1` · `#### Heading` · `## Geography` · `## History` · `## Administration` · `## Population` · `[text] (url)` · `` ```wikitext `` · `` ```markdown `` · `[https://` · `] (https://` · `**Concise edit summary:**`

Before: * 💻 **Computing & Open Source Technology**
* 📚 **Education Systems in South Asia**

After: * Computing and open source technology
* Education systems in South Asia

Do not flag: Markdown on a surface that renders Markdown is correct, and this whole entry is conditioned on the surface. As an authorship signal Markdown alone is weak: developers, researchers and technical writers type asterisks and hashes by habit, Obsidian, GitHub, Reddit, Discord, Slack, Notes and Docs all encourage it, and a newcomer may reasonably assume the surface supports it. The strong signal is Markdown mixed with the destination's own markup, strongest inside a fenced code block. A '---' line in a Markdown file is usually YAML front matter, a hyphen or bullet character in plain text is an ordinary list, and a fenced block quoting code is the point; the bullet sub-form is only a tell where the surface has its own list syntax. Fenced blocks and Markdown links score on every Markdown document, so read this entry's hits together with the surface they were found on.

### Outline plan published instead of the section `outline-plan-left-in-body`

Severity: **always** · Scope: universal

A sentence describing what a section would contain is emitted in place of the content: 'This section would speculate on potential developments and the changing landscape of global energy.' The model's outline survived into the published text. Write the section or delete the heading.

Cues: `This section would speculate on` · `potential developments and the changing landscape`

Before: This section would speculate on potential developments in global energy.

After: The IEA's 2025 outlook puts peak oil demand between 2029 and 2032 under current policies.

Do not flag: 'This section covers X' as a signpost in documentation is meta-signposting at worst, and belongs to another pattern; the tell here is the conditional 'would', describing content that was never written. An outline document, a table of contents or a proposal whose job is to describe planned sections is doing exactly that.

### Reasoning scaffolding and disclosed inference method `reasoning-chain-leak`

Severity: **always** · Scope: english

Chain-of-thought scaffolding published as prose: 'Let me think step by step', 'Breaking this down', 'To approach this systematically', 'Here's my thought process', 'First, let's consider', and numbered reasoning steps that read as an internal monologue rather than an argument for a reader. The first-person disclosure sub-form narrates the model's own inputs and derivation in place of a source ('My analysis is based on available track titles and public song snippets', 'Where lyrics aren't fully accessible, I've inferred common motifs'), which admits the content was inferred. State the conclusion and the evidence; when the disclosure admits inference, cut what it discloses as well.

Cues: `Let me think step by step` · `Breaking this down step by step` · `To approach this systematically` · `Step 1:` · `Here's my thought process` · `First, let's consider` · `Working through this logically` · `My analysis is based on available track titles` · `I've inferred common motifs from` · `Where lyrics aren't fully accessible` · `public song snippets from streaming platforms` · `overall discography themes`

Before: Let me think step by step. First, let's consider the write path. The cache is invalidated on write.

After: The cache is invalidated on write.

Do not flag: A methods section that states how a result was obtained is documentation, and a runbook or tutorial with numbered steps is the format. 'Breaking this down' about an actual cost breakdown is literal, so only the scaffolded forms ('breaking this down step by step', 'breaking this down into its parts') carry a regex and the bare phrase stays a cue. The tell is process narration standing in for the result, or a first-person account of the writer's own guessing published as fact.

### Unfilled placeholder in the body `unfilled-placeholder`

Severity: **always** · Scope: universal

A fill-in-the-blank slot the writer was meant to replace, shipped as-is: bracketed nouns ('[Your Name]', '[Entertainer's Name]', '[Specific Topic]', '[link to source list]'), bracketed instructions ('[Describe the specific section that needs editing and provide clear reasons why]', '[INSERT SOURCE URL]'), parenthesised prompts ('(Add your channel URL here)', '(If available)') and template variables ('{client_name}'). Near-definitive evidence of pasted, unedited boilerplate. Fill in the real value or delete the sentence.

Cues: `[Your Name]` · `[INSERT SOURCE URL]` · `[Describe the specific section]` · `[Specific Topic]` · `[Language, e.g., non-English]` · `[link to the revised article]` · `[link to source list]` · `[Entertainer's Name]` · `(Add your channel URL here)` · `(If available)` · `Hi {client_name},` · `<!-- Add citation if available -->` · `[add ...]` · `[fill in ...]` · `[TODO]`

Before: Best regards, [Your Name] and Chloe

After: Best regards, Chloe Martens

Do not flag: Templates and scaffolds are supposed to carry slots: a preload template, a form, an article-creation boilerplate, a mail-merge draft. The tell is a slot in finished, published text. Bracketed editorial insertions inside a quotation ('[sic]', '[the minister]') and bracketed citation numbers are normal. Code and configuration that use {placeholders} as syntax are not prose, and '(if available)' is ordinary enough in human writing that it is kept as a cue with no regex. Humans forget template slots too, so treat this as a publishing bug rather than proof of authorship.

### Roleplay action markers `roleplay-action-markers`

Severity: **cluster** · Scope: universal

Asterisk-wrapped stage directions from chat roleplay left in prose: '*nods*', '*sighs*', '*sighs and looks away*', '*leans in*'. The inner phrase opens with a stage verb, which is what separates it from ordinary emphasis. Two or more in a document is the threshold, because a single pair of asterisks may be Markdown italics.

Cues: `*nods thoughtfully*` · `*sighs*` · `*nods*` · `*leans in*`

Before: *nods thoughtfully* The migration ran clean.

After: The migration ran clean.

Do not flag: Markdown emphasis around a word that happens to be one of these verbs ('it *looks* fine') is not a stage direction, which is exactly why the threshold is two. Fiction, screenplays and chat fiction use stage directions on purpose. Double-asterisk bold is excluded by the lookarounds.

### Self-certification of compliance `self-certification-of-compliance`

Severity: **cluster** · Scope: english

The text asserts its own neutrality, sourcing or rule-conformance instead of demonstrating it: 'Written to Wikipedia Manual of Style. Neutral tone, sourced throughout.', 'ensure that the content is presented in a neutral tone, supported by reliable sources', 'We remain committed to creating content that aligns with the mission'. The change-note form stacks verbose, unspecific assurances across a range of improvements nobody would bundle ('for clarity and compliance with the Manual of Style', 'corrected promotional wording, improved sourcing and neutrality'). The AI-disclosure form pre-empts the objection ('I understand concerns regarding AI-generated content, and I worked to ensure it adheres to the rules', 'these comments reflect my own thoughts'). Delete the claim and let the text carry it.

Cues: `Written to Wikipedia Manual of Style` · `Neutral tone, sourced throughout` · `We remain committed to creating content that aligns with Wikipedia's mission` · `presented in a neutral tone, supported by reliable sources` · `I understand [the/your] concern(s) [about/regarding] AI-generated` · `I understand (that) my [contributions] may [have been] perceived as` · `to ensure (that) [the content obeys] Wikipedia's [rules]` · `to ensure the article adheres to Wikipedia's` · `reflect my thoughts` · `ensured that... adheres to` · `in compliance with` · `complies with` · `Wikipedia guidelines` · `Wikipedia style` · `Wikipedia standards` · `for clarity and compliance with the Manual of Style` · `corrected promotional wording` · `improved sourcing and neutrality` (+2)

Before: Revised the section for clarity and compliance with the Manual of Style; corrected promotional wording and improved sourcing and neutrality.

After: removed excessive links per MOS:OVERLINK

Do not flag: A human citing one rule, briefly and with a link ('removed excessive links per MOS:OVERLINK'), is normal practice, and a common abbreviation such as 'ce' for copy edit is not a chatbot. A compliance statement a process actually requires (an accessibility statement, a licence header, a declared conflict of interest) is content. The tell is unspecific assurance stacked several deep, covering improvements nobody would bundle in one pass. The move transfers to any venue with a rulebook, so the English wording of the cues is an instance rather than the limit. Templated-change-note covers the neighbouring case, an edit summary written as exhaustive procedural prose; 'for a more neutral tone' is scored there alone so one summary does not report twice. What this entry scores is the assurance of rule-conformance itself, wherever it sits, including in the body or on a talk page.

### Letter register on a surface that is not correspondence `letter-register-on-non-correspondence`

Severity: **context** · Scope: english

Business-letter framing on a ticket, a talk page, a comment, a form or an article: 'Dear Editorial Team,', 'I hope this message finds you well', 'I am writing to request an edit', 'Thank you for your understanding and assistance in this matter', 'Best regards,'. The register is right in an actual letter; the tell is its arrival where nobody writes letters, and it usually travels with unfilled placeholders from the same paste.

Cues: `I hope this message finds you well` · `I trust this message finds you well` · `I am writing to request` · `I am writing to express my deep concern` · `Thank you for your understanding and assistance in this matter` · `Best regards,` · `Dear Wikipedia Editorial Team` · `We hope to resubmit our work once these changes have been made`

Before: Dear Wikipedia Editorial Team, I hope this message finds you well. I am writing to request an edit to the entry.

After: The second paragraph gives the wrong founding year: the charter is dated 1924, not 1932.

Do not flag: In an actual email, cover letter or formal complaint this is the correct register and predates chatbots by centuries. Judge by surface: a talk page, an issue, a code comment, a commit message, an article. Formality alone is not a tell, and a non-native speaker leaning on a letter template is not a chatbot. A first contact with a stranger may reasonably borrow the register anywhere.

### Provenance signals outside the text `out-of-text-provenance-signal`

Severity: **context** · Scope: universal

Evidence about how the text arrived rather than how it reads: the whole document appearing as a single paste event in the editor's version history, and an author's sudden shift to flawless or formal prose against their own baseline, especially where that baseline predates late 2022. Process evidence of this kind is more defensible than a detector score, and it is never on its own a reason to change a sentence.

Before: A 2,000-word section arrives in one paste, from an account whose other edits are two-line notes.

After: (no text edit; ask the author how the section was written)

Do not flag: A single paste is often a draft written elsewhere, in a local editor, a notes app or another document. Writers code-switch to a formal register in some venues, and long-term AI users drift in parallel with the models, so a gradual change proves nothing; only a dramatic and otherwise unexplainable shift counts. Consistency with pre-2023 habits, the same boldface or the same list style, argues against AI. Never treat this as a defect in the prose. Permissions-gaming carries the cross-document twin of this signal, many benign rewrites across unrelated pages in quick succession, where the volume and the spread rather than any sentence are what shows.
