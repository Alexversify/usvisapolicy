"""원문 전문 보관·전문 번역(src/fulltext.py)과 과거 글 채우기를 기존 코드에 연결합니다.

backfill 워크플로가 매번 먼저 실행합니다. 이미 적용됐으면 아무것도 바꾸지 않습니다.
고칠 자리를 찾지 못하면 실패로 끝내 잘못된 코드가 커밋되지 않게 합니다.

    python scripts/migrate_fulltext.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAIN = [
    (
        "from src import render, sources, store, taxonomy, translate  # noqa: E402",
        "from src import fulltext, render, sources, store, taxonomy, translate  # noqa: E402",
    ),
    (
        '    since = today - dt.timedelta(days=int(cfg.get("backfill_days", 45)))\n',
        '    since = today - dt.timedelta(days=int(cfg.get("backfill_days", 45)))\n'
        '    backfill_cfg = cfg.get("backfill") or {}\n'
        '    if os.environ.get("BACKFILL") and backfill_cfg.get("since"):\n'
        "        # 과거 글 채우기: 지정일 이후 글을 모두 대상으로 하고, 예전에 '오래됨'으로 넘긴 글을 다시 봅니다.\n"
        '        since = dt.date.fromisoformat(str(backfill_cfg["since"]))\n'
        '        seen = {k: v for k, v in seen.items() if not str(v).startswith("old ")}\n'
        '        known = {x["id"] for x in index} | set(seen)\n',
    ),
    (
        '        cap = int(cfg.get("max_new_per_run", 15))',
        '        cap = int(os.environ.get("MAX_NEW") or cfg.get("max_new_per_run", 15))',
    ),
    (
        "            res = sources.collect_federal_register(key, scfg, since)\n",
        '            if os.environ.get("BACKFILL"):\n'
        '                scfg = {**scfg, "max_pages": int((cfg.get("backfill") or {}).get("fr_max_pages", 20))}\n'
        "            res = sources.collect_federal_register(key, scfg, since)\n",
    ),
    (
        "            res = sources.collect_listing(browser, key, scfg)\n",
        '            bf = cfg.get("backfill") or {}\n'
        '            pages = int((bf.get("pages") or {}).get(key, 0) or 0) if os.environ.get("BACKFILL") else 0\n'
        "            if pages > 1:\n"
        "                # 과거 글 채우기: 목록의 뒤 페이지까지 봅니다. 빈 페이지는 실패로 치지 않습니다.\n"
        '                fmt = (bf.get("page_fmt") or {}).get(key) or "{u}{sep}page={n}"\n'
        "                urls = []\n"
        '                for u in scfg.get("list_urls", []):\n'
        "                    urls.append(u)\n"
        '                    urls += [fmt.format(u=u, sep="&" if "?" in u else "?", n=n) for n in range(1, pages)]\n'
        '                scfg = {**scfg, "list_urls": urls, "max_items": None}\n'
        "            res = sources.collect_listing(browser, key, scfg)\n"
        '            if pages > 1 and res["error"]:\n'
        '                res["error"] = "; ".join(p for p in res["error"].split("; ") if "page=" not in p and "/page/" not in p) or None\n',
    ),
    (
        "        for it in queue[:cap]:\n",
        '        new_started = __import__("time").time()\n'
        "        for it in queue[:cap]:\n"
        '            if fulltext.past_deadline(cfg) or (os.environ.get("NEW_BUDGET_MIN") and __import__("time").time() - new_started > float(os.environ["NEW_BUDGET_MIN"]) * 60):\n'
        '                print("  - 시간 한도에 닿아 나머지 새 글은 다음 실행에서 처리")\n'
        "                break\n",
    ),
    (
        '            store.save_article(it["id"], article)\n            sources.archive_save',
        "            # 공식 원문 전문을 보관하고 4개 언어로 전문 번역합니다.\n"
        '            fulltext.ensure(article, browser, cfg, item=it)\n'
        '            store.save_article(it["id"], article)\n            sources.archive_save',
    ),
    (
        '"category", "agency", "topics", "tags", "added")})\n\n    # 번역이 하나라도',
        '"category", "agency", "topics", "tags", "added")})\n\n'
        '        print("[2b/3] 원문 보관·전문 번역")\n'
        "        fulltext.backfill(index, browser, cfg)\n\n"
        "    # 번역이 하나라도",
    ),
]

RENDER = [
    ("from src import taxonomy\n", "from src import fulltext, taxonomy\n"),
    ('{who}{action}\n<div class="src">', '{who}{action}\n{fulltext.section(a, lang)}\n<div class="src">'),
]

SETTINGS_BLOCK = """
# 과거 글 채우기. backfill 워크플로(BACKFILL=1)에서만 씁니다. 정기 실행은 위 backfill_days 기준 그대로입니다.
backfill:
  since: 2026-01-01
  # 목록을 몇 페이지까지 볼지. 0이면 과거 글을 채우지 않습니다.
  pages:
    uscis_news: 30
    state_press: 20
    dhs_news: 0
  page_fmt:
    state_press: "{u}page/{n}/"
  # 연방관보는 100건씩 몇 페이지까지 볼지
  fr_max_pages: 20

# 공식 원문 전문 보관과 전문 번역 (src/fulltext.py)
fulltext:
  enabled: true
  # 이보다 긴 문서는 앞부분만 번역하고 나머지는 원문으로 보여줍니다. 원문 보관은 전체.
  max_chars: 300000
  chunk_chars: 4500
  workers: 8
  # 정기 실행에서 기존 기사를 몇 건까지, 몇 분까지 채울지
  backfill_per_run: 6
  budget_min: 8
  # 한 실행의 전체 시간 한도(분). 넘으면 하던 것까지 저장하고 다음 실행에 넘깁니다. backfill 워크플로는 RUN_DEADLINE_MIN 으로 따로 정합니다.
  deadline_min: 18
"""

CLAUDE_BLOCK = """
## 원문 보관과 전문 번역

- src/fulltext.py. 기사마다 공식 원문 전체를 문단 단위로 data/articles/<id>.json 의 original.blocks 에 보관하고,
  문단마다 ko·es·zh·ja 전문 번역을 full.<lang> 에 같은 순서로 넣는다. 아직 못 한 문단은 null.
- 기사 페이지는 요약 아래에 전문을 보여준다. 번역·원문·대조 보기를 고를 수 있다. 원문 사이트가 글을 내려도 여기 남는다.
- 정기 실행은 새 기사의 전문을 바로 만들고, 빠진 기존 기사를 실행당 몇 건씩 채운다 (settings.yaml fulltext).
- 과거 글은 .github/workflows/backfill.yml 이 settings.yaml backfill.since 이후 것을 채운다.
- 번역 수정은 full.<lang> 의 해당 문단만 고친다. 문단 수와 순서를 바꾸지 않는다.
"""


def patch(path: Path, pairs: list[tuple[str, str]]) -> bool:
    s = path.read_text(encoding="utf-8")
    changed = False
    for old, new in pairs:
        if new in s:
            continue
        n = s.count(old)
        if n != 1:
            sys.exit(f"{path.name}: 고칠 자리를 {n}곳 찾음 (1곳이어야 함): {old[:80]!r}")
        s = s.replace(old, new)
        changed = True
    if changed:
        path.write_text(s, encoding="utf-8")
        print(f"고침: {path.relative_to(ROOT)}")
    return changed


def append(path: Path, marker: str, block: str) -> bool:
    s = path.read_text(encoding="utf-8")
    if marker in s:
        return False
    path.write_text(s.rstrip("\n") + "\n" + block, encoding="utf-8")
    print(f"추가: {path.relative_to(ROOT)}")
    return True


def main() -> int:
    patch(ROOT / "src" / "main.py", MAIN)
    patch(ROOT / "src" / "render.py", RENDER)
    append(ROOT / "config" / "settings.yaml", "\nfulltext:", SETTINGS_BLOCK)
    append(ROOT / "CLAUDE.md", "## 원문 보관과 전문 번역", CLAUDE_BLOCK)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
