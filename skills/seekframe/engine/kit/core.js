'use strict';
const VERTICAL = new URLSearchParams(location.search).get('f') === '9:16';
const W = VERTICAL ? 1080 : 1920, H = VERTICAL ? 1920 : 1080, FPS = 60;
const SAFE = VERTICAL ? { l: 90, r: W - 200, t: 290, b: H - 420 } : { l: 150, r: W - 150, t: 108, b: H - 110 };
const SW = SAFE.r - SAFE.l;
document.documentElement.style.setProperty('--W', W + 'px');
document.documentElement.style.setProperty('--H', H + 'px');
let DUR = 40;
const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
const lerp = (a, b, t) => a + (b - a) * t;
const P = (t, a, b) => clamp((t - a) / (b - a));
const ease = {
  lin: x => x,
  inCubic: x => x * x * x,
  outCubic: x => 1 - Math.pow(1 - x, 3),
  inOutCubic: x => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  inQuart: x => x * x * x * x,
  outQuint: x => 1 - Math.pow(1 - x, 5),
  outExpo: x => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
  outBackS: x => { const s = 2.6; return 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2); },
};
const E = (t, a, b, fn = ease.outExpo) => fn(P(t, a, b));
function spring(dt, f = 2.2, z = 0.42) {
  if (dt <= 0) return 0;
  const w = 2 * Math.PI * f, wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * dt) * (Math.cos(wd * dt) + ((z * w) / wd) * Math.sin(wd * dt));
}
function hash(n) {
  n = (n ^ 61) ^ (n >>> 16); n = n + (n << 3); n = n ^ (n >>> 4);
  n = Math.imul(n, 0x27d4eb2d); n = n ^ (n >>> 15); return n >>> 0;
}
function h(tag, cls, parent, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  if (parent) parent.appendChild(e);
  return e;
}
const SVGNS = 'http://www.w3.org/2000/svg';
function sv(tag, attrs, parent) {
  const e = document.createElementNS(SVGNS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}
function css(e, o) { for (const k in o) e.style[k] = o[k]; return e; }
function at(parent, x, y, cls, html, style) {
  const e = h('div', 'a ' + (cls || ''), parent, html);
  css(e, Object.assign({ left: x + 'px', top: y + 'px' }, style || {}));
  return e;
}
const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/#+-=:.';
function scramble(text, p, seed) {
  const n = text.length, k = Math.floor(p * (n + 6));
  let s = '';
  for (let i = 0; i < n; i++) {
    const c = text[i];
    if (i < k - 6 || c === ' ' || p >= 1) s += c;
    else if (i < k) s += GLYPHS[hash(i * 131 + seed * 7) % GLYPHS.length];
    else s += ' ';
  }
  return s;
}
function typed(text, p) { return text.slice(0, Math.round(clamp(p) * text.length)); }
const brandVar = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

const HUD = (() => {
  const root = document.getElementById('hud');
  const s = sv('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, root);
  const m = 44, L = 22, paths = [];
  [[m, m, 1, 1], [W - m, m, -1, 1], [m, H - m, 1, -1], [W - m, H - m, -1, -1]].forEach(([x, y, dx, dy]) => {
    paths.push(sv('path', { d: `M${x} ${y + dy * L}V${y}H${x + dx * L}`, fill: 'none', 'stroke-width': 1.5 }, s));
  });
  const prog = sv('rect', { x: 0, y: H - 3, height: 3, width: 0 }, s);
  const tl = h('div', 'hudtxt', root); css(tl, VERTICAL ? { left: SAFE.l + 'px', top: (SAFE.t - 70) + 'px' } : { left: '80px', top: '35px' });
  const tr = h('div', 'hudtxt', root); css(tr, { right: '80px', top: '35px', textAlign: 'right' });
  const bl = h('div', 'hudtxt', root); css(bl, { left: '80px', bottom: '33px' });
  const br = h('div', 'hudtxt', root); css(br, { right: '80px', bottom: '33px', textAlign: 'right' });
  if (VERTICAL) [tr, bl, br].forEach(e => (e.style.display = 'none'));
  let sections = [[0, '']], bottoms = [[0, '']], site = '';
  const pick = (list, t) => { let r = list[0]; for (const e of list) if (t >= e[0]) r = e; return r; };
  const pad = n => String(n).padStart(2, '0');
  return {
    configure(sec, bot, url) { sections = sec; bottoms = bot; site = url || ''; },
    update(t, tone) {
      const ink = brandVar(tone === 'light' ? '--brand-dark' : '--brand-light');
      const a = tone === 'light' ? 0.62 : tone === 'red' ? 0.9 : 0.6;
      paths.forEach(p => { p.setAttribute('stroke', ink); p.setAttribute('stroke-opacity', a * 0.8); });
      prog.setAttribute('width', (W * clamp(t / DUR)).toFixed(1));
      prog.setAttribute('fill', tone === 'red' ? brandVar('--brand-light') : brandVar('--brand-accent'));
      const sec = pick(sections, t), bot = pick(bottoms, t), seed = Math.floor(t * 30);
      tl.textContent = scramble(sec[1].toUpperCase(), P(t, sec[0], sec[0] + 0.35), seed);
      bl.textContent = scramble(bot[1].toUpperCase(), P(t, bot[0], bot[0] + 0.5), seed + 3);
      const fr = Math.round(t * FPS);
      tr.textContent = `TC ${pad(Math.floor(fr / 3600))}:${pad(Math.floor(fr / 60) % 60)}:${pad(fr % 60)}  ·  ${W}×${H}  ·  ${FPS}P`;
      br.textContent = site.toUpperCase();
      [tl, tr, bl, br].forEach(e => { e.style.color = ink; e.style.opacity = a; });
      root.style.opacity = E(t, 0.1, 0.8, ease.outCubic) * (1 - E(t, DUR - 0.8, DUR - 0.2, ease.inOutCubic));
    },
  };
})();

const GRAIN = (() => {
  const cv = document.getElementById('grain'); cv.width = W / 2; cv.height = H / 2;
  const g = cv.getContext('2d');
  const img = g.createImageData(cv.width, cv.height);
  return {
    update(frame) {
      let seed = (frame * 2654435761) >>> 0;
      const d = img.data;
      for (let i = 0; i < d.length; i += 4) {
        seed ^= seed << 13; seed >>>= 0; seed ^= seed >>> 17; seed ^= seed << 5; seed >>>= 0;
        const v = seed & 255;
        d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255;
      }
      g.putImageData(img, 0, 0);
    },
  };
})();
