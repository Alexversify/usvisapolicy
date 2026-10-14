"""원문 전문 보관과 전문 번역.

- 기사마다 공식 원문 전체를 문단 단위로 data/articles/<id>.json 의 "original" 에 보관합니다.
  원문 사이트가 글을 내리거나 주소를 바꿔도 이 사이트에서 전문을 볼 수 있습니다.
- 원문 문단 하나하나를 4개 언어(ko, es, zh, ja)로 빠짐없이 번역해 "full" 에 넣습니다.
  문단 수와 순서가 원문과 같아 화면에서 번역, 원문, 대조(나란히) 보기를 고를 수 있습니다.
- 요약(langs)은 그대로 두고, 그 아래에 전문을 붙입니다.

저장 형식
  "original": {"blocks": [{"t": "h|p|li|tr", "x": "..."}], "fetched": "...Z", "from": "page|federalregister.gov|pdf|archive", "chars": 1234}
  "full": {"ko": ["...", null, ...], "es": [...], ...}   # original.blocks 와 같은 순서. null 은 아직 번역 못 한 문단
"""

from __future__ import annotations

import datetime as dt
import html as html_lib
import io
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from typing import Any

import requests

from src import sources, store, translate
from src.i18n import HTML_LANG

LANG_NAMES = {
    "ko": "Korean",
    "es": "Spanish (neutral Latin American)",
    "zh": "Simplified Chinese",
    "ja": "Japanese",
}

# ---------------------------------------------------------------- 실행 시간 한도
# 한 실행이 워크플로 제한 시간을 넘겨 통째로 취소되지 않도록, 한도가 지나면 새 번역 요청을 멈추고
# 그때까지 한 것만 저장합니다. 남은 문단은 다음 실행이 이어서 합니다.
_START = time.time()


def past_deadline(cfg: dict[str, Any] | None = None) -> bool:
    m = os.environ.get("RUN_DEADLINE_MIN") or ((cfg or {}).get("fulltext") or {}).get("deadline_min") or 18
    return time.time() - _START > float(m) * 60


# ---------------------------------------------------------------- 원문을 문단으로

SKIP_TAGS = {"script", "style", "noscript", "nav", "header", "footer", "aside", "form", "button", "svg", "select", "iframe", "template"}
BLOCK_TAGS = {
    "p", "div", "section", "article", "li", "tr", "blockquote", "dd", "dt", "pre", "table", "ul", "ol",
    "figcaption", "caption", "h1", "h2", "h3", "h4", "h5", "h6", "main",
}
BOILER = re.compile(
    r"^(return to top|back to top|top of page|last reviewed/updated:?.*|share( this page)?|print|"
    r"was this page helpful\??.*|yes|no|related (links|content|topics)|topics|skip to main content|"
    r"an official website of the united states government|here'?s how you know|"
    r"official websites use \.gov.*|secure \.gov websites use https.*|\|)$",
    re.I,
)


class _Blocks(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[dict[str, str]] = []
        self.buf: list[str] = []
        self.kind = "p"
        self.skip = 0

    def _text(self) -> str:
        txt = re.sub(r"[ \t\r\f\v\xa0]+", " ", "".join(self.buf))
        txt = re.sub(r" *\n *", "\n", txt).strip(" \n|")
        return re.sub(r"\n{2,}", "\n", txt)

    def flush(self) -> None:
        txt = self._text()
        if txt:
            self.out.append({"t": self.kind, "x": txt})
        self.buf = []
        self.kind = "p"

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag in SKIP_TAGS:
            self.skip += 1
            return
        if self.skip:
            return
        if tag == "br":
            self.buf.append("\n")
            return
        if tag in ("td", "th"):
            if self._text():
                self.buf.append(" | ")
            return
        if tag in BLOCK_TAGS:
            kind = "h" if re.fullmatch(r"h[1-6]", tag) else "li" if tag == "li" else "tr" if tag == "tr" else "p"
            if self._text():
                self.flush()
                self.kind = kind
            elif kind != "p":
                self.kind = kind

    def handle_startendtag(self, tag: str, attrs: Any) -> None:
        if tag == "br" and not self.skip:
            self.buf.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_TAGS:
            if self.skip:
                self.skip -= 1
            return
        if self.skip:
            return
        if tag in BLOCK_TAGS:
            self.flush()

    def handle_data(self, data: str) -> None:
        if not self.skip:
            # 원본 HTML의 줄바꿈은 의미가 없습니다. 줄바꿈은 <br> 에서만 만듭니다.
            self.buf.append(re.sub(r"\s+", " ", data))


def html_to_blocks(page: str, title: str = "") -> list[dict[str, str]]:
    p = _Blocks()
    try:
        p.feed(page)
        p.close()
    except Exception:  # noqa: BLE001  깨진 HTML도 읽은 데까지는 씁니다
        pass
    p.flush()
    return clean_blocks(p.out, title)


def clean_blocks(blocks: list[dict[str, str]], title: str = "") -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    norm_title = re.sub(r"\W+", " ", title or "").strip().lower()
    for b in blocks:
        x = b["x"].strip()
        if not x or BOILER.match(x):
            continue
        if not out and norm_title and re.sub(r"\W+", " ", x).strip().lower() == norm_title:
            continue  # 제목은 화면 위쪽에 따로 있습니다
        if out and out[-1]["x"] == x:
            continue
        out.append({"t": b.get("t", "p"), "x": x})
    return out


def text_to_blocks(text: str) -> list[dict[str, str]]:
    """PDF처럼 줄 단위 텍스트를 문단으로 묶습니다."""
    paras: list[str] = []
    cur: list[str] = []

    def flush() -> None:
        if cur:
            paras.append(re.sub(r"\s+", " ", " ".join(cur)).strip())
            cur.clear()

    for line in (text or "").splitlines():
        s = line.strip()
        if not s:
            flush()
            continue
        if re.match(r"^(•|▪|-|•|\d{1,2}\.|\([a-z0-9ivx]{1,4}\))\s", s):
            flush()
        cur.append(s)
        if s.endswith((".", ":", "?", ";")) and len(s) < 75:
            flush()
    flush()
    bullet = re.compile(r"^(•|▪|-|\u2022)\s+")
    return clean_blocks([{"t": "li", "x": bullet.sub("", x)} if bullet.match(x) else {"t": "p", "x": x} for x in paras if x])


def _chars(blocks: list[dict[str, str]]) -> int:
    return sum(len(b["x"]) for b in blocks)


def _get(url: str, timeout: int = 60, **kw: Any) -> requests.Response:
    return requests.get(url, timeout=timeout, headers={"User-Agent": sources.UA}, **kw)


def _pdf_blocks(url: str, max_chars: int) -> list[dict[str, str]]:
    try:
        from pypdf import PdfReader

        r = _get(url, 90)
        r.raise_for_status()
        reader = PdfReader(io.BytesIO(r.content))
        parts: list[str] = []
        for pg in reader.pages:
            parts.append(pg.extract_text() or "")
            if sum(len(x) for x in parts) > max_chars * 1.2:
                break
        return text_to_blocks("\n".join(parts))
    except Exception as exc:  # noqa: BLE001
        print(f"    ! PDF 원문 실패: {type(exc).__name__}")
        return []


def _fr_original(num: str, max_chars: int) -> tuple[list[dict[str, str]], str]:
    """연방관보 문서 전문. 게재본은 HTML 전문, 공개열람본은 PDF."""
    try:
        r = _get(f"https://www.federalregister.gov/api/v1/documents/{num}.json", 30,
                 params=[("fields[]", "body_html_url"), ("fields[]", "pdf_url"), ("fields[]", "title")])
        if r.ok:
            d = r.json()
            if d.get("body_html_url"):
                h = _get(d["body_html_url"], 90)
                if h.ok:
                    blocks = html_to_blocks(h.text, d.get("title") or "")
                    if _chars(blocks) > 200:
                        return blocks, "federalregister.gov"
            if d.get("pdf_url"):
                blocks = _pdf_blocks(d["pdf_url"], max_chars)
                if blocks:
                    return blocks, "pdf"
    except Exception as exc:  # noqa: BLE001
        print(f"    ! 연방관보 원문 실패: {type(exc).__name__}")
    try:
        r = _get(f"https://www.federalregister.gov/api/v1/public-inspection-documents/{num}.json", 30)
        if r.ok and r.json().get("pdf_url"):
            blocks = _pdf_blocks(r.json()["pdf_url"], max_chars)
            if blocks:
                return blocks, "pi-pdf"
    except Exception as exc:  # noqa: BLE001
        print(f"    ! 공개열람 원문 실패: {type(exc).__name__}")
    return [], ""


def _browser_html(browser: Any, url: str) -> tuple[str, str]:
    """(제목, 본문 HTML). 메뉴·머리말·꼬리말은 빼고 본문 영역만."""
    page = browser._ctx.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)
        browser._settle(page)
        d = page.evaluate(
            """() => {
                const pick = s => document.querySelector(s);
                const main = pick('main') || pick('article') || pick('#main-content') || pick('.tsg-rwd-main-copy-body-frame') || document.body;
                const c = main.cloneNode(true);
                c.querySelectorAll('nav, header, footer, script, style, noscript, aside, form, button, svg, iframe, .usa-breadcrumb, .breadcrumb, [role=navigation], .usa-sidenav, .visually-hidden, .sr-only, .element-invisible').forEach(n => n.remove());
                return {title: ((pick('h1') || {}).innerText || document.title || '').trim(), html: c.innerHTML};
            }"""
        )
        return d.get("title") or "", d.get("html") or ""
    finally:
        page.close()


def _main_region(page: str) -> str:
    page = re.sub(r"(?is)<(nav|header|footer)[^>]*>.*?</\1>", " ", page)
    for mark in ("tsg-rwd-main-copy-body-frame", "<main", 'id="main-content"', "<article"):
        i = page.find(mark)
        if i != -1:
            return page[max(page.rfind("<", 0, i), 0) if not mark.startswith("<") else i:]
    return page


def fetch_original(a: dict[str, Any], browser: Any, item: dict[str, Any] | None, max_chars: int) -> dict[str, Any] | None:
    url = a["url"]
    title = a.get("original_title") or ""
    blocks: list[dict[str, str]] = []
    via = ""
    if "federalregister.gov" in url:
        num = (item or {}).get("doc") or sources.fr_doc_number(url)
        if num:
            blocks, via = _fr_original(num, max_chars)
    elif url.lower().split("?")[0].endswith(".pdf"):
        blocks, via = _pdf_blocks(url, max_chars), "pdf"
    else:
        page_url = url.split("?")[0] if a.get("source") == "uscis_vb_chart" else url
        if browser is not None:
            try:
                t, h = _browser_html(browser, page_url)
                blocks, via = html_to_blocks(h, t or title), "page"
            except Exception as exc:  # noqa: BLE001
                print(f"    ! 원문 페이지 실패: {type(exc).__name__}")
        joined = " ".join(b["x"] for b in blocks[:20])
        if _chars(blocks) < 200 or sources.looks_blocked(joined):
            got = sources.archive_get(page_url, 3650)
            if got:
                blocks, via = html_to_blocks(_main_region(got[0]), title), "archive"
    if _chars(blocks) < 80:
        return None
    return {
        "blocks": blocks,
        "fetched": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "from": via,
        "chars": _chars(blocks),
    }


# ---------------------------------------------------------------- 전문 번역

FULL_SYSTEM = """You are a senior legal translator for usvisapolicy.com, which publishes official U.S. immigration
documents (USCIS, Department of State, DHS, Federal Register, presidential documents) in several languages.

You receive a JSON array of English text segments from ONE official document, in reading order.
Translate EVERY segment completely and faithfully into {lang}.

Rules:
- Full translation, not a summary. Translate every sentence, clause, list item, number, date and condition.
  Never omit, shorten, merge, split, reorder or add content. No explanations, no translator notes.
- Return exactly the same number of segments, in the same order.
- Keep form numbers (I-129, DS-160), visa classes (H-1B, EB-5), CFR and U.S.C. citations, docket numbers,
  URLs, email addresses and phone numbers exactly as in the source. Keep agency acronyms (USCIS, DHS, CBP, ICE).
  On first use you may add the translated agency name followed by the acronym in parentheses.
- Use the official, formal register used for laws and government notices in {lang}.
- Keep line breaks inside a segment.
- Never use the em dash character. Use commas or periods.
{extra}
Return ONLY a JSON array of strings. No code fences, no other text."""

EXTRA = {
    "ko": "- Korean: write in formal 합니다체 (공문서 문체). Never use the word \"아울러\".",
    "ja": "- Japanese: write in formal である調 or です・ます調 consistently, as in government notices.",
    "zh": "- Chinese: Simplified Chinese, formal written style used by government notices.",
    "es": "- Spanish: formal register, neutral Latin American Spanish.",
}


def _clean(s: str, lang: str) -> str:
    s = s.replace("—", ", ")
    if lang == "ko":
        s = s.replace("아울러 ", "").replace("아울러", "")
    return s


def _call(texts: list[str], lang: str, model: str) -> list[str] | None:
    from . import llm

    raw = llm.complete(
        FULL_SYSTEM.format(lang=LANG_NAMES[lang], extra=EXTRA.get(lang, "")),
        json.dumps(texts, ensure_ascii=False),
        model,
    ).strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
    try:
        out = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\[.*\]", raw, re.S)
        out = json.loads(m.group(0)) if m else None
    if isinstance(out, list) and len(out) == len(texts) and all(isinstance(x, str) for x in out):
        return [_clean(x, lang) for x in out]
    return None


def _translate(texts: list[str], lang: str, model: str) -> list[str | None]:
    """한 덩어리 번역. 개수가 안 맞거나 실패하면 반으로 나눠 다시 합니다. 끝까지 안 되는 문단은 None."""
    for _ in range(2):
        try:
            out = _call(texts, lang, model)
            if out is not None:
                return list(out)
        except Exception as exc:  # noqa: BLE001
            from . import llm

            if llm.blocked():
                return [None] * len(texts)
            print(f"    ! 전문 번역 오류 ({lang}): {type(exc).__name__}: {str(exc)[:120]}")
            time.sleep(3)
    if len(texts) == 1:
        return [None]
    mid = len(texts) // 2
    return _translate(texts[:mid], lang, model) + _translate(texts[mid:], lang, model)


def _chunks(texts: list[str], size: int) -> list[tuple[int, int]]:
    spans, start, n = [], 0, 0
    for i, x in enumerate(texts):
        if i > start and (n + len(x) > size or i - start >= 60):
            spans.append((start, i))
            start, n = i, 0
        n += len(x)
    if start < len(texts):
        spans.append((start, len(texts)))
    return spans


def translate_full(a: dict[str, Any], langs: list[str], model: str, fcfg: dict[str, Any], cfg: dict[str, Any] | None = None) -> bool:
    blocks = (a.get("original") or {}).get("blocks") or []
    if not blocks:
        return False
    limit = _limit(blocks, int(fcfg.get("max_chars", 300000)))
    texts = [b["x"] for b in blocks[:limit]]
    full = a.setdefault("full", {})
    jobs = []
    for lang in langs:
        if lang not in LANG_NAMES:
            continue
        cur = full.get(lang)
        if not isinstance(cur, list) or len(cur) != limit:
            cur = [None] * limit
            full[lang] = cur
        for s, e in _chunks(texts, int(fcfg.get("chunk_chars", 4500))):
            if any(cur[i] is None for i in range(s, e)):
                jobs.append((lang, s, e))
    if not jobs:
        return False

    def run(job: tuple[str, int, int]) -> tuple[str, int, list[str | None]]:
        lang, s, e = job
        if past_deadline(cfg):
            return lang, s, [None] * (e - s)
        return lang, s, _translate(texts[s:e], lang, model)

    with ThreadPoolExecutor(max_workers=int(fcfg.get("workers", 6))) as ex:
        for lang, s, out in ex.map(run, jobs):
            for k, v in enumerate(out):
                if v is not None:
                    full[lang][s + k] = v
    a["full_model"] = model
    return True


def _limit(blocks: list[dict[str, str]], max_chars: int) -> int:
    n = 0
    for i, b in enumerate(blocks):
        n += len(b["x"])
        if n > max_chars:
            return max(i, 1)
    return len(blocks)


def needs_work(a: dict[str, Any], langs: list[str], fcfg: dict[str, Any]) -> bool:
    o = a.get("original") or {}
    if not o.get("blocks"):
        return int(a.get("original_fail", 0)) < int(fcfg.get("max_fetch_fail", 5))
    if not translate.enabled():
        return False
    limit = _limit(o["blocks"], int(fcfg.get("max_chars", 300000)))
    for lang in langs:
        if lang not in LANG_NAMES:
            continue
        cur = (a.get("full") or {}).get(lang)
        if not isinstance(cur, list) or len(cur) != limit or any(x is None for x in cur):
            return True
    return False


def ensure(a: dict[str, Any], browser: Any, cfg: dict[str, Any], item: dict[str, Any] | None = None) -> bool:
    """원문을 보관하고 전문을 번역합니다. 실패해도 예외를 던지지 않습니다. 바뀐 게 있으면 True."""
    fcfg = cfg.get("fulltext") or {}
    if fcfg.get("enabled") is False:
        return False
    changed = False
    try:
        o = a.get("original") or {}
        refetch = o.get("from") == "pi-pdf" and "/public-inspection/" not in a["url"]
        if not o.get("blocks") or refetch:
            got = fetch_original(a, browser, item, int(fcfg.get("max_chars", 300000)))
            if got:
                if refetch:
                    a.pop("full", None)
                a["original"] = got
                a.pop("original_fail", None)
                print(f"    - 원문 보관 {got['chars']:,}자 ({got['from']}, {len(got['blocks'])}문단)")
            elif not o.get("blocks"):
                a["original_fail"] = int(a.get("original_fail", 0)) + 1
                print(f"    ! 원문 보관 실패 ({a['original_fail']}회)")
            changed = True
        if translate.enabled() and (a.get("original") or {}).get("blocks"):
            langs = [l for l in cfg["languages"] if l in LANG_NAMES]
            if not past_deadline(cfg) and translate_full(a, langs, cfg["model"], fcfg, cfg):
                stat = []
                for l in langs:
                    arr = a["full"].get(l, [])
                    stat.append(f"{l}:{sum(1 for x in arr if x is not None)}/{len(arr)}")
                print("    - 전문 번역 " + ", ".join(stat))
                changed = True
    except Exception as exc:  # noqa: BLE001
        print(f"    ! 전문 처리 오류: {type(exc).__name__}: {str(exc)[:200]}")
    return changed


# 이번 실행의 기존 기사 전문 채우기 결과. main 이 실행 기록에 남깁니다.
STATS: dict[str, int] = {}


def backfill(index: list[dict[str, Any]], browser: Any, cfg: dict[str, Any]) -> None:
    """이미 올린 기사 중 원문 보관이나 전문 번역이 빠진 것을 채웁니다. 최신 기사부터, 실행 시간 안에서만."""
    fcfg = cfg.get("fulltext") or {}
    if fcfg.get("enabled") is False:
        return
    STATS.clear()
    limit = int(os.environ.get("FULLTEXT_BACKFILL") or fcfg.get("backfill_per_run", 6))
    budget = float(os.environ.get("FULLTEXT_BUDGET_MIN") or fcfg.get("budget_min", 8)) * 60
    start = time.time()
    langs = cfg["languages"]
    done = 0
    for row in sorted(index, key=lambda r: r.get("published") or "", reverse=True):
        if done >= limit or time.time() - start > budget or past_deadline(cfg):
            break
        a = store.load_article(row["id"])
        if not a or not needs_work(a, langs, fcfg):
            continue
        print(f"  · 전문 [{a.get('source')}] {(a.get('original_title') or '')[:70]}")
        if ensure(a, browser, cfg):
            store.save_article(a["id"], a)
        done += 1
    left = 0
    for r in index:
        x = store.load_article(r["id"])
        if x and needs_work(x, langs, fcfg):
            left += 1
    STATS.update({"done": done, "left": left})
    print(f"  - 전문 처리 {done}건, 남은 기사 {left}건")


# ---------------------------------------------------------------- 화면

T = {
    "full": {"ko": "전문 번역", "en": "Full text", "es": "Traducción completa", "zh": "全文翻译", "ja": "全文翻訳"},
    "btn_tr": {"ko": "번역", "en": "Text", "es": "Traducción", "zh": "译文", "ja": "翻訳"},
    "btn_or": {"ko": "원문", "en": "Original", "es": "Original", "zh": "原文", "ja": "原文"},
    "btn_both": {"ko": "대조", "en": "Both", "es": "Ambos", "zh": "对照", "ja": "対訳"},
    "note": {
        "ko": "공식 원문 전체를 {date}에 이 사이트에 보관했습니다. 원문 링크가 바뀌거나 삭제되어도 여기서 전문을 볼 수 있습니다. 번역은 AI가 원문 전체를 문단 단위로 옮긴 것이며 법적 효력은 영문 원문에만 있습니다.",
        "en": "The complete official text was archived on this site on {date}. It stays available here even if the source link changes or is removed.",
        "es": "El texto oficial completo se archivó en este sitio el {date}. Sigue disponible aquí aunque el enlace original cambie o se elimine. La traducción fue hecha con IA párrafo por párrafo; solo el texto original en inglés tiene validez legal.",
        "zh": "官方原文全文已于 {date} 保存在本站。即使原链接变更或被删除，仍可在此查看全文。译文由 AI 逐段翻译，仅英文原文具有法律效力。",
        "ja": "公式原文の全文を {date} に本サイトに保存しました。元のリンクが変更・削除されても、ここで全文を確認できます。翻訳はAIが原文全体を段落ごとに訳したもので、法的効力は英語原文のみにあります。",
    },
    "pending": {
        "ko": "전문 번역을 진행 중입니다. 아직 번역되지 않은 문단은 원문으로 표시됩니다.",
        "en": "",
        "es": "La traducción completa está en curso. Los párrafos aún no traducidos se muestran en el original.",
        "zh": "全文翻译进行中。尚未翻译的段落显示为原文。",
        "ja": "全文翻訳を進めています。未翻訳の段落は原文で表示しています。",
    },
    "cut": {
        "ko": "원문이 매우 길어 앞부분 {n}개 문단을 번역했습니다. 이후 문단은 원문으로 표시됩니다.",
        "en": "",
        "es": "El original es muy extenso; se tradujeron los primeros {n} párrafos. El resto se muestra en el original.",
        "zh": "原文篇幅很长，已翻译前 {n} 段，其余段落显示为原文。",
        "ja": "原文が非常に長いため、最初の{n}段落を翻訳しました。以降は原文で表示しています。",
    },
    "none": {
        "ko": "원문 전문을 보관하는 중입니다. 다음 수집 때 다시 시도합니다.",
        "en": "The complete original text is being archived and will appear here shortly.",
        "es": "El texto original completo se está archivando y aparecerá aquí en breve.",
        "zh": "官方原文全文正在保存，稍后将显示在此。",
        "ja": "原文全文を保存中です。まもなくここに表示されます。",
    },
}

CSS = """
.ft{margin-top:30px;padding-top:20px;border-top:1px solid var(--hair)}
.ft h2{margin-top:0}
.ft-bar{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0 12px}
.ft-bar button{border:1px solid var(--rule);background:var(--paper);color:var(--ink-2);font:inherit;font-size:13px;padding:5px 13px;border-radius:999px;cursor:pointer}
.ft-bar button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.ft-note{font-size:12.5px;color:var(--faint);margin:0 0 16px}
.ft-row{margin:0 0 13px;line-height:1.8}
.ft-row>div{white-space:normal}
.ft-h{font-weight:700;font-size:16.5px;margin-top:22px}
.ft-li{position:relative;padding-left:18px}
.ft-li>div::before{content:"\\2022";position:absolute;left:4px}
.ft-tr{font-size:14px;padding:6px 10px;background:var(--chip);border-radius:6px}
.ft[data-mode="tr"] .ft-o{display:none}
.ft[data-mode="tr"] .ft-miss .ft-o{display:block}
.ft[data-mode="or"] .ft-t{display:none}
.ft .ft-miss .ft-t{display:none}
.ft[data-mode="both"] .ft-row{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.ft[data-mode="both"] .ft-o{color:var(--muted)}
.ft[data-mode="both"] .ft-miss{display:block}
@media (max-width:700px){.ft[data-mode="both"] .ft-row{grid-template-columns:1fr;gap:4px}}
"""

JS = """(function(){var s=document.querySelector('.ft');if(!s)return;var bs=s.querySelectorAll('.ft-bar button');
function set(m){s.dataset.mode=m;bs.forEach(function(x){x.setAttribute('aria-pressed',String(x.dataset.m===m))});}
bs.forEach(function(b){b.addEventListener('click',function(){set(b.dataset.m);try{localStorage.setItem('uvp-ft',b.dataset.m)}catch(e){}})});
try{var m=localStorage.getItem('uvp-ft');if(m&&s.querySelector('.ft-bar button[data-m="'+m+'"]'))set(m)}catch(e){}})();"""


def _t(key: str, lang: str) -> str:
    row = T[key]
    return row.get(lang) or row["en"]


def section(a: dict[str, Any], lang: str) -> str:
    e = html_lib.escape
    o = a.get("original") or {}
    blocks = o.get("blocks") or []
    style = f"<style>{CSS}</style>"
    if not blocks:
        return f'{style}<section class="ft" id="fulltext"><h2>{e(_t("full", lang))}</h2><p class="ft-note">{e(_t("none", lang))}</p></section>'
    date = (o.get("fetched") or "")[:10]
    tr = (a.get("full") or {}).get(lang) if lang != "en" else None
    rows = []
    missing = 0
    for i, b in enumerate(blocks):
        orig = e(b["x"])
        if lang == "en":
            rows.append(f'<div class="ft-row ft-{e(b["t"])}"><div class="ft-o" lang="en">{orig}</div></div>')
            continue
        t = tr[i] if isinstance(tr, list) and i < len(tr) else None
        if t is None:
            missing += 1
        miss = " ft-miss" if t is None else ""
        rows.append(
            f'<div class="ft-row ft-{e(b["t"])}{miss}"><div class="ft-t" lang="{HTML_LANG.get(lang, lang)}">{e(t or "")}</div>'
            f'<div class="ft-o" lang="en">{orig}</div></div>'
        )
    notes = [e(_t("note", lang).format(date=date))]
    if lang != "en" and missing:
        limit = len(tr) if isinstance(tr, list) else 0
        if isinstance(tr, list) and limit < len(blocks) and all(x is not None for x in tr):
            notes.append(e(_t("cut", lang).format(n=limit)))
        else:
            notes.append(e(_t("pending", lang)))
    bar = ""
    if lang != "en":
        bar = (
            '<div class="ft-bar" role="group">'
            f'<button type="button" data-m="tr" aria-pressed="true">{e(_t("btn_tr", lang))}</button>'
            f'<button type="button" data-m="or" aria-pressed="false">{e(_t("btn_or", lang))}</button>'
            f'<button type="button" data-m="both" aria-pressed="false">{e(_t("btn_both", lang))}</button></div>'
        )
    return (
        f'{style}<section class="ft" id="fulltext" data-mode="{"or" if lang == "en" else "tr"}">'
        f'<h2>{e(_t("full", lang))}</h2>{bar}<p class="ft-note">{"<br>".join(notes)}</p>'
        f'<div class="ft-body">{"".join(rows)}</div></section><script>{JS}</script>'
    )
