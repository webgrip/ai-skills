#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const USAGE = `node upload.mjs <project> <video-id> <cues.json> <video.mp4> <subtitles.srt>
  writes <video>.upload.json beside the video; renders thumbnails once per video when videos.mjs sets
  youtube.thumb; writes <video>-youtube.md when the youtube-upload-kit skill is found
  (YOUTUBE_UPLOAD_KIT, or installed next to seekframe)`;

const [projectArg, id, cuesPath, videoPath, srtPath] = process.argv.slice(2);
if (!srtPath) { console.error(USAGE); process.exit(2); }
const HERE = path.dirname(new URL(import.meta.url).pathname);
const RUNTIME = process.env.SEEKFRAME_RUNTIME || path.join(process.env.XDG_CACHE_HOME || path.join(process.env.HOME, '.cache'), 'seekframe');
const project = path.resolve(projectArg);
const { VIDEOS } = await import(path.join(project, 'videos.mjs'));
const v = VIDEOS.find(x => x.id === id);
if (!v) { console.error(`no video ${id} in ${project}/videos.mjs`); process.exit(2); }
const cues = JSON.parse(fs.readFileSync(cuesPath, 'utf8'));
const dest = path.dirname(path.resolve(videoPath));
const base = path.basename(videoPath, '.mp4');
const rel = p => path.relative(dest, p);

function findKit() {
  const env = process.env.YOUTUBE_UPLOAD_KIT;
  if (env) return fs.existsSync(path.join(env, 'scripts/sheet.mjs')) ? env : null;
  const flat = path.resolve(HERE, '../../youtube-upload-kit');
  if (fs.existsSync(path.join(flat, 'scripts/sheet.mjs'))) return flat;
  const cached = path.resolve(HERE, '../../../youtube-upload-kit');
  if (!fs.existsSync(cached)) return null;
  const versions = fs.readdirSync(cached).filter(d => fs.existsSync(path.join(cached, d, 'scripts/sheet.mjs')))
    .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  return versions.length ? path.join(cached, versions[versions.length - 1]) : null;
}

function voiceOf() {
  if (!base.endsWith('-voice')) return null;
  const dir = path.join(project, 'voice');
  const metas = fs.existsSync(dir) ? fs.readdirSync(dir).filter(f => f.startsWith(id + '-') && /-\d{2}\.json$/.test(f)) : [];
  if (!metas.length) return { provider: null, plan: null };
  const plans = metas.map(f => JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')).plan || 'free');
  return { provider: 'ElevenLabs', plan: plans.every(p => p !== 'free') ? 'paid' : 'free' };
}

function languageOf() {
  const conf = path.join(project, 'voice', 'voices.json');
  return (fs.existsSync(conf) && JSON.parse(fs.readFileSync(conf, 'utf8')).languages?.[id]) || v.youtube?.language || 'en';
}

function thumbnails(kit) {
  const spec = v.youtube?.thumb;
  const dir = path.join(dest, 'thumbs', id);
  const existing = () => fs.existsSync(dir) ? fs.readdirSync(dir).filter(f => /^thumb(-[a-c])?\.jpg$/.test(f)).sort().map(f => path.join(dir, f)) : [];
  if (existing().length || !spec || !kit) return existing();
  fs.mkdirSync(dir, { recursive: true });
  const work = path.join(project, '.work', id, 'thumb');
  const t = spec.frame ?? cues.lines[0].t0 + cues.lines[0].dur * 0.75;
  const run = (cmd, args) => { const r = spawnSync(cmd, args, { stdio: 'inherit' }); if (r.status !== 0) throw new Error(`${path.basename(cmd)} exited ${r.status}`); };
  run(process.execPath, [path.join(HERE, 'render.mjs'), 'stills', project, id, work, String(t)]);
  const still = path.join(work, fs.readdirSync(work).filter(f => f.endsWith('.png')).sort().pop());
  const [y0, h] = spec.crop || [0, 1080];
  run(path.join(RUNTIME, 'ffmpeg'), ['-nostdin', '-loglevel', 'error', '-y', '-i', still, '-vf', `crop=1920:${h}:0:${y0}`, path.join(dir, 'still-art.png')]);
  const { frame, crop, ...look } = spec;
  const config = { brand: path.join(project, 'brand.css'), product: v.product, kicker: v.kicker, bg: 'still-art.png', ...look };
  fs.writeFileSync(path.join(dir, 'thumb.json'), JSON.stringify(config, null, 2));
  run(process.execPath, [path.join(kit, 'scripts/thumb.mjs'), path.join(dir, 'thumb.json'), path.join(dir, 'thumb.jpg')]);
  return existing();
}

const kit = findKit();
const thumbs = thumbnails(kit);
const spec = v.youtube?.thumb;
const upload = {
  id: base,
  file: path.basename(videoPath),
  subtitles: path.basename(srtPath),
  duration: cues.dur,
  language: languageOf(),
  product: v.product,
  lines: cues.lines,
  voice: voiceOf(),
  thumbs: thumbs.map(rel),
  thumbWords: spec ? (spec.variants ? spec.variants.map(x => x.words || spec.words) : [spec.words]).filter(Boolean) : [],
  youtube: v.youtube || {},
};
const json = path.join(dest, base + '.upload.json');
fs.writeFileSync(json, JSON.stringify(upload, null, 1));
if (!kit) {
  console.log(`${json}\n  youtube-upload-kit not found: set YOUTUBE_UPLOAD_KIT to make the upload sheet`);
} else {
  const r = spawnSync(process.execPath, [path.join(kit, 'scripts/sheet.mjs'), json, ...(process.env.SEEKFRAME_OFFLINE ? ['--offline'] : [])], { stdio: 'inherit' });
  if (r.status !== 0) console.error('upload sheet failed; the video itself is fine');
}
