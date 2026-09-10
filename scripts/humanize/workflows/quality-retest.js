export const meta = {
  name: 'humanize-quality-retest',
  description: 'Blind head-to-head of the humanize skill against a plain agent on the same request, English and Dutch, two comparisons (rewrite, edit), rhythm loss measured by the scanner',
  phases: [
    { title: 'Run', detail: 'same request to both arms, skill arm picks its own mode' },
    { title: 'Measure', detail: 'scan.py on every output and every original' },
    { title: 'Grade', detail: 'blind native-reader grade, each pair graded in both positions' },
  ],
}

const SKILL = '/Users/ryangrippeling/projects/webgrip/webgrip-ai-skills/skills/humanize'
const SCRATCH = '/private/tmp/claude-501/-Users-ryangrippeling-projects-webgrip-twente-dev/f4fbfffd-c338-4a42-8df7-99e8c28b0f52/scratchpad/deai/quality'
const seed = Number((args && args.seed) || 0)

const COMPARISONS = [
  {
    key: 'rewrite',
    expect_mode: 'rewrite',
    request: {
      en: 'Rewrite this so it reads like a person wrote it. Keep every fact.',
      nl: 'Herschrijf dit zodat het klinkt alsof een mens het schreef. Houd elk feit.',
    },
  },
  {
    key: 'edit',
    expect_mode: 'edit',
    request: {
      en: 'This is my draft. Fix only what reads as AI-written and leave everything else exactly as I wrote it.',
      nl: 'Dit is mijn concept. Haal alleen weg wat als AI leest en laat de rest precies zoals ik het schreef.',
    },
  },
]

const CASES = [
  {
    id: 'en-linkedin-post', lang: 'en', first_person: true,
    text: `In today's rapidly evolving tech landscape, we're thrilled to announce something special. It's not just a product launch — it's a paradigm shift.\n\nAfter 14 months of relentless work, our team has built something that fundamentally reimagines how developers approach observability. By leveraging cutting-edge AI, we've reduced mean time to resolution by 47%, cut alert noise by two thirds, and empowered engineers to focus on what truly matters: building.\n\nExperts agree this represents a pivotal moment for the industry. Studies show that teams adopting intelligent observability see significant improvements across the board.\n\nDespite the challenges ahead, the future looks incredibly bright. Let's build it together.\n\nWhat's your take? Drop a comment below! 🚀\n\n#Observability #AI #DevOps #Innovation #FutureOfWork #Engineering`,
    facts: ['14 months', '47%', 'two thirds'],
  },
  {
    id: 'en-technical-readme', lang: 'en', first_person: false,
    text: `## Introduction\n\nIn the ever-evolving world of container orchestration, managing secrets isn't just a technical challenge — it's a trust problem.\n\nThis tool serves as a bridge between your vault and your cluster. It stands as a testament to the principle that secrets should never live in Git.\n\n**Key Features:**\n\n- **Secure:** Secrets never touch disk unencrypted.\n- **Fast:** Sync completes in under 200ms.\n- **Simple:** One YAML file, zero dependencies.\n\nIt's worth noting that the tool supports both HashiCorp Vault and OpenBao. Whether you're a startup or an enterprise, the workflow remains the same.\n\n## Conclusion\n\nIn conclusion, secret management doesn't have to be painful. Despite its challenges, the ecosystem continues to evolve, paving the way for a more secure future.`,
    facts: ['200ms', 'HashiCorp Vault', 'OpenBao', 'One YAML file'],
  },
  {
    id: 'en-incident-writeup', lang: 'en', first_person: true,
    text: `Our recent outage wasn't just downtime — it was a learning opportunity.\n\nOn March 3rd, a cascading failure took down the payments API for 43 minutes. The root cause? A retry storm. Our retries didn't just fail to help; they actively made things worse.\n\nHere's the thing: resilience isn't about preventing failure. It's about failing gracefully.\n\nWe've since implemented exponential backoff with jitter, reduced our retry budget from 3 to 1, and established a circuit breaker at the gateway. The results speak for themselves.\n\nWhat nobody tells you about incident response is that the technical fix is the easy part.`,
    facts: ['March 3rd', '43 minutes', '3 to 1'],
  },
  {
    id: 'nl-linkedin-post', lang: 'nl', first_person: true,
    text: `In het snel veranderende landschap van vandaag zijn we verheugd om iets bijzonders aan te kondigen. Het is niet zomaar een release — het is een nieuwe manier van werken. Na 8 maanden bouwen hebben we de doorlooptijd van deploys teruggebracht van 40 naar 6 minuten, en de teams in Enschede, Hengelo, en Almelo werken er sinds maart mee. Experts zijn het erover eens dat dit een cruciale stap is. Wat vind jij? Laat het weten in de reacties! 🚀`,
    facts: ['8 maanden', '40 naar 6 minuten', 'Enschede', 'Hengelo', 'Almelo', 'maart'],
  },
  {
    id: 'nl-meetup-description', lang: 'nl', first_person: true,
    text: `Eén avond, geen verkooppraatje.\n\nLaten we erin duiken: op donderdag 12 februari om 19:00 openen we de deuren van Code14 aan de Hogepad 81 in Rijssen voor een avond vol inspiratie, kennis, en verbinding. Twee talks van ontwikkelaars die het werk zelf deden — geen keynotes, geen productdemo's.\n\nHet is belangrijk om te benadrukken dat de avond gratis is en dat er plek is voor 35 mensen. Kortom, een avond die je niet wilt missen.\n\nMeld je aan en deel dit met je netwerk!`,
    facts: ['donderdag 12 februari', '19:00', 'Code14', 'Hogepad 81', 'Rijssen', 'twee talks', 'gratis', '35 plekken'],
  },
  {
    id: 'nl-readme-intro', lang: 'nl', first_person: false,
    text: `## Introductie\n\nIn de snel veranderende wereld van containerorkestratie is het beheren van secrets niet zomaar een technische uitdaging — het is een vertrouwenskwestie.\n\nDeze tool dient als brug tussen je vault en je cluster. Het is een testament aan het principe dat secrets nooit in Git horen.\n\n**Belangrijkste kenmerken:**\n\n- **Veilig:** Secrets raken nooit onversleuteld de schijf.\n- **Snel:** Synchronisatie is klaar in onder de 200 ms.\n- **Simpel:** Eén YAML-bestand, geen afhankelijkheden.\n\nHet is belangrijk om op te merken dat de tool zowel HashiCorp Vault als OpenBao ondersteunt. Of je nu een startup of een enterprise bent, de workflow blijft hetzelfde.\n\n## Conclusie\n\nKortom, secretbeheer hoeft niet pijnlijk te zijn. Ondanks de uitdagingen blijft het ecosysteem evolueren en effent het de weg naar een veiligere toekomst.`,
    facts: ['onder de 200 ms', 'HashiCorp Vault', 'OpenBao', 'één YAML-bestand'],
  },
]

const OUTPUT = {
  type: 'object',
  properties: {
    text: { type: 'string' },
    account: { type: 'string' },
    mode_reported: { type: 'string' },
  },
  required: ['text', 'account', 'mode_reported'],
}
const METRICS = {
  type: 'object',
  properties: {
    sentence_length_variation: { type: 'number' },
    em_dashes_per_500_words: { type: 'number' },
    always_hits: { type: 'integer' },
    cluster_hits: { type: 'integer' },
  },
  required: ['sentence_length_variation', 'em_dashes_per_500_words', 'always_hits', 'cluster_hits'],
}
const MEASURED = {
  type: 'object',
  properties: {
    original: METRICS,
    outputs: { type: 'array', items: { type: 'object', properties: { key: { type: 'string' }, metrics: METRICS }, required: ['key', 'metrics'] } },
  },
  required: ['original', 'outputs'],
}
const GRADE = {
  type: 'object',
  properties: {
    facts_kept: { type: 'integer' },
    facts_total: { type: 'integer' },
    facts_invented: { type: 'array', items: { type: 'string' } },
    tells_remaining: { type: 'array', items: { type: 'string' } },
    naturalness: { type: 'integer' },
    first_person_dropped: { type: 'boolean' },
    stance_dropped: { type: 'boolean' },
    better_arm: { type: 'string', enum: ['A', 'B', 'tie'] },
    reasoning: { type: 'string' },
  },
  required: ['facts_kept', 'facts_total', 'facts_invented', 'tells_remaining', 'naturalness', 'first_person_dropped', 'stance_dropped', 'better_arm', 'reasoning'],
}

const GRADER = {
  en: 'You are a careful human editor grading two rewrites of the same text. You do not know which tool produced which; judge only what is on the page.',
  nl: 'Je bent eindredacteur bij een Nederlandse krant. Je leest al twintig jaar kopij van anderen en je hoort meteen of een zin door een Nederlander is geschreven of uit het Engels is gerold. Je hebt een hekel aan ambtelijk Nederlands en aan zinnen die kloppen maar die niemand zo zegt. Je beoordeelt twee herschrijvingen van dezelfde tekst en weet niet welk gereedschap welke maakte; je oordeelt alleen over wat er staat.',
}

const LEAKAGE = [
  /^(Mode|Register|Modus|Patterns?|Patronen|Scan|Changed|Gewijzigd)\s*:/m,
  /`[a-z0-9]+(?:-[a-z0-9]+)+`/,
  /\b\d+\s+(hits?|dashes|treffers|streepjes)\b/i,
  /em dashes\/500w/,
]
const leakageCount = text => LEAKAGE.filter(re => re.test(text)).length

const FLATTEN_RATIO = 0.6
const FLATTEN_FLOOR = 0.30
const flattened = (m, original, grade, c) =>
  m.sentence_length_variation < FLATTEN_RATIO * original.sentence_length_variation
  || m.sentence_length_variation < FLATTEN_FLOOR
  || (c.first_person && grade.first_person_dropped)
  || grade.stance_dropped

function baselinePrompt(c, comparison) {
  return `${comparison.request[c.lang]}\n\n---\n${c.text}\n---\n\nReturn only the text, as the field "text". Leave "account" empty and "mode_reported" empty.`
}

function skillPrompt(c, comparison) {
  return `Read ${SKILL}/SKILL.md and follow it. The user says: "${comparison.request[c.lang]}"\n\n---\n${c.text}\n---\n\nThe catalog is at ${SKILL}/patterns-${c.lang}.md, the method at ${SKILL}/method.md, the scanner at ${SKILL}/scripts/scan.py. Return what the skill's return contract specifies, nothing more. Put the deliverable text in "text" and any account the contract allows in "account", never inside "text". Put the mode you chose in "mode_reported".`
}

phase('Run')
const runs = []
for (const comparison of COMPARISONS) {
  for (const c of CASES) {
    runs.push({ comparison: comparison.key, case: c.id, arm: 'without', job: () =>
      agent(baselinePrompt(c, comparison), { label: `run:${comparison.key}/${c.id}/without`, phase: 'Run', schema: OUTPUT }) })
    runs.push({ comparison: comparison.key, case: c.id, arm: 'with', job: () =>
      agent(skillPrompt(c, comparison), { label: `run:${comparison.key}/${c.id}/with`, phase: 'Run', schema: OUTPUT }) })
  }
}
const outputs = await parallel(runs.map(r => r.job))
const results = runs.map((r, i) => ({ ...r, out: outputs[i] })).filter(r => r.out)
log(`${results.length}/${runs.length} runs returned`)

const routingMisses = results
  .filter(r => r.arm === 'with')
  .filter(r => r.out.mode_reported.toLowerCase() !== COMPARISONS.find(k => k.key === r.comparison).expect_mode)
  .map(r => `${r.comparison}/${r.case}: reported ${r.out.mode_reported || 'nothing'}`)
const leakage = Object.fromEntries(results.filter(r => r.arm === 'with').map(r => [`${r.comparison}/${r.case}`, leakageCount(r.out.text)]))

phase('Measure')
const measured = await parallel(CASES.map(c => () => {
  const mine = results.filter(r => r.case === c.id)
  const files = mine.map(r => ({ key: `${r.comparison}/${r.arm}`, text: r.out.text }))
  return agent(`Measure texts with the humanize scanner. Write each text below to its own file under ${SCRATCH}/${c.id}/ (create the directory), then run \`python3 ${SKILL}/scripts/scan.py --json --lang ${c.lang} --fail-on never FILE\` on each and read the JSON. Return for the original and for every output: sentence_length_variation and em_dashes_per_500_words from "metrics", and the counts of findings with severity "always" and "cluster". Return numbers exactly as the scanner printed them; measure, do not estimate.

ORIGINAL:
---
${c.text}
---

${files.map(f => `OUTPUT ${f.key}:\n---\n${f.text}\n---`).join('\n\n')}`, { label: `measure:${c.id}`, phase: 'Measure', schema: MEASURED, effort: 'low' })
    .then(m => m && { case: c.id, ...m })
})).then(all => all.filter(Boolean))
const metricsFor = (caseId, key) => {
  const m = measured.find(x => x.case === caseId)
  if (!m) return null
  const o = m.outputs.find(x => x.key === key)
  return o ? { original: m.original, out: o.metrics } : null
}

phase('Grade')
const pairs = []
COMPARISONS.forEach((comparison, k) => CASES.forEach((c, i) => {
  const withSkill = results.find(r => r.comparison === comparison.key && r.case === c.id && r.arm === 'with')
  const without = results.find(r => r.comparison === comparison.key && r.case === c.id && r.arm === 'without')
  if (!withSkill || !without) return
  const skillFirst = (seed + i + k) % 2 === 0
  pairs.push({ comparison, c, withSkill, without, orders: [skillFirst, !skillFirst] })
}))

function gradePrompt(c, A, B, gradeLabel) {
  const facts = JSON.stringify(c.facts)
  if (c.lang === 'nl') {
    return `${GRADER.nl}

ORIGINEEL:
---
${c.text}
---

HERSCHRIJVING A:
---
${A}
---

HERSCHRIJVING B:
---
${B}
---

Deze feiten staan in het origineel en moeten letterlijk of in gelijkwaardige vorm overleven: ${facts}.

Beoordeel herschrijving "${gradeLabel}":
- facts_kept van facts_total (${c.facts.length}): hoeveel overleefden
- facts_invented: elk getal, elke naam, datum, oorzaak of bewering in die herschrijving die NIET in het origineel staat. Citeer elk.
- tells_remaining: AI-schrijfpatronen die er nog in zitten. Noem ze gewoon bij naam (gedachtestreepje, niet-x-maar-y, drieslag, vage bron, opbeurend slot, hol versterkend woord, seriekomma, enzovoort) en citeer de passage.
- naturalness 1 tot 5: zou jij dit als tekst van een mens laten doorgaan?
- first_person_dropped: true als het origineel in de ik- of wij-vorm sprak en die in deze herschrijving verdwenen is.
- stance_dropped: true als een mening, toegeving of terzijde uit het origineel in deze herschrijving verdwenen is.
- better_arm: welke van A of B is in zijn geheel de betere herschrijving, of tie. Feiten behouden en niet verzinnen weegt zwaarder dan stilistische glans.
- reasoning: twee of drie zinnen, in het Nederlands.`
  }
  return `${GRADER.en}

ORIGINAL:
---
${c.text}
---

REWRITE A:
---
${A}
---

REWRITE B:
---
${B}
---

These facts appear in the original and must survive verbatim or in an equivalent form: ${facts}.

Grade the rewrite labelled "${gradeLabel}" on:
- facts_kept out of facts_total (${c.facts.length}): how many survived
- facts_invented: any number, name, date, cause or claim in that rewrite that is NOT in the original. Quote each.
- tells_remaining: AI-writing patterns still present. Name them plainly (em dash, not-X-but-Y, rule of three, vague attribution, inspirational closer, hollow intensifier, and so on) and quote the span.
- naturalness 1 to 5: would a careful human editor let this ship as a person's writing?
- first_person_dropped: true if the original spoke in the first person and this rewrite no longer does.
- stance_dropped: true if an opinion, admission or aside in the original is gone from this rewrite.
- better_arm: which of A or B is the better rewrite overall, or tie. Weigh facts kept and not invented above stylistic polish.
- reasoning: two or three sentences.`
}

const graded = await parallel(pairs.flatMap(p => p.orders.map((skillFirst, o) => () => {
  const A = skillFirst ? p.withSkill.out.text : p.without.out.text
  const B = skillFirst ? p.without.out.text : p.withSkill.out.text
  const gradeLabel = skillFirst ? 'A' : 'B'
  return agent(gradePrompt(p.c, A, B, gradeLabel), { label: `grade:${p.comparison.key}/${p.c.id}/${o ? 'swap' : 'base'}`, phase: 'Grade', schema: GRADE, effort: 'xhigh' })
    .then(g => g && { comparison: p.comparison.key, case: p.c.id, order: o, skillFirst, skill_better: g.better_arm === gradeLabel, tie: g.better_arm === 'tie', g })
}))).then(all => all.filter(Boolean))

function summarize(comparisonKey, lang) {
  return CASES.filter(c => c.lang === lang).map(c => {
    const gs = graded.filter(x => x.comparison === comparisonKey && x.case === c.id)
    if (gs.length < 2) return { case: c.id, status: 'incomplete', grades: gs.length }
    const wins = gs.filter(x => x.skill_better).length
    const won = wins === 2 ? 'won' : wins === 0 && gs.every(x => !x.tie) ? 'lost' : 'tie'
    const g = gs[0].g
    const m = metricsFor(c.id, `${comparisonKey}/with`)
    return {
      case: c.id,
      skill: won,
      facts: `${Math.min(...gs.map(x => x.g.facts_kept))}/${g.facts_total}`,
      invented: [...new Set(gs.flatMap(x => x.g.facts_invented))],
      naturalness: gs.map(x => x.g.naturalness),
      tells_remaining: g.tells_remaining,
      flattened: m ? flattened(m.out, m.original, g, c) : null,
      cv: m ? { original: m.original.sentence_length_variation, output: m.out.sentence_length_variation } : null,
      leakage: leakage[`${comparisonKey}/${c.id}`],
      reasoning: g.reasoning,
    }
  })
}

return {
  seed,
  constants: { FLATTEN_RATIO, FLATTEN_FLOOR },
  routing_misses: routingMisses,
  leakage,
  rewrite: { en: summarize('rewrite', 'en'), nl: summarize('rewrite', 'nl') },
  edit: { en: summarize('edit', 'en'), nl: summarize('edit', 'nl') },
}
