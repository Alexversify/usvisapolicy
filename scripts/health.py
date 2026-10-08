"""수집 상태 점검. 문제가 이어지면 종료 코드 1로 Actions 실행을 실패시켜 GitHub 알림 메일이 가게 합니다.

- 소스가 6회 연속(약 3시간) 실패. settings.yaml 에서 alert: false 인 소스는 제외 (차단이 알려진 travel.state.gov)
- 번역이 4회 연속(약 2시간) 실패 (API 키 만료, 크레딧 소진, 모델 중단 등)
- 마지막 수집이 24시간 넘게 없음
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    st = json.loads((ROOT / "data" / "status.json").read_text(encoding="utf-8"))
    problems = []
    checked = dt.datetime.strptime(st["checked"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=dt.timezone.utc)
    if dt.datetime.now(dt.timezone.utc) - checked > dt.timedelta(hours=24):
        problems.append(f"마지막 수집 {st['checked']} 이후 24시간 넘게 갱신 없음")
    for key, r in (st.get("sources") or {}).items():
        if r.get("alert", True) and r.get("fail_streak", 0) >= 6:
            problems.append(f"{key}: {r['fail_streak']}회 연속 수집 실패. {(r.get('error') or '')[:200]}")
    t = st.get("translate") or {}
    if t.get("fail_streak", 0) >= 4:
        problems.append("번역 4회 연속 실패" + ("" if t.get("key", True) else " (ANTHROPIC_API_KEY 없음)")
                        + ". API 키, 크레딧, settings.yaml 의 model 을 확인하세요.")
    for p in problems:
        print(f"::error title=usvisapolicy 점검::{p}")
    if not problems:
        print("이상 없음")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
