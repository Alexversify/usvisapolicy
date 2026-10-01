"""진입점.

python -m src.main               수집 → 번역 → 사이트 생성
python -m src.main --render-only 데이터는 그대로 두고 docs/만 다시 생성 (디자인 수정 후)
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import render, sources, store, translate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BROWSER_SOURCES = {"uscis_news", "dos_visa_news", "visa_bulletin"}
FR_SOURCES = {"federal_register", "presidential"}


def load_cfg() -> dict[str, Any]:
    return yaml.safe_load((ROOT / "config" / "settings.yaml").read_text(encoding="utf-8"))


def collect(cfg: dict[str, Any], browser: Any, since: dt.date) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for key, scfg in cfg["sources"].items():
        if not scfg.get("enabled", True):
            continue
        if key in FR_SOURCES:
            res = sources.collect_federal_register(key, scfg, since)
        elif key in BROWSER_SOURCES:
            if browser is None:
                print(f"  - {key}: 건너뜀 (브라우저 없음)")
                continue
            res = sources.collect_listing(browser, key, scfg)
        else:
            continue
        print(f"  - {key}: {res['error'] or 'ok'} ({len(res['items'])}건)")
        found.extend(res["items"])
    return found


def source_text(item: dict[str, Any], browser: Any) -> tuple[str, str | None]:
    """(본문, 페이지에서 찾은 게시일)."""
    if item.get("prefetched_text") is not None:
        extra = sources.fetch_fr_text(item.get("text_url"))
        return (item["prefetched_text"] + ("\n\n--- FULL TEXT (truncated) ---\n" + extra if extra else ""), None)
    if browser is None:
        return "", None
    try:
        art = browser.article(item["url"])
    except Exception as exc:  # noqa: BLE001
        print(f"    ! 본문 실패: {exc}")
        return "", None
    return art.get("text") or "", sources.parse_date(art.get("date") or "") or sources.parse_date((art.get("text") or "")[:600])


def run(cfg: dict[str, Any]) -> None:
    langs = cfg["languages"]
    index = store.load_index()
    seen = store.load_seen()
    known = {x["id"] for x in index} | set(seen)
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
        found = collect(cfg, browser, since)

        fresh: dict[str, dict[str, Any]] = {}
        for it in found:
            if it["id"] in known or it["id"] in fresh:
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
            published = published or data.get("published") or today.isoformat()
            article = {
                "id": it["id"],
                "source": it["source"],
                "url": it["url"],
                "original_title": it["title"],
                "published": published,
                "effective_date": data.get("effective_date") or it.get("effective_on"),
                "importance": data.get("importance", "medium"),
                "tags": data.get("tags", [])[:8],
                "langs": data["langs"],
                "added": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ"),
                "model": cfg["model"],
            }
            store.save_article(it["id"], article)
            index.append({k: article[k] for k in ("id", "source", "url", "published", "effective_date", "importance", "tags", "added")})

    store.save_index(index)
    store.save_seen(seen)


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
