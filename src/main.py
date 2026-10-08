"""진입점.

python -m src.main               수집 → 번역 → 사이트 생성
python -m src.main --render-only 데이터는 그대로 두고 docs/만 다시 생성 (디자인 수정 후)
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import os
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import render, sources, store, translate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BROWSER_SOURCES = {"uscis_news", "dos_visa_news", "visa_bulletin", "dhs_news", "state_press"}
FR_SOURCES = {"federal_register", "presidential"}
PI_SOURCES = {"fr_public_inspection"}
CHART_SOURCES = {"uscis_vb_chart"}


def load_cfg() -> dict[str, Any]:
    return yaml.safe_load((ROOT / "config" / "settings.yaml").read_text(encoding="utf-8"))


def collect(cfg: dict[str, Any], browser: Any, since: dt.date, report: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for key, scfg in cfg["sources"].items():
        if not scfg.get("enabled", True):
            continue
        if key in FR_SOURCES:
            res = sources.collect_federal_register(key, scfg, since)
        elif key in PI_SOURCES:
            res = sources.collect_public_inspection(key, scfg)
        elif key in CHART_SOURCES:
            if browser is None:
                print(f"  - {key}: 건너뜀 (브라우저 없음)")
                continue
            res = sources.collect_uscis_vb_chart(browser, key, scfg)
        elif key in BROWSER_SOURCES:
            if browser is None and not scfg.get("archive_fallback"):
                print(f"  - {key}: 건너뜀 (브라우저 없음)")
                report[key] = {"ok": False, "items": 0, "error": "브라우저 없음"}
                continue
            res = sources.collect_listing(browser, key, scfg)
        else:
            continue
        print(f"  - {key}: {res['error'] or 'ok'} ({len(res['items'])}건)")
        report[key] = {"ok": not res["error"], "items": len(res["items"]), "error": (res["error"] or "")[:300] or None}
        via = sorted({it.get("via") for it in res["items"] if it.get("via")})
        if via:
            report[key]["via"] = via[0]
        if res["error"] and os.environ.get("GITHUB_ACTIONS"):
            # Actions 실행 요약에 경고로 드러냅니다. 실행은 초록색이어도 소스 실패를 놓치지 않게 합니다.
            print(f"::warning title=수집 실패 {key}::{res['error'][:300]}")
        found.extend(res["items"])
    return found


def source_text(item: dict[str, Any], browser: Any) -> tuple[str, str | None]:
    """(본문, 페이지에서 찾은 게시일)."""
    if item.get("prefetched_text") is not None and not item.get("text_url") and not item.get("pdf_url"):
        return item["prefetched_text"], None
    if item.get("prefetched_text") is not None:
        extra = sources.fetch_fr_text(item.get("text_url"), pdf_url=item.get("pdf_url"))
        return (item["prefetched_text"] + ("\n\n--- FULL TEXT (truncated) ---\n" + extra if extra else ""), None)
    art: dict[str, Any] = {}
    if browser is not None:
        try:
            art = browser.article(item["url"])
        except Exception as exc:  # noqa: BLE001
            print(f"    ! 본문 실패: {exc}")
    text = art.get("text") or ""
    if item.get("archive_fallback") and (len(text.strip()) < 200 or sources.looks_blocked(text) or sources.looks_blocked(art.get("title") or "")):
        # 차단된 국무부 페이지는 인터넷 아카이브 사본에서 본문을 읽습니다.
        got = sources.archive_get(item["url"])
        if not got:
            print("    ! 차단, 아카이브 사본 없음. 다음 실행에서 재시도")
            return "", None
        text = sources.html_main_text(got[0])
        print(f"    - 아카이브 사본으로 본문 확보 ({got[1][:8]})")
        return text, sources.parse_date(text[:600])
    return text, sources.parse_date(art.get("date") or "") or sources.parse_date(text[:600])


def run(cfg: dict[str, Any]) -> None:
    langs = cfg["languages"]
    index = store.load_index()
    seen = store.load_seen()
    known = {x["id"] for x in index} | set(seen)
    # 공개열람본으로 이미 낸 문서가 다음 날 정식 게재되면 URL이 달라도 같은 문서 번호입니다.
    known_docs = {sources.fr_doc_number(x["url"]) for x in index} | {sources.fr_doc_number(v) for v in seen.values()}
    known_docs.discard(None)
    today = dt.date.today()
    since = today - dt.timedelta(days=int(cfg.get("backfill_days", 45)))

    need_browser = any(
        k in BROWSER_SOURCES and v.get("enabled", True) for k, v in cfg["sources"].items()
    )
    browser_cm: Any = contextlib.nullcontext(None)
    if need_browser:
        try:
            import playwright  # noqa: F401

            browser_cm = sources.Browser()
        except ImportError:
            print("  ! playwright 미설치. 브라우저 소스는 건너뜁니다.")

    with browser_cm as browser:
        print("[1/3] 수집")
        report: dict[str, Any] = {}
        found = collect(cfg, browser, since, report)

        fresh: dict[str, dict[str, Any]] = {}
        for it in found:
            if it["id"] in known or it["id"] in fresh:
                continue
            if it.get("doc") and (it["doc"] in known_docs or any(f.get("doc") == it["doc"] for f in fresh.values())):
                promote_published(index, it)
                continue
            if it.get("published") and it["published"] < since.isoformat():
                seen[it["id"]] = f"old {it['published']} {it['url']}"
                continue
            fresh[it["id"]] = it
        queue = sorted(fresh.values(), key=lambda x: x.get("published") or "9999", reverse=True)
        cap = int(cfg.get("max_new_per_run", 15))
        print(f"  - 새 글 {len(queue)}건, 이번 실행 처리 {min(len(queue), cap)}건")

        print("[2/3] 번역")
        if not translate.enabled():
            print("  ! ANTHROPIC_API_KEY 없음. 번역을 건너뜁니다.")
            queue = []
        labels = {k: v.get("label", k) for k, v in cfg["sources"].items()}
        for it in queue[:cap]:
            print(f"  · [{it['source']}] {it['title'][:80]}")
            text, page_date = source_text(it, browser)
            if len(text.strip()) < 80:
                print("    ! 본문이 비어 다음 실행에서 재시도")
                continue
            published = it.get("published") or page_date
            if published and published < since.isoformat():
                seen[it["id"]] = f"old {published} {it['url']}"
                continue
            data = translate.build({**it, "published": published}, text, langs, cfg["model"], labels[it["source"]])
            if not data:
                continue
            if data.get("relevant") is False:
                # 연방관보 검색어에 걸렸지만 비자·이민과 무관한 문서 (전력망, 기념일 선포 등)
                print("    - 이민과 무관. 게시하지 않음")
                seen[it["id"]] = f"irrelevant {published or ''} {it['url']}"
                continue
            published = published or data.get("published") or today.isoformat()
            article = {
                "id": it["id"],
                "source": it["source"],
                "url": it["url"],
                "original_title": it["title"],
                "published": published,
                "effective_date": data.get("effective_date") or it.get("effective_on"),
                "importance": data.get("importance", "medium"),
                "category": data.get("category") if data.get("category") in translate.CATEGORIES else "notice",
                "tags": data.get("tags", [])[:8],
                "langs": data["langs"],
                "added": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                "model": cfg["model"],
            }
            store.save_article(it["id"], article)
            index.append({k: article[k] for k in ("id", "source", "url", "published", "effective_date", "importance", "category", "tags", "added")})

    backfill_categories(cfg, index)
    store.save_index(index)
    store.save_seen(seen)
    store.save_status({
        "checked": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "sources": report,
    })


def promote_published(index: list[dict[str, Any]], it: dict[str, Any]) -> None:
    """공개열람본으로 낸 기사의 원문 링크를 정식 게재본 주소로 바꿉니다."""
    if "/public-inspection/" in it["url"]:
        return
    for row in index:
        if "/public-inspection/" in row["url"] and sources.fr_doc_number(row["url"]) == it["doc"]:
            row["url"] = it["url"]
            a = store.load_article(row["id"])
            if a:
                a["url"] = it["url"]
                if it.get("effective_on") and not a.get("effective_date"):
                    a["effective_date"] = row["effective_date"] = it["effective_on"]
                store.save_article(row["id"], a)
            print(f"  - 게재본 링크로 교체: {it['doc']}")


def backfill_categories(cfg: dict[str, Any], index: list[dict[str, Any]]) -> None:
    """카테고리가 없는 기존 기사를 분류해 채웁니다. 한 번 채우면 다시 호출하지 않습니다."""
    if not translate.enabled():
        return
    missing = []
    for row in index:
        if row.get("category"):
            continue
        a = store.load_article(row["id"])
        if a:
            en = a["langs"].get("en", {})
            missing.append({"id": a["id"], "title": en.get("title") or a["original_title"], "summary": en.get("summary", "")})
    if not missing:
        return
    print(f"  - 카테고리 보충 {len(missing)}건")
    for i in range(0, len(missing), 40):
        result = translate.classify(missing[i:i + 40], cfg["model"])
        for row in index:
            cat = result.get(row["id"])
            if cat:
                row["category"] = cat
                a = store.load_article(row["id"])
                if a:
                    a["category"] = cat
                    store.save_article(row["id"], a)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--render-only", action="store_true")
    args = ap.parse_args()
    cfg = load_cfg()
    if not args.render_only:
        run(cfg)
    print("[3/3] 사이트 생성")
    out = render.render_all(cfg)
    print(f"  - {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
