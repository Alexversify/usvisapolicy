// usvisapolicy → feedbal 피드백 전송 (accdocu와 같은 방식)
// POST /feedback  사이트 피드백 버튼이 보낸 내용을 feedbal.com/api/intake 로 넘긴다.
// 사이트 키는 Cloudflare Pages 환경변수 FEEDBAL_KEY 에만 둔다. 브라우저에 노출하지 않는다.

const FEEDBAL_URL = 'https://feedbal.com/api/intake';
const SITE_ID = 'usvisapolicy';
const KIND = { translation: 'bug', content: 'bug', feature: 'idea', other: 'question' };
const LABEL = { translation: '번역 오류', content: '내용 오류', feature: '기능·디자인', other: '기타' };

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });
}

export async function onRequestPost({ request, env }) {
  if (!env.FEEDBAL_KEY) return json({ error: 'no_key' }, 503);

  let p = {};
  try { p = JSON.parse(await request.text()); } catch (_) { return json({ error: 'bad_json' }, 400); }

  const message = String(p.message || '').trim().slice(0, 4000);
  if (!message) return json({ error: 'empty' }, 400);
  const type = KIND[p.type] ? p.type : 'other';
  const lang = String(p.lang || '').slice(0, 10);
  const firstLine = message.split('\n')[0].slice(0, 80);

  const body = message + '\n\n' + [
    `- 유형: ${LABEL[type]}`,
    `- 언어: ${lang}`,
    p.article_id ? `- 기사 ID: ${String(p.article_id).slice(0, 20)} (data/articles/${String(p.article_id).slice(0, 20)}.json)` : '',
    p.page_title ? `- 페이지 제목: ${String(p.page_title).slice(0, 200)}` : '',
  ].filter(Boolean).join('\n');

  let res;
  try {
    res = await fetch(FEEDBAL_URL, {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-site-id': SITE_ID, 'x-site-key': env.FEEDBAL_KEY },
      body: JSON.stringify({
        kind: KIND[type],
        title: `[${lang || '-'}] ${LABEL[type]}: ${firstLine}`,
        body,
        reporter: String(p.email || '').slice(0, 300),
        page: String(p.page_url || '').slice(0, 300),
        ua: (request.headers.get('user-agent') || '').slice(0, 300),
      }),
    });
  } catch (_) {
    return json({ error: 'unreachable' }, 502);
  }
  if (!res.ok) return json({ error: 'rejected' }, 502);
  return json({ ok: true });
}

export function onRequest() {
  return json({ error: 'method' }, 405);
}
