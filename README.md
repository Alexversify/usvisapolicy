# usvisapolicy.com

USCIS, 미 국무부, 연방관보, 대통령령의 이민 정책 업데이트를 하루 두 번 수집해
Claude가 한국어·영어·스페인어·중국어·일본어 기사로 요약·번역해 게시합니다.
피드백은 feedbal.com으로 받고, 승인한 피드백은 Claude가 코드나 번역을 고쳐 PR로 올립니다.

## 수집 대상

| 소스 | 방식 | 내용 |
|---|---|---|
| USCIS Newsroom (All News, Alerts) | Playwright | 보도자료, 정책 알림 |
| 국무부 travel.state.gov Visas News | Playwright | 비자 정책, 영사 업무 공지 |
| Visa Bulletin | Playwright | 최근 2개월 |
| Federal Register (USCIS, 국무부) | 공개 API | 규칙 제정, 공고. 정보수집 공고는 제외 |
| Federal Register 대통령 문서 | 공개 API | 비자·입국 관련 포고문, 행정명령 |

USCIS와 travel.state.gov는 봇 차단이 있어 requests로는 안 열립니다. visacal과 같이 실제 브라우저로 엽니다.

## 설치 (최초 1회, 약 15분)

1. GitHub에 `Alexversify/usvisapolicy` 저장소를 public으로 만들고 이 폴더를 올립니다.
   ```
   cd usvisapolicy
   git init -b main && git add . && git commit -m "init"
   gh repo create Alexversify/usvisapolicy --public --source . --push
   ```
2. **Anthropic API 키 등록.** console.anthropic.com에서 키를 하나 새로 만듭니다(이름 예: `usvisapolicy-github`).
   accdocu 키를 같이 써도 동작하지만, 키를 나눠야 사이트별 비용이 따로 보입니다.
   ```
   gh secret set ANTHROPIC_API_KEY -R Alexversify/usvisapolicy
   ```
   또는 저장소 폴더에서 `claude` 실행 후 `/install-github-app` (accdocu와 같은 방식, 시크릿 등록까지 자동).
3. **Actions 권한.** Settings > Actions > General > Workflow permissions에서
   `Read and write permissions`, `Allow GitHub Actions to create and approve pull requests` 둘 다 체크.
4. **Pages.** Settings > Pages > Source `Deploy from a branch`, 브랜치 `main`, 폴더 `/docs`.
   Custom domain `usvisapolicy.com`, Enforce HTTPS 체크.
5. **DNS (Cloudflare).** `@` A 레코드 4개 185.199.108.153 / 109.153 / 110.153 / 111.153,
   `www` CNAME `alexversify.github.io`. 프록시는 DNS only(회색 구름)로 둡니다.
6. Actions 탭 > `news` > Run workflow. 최근 45일치를 최대 15건씩 번역합니다. 몇 번 돌면 다 채워집니다.

Cloudflare Pages로 올리고 싶으면 저장소를 연결하고 빌드 명령 비움, 출력 디렉터리 `docs`로 두면 됩니다.

## feedbal.com 연동

### 1. 사이트 → feedbal.com (피드백 접수)

모든 페이지 우하단 `피드백` 버튼이 `config/site.yaml`의 `feedbal.endpoint`로 POST 합니다.
현재 값은 `https://feedbal.com/api/feedback`이며, feedbal.com의 실제 수신 주소와 다르면 이 값만 바꾸면 됩니다.
feedbal.com이 자체 위젯 스크립트를 제공하면 `feedbal.widget_script`에 넣으면 자체 버튼 대신 그 위젯이 뜹니다.

요청 형식: `POST`, `Content-Type: text/plain`, 본문은 JSON 문자열.

```json
{
  "site_key": "usvisapolicy",
  "type": "translation | content | feature | other",
  "message": "중국어 제목이 원문과 다릅니다",
  "email": "user@example.com",
  "page_url": "https://usvisapolicy.com/zh/news/a1b2c3d4e5f6.html",
  "page_title": "...",
  "lang": "zh-Hans",
  "article_id": "a1b2c3d4e5f6",
  "user_agent": "...",
  "created_at": "2026-10-01T03:00:00.000Z"
}
```

text/plain인 이유: JSON으로 보내면 브라우저가 OPTIONS 프리플라이트를 먼저 보냅니다. feedbal.com 쪽 CORS 설정과 무관하게 동작하게 하려는 것입니다.
수신 서버는 `Access-Control-Allow-Origin: https://usvisapolicy.com`만 응답하면 됩니다. 실패 시 위젯은 메일 작성 화면으로 대체됩니다.

### 2. feedbal.com → GitHub (수정 요청)

feedbal.com에서 피드백을 검토하고 "개발 요청"을 누르면 아래 API를 호출하도록 연결합니다.

```
POST https://api.github.com/repos/Alexversify/usvisapolicy/dispatches
Authorization: Bearer <GitHub fine-grained token>
Accept: application/vnd.github+json

{
  "event_type": "feedbal",
  "client_payload": {
    "feedback_id": "1234",
    "type": "translation",
    "message": "사용자 피드백 원문",
    "page_url": "https://usvisapolicy.com/zh/news/a1b2c3d4e5f6.html",
    "lang": "zh-Hans",
    "article_id": "a1b2c3d4e5f6",
    "instruction": "관리자 추가 지시 (선택)"
  }
}
```

토큰은 GitHub > Settings > Developer settings > Fine-grained tokens에서 이 저장소만 선택하고
`Contents: Read and write` 권한 하나만 줍니다. feedbal.com 서버 환경변수에만 둡니다.

`.github/workflows/claude.yml`이 받아서 Claude가 수정하고 `feedbal/<id>` 브랜치로 PR을 올립니다.
PR을 머지하면 Pages가 바로 반영합니다. 폰에서 GitHub 앱으로 머지해도 됩니다.

- 검토 없이 바로 반영하려면 저장소 Variables에 `FEEDBAL_AUTOMERGE=true`.
  피드백 원문은 외부인 입력이므로 처음에는 PR 검토를 권합니다.
- feedbal.com에 처리 결과를 돌려받으려면 Secrets에 `FEEDBAL_CALLBACK_URL`(필요하면 `FEEDBAL_CALLBACK_TOKEN`)을 넣습니다.
  `{site_key, feedback_id, status: pr_opened|no_change|failed, pr_url, run_url}`를 POST 합니다.

### 3. 직접 수정 (accdocu와 동일)

| 상황 | 방법 |
|---|---|
| 폰만 있다 | 저장소 이슈에 `@claude 일본어 목록 글자 크기 1pt 키워줘` |
| 새 컴퓨터 | `gh repo clone Alexversify/usvisapolicy && cd usvisapolicy && claude` |
| 데스크톱 앱 | 이 폴더를 연결하고 대화로 수정 |

`CLAUDE.md`에 구조와 규칙이 있어 설명 없이 바로 요청하면 됩니다.

## 운영 메모

- 번역 비용은 `settings.yaml`의 `max_new_per_run`(실행당 최대 건수)과 `model`로 조절합니다.
  하루 신규 공지는 보통 0~5건입니다.
- 번역이 실패한 글은 다음 실행에서 다시 시도합니다. 오래된 글(45일 초과)은 `data/seen.json`에 기록하고 건너뜁니다.
- 특정 기사를 다시 번역하려면 `data/index.json`에서 해당 항목과 `data/articles/<id>.json`을 지우고 `news`를 실행합니다.
- Actions 로그에 `uscis_news: ok (0건)`이 반복되면 USCIS 페이지 구조가 바뀐 것입니다. `settings.yaml`의 `link_pattern`을 점검합니다.
- 기사마다 원문 링크와 "AI 요약·번역, 법적 효력은 원문" 고지가 붙습니다. 하단 상담 버튼은 `site.yaml`의 `cta.consult_url`, 비면 alex@lawhanmi.com 메일로 연결됩니다.
- 광고, GA4는 `site.yaml` 값을 채우면 붙습니다. 비어 있으면 태그 자체가 출력되지 않습니다.
