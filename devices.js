// iPhone Duo stage: Apple's official bezels shown straight-on, a position picker, and a fade between them.
(() => {
  const DUO = [
    ['closed', 'Closed', 310, 'Closed, the outer screen runs your workout like any iPhone.'],
    ['open', 'Open', 620, 'Open, Home shows two columns: your week and shortcuts beside your saved timers and meals.'],
    ['upright', 'Upright', 450, 'Held upright, the timer sits on top with heart rate zones and today\'s exercises below.'],
    ['book', 'Book', 620, 'Half-folded like a book, the timer takes one page, heart rate zones and exercises the other.'],
    ['bench', 'On a bench', 600, 'Half-folded on a bench, the ring faces you and big controls lie flat under your hand.'],
  ];
  const q = new URLSearchParams(location.search);
  document.querySelectorAll('[data-duo-stage]').forEach(el => {
    el.classList.add('stage');
    el.innerHTML = `<div class="shots">${DUO.map(([k, l, w]) => `<div class="shot"><img class="fr" src="assets/framed/duo-${k}.webp" alt="HasGym on iPhone Duo, ${l.toLowerCase()}" style="width:${w}px"></div>`).join('')}</div>
      <div class="pkw"><div class="pk" role="group" aria-label="iPhone Duo position"><i class="gl"></i>${DUO.map(d => `<button type="button">${d[1]}<u></u></button>`).join('')}</div>
      <button type="button" class="pp" aria-label="Pause switching">❚❚</button></div><p class="cap"></p>`;
    const shots = [...el.querySelectorAll('.shot')], btns = [...el.querySelectorAll('.pk button')], gl = el.querySelector('.gl'),
      cap = el.querySelector('.cap'), pkw = el.querySelector('.pkw');
    let i = Math.max(0, DUO.findIndex(d => d[0] === q.get('pose'))), timer, paused = q.has('pose') || q.has('static');
    const show = n => { i = (n + DUO.length) % DUO.length;
      shots.forEach((s, j) => s.classList.toggle('on', j === i));
      btns.forEach((b, j) => { b.classList.toggle('on', j === i); b.setAttribute('aria-pressed', j === i); });
      gl.style.width = btns[i].offsetWidth + 'px'; gl.style.transform = `translateX(${btns[i].offsetLeft}px)`;
      cap.textContent = DUO[i][3]; };
    const run = () => { clearInterval(timer); pkw.classList.toggle('paused', paused); if (!paused) timer = setInterval(() => show(i + 1), 4000); };
    btns.forEach((b, j) => b.onclick = () => { show(j); run(); });
    el.querySelector('.pp').onclick = e => { paused = !paused; e.target.textContent = paused ? '▶' : '❚❚'; run(); };
    document.fonts.ready.then(() => { show(i); run(); });
  });
})();
