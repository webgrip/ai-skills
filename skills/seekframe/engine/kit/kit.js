'use strict';
const KIT = { scenes: {}, noTitle: {}, ground: {}, note: {}, sfx: {} };
function defineScene(name, fn, opts = {}) {
  KIT.scenes[name] = fn;
  if (opts.noTitle) KIT.noTitle[name] = true;
  if (opts.ground) KIT.ground[name] = opts.ground;
  if (opts.note) KIT.note[name] = opts.note;
  if (opts.sfx) KIT.sfx[name] = opts.sfx;
}
const WPS = 2.45;
const TR = { wipe: 0.42, rise: 0.55, page: 0.62, zoom: 0.45, flap: 0.55, cut: 0.0 };
const TR_ORDER = ['wipe', 'rise', 'page', 'zoom', 'flap'];
const wordCount = s => s.trim().split(/\s+/).filter(Boolean).length;

function planVideo(V, timing) {
  const lines = V.lines.map((l, i) => Object.assign({ i }, l));
  const B = V.bpm ? 60 / V.bpm : 0;
  let t = B ? Math.ceil(0.6 / B) * B : 0.6;
  lines.forEach((l, i) => {
    let d = Math.max(l.min || 2.6, wordCount(l.vo) / WPS + (l.gap != null ? l.gap : 0.95));
    if (timing && timing[i]) d = Math.max(l.min || 2.2, timing[i].dur + (l.gap != null ? l.gap : 0.6));
    if (l.sc === 'endcard') d = Math.max(d, 5.5);
    if (l.beats) d = l.beats * B;
    else if (B) d = Math.ceil(d / (2 * B) - 1e-6) * 2 * B;
    l.t0 = t; l.dur = d; t += d;
  });
  const dur = +(t + 0.2).toFixed(2);
  const scenes = [];
  lines.forEach(l => {
    const last = scenes[scenes.length - 1];
    if (last && l.g && last.g === l.g) { last.lines.push(l); last.t1 = l.t0 + l.dur; return; }
    scenes.push({ g: l.g, type: l.sc, p: Object.assign({}, l.p || {}), lines: [l], t0: l.t0, t1: l.t0 + l.dur, tr: l.tr });
  });
  scenes.forEach((s, i) => {
    if (!KIT.scenes[s.type]) throw new Error(`unknown scene "${s.type}" in line ${s.lines[0].i + 1}`);
    s.i = i;
    s.planned = s.lines.some(l => l.planned);
    s.ground = s.p.ground || (s.planned ? 'paper' : (KIT.ground[s.type] || 'dark'));
    if (!s.p.note && KIT.note[s.type]) s.p.note = KIT.note[s.type];
    s.beats = s.lines.map(l => l.t0 - s.t0);
    s.dur = s.t1 - s.t0;
    if (i === 0) { s.t0 = 0; s.beats = s.lines.map(l => l.t0); s.dur = s.t1; }
  });
  let k = (V.seed || 0) % TR_ORDER.length;
  scenes.forEach((s, i) => {
    if (i === 0) { s.trType = 'cut'; return; }
    if (s.tr) { s.trType = s.tr; return; }
    if (s.type === 'endcard') { s.trType = 'zoom'; return; }
    let c = TR_ORDER[k % TR_ORDER.length]; k++;
    if (c === scenes[i - 1].trType) { c = TR_ORDER[k % TR_ORDER.length]; k++; }
    s.trType = c;
  });
  return { V, lines, scenes, dur };
}

function beatInfo(s, lt) {
  let b = 0;
  s.beats.forEach((t0, i) => { if (lt >= t0 - 0.05) b = i; });
  const t0 = s.beats[b], t1 = b + 1 < s.beats.length ? s.beats[b + 1] : s.dur;
  return { beat: b, bt: lt - t0, bdur: t1 - t0, beats: s.beats, dur: s.dur, n: s.beats.length };
}

function richWords(parent, text) {
  const out = [];
  let acc = false;
  text.split(' ').forEach((raw, i, arr) => {
    let w = raw;
    const open = w.startsWith('*'), close = w.endsWith('*');
    if (open) { acc = true; w = w.slice(1); }
    if (close) w = w.slice(0, -1);
    const o = h('span', 'wm', parent); const n = h('span', 'wi', o, w);
    if (acc) n.style.color = 'var(--acc)';
    out.push({ o, n });
    if (close) acc = false;
    if (i < arr.length - 1) parent.appendChild(document.createTextNode(' '));
  });
  return out;
}

function titleBlock(root, s, V) {
  const kick = at(root, 150, 108, 'mono', '', { fontSize: '15px', letterSpacing: '0.18em', color: 'var(--mute)', whiteSpace: 'nowrap' });
  const items = [];
  s.lines.forEach((l, i) => {
    const prev = items[items.length - 1];
    if (prev && prev.text === (l.h || '')) { prev.t1 = l.t0 - s.t0 + l.dur; return; }
    const hb = at(root, 146, 132, '', '', { fontSize: (s.p.hsize || 76) + 'px', fontWeight: 780, letterSpacing: '-0.028em', whiteSpace: 'nowrap', lineHeight: 1.1, color: 'var(--ink)' });
    items.push({ hb, ws: richWords(hb, l.h || ''), text: l.h || '', t0: i === 0 ? 0 : l.t0 - s.t0, t1: l.t0 - s.t0 + l.dur });
  });
  let fitted = false;
  const ktext = (s.p.k || V.kicker || '').toUpperCase();
  return lt => {
    if (!fitted) {
      items.forEach(it => { const w = it.hb.scrollWidth; if (w > 1640) it.hb.style.fontSize = Math.floor((s.p.hsize || 76) * 1640 / w) + 'px'; });
      fitted = true;
    }
    kick.textContent = scramble(ktext, P(lt, 0.05, 0.4), Math.floor((s.t0 + lt) * 30));
    items.forEach((it, i) => {
      const last = i === items.length - 1;
      const on = lt >= it.t0 - 0.05 && (last || lt < it.t1 + 0.3);
      it.hb.style.display = on ? '' : 'none';
      if (!on) return;
      const out = last ? 0 : E(lt, it.t1 - 0.05, it.t1 + 0.28, ease.inCubic);
      const st = it.t0 + (i === 0 ? 0.15 : 0.05);
      it.ws.forEach((w, j) => {
        const p = E(lt, st + j * 0.045, st + 0.55 + j * 0.045);
        w.n.style.transform = `translateY(${(1 - p) * 105 - out * 105}%)`;
      });
    });
  };
}

function plannedFrame(root, V) {
  const label = (V.txt && V.txt.planned) || 'PLANNED · NOT BUILT YET';
  const f = at(root, 34, 34, '', '', { width: (W - 68) + 'px', height: (H - 68) + 'px', border: '2px dashed var(--acc)', borderRadius: '18px', pointerEvents: 'none' });
  const l = at(root, W - 72, 74, 'mono', label, { fontSize: '13px', letterSpacing: '0.18em', color: 'var(--bg)', background: 'var(--acc)', padding: '7px 12px', borderRadius: '6px', transform: 'translateX(-100%)', whiteSpace: 'nowrap' });
  return lt => { const p = E(lt, 0.1, 0.5); f.style.opacity = p; l.style.opacity = p; };
}

const worldEl = document.getElementById('world');
let PLAN = null;

function makeInstance(s, V) {
  const root = h('div', 'scene g-' + s.ground, worldEl);
  root.style.background = 'var(--bg)';
  const cam = at(root, 0, 0, '', '', { width: W + 'px', height: H + 'px', transformOrigin: '50% 55%' });
  const upd = KIT.scenes[s.type](cam, s.p, { scene: s, lines: s.lines, video: V, dur: s.dur });
  const title = KIT.noTitle[s.type] ? null : titleBlock(root, s, V);
  const pf = s.planned ? plannedFrame(root, V) : null;
  const shade = h('div', 'shade', root); css(shade, { background: '#000' });
  return { root, cam, upd, title, pf, shade };
}

function buildVideo(V) {
  PLAN = planVideo(V, window.TIMING);
  DUR = PLAN.dur;
  PLAN.scenes.forEach(s => { s.inst = makeInstance(s, V); });
  PLAN.band = h('div', '', worldEl); css(PLAN.band, { position: 'absolute', inset: 0, display: 'none', zIndex: 50 });
  const secs = [], bots = [];
  PLAN.scenes.forEach(s => {
    const sec = s.p.sec || V.hud || '';
    const bot = s.planned ? ((V.txt && V.txt.plannedNote) || 'Planned · not built yet') : (s.p.note || V.note || '');
    if (!secs.length || secs[secs.length - 1][1] !== sec) secs.push([s.t0, sec]);
    if (!bots.length || bots[bots.length - 1][1] !== bot) bots.push([s.t0, bot]);
  });
  HUD.configure(secs, bots, V.site);
  PLAN.impacts = PLAN.scenes.filter(s => s.p.impact).map(s => s.t0 + (s.p.impact === true ? 0 : s.p.impact));
}

const TAN52 = Math.tan(52 * Math.PI / 180), SL52 = H / TAN52;
const wipePoly = x => `polygon(-10px -10px, ${x + SL52}px -10px, ${x}px ${H + 10}px, -10px ${H + 10}px)`;
const bandPoly = x => `polygon(${x - 150 + SL52}px -10px, ${x + SL52}px -10px, ${x}px ${H + 10}px, ${x - 150}px ${H + 10}px)`;
const BAND = { dark: '--brand-accent-on-dark', paper: '--brand-accent', red: '--brand-dark' };

function shakeAt(t) {
  let x = 0, y = 0, r = 0;
  PLAN.impacts.forEach(ti => {
    const d = t - ti; if (d < 0 || d > 0.5) return;
    const k = 4.5 * Math.exp(-d * 11);
    x += k * Math.sin(d * 97 + ti); y += k * Math.cos(d * 83 + ti * 2); r += k * 0.02 * Math.sin(d * 71);
  });
  return `translate(${x}px, ${y}px) rotate(${r}deg)`;
}

window.seek = function (t) {
  const S = PLAN.scenes;
  let top = S[0];
  S.forEach((s, i) => {
    const nx = S[i + 1];
    const end = nx ? nx.t0 + TR[nx.trType] : PLAN.dur + 1;
    const on = t >= s.t0 && t < end;
    const I = s.inst;
    I.root.style.display = on ? '' : 'none';
    css(I.root, { transform: '', clipPath: 'none', opacity: '', zIndex: i + 1, transformOrigin: '' });
    I.shade.style.opacity = 0;
    if (!on) return;
    top = s;
    const lt = t - s.t0;
    I.cam.style.transform = `scale(${1 + 0.018 * clamp(lt / Math.max(4, s.dur))})`;
    I.upd(lt, beatInfo(s, lt));
    if (I.title) I.title(lt);
    if (I.pf) I.pf(lt);
  });
  PLAN.band.style.display = 'none';
  S.forEach((s, i) => {
    if (i === 0) return;
    const d = TR[s.trType]; if (!d || t < s.t0 || t >= s.t0 + d) return;
    const prev = S[i - 1].inst, cur = s.inst;
    const e = ease.inOutCubic(P(t, s.t0, s.t0 + d));
    if (s.trType === 'wipe') {
      const x = lerp(-SL52 - 160, W + 20, e);
      cur.root.style.clipPath = wipePoly(x - 150);
      css(PLAN.band, { display: '', background: brandVar(BAND[s.ground]), clipPath: bandPoly(x) });
    } else if (s.trType === 'rise') {
      cur.root.style.transform = `translateY(${(1 - e) * 100}%)`;
      prev.root.style.transform = `scale(${1 - 0.06 * e})`; prev.shade.style.opacity = 0.45 * e;
    } else if (s.trType === 'zoom') {
      prev.root.style.transform = `scale(${1 + 0.14 * e})`; prev.root.style.opacity = 1 - e;
      cur.root.style.transform = `scale(${0.93 + 0.07 * e})`; cur.root.style.opacity = e;
      prev.root.style.zIndex = i + 2;
    } else if (s.trType === 'page') {
      prev.root.style.zIndex = i + 2;
      css(prev.root, { transformOrigin: '0 50%', transform: `perspective(2400px) rotateY(${-e * 96}deg)` });
      prev.shade.style.opacity = 0.55 * e; cur.shade.style.opacity = 0.35 * (1 - e);
    } else if (s.trType === 'flap') {
      prev.root.style.zIndex = i + 2;
      css(prev.root, { transformOrigin: '50% 0', transform: `perspective(2400px) rotateX(${e * 96}deg)` });
      prev.shade.style.opacity = 0.5 * e; cur.shade.style.opacity = 0.3 * (1 - e);
    }
  });
  worldEl.style.transform = shakeAt(t);
  const tone = top.ground === 'paper' ? 'light' : top.ground === 'red' ? 'red' : 'dark';
  HUD.update(t, tone);
  document.getElementById('vig').style.opacity = tone === 'dark' ? 1 : tone === 'red' ? 0.45 : 0;
  GRAIN.update(Math.floor(Math.round(t * FPS) / 2));
  document.getElementById('fade').style.opacity = E(t, PLAN.dur - 0.6, PLAN.dur - 0.05, ease.inOutCubic) + (1 - E(t, 0, 0.12));
};

window.CUES = function () {
  return {
    dur: PLAN.dur, style: PLAN.V.music || 'tech', id: PLAN.V.id, group: PLAN.V.group, bpm: PLAN.V.bpm || null,
    scenes: PLAN.scenes.map(s => ({ t0: s.t0, dur: s.dur, type: s.type, tr: s.trType, ground: s.ground, planned: s.planned, beats: s.beats.map(b => b + s.t0), energy: s.p.energy })),
    lines: PLAN.lines.map(l => ({ t0: l.t0, dur: l.dur, vo: l.vo, h: l.h })),
    sfx: PLAN.scenes.flatMap(s => (KIT.sfx[s.type] ? KIT.sfx[s.type](s) : []).filter(e => e.t >= 0 && e.t < s.dur + 0.6).map(e => Object.assign({}, e, { t: +(s.t0 + e.t).toFixed(3) }))),
  };
};
