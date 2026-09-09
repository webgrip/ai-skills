export const meta = {
  name: 'humanize-quality-retest',
  description: 'Re-run the output-quality head-to-head after fixing the output contract and the catalog, same cases and same blind grading',
  phases: [
    { title: 'Run', detail: 'the skill applied to real slop, with and without' },
    { title: 'Grade', detail: 'blind graders score facts kept, tells gone, naturalness' },
  ],
}

const SKILL = '/Users/ryangrippeling/projects/webgrip/webgrip-ai-skills/skills/humanize'
const S = '/Users/ryangrippeling/projects/webgrip/webgrip-ai-skills/scripts/humanize'

const CASES = [
  {
    id: 'linkedin-post',
    text: `In today's rapidly evolving tech landscape, we're thrilled to announce something special. It's not just a product launch — it's a paradigm shift.\n\nAfter 14 months of relentless work, our team has built something that fundamentally reimagines how developers approach observability. By leveraging cutting-edge AI, we've reduced mean time to resolution by 47%, cut alert noise by two thirds, and empowered engineers to focus on what truly matters: building.\n\nExperts agree this represents a pivotal moment for the industry. Studies show that teams adopting intelligent observability see significant improvements across the board.\n\nDespite the challenges ahead, the future looks incredibly bright. Let's build it together.\n\nWhat's your take? Drop a comment below! 🚀\n\n#Observability #AI #DevOps #Innovation #FutureOfWork #Engineering`,
    facts: ['14 months', '47%', 'two thirds'],
  },
  {
    id: 'technical-readme',
    text: `## Introduction\n\nIn the ever-evolving world of container orchestration, managing secrets isn't just a technical challenge — it's a trust problem.\n\nThis tool serves as a bridge between your vault and your cluster. It stands as a testament to the principle that secrets should never live in Git.\n\n**Key Features:**\n\n- **Secure:** Secrets never touch disk unencrypted.\n- **Fast:** Sync completes in under 200ms.\n- **Simple:** One YAML file, zero dependencies.\n\nIt's worth noting that the tool supports both HashiCorp Vault and OpenBao. Whether you're a startup or an enterprise, the workflow remains the same.\n\n## Conclusion\n\nIn conclusion, secret management doesn't have to be painful. Despite its challenges, the ecosystem continues to evolve, paving the way for a more secure future.`,
    facts: ['200ms', 'HashiCorp Vault', 'OpenBao', 'One YAML file'],
  },
  {
    id: 'incident-writeup',
    text: `Our recent outage wasn't just downtime — it was a learning opportunity.\n\nOn March 3rd, a cascading failure took down the payments API for 43 minutes. The root cause? A retry storm. Our retries didn't just fail to help; they actively made things worse.\n\nHere's the thing: resilience isn't about preventing failure. It's about failing gracefully.\n\nWe've since implemented exponential backoff with jitter, reduced our retry budget from 3 to 1, and established a circuit breaker at the gateway. The results speak for themselves.\n\nWhat nobody tells you about incident response is that the technical fix is the easy part.`,
    facts: ['March 3rd', '43 minutes', '3 to 1'],
  },
]

const OUTPUT = { type: 'object', properties: { id: { type: 'string' }, arm: { type: 'string' }, result: { type: 'string' }, notes: { type: 'string' } }, required: ['id', 'arm', 'result', 'notes'] }
const GRADE = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    facts_kept: { type: 'integer' },
    facts_total: { type: 'integer' },
    facts_invented: { type: 'array', items: { type: 'string' } },
    tells_remaining: { type: 'array', items: { type: 'string' } },
    naturalness: { type: 'integer' },
    voice_flattened: { type: 'boolean' },
    better_arm: { type: 'string', enum: ['A', 'B', 'tie'] },
    reasoning: { type: 'string' },
  },
  required: ['id', 'facts_kept', 'facts_total', 'facts_invented', 'tells_remaining', 'naturalness', 'voice_flattened', 'better_arm', 'reasoning'],
}
const ENREVIEW = {
  type: 'object',
  properties: {
    categorie: { type: 'string' },
    reviewed: { type: 'integer' },
    problems: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' },
      kind: { type: 'string', enum: ['after-still-has-tell', 'after-worse-than-before', 'before-does-not-demonstrate', 'cue-not-real', 'definition-wrong', 'severity-wrong', 'duplicate-of'] },
      problem: { type: 'string' },
      fix: { type: 'string' },
      confidence: { type: 'string', enum: ['certain', 'unsure'] },
    }, required: ['id', 'kind', 'problem', 'fix', 'confidence'] } },
    verdict: { type: 'string' },
  },
  required: ['categorie', 'reviewed', 'problems', 'verdict'],
}

phase('Run')
const runs = await parallel(CASES.flatMap(c => [
  () => agent(`You are editing a draft. Here is the text:\n\n---\n${c.text}\n---\n\nRewrite it so it reads like a person wrote it. Keep every fact. Return only the rewritten text, nothing else.`,
    { label: `run:${c.id}/without`, phase: 'Run', schema: OUTPUT }).then(r => r && { ...r, id: c.id, arm: 'without' }),
  () => agent(`Read ${SKILL}/SKILL.md and follow it as your instructions. Then apply it in edit mode to this text:\n\n---\n${c.text}\n---\n\nThe catalog is at ${SKILL}/patterns-en.md and the method at ${SKILL}/method.md; the scanner is ${SKILL}/scripts/scan.py. Return exactly what the skill tells you to return, in the form the skill specifies. Do not add a wrapper, a preamble or headers of your own.`,
    { label: `run:${c.id}/with`, phase: 'Run', schema: OUTPUT }).then(r => r && { ...r, id: c.id, arm: 'with' }),
])).then(r => r.filter(Boolean))
log(`${runs.length} runs across ${CASES.length} cases`)

phase('Grade')
const grades = (await parallel(CASES.map(c => () => {
  const withSkill = runs.find(r => r.id === c.id && r.arm === 'with')
  const without = runs.find(r => r.id === c.id && r.arm === 'without')
  if (!withSkill || !without) return Promise.resolve(null)
  const [A, B] = c.id.length % 2 ? [withSkill, without] : [without, withSkill]
  return agent(`You are grading two rewrites of the same text. You do not know which tool produced which; judge only what is on the page.

ORIGINAL:
---
${c.text}
---

REWRITE A:
---
${A.result}
---

REWRITE B:
---
${B.result}
---

These facts appear in the original and must survive verbatim or in an equivalent form: ${JSON.stringify(c.facts)}.

Grade the rewrite labelled "${A === withSkill ? 'A' : 'B'}" on:
- facts_kept out of facts_total (${c.facts.length}): how many survived
- facts_invented: any number, name, date, cause or claim in that rewrite that is NOT in the original. Quote each.
- tells_remaining: AI-writing patterns still present in that rewrite. Name them plainly (em dash, not-X-but-Y, rule of three, vague attribution, inspirational closer, hollow intensifier, and so on) and quote the span.
- naturalness 1 to 5: would a careful human editor let this ship as a person's writing?
- voice_flattened: true if the rewrite is sterile — every sentence the same length, no stance, no first person where the original had one, or a stock staccato rhythm substituted for the original voice.
- better_arm: which of A or B is the better rewrite overall, or tie. Weigh facts kept and not invented above stylistic polish.
- reasoning: two or three sentences.

Return the grade for the rewrite you were asked about, with id "${c.id}".`, { label: `grade:${c.id}`, phase: 'Grade', schema: GRADE, effort: 'xhigh' })
    .then(g => g && { ...g, arm_graded: A === withSkill ? 'A=with' : 'B=with', better_arm_is_skill: (g.better_arm === 'A') === (A === withSkill) })
}))).filter(Boolean)
log(`graded ${grades.length} cases`)

return {
  grades: grades.map(g => ({
    case: g.id,
    facts: `${g.facts_kept}/${g.facts_total}`,
    invented: g.facts_invented,
    tells_remaining: g.tells_remaining,
    naturalness: g.naturalness,
    voice_flattened: g.voice_flattened,
    skill_won: g.better_arm_is_skill,
    reasoning: g.reasoning,
  })),
}
