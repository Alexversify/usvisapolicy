"""기관·주제 분류.

번역 단계에서 Claude가 agency, topics 를 고릅니다. 그 값이 없는 기사(예전 기사)는
rule_classify 로 출처와 태그·제목에서 임시로 채우고, 다음 수집 때 Claude가 다시 분류합니다.
"""

from __future__ import annotations

import re
from typing import Any

from src.i18n import AGENCY_ORDER, TOPIC_ORDER

AGENCIES = AGENCY_ORDER
TOPICS = TOPIC_ORDER

SOURCE_AGENCY = {
    "uscis_news": "uscis", "uscis_policy_manual": "uscis", "uscis_vb_chart": "uscis", "dos_visa_news": "state", "visa_bulletin": "state",
    "state_press": "state", "dhs_news": "dhs", "presidential": "president",
}

# (주제, 정규식). 앞에서부터 맞는 것을 최대 3개.
TOPIC_RULES = [
    ("visa_bulletin", r"visa bulletin|priority date|dates for filing|final action date"),
    ("h1b", r"\bh-1b\b|specialty occupation|labor condition application"),
    ("students", r"\bopt\b|optional practical training|\bf-1\b|\bj-1\b|student|sevp|sevis|exchange visitor"),
    ("eb5", r"\beb-5\b|regional center|immigrant investor"),
    ("employment", r"\bh-2[ab]?\b|\beb-[1-4]\b|perm|labor certification|employment authorization|\bead\b|i-140|i-129|employment-based"),
    ("humanitarian", r"refugee|asylum|\btps\b|temporary protected|parole|humanitarian"),
    ("citizenship", r"naturaliz|citizenship|denaturaliz|n-400|birthright|born in the united states"),
    ("family", r"adjustment of status|i-485|green card|permanent resid|family|spouse|diversity visa|public charge|\blpr\b"),
    ("travel", r"entry|travel ban|proclamation|visa issuance|consular|visa bond|visa waiver|esta|i-94|restriction on entry|terrorist organization"),
    ("fees", r"\bfees?\b|inflation adjust|\$\d"),
    ("enforcement", r"fraud|arrest|charged|indict|convict|sentenc|deport|removal|detain|illegal alien|smuggl|voting|enforcement|worst of the worst"),
]


def rule_classify(a: dict[str, Any]) -> tuple[str, list[str]]:
    en = (a.get("langs") or {}).get("en") or {}
    text = " ".join([a.get("original_title", ""), en.get("title", ""), en.get("summary", ""), " ".join(a.get("tags", []))]).lower()
    ag = SOURCE_AGENCY.get(a.get("source", ""))
    if not ag:
        for key, pat in [("ice", r"\bice\b|immigration and customs enforcement|sevp"), ("cbp", r"\bcbp\b|customs and border"),
                         ("dol", r"department of labor|\bdol\b|employment and training"), ("doj", r"eoir|immigration court|attorney general|justice"),
                         ("courts", r"district court|court order|enjoin"), ("state", r"department of state|state department|secretary of state"),
                         ("uscis", r"uscis|citizenship and immigration services"), ("dhs", r"homeland security|\bdhs\b")]:
            if re.search(pat, text):
                ag = key
                break
    topics = [k for k, pat in TOPIC_RULES if re.search(pat, text)][:3]
    return ag or "other", topics or ["other"]


def clean(agency: Any, topics: Any) -> tuple[str | None, list[str]]:
    ag = agency if agency in AGENCIES else None
    tp = [t for t in (topics or []) if t in TOPICS][:3] if isinstance(topics, list) else []
    return ag, tp
