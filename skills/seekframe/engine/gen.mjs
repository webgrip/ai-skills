#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const projectArg = process.argv[2];
if (!projectArg) { console.error('node gen.mjs <project>: writes <project>/videos/<id>.js and <project>/scripts.md from <project>/videos.mjs'); process.exit(2); }
const project = path.resolve(projectArg);
const { VIDEOS: SOURCE } = await import(path.join(project, 'videos.mjs'));
const partsFile = path.join(project, 'parts.mjs');
const { CLAIMS = {}, HOOKS = {}, CLOSES = {} } = fs.existsSync(partsFile) ? await import(partsFile) : {};
for (const [id, c] of Object.entries(CLAIMS)) {
  if (!['live', 'planned'].includes(c.status)) throw new Error(`claim "${id}" needs status 'live' or 'planned'`);
  if (!c.proof) throw new Error(`claim "${id}" needs proof: where a reader can check it`);
  if (!c.sc) throw new Error(`claim "${id}" needs sc: the one scene that always shows it`);
}
const pick = (x, register) => (x && typeof x === 'object' && !Array.isArray(x) ? x[register] : x);
function expand(v) {
  if (!v.recipe) return v;
  const r = v.recipe;
  const hook = HOOKS[r.hook];
  if (!hook) throw new Error(`video "${v.id}": no hook "${r.hook}" in parts.mjs`);
  const lines = hook.lines.map(l => ({ g: 'hook-' + r.hook, ...l }));
  for (const id of r.claims || []) {
    const c = CLAIMS[id];
    if (!c) throw new Error(`video "${v.id}": no claim "${id}" in parts.mjs`);
    const say = pick(c.say, r.register);
    if (!say) throw new Error(`video "${v.id}": claim "${id}" has no "${r.register}" phrasing`);
    for (const one of [].concat(say)) lines.push({ h: pick(c.h, r.register), sc: c.sc, p: c.p, g: 'claim-' + id, planned: c.status === 'planned', claim: id, ...(typeof one === 'string' ? { vo: one } : one) });
  }
  const close = CLOSES[r.close || 'default'];
  if (r.close && !close) throw new Error(`video "${v.id}": no close "${r.close}" in parts.mjs`);
  if (close) lines.push(...close.lines.map(l => ({ g: 'close', ...l })));
  return { ...v, lines };
}
const VIDEOS = SOURCE.map(expand);
const words = s => s.trim().split(/\s+/).length;
const estimate = v => 0.8 + v.lines.reduce((a, l) => a + Math.max(l.sc === 'endcard' ? 5.5 : 2.6, words(l.vo) / 2.45 + 0.95), 0);
const ids = new Set();
fs.mkdirSync(path.join(project, 'videos'), { recursive: true });
for (const v of VIDEOS) {
  if (!/^[a-z0-9][a-z0-9-]*$/.test(v.id)) throw new Error(`video id "${v.id}" must be lowercase-with-hyphens`);
  if (ids.has(v.id)) throw new Error(`duplicate video id "${v.id}"`);
  if (!v.group) throw new Error(`video "${v.id}" needs a group (its output folder)`);
  ids.add(v.id);
  const dst = path.join(project, 'videos', v.id + '.js');
  fs.writeFileSync(dst + '.tmp', `window.VIDEO = ${JSON.stringify(v)};\n`);
  fs.renameSync(dst + '.tmp', dst);
}
let md = '# Voice-over scripts\n\nOne block per video; blank lines are where the video cuts. Lines tagged planned stay labelled on screen.\n';
for (const g of [...new Set(VIDEOS.map(v => v.group))]) {
  md += `\n## ${g}\n`;
  for (const v of VIDEOS.filter(x => x.group === g)) {
    md += `\n### ${v.id} · ${v.name || v.id} (about ${Math.round(estimate(v))} s)\n\n\`\`\`\n${v.voice ? v.voice + '\n' : ''}${v.lines.map(l => l.vo).join('\n\n')}\n\`\`\`\n`;
  }
}
fs.writeFileSync(path.join(project, 'scripts.md'), md);
if (Object.keys(CLAIMS).length) {
  const used = VIDEOS.map(v => [v.id, new Set(v.lines.map(l => l.claim).filter(Boolean))]);
  let cm = '# Claims by video\n\nGenerated from parts.mjs and videos.mjs. A claim used nowhere is either new or dead.\n\n';
  cm += `| Claim | Status | Scene | Proof | ${used.map(([id]) => id).join(' | ')} |\n|${'---|'.repeat(4 + used.length)}\n`;
  for (const [id, c] of Object.entries(CLAIMS)) cm += `| ${id} | ${c.status} | ${c.sc} | ${c.proof} | ${used.map(([, u]) => (u.has(id) ? 'x' : '')).join(' | ')} |\n`;
  fs.writeFileSync(path.join(project, 'claims.md'), cm);
}
console.log(VIDEOS.map(v => `${v.id} ~${Math.round(estimate(v))}s`).join('\n'));
