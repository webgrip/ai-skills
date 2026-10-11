#!/usr/bin/env node
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const USAGE = `node render.mjs <mode> <project> <video-id> ...
  meta   <project> <id> <cues.json>                             cue sheet for music, voice and subtitles
  stills <project> <id> <outdir> <t1,t2,...>                    exact frames as PNG
  sheet  <project> <id> <out.png>                                one frame late in every line, 4 across
  video  <project> <id> <out.mkv> [workers] [subframes] [from] [to]   motion-blurred lossless video`;

const HERE = path.dirname(new URL(import.meta.url).pathname);
const RUNTIME = process.env.SEEKFRAME_RUNTIME || path.join(process.env.XDG_CACHE_HOME || path.join(process.env.HOME, '.cache'), 'seekframe');
const FFMPEG = path.join(RUNTIME, 'ffmpeg');
const FPS = 60;
const [mode, projectArg, id, ...args] = process.argv.slice(2);
if (!mode || !projectArg || !id) { console.error(USAGE); process.exit(2); }
const project = path.resolve(projectArg);
if (!fs.existsSync(path.join(project, 'videos', id + '.js'))) {
  console.error(`no ${path.join(project, 'videos', id + '.js')}; run: node ${path.join(HERE, 'gen.mjs')} ${project}`);
  process.exit(2);
}
const { chromium } = await import(process.env.PLAYWRIGHT_MJS || path.join(RUNTIME, 'node_modules/playwright/index.mjs'));
const CACHE = path.join(process.env.HOME, '.cache/ms-playwright');
const CHROME = process.env.REEL_CHROME || (fs.existsSync(CACHE)
  ? fs.readdirSync(CACHE).filter(d => d.startsWith('chromium_headless_shell-')).sort((a, b) => +b.split('-')[1] - +a.split('-')[1])
    .map(d => path.join(CACHE, d, 'chrome-headless-shell-linux64/chrome-headless-shell')).find(f => fs.existsSync(f))
  : undefined);
const PAGE = 'file://' + path.join(HERE, 'kit', 'kit.html') + '?v=' + encodeURIComponent(id) + '&p=' + encodeURIComponent(project);

async function open() {
  const browser = await chromium.launch({ executablePath: CHROME, args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text', '--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(PAGE);
  const dur = await page.evaluate(() => window.READY).catch(e => { throw new Error(errors.concat(e.message).join(' | ')); });
  const cdp = await page.context().newCDPSession(page);
  const shot = async t => {
    await page.evaluate(t => window.seek(t), t);
    const r = await cdp.send('Page.captureScreenshot', { format: 'png', optimizeForSpeed: true });
    return Buffer.from(r.data, 'base64');
  };
  return { browser, page, shot, dur, errors };
}

const run = (cmd, argv, opts = {}) => new Promise((res, rej) => {
  const c = spawn(cmd, argv, Object.assign({ stdio: 'inherit' }, opts));
  c.on('close', code => (code === 0 ? res() : rej(new Error(`${path.basename(cmd)} exited ${code}`))));
  return c;
});

if (mode === 'meta') {
  const [out] = args;
  const { browser, page } = await open();
  const cues = await page.evaluate(() => window.CUES());
  fs.writeFileSync(out, JSON.stringify(cues, null, 1));
  console.log(cues.dur.toFixed(2) + 's', cues.scenes.map(s => `${s.type}@${s.t0.toFixed(1)}+${s.dur.toFixed(1)}`).join(' '));
  await browser.close();
} else if (mode === 'stills') {
  const [outdir, list] = args;
  fs.mkdirSync(outdir, { recursive: true });
  const { browser, shot } = await open();
  for (const s of list.split(',')) {
    const t = parseFloat(s);
    fs.writeFileSync(path.join(outdir, `t${t.toFixed(2).padStart(6, '0')}.png`), await shot(t));
  }
  await browser.close();
} else if (mode === 'sheet') {
  const [out] = args;
  const { browser, page, shot, errors } = await open();
  const cues = await page.evaluate(() => window.CUES());
  const times = cues.lines.map(l => +(l.t0 + Math.min(l.dur - 0.3, Math.max(1.6, l.dur * 0.75))).toFixed(2));
  const cols = 4, rows = Math.ceil(times.length / cols);
  const ff = spawn(FFMPEG, ['-nostdin', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'png', '-i', '-', '-vf', `scale=480:270,tile=${cols}x${rows}:padding=4:color=white`, '-frames:v', '1', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (const t of times) ff.stdin.write(await shot(t));
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log(id, cues.dur.toFixed(1) + 's', errors.length ? 'PAGE ERRORS: ' + errors.join(' | ') : 'ok');
} else if (mode === 'worker') {
  const [out, a, b, sub] = args;
  const K = +sub;
  const ff = spawn(FFMPEG, ['-nostdin', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS * K), '-c:v', 'png', '-i', '-',
    '-vf', `tmix=frames=${K},select='eq(mod(n\\,${K})\\,${K - 1})',setpts=N/(${FPS}*TB)`, '-r', String(FPS), '-c:v', 'ffv1', '-level', '3', '-pix_fmt', 'bgr0', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const { browser, shot, dur } = await open();
  const shutter = 0.5;
  for (let i = +a; i < +b; i++) {
    for (let k = 0; k < K; k++) {
      const t = Math.max(0, i / FPS + ((k + 0.5) / K - 0.5) * shutter / FPS);
      if (!ff.stdin.write(await shot(Math.min(t, dur - 1e-4)))) await new Promise(r => ff.stdin.once('drain', r));
    }
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
} else if (mode === 'video') {
  const [out, workersArg, subArg, fromArg, toArg] = args;
  const probe = await open();
  const total = probe.dur;
  await probe.browser.close();
  const workers = +(workersArg || 16), K = +(subArg || 8);
  const F0 = Math.round(+(fromArg || 0) * FPS), F1 = Math.round(+(toArg || total) * FPS);
  const tmp = path.join(path.dirname(path.resolve(out)), 'segments');
  fs.rmSync(tmp, { recursive: true, force: true });
  fs.mkdirSync(tmp, { recursive: true });
  const per = Math.ceil((F1 - F0) / workers), t0 = Date.now(), jobs = [];
  for (let w = 0; w < workers; w++) {
    const a = F0 + w * per, b = Math.min(F1, a + per);
    if (a >= b) break;
    const seg = path.join(tmp, `seg${String(w).padStart(3, '0')}.mkv`);
    jobs.push({ seg, p: run(process.execPath, [new URL(import.meta.url).pathname, 'worker', project, id, seg, String(a), String(b), String(K)]) });
  }
  await Promise.all(jobs.map(j => j.p));
  fs.writeFileSync(path.join(tmp, 'list.txt'), jobs.map(j => `file '${j.seg}'`).join('\n'));
  await run(FFMPEG, ['-nostdin', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(tmp, 'list.txt'), '-c', 'copy', out]);
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log(`rendered ${F1 - F0} frames × ${K} sub-frames in ${((Date.now() - t0) / 1000).toFixed(1)} s → ${out}`);
} else {
  console.error(USAGE);
  process.exit(2);
}
