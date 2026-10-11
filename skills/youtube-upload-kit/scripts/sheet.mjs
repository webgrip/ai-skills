#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const USAGE = `node sheet.mjs <upload.json> [out.md] [--offline]
  upload.json: {"id", "file", "subtitles", "duration", "language": "en", "product",
                "lines": [{"t0", "dur", "h", "vo"}], "voice": {"provider": "ElevenLabs", "plan": "free|paid"} | null,
                "thumbs": ["thumb-a.jpg", ...], "thumbWords": ["Ten agents.\\n*One laptop.*", ...],
                "youtube": {"title", "titles": [...], "above": ["problem", "what the video shows"], "link",
                            "hashtags": [...], "tags": [...], "category", "chapters": [{"line": 1, "title"}],
                            "trademarks": [...], "credits": [...], "endScreen": {"from": 40}, "playlist",
                            "visibility": "unlisted|public|private", "paidPromotion": false, "realPerson": false}}
  writes the Studio upload sheet (default <upload.json minus .upload.json>-youtube.md) in the order the
  upload dialog asks, and prints every rule the package breaks`;

const argv = process.argv.slice(2);
const offline = argv.includes('--offline');
const [inPath, outArg] = argv.filter(a => a !== '--offline');
if (!inPath) { console.error(USAGE); process.exit(2); }
const u = JSON.parse(fs.readFileSync(inPath, 'utf8'));
const y = u.youtube || {};
const out = outArg || inPath.replace(/(\.upload)?\.json$/, '') + '-youtube.md';
const problems = [];
const problem = (level, text) => problems.push({ level, text });

const clock = t => { const s = Math.max(0, Math.floor(t)); return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`; };
const plain = s => (s || '').replace(/\*/g, '').replace(/\s+/g, ' ').trim();
const stem = w => w.toLowerCase().replace(/[^a-z0-9]/g, '').replace(/s$/, '');
const FILLER = new Set(['your', 'you', 'with', 'that', 'this', 'from', 'them', 'they', 'what', 'into', 'have', 'about', 'without', 'when', 'than', 'then', 'just', 'every', 'own']);
const contentWords = s => new Set(plain(s).split(' ').map(stem).filter(w => w.length >= 4 && !FILLER.has(w)));
const duration = +u.duration || 0;
const lines = u.lines || [];

function chapters() {
  if (y.chapters?.length) {
    return y.chapters.map((c, i) => ({ t: i === 0 ? 0 : (lines[c.line - 1]?.t0 ?? c.t ?? 0), title: c.title, auto: false }));
  }
  const target = Math.max(10, duration / 5), list = [];
  for (const l of lines) {
    if (!list.length || l.t0 - list[list.length - 1].t >= target) list.push({ t: list.length ? l.t0 : 0, title: plain(l.h) || plain(l.vo).split(' ').slice(0, 6).join(' '), auto: true });
  }
  while (list.length > 1 && duration - list[list.length - 1].t < 10) list.pop();
  return list;
}
const chs = chapters();
if (chs.length >= 3) chs.forEach((c, i) => {
  const end = i + 1 < chs.length ? chs[i + 1].t : duration;
  if (end - c.t < 10) problem('fix', `chapter "${c.title}" lasts ${(end - c.t).toFixed(1)} s; YouTube needs at least 10 s per chapter`);
});
if (chs.length < 3) problem('note', `chapters left out: ${clock(duration)} does not split into three of at least 10 s`);
else if (chs.some(c => c.auto)) problem('check', 'chapter titles were taken from the on-screen headlines; rename them to what a viewer would search for, or set youtube.chapters');

const title = y.title || '';
if (!title) problem('fix', 'no youtube.title');
if (title.length > 100) problem('fix', `title is ${title.length} characters; the limit is 100`);
if (title.length > 60) problem('check', `title is ${title.length} characters; about 60 show before truncation, so the outcome must sit in the first 60`);
if (u.product && title && !title.trim().endsWith(u.product)) problem('check', `put the product name last in the title ("… | ${u.product}")`);
for (const words of u.thumbWords || []) {
  const shared = [...contentWords(words)].filter(w => contentWords(title).has(w));
  if (shared.length) problem('check', `thumbnail "${plain(words)}" repeats the title (${shared.join(', ')}); the two should add to each other`);
}
if ((y.titles || []).length > 2) problem('fix', 'Test & Compare takes three titles at most: the title plus two alternatives');
if ((u.thumbs || []).length > 3) problem('fix', 'Test & Compare takes three thumbnails at most');

const freeVoice = u.voice && u.voice.plan !== 'paid';
const credits = [];
if (u.voice?.provider) credits.push(`Voice: ${u.voice.provider}${/elevenlabs/i.test(u.voice.provider) ? ' (elevenlabs.io)' : ''}`);
for (const t of y.trademarks || []) credits.push(`${t} is a trademark of its owner.`);
credits.push(...(y.credits || []));
const hashtags = (y.hashtags || []).map(h => '#' + h.replace(/^#/, ''));
if (hashtags.length > 3) problem('check', `${hashtags.length} hashtags; only three show above the title`);
const description = [
  (y.above || []).join('\n'),
  y.link || '',
  chs.length >= 3 ? chs.map(c => `${clock(c.t)} ${c.title}`).join('\n') : '',
  hashtags.join(' '),
  credits.join('\n'),
].filter(Boolean).join('\n\n');
if (!(y.above || []).length) problem('fix', 'no youtube.above: the two lines above the fold (the problem, what the video shows)');
if (description.length > 5000) problem('fix', `description is ${description.length} characters; the limit is 5000`);
const tags = y.tags || [];
if (tags.join(',').length > 500) problem('fix', 'tags exceed 500 characters');

let visibility = (y.visibility || 'unlisted').toLowerCase();
if (freeVoice && visibility === 'public') {
  problem('fix', 'the voice was made on a free plan (non-commercial only); it stays unlisted until the audio is remade on a paid plan');
  visibility = 'unlisted';
}

if (y.link && !offline) {
  try {
    const r = await fetch(y.link, { method: 'GET', redirect: 'follow', signal: AbortSignal.timeout(8000) });
    if (!r.ok) problem('fix', `${y.link} answers ${r.status}; fix it or leave the link out`);
  } catch (e) {
    problem('fix', `${y.link} does not load (${e.cause?.code || e.name}); fix it or leave the link out`);
  }
}
for (const t of u.thumbs || []) {
  const p = path.resolve(path.dirname(inPath), t);
  if (!fs.existsSync(p)) problem('fix', `thumbnail ${t} does not exist`);
  else if (fs.statSync(p).size > 2e6) problem('fix', `thumbnail ${t} is over 2 MB; save it as JPG`);
}

let endScreen = 'Skip: the edit leaves no free 5 to 20 s at the end. Leave that space in the next cut if a related video exists.';
if (y.endScreen?.from != null) {
  const tail = duration - y.endScreen.from;
  if (duration < 25) problem('fix', 'end screens need a video of at least 25 s');
  if (tail < 5 || tail > 20) problem('fix', `end screen window is ${tail.toFixed(1)} s; it must be 5 to 20 s`);
  endScreen = `From ${clock(y.endScreen.from)}: ${y.endScreen.what || 'the related video or playlist plus subscribe'}`;
}

const row = (k, v) => `| ${k} | ${v} |`;
const block = s => '```\n' + s + '\n```';
const md = [
  `# Upload sheet: ${u.id}`,
  '',
  `File \`${u.file}\` · ${clock(duration)} · generated from the render; edit the source, not this file.`,
  '',
  problems.length ? '## Before you upload\n\n' + problems.map(p => `- **${p.level}**: ${p.text}`).join('\n') : '## Before you upload\n\nNothing to fix.',
  '',
  '## 1. Details',
  '',
  '**Title**',
  '',
  block(title),
  '',
  ...(y.titles?.length ? ['**A/B Testing** (next to the title), alternatives:', '', ...y.titles.map(t => `- \`${t}\``), ''] : []),
  '**Description**',
  '',
  block(description),
  '',
  '**Thumbnail**: ' + ((u.thumbs || []).length
    ? `Upload file \`${u.thumbs[0]}\`${u.thumbs.length > 1 ? `; A/B Testing adds ${u.thumbs.slice(1).map(t => `\`${t}\``).join(', ')}` : ''}.`
    : 'none rendered; make them with scripts/thumb.mjs from a frame of this video.'),
  '',
  `**Playlists**: ${y.playlist || 'none yet'}`,
  '',
  '**Audience**: No, it\'s not made for kids.',
  '',
  '**Show more**',
  '',
  '| Field | Set to |',
  '|---|---|',
  row('Paid promotion', y.paidPromotion ? 'Checked: a third party paid for or supplied what is promoted' : 'Unchecked: it covers paid relationships with a third party, not your own product'),
  row('Altered or synthetic content', y.realPerson ? 'Yes: a real person appears to say or do something they did not' : 'No: animation, and any synthetic narrator is not a real person'),
  row('Automatic chapters', chs.length >= 3 ? 'Off: the description carries the chapters' : 'On, or leave chapters out'),
  row('Featured places, automatic concepts', 'Off'),
  row('Tags', tags.length ? '`' + tags.join(', ') + '`' : 'Leave empty: tags matter little, except for common misspellings'),
  row('Language', `${u.language || 'en'} for the video and the title and description`),
  row('Caption certification', 'This content has never aired on television in the US'),
  row('Recording date and location', 'Leave empty'),
  row('License', freeVoice ? 'Standard YouTube License: Creative Commons would allow commercial reuse of non-commercial audio' : 'Standard YouTube License'),
  row('Allow embedding', 'On'),
  row('Publish to subscriptions feed', visibility === 'public' ? 'On' : 'No effect while not public'),
  row('Shorts remixing', freeVoice ? 'Don\'t allow video remixing; blocking audio-only remixing needs Content Manager' : 'Allow'),
  row('Automatic dubbing', u.voice ? 'Off: it would replace the chosen voice' : 'Your choice'),
  row('Category', y.category || 'Science & Technology'),
  row('Comments', visibility === 'unlisted' ? 'On, hold potentially inappropriate comments, sort by Newest' : 'On, hold potentially inappropriate comments'),
  row('Show like count', 'On'),
  '',
  '## 2. Video elements',
  '',
  `- **Subtitles**: upload \`${u.subtitles || 'the .srt'}\`, language ${u.language || 'en'}; play a few seconds in Edit to check the timing.`,
  `- **End screen**: ${endScreen}`,
  '- **Cards**: only when a related video exists to point to.',
  '- **Quiz**: skip for a promo or explainer under a few minutes.',
  '',
  '## 3. Checks',
  '',
  'Wait for "Checks complete. No issues found." before setting visibility.',
  '',
  '## 4. Visibility',
  '',
  `**${visibility[0].toUpperCase() + visibility.slice(1)}**${freeVoice ? ': free-plan voice, non-commercial with attribution until the audio is remade on a paid plan' : visibility === 'unlisted' ? ': link only, comments on, viewers need no Google account' : ''}.`,
  '',
  '## Afterwards',
  '',
  'Wait days, not hours. Compare click-through against the channel\'s own median, and read the first 30 s of the retention curve: a cliff there means the thumbnail promised something else.',
  '',
].join('\n');

fs.writeFileSync(out, md);
console.log(`${out}`);
for (const p of problems) console.log(`  ${p.level}: ${p.text}`);
