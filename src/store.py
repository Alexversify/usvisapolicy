"""data/ 저장소.

data/index.json       기사 목록 (id, source, url, 날짜, 상태). 화면 생성의 기준
data/articles/<id>.json  기사 1건의 다국어 본문
data/seen.json        번역하지 않고 넘긴 URL (기준선, 정보성 공고 등). 다시 보지 않음
data/status.json      마지막 수집 시각과 소스별 결과. 화면의 "마지막 확인" 시각

git 커밋 이력이 곧 변경 로그입니다. 특정 기사 번역을 고치려면 articles/<id>.json을 직접 수정해도 됩니다.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARTICLES = DATA / "articles"
INDEX = DATA / "index.json"
SEEN = DATA / "seen.json"
STATUS = DATA / "status.json"


def _read(p: Path, default: Any) -> Any:
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def _write(p: Path, data: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_index() -> list[dict[str, Any]]:
    return _read(INDEX, [])


def save_index(items: list[dict[str, Any]]) -> None:
    items.sort(key=lambda x: (x.get("published") or "", x.get("added") or ""), reverse=True)
    _write(INDEX, items)


def load_seen() -> dict[str, str]:
    return _read(SEEN, {})


def save_seen(seen: dict[str, str]) -> None:
    _write(SEEN, dict(sorted(seen.items())))


def load_article(aid: str) -> dict[str, Any] | None:
    return _read(ARTICLES / f"{aid}.json", None)


def save_article(aid: str, data: dict[str, Any]) -> None:
    _write(ARTICLES / f"{aid}.json", data)


def load_status() -> dict[str, Any]:
    return _read(STATUS, {})


def save_status(data: dict[str, Any]) -> None:
    _write(STATUS, data)
