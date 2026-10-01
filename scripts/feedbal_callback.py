"""처리 결과를 feedbal.com 에 회신합니다. FEEDBAL_CALLBACK_URL 이 있을 때만 실행됩니다."""
import json
import os
import urllib.request

body = json.dumps({
    "site_key": "usvisapolicy",
    "feedback_id": os.environ.get("FID"),
    "status": "pr_opened" if os.environ.get("PR_URL") else ("no_change" if os.environ.get("STATUS") == "success" else "failed"),
    "pr_url": os.environ.get("PR_URL") or None,
    "run_url": os.environ.get("RUN_URL"),
}).encode()
req = urllib.request.Request(
    os.environ["FEEDBAL_CALLBACK_URL"], data=body, method="POST",
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {os.environ.get('CALLBACK_TOKEN', '')}"},
)
try:
    print(urllib.request.urlopen(req, timeout=20).status)
except Exception as e:  # noqa: BLE001
    print("callback failed:", e)
