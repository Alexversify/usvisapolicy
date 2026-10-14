// usvisapolicy 관리 페이지  /admin
// 사이트 메뉴에는 없고, 구글 로그인으로 허용된 계정만 들어옵니다.
// - 로그인: Google Identity Services 로 받은 ID 토큰을 구글 공개키로 검증하고, 허용 메일이면 7일짜리 세션 쿠키를 줍니다.
// - 세션 서명 키는 이미 있는 Pages 환경변수 FEEDBAL_KEY 에서 파생합니다 (새 비밀값 불필요).
// - 데이터: 저장소 data/ 의 runlog.json, status.json, index.json 과 GitHub Actions 실행 목록.

const CLIENT_ID = '951601838256-a95nn0c4r6r18nq9khdr5g3mtvjcb3i5.apps.googleusercontent.com';
const ALLOWED = ['ktw199482@gmail.com'];
const REPO = 'Alexversify/usvisapolicy';
const RAW = `https://raw.githubusercontent.com/${REPO}/main/data/`;
const COOKIE = 'uvp_admin';
const SESSION_DAYS = 7;

const SEC_HEADERS = {
  'x-robots-tag': 'noindex, nofollow',
  'cache-control': 'no-store',
  'referrer-policy': 'same-origin',
  'x-frame-options': 'DENY',
};

function json(data, status = 200, extra = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', ...SEC_HEADERS, ...extra },
  });
}
function page(body, status = 200) {
  return new Response(body, { status, headers: { 'content-type': 'text/html; charset=utf-8', ...SEC_HEADERS } });
}

// ---------- base64url
const enc = new TextEncoder();
function b64u(buf) {
  const s = btoa(String.fromCharCode(...new Uint8Array(buf)));
  return s.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
function unb64u(s) {
  s = s.replace(/-/g, '+').replace(/_/g, '/');
  while (s.length % 4) s += '=';
  const bin = atob(s);
  return Uint8Array.from(bin, (c) => c.charCodeAt(0));
}

// ---------- 세션
async function hmacKey(env) {
  const base = await crypto.subtle.importKey('raw', enc.encode(env.FEEDBAL_KEY), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const derived = await crypto.subtle.sign('HMAC', base, enc.encode('usvisapolicy-admin-session-v1'));
  return crypto.subtle.importKey('raw', derived, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign', 'verify']);
}
async function makeSession(env, email) {
  const payload = b64u(enc.encode(JSON.stringify({ e: email, x: Date.now() + SESSION_DAYS * 864e5 })));
  const sig = b64u(await crypto.subtle.sign('HMAC', await hmacKey(env), enc.encode(payload)));
  return `${payload}.${sig}`;
}
async function readSession(request, env) {
  const m = (request.headers.get('cookie') || '').match(new RegExp(`(?:^|;\\s*)${COOKIE}=([^;]+)`));
  if (!m) return null;
  const [payload, sig] = m[1].split('.');
  if (!payload || !sig) return null;
  try {
    const ok = await crypto.subtle.verify('HMAC', await hmacKey(env), unb64u(sig), enc.encode(payload));
    if (!ok) return null;
    const p = JSON.parse(new TextDecoder().decode(unb64u(payload)));
    if (!p.e || !ALLOWED.includes(p.e) || p.x < Date.now()) return null;
    return p.e;
  } catch (_) {
    return null;
  }
}
function cookie(value, maxAge) {
  return `${COOKIE}=${value}; Path=/admin; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;
}

// ---------- 구글 ID 토큰 검증
async function verifyGoogle(token) {
  const parts = String(token || '').split('.');
  if (parts.length !== 3) throw new Error('형식 오류');
  const header = JSON.parse(new TextDecoder().decode(unb64u(parts[0])));
  const claims = JSON.parse(new TextDecoder().decode(unb64u(parts[1])));
  const certs = await fetch('https://www.googleapis.com/oauth2/v3/certs', { cf: { cacheTtl: 3600 } }).then((r) => r.json());
  const jwk = (certs.keys || []).find((k) => k.kid === header.kid);
  if (!jwk || header.alg !== 'RS256') throw new Error('키 없음');
  const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
  const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, unb64u(parts[2]), enc.encode(`${parts[0]}.${parts[1]}`));
  if (!ok) throw new Error('서명 불일치');
  if (!['accounts.google.com', 'https://accounts.google.com'].includes(claims.iss)) throw new Error('발급자 불일치');
  if (claims.aud !== CLIENT_ID) throw new Error('클라이언트 불일치');
  if (!claims.exp || claims.exp * 1000 < Date.now()) throw new Error('만료');
  if (!claims.email_verified) throw new Error('메일 미인증');
  return String(claims.email).toLowerCase();
}

// ---------- 데이터
async function getJSON(url, headers = {}) {
  try {
    const r = await fetch(url, { headers: { 'user-agent': 'usvisapolicy-admin', ...headers }, cf: { cacheTtl: 60 } });
    if (!r.ok) return null;
    return await r.json();
  } catch (_) {
    return null;
  }
}
async function data() {
  const [runlog, status, index, runs] = await Promise.all([
    getJSON(RAW + 'runlog.json'),
    getJSON(RAW + 'status.json'),
    getJSON(RAW + 'index.json'),
    getJSON(`https://api.github.com/repos/${REPO}/actions/runs?per_page=20`, { accept: 'application/vnd.github+json' }),
  ]);
  return {
    runlog: Array.isArray(runlog) ? runlog : [],
    status: status || {},
    index: Array.isArray(index) ? index.map((r) => ({ id: r.id, source: r.source, published: r.published, added: r.added, category: r.category })) : [],
    runs: runs && Array.isArray(runs.workflow_runs)
      ? runs.workflow_runs.map((w) => ({ name: w.name, status: w.status, conclusion: w.conclusion, event: w.event, created: w.created_at, updated: w.updated_at, url: w.html_url }))
      : null,
  };
}

// ---------- 라우팅
export async function onRequest({ request, env }) {
  if (!env.FEEDBAL_KEY) return page('<p>관리 페이지 설정이 끝나지 않았습니다 (FEEDBAL_KEY 없음).</p>', 503);
  const url = new URL(request.url);
  const path = url.pathname.replace(/\/+$/, '') || '/admin';

  if (path === '/admin/login' && request.method === 'POST') {
    let body = {};
    try { body = await request.json(); } catch (_) { return json({ error: '요청 형식 오류' }, 400); }
    try {
      const email = await verifyGoogle(body.credential);
      if (!ALLOWED.includes(email)) return json({ error: `${email} 계정은 접근 권한이 없습니다.` }, 403);
      return json({ ok: true }, 200, { 'set-cookie': cookie(await makeSession(env, email), SESSION_DAYS * 86400) });
    } catch (e) {
      return json({ error: `로그인 확인 실패: ${e.message}` }, 401);
    }
  }
  if (path === '/admin/logout') {
    return new Response(null, { status: 302, headers: { location: '/admin', 'set-cookie': cookie('', 0), ...SEC_HEADERS } });
  }

  const who = await readSession(request, env);
  if (path === '/admin/api/data') {
    if (!who) return json({ error: 'login' }, 401);
    return json(await data());
  }
  if (path !== '/admin') return new Response('Not found', { status: 404, headers: SEC_HEADERS });
  return page(who ? DASH.replace('__WHO__', who) : LOGIN.replace(/__CLIENT_ID__/g, CLIENT_ID));
}

// ---------- 화면
const CSS = `
:root{--bg:#f7f7f5;--card:#fff;--fg:#1d1d1f;--mut:#6b6b70;--line:#e3e3e0;--acc:#1f5eff;--ok:#178a4a;--bad:#c4352b;--warn:#a76a00;--chip:#f0f0ec}
@media (prefers-color-scheme:dark){:root{--bg:#0f1218;--card:#171b23;--fg:#e8e9ec;--mut:#9aa0ab;--line:#2a303b;--acc:#7aa2ff;--ok:#4cc38a;--bad:#ff7b72;--warn:#e3b341;--chip:#222833}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Pretendard","Apple SD Gothic Neo","Noto Sans KR",sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:20px 16px 60px}
header{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:18px}
h1{font-size:20px;margin:0}h2{font-size:16px;margin:28px 0 10px}
.mut{color:var(--mut)}.ok{color:var(--ok)}.bad{color:var(--bad)}.warn{color:var(--warn)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.card .v{font-size:22px;font-weight:650;margin-top:2px}.card .k{font-size:12.5px;color:var(--mut)}
.tbl{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow-x:auto}
td:first-child{white-space:nowrap}
table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{font-weight:600;color:var(--mut);white-space:nowrap;background:var(--chip)}tr:last-child td{border-bottom:0}
td.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
.chip{display:inline-block;padding:1px 8px;border-radius:99px;background:var(--chip);font-size:12px;white-space:nowrap}
details summary{cursor:pointer}details ul{margin:6px 0 0;padding-left:18px}
.links{display:flex;flex-wrap:wrap;gap:8px}.links a{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:7px 12px}
.err{font-size:12.5px;color:var(--bad);word-break:break-all}
.toolbar{display:flex;gap:8px;align-items:center}button{font:inherit;padding:6px 12px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--fg);cursor:pointer}
.login{max-width:380px;margin:12vh auto;text-align:center}.login .card{padding:28px}
`;

const LOGIN = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>관리 | US Visa Policy</title><style>${CSS}</style>
<script src="https://accounts.google.com/gsi/client" async defer></script></head><body>
<div class="login"><div class="card"><h1>usvisapolicy 관리</h1><p class="mut">허용된 구글 계정으로 로그인하세요.</p>
<div id="g_id_onload" data-client_id="__CLIENT_ID__" data-callback="onGoogle" data-auto_prompt="false"></div>
<div style="display:flex;justify-content:center;margin-top:16px"><div class="g_id_signin" data-type="standard" data-theme="outline" data-size="large" data-text="signin_with" data-locale="ko"></div></div>
<p id="msg" class="err" style="margin-top:14px"></p></div></div>
<script>
async function onGoogle(r){const m=document.getElementById('msg');m.textContent='확인 중...';
 try{const x=await fetch('/admin/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({credential:r.credential})});
 const j=await x.json();if(x.ok){location.reload()}else{m.textContent=j.error||'로그인 실패'}}catch(e){m.textContent='네트워크 오류'}}
</script></body></html>`;

const DASH = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>관리 | US Visa Policy</title><style>${CSS}</style></head><body><div class="wrap">
<header><div><h1>usvisapolicy 관리</h1><div class="mut" id="sub">불러오는 중...</div></div>
<div class="toolbar"><button id="reload" type="button">새로고침</button><span class="mut">__WHO__</span><a href="/admin/logout">로그아웃</a></div></header>
<div class="cards" id="cards"></div>
<h2>실행 기록</h2><div class="tbl"><table><thead><tr><th>시각 (KST)</th><th>종류</th><th>새 글</th><th>전문 번역</th><th>비용</th><th>문제</th><th></th></tr></thead><tbody id="runlog"></tbody></table></div>
<h2>수집 소스 상태</h2><div class="tbl"><table><thead><tr><th>소스</th><th>상태</th><th class="n">목록 건수</th><th class="n">연속 실패</th><th>오류</th></tr></thead><tbody id="sources"></tbody></table></div>
<h2>GitHub 실행</h2><div class="tbl"><table><thead><tr><th>시작 (KST)</th><th>작업</th><th>결과</th><th class="n">걸린 시간</th><th></th></tr></thead><tbody id="runs"></tbody></table></div>
<h2>바로가기</h2><div class="links">
<a href="https://usvisapolicy.com/ko/" target="_blank" rel="noopener">사이트</a>
<a href="https://github.com/${REPO}/actions" target="_blank" rel="noopener">GitHub Actions</a>
<a href="https://github.com/${REPO}/commits/main" target="_blank" rel="noopener">커밋 기록</a>
<a href="https://feedbal.com" target="_blank" rel="noopener">feedbal (건의)</a>
<a href="https://console.anthropic.com/settings/usage" target="_blank" rel="noopener">Anthropic 사용량</a>
<a href="https://dash.cloudflare.com" target="_blank" rel="noopener">Cloudflare</a>
</div></div>
<script>
const SRC_NAME={uscis_news:'USCIS 뉴스',uscis_policy_manual:'USCIS Policy Manual',dos_visa_news:'국무부 비자 뉴스',visa_bulletin:'Visa Bulletin',uscis_vb_chart:'USCIS VB 차트',state_press:'국무부 보도자료',federal_register:'연방관보',fr_public_inspection:'연방관보 공개열람',dhs_news:'DHS 뉴스',presidential:'대통령령'};
const KIND={news:'정기 수집',backfill:'과거 글 채우기',manual:'수동 실행'};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const kst=t=>{if(!t)return'';const d=new Date(t);return d.toLocaleString('ko-KR',{timeZone:'Asia/Seoul',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false})};
const usd=v=>v==null?'-':'$'+Number(v).toFixed(2);
const sname=k=>SRC_NAME[k]||k;
function card(k,v,cls=''){return '<div class="card"><div class="k">'+esc(k)+'</div><div class="v '+cls+'">'+v+'</div></div>'}
async function load(){
 document.getElementById('sub').textContent='불러오는 중...';
 const r=await fetch('/admin/api/data',{cache:'no-store'});
 if(r.status===401){location.reload();return}
 const d=await r.json();const now=Date.now(),wk=7*864e5;
 const log=d.runlog||[];const st=d.status||{};const srcs=st.sources||{};
 const week=log.filter(x=>now-new Date(x.t)<wk);
 const added7=week.reduce((a,x)=>a+(x.added||[]).length,0);
 const cost7=week.reduce((a,x)=>a+(x.cost||0),0);
 const day=log.filter(x=>now-new Date(x.t)<864e5).reduce((a,x)=>a+(x.cost||0),0);
 const ftLeft=(log.find(x=>x.fulltext&&x.fulltext.left!=null)||{}).fulltext?.left;
 const bad=Object.entries(srcs).filter(([k,v])=>!v.ok);
 document.getElementById('sub').textContent='마지막 수집 '+(st.checked?kst(st.checked.replace(/Z$/,':00Z')):'-')+' · 기사 '+(d.index||[]).length+'건';
 document.getElementById('cards').innerHTML=
  card('전체 기사',(d.index||[]).length+'건')+
  card('최근 7일 새 글',added7+'건')+
  card('오늘(24시간) API 비용',usd(day))+
  card('최근 7일 API 비용',usd(cost7))+
  card('전문 번역 남은 기사',ftLeft==null?'-':ftLeft+'건')+
  card('문제 있는 소스',bad.length+'곳',bad.length?'warn':'ok');
 document.getElementById('runlog').innerHTML=log.length?log.slice(0,120).map(x=>{
  const a=x.added||[];const f=x.failed||[];const errs=Object.entries(x.errors||{});
  const list=a.length?'<details><summary>'+a.length+'건 (후보 '+(x.found??0)+')</summary><ul>'+a.map(i=>'<li><span class="chip">'+esc(sname(i.source))+'</span> <a href="/ko/news/'+esc(i.id)+'" target="_blank">'+esc(i.title)+'</a></li>').join('')+'</ul></details>':'<span class="mut">0건'+(x.found?' (후보 '+x.found+')':'')+'</span>';
  const ft=x.fulltext&&x.fulltext.done!=null?x.fulltext.done+'건 · 남음 '+x.fulltext.left:'-';
  const prob=[];if(x.limited)prob.push('<div class="warn">비용·사용량 한도 도달</div>');
  if(f.length)prob.push('<details><summary class="bad">번역 실패 '+f.length+'건</summary><ul>'+f.map(i=>'<li><a href="'+esc(i.url)+'" target="_blank" rel="noopener">'+esc(i.title)+'</a></li>').join('')+'</ul></details>');
  if(errs.length)prob.push('<details><summary class="mut">소스 오류 '+errs.length+'곳</summary><ul>'+errs.map(([k,v])=>'<li><b>'+esc(sname(k))+'</b> <span class="err">'+esc(v)+'</span></li>').join('')+'</ul></details>');
  return '<tr><td style="white-space:nowrap">'+kst(x.t)+'</td><td><span class="chip">'+esc(KIND[x.kind]||x.kind)+'</span></td><td>'+list+'</td><td style="white-space:nowrap">'+ft+'</td><td class="n">'+usd(x.cost)+'</td><td>'+(prob.join('')||'<span class="ok">없음</span>')+'</td><td>'+(x.run?'<a href="'+esc(x.run)+'" target="_blank" rel="noopener">로그</a>':'')+'</td></tr>'}).join('')
  :'<tr><td colspan="7" class="mut">실행 기록은 다음 실행부터 쌓입니다.</td></tr>';
 document.getElementById('sources').innerHTML=Object.entries(srcs).map(([k,v])=>'<tr><td>'+esc(sname(k))+'</td><td class="'+(v.ok?'ok':'bad')+'">'+(v.ok?'정상':'실패')+'</td><td class="n">'+(v.items??'-')+'</td><td class="n">'+(v.fail_streak||0)+'</td><td class="err">'+esc(v.error||'')+'</td></tr>').join('')||'<tr><td colspan="5" class="mut">없음</td></tr>';
 const runs=d.runs;
 document.getElementById('runs').innerHTML=runs==null?'<tr><td colspan="5" class="mut">GitHub 실행 목록을 불러오지 못했습니다. 바로가기의 GitHub Actions에서 확인하세요.</td></tr>':runs.map(w=>{
  const res=w.status!=='completed'?'<span class="warn">진행 중</span>':(w.conclusion==='success'?'<span class="ok">성공</span>':'<span class="bad">'+esc(w.conclusion)+'</span>');
  const mins=w.status==='completed'?Math.round((new Date(w.updated)-new Date(w.created))/6e4)+'분':'';
  return '<tr><td style="white-space:nowrap">'+kst(w.created)+'</td><td>'+esc(w.name)+'</td><td>'+res+'</td><td class="n">'+mins+'</td><td><a href="'+esc(w.url)+'" target="_blank" rel="noopener">보기</a></td></tr>'}).join('');
}
document.getElementById('reload').onclick=load;load();
</script></body></html>`;
