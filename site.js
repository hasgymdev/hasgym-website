// HasGym website: live synced devices in the hero, sticky header section tracking.
(() => {
  if (location.search.includes('static')) document.documentElement.classList.add('no-anim');
  const ACTIVE = 20, REST = 10, SETS = 30, TOTAL = SETS * (ACTIVE + REST);
  const mmss = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  const icon = d => `<svg viewBox="0 0 24 24"><path d="${d}"/></svg>`;
  const controls = `<div class="lv-ct"><span>${icon('M11 6v12L3 12zM21 6v12l-8-6z')}</span><span class="p">${icon('M6 4h4.500v16H6zM13.500 4H18v16h-4.500z')}</span><span>${icon('M13 6v12l8-6zM3 6v12l8-6z')}</span></div>`;
  const ring = d => `<div class="lv-ring" style="width:${d}px;height:${d}px"><svg viewBox="0 0 100 100"><circle class="tr" cx="50" cy="50" r="46"/>
    <circle class="pr f-ring" cx="50" cy="50" r="46" stroke-dasharray="289" stroke-dashoffset="0"/></svg>
    <div class="lv-rc"><span class="lv-pill f-phase">ACTIVE</span><b class="f-time">0:20</b></div></div>`;
  const row = `<div class="lv-row"><span><b class="f-elapsed">0:00</b>/${mmss(TOTAL)}</span><span><b class="f-sets">0</b> / ${SETS} sets done</span></div><u class="lv-bar"><i class="f-bar"></i></u>`;
  const cards = `<div class="lv-cards"><div><p><span class="lv-heart">♥</span><b class="f-hr">128</b> bpm</p><em class="f-zone"><i></i><i></i><i></i><i></i><i></i></em></div>
    <div><p><b class="f-cal">0</b></p><small>ACTIVE CAL</small></div></div>`;
  const head = '<div class="lv-hd">INTERVAL<small>STRENGTH</small></div>';
  const sb = '<div class="sb"><b>9:41</b><svg viewBox="0 0 78 14"><rect x="0" y="9" width="3.5" height="5" rx="1"/><rect x="5.5" y="6" width="3.5" height="8" rx="1"/><rect x="11" y="3" width="3.5" height="11" rx="1"/><rect x="16.5" y="0" width="3.5" height="14" rx="1"/><path d="M34.5 2.2c3 0 5.7 1.2 7.7 3.1l-1.700 1.800a8.700 8.700 0 0 0-12 0l-1.700-1.800a11.200 11.200 0 0 1 7.700-3.100zm0 4.800c1.700 0 3.200.700 4.300 1.800l-1.800 1.800a3.600 3.600 0 0 0-5 0l-1.800-1.800A6.100 6.100 0 0 1 34.500 7zm0 4.200 1.700 1.800-1.700 1.700-1.700-1.700z"/><rect x="50" y="1" width="25" height="12" rx="3.8" opacity=".4"/><rect x="51.5" y="2.5" width="22" height="9" rx="2.4"/></svg></div>';

  const LIVE = {
    phone: `<div class="lv lv-phone">${sb}${head}<div class="lv-x">✕</div>${ring(292)}${row}${cards}
      <div class="lv-dots"><i class="on"></i><i></i><i></i></div>${controls}</div>`,
    watch: `<div class="lv lv-watch"><div class="lw-top"><b class="f-phase">ACTIVE</b><span>9:41</span></div>
      <div class="lw-big"><svg viewBox="0 0 184 56" preserveAspectRatio="none"><path class="tk" d="M92 2H170a12 12 0 0 1 12 12V42a12 12 0 0 1-12 12H14A12 12 0 0 1 2 42V14A12 12 0 0 1 14 2H92"/><path class="f-wtrack" d="M92 2H170a12 12 0 0 1 12 12V42a12 12 0 0 1-12 12H14A12 12 0 0 1 2 42V14A12 12 0 0 1 14 2H92" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/></svg><b class="f-time">0:20</b></div>
      <div class="lw-g"><div><b class="f-elapsed">0:00</b><small>ELAPSED</small></div><div><b class="f-setsof">0/${SETS}</b><small>SETS</small></div>
      <div><b class="f-left">${SETS}</b><small>SETS LEFT</small></div><div><b class="f-tleft">${mmss(TOTAL)}</b><small>TIME LEFT</small></div></div></div>`,
  };
  document.querySelectorAll('[data-live]').forEach(el => el.insertAdjacentHTML('afterbegin', LIVE[el.dataset.live]));

  const all = c => document.querySelectorAll('.' + c);
  const set = (c, v) => all(c).forEach(e => { if (e.textContent !== v) e.textContent = v; });
  const start = Date.now() - (+new URLSearchParams(location.search).get('t') || 0) * 1000;
  let hr = 126; let last = -1;
  function tick() {
    const el = Math.floor((Date.now() - start) / 1000) % TOTAL, inSet = el % (ACTIVE + REST), active = inSet < ACTIVE;
    const left = active ? ACTIVE - inSet : ACTIVE + REST - inSet, done = Math.floor(el / (ACTIVE + REST)) + (active ? 0 : 1);
    const frac = active ? inSet / ACTIVE : (inSet - ACTIVE) / REST;
    if (el !== last) {
      hr += active ? Math.max(0, (152 - hr) * .12) : -(hr - 118) * .14; hr += Math.sin(el * 1.7) * .8;
      const bpm = Math.round(hr), z = bpm < 132 ? 0 : bpm < 146 ? 1 : bpm < 159 ? 2 : bpm < 173 ? 3 : 4; last = el;
      document.querySelectorAll('.lv').forEach(e => e.dataset.phase = active ? 'active' : 'rest');
      set('f-phase', active ? 'ACTIVE' : 'REST'); set('f-time', mmss(left)); set('f-elapsed', mmss(el)); set('f-sets', String(done));
      set('f-setsof', `${done}/${SETS}`); set('f-left', String(SETS - done)); set('f-tleft', mmss(TOTAL - el));
      set('f-hr', String(Math.round(hr))); set('f-cal', String(Math.round(el * .13)));
      all('f-zone').forEach(e => [...e.children].forEach((i, n) => i.className = n <= z ? 'on z' + n : ''));
      all('f-bar').forEach(e => e.style.width = el / TOTAL * 100 + '%');
    }
    const smooth = ((Date.now() - start) / 1000 % (ACTIVE + REST));
    const f = active ? smooth / ACTIVE : (smooth - ACTIVE) / REST;
    all('f-ring').forEach(e => e.style.strokeDashoffset = 289 * (1 - Math.min(1, Math.max(0, f))));
    all('f-wtrack').forEach(e => { e.style.strokeDashoffset = 100 * (1 - Math.min(1, Math.max(0, f))); e.style.opacity = f > 0 ? 1 : 0; });
    requestAnimationFrame(tick);
  }
  if (document.querySelector('[data-live]')) tick();

  // Overview cards: three screens each. A tap shows the next one; left alone, they change every 10 seconds.
  document.querySelectorAll('.hg-oc').forEach(card => { const imgs = [...card.querySelectorAll('.hg-rot img')], dots = [...card.querySelectorAll('.hg-dots i')];
    let n = +new URLSearchParams(location.search).get('rot') || 0, timer;
    const show = () => { imgs.forEach((im, k) => im.classList.toggle('on', k === n % imgs.length)); dots.forEach((d, k) => d.classList.toggle('on', k === n % imgs.length)); };
    const auto = () => { clearInterval(timer); if (!location.search.includes('static')) timer = setInterval(() => { n++; show(); }, 10000); };
    card.addEventListener('click', () => { n++; show(); auto(); }); show(); auto(); });

  // Sticky header: move the highlight to the section in view.
  const links = [...document.querySelectorAll('.hg-nav a')], pill = document.querySelector('.hg-nav i');
  const secs = links.map(a => document.querySelector(a.getAttribute('href')));
  function spy() {
    const y = scrollY + innerHeight * .35; let n = -1;
    secs.forEach((s, i) => { if (s && s.offsetTop <= y) n = i; });
    links.forEach((a, i) => a.classList.toggle('on', i === n));
    if (pill) { if (n < 0) pill.style.opacity = 0; else { pill.style.opacity = 1; pill.style.width = links[n].offsetWidth + 'px'; pill.style.transform = `translateX(${links[n].offsetLeft}px)`; } }
    document.querySelector('.hg-top').classList.toggle('scrolled', scrollY > 8);
  }
  if (links.length) { addEventListener('scroll', spy, { passive: true }); addEventListener('resize', spy); document.fonts.ready.then(spy); spy(); }
})();
