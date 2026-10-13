"""Claude 호출 공용 함수.

순서: API 크레딧(ANTHROPIC_API_KEY) → 부족하면 Max 구독(CLAUDE_CODE_OAUTH_TOKEN) → 둘 다 소진되면 중단.
두 경우 모두 Claude Code CLI(`claude -p`)로 실행합니다. CLI는 API 키가 있으면 그걸 먼저 쓰므로,
구독으로 돌릴 때는 하위 프로세스 환경에서 API 키를 뺍니다.
크레딧이 바닥나도 카드 결제로 넘어가지 않게 하려면 Anthropic 콘솔에서 자동 충전(Auto-reload)을 꺼 두세요.
"""
from __future__ import annotations

import json
import os
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


def _has_api() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _has_max() -> bool:
    return bool(os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"))


def enabled() -> bool:
    return (_has_api() or _has_max()) and shutil.which("claude") is not None


def blocked() -> bool:
    return (_api_blocked or not _has_api()) and (_max_blocked or not _has_max())


def _run(system: str, user: str, model: str, timeout: int, use_api: bool) -> str:
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
