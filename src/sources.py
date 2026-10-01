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
import re
from typing import Any
from urllib.parse import urljoin

import requests

FR_API = "https://www.federalregister.gov/api/v1/documents.json"
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
        self._browser = self._pw.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
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

    def article(self, url: str) -> dict[str, str]:
        """본문 텍스트와 게시일 후보를 돌려줍니다."""
        page = self._ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)
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


def collect_listing(browser: Browser, key: str, cfg: dict[str, Any]) -> dict[str, Any]:
    """목록 페이지에서 패턴에 맞는 기사 링크를 뽑습니다."""
    pat = re.compile(cfg["link_pattern"])
    seen: dict[str, dict[str, Any]] = {}
    errors = []
    for list_url in cfg.get("list_urls", []):
        try:
            for link in browser.links(list_url):
                href = urljoin(list_url, link["href"]).split("#")[0]
                if not pat.search(href) or href in seen:
                    continue
                title = re.sub(r"\s+", " ", link["text"]).strip()
                if len(title) < 8:
                    continue
                seen[href] = {
                    "id": item_id(href),
                    "source": key,
                    "url": href,
                    "title": title,
                    "published": parse_date(link.get("time", "")) or parse_date(link.get("context", "")),
                }
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{list_url}: {exc}")
    items = list(seen.values())
    if cfg.get("max_items"):
        items = items[: cfg["max_items"]]
    return {"source": key, "error": "; ".join(errors) or None, "items": items}


# ---------------------------------------------------------------- Federal Register


def collect_federal_register(key: str, cfg: dict[str, Any], since: dt.date) -> dict[str, Any]:
    params: list[tuple[str, str]] = [
        ("conditions[publication_date][gte]", since.isoformat()),
        ("order", "newest"),
        ("per_page", "60"),
    ]
    if cfg.get("term"):
        params.append(("conditions[term]", cfg["term"]))
    for agency in cfg.get("agencies", []) or []:
        params.append(("conditions[agencies][]", agency))
    for t in cfg.get("types", []) or []:
        params.append(("conditions[type][]", t))
    for f in ("document_number", "title", "type", "subtype", "publication_date", "effective_on",
              "comments_close_on", "abstract", "html_url", "agencies", "raw_text_url"):
        params.append(("fields[]", f))
    try:
        res = requests.get(FR_API, params=params, timeout=30, headers={"User-Agent": UA})
        res.raise_for_status()
        docs = res.json().get("results", []) or []
    except Exception as exc:  # noqa: BLE001
        return {"source": key, "error": str(exc), "items": []}

    skip = tuple(cfg.get("skip_title_prefixes", []) or [])
    items = []
    for d in docs:
        title = (d.get("title") or "").strip()
        if not title or (skip and title.startswith(skip)):
            continue
        url = d.get("html_url")
        agencies = ", ".join(a.get("name", "") for a in (d.get("agencies") or []) if a.get("name"))
        body = "\n".join(
            x for x in [
                f"Document type: {d.get('type')} {d.get('subtype') or ''}".strip(),
                f"Agencies: {agencies}" if agencies else "",
                f"Publication date: {d.get('publication_date')}",
                f"Effective date: {d.get('effective_on')}" if d.get("effective_on") else "",
                f"Comments close: {d.get('comments_close_on')}" if d.get("comments_close_on") else "",
                "",
                d.get("abstract") or "",
            ] if x is not None
        )
        items.append({
            "id": item_id(url),
            "source": key,
            "url": url,
            "title": title,
            "published": d.get("publication_date"),
            "effective_on": d.get("effective_on"),
            "prefetched_text": body,
            "text_url": d.get("raw_text_url"),
        })
    return {"source": key, "error": None, "items": items}


def fetch_fr_text(url: str | None, limit: int = 14000) -> str:
    """Federal Register 원문 텍스트. 실패하면 빈 문자열."""
    if not url:
        return ""
    try:
        res = requests.get(url, timeout=30, headers={"User-Agent": UA})
        res.raise_for_status()
        text = re.sub(r"<[^>]+>", " ", res.text)
        return re.sub(r"[ \t]+", " ", text)[:limit]
    except Exception:  # noqa: BLE001
        return ""
