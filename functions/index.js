// 첫 주소(/)를 서버에서 바로 언어 페이지로 보냅니다.
// 예전에는 빈 화면에서 스크립트로 옮겼는데, 검색엔진·광고 심사 크롤러가 내용 없는 페이지로 볼 수 있어 바꿨습니다.
const LANGS = ["ko", "en", "es", "zh", "ja"];

export function onRequestGet({ request }) {
  const url = new URL(request.url);
  let lang = "";
  const m = (request.headers.get("Cookie") || "").match(/(?:^|;\s*)uvp-lang=([a-z]{2})/);
  if (m && LANGS.includes(m[1])) lang = m[1];
  if (!lang) {
    for (const part of (request.headers.get("Accept-Language") || "").split(",")) {
      const k = part.trim().slice(0, 2).toLowerCase();
      if (LANGS.includes(k)) { lang = k; break; }
    }
  }
  url.pathname = "/" + (lang || "en") + "/";
  return new Response(null, { status: 302, headers: { Location: url.toString(), "Cache-Control": "no-store", Vary: "Accept-Language, Cookie" } });
}
