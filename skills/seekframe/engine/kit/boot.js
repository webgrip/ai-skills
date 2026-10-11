'use strict';
const loadScript = (src, optional) => new Promise((res, rej) => {
  const sc = document.createElement('script');
  sc.src = src; sc.onload = res; sc.onerror = optional ? res : () => rej(new Error('cannot load ' + src));
  document.head.appendChild(sc);
});
const loadStyle = href => new Promise(res => {
  const l = document.createElement('link');
  l.rel = 'stylesheet'; l.href = href; l.onload = res; l.onerror = res;
  document.head.appendChild(l);
});

window.READY = (async () => {
  const q = new URLSearchParams(location.search);
  const id = q.get('v'), project = 'file://' + q.get('p');
  await loadStyle(project + '/brand.css');
  await loadScript(project + '/scenes.js', true);
  await loadScript(project + '/videos/' + id + '.js');
  await loadScript(project + '/videos/' + id + '.timing.js', true);
  await document.fonts.ready;
  const fam = v => brandVar(v).split(',')[0].replace(/["']/g, '').trim();
  await Promise.all(['800 100px', '400 20px', '500 20px'].flatMap(w => [document.fonts.load(`${w} "${fam('--font-sans')}"`), document.fonts.load(`${w} "${fam('--font-mono')}"`)]));
  buildVideo(window.VIDEO);
  window.seek(0);
  return PLAN.dur;
})();
