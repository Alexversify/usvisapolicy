(function(){
  // 목록 필터
  var list = document.querySelector('.list');
  if (list) {
    var state = {cat: 'all', src: 'all', hot: false, q: ''};
    try { var h = (location.hash || '').slice(1); if (h) state.cat = h; } catch(e) {}
    var cards = Array.prototype.slice.call(list.querySelectorAll('.card'));
    var none = document.getElementById('no-match');
    function apply(){
      var shown = 0, q = state.q.trim().toLowerCase();
      cards.forEach(function(c){
        var ok = (state.cat === 'all' || c.dataset.cat === state.cat)
          && (state.src === 'all' || c.dataset.src === state.src)
          && (!state.hot || c.dataset.imp === 'high')
          && (!q || c.dataset.q.indexOf(q) !== -1);
        c.hidden = !ok; if (ok) shown++;
      });
      if (none) none.hidden = shown !== 0;
    }
    var tabs = document.querySelectorAll('[data-filter-cat]');
    function setCat(v){
      state.cat = v;
      tabs.forEach(function(x){ x.setAttribute('aria-pressed', x.dataset.filterCat === v ? 'true' : 'false'); });
      try { history.replaceState(null, '', v === 'all' ? location.pathname : '#' + v); } catch(e) {}
      apply();
    }
    tabs.forEach(function(b){ b.addEventListener('click', function(){ setCat(b.dataset.filterCat); }); });
    var sel = document.querySelector('select[data-filter-src]');
    if (sel) sel.addEventListener('change', function(){ state.src = sel.value; apply(); });
    if (state.cat !== 'all') setCat(state.cat);
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
