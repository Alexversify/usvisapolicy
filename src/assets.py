"""공통 CSS와 JS. docs/assets/ 로 복사됩니다."""

CSS = r"""
:root{
  --ink:#13233a; --ink-2:#2b3d57; --muted:#5f6b7d; --faint:#8b95a5;
  --rule:#d9dfe7; --hair:#e9edf2; --ground:#f4f6f9; --paper:#ffffff;
  --accent:#1d4ed8; --hot:#b42318; --hot-bg:#fdecea; --chip:#eef2f7;
  --font: Pretendard, "Noto Sans KR", "Noto Sans JP", "Noto Sans SC", "PingFang SC", "Hiragino Sans", "Apple SD Gothic Neo", system-ui, -apple-system, "Segoe UI", sans-serif;
}
:root:not([data-theme="light"]){color-scheme:light dark}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ink:#e7ecf3; --ink-2:#c3cddb; --muted:#9aa6b8; --faint:#77839a;
    --rule:#2b3647; --hair:#222c3b; --ground:#0f1622; --paper:#151e2c;
    --accent:#7aa2ff; --hot:#ff8a80; --hot-bg:#3a1d1d; --chip:#1d2838;
  }
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--font);font-size:16px;line-height:1.65;word-break:keep-all;overflow-wrap:anywhere}
a{color:inherit}
.wrap{max-width:980px;margin:0 auto;padding:0 16px}
header.top{background:var(--paper);border-bottom:1px solid var(--rule)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:60px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:8px;text-decoration:none;font-weight:800;letter-spacing:-.02em;font-size:18px}
.brand svg{width:22px;height:22px;flex:none}
.langs{display:flex;gap:2px;flex-wrap:wrap}
.langs a{font-size:13px;text-decoration:none;color:var(--muted);padding:5px 9px;border-radius:999px}
.langs a:hover{background:var(--chip);color:var(--ink)}
.langs a[aria-current="true"]{background:var(--ink);color:var(--paper);font-weight:600}
.hero{padding:34px 0 18px}
.hero h1{font-size:clamp(24px,4.4vw,34px);line-height:1.25;letter-spacing:-.025em;margin:0 0 8px}
.hero p{margin:0;color:var(--muted);font-size:14px}
.bar{position:sticky;top:0;z-index:5;background:var(--ground);padding:10px 0 12px;border-bottom:1px solid var(--hair)}
.bar .row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.chip{border:1px solid var(--rule);background:var(--paper);color:var(--ink-2);font:inherit;font-size:13px;padding:6px 12px;border-radius:999px;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:var(--paper)}
.chip.hot[aria-pressed="true"]{background:var(--hot);border-color:var(--hot);color:#fff}
.search{flex:1 1 220px;min-width:0;border:1px solid var(--rule);background:var(--paper);color:var(--ink);font:inherit;font-size:14px;padding:8px 12px;border-radius:8px}
.list{list-style:none;margin:0;padding:8px 0 0}
.card{display:grid;grid-template-columns:92px 1fr;gap:16px;padding:20px 0;border-bottom:1px solid var(--hair)}
.card time{font-size:13px;color:var(--faint);font-variant-numeric:tabular-nums;padding-top:3px}
.card h2{font-size:18px;line-height:1.4;margin:4px 0 6px;letter-spacing:-.015em}
.card h2 a{text-decoration:none}
.card h2 a:hover{text-decoration:underline;text-underline-offset:3px}
.card p{margin:0;color:var(--ink-2);font-size:14.5px}
.meta{display:flex;gap:6px;flex-wrap:wrap;align-items:center;font-size:12px}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;background:var(--chip);color:var(--ink-2);font-weight:600}
.badge.hot{background:var(--hot-bg);color:var(--hot)}
.tag{color:var(--faint)}
.eff{font-size:12.5px;color:var(--muted);margin-top:6px}
.empty{padding:48px 0;color:var(--muted);text-align:center}
article.doc{background:var(--paper);border:1px solid var(--rule);border-radius:10px;padding:28px clamp(18px,4vw,40px);margin:24px 0}
article.doc h1{font-size:clamp(22px,3.8vw,30px);line-height:1.3;letter-spacing:-.02em;margin:10px 0 14px}
.facts{display:flex;gap:18px;flex-wrap:wrap;font-size:13.5px;color:var(--muted);padding-bottom:16px;border-bottom:1px solid var(--hair)}
.facts b{color:var(--ink);font-weight:600}
.lede{font-size:17px;line-height:1.7;margin:18px 0}
article.doc h2{font-size:15px;margin:26px 0 8px;color:var(--ink)}
article.doc ul{margin:0;padding-left:20px}
article.doc li{margin:6px 0}
.callout{background:var(--chip);border-radius:8px;padding:12px 14px;margin-top:8px}
.src{margin-top:26px;padding-top:16px;border-top:1px solid var(--hair);font-size:13.5px;color:var(--muted)}
.src a.btn{display:inline-block;margin-top:8px;padding:9px 14px;border:1px solid var(--ink);border-radius:8px;text-decoration:none;color:var(--ink);font-weight:600}
.note{font-size:12.5px;color:var(--faint);margin-top:12px}
.cta{display:block;text-align:center;background:var(--ink);color:var(--paper);text-decoration:none;font-weight:600;padding:13px;border-radius:8px;margin:18px 0 0}
.backlink{display:inline-block;margin-top:18px;font-size:14px;color:var(--muted);text-decoration:none}
footer{margin:48px 0 0;padding:22px 0 90px;border-top:1px solid var(--rule);color:var(--faint);font-size:12.5px}
footer p{margin:4px 0;max-width:72ch}
#fb-btn{position:fixed;right:16px;bottom:16px;z-index:20;background:var(--ink);color:var(--paper);border:0;border-radius:999px;padding:11px 16px;font:inherit;font-size:14px;font-weight:600;cursor:pointer;box-shadow:0 6px 20px rgba(0,0,0,.18)}
#fb-dlg{border:1px solid var(--rule);border-radius:12px;padding:0;width:min(440px,calc(100vw - 32px));background:var(--paper);color:var(--ink)}
#fb-dlg::backdrop{background:rgba(10,15,25,.45)}
#fb-dlg form{padding:20px;display:grid;gap:10px}
#fb-dlg h3{margin:0 0 4px;font-size:17px}
#fb-dlg label{font-size:13px;color:var(--muted);display:grid;gap:4px}
#fb-dlg select,#fb-dlg textarea,#fb-dlg input{font:inherit;font-size:14px;border:1px solid var(--rule);border-radius:8px;padding:9px 10px;background:var(--paper);color:var(--ink);width:100%}
#fb-dlg textarea{min-height:110px;resize:vertical}
#fb-dlg .acts{display:flex;gap:8px;justify-content:flex-end}
#fb-dlg button{font:inherit;font-size:14px;border-radius:8px;padding:9px 14px;cursor:pointer;border:1px solid var(--rule);background:var(--paper);color:var(--ink)}
#fb-dlg button[type=submit]{background:var(--ink);color:var(--paper);border-color:var(--ink);font-weight:600}
#fb-msg{font-size:13px;color:var(--muted);min-height:1em}
@media (max-width:600px){
  .card{grid-template-columns:1fr;gap:4px}
  .card h2{font-size:17px}
  header.top .wrap{padding-top:8px;padding-bottom:8px}
}
"""

JS = r"""
(function(){
  // 목록 필터
  var list = document.querySelector('.list');
  if (list) {
    var state = {src: 'all', hot: false, q: ''};
    var cards = Array.prototype.slice.call(list.querySelectorAll('.card'));
    var none = document.getElementById('no-match');
    function apply(){
      var shown = 0, q = state.q.trim().toLowerCase();
      cards.forEach(function(c){
        var ok = (state.src === 'all' || c.dataset.src === state.src)
          && (!state.hot || c.dataset.imp === 'high')
          && (!q || c.dataset.q.indexOf(q) !== -1);
        c.hidden = !ok; if (ok) shown++;
      });
      if (none) none.hidden = shown !== 0;
    }
    document.querySelectorAll('[data-filter-src]').forEach(function(b){
      b.addEventListener('click', function(){
        state.src = b.dataset.filterSrc;
        document.querySelectorAll('[data-filter-src]').forEach(function(x){ x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        apply();
      });
    });
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
"""

LOGO = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="3" width="20" height="18" rx="3" fill="currentColor"/>'
    '<path d="M6 8h12M6 12h8M6 16h10" stroke="var(--paper)" stroke-width="2" stroke-linecap="round"/></svg>'
)
