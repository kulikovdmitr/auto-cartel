  const cur = {{ site.currency|tojson }};
  const sided = new Set({{ sided|tojson }});
  const fmt = n => n.toLocaleString('ru-RU');
  const boxes = [...document.querySelectorAll('input[name=panels]')];
  const bySlug = Object.fromEntries(boxes.map(b => [b.value, b]));
  const hint = document.getElementById('hint');
  let side = 'left';

  const slugOf = el => sided.has(el.dataset.base) ? el.dataset.base + '-' + side : el.dataset.base;

  function calc() {
    let sum = 0, min = 0;
    document.querySelectorAll('input[name=services]:checked, input[name=panels]:checked').forEach(i => {
      sum += +i.dataset.price; min += +i.dataset.hours;
    });
    document.getElementById('sum').textContent = sum ? 'от ' + fmt(sum) + ' ' + cur : '—';
    document.getElementById('time').textContent = min ? 'около ' + Math.max(0.5, Math.round(min / 30) / 2) + ' ч работы' : '';
  }

  function sync() {
    document.querySelectorAll('.panel').forEach(el => {
      const box = bySlug[slugOf(el)], on = !!(box && box.checked);
      el.classList.toggle('on', on);
      el.setAttribute('aria-pressed', on);
      el.setAttribute('aria-label', box.dataset.title);
    });
    const ul = document.getElementById('chosen');
    ul.replaceChildren();
    const picked = boxes.filter(b => b.checked);
    if (!picked.length) {
      const li = document.createElement('li');
      li.className = 'empty'; li.textContent = 'Нажмите на деталь кузова';
      ul.append(li);
    }
    picked.forEach(b => {
      const li = document.createElement('li');
      const t = document.createElement('span'); t.textContent = b.dataset.title;
      const p = document.createElement('span'); p.textContent = 'от ' + fmt(+b.dataset.price) + ' ' + cur;
      const x = document.createElement('button');
      x.type = 'button'; x.textContent = '×'; x.setAttribute('aria-label', 'Убрать: ' + b.dataset.title);
      x.onclick = () => { b.checked = false; sync(); };
      li.append(t, p, x); ul.append(li);
    });
    calc();
  }

  function show(view) {
    document.querySelectorAll('.tabs button').forEach(b => b.setAttribute('aria-pressed', b.dataset.view === view));
    document.getElementById('v-side').toggleAttribute('hidden', view === 'top');
    document.getElementById('v-top').toggleAttribute('hidden', view !== 'top');
    if (view !== 'top') {
      side = view;
      document.getElementById('sideg').setAttribute('transform', view === 'right' ? 'translate(800,0) scale(-1,1)' : '');
    }
    sync();
  }

  function toggle(el) { const b = bySlug[slugOf(el)]; b.checked = !b.checked; sync(); }

  document.addEventListener('change', e => { if (e.target.matches('input[name=panels]')) sync(); else calc(); });
  document.querySelectorAll('.tabs button').forEach(b => b.onclick = () => show(b.dataset.view));
  document.querySelectorAll('.panel').forEach(el => {
    el.onclick = () => toggle(el);
    el.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(el); } };
    el.onpointerenter = () => { const b = bySlug[slugOf(el)]; hint.textContent = b.dataset.title + ', от ' + fmt(+b.dataset.price) + ' ' + cur; };
    el.onpointerleave = () => { hint.textContent = ''; };
  });
  show('left');