"""Claude 호출 공용 함수.

API 키(ANTHROPIC_API_KEY)를 쓰지 않습니다. Claude Code CLI(`claude -p`)를 구독 토큰
(CLAUDE_CODE_OAUTH_TOKEN, `claude setup-token` 으로 발급)으로 실행해 Max 플랜 사용량 안에서 처리합니다.
API 키가 환경에 있어도 하위 프로세스에는 넘기지 않습니다 (CLI는 API 키를 우선하기 때문).
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
    """구독 사용량 한도에 걸림. 이번 실행은 번역을 멈추고 다음 실행에 넘깁니다."""


_LIMIT_HINTS = ("usage limit", "rate limit", "limit reached", "429", "overloaded", "quota")
_blocked = False


def enabled() -> bool:
    return bool(os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")) and shutil.which("claude") is not None


def blocked() -> bool:
    return _blocked


def complete(system: str, user: str, model: str, timeout: int = 600) -> str:
    """system/user 한 번 주고 텍스트 답을 받습니다. 도구·CLAUDE.md·MCP 없이 순수 생성만 합니다."""
    global _blocked
    if _blocked:
        raise UsageLimit("이번 실행에서 이미 사용량 한도에 걸렸습니다")
    if not enabled():
        raise LLMError("CLAUDE_CODE_OAUTH_TOKEN 또는 claude CLI 없음")
    env = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
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
            _blocked = True
            raise UsageLimit(detail)
        raise LLMError(f"claude CLI 실패 (code {proc.returncode}): {detail}")
    return text
