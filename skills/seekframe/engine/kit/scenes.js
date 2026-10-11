'use strict';
const VAR = { ink: 'var(--ink)', mute: 'var(--mute)', acc: 'var(--acc)', line: 'var(--line)', card: 'var(--card)', cardInk: 'var(--cardInk)', bg: 'var(--bg)' };
const monoT = (size, color, extra = {}) => Object.assign({ fontSize: size + 'px', letterSpacing: '0.14em', color: color || VAR.mute, whiteSpace: 'nowrap', fontFamily: 'var(--font-mono)' }, extra);

const ICON = {
  doc: `<rect x="14" y="8" width="36" height="48" rx="5" class="ik"/><path d="M22 22h20M22 31h20M22 40h12" class="ik"/>`,
  check: `<rect x="8" y="8" width="48" height="48" rx="10" class="ik"/><path d="M20 33l8 8 16-18" class="ia"/>`,
  person: `<circle cx="32" cy="22" r="11" class="ik"/><path d="M12 56c2-12 10-18 20-18s18 6 20 18" class="ik"/>`,
  shield: `<path d="M32 6 52 14v16c0 14-9 23-20 28C21 53 12 44 12 30V14z" class="ik"/><path d="M23 31l7 7 12-14" class="ia"/>`,
  clock: `<circle cx="32" cy="32" r="24" class="ik"/><path d="M32 18v14l10 6" class="ia"/>`,
  bolt: `<path d="M36 6 16 36h14l-4 22 22-32H34z" class="ia"/>`,
  eye: `<path d="M6 32s10-16 26-16 26 16 26 16-10 16-26 16S6 32 6 32z" class="ik"/><circle cx="32" cy="32" r="7" class="ia"/>`,
  stack: `<path d="M32 8 56 20 32 32 8 20z" class="ik"/><path d="M8 32l24 12 24-12M8 44l24 12 24-12" class="ia"/>`,
  chat: `<path d="M10 12h44v30H26l-12 10V42h-4z" class="ik"/><path d="M20 24h24M20 32h14" class="ia"/>`,
  key: `<circle cx="20" cy="32" r="10" class="ik"/><path d="M30 32h26M48 32v9M56 32v7" class="ik"/>`,
};
function icon(parent, name, size, x, y) {
  const s = sv('svg', { width: size, height: size, viewBox: '0 0 64 64' }, parent);
  s.innerHTML = ICON[name] || ICON.doc;
  css(s, { position: 'absolute', left: x + 'px', top: y + 'px' });
  return s;
}

defineScene('statement', (root, p, ctx) => {
  const items = p.items || ctx.lines.map(l => l.h || '');
  const center = p.align === 'center';
  const els = items.map(txt => {
    const size = p.size || (txt.length > 40 ? 84 : txt.length > 26 ? 104 : 128);
    const e = at(root, center ? 0 : 150, 0, '', '', { width: (center ? W : 1620) + 'px', textAlign: center ? 'center' : 'left', fontSize: size + 'px', fontWeight: 820, letterSpacing: '-0.035em', lineHeight: 1.03, color: VAR.ink, padding: center ? '0 140px' : '0' });
    return { e, ws: richWords(e, txt) };
  });
  let hs = null;
  const itemAt = (info, i) => (info.beats[i] != null ? info.beats[i] : info.beats[info.beats.length - 1] + (i - info.beats.length + 1) * (p.every || 0.9));
  return (lt, info) => {
    if (!hs) hs = els.map(x => x.e.offsetHeight);
    let k = 0;
    els.forEach((x, i) => { if (lt >= itemAt(info, i) - 0.05) k = i; });
    const gap = 28;
    const blockH = i1 => hs.slice(0, i1 + 1).reduce((a, b) => a + b, 0) + gap * i1;
    const topFor = i1 => (H - blockH(i1)) / 2 + 10;
    const tk = itemAt(info, k);
    els.forEach((x, i) => {
      const vis = i <= k;
      x.e.style.display = vis ? '' : 'none';
      if (!vis) return;
      const m = E(lt, tk, tk + 0.7, ease.inOutCubic);
      const top = k > 0 ? lerp(topFor(k - 1), topFor(k), m) : topFor(0);
      x.e.style.top = (top + hs.slice(0, i).reduce((a, b) => a + b, 0) + gap * i) + 'px';
      x.e.style.opacity = i < k ? lerp(1, p.dim != null ? p.dim : 0.32, E(lt, tk, tk + 0.6)) : 1;
      const st = Math.max(0.12, itemAt(info, i));
      x.ws.forEach((w, j) => {
        const q = E(lt, st + j * 0.06, st + 0.6 + j * 0.06, ease.outExpo);
        w.n.style.transform = `translateY(${(1 - q) * 110}%)`;
      });
    });
  };
}, { noTitle: true, sfx: s => (s.p.items || s.beats).map((_, i) => ({ t: Math.max(0.12, s.beats[i] != null ? s.beats[i] : s.beats[s.beats.length - 1] + (i - s.beats.length + 1) * (s.p.every || 0.9)), k: 'word', i })).concat(s.p.energy === 'drop' ? [{ t: 0.02, k: 'drop' }] : []) });

defineScene('slam', (root, p, ctx) => {
  const B = 60 / (ctx.video.bpm || 124);
  const word = p.words || ['ONE', 'BIG', 'IDEA'];
  const row = at(root, 0, 250, '', '', { width: W + 'px', display: 'flex', justifyContent: 'center', gap: '28px' });
  const fs = p.size || (word.join('').length > 8 ? 230 : 300);
  const ls = word.map(c => { const e = h('span', '', row, c); css(e, { display: 'inline-block', fontSize: fs + 'px', fontWeight: 900, lineHeight: 1, color: VAR.ink, letterSpacing: '-0.02em' }); return e; });
  const sub = at(root, 0, 720, 'mono', '', { width: W + 'px', textAlign: 'center', fontSize: '40px', letterSpacing: '0.42em', color: VAR.ink });
  const subTxt = (p.sub || '').toUpperCase();
  let fitted = false;
  return (lt, info) => {
    if (!fitted) { const w = row.scrollWidth; if (w > 1680) ls.forEach(e => (e.style.fontSize = Math.floor(fs * 1680 / w) + 'px')); fitted = true; }
    ls.forEach((e, i) => {
      const t0 = 0.02 + i * B, k = P(lt, t0, t0 + 0.12);
      const settle = lt > t0 + 0.12 ? 1 + 0.06 * Math.exp(-(lt - t0 - 0.12) * 12) * Math.sin((lt - t0) * 50) : 1;
      e.style.opacity = k > 0 ? 1 : 0;
      e.style.transform = `scale(${lerp(1.9, 1, ease.inQuart(k)) * settle}) rotate(${(1 - k) * (i % 2 ? 6 : -6)}deg)`;
      e.style.color = lt >= t0 && Math.exp(-Math.max(0, lt - t0) * 7) > 0.4 ? VAR.bg : VAR.ink;
    });
    const sb = info.beats[1] != null ? info.beats[1] : word.length * B + 0.2;
    sub.textContent = typed(subTxt, P(lt, sb, sb + 0.9));
  };
}, { noTitle: true, ground: 'red', sfx: s => { const B = 60 / ((window.VIDEO && window.VIDEO.bpm) || 124); return (s.p.words || ['ONE', 'BIG', 'IDEA']).map((w, i) => ({ t: 0.02 + i * B, k: 'slam' })); } });

defineScene('tiles', (root, p) => {
  const items = p.items || [], cols = p.cols || 3, rows = Math.ceil(items.length / cols);
  const GW = 1620, GAP = 24, tw = (GW - GAP * (cols - 1)) / cols, th = Math.min(270, (580 - GAP * (rows - 1)) / rows);
  const grid = at(root, 150, 320, '', '', { width: GW + 'px', height: (rows * th + GAP * (rows - 1)) + 'px', perspective: '1600px' });
  const tiles = items.map((it, i) => {
    const x = (i % cols) * (tw + GAP), y = Math.floor(i / cols) * (th + GAP);
    const t = at(grid, x, y, '', '', { width: tw + 'px', height: th + 'px', border: `1.5px ${it.planned ? 'dashed' : 'solid'} ${VAR.line}`, borderRadius: '20px', background: VAR.bg, transformOrigin: '50% 0', overflow: 'hidden' });
    const bar = at(t, 0, 0, '', '', { width: tw + 'px', height: '5px', background: VAR.acc, transformOrigin: '0 50%', transform: 'scaleX(0)' });
    icon(t, it.icon || 'check', 52, 28, 24);
    at(t, 28, 92, '', it.t, { fontSize: (it.t.length > 24 ? 28 : 33) + 'px', fontWeight: 760, color: VAR.ink, letterSpacing: '-0.015em', width: (tw - 56) + 'px', lineHeight: 1.12 });
    if (it.s) at(t, 28, th - 64, '', it.s, { fontSize: '20px', color: VAR.mute, width: (tw - 56) + 'px', lineHeight: 1.3 });
    if (it.planned) at(t, tw - 24, 24, 'mono', it.planned === true ? 'PLANNED' : it.planned, monoT(11, VAR.acc, { letterSpacing: '0.16em', border: `1.5px dashed ${VAR.acc}`, borderRadius: '5px', padding: '4px 8px', transform: 'translateX(-100%)' }));
    return { t, bar };
  });
  return (lt, info) => {
    const hl = p.hl ? p.hl[Math.min(info.beat, p.hl.length - 1)] || [] : null;
    const bt = info.beats[info.beat] || 0;
    tiles.forEach((o, i) => {
      const t0 = 0.2 + i * 0.13, q = spring(lt - t0, 2.3, 0.55);
      const on = hl ? hl.includes(i) : false;
      o.t.style.transform = `rotateX(${(1 - q) * -90}deg)`;
      o.bar.style.transform = `scaleX(${on ? E(lt, bt + 0.2, bt + 0.5) : 0})`;
      o.t.style.borderColor = on ? VAR.acc : VAR.line;
      o.t.style.opacity = (lt >= t0 ? 1 : 0) * (hl && hl.length && !on ? lerp(1, 0.45, E(lt, bt + 0.1, bt + 0.4)) : 1);
    });
  };
}, { sfx: s => (s.p.items || []).map((x, i) => ({ t: 0.2 + i * 0.13, k: 'flap' })).concat(s.beats.slice(1).map(b => ({ t: b + 0.2, k: 'blip' }))) });

defineScene('steps', (root, p, ctx) => {
  const st = p.steps || ['Plan', 'Build', 'Check', 'Ship'];
  const n = st.length, X0 = 230, X1 = 1690, Y = 600, dx = (X1 - X0) / Math.max(1, n - 1);
  const s = sv('svg', { width: W, height: H }, root); css(s, { position: 'absolute', left: 0, top: 0 });
  sv('line', { x1: X0, y1: Y, x2: X1, y2: Y, style: `stroke:${VAR.line};stroke-width:3` }, s);
  const run = sv('line', { x1: X0, y1: Y, x2: X0, y2: Y, style: `stroke:${VAR.acc};stroke-width:5;stroke-linecap:round` }, s);
  const nodes = st.map((label, i) => {
    const x = X0 + i * dx;
    const c = sv('circle', { cx: x, cy: Y, r: 26, style: `fill:${VAR.bg};stroke:${VAR.line};stroke-width:3` }, s);
    const tick = sv('path', { d: `M${x - 11} ${Y + 1}l7 7 15-16`, style: `fill:none;stroke:${VAR.bg};stroke-width:5;stroke-linecap:round;stroke-linejoin:round;opacity:0` }, s);
    const l = at(root, x, Y + 56, '', label, { transform: 'translateX(-50%)', fontSize: '34px', fontWeight: 760, color: VAR.ink, whiteSpace: 'nowrap', opacity: 0 });
    return { c, tick, l };
  });
  const at_ = j => (p.lit && info_.beats[p.lit[j]] != null ? info_.beats[p.lit[j]] + 0.45 : 0.9 + j * Math.max(0.55, (ctx.dur - 2.2) / Math.max(1, n - 1)));
  let info_ = null;
  return (lt, info) => {
    info_ = info;
    let reach = X0;
    nodes.forEach((o, j) => {
      const t0 = at_(j), q = E(lt, t0, t0 + 0.35, ease.outBackS);
      o.l.style.opacity = E(lt, t0 - 0.2, t0 + 0.2);
      o.c.style.fill = lt >= t0 ? VAR.acc : VAR.bg;
      o.c.style.stroke = lt >= t0 ? VAR.acc : VAR.line;
      o.c.setAttribute('r', 26 * (lt >= t0 ? lerp(0.7, 1, q) : 1));
      o.tick.style.opacity = lt >= t0 ? q : 0;
      if (lt >= t0) reach = X0 + j * dx;
    });
    run.setAttribute('x2', reach);
  };
}, { sfx: s => { const n = (s.p.steps || [0, 0, 0, 0]).length; return Array.from({ length: n }, (_, j) => ({ t: s.p.lit && s.beats[s.p.lit[j]] != null ? s.beats[s.p.lit[j]] + 0.45 : 0.9 + j * Math.max(0.55, (s.dur - 2.2) / Math.max(1, n - 1)), k: 'check', i: j })); } });

defineScene('compare', (root, p, ctx) => {
  const lanes = p.lanes || [{ label: 'The usual way', speed: 0.3 }, { label: 'With the product', speed: 1 }];
  const X0 = 520, X1 = 1680, top = 360, gap = 170;
  const els = lanes.map((ln, i) => {
    const y = top + i * gap;
    at(root, 150, y - 18, '', ln.label, { fontSize: '34px', fontWeight: 760, color: i === lanes.length - 1 ? VAR.acc : VAR.ink, whiteSpace: 'nowrap' });
    const track = at(root, X0, y, '', '', { width: (X1 - X0) + 'px', height: '10px', borderRadius: '5px', background: VAR.line });
    const bar = at(root, X0, y, '', '', { width: '0px', height: '10px', borderRadius: '5px', background: i === lanes.length - 1 ? VAR.acc : VAR.ink });
    const end = at(root, X1, y + 26, 'mono', (ln.end || '').toUpperCase(), monoT(15, VAR.mute, { transform: 'translateX(-100%)', opacity: 0 }));
    return { ln, bar, end, track };
  });
  at(root, X0, top + lanes.length * gap - 40, 'mono', (p.note || 'Illustration · not a measurement').toUpperCase(), monoT(13, VAR.mute, { letterSpacing: '0.16em' }));
  return lt => {
    els.forEach(o => {
      const q = clamp(E(lt, 0.5, 0.5 + 2.4 / o.ln.speed, ease.inOutCubic));
      o.bar.style.width = ((X1 - X0) * q) + 'px';
      o.end.style.opacity = E(lt, 0.5 + 2.4 / o.ln.speed, 0.8 + 2.4 / o.ln.speed);
    });
  };
}, { sfx: s => [{ t: 0.5, k: 'whoosh', d: 2.4 }, { t: 2.95, k: 'chime' }] });

defineScene('endcard', (root, p, ctx) => {
  const name = p.name || ctx.video.product || '';
  const wm = at(root, 0, 380, '', '', { width: W + 'px', textAlign: 'center', fontSize: '190px', fontWeight: 860, letterSpacing: '-0.04em', color: VAR.ink, lineHeight: 1 });
  const ws = richWords(wm, name);
  if (ws.length) h('span', '', ws[ws.length - 1].n, '.').style.color = 'var(--acc)';
  const a = at(root, 0, 640, '', p.a || '', { width: W + 'px', textAlign: 'center', fontSize: '54px', fontWeight: 700, color: VAR.ink, opacity: 0 });
  const b = at(root, 0, 712, '', p.b || '', { width: W + 'px', textAlign: 'center', fontSize: '54px', fontWeight: 700, color: VAR.acc, opacity: 0 });
  const url = at(root, 0, 860, 'mono', (p.url || ctx.video.site || '').toUpperCase(), monoT(20, VAR.mute, { width: W + 'px', textAlign: 'center', letterSpacing: '0.3em', opacity: 0 }));
  return lt => {
    ws.forEach((w, j) => { const q = E(lt, 0.3 + j * 0.08, 1.1 + j * 0.08); w.n.style.transform = `translateY(${(1 - q) * 110}%)`; });
    a.style.opacity = E(lt, 1.3, 1.7); a.style.transform = `translateY(${(1 - E(lt, 1.3, 1.9)) * 20}px)`;
    b.style.opacity = E(lt, 1.8, 2.2); b.style.transform = `translateY(${(1 - E(lt, 1.8, 2.4)) * 20}px)`;
    url.style.opacity = E(lt, 2.4, 2.9);
  };
}, { noTitle: true, sfx: () => [{ t: 0.3, k: 'swell', d: 0.6 }, { t: 0.9, k: 'impact' }, { t: 1.4, k: 'tagline' }] });
