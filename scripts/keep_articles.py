"""한 번 올린 기사는 내리지 않습니다.

기준 커밋(기본 origin/main)의 data/index.json 에 있던 기사가 지금 작업본에서 빠졌으면
목록 행과 기사 파일을 기준 커밋에서 되살립니다. 원문이 삭제돼도, 커밋을 합치다 행이 사라져도 남습니다.

    python scripts/keep_articles.py [기준 커밋]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import store  # noqa: E402


def git_show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def main() -> int:
    ref = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    raw = git_show(ref, "data/index.json")
    if raw is None:
        print(f"기준 {ref} 에 index.json 없음. 건너뜀")
        return 0
    base = json.loads(raw)
    index = store.load_index()
    have = {r["id"] for r in index}
    restored = 0
    for row in base:
        aid = row["id"]
        path = store.ARTICLES / f"{aid}.json"
        if not path.exists():
            body = git_show(ref, f"data/articles/{aid}.json")
            if body is None:
                continue
            path.write_text(body, encoding="utf-8")
            restored += 1
        if aid not in have:
            index.append(row)
            have.add(aid)
            restored += 1
    if restored:
        store.save_index(index)
        print(f"::warning title=기사 보존::{ref} 에 있던 기사 {restored}건(행/파일)을 되살렸습니다")
    else:
        print("빠진 기사 없음")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
