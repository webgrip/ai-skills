export const meta = {
  name: 'ai-tells-consolidate-en',
  description: 'Extract every AI-writing pattern from 5 skill repos and 6 English lists, merge per category, verify against human control text, synthesize methodology',
  phases: [
    { title: 'Extract', detail: 'one reader per source, structured inventory' },
    { title: 'Merge', detail: 'one merger per category, dedup across sources' },
        { title: 'Consolidate', detail: 'cross-category dedup into catalog-en.json' },
    { title: 'Method', detail: 'workflow, gates, register, voice, false positives' },
  ],
}

const S = '/Users/ryangrippeling/projects/webgrip/webgrip-ai-skills/scripts/humanize'
const CATS = ['vocabulary', 'syntax', 'rhetoric', 'structure', 'punctuation-format', 'content', 'artifacts', 'translationese']

const SOURCES = [
  { id: 'humanizer', files: [`${S}/repos/humanizer/SKILL.md`, `${S}/repos/humanizer/README.md`], hint: 'blader/humanizer Claude skill, 35 Wikipedia-derived patterns plus voice matching. The README carries install and category summaries; SKILL.md is the rulebook.' },
  { id: 'no-ai-slop', files: [`${S}/repos/no-ai-slop/skills/no-ai-slop/SKILL.md`, `${S}/repos/no-ai-slop/skills/no-ai-slop/eval.md`, `${S}/repos/no-ai-slop/README.md`], hint: 'petergyang/no-ai-slop skill, 20+ patterns, voice preservation, detect-only mode.' },
  { id: 'avoid-ai-writing-skill-a', files: [`${S}/repos/avoid-ai-writing/SKILL.md`], range: [1, 460], hint: 'conorbronsdon/avoid-ai-writing SKILL.md first half: what it is, modes, the start of the remove-or-fix rulebook (lines 69 onward are the patterns).' },
  { id: 'avoid-ai-writing-skill-b', files: [`${S}/repos/avoid-ai-writing/SKILL.md`], range: [440, 872], hint: 'conorbronsdon/avoid-ai-writing SKILL.md second half: rest of the rulebook, severity tiers (line 638), self-reference escape hatch, context profiles (688), voice profiles (755), house style, output format, tone calibration.' },
  { id: 'avoid-ai-writing-detector', files: [`${S}/repos/avoid-ai-writing/detector/CATEGORIES.md`, `${S}/repos/avoid-ai-writing/detector/patterns.js`, `${S}/repos/avoid-ai-writing/detector/README.md`], hint: 'The deterministic regex detector behind avoid-ai-writing. patterns.js is 2495 lines: read CATEGORIES.md first, then walk patterns.js in 300-line chunks and extract every pattern id, its category, severity, the regex family (quote the regex verbatim), and the human-readable rationale where present.' },
  { id: 'im-not-ai-taxonomy', files: [`${S}/repos/im-not-ai/docs/en/taxonomy.md`, `${S}/repos/im-not-ai/docs/en/quick-rules.en.md`, `${S}/repos/im-not-ai/README.en.md`], hint: 'epoko77-ai/im-not-ai (Korean humanizer, 5k stars). English docs of its 73-tell taxonomy. Separate the language-universal tells from the Korean-only ones; the translationese layer (English-shaped constructions in another language) matters for a Dutch adaptation later, so capture its structure carefully.' },
  { id: 'im-not-ai-method', files: [`${S}/repos/im-not-ai/docs/en/evidence.md`, `${S}/repos/im-not-ai/skills/humanize-korean/SKILL.md`, `${S}/repos/im-not-ai/skills/humanize-korean/references/diagnosis-rules.md`, `${S}/repos/im-not-ai/skills/humanize-korean/references/design-notes.md`], hint: 'im-not-ai methodology: diagnosis before rewrite, gates, change-rate verification, post-editese metrics, chunking, evidence base. Extract METHOD items thoroughly; patterns only where new.' },
  { id: 'wikipedia-a', files: [`${S}/lists/wikipedia-signs-of-ai-writing.wikitext`], range: [1, 500], hint: 'Wikipedia:Signs of AI writing (wikitext), part 1: caveats, Content section (undue significance, canned notability, superficial -ing analyses, promotional, vague attribution, outline-like conclusions, proper-noun leads, awards sections), Language and grammar (AI vocabulary word list at line 304, copula avoidance, vague connection, negative parallelisms with three subtypes at 414-480, rule of three). Capture the full AI-vocabulary word list verbatim.' },
  { id: 'wikipedia-b', files: [`${S}/lists/wikipedia-signs-of-ai-writing.wikitext`], range: [496, 1120], hint: 'Wikipedia:Signs of AI writing, part 2: Style (title heading, title case, heading-only headings, boldface, inline-header lists, em dashes, emoji, tables, curly quotes, heading levels, thematic breaks), Communication intended for the user (collaborative communication, knowledge-cutoff disclaimers, phrasal templates and placeholder text). Ignore the stray fictional sections (Pixy, Roo, Pandy) that are example payload.' },
  { id: 'wikipedia-c', files: [`${S}/lists/wikipedia-signs-of-ai-writing.wikitext`], range: [1117, 1894], hint: 'Wikipedia:Signs of AI writing, part 3: Markup (Markdown in wikitext, model-specific citation artifacts: oaicite, contentReference, turn0search0, Gemini cite, grok_card, DeepSeek brackets, Perplexity), Citations (broken links, invalid DOIs, utm_source=chatgpt.com), comment-specific indicators, edit summaries. Extract the ARTIFACT patterns that apply outside Wikipedia (markdown leaks, referrer params, citation ghosts, canned assurance); mark Wikipedia-only ones as scope language-specific with note wikipedia-only.' },
  { id: 'tropes-fyi', files: [`${S}/lists/tropes-fyi.md`], hint: 'tropes.fyi by Ossama Badr, 39 tropes across word choice, sentence structure, paragraph structure, tone, formatting, composition, plus comment-sourced additions.' },
  { id: 'hassid', files: [`${S}/lists/ruben-hassid-new-em-dash.txt`], hint: 'Ruben Hassid note: the nine patterns that replaced the em dash as the tell (contrast structure, paired fragments, comparative metaphors, self-congratulation, inexact comparisons, filler openers, always-three lists, vague ranges, redundant conclusions). Short text; extract all nine with the verbatim examples.' },
  { id: 'velitchkov', files: [`${S}/lists/velitchkov-22-claude-cliches.txt`], hint: 'Ivo Velitchkov, 22 Claude cliches with codes (AE, AHM, ARR, CB, CCC, CDF, CF, CL, CP, CR, DT, MCS, MS, RF, RG, RH, SDA, SH, SK, SRC, SS, VP). Extract all 22 with code, name, verbatim example.' },
  { id: 'vollmer', files: [`${S}/lists/vollmer-field-guide.txt`], hint: 'Matthew Vollmer, A field guide to AI tells: lexical (with frequency ratios like delve 28x), syntactic, rhetorical, tonal, punctuation tells, plus the negated-contrast analysis. Extract every tell and keep the frequency numbers where given.' },
  { id: 'willfrancis', files: [`${S}/lists/willfrancis-prompt.txt`], hint: 'Will Francis, custom-instructions prompt for Claude: banned words, banned phrases, structure rules, style rules, and the argument that structural rules outperform word lists. Extract the banned lists verbatim and the methodology claims.' },
  { id: 'goedecke', files: [`${S}/lists/goedecke-em-dashes.txt`], hint: 'Sean Goedecke on why models overuse em dashes and why bare prohibition fails. Mostly methodology; extract the substitution advice and any pattern mentioned.' },
  { id: 'baseline', files: [`${S}/baseline/house-copy-rule.md`, `${S}/baseline/blog-writer-edit-passes.md`], hint: 'BASELINE: what the house already had. A Dutch memory note with the copy rule (no em dashes, no not-x-but-y, no X-geen-Y slogan openers, colon reveal, tricolon, throat-clearers, aphoristic ender, hollow intensifiers, meta-signposting) and the blog-writer de-AI-ify catalog. Extract every pattern so the merge can mark what was already known. Tag scope universal unless clearly Dutch-only.' },
]

const EXTRACT = {
  type: 'object',
  properties: {
    source: { type: 'string' },
    patterns: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          category: { type: 'string', enum: CATS },
          definition: { type: 'string' },
          cues: { type: 'array', items: { type: 'string' } },
          examples: { type: 'array', items: { type: 'object', properties: { before: { type: 'string' }, after: { type: 'string' } }, required: ['before'] } },
          severity: { type: 'string', enum: ['always', 'cluster', 'context'] },
          scope: { type: 'string', enum: ['universal', 'english', 'language-specific'] },
          notes: { type: 'string' },
        },
        required: ['name', 'category', 'definition', 'cues', 'examples', 'severity', 'scope'],
      },
    },
    methodology: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          topic: { type: 'string', enum: ['workflow', 'gates', 'false-positives', 'register', 'voice', 'facts', 'scoring', 'modes', 'output', 'other'] },
          rule: { type: 'string' },
        },
        required: ['topic', 'rule'],
      },
    },
    coverage_note: { type: 'string' },
  },
  required: ['source', 'patterns', 'methodology', 'coverage_note'],
}

const ENTRY = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    name: { type: 'string' },
    definition: { type: 'string' },
    cues: { type: 'array', items: { type: 'string' } },
    regex: { type: 'array', items: { type: 'string' } },
    examples: { type: 'array', items: { type: 'object', properties: { before: { type: 'string' }, after: { type: 'string' } }, required: ['before', 'after'] } },
    severity: { type: 'string', enum: ['always', 'cluster', 'context'] },
    scope: { type: 'string', enum: ['universal', 'english', 'language-specific'] },
    sources: { type: 'array', items: { type: 'string' } },
    merged_from: { type: 'array', items: { type: 'string' } },
    false_positives: { type: 'string' },
    in_baseline: { type: 'boolean' },
  },
  required: ['id', 'name', 'definition', 'cues', 'regex', 'examples', 'severity', 'scope', 'sources', 'merged_from', 'false_positives', 'in_baseline'],
}

const MERGED = { type: 'object', properties: { category: { type: 'string' }, entries: { type: 'array', items: ENTRY }, note: { type: 'string' } }, required: ['category', 'entries', 'note'] }
const VERIFIED = { type: 'object', properties: { category: { type: 'string' }, entries: { type: 'array', items: ENTRY }, report: { type: 'string' }, added: { type: 'integer' }, regex_dropped: { type: 'integer' } }, required: ['category', 'entries', 'report', 'added', 'regex_dropped'] }
const DEDUP = { type: 'object', properties: { merged: { type: 'integer' }, moved: { type: 'integer' }, total: { type: 'integer' }, per_category: { type: 'object', additionalProperties: { type: 'integer' } }, notes: { type: 'string' } }, required: ['merged', 'moved', 'total', 'notes'] }
const NEW = { type: 'object', properties: { new_count: { type: 'integer' }, known_count: { type: 'integer' }, dropped_from_baseline: { type: 'array', items: { type: 'string' } }, headline_new: { type: 'array', items: { type: 'string' } } }, required: ['new_count', 'known_count', 'dropped_from_baseline', 'headline_new'] }
const CRITIC = { type: 'object', properties: { ok: { type: 'boolean' }, issues: { type: 'array', items: { type: 'string' } }, counts: { type: 'object', additionalProperties: { type: 'integer' } } }, required: ['ok', 'issues'] }
const METHOD = { type: 'object', properties: { sections: { type: 'array', items: { type: 'string' } }, contradictions: { type: 'array', items: { type: 'string' } }, path: { type: 'string' } }, required: ['sections', 'contradictions', 'path'] }

const CAT_GUIDE = `Categories (assign exactly one):
- vocabulary: single words or short stock phrases (delve, tapestry, genuinely, "it's worth noting", "in today's fast-paced world")
- syntax: sentence-level constructions (negative parallelism "not X but Y", tricolon, participle chains, copula avoidance "serves as", false ranges, anaphora, rhetorical self-question, paired fragments "Fast. Simple.")
- rhetoric: argumentative moves and tone (colon reveal, aphoristic ender, false suspense, stakes inflation, self-ranking claims, meta-signposting, reflexive hedging, sycophancy, candor flags "the honest answer", corrective pivot, compliment sandwich)
- structure: paragraph and document shape (uniform paragraph length, listicle-as-prose, fractal summaries, five-paragraph essay, headers as topics, bold-first bullets, inline-header lists, signposted conclusions, "despite challenges" outline endings)
- punctuation-format: em and en dashes, curly quotes, emoji, boldface density, title case, unicode arrows, hyphenation, thematic breaks, heading levels, tables
- content: substance failures (vague attribution "experts say", promotional language, inflated significance/legacy, canned notability, fabricated first-person experience, knowledge-cutoff disclaimers, missing first-hand detail, both-sides padding, invented concept labels)
- artifacts: chatbot leftovers and machine fingerprints (collaborative closers "I hope this helps", "as an AI", markdown leaking into non-markdown surfaces, oaicite/contentReference/turn0search citations, utm_source=chatgpt.com, placeholder text "[insert name]", canned assurance of policy adherence)
- translationese: constructions that only exist because English-shaped text was generated in another language (source-language word order, calqued idioms, English punctuation conventions in the target language, mechanical parallelism carried over). Universal method, language-specific instances.`

function extractPrompt(src) {
  const how = src.range
    ? `Read ONLY lines ${src.range[0]}-${src.range[1]} of ${src.files[0]} with sed -n '${src.range[0]},${src.range[1]}p' in chunks of at most 250 lines (several sed calls). Do not read outside that range; another agent covers the rest.`
    : `Read every file completely: ${src.files.join(' ; ')}. Use sed -n in chunks of at most 250 lines so nothing is skipped.`
  return `You are one extractor in a fan-out that consolidates AI-writing-pattern catalogs into one skill. Your source is "${src.id}". ${src.hint}

${how}

Task: inventory EVERY distinct pattern the source names or implies. Do not summarize, do not skip "obvious" ones, do not merge two distinct patterns into one. For each pattern give:
- name: the source's own name where it has one
- category: ${CAT_GUIDE}
- definition: one or two sentences, in your own words, precise enough that a regex author or a rewriter could act on it
- cues: literal trigger phrases or words, verbatim from the source, as many as the source gives (for word lists: every word)
- examples: the source's before/after examples verbatim where present; if only a "before" exists, give that
- severity: always (never acceptable in target prose), cluster (only a tell when several co-occur or density is high), context (fine in some registers, e.g. formal or academic)
- scope: universal (applies to any language), english (the specific words are English but the mechanism transfers), language-specific (only makes sense in the source's language or on the source's platform)
- notes: false-positive guidance, frequency numbers, severity tier labels, or anything the source adds that the definition does not carry

Also collect methodology as separate items: workflow steps (detect before rewrite, chunking, iterate-to-convergence), gates (fact/number/quote/name protection, change-rate limits), false-positive rules, register or context tolerance profiles, voice matching, scoring schemes, modes (detect/edit/rewrite/write), output formats, and explicit anti-goals (no detector bypass, no fact bending). Each as {topic, rule} with the rule stated as an instruction.

coverage_note: say what you read (line ranges or files), what you deliberately left out and why, and anything in the source you could not classify.

Also write your complete structured result as JSON to ${S}/out/extract-${src.id}.json (same content you return). Return the structured result.`
}

function mergePrompt(cat, raw, baselineNames) {
  return `You merge one category of a consolidated AI-writing-pattern catalog and verify your own work. Category: "${cat}".
${CAT_GUIDE}

Below are every raw pattern in this category extracted from ${SOURCES.length} sources (each carries its source id). Raw entries from the source "baseline" describe what the house ALREADY had; they are input like any other, but any canonical entry that covers a baseline entry gets in_baseline: true.

Baseline pattern names for reference: ${JSON.stringify(baselineNames)}

Produce canonical entries:
- Dedupe by MEANING, not by name. "Negative parallelism", "contrastive binary", "binary contrast", "It's not X, it's Y", "negation pivot" are one entry (sub-forms listed in cues and definition). Keep genuinely distinct patterns separate ("colon reveal" is not "negative parallelism").
- id: stable kebab-case, descriptive (negative-parallelism, colon-reveal, rule-of-three, em-dash-density). No source prefixes.
- definition: the most precise wording, standing alone, 2-4 sentences, naming sub-forms.
- cues: union of literal cues across sources, deduplicated, verbatim. For word lists keep every word.
- regex: Python re patterns (the scanner applies IGNORECASE; write lowercase; \\b word boundaries; tight enough not to fire on ordinary human prose). Only where a literal cue exists; [] for structural patterns. JSON-escaped backslashes.
- examples: 1-3 before/after pairs, short; write a faithful after where a source only had a before. The after must not itself contain any tell (no em dash, no "not X but Y", no tricolon, no hollow intensifier).
- severity, scope: reconcile; stricter reading only when two or more sources back it, else majority.
- sources: every source id that carried it. merged_from: every raw name you folded in (verbatim), so every raw entry is accounted for.
- false_positives: when NOT to flag, folding in every source's notes for this pattern.
- in_baseline: true if any baseline raw entry is covered.

Then verify before returning:
1. Every raw name below has a home (its own entry or a merged_from). Do not drop patterns for being minor.
2. Regex check: write and run a Python script that compiles every regex (re.IGNORECASE) and counts matches per 10,000 words on the human-written control text ${S}/control/en-strunk-elements-of-style.txt and ${S}/control/en-twain-innocents-abroad.txt. Fix or remove any regex that fails to compile. Tighten or remove any regex that fires more than 2 times per 10,000 words on that prose (keep the cue as prose). Each regex must also match at least one of its own cues or the entry's before example.
3. Definitions actionable; severity, scope and false_positives present.

Write the result as JSON to ${S}/out/verified-${cat}.json with shape {category, entries, report, added, regex_dropped} (report: two or three sentences on what over-matched and what you folded) and return it.

RAW ENTRIES:
${JSON.stringify(raw)}`
}

phase('Extract')
log(`extracting ${SOURCES.length} sources`)
const extracted = (await parallel(SOURCES.map(src => () =>
  agent(extractPrompt(src), { label: `extract:${src.id}`, phase: 'Extract', schema: EXTRACT })
))).filter(Boolean)
log(`extracted ${extracted.length}/${SOURCES.length} sources, ${extracted.reduce((n, e) => n + e.patterns.length, 0)} raw patterns, ${extracted.reduce((n, e) => n + e.methodology.length, 0)} methodology items`)
const failed = SOURCES.filter(s => !extracted.some(e => e.source === s.id || (e.source || '').includes(s.id)))
if (failed.length) log(`WARNING extraction returned nothing for: ${failed.map(s => s.id).join(', ')}`)

const rawByCat = Object.fromEntries(CATS.map(c => [c, []]))
for (const e of extracted) {
  for (const p of e.patterns) {
    const cat = CATS.includes(p.category) ? p.category : 'rhetoric'
    rawByCat[cat].push({ ...p, source: e.source })
  }
}
const baselineNames = extracted.filter(e => e.source === 'baseline' || (e.source || '').includes('baseline')).flatMap(e => e.patterns.map(p => p.name))
const allMethod = extracted.flatMap(e => e.methodology.map(m => ({ ...m, source: e.source })))
log(`per category: ${CATS.map(c => `${c}=${rawByCat[c].length}`).join(' ')}`)

phase('Method')
const methodPromise = agent(`Synthesize the METHODOLOGY half of a consolidated AI-writing skill from ${allMethod.length} rules gathered across ${extracted.length} sources (blader/humanizer, petergyang/no-ai-slop, conorbronsdon/avoid-ai-writing and its detector, epoko77-ai/im-not-ai, Wikipedia:Signs of AI writing, tropes.fyi, Ruben Hassid, Ivo Velitchkov, Matthew Vollmer, Will Francis, Sean Goedecke, and the house baseline).

Rules (JSON, each with topic and source):
${JSON.stringify(allMethod)}

Write ${S}/out/methodology.md: a procedure spec an agent can follow, not an essay. Sections, each as imperative bullets with the source ids in brackets where a rule is contested or non-obvious:
1. Modes: detect (report only), edit (minimal surgical), rewrite (full pass), write-fresh (prevent while drafting). What each returns.
2. Workflow: language detection, register detection, read the writer's sample if any, diagnose before touching (cluster/density logic), rewrite by hand never by find-and-replace, iterate to convergence, final self-scan.
3. Gates and protections: numbers, names, dates, quotes, citations, code, URLs, the author's claims; change-rate limits; never add facts; never bend meaning; no detector-bypass tricks; disclosure norms.
4. Register and context tolerance: which patterns are acceptable where (LinkedIn vs technical blog vs docs vs academic vs chat reply vs marketing), as a table if the sources give one.
5. Voice matching: how to read a sample and what to copy (sentence length distribution, punctuation habits, word level, humor, first person), and what NOT to flatten.
6. False positives: the universal do-not-flag list.
7. Scoring: any scheme worth keeping (density per N words, 0-100, tiers P0-P3), pick one recommended and note the others.
8. Substitution rule: give the model a replacement, not a bare prohibition (comma/period for em dash, write the contrast out, etc.), with the evidence for why prohibition alone fails.
9. Contradictions between sources and the resolution you recommend (e.g. zero em dashes vs allow if the sample uses them; word lists vs structure-first).
Keep it under 250 lines. No dates, no history, no praise of the sources.

Return: the section titles you wrote, the contradictions you found, and the path.`, { label: 'method:synthesize', phase: 'Method', schema: METHOD })

phase('Merge')
const verified = (await parallel(
  CATS.filter(c => rawByCat[c].length > 0).map(cat => () =>
    agent(mergePrompt(cat, rawByCat[cat], baselineNames), { label: `merge:${cat}`, phase: 'Merge', schema: VERIFIED }))
)).filter(Boolean)
log(`merged ${verified.length} categories, ${verified.reduce((n, v) => n + v.entries.length, 0)} entries, -${verified.reduce((n, v) => n + v.regex_dropped, 0)} regexes dropped`)

phase('Consolidate')
const slim = verified.flatMap(v => v.entries.map(e => ({ id: e.id, category: v.category, name: e.name, definition: e.definition, severity: e.severity, scope: e.scope, in_baseline: e.in_baseline })))
const dedup = await agent(`Cross-category consolidation of an AI-writing-pattern catalog. Eight category files were merged and verified independently, so the same pattern may exist in two categories under different ids, and some entries sit in the wrong category.

Slim list of every entry (id, category, name, definition, severity, scope, in_baseline):
${JSON.stringify(slim)}

Full entries live in ${S}/out/verified-<category>.json.

Do:
1. Find duplicates across categories (same mechanism, different id). For each pair choose the survivor (the richer entry), union the loser's cues, regex, examples, sources, merged_from into it, and drop the loser.
2. Find misfiled entries and move them to the right category (${CATS.join(', ')}).
3. Make ids unique and consistent (kebab-case, no source prefixes).
4. Write ${S}/out/catalog-en.json with shape {"categories": {"<category>": [entries...]}, "count": N}. Entries keep the full shape from the verified files.
5. Also write ${S}/out/catalog-en-index.md: one line per entry "- <id> (<category>, <severity>): <name>" grouped by category, for humans.

Return counts (merged pairs, moved entries, total entries, per_category) and short notes on the judgment calls.`, { label: 'consolidate:catalog', phase: 'Consolidate', schema: DEDUP })
log(dedup ? `catalog: ${dedup.total} entries after ${dedup.merged} merges and ${dedup.moved} moves` : 'WARNING consolidation returned null')

const method = await methodPromise

return {
  sources_extracted: extracted.length,
  raw_patterns: extracted.reduce((n, e) => n + e.patterns.length, 0),
  per_category_raw: Object.fromEntries(CATS.map(c => [c, rawByCat[c].length])),
  catalog: dedup,
  method,
  coverage_notes: extracted.map(e => `${e.source}: ${e.coverage_note}`),
}