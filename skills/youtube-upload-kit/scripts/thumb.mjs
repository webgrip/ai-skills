#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const USAGE = `node thumb.mjs <config.json> <out.jpg|out.png>
  config: {"words": "Two lines\\n*accent*", "kicker", "badge", "product", "brand": "brand.css",
           "bg": "still.png", "bgZoom": 1.05, "bgPos": "690px 55%", "ground": "dark|paper|red", "ratio": "16:9|9:16",
           "variants": [{...}, {...}]}   variants become <out>-a, -b, -c for Test & Compare
  paths in the config are relative to the config file`;
const [cfgPath, out] = process.argv.slice(2);
if (!cfgPath || !out) { console.error(USAGE); process.exit(2); }
const HERE = path.dirname(new URL(import.meta.url).pathname);
const RUNTIME = process.env.SEEKFRAME_RUNTIME || path.join(process.env.XDG_CACHE_HOME || path.join(process.env.HOME, '.cache'), 'seekframe');
if (!process.env.PLAYWRIGHT_MJS && !fs.existsSync(path.join(RUNTIME, 'node_modules/playwright'))) {
  console.error(`first run: npm i --prefix ${RUNTIME} playwright@1.63.0 && node ${RUNTIME}/node_modules/playwright/cli.js install chromium-headless-shell`);
  process.exit(2);
}
const { chromium } = await import(process.env.PLAYWRIGHT_MJS || path.join(RUNTIME, 'node_modules/playwright/index.mjs'));
const CACHE = path.join(process.env.HOME, '.cache/ms-playwright');
const CHROME = process.env.REEL_CHROME || (fs.existsSync(CACHE)
  ? fs.readdirSync(CACHE).filter(d => d.startsWith('chromium_headless_shell-')).sort((a, b) => +b.split('-')[1] - +a.split('-')[1])
    .map(d => path.join(CACHE, d, 'chrome-headless-shell-linux64/chrome-headless-shell')).find(f => fs.existsSync(f))
  : undefined);

const base = path.dirname(path.resolve(cfgPath));
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const list = cfg.variants ? cfg.variants.map((v, i) => [{ ...cfg, variants: undefined, ...v }, String.fromCharCode(97 + i)]) : [[cfg, '']];
const ext = path.extname(out).toLowerCase() || '.jpg';
const browser = await chromium.launch({ executablePath: CHROME, args: ['--force-color-profile=srgb', '--allow-file-access-from-files'] });
for (const [c, tag] of list) {
  for (const k of ['bg', 'brand']) if (c[k]) c[k] = 'file://' + path.resolve(base, c[k]);
  const vertical = c.ratio === '9:16';
  const size = vertical ? { width: 1080, height: 1920 } : { width: 1280, height: 720 };
  const page = await browser.newPage({ viewport: size, deviceScaleFactor: vertical ? 1 : 2 });
  await page.goto('file://' + path.join(HERE, 'thumb.html') + '?c=' + encodeURIComponent(JSON.stringify(c)));
  await page.evaluate(() => window.READY);
  const file = tag ? out.replace(/(\.[a-z]+)?$/i, `-${tag}${ext}`) : out;
  await page.screenshot({ path: file, type: ext === '.png' ? 'png' : 'jpeg', quality: ext === '.png' ? undefined : 90, clip: { x: 0, y: 0, ...size } });
  const kb = Math.round(fs.statSync(file).size / 1024);
  console.log(`${file} ${kb} KB${kb > 2000 ? '  over 2 MB: YouTube mobile upload refuses it; save as .jpg' : ''}`);
  await page.close();
}
await browser.close();
