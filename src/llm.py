"""Claude 호출 공용 함수.

순서: API 크레딧(ANTHROPIC_API_KEY) → 부족하면 Max 구독(CLAUDE_CODE_OAUTH_TOKEN) → 둘 다 소진되면 중단.
두 경우 모두 Claude Code CLI(`claude -p`)로 실행합니다. CLI는 API 키가 있으면 그걸 먼저 쓰므로,
구독으로 돌릴 때는 하위 프로세스 환경에서 API 키를 뺍니다.
크레딧이 바닥나도 카드 결제로 넘어가지 않게 하려면 Anthropic 콘솔에서 자동 충전(Auto-reload)을 꺼 두세요.

월 상한: API로 쓴 금액을 data/llm_spend/YYYY-MM/ 에 실행마다 기록하고, 이번 달 합계가
LLM_MONTHLY_CAP_USD(저장소 변수, 없으면 DEFAULT_MONTHLY_CAP) 이상이면 그달 남은 기간은 API를 쓰지 않습니다.
그 뒤로는 Max 구독으로만 돌고, 상한을 올리려면 소유자가 저장소 변수를 직접 바꿔야 합니다(= 동의).
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


class LLMError(RuntimeError):
    pass


class UsageLimit(LLMError):
    """크레딧과 구독 사용량이 모두 소진됨. 이번 실행은 멈추고 다음 실행에 넘깁니다."""


_LIMIT_HINTS = ("usage limit", "rate limit", "limit reached", "429", "overloaded", "quota",
                "credit balance", "insufficient", "billing", "402", "invalid x-api-key", "authentication")
_api_blocked = False   # 이번 실행에서 API 크레딧이 바닥났거나 키가 거부됨
_max_blocked = False   # 이번 실행에서 구독 사용량 한도에 걸림
_spent_usd = 0.0       # 이번 실행에서 쓴 금액(달러, CLI 가 보고한 값)


def _cap_usd() -> float | None:
    """실행당 비용 한도(달러). 워크플로의 LLM_MAX_USD_PER_RUN. 없으면 한도 없음."""
    v = os.environ.get("LLM_MAX_USD_PER_RUN")
    return float(v) if v else None


def spent_usd() -> float:
    return _spent_usd


def _over_cap() -> bool:
    cap = _cap_usd()
    return cap is not None and _spent_usd >= cap

DEFAULT_MONTHLY_CAP = 40   # 달러. 저장소 변수 LLM_MONTHLY_CAP_USD 로 바꿈 (전체 사이트 합계 $50 안에서 나눔)
_LEDGER = Path(__file__).resolve().parents[1] / "data" / "llm_spend"
_api_usd = 0.0         # 이번 실행에서 API(과금)로 쓴 금액
_month_logged = False  # 이번 달 상한 도달 안내를 이미 찍었는지


def _month() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m")


def _run_file() -> Path:
    rid = os.environ.get("GITHUB_RUN_ID", "local")
    att = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    job = os.environ.get("GITHUB_JOB", "run")
    return _LEDGER / _month() / f"{rid}-{att}-{job}.json"


def monthly_cap() -> float:
    v = (os.environ.get("LLM_MONTHLY_CAP_USD") or "").strip()
    try:
        return float(v) if v else float(DEFAULT_MONTHLY_CAP)
    except ValueError:
        return float(DEFAULT_MONTHLY_CAP)


def month_api_usd() -> float:
    """이번 달 API 사용액. 커밋된 지난 실행 기록 + 이번 실행."""
    total, me = 0.0, _run_file()
    d = _LEDGER / _month()
    if d.is_dir():
        for p in d.glob("*.json"):
            if p == me:
                continue
            try:
                total += float(json.loads(p.read_text(encoding="utf-8")).get("api_usd") or 0)
            except Exception:  # noqa: BLE001
                pass
    return total + _api_usd


def _record_api(cost: float) -> None:
    global _api_usd
    _api_usd += cost
    try:
        f = _run_file()
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"api_usd": round(_api_usd, 4), "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"[llm] 사용액 기록 실패: {exc}", flush=True)


def month_cap_reached() -> bool:
    global _month_logged
    used, cap = month_api_usd(), monthly_cap()
    if used < cap:
        return False
    if not _month_logged:
        _month_logged = True
        print(f"[llm] 이번 달 API 사용 ${used:.2f} / 상한 ${cap:.2f} 도달. 이번 달은 API를 쓰지 않습니다.", flush=True)
        try:
            m = _LEDGER / _month() / "CAP_REACHED"
            m.parent.mkdir(parents=True, exist_ok=True)
            m.write_text(f"{used:.2f} / {cap:.2f}\n", encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
    return True


def _has_api() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _has_max() -> bool:
    return bool(os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"))


def enabled() -> bool:
    return (_has_api() or _has_max()) and shutil.which("claude") is not None


def blocked() -> bool:
    return ((_api_blocked or not _has_api()) and (_max_blocked or not _has_max())) or _over_cap()


def _run(system: str, user: str, model: str, timeout: int, use_api: bool) -> str:
    global _spent_usd
    drop = ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_AUTH_TOKEN") if use_api else ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
    env = {k: v for k, v in os.environ.items() if k not in drop}
    with tempfile.TemporaryDirectory() as tmp:
        sp = os.path.join(tmp, "system.txt")
        with open(sp, "w", encoding="utf-8") as f:
            f.write(system)
        cmd = [
            "claude", "-p",
            "--model", model,
            "--system-prompt-file", sp,
            "--tools", "",
            "--setting-sources", "",
            "--strict-mcp-config",
            "--no-session-persistence",
            "--output-format", "json",
        ]
        try:
            proc = subprocess.run(cmd, input=user, capture_output=True, text=True,
                                  timeout=timeout, cwd=tmp, env=env)
        except subprocess.TimeoutExpired as exc:
            raise LLMError("claude CLI 시간 초과") from exc
    out = proc.stdout.strip()
    try:
        data = json.loads(out.splitlines()[-1]) if out else {}
    except json.JSONDecodeError:
        data = {}
    if isinstance(data, dict):
        try:
            cost = float(data.get("total_cost_usd") or 0)
            _spent_usd += cost
            if use_api:
                _record_api(cost)
        except (TypeError, ValueError):
            pass
    text = data.get("result") if isinstance(data, dict) else None
    if proc.returncode != 0 or data.get("is_error") or not isinstance(text, str):
        detail = (text or proc.stderr or out or "").strip()[:300]
        if any(h in detail.lower() for h in _LIMIT_HINTS):
            raise UsageLimit(detail)
        raise LLMError(f"claude CLI 실패 (code {proc.returncode}): {detail}")
    return text


def complete(system: str, user: str, model: str, timeout: int = 600) -> str:
    """system/user 한 번 주고 텍스트 답을 받습니다. 도구·CLAUDE.md·MCP 없이 순수 생성만 합니다."""
    global _api_blocked, _max_blocked
    if not enabled():
        raise LLMError("ANTHROPIC_API_KEY / CLAUDE_CODE_OAUTH_TOKEN 또는 claude CLI 없음")
    if _over_cap():
        raise UsageLimit(f"이번 실행 비용 한도 ${_cap_usd():.2f} 도달 (사용 ${_spent_usd:.2f}), 나머지는 다음 실행에서")
    if _has_api() and not _api_blocked and month_cap_reached():
        _api_blocked = True
    if _has_api() and not _api_blocked:
        try:
            return _run(system, user, model, timeout, use_api=True)
        except UsageLimit as exc:
            _api_blocked = True
            print(f"[llm] API 크레딧 사용 불가, Max 구독으로 전환: {str(exc)[:120]}", flush=True)
    if _has_max() and not _max_blocked:
        try:
            return _run(system, user, model, timeout, use_api=False)
        except UsageLimit:
            _max_blocked = True
            raise
    raise UsageLimit("API 크레딧과 Max 구독 사용량이 모두 소진되어 이번 실행을 멈춥니다")
