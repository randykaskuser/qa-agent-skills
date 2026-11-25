// QA browser helpers.
// Paste the whole file into the browser's javascript_tool on the page under test.
// Reinstall after every navigation or reload (a reload also removes them).
(() => {
  if (window.__qa?.installed) return 'already';
  // logGet: set to a RegExp of GET routes worth logging for your project, e.g. /\/api\/config|\/s\//
  const qa = window.__qa = { reqs: [], fail: null, delay: null, logGet: /__never__/ };
  const of = qa.origFetch = window.fetch;
  const fmt = b => b instanceof FormData ? '[FormData:' + [...b.keys()].join(',') + ']' : b instanceof Blob ? `[Blob ${b.size}b ${b.type}]` : typeof b === 'string' ? b.slice(0, 800) : b;
  window.fetch = async function (input, init = {}) {
    const url = String(typeof input === 'string' ? input : input.url), method = (init.method || input.method || 'GET').toUpperCase();
    const e = { t: Date.now(), method, url: url.slice(0, 250), body: fmt(init.body) };
    if (method !== 'GET' || qa.logGet.test(url)) qa.reqs.push(e);
    if (qa.delay && qa.delay.re.test(url)) await new Promise(r => setTimeout(r, qa.delay.ms));   // slow-network race tests
    if (qa.fail && qa.fail.test(url)) { e.status = 'FORCED-FAIL'; throw new TypeError('QA forced failure'); } // error-path tests
    const r = await of.apply(this, arguments); e.status = r.status; return r;
  };
  const xo = XMLHttpRequest.prototype.open, xs = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (m, u) { this.__e = { t: Date.now(), method: m, url: String(u).slice(0, 250), xhr: true }; return xo.apply(this, arguments); };
  XMLHttpRequest.prototype.send = function (b) { const e = this.__e; e.body = fmt(b); qa.reqs.push(e); this.addEventListener('loadend', () => e.status = this.status); return xs.apply(this, arguments); };
  // Test image: any size/format; noise=true makes a large file (2400x1260 ≈ 8–10 MB PNG)
  qa.img = (w, h, name, { type = 'image/png', label = `${w}x${h}`, color = '#1d4ed8', noise = false } = {}) => new Promise(res => {
    const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d');
    if (noise) { const d = x.createImageData(w, h), u = new Uint32Array(d.data.buffer); for (let i = 0; i < u.length; i++) u[i] = (Math.random() * 0xffffffff) | 0xff000000; x.putImageData(d, 0, 0); }
    else { x.fillStyle = color; x.fillRect(0, 0, w, h); }
    x.fillStyle = '#fff'; x.font = `bold ${Math.max(14, Math.round(h / 8))}px sans-serif`; x.fillText(label, 20, Math.round(h / 2));
    c.toBlob(b => res(new File([b], name, { type })), type, 0.9);
  });
  qa.setFile = (input, file) => { const dt = new DataTransfer(); dt.items.add(file); input.files = dt.files; input.dispatchEvent(new Event('change', { bubbles: true })); };
  // Simulated paste of rich HTML (Google Docs/Word-like) into a contenteditable
  qa.paste = (el, html, text = '') => { const dt = new DataTransfer(); dt.setData('text/html', html); dt.setData('text/plain', text); const ev = new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true }); el.focus(); el.dispatchEvent(ev); return ev.defaultPrevented; };
  // og tags of a share page (same-origin fetch from a tab on that domain) + whether the image actually loads
  qa.og = async path => { const t = await fetch(path, { credentials: 'omit', cache: 'no-store' }).then(r => r.text()); const g = p => (t.match(new RegExp(`<meta (?:property|name)="${p}" content="([^"]+)"`)) || [])[1] ?? null;
    const img = g('og:image'); const loads = img ? await new Promise(r => { const i = new Image(); i.onload = () => r(`${i.naturalWidth}x${i.naturalHeight}`); i.onerror = () => r('ERROR'); i.src = img; }) : null;
    return { title: g('og:title'), image: img, loads, w: g('og:image:width'), h: g('og:image:height'), type: g('og:image:type'), signed: img ? /Signature=/.test(img) : null }; };
  // Capture short-lived toasts/messages: const stop = __qa.watch(); …action…; await wait; stop() → array of new text lines
  qa.watch = (re = /fail|error|success|saved|created|upload|invalid|required/i) => { const seen = new Set(), before = new Set(document.body.innerText.split('\n'));
    const mo = new MutationObserver(() => document.body.innerText.split('\n').forEach(l => { l = l.trim(); if (l && !before.has(l) && re.test(l)) seen.add(l.slice(0, 200)); }));
    mo.observe(document.body, { childList: true, subtree: true, characterData: true }); return () => { mo.disconnect(); return [...seen]; }; };
  qa.installed = true; return 'installed';
})();
