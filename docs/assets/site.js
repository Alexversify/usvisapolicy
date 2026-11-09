(function(){
  // 목록 필터
  var list = document.querySelector('.list');
  if (list) {
    var state = {cat: 'all', agency: 'all', topic: '', hot: false, q: ''};
    try { var h = (location.hash || '').slice(1); if (h) state.cat = h; } catch(e) {}
    var cards = Array.prototype.slice.call(list.querySelectorAll('.card'));
    function qtext(c){ if (c._q == null) { var h = c.querySelector('h2'), p = c.querySelector('p'); c._q = ((h ? h.textContent : '') + ' ' + (p ? p.textContent : '') + ' ' + c.dataset.q).toLowerCase(); } return c._q; }
    var none = document.getElementById('no-match');
    // 페이지 나누기: 걸러진 글을 페이지당 개수만큼만 보여줍니다. 개수는 브라우저에 기억합니다.
    var pager = document.querySelector('.pager');
    var perSel = pager && pager.querySelector('[data-per-page]');
    var per = 10, page = 1, matched = [];
    try { var sv = parseInt(localStorage.getItem('uvp-per'), 10); if ([5, 10, 20].indexOf(sv) !== -1) per = sv; } catch(e) {}
    if (perSel) perSel.value = String(per);
    function show(scroll){
      var pages = Math.max(1, Math.ceil(matched.length / per));
      if (page > pages) page = pages;
      var a = (page - 1) * per, b = a + per;
      cards.forEach(function(c){ c.hidden = true; });
      matched.slice(a, b).forEach(function(c){ c.hidden = false; });
      if (!pager) return;
      pager.hidden = matched.length === 0;
      pager.querySelector('.pg-total').textContent = pager.dataset.total.replace('{n}', matched.length);
      var box = pager.querySelector('.pg-btns'); box.innerHTML = '';
      function btn(label, p, cur, dis){
        var x = document.createElement('button'); x.type = 'button'; x.className = 'pg'; x.textContent = label;
        if (cur) x.setAttribute('aria-current', 'page');
        if (dis) x.disabled = true; else x.addEventListener('click', function(){ page = p; show(true); });
        box.appendChild(x);
      }
      function gap(){ var g = document.createElement('span'); g.className = 'pg-gap'; g.textContent = '…'; box.appendChild(g); }
      if (pages > 1) {
        btn(pager.dataset.prev, page - 1, false, page === 1);
        var lo = Math.max(1, page - 2), hi = Math.min(pages, page + 2);
        if (lo > 1) { btn('1', 1); if (lo > 2) gap(); }
        for (var i = lo; i <= hi; i++) btn(String(i), i, i === page);
        if (hi < pages) { if (hi < pages - 1) gap(); btn(String(pages), pages); }
        btn(pager.dataset.next, page + 1, false, page === pages);
      }
      if (scroll) {
        // 고정 필터 막대 높이만큼 띄워 목록 첫 글이 가려지지 않게 올립니다.
        var bar = document.querySelector('.bar'), off = bar ? bar.getBoundingClientRect().height : 0;
        window.scrollTo({top: list.getBoundingClientRect().top + window.pageYOffset - off - 8, behavior: 'smooth'});
      }
    }
    if (perSel) perSel.addEventListener('change', function(){
      per = parseInt(perSel.value, 10) || 10; page = 1;
      try { localStorage.setItem('uvp-per', String(per)); } catch(e) {}
      show(false);
    });
    function apply(){
      var q = state.q.trim().toLowerCase();
      matched = cards.filter(function(c){
        return (state.cat === 'all' || c.dataset.cat === state.cat)
          && (state.agency === 'all' || c.dataset.agency === state.agency)
          && (!state.topic || c.dataset.topics.indexOf(' ' + state.topic + ' ') !== -1)
          && (!state.hot || c.dataset.imp === 'high')
          && (!q || qtext(c).indexOf(q) !== -1);
      });
      if (none) none.hidden = matched.length !== 0;
      page = 1;
      show(false);
    }
    var tabs = document.querySelectorAll('[data-filter-cat]');
    function setCat(v){
      state.cat = v;
      tabs.forEach(function(x){ x.setAttribute('aria-pressed', x.dataset.filterCat === v ? 'true' : 'false'); });
      try { history.replaceState(null, '', v === 'all' ? location.pathname : '#' + v); } catch(e) {}
      apply();
    }
    tabs.forEach(function(b){ b.addEventListener('click', function(){ setCat(b.dataset.filterCat); }); });
    var sel = document.querySelector('select[data-filter-agency]');
    if (sel) sel.addEventListener('change', function(){ state.agency = sel.value; apply(); });
    // 주요 이슈 타일: 누르면 그 주제만, 다시 누르거나 해제 칩을 누르면 전체.
    var tiles = document.querySelectorAll('[data-filter-topic]');
    var clearBtn = document.querySelector('[data-clear-topic]');
    function setTopic(v, label){
      state.topic = v;
      tiles.forEach(function(x){ x.setAttribute('aria-pressed', x.dataset.filterTopic === v ? 'true' : 'false'); });
      if (clearBtn) { clearBtn.hidden = !v; clearBtn.textContent = v ? label + ' ✕' : ''; }
      apply();
      if (v) { var b = document.querySelector('.bar'); if (b) b.scrollIntoView({behavior: 'smooth', block: 'start'}); }
    }
    tiles.forEach(function(b){ b.addEventListener('click', function(){
      var v = b.dataset.filterTopic;
      setTopic(state.topic === v ? '' : v, b.querySelector('b').textContent);
    }); });
    if (clearBtn) clearBtn.addEventListener('click', function(){ setTopic('', ''); });
    var more = document.querySelector('[data-more-topics]');
    if (more) more.addEventListener('click', function(){ more.closest('.issues').classList.add('open'); });
    if (state.cat !== 'all') setCat(state.cat); else apply();
    // 뒤로가기 등으로 주소의 #분류가 바뀌면 탭도 따라갑니다.
    window.addEventListener('hashchange', function(){ var v = (location.hash || '').slice(1) || 'all'; if (v !== state.cat) setCat(v); });
    var hot = document.querySelector('[data-filter-hot]');
    if (hot) hot.addEventListener('click', function(){ state.hot = !state.hot; hot.setAttribute('aria-pressed', String(state.hot)); apply(); });
    var s = document.querySelector('.search');
    if (s) s.addEventListener('input', function(){ state.q = s.value; apply(); });
  }

  // 언어 선택 기억
  document.querySelectorAll('.langs a').forEach(function(a){
    a.addEventListener('click', function(){ try { localStorage.setItem('uvp-lang', a.dataset.lang); } catch(e){} });
  });

  // feedbal.com 피드백
  var cfg = document.body.dataset;
  var btn = document.getElementById('fb-btn'), dlg = document.getElementById('fb-dlg');
  if (!btn || !dlg) return;
  var form = dlg.querySelector('form'), msg = document.getElementById('fb-msg');
  btn.addEventListener('click', function(){
    msg.textContent = '';
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
  });
  dlg.querySelector('[data-close]').addEventListener('click', function(){ dlg.close ? dlg.close() : dlg.removeAttribute('open'); });
  function mailFallback(p){
    if (!cfg.fbMail) return;
    var body = '[' + p.type + '] ' + p.page_url + '\n\n' + p.message + (p.email ? '\n\nreply: ' + p.email : '');
    location.href = 'mailto:' + cfg.fbMail + '?subject=' + encodeURIComponent('[usvisapolicy] feedback') + '&body=' + encodeURIComponent(body);
  }
  form.addEventListener('submit', function(ev){
    ev.preventDefault();
    var f = new FormData(form);
    var p = {
      site_key: cfg.fbSite || '',
      type: f.get('type'),
      message: String(f.get('message') || '').trim(),
      email: String(f.get('email') || '').trim(),
      page_url: location.href,
      page_title: document.title,
      lang: document.documentElement.lang,
      article_id: cfg.article || '',
      user_agent: navigator.userAgent,
      created_at: new Date().toISOString()
    };
    if (!p.message) return;
    var sendBtn = form.querySelector('[type=submit]'); sendBtn.disabled = true;
    if (!cfg.fbEndpoint) { mailFallback(p); sendBtn.disabled = false; return; }
    // text/plain으로 보내야 CORS 프리플라이트가 생기지 않습니다.
    fetch(cfg.fbEndpoint, {method: 'POST', headers: {'Content-Type': 'text/plain;charset=UTF-8'}, body: JSON.stringify(p)})
      .then(function(r){ if (!r.ok) throw new Error(r.status); msg.textContent = cfg.fbOk; form.reset(); setTimeout(function(){ dlg.close && dlg.close(); }, 1400); })
      .catch(function(){ msg.textContent = cfg.fbFail; setTimeout(function(){ mailFallback(p); }, 600); })
      .finally(function(){ sendBtn.disabled = false; });
  });
})();
