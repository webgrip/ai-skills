export const meta = {
  name: 'humanize-apply-en-review',
  description: 'Apply the adversarial review findings to the English catalog, one agent per category, each verifying its own regexes against human prose',
  phases: [{ title: 'Apply', detail: 'one agent per category' }],
}

const S = '/Users/ryangrippeling/projects/webgrip/webgrip-ai-skills/scripts/humanize'
const PROBLEMS = '/private/tmp/claude-501/-Users-ryangrippeling-projects-webgrip-twente-dev/f4fbfffd-c338-4a42-8df7-99e8c28b0f52/scratchpad/deai/out/en-problems.json'
const CATS = ['vocabulary', 'syntax', 'rhetoric', 'structure', 'punctuation-format', 'content', 'artifacts']

const RESULT = {
  type: 'object',
  properties: {
    categorie: { type: 'string' },
    applied: { type: 'array', items: { type: 'string' } },
    rejected: { type: 'array', items: { type: 'string' } },
    entries_before: { type: 'integer' },
    entries_after: { type: 'integer' },
    report: { type: 'string' },
  },
  required: ['categorie', 'applied', 'rejected', 'entries_before', 'entries_after', 'report'],
}

function prompt(cat) {
  return `An adversarial reviewer read the "${cat}" category of an English catalog of AI-writing tells and reported problems. Apply the ones that are right and reject the ones that are not.

**Your findings**: read ${PROBLEMS} with python3 and filter to categorie == "${cat}". Each has id, kind, problem, fix, confidence.

**The catalog**: ${S}/catalog/catalog-en.json, key categories["${cat}"]. Read and write it with python3; never print the whole file.

Apply, in this order:

1. **confidence "certain"**: apply the fix unless you can show it is wrong. If you reject one, say why in "rejected". The reviewer was strict and mostly right; the burden is on rejecting, not on applying.
2. **confidence "unsure"**: apply only when you can verify the claim yourself against the entry and the control corpus. Otherwise fold the nuance into false_positives instead of changing the entry, and record that in "applied".
3. **kind "duplicate-of"**: do not delete an entry unless the fix names the survivor and the survivor is genuinely the same mechanism. Prefer moving the overlapping cues to the survivor and adding a cross-reference line to false_positives of both.
4. **kind "severity-wrong"**: a severity that the entry's own false_positives contradicts is always wrong. Lowering always to cluster needs no further evidence when the false_positives says one hit proves nothing. Raising a severity needs a reason you state.
5. **kind "cue-not-real"**: delete the cue. If a regex uses it, adjust the regex in the same edit, then re-verify that regex.

Hard rules for anything you write:
- **A cue is never the corrected form.** If the entry teaches "utilize to use", "use" is not a cue. Check the whole cue list of every entry you touch for this and fix it even where the reviewer did not flag it.
- **An "after" example never contains a tell from any category**: no em dash, no not-X-but-Y, no colon reveal, no rule of three, no hollow intensifier, no signposted conclusion. If a fix introduces one, write a better sentence yourself.
- **An "after" never asserts something the "before" did not support.** Removing a hedge by inventing certainty is forbidden; remove it by supplying the concrete detail instead.
- Every regex you add or change must compile under Python re with IGNORECASE, match at least one of its own cues or the entry's before example, and fire at most twice per 10,000 words on ${S}/control/en-strunk-elements-of-style.txt. Run a script to check; report anything you dropped for over-matching.
- Keep the JSON shape and key names exactly as they are. Keep every entry's id stable unless a duplicate merge removes it.

**Do not write to catalog-en.json.** Other agents are working on other categories of it. Write your finished list of entries to ${S}/catalog/en-reviewed-${cat}.json as {"categorie": "${cat}", "entries": [...]}; the caller merges the categories back.

Return: applied (one line per change, with the entry id), rejected (with the reason), entry counts before and after, and a report of two or three sentences naming what mattered most.`
}

phase('Apply')
const results = (await parallel(CATS.map(cat => () =>
  agent(prompt(cat), { label: `apply:${cat}`, phase: 'Apply', schema: RESULT, effort: 'xhigh' })
))).filter(Boolean)

return {
  per_category: results.map(r => `${r.categorie}: ${r.entries_before} -> ${r.entries_after} entries, ${r.applied.length} applied, ${r.rejected.length} rejected — ${r.report}`),
  applied: results.flatMap(r => r.applied),
  rejected: results.flatMap(r => r.rejected),
}
