"""Claude로 원문을 5개 언어 기사로 만듭니다.

원문 번역문을 통째로 싣지 않습니다. 정부 공지는 길고 반복이 많아 아무도 끝까지 읽지 않습니다.
언어별로 제목, 요약, 핵심 포인트, 영향 대상만 만들고 원문 링크를 반드시 붙입니다.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

LANG_NAMES = {
    "ko": "Korean",
    "en": "English",
    "es": "Spanish (neutral Latin American)",
    "zh": "Simplified Chinese",
    "ja": "Japanese",
}

SYSTEM = """You are the editor of usvisapolicy.com, a multilingual newsroom that explains official U.S. immigration
announcements (USCIS, the Department of State, the Federal Register, presidential proclamations) to
applicants, employers and attorneys. The site is operated by a Korean law firm.

Rules:
- Use only facts in the source. Never invent dates, fees, form numbers, or eligibility rules.
  If something is unclear in the source, say it is not specified.
- Keep legal terms precise. Keep form numbers (I-129, DS-160), visa classes (H-1B, EB-5) and agency
  names in their original Latin form in every language.
- Neutral, factual newsroom tone. No hype, no advice phrased as legal advice.
- Proposed rules are not law. Say clearly that the change is only proposed, not final or in effect, and give
  the comment deadline if the source states it. If the source says it was filed for public inspection, say it is
  scheduled to be published in the Federal Register.
- For fees, always state who pays (applicant, employer, school, sponsor) and when, if the source says so.
- Never use the em dash character. Use commas or periods.
- In Korean, never use the word "아울러". Write natural Korean news style (~다/~습니다 consistent within an article, prefer ~습니다).
- Each language version must be written natively, not a word-for-word translation.

Return ONLY a JSON object, no code fences, in this exact shape:
{
  "relevant": true,
  "published": "YYYY-MM-DD or null (publication date stated in the source)",
  "effective_date": "YYYY-MM-DD or null (when the change takes effect, if stated)",
  "importance": "high | medium | low",
  "category": "policy | fees | processing | enforcement | notice",
  "agency": "uscis | state | dhs | ice | cbp | dol | doj | president | courts | other",
  "topics": ["1 to 3 of: h1b, students, employment, eb5, family, citizenship, humanitarian, travel, visa_bulletin, fees, enforcement, other"],
  "tags": ["short English tags such as H-1B, EB-5, Fees, Visa Bulletin, Travel Ban, TPS, Naturalization"],
  "langs": {
    "<lang code>": {
      "title": "clear headline, max ~90 characters",
      "summary": "2 to 3 sentence summary",
      "points": ["3 to 6 key points, each one sentence"],
      "who": "one sentence on who is affected",
      "action": "one sentence on what affected people should do next, or empty string if nothing"
    }
  }
}
category:
- policy: new or changed rules, eligibility, policy manual updates, proclamations, executive orders, travel/entry restrictions, Visa Bulletin
- fees: filing fees, visa fees, fee schedules, payment changes
- processing: caps, filing locations, forms, processing times, appointments, system or operational notices
- enforcement: fraud, criminal cases, arrests, prosecutions, denaturalization, investigations
- notice: anything else (public access, delegations, general announcements)
importance high = changes eligibility, fees, travel/entry, or deadlines for many people.
agency = the body whose action this is (who issued the rule, order or announcement), not who reposted it:
- uscis: USCIS. state: Department of State (visas, consular, Visa Bulletin, FTO designations).
- dhs: DHS headquarters or the DHS Secretary. ice: ICE, including SEVP. cbp: CBP.
- dol: Department of Labor (PERM, LCA, prevailing wage). doj: DOJ, EOIR, immigration courts, Attorney General.
- president: proclamations, executive orders, presidential determinations. courts: federal court rulings.
topics (most specific first, at most 3):
- h1b: H-1B and specialty occupation workers. students: F-1, J-1, M-1, OPT, STEM OPT, SEVP/SEVIS.
- employment: other work visas and employment-based immigration (H-2A/B, L-1, O-1, EB-1/2/3, PERM, EAD, grace periods).
- eb5: EB-5 investors. family: family-based immigration, adjustment of status, green cards, diversity visa, public charge.
- citizenship: naturalization, N-400, denaturalization, citizenship claims, birthright.
- humanitarian: refugees, asylum, TPS, parole. travel: entry restrictions, travel bans, visa issuance, consular processing, ESTA, I-94.
- visa_bulletin: Visa Bulletin and priority dates. fees: any fee change. enforcement: arrests, removals, fraud, prosecutions, border enforcement.
- other: none of the above.
relevant = false when the document has no real bearing on U.S. visas, immigration, entry, citizenship or
immigration enforcement (for example energy, trade or commemorative proclamations that only mention
immigration in passing). Still fill every other field.
"""


def _client():
    import anthropic

    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def enabled() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def build(item: dict[str, Any], text: str, langs: list[str], model: str, source_label: str) -> dict[str, Any] | None:
    """기사 JSON을 돌려줍니다. 실패하면 None (다음 실행에서 재시도)."""
    wanted = ", ".join(f"{c} ({LANG_NAMES.get(c, c)})" for c in langs)
    user = (
        f"Languages to produce (keys of langs): {wanted}\n"
        f"Source: {source_label}\n"
        f"Original title: {item.get('title')}\n"
        f"URL: {item.get('url')}\n"
        f"Listed date: {item.get('published') or 'unknown'}\n\n"
        f"--- SOURCE TEXT ---\n{text[:16000]}"
    )
    try:
        msg = _client().messages.create(
            model=model,
            max_tokens=8000,
            system=SYSTEM,
            messages=[{"role": "user", "content": user}],
        )
    except Exception as exc:  # noqa: BLE001
        print(f"    ! API 오류: {exc}")
        return None
    raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.S)
        if not m:
            print("    ! 응답 파싱 실패")
            return None
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            print("    ! 응답 파싱 실패")
            return None
    missing = [c for c in langs if c not in (data.get("langs") or {})]
    if missing:
        print(f"    ! 언어 누락: {missing}")
        return None
    # 사용자 문체 규칙을 한 번 더 강제합니다.
    for loc in data["langs"].values():
        for k, v in list(loc.items()):
            if isinstance(v, str):
                loc[k] = v.replace("—", ", ").replace("아울러 ", "").replace("아울러", "")
            elif isinstance(v, list):
                loc[k] = [s.replace("—", ", ").replace("아울러 ", "") for s in v if isinstance(s, str)]
    return data


CATEGORIES = ["policy", "fees", "processing", "enforcement", "notice"]

CLASSIFY_SYSTEM = """Classify each U.S. immigration news item into exactly one category:
policy (rules, eligibility, policy changes, proclamations, entry restrictions, Visa Bulletin),
fees (filing or visa fees), processing (caps, forms, filing locations, processing, operations),
enforcement (fraud, criminal cases, prosecutions, denaturalization), notice (anything else).
Return ONLY a JSON object mapping id to category. No code fences."""


def classify(items: list[dict[str, str]], model: str) -> dict[str, str]:
    """카테고리가 없는 기존 기사를 한 번에 분류합니다. items: [{id, title, summary}]"""
    if not items:
        return {}
    try:
        msg = _client().messages.create(
            model=model,
            max_tokens=2000,
            system=CLASSIFY_SYSTEM,
            messages=[{"role": "user", "content": json.dumps(items, ensure_ascii=False)}],
        )
        raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        m = re.search(r"\{.*\}", raw, re.S)
        data = json.loads(m.group(0)) if m else {}
    except Exception as exc:  # noqa: BLE001
        print(f"    ! 분류 실패: {exc}")
        return {}
    return {k: v for k, v in data.items() if v in CATEGORIES}
