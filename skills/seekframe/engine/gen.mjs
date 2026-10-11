#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const projectArg = process.argv[2];
if (!projectArg) { console.error('node gen.mjs <project>: writes <project>/videos/<id>.js and <project>/scripts.md from <project>/videos.mjs'); process.exit(2); }
const project = path.resolve(projectArg);
const { VIDEOS } = await import(path.join(project, 'videos.mjs'));
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
console.log(VIDEOS.map(v => `${v.id} ~${Math.round(estimate(v))}s`).join('\n'));
