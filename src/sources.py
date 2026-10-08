"""소스별 수집.

원칙
1. USCIS와 travel.state.gov는 봇 차단이 있어 Playwright 실제 브라우저로 엽니다.
2. Federal Register는 공개 JSON API라 requests로 충분합니다.
3. 한 소스가 실패해도 나머지는 돌아야 합니다. 예외 대신 error 필드로 돌려줍니다.
4. 목록 단계에서는 제목, URL, 날짜만 잡고 본문은 새 글일 때만 엽니다.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import html as html_lib
import os
import re
from typing import Any
from urllib.parse import urljoin

import requests

FR_API = "https://www.federalregister.gov/api/v1/documents.json"
FR_PI_API = "https://www.federalregister.gov/api/v1/public-inspection-documents/current.json"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
)

MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December"
DATE_RE = re.compile(rf"\b({MONTHS})\.?\s+(\d{{1,2}}),\s+(20\d\d)\b")
ISO_RE = re.compile(r"\b(20\d\d)-(\d\d)-(\d\d)\b")
SLASH_RE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d\d)\b")


def item_id(url: str) -> str:
    return hashlib.sha1(url.split("#")[0].rstrip("/").encode()).hexdigest()[:12]


def parse_date(text: str) -> str | None:
    """영문 날짜 표기를 YYYY-MM-DD로. 못 찾으면 None."""
    if not text:
        return None
    m = ISO_RE.search(text)
    if m:
        return m.group(0)
    m = DATE_RE.search(text)
    if m:
        mon = m.group(1)[:3]
        try:
            d = dt.datetime.strptime(f"{mon} {m.group(2)} {m.group(3)}", "%b %d %Y").date()
            return d.isoformat()
        except ValueError:
            pass
    m = SLASH_RE.search(text)
    if m:
        try:
            return dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2))).isoformat()
        except ValueError:
            pass
    return None


# ---------------------------------------------------------------- 브라우저


class Browser:
    """Playwright 브라우저를 한 번만 띄워 여러 페이지에 재사용합니다."""

    def __enter__(self) -> "Browser":
        from playwright.sync_api import sync_playwright

        self._pw = sync_playwright().start()
        # travel.state.gov는 headless 브라우저를 막습니다. HEADFUL=1 이면 xvfb 위에서 일반 창으로 엽니다.
        headless = os.environ.get("HEADFUL") != "1"
        self._browser = self._pw.chromium.launch(headless=headless, args=["--disable-blink-features=AutomationControlled"])
        self._ctx = self._browser.new_context(user_agent=UA, locale="en-US", viewport={"width": 1400, "height": 1000})
        return self

    def __exit__(self, *exc: Any) -> None:
        try:
            self._ctx.close()
            self._browser.close()
        finally:
            self._pw.stop()

    def links(self, url: str) -> list[dict[str, str]]:
        """페이지의 모든 링크와, 링크를 감싼 블록의 텍스트(날짜 추출용)를 돌려줍니다."""
        page = self._ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2500)
            self._settle(page)
            return page.evaluate(
                """() => Array.from(document.querySelectorAll('a[href]')).map(a => {
                    let box = a.closest('li, article, tr, .views-row, .usa-collection__item') || a.parentElement;
                    let t = a.closest('li, article, tr, .views-row, .usa-collection__item');
                    let time = (t && t.querySelector('time')) ? (t.querySelector('time').getAttribute('datetime') || t.querySelector('time').innerText) : '';
                    return {href: a.href, text: (a.innerText || '').trim(), context: ((box && box.innerText) || '').slice(0, 400), time: time || ''};
                })"""
            )
        finally:
            page.close()

    @staticmethod
    def _settle(page: Any, limit_ms: int = 25000) -> None:
        """대기 화면("Just a moment...")이 뜨면 일반 브라우저처럼 실제 페이지로 넘어갈 때까지 기다립니다.
        대기 화면을 푸는 조작은 하지 않습니다. 시간이 지나도 그대로면 그대로 돌려주고, 수집 실패로 기록됩니다."""
        waited = 0
        while waited < limit_ms:
            try:
                title = (page.title() or "").lower()
                links = page.evaluate("document.querySelectorAll('a[href]').length")
            except Exception:  # noqa: BLE001  페이지 전환 중
                title, links = "just a moment", 0
            if "just a moment" not in title and "attention required" not in title and links > 5:
                return
            page.wait_for_timeout(2500)
            waited += 2500

    def article(self, url: str) -> dict[str, str]:
        """본문 텍스트와 게시일 후보를 돌려줍니다."""
        page = self._ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)
            self._settle(page)
            data = page.evaluate(
                """() => {
                    const pick = s => document.querySelector(s);
                    const main = pick('main') || pick('article') || pick('#main-content') || pick('.tsg-rwd-main-copy-body-frame') || document.body;
                    const clone = main.cloneNode(true);
                    clone.querySelectorAll('nav, header, footer, script, style, .usa-breadcrumb, .breadcrumb, aside').forEach(n => n.remove());
                    const meta = n => (document.querySelector(`meta[property="${n}"], meta[name="${n}"]`) || {}).content || '';
                    const t = document.querySelector('time');
                    return {
                        title: (pick('h1') || {}).innerText || document.title,
                        text: clone.innerText,
                        date: meta('article:published_time') || meta('dcterms.date') || meta('date') || (t ? (t.getAttribute('datetime') || t.innerText) : ''),
                    };
                }"""
            )
            data["text"] = re.sub(r"\n{3,}", "\n\n", data.get("text") or "").strip()
            return data
        finally:
            page.close()


# ---------------------------------------------------------------- 인터넷 아카이브 대체 경로
# travel.state.gov는 GitHub Actions 같은 데이터센터 IP에 Cloudflare 확인 화면만 돌려줍니다.
# 확인 화면을 통과시키는 조작은 하지 않고, 같은 공개 페이지의 인터넷 아카이브(web.archive.org)
# 최신 사본을 읽습니다. 기사에는 원래 주소(travel.state.gov)를 그대로 링크합니다.

ARCHIVE_CDX = "https://web.archive.org/cdx/search/cdx"
BLOCK_MARKS = ("just a moment", "cf-chl", "challenge-platform", "attention required", "cloudflare ray id")


def looks_blocked(text: str) -> bool:
    low = (text or "")[:4000].lower()
    return any(m in low for m in BLOCK_MARKS)


def archive_get(url: str, max_age_days: int = 60) -> tuple[str, str] | None:
    """(원본 HTML, 사본 시각 YYYYMMDDhhmmss). 최근 사본 중 확인 화면이 아닌 첫 번째. 없으면 None.
    실패 이유는 로그에 남깁니다."""
    now = dt.datetime.now(dt.timezone.utc)
    oldest = (now - dt.timedelta(days=max_age_days)).strftime("%Y%m%d%H%M%S")
    stamps: list[str] = []
    why = []
    # 1) available API: 가장 최근 사본 하나. 빠릅니다.
    try:
        r = requests.get("https://archive.org/wayback/available", params={"url": url, "timestamp": now.strftime("%Y%m%d%H%M%S")},
                         timeout=30, headers={"User-Agent": UA})
        snap = ((r.json() or {}).get("archived_snapshots") or {}).get("closest") or {}
        if snap.get("timestamp") and str(snap.get("status", "200")) == "200":
            stamps.append(snap["timestamp"])
        else:
            why.append(f"available: 사본 없음 ({r.status_code})")
    except Exception as exc:  # noqa: BLE001
        why.append(f"available: {type(exc).__name__}")
    # 2) CDX: 최근 사본 여러 개. 최신 사본이 확인 화면일 때를 대비합니다.
    try:
        r = requests.get(ARCHIVE_CDX, params={
            "url": url, "output": "json", "fl": "timestamp,statuscode",
            "filter": "statuscode:200", "limit": "-6",
        }, timeout=60, headers={"User-Agent": UA})
        r.raise_for_status()
        stamps += [row[0] for row in (r.json() or [])[1:] if row and str(row[0]).isdigit()]
    except Exception as exc:  # noqa: BLE001
        why.append(f"cdx: {type(exc).__name__}")
    for ts in sorted(set(stamps), reverse=True):
        if ts < oldest:
            why.append(f"최신 사본이 오래됨 ({ts[:8]})")
            break
        try:
            r = requests.get(f"https://web.archive.org/web/{ts}id_/{url}", timeout=60, headers={"User-Agent": UA})
        except Exception as exc:  # noqa: BLE001
            why.append(f"{ts[:8]}: {type(exc).__name__}")
            continue
        if r.status_code == 200 and not looks_blocked(r.text):
            return r.text, ts
        why.append(f"{ts[:8]}: {'확인 화면' if r.status_code == 200 else r.status_code}")
    print(f"    ! 아카이브 실패 {url}: {'; '.join(why) or '사본 없음'}")
    return None


def _strip(fragment: str) -> str:
    fragment = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", fragment)
    fragment = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|tr)>", "\n", fragment)
    text = html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))
    text = re.sub(r"[ \t\xa0]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def html_links(page: str, base: str) -> list[dict[str, str]]:
    """원본 HTML에서 링크, 링크 문구, 앞뒤 문맥(날짜 추출용)을 뽑습니다."""
    out = []
    for m in re.finditer(r'(?is)<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page):
        # 문맥은 링크를 감싼 항목(li, tr, p) 안에서만 봅니다. 옆 항목의 날짜를 가져오지 않게 합니다.
        lo = max(page.rfind(t, 0, m.start()) for t in ("<li", "<tr", "<p", "<article"))
        his = [i for i in (page.find(t, m.end()) for t in ("</li>", "</tr>", "</p>", "</article>")) if i != -1]
        lo = lo if lo != -1 and m.start() - lo < 1500 else m.start()
        hi = min(his) if his and min(his) - m.end() < 1500 else m.end()
        ctx = _strip(page[lo:hi])
        out.append({"href": urljoin(base, html_lib.unescape(m.group(1))), "text": _strip(m.group(2)), "context": ctx[:400], "time": ""})
    return out


def html_main_text(page: str) -> str:
    """원본 HTML의 본문 텍스트. 국무부 페이지는 본문 영역부터 읽어 메뉴 문구를 줄입니다."""
    page = re.sub(r"(?is)<(nav|header|footer)[^>]*>.*?</\1>", " ", page)
    for mark in ("tsg-rwd-main-copy-body-frame", "<main", 'id="main-content"', "<article"):
        i = page.find(mark)
        if i != -1:
            page = page[max(page.rfind("<", 0, i), 0) if not mark.startswith("<") else i:]
            break
    return _strip(page)


def collect_listing(browser: Browser, key: str, cfg: dict[str, Any]) -> dict[str, Any]:
    """목록 페이지에서 패턴에 맞는 기사 링크를 뽑습니다."""
    pat = re.compile(cfg["link_pattern"])
    # DHS처럼 이민 외 소식(재난, 사이버 등)이 섞인 목록은 제목 키워드로 먼저 거릅니다.
    title_pat = re.compile(cfg["title_pattern"], re.I) if cfg.get("title_pattern") else None
    seen: dict[str, dict[str, Any]] = {}
    errors = []
    for list_url in cfg.get("list_urls", []):
        try:
            links = browser.links(list_url) if browser is not None else []
            via = ""
            blocked = browser is None or len(links) < 5 or any("cloudflare.com" in l["href"] for l in links[:5])
            if blocked and cfg.get("archive_fallback"):
                got = archive_get(list_url, int(cfg.get("archive_max_age_days", 14)))
                if got:
                    links, via = html_links(got[0], list_url), f"archive {got[1]}"
                    print(f"    {key}: 차단되어 인터넷 아카이브 사본 사용 ({got[1][:8]})")
            before = len(seen)
            for link in links:
                href = urljoin(list_url, link["href"]).split("#")[0]
                if not pat.search(href) or href in seen:
                    continue
                title = re.sub(r"\s+", " ", link["text"]).strip()
                if len(title) < 8 or (title_pat and not title_pat.search(title)):
                    continue
                seen[href] = {
                    "id": item_id(href),
                    "source": key,
                    "url": href,
                    "title": title,
                    "published": parse_date(link.get("time", "")) or parse_date(link.get("context", "")),
                    "archive_fallback": bool(cfg.get("archive_fallback")),
                    "via": via,
                }
            if len(seen) == before and not title_pat:
                # 차단 페이지나 구조 변경을 로그로 드러냅니다.
                sample = [(l["href"], l["text"][:40]) for l in links][:3]
                errors.append(f"{list_url}: 일치 링크 0 (전체 링크 {len(links)}개, 예시 {sample})")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{list_url}: {exc}")
    items = list(seen.values())
    if cfg.get("max_items"):
        items = items[: cfg["max_items"]]
    return {"source": key, "error": "; ".join(errors) or None, "items": items}


# ---------------------------------------------------------------- USCIS Visa Bulletin 차트 공지

VB_RE = re.compile(rf"Visa Bulletin for ({MONTHS}) (20\d\d)", re.I)


def collect_uscis_vb_chart(browser: Browser, key: str, cfg: dict[str, Any]) -> dict[str, Any]:
    """USCIS 'Adjustment of Status Filing Charts from the Visa Bulletin' 페이지.
    travel.state.gov가 막혀도 매달 어떤 Visa Bulletin의 어느 차트를 쓰는지 여기서 확인됩니다.
    달마다 새 기사가 되도록 주소에 해당 월을 붙여 구분합니다."""
    url = cfg["url"]
    try:
        art = browser.article(url)
    except Exception as exc:  # noqa: BLE001
        return {"source": key, "error": f"{url}: {exc}", "items": []}
    text = art.get("text") or ""
    found = []
    for m in VB_RE.finditer(text):
        try:
            d = dt.datetime.strptime(f"{m.group(1)[:3]} 1 {m.group(2)}", "%b %d %Y").date()
        except ValueError:
            continue
        found.append(d)
    if not found:
        return {"source": key, "error": f"{url}: 'Visa Bulletin for <월> <연도>' 문구 없음 (구조 변경?)", "items": []}
    month = max(found)
    label = month.strftime("%B %Y")
    page_url = f"{url}?bulletin={month.strftime('%Y-%m')}"
    return {"source": key, "error": None, "items": [{
        "id": item_id(page_url),
        "source": key,
        "url": page_url,
        "title": f"Visa Bulletin for {label}: USCIS adjustment of status filing charts",
        "published": parse_date(art.get("date") or "") or None,
        "prefetched_text": (
            f"Source page: USCIS 'Adjustment of Status Filing Charts from the Visa Bulletin'. "
            f"Latest bulletin referenced on the page: Visa Bulletin for {label}. "
            "Summarize which chart (Final Action Dates or Dates for Filing) USCIS says to use for "
            "family-sponsored and employment-based adjustment of status filings for that month. "
            "Use only what the page states; do not invent priority dates.\n\n" + text[:14000]
        ),
    }]}


# ---------------------------------------------------------------- Federal Register


FR_DOC_RE = re.compile(r"/(\d{4}-\d{4,6})(?:/|$|\.)")


def fr_doc_number(url: str | None) -> str | None:
    """연방관보 URL에서 문서 번호(예: 2026-20660)를 뽑습니다. 공개열람본과 게재본이 같은 번호를 씁니다."""
    m = FR_DOC_RE.search(url or "")
    return m.group(1) if m else None


def _fr_item(key: str, d: dict[str, Any], skip: tuple[str, ...], stage: str) -> dict[str, Any] | None:
    title = (d.get("title") or "").strip()
    if not title or any(x.lower() in title.lower() for x in skip):
        return None
    url = d.get("html_url")
    agencies = ", ".join(a.get("name", "") for a in (d.get("agencies") or []) if a.get("name"))
    body = "\n".join(
        x for x in [
            stage,
            f"Document type: {d.get('type')} {d.get('subtype') or ''}".strip(),
            f"Document number: {d.get('document_number')}",
            f"Agencies: {agencies}" if agencies else "",
            f"Publication date: {d.get('publication_date')}" if d.get("publication_date") else "",
            f"Effective date: {d.get('effective_on')}" if d.get("effective_on") else "",
            f"Comments close: {d.get('comments_close_on')}" if d.get("comments_close_on") else "",
            "",
            d.get("abstract") or "",
        ] if x is not None
    )
    return {
        "id": item_id(url),
        "source": key,
        "url": url,
        "doc": d.get("document_number"),
        "title": title,
        "published": d.get("publication_date") if stage == "" else (d.get("filed_at") or "")[:10] or d.get("publication_date"),
        "effective_on": d.get("effective_on"),
        "prefetched_text": body.strip(),
        "text_url": d.get("raw_text_url"),
        "pdf_url": d.get("pdf_url"),
    }


def collect_federal_register(key: str, cfg: dict[str, Any], since: dt.date) -> dict[str, Any]:
    """게재된 연방관보 문서. 정보수집 공고가 많아 한 페이지만 보면 실제 규정이 밀려나므로 여러 페이지를 봅니다."""
    params: list[tuple[str, str]] = [
        ("conditions[publication_date][gte]", since.isoformat()),
        ("order", "newest"),
        ("per_page", "100"),
    ]
    if cfg.get("term"):
        params.append(("conditions[term]", cfg["term"]))
    for agency in cfg.get("agencies", []) or []:
        params.append(("conditions[agencies][]", agency))
    for t in cfg.get("types", []) or []:
        params.append(("conditions[type][]", t))
    for f in ("document_number", "title", "type", "subtype", "publication_date", "effective_on",
              "comments_close_on", "abstract", "html_url", "agencies", "raw_text_url", "pdf_url"):
        params.append(("fields[]", f))
    docs: list[dict[str, Any]] = []
    try:
        for page in range(1, int(cfg.get("max_pages", 5)) + 1):
            res = requests.get(FR_API, params=params + [("page", str(page))], timeout=30, headers={"User-Agent": UA})
            res.raise_for_status()
            data = res.json()
            docs.extend(data.get("results", []) or [])
            if page >= int(data.get("total_pages") or 1):
                break
    except Exception as exc:  # noqa: BLE001
        if not docs:
            return {"source": key, "error": str(exc), "items": []}
    skip = tuple(cfg.get("skip_title_prefixes", []) or [])
    items = [x for x in (_fr_item(key, d, skip, "") for d in docs) if x]
    return {"source": key, "error": None, "items": items}


def collect_public_inspection(key: str, cfg: dict[str, Any]) -> dict[str, Any]:
    """게재 전날 공개되는 공개열람 문서. 규정안이 발표되는 날 바로 잡기 위해 씁니다.
    기관과 제목 키워드로 거릅니다 (공개열람 API는 검색어 조건을 받지 않습니다)."""
    try:
        res = requests.get(FR_PI_API, timeout=30, headers={"User-Agent": UA})
        res.raise_for_status()
        docs = res.json().get("results", []) or []
    except Exception as exc:  # noqa: BLE001
        return {"source": key, "error": str(exc), "items": []}
    agencies = set(cfg.get("agencies", []) or [])
    types = {t.lower() for t in (cfg.get("types", []) or [])}
    words = re.compile(cfg.get("title_pattern") or ".", re.I)
    # 이민 전담 기관 문서는 제목과 상관없이 받습니다. 나머지(DHS 본부, CBP, 노동부 등)는 제목 키워드로 거릅니다.
    core = set(cfg.get("core_agencies", []) or [])
    skip = tuple(cfg.get("skip_title_prefixes", []) or [])
    items = []
    for d in docs:
        slugs = {a.get("slug") for a in (d.get("agencies") or [])}
        if agencies and not (slugs & agencies):
            continue
        if types and (d.get("type") or "").lower() not in types:
            continue
        ex = d.get("excerpts") or ""
        text = (d.get("title") or "") + " " + (" ".join(ex) if isinstance(ex, list) else str(ex))
        if not (slugs & core) and not words.search(text):
            continue
        it = _fr_item(key, d, skip, "Stage: filed for public inspection (scheduled for publication in the Federal Register)")
        if it:
            items.append(it)
    return {"source": key, "error": None, "items": items}


def fetch_fr_text(url: str | None, limit: int = 14000, pdf_url: str | None = None) -> str:
    """Federal Register 원문 텍스트. 텍스트본이 없으면(공개열람본) PDF에서 뽑습니다. 실패하면 빈 문자열."""
    if url:
        try:
            res = requests.get(url, timeout=30, headers={"User-Agent": UA})
            res.raise_for_status()
            text = re.sub(r"<[^>]+>", " ", res.text)
            text = re.sub(r"[ \t]+", " ", text)[:limit]
            if len(text.strip()) > 200:
                return text
        except Exception:  # noqa: BLE001
            pass
    if pdf_url:
        try:
            import io

            from pypdf import PdfReader

            res = requests.get(pdf_url, timeout=60, headers={"User-Agent": UA})
            res.raise_for_status()
            reader = PdfReader(io.BytesIO(res.content))
            out = []
            for pg in reader.pages[:12]:
                out.append(pg.extract_text() or "")
                if sum(len(x) for x in out) > limit:
                    break
            return re.sub(r"[ \t]+", " ", "\n".join(out))[:limit]
        except Exception:  # noqa: BLE001
            return ""
    return ""
