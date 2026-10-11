#!/usr/bin/env node
import fs from 'node:fs';

const file = process.argv[2];
if (!file) { console.error('node lines.mjs <project>/videos/<id>.js: prints the line count and the words per line'); process.exit(2); }
if (!fs.existsSync(file)) { console.error(`no ${file}: run gen.mjs first`); process.exit(2); }
const video = JSON.parse(fs.readFileSync(file, 'utf8').replace(/^window\.VIDEO = /, '').replace(/;\s*$/, ''));
console.log(video.lines.length, JSON.stringify(video.lines.map(l => l.vo.trim().split(/\s+/).length)));
