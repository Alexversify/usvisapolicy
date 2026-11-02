"""비자 문호(Visa Bulletin) 전용 페이지. /<lang>/visa-bulletin/ (최신 달), /<lang>/visa-bulletin/<YYYY-MM>.html (달별).

데이터는 data/visa_bulletin/<YYYY-MM>.json (sources.collect_vb_mirror 가 저장). 표 4개(가족·취업 x 최종조치일·접수가능일),
전월 대비 변동, USCIS 지정 차트를 5개 언어로 보여줍니다.
"""

from __future__ import annotations

import datetime as dt
import html
import json
from typing import Any

from src import store

e = html.escape
VB_DIR = store.DATA / "visa_bulletin"
COLS = ["row", "china", "india", "mexico", "philippines"]
CHARTS = [("fam", "final"), ("fam", "filing"), ("emp", "final"), ("emp", "filing")]

T: dict[str, dict[str, str]] = {
    "nav": {"ko": "비자 문호", "en": "Visa Bulletin", "es": "Boletín de Visas", "zh": "签证排期", "ja": "ビザ・ブリテン"},
    "h1": {"ko": "{m} 비자 문호", "en": "Visa Bulletin for {m}", "es": "Boletín de Visas de {m}", "zh": "{m}签证排期", "ja": "{m}のビザ・ブリテン"},
    "desc": {
        "ko": "{m} 미 국무부 비자 문호(Visa Bulletin). 가족·취업 이민 최종조치일과 접수가능일 전체 표, 전월 대비 변동, USCIS 지정 차트.",
        "en": "Visa Bulletin for {m}: full family and employment Final Action and Dates for Filing charts, month-over-month changes and the USCIS chart designation.",
        "es": "Boletín de Visas de {m}: tablas completas de fechas de acción final y de presentación, familiares y de empleo, cambios respecto al mes anterior y la tabla designada por USCIS.",
        "zh": "{m}美国国务院签证排期：家庭与职业移民的最终裁决日和递件日完整表格、与上月相比的变化，以及 USCIS 指定表格。",
        "ja": "{m}の米国務省ビザ・ブリテン。家族・雇用移民の最終処理日と申請受付日の全表、前月からの変動、USCIS指定チャート。",
    },
    "intro": {
        "ko": "미 국무부가 매달 발표하는 이민비자 순번 기준표입니다. 내 우선일(Priority Date)이 표의 날짜보다 앞서면 해당 단계로 진행할 수 있습니다. C는 대기 없음(Current), U는 이번 달 발급 불가(Unauthorized)입니다.",
        "en": "The State Department's monthly cutoff chart for immigrant visas. If your priority date is earlier than the date shown, you can move to that stage. C means current (no wait) and U means unauthorized this month.",
        "es": "La tabla mensual del Departamento de Estado con las fechas límite para visas de inmigrante. Si su fecha de prioridad es anterior a la fecha indicada, puede avanzar a esa etapa. C significa vigente (sin espera) y U, no autorizado este mes.",
        "zh": "美国国务院每月发布的移民签证排期表。如果您的优先日早于表中日期，即可进入相应阶段。C 表示无需排期（Current），U 表示本月不可签发（Unauthorized）。",
        "ja": "米国務省が毎月発表する移民ビザの順番待ち基準表です。優先日(Priority Date)が表の日付より前であれば、その段階に進めます。Cは待ちなし(Current)、Uは今月は発給不可(Unauthorized)です。",
    },
    "final": {"ko": "최종조치일 (Final Action Dates)", "en": "Final Action Dates", "es": "Fechas de acción final (Final Action Dates)", "zh": "最终裁决日（Final Action Dates）", "ja": "最終処理日（Final Action Dates）"},
    "filing": {"ko": "접수가능일 (Dates for Filing)", "en": "Dates for Filing", "es": "Fechas de presentación (Dates for Filing)", "zh": "递件日（Dates for Filing）", "ja": "申請受付日（Dates for Filing）"},
    "final_d": {
        "ko": "이민비자 발급과 영주권 승인이 가능한 기준일입니다.",
        "en": "The date before which an immigrant visa can be issued or a green card approved.",
        "es": "Fecha antes de la cual se puede emitir la visa de inmigrante o aprobar la residencia.",
        "zh": "优先日早于此日期即可签发移民签证或批准绿卡。",
        "ja": "移民ビザの発給とグリーンカードの承認が可能になる基準日です。",
    },
    "filing_d": {
        "ko": "서류 접수(국무부 NVC 서류 제출, 조건 충족 시 USCIS 신분조정 접수)를 시작할 수 있는 기준일입니다.",
        "en": "The date before which you can start filing (NVC documents, or adjustment of status when USCIS allows this chart).",
        "es": "Fecha antes de la cual puede empezar a presentar documentos (NVC, o ajuste de estatus si USCIS permite esta tabla).",
        "zh": "优先日早于此日期即可开始递交材料（向 NVC 递件，或在 USCIS 允许时递交身份调整）。",
        "ja": "書類提出（NVCへの提出、USCISが認める場合は身分調整申請）を始められる基準日です。",
    },
    "fam": {"ko": "가족 이민", "en": "Family-sponsored", "es": "Por familia", "zh": "亲属移民", "ja": "家族移民"},
    "emp": {"ko": "취업 이민", "en": "Employment-based", "es": "Por empleo", "zh": "职业移民", "ja": "雇用移民"},
    "col_cat": {"ko": "구분", "en": "Category", "es": "Categoría", "zh": "类别", "ja": "区分"},
    "row": {"ko": "일반 국가", "en": "All other countries", "es": "Resto de países", "zh": "其他国家", "ja": "一般の国"},
    "china": {"ko": "중국(본토)", "en": "China (mainland)", "es": "China (continental)", "zh": "中国（大陆）", "ja": "中国（本土）"},
    "india": {"ko": "인도", "en": "India", "es": "India", "zh": "印度", "ja": "インド"},
    "mexico": {"ko": "멕시코", "en": "Mexico", "es": "México", "zh": "墨西哥", "ja": "メキシコ"},
    "philippines": {"ko": "필리핀", "en": "Philippines", "es": "Filipinas", "zh": "菲律宾", "ja": "フィリピン"},
    "korea_note": {
        "ko": "한국 출생자는 '일반 국가' 열을 봅니다.",
        "en": "Applicants born in Korea use the “All other countries” column.",
        "es": "Los nacidos en Corea usan la columna “Resto de países”.",
        "zh": "韩国出生者请看“其他国家”一栏。",
        "ja": "韓国出生者は「一般の国」の列を見ます。",
    },
    "uscis": {
        "ko": "USCIS 지정 차트 (미국 내 신분조정 I-485): 가족 이민 {fam}, 취업 이민 {emp}",
        "en": "USCIS chart for adjustment of status (I-485): family {fam}, employment {emp}",
        "es": "Tabla de USCIS para ajuste de estatus (I-485): familiar {fam}, empleo {emp}",
        "zh": "USCIS 指定表格（境内身份调整 I-485）：亲属移民 {fam}，职业移民 {emp}",
        "ja": "USCIS指定チャート（米国内の身分調整 I-485）：家族移民 {fam}、雇用移民 {emp}",
    },
    "u_final": {"ko": "최종조치일", "en": "Final Action Dates", "es": "acción final", "zh": "最终裁决日", "ja": "最終処理日"},
    "u_filing": {"ko": "접수가능일", "en": "Dates for Filing", "es": "fechas de presentación", "zh": "递件日", "ja": "申請受付日"},
    "u_none": {"ko": "발표 전", "en": "not yet announced", "es": "aún no anunciada", "zh": "尚未公布", "ja": "未発表"},
    "adv": {"ko": "▲ {d}일 전진", "en": "▲ {d} days", "es": "▲ {d} días", "zh": "▲ 前进{d}天", "ja": "▲ {d}日前進"},
    "ret": {"ko": "▼ {d}일 후퇴", "en": "▼ {d} days", "es": "▼ {d} días", "zh": "▼ 倒退{d}天", "ja": "▼ {d}日後退"},
    "chg": {"ko": "변동", "en": "changed", "es": "cambio", "zh": "变动", "ja": "変動"},
    "legend": {
        "ko": "▲ 전월보다 전진, ▼ 전월보다 후퇴. 표시 없는 칸은 변동 없음.",
        "en": "▲ advanced, ▼ retrogressed compared with the previous month. Unmarked cells did not change.",
        "es": "▲ avanzó, ▼ retrocedió respecto al mes anterior. Las celdas sin marca no cambiaron.",
        "zh": "▲ 较上月前进，▼ 较上月倒退。未标注表示无变化。",
        "ja": "▲ 前月より前進、▼ 前月より後退。表示のない欄は変動なし。",
    },
    "summary": {"ko": "이번 달 요약", "en": "This month at a glance", "es": "Resumen del mes", "zh": "本月概要", "ja": "今月の概要"},
    "s_adv": {"ko": "전진 {n}칸", "en": "{n} cells advanced", "es": "{n} celdas avanzaron", "zh": "前进 {n} 项", "ja": "前進 {n}件"},
    "s_ret": {"ko": "후퇴 {n}칸", "en": "{n} cells retrogressed", "es": "{n} celdas retrocedieron", "zh": "倒退 {n} 项", "ja": "後退 {n}件"},
    "s_none": {"ko": "전월과 같음", "en": "No change from last month", "es": "Sin cambios respecto al mes anterior", "zh": "与上月相同", "ja": "前月と同じ"},
    "months": {"ko": "다른 달", "en": "Other months", "es": "Otros meses", "zh": "其他月份", "ja": "他の月"},
    "official": {"ko": "국무부 원문", "en": "Official bulletin", "es": "Boletín oficial", "zh": "国务院原文", "ja": "国務省原文"},
    "article": {"ko": "해설 기사와 원문 전문 번역", "en": "Explainer and full text", "es": "Explicación y texto completo", "zh": "解读文章与原文全文翻译", "ja": "解説記事と原文全文翻訳"},
    "note": {
        "ko": "표는 국무부 원문 수치를 그대로 옮긴 것입니다. 실제 진행 가능 여부는 국무부 원문과 USCIS 안내로 확인하십시오.",
        "en": "Figures are taken as published by the State Department. Confirm eligibility with the official bulletin and USCIS guidance.",
        "es": "Las cifras se toman tal como las publica el Departamento de Estado. Confirme con el boletín oficial y las indicaciones de USCIS.",
        "zh": "表中数字按美国国务院原文转载。实际能否推进，请以国务院原文和 USCIS 公告为准。",
        "ja": "表は国務省原文の数値をそのまま掲載しています。実際に進めるかどうかは国務省原文とUSCISの案内で確認してください。",
    },
    "empty": {"ko": "아직 수집된 비자 문호가 없습니다.", "en": "No Visa Bulletin collected yet.", "es": "Aún no hay boletines.", "zh": "暂无签证排期数据。", "ja": "まだビザ・ブリテンがありません。"},
}

ROW_DESC: dict[str, dict[str, str]] = {
    "F1": {"ko": "시민권자의 21세 이상 미혼 자녀", "en": "Unmarried sons and daughters (21+) of U.S. citizens", "es": "Hijos solteros (21+) de ciudadanos", "zh": "公民的21岁以上未婚子女", "ja": "市民の21歳以上の未婚の子"},
    "F2A": {"ko": "영주권자의 배우자와 21세 미만 자녀", "en": "Spouses and children (under 21) of permanent residents", "es": "Cónyuges e hijos (menores de 21) de residentes", "zh": "绿卡持有人的配偶及21岁以下子女", "ja": "永住者の配偶者と21歳未満の子"},
    "F2B": {"ko": "영주권자의 21세 이상 미혼 자녀", "en": "Unmarried sons and daughters (21+) of permanent residents", "es": "Hijos solteros (21+) de residentes", "zh": "绿卡持有人的21岁以上未婚子女", "ja": "永住者の21歳以上の未婚の子"},
    "F3": {"ko": "시민권자의 기혼 자녀", "en": "Married sons and daughters of U.S. citizens", "es": "Hijos casados de ciudadanos", "zh": "公民的已婚子女", "ja": "市民の既婚の子"},
    "F4": {"ko": "시민권자의 형제자매", "en": "Brothers and sisters of adult U.S. citizens", "es": "Hermanos de ciudadanos adultos", "zh": "成年公民的兄弟姐妹", "ja": "成人市民の兄弟姉妹"},
    "EB1": {"ko": "1순위: 특기자, 저명 교수·연구원, 다국적 기업 임원", "en": "1st: extraordinary ability, outstanding researchers, multinational executives", "es": "1.ª: habilidad extraordinaria, investigadores, ejecutivos multinacionales", "zh": "第一优先：杰出人才、杰出研究人员、跨国公司高管", "ja": "第1優先：卓越した能力者、著名研究者、多国籍企業の管理職"},
    "EB2": {"ko": "2순위: 석사 이상 전문직, 특출한 능력자 (NIW 포함)", "en": "2nd: advanced degree or exceptional ability (incl. NIW)", "es": "2.ª: título avanzado o habilidad excepcional (incl. NIW)", "zh": "第二优先：高学历或特殊能力（含 NIW）", "ja": "第2優先：修士以上の専門職、特別な能力者（NIW含む）"},
    "EB3": {"ko": "3순위: 숙련공·학사 전문직", "en": "3rd: skilled workers and professionals", "es": "3.ª: trabajadores calificados y profesionales", "zh": "第三优先：技术工人与专业人员", "ja": "第3優先：熟練労働者・学士専門職"},
    "EW": {"ko": "3순위 비숙련 근로자", "en": "3rd: other (unskilled) workers", "es": "3.ª: otros trabajadores (no calificados)", "zh": "第三优先：非技术工人", "ja": "第3優先：非熟練労働者"},
    "EB4": {"ko": "4순위: 특별 이민", "en": "4th: certain special immigrants", "es": "4.ª: inmigrantes especiales", "zh": "第四优先：特殊移民", "ja": "第4優先：特別移民"},
    "RW": {"ko": "종교 종사자", "en": "Certain religious workers", "es": "Trabajadores religiosos", "zh": "宗教工作者", "ja": "宗教従事者"},
    "EB5U": {"ko": "투자이민 비지정 (Unreserved)", "en": "5th: investors, unreserved", "es": "5.ª: inversionistas, no reservada", "zh": "第五优先：投资移民，非预留", "ja": "第5優先：投資移民（非指定枠）"},
    "EB5R": {"ko": "투자이민 지정: 농촌 (20%)", "en": "5th set-aside: rural (20%)", "es": "5.ª reservada: rural (20%)", "zh": "第五优先预留：农村（20%）", "ja": "投資移民指定枠：農村（20%）"},
    "EB5H": {"ko": "투자이민 지정: 고실업 지역 (10%)", "en": "5th set-aside: high unemployment (10%)", "es": "5.ª reservada: alto desempleo (10%)", "zh": "第五优先预留：高失业区（10%）", "ja": "投資移民指定枠：高失業地域（10%）"},
    "EB5I": {"ko": "투자이민 지정: 인프라 (2%)", "en": "5th set-aside: infrastructure (2%)", "es": "5.ª reservada: infraestructura (2%)", "zh": "第五优先预留：基础设施（2%）", "ja": "投資移民指定枠：インフラ（2%）"},
}
ROW_CODE = {"EB1": "EB-1", "EB2": "EB-2", "EB3": "EB-3", "EW": "EW", "EB4": "EB-4", "RW": "RW",
            "EB5U": "EB-5", "EB5R": "EB-5", "EB5H": "EB-5", "EB5I": "EB-5"}

ES_MONTHS = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
EN_MONTHS = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
EN_MON3 = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def t(key: str, lang: str) -> str:
    v = T[key]
    return v.get(lang) or v["en"]


def month_label(y: int, m: int, lang: str) -> str:
    if lang == "ko":
        return f"{y}년 {m}월"
    if lang in ("zh", "ja"):
        return f"{y}年{m}月"
    if lang == "es":
        return f"{ES_MONTHS[m]} de {y}"
    return f"{EN_MONTHS[m]} {y}"


def cell_date(v: str, lang: str) -> str:
    try:
        d = dt.date.fromisoformat(v)
    except (TypeError, ValueError):
        return v or ""
    if lang in ("ko", "zh", "ja"):
        return f"{d.year}.{d.month:02d}.{d.day:02d}"
    if lang == "es":
        return f"{d.day:02d}/{d.month:02d}/{d.year}"
    return f"{EN_MON3[d.month]} {d.day}, {d.year}"


def load_all() -> list[dict[str, Any]]:
    if not VB_DIR.exists():
        return []
    out = []
    for p in sorted(VB_DIR.glob("????-??.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if len(d.get("charts") or {}) >= 4:
            out.append(d)
    return out


def _table(lang: str, rec: dict[str, Any], group: str, kind: str) -> str:
    key = f"{group}_{kind}"
    chart = (rec.get("charts") or {}).get(key) or {}
    chg = {(c.get("row"), c.get("col")): c for c in rec.get("changes") or [] if c.get("chart") == key}
    head = "".join(f"<th>{e(t(c, lang))}</th>" for c in COLS)
    rows = []
    for code, vals in chart.items():
        desc = (ROW_DESC.get(code) or {}).get(lang) or (ROW_DESC.get(code) or {}).get("en") or ""
        label = code if code.startswith("F") else ROW_CODE.get(code, code)
        tds = []
        for i, col in enumerate(COLS):
            v = vals[i] if i < len(vals) else ""
            c = chg.get((code, col))
            mark, cls = "", ""
            if c and c.get("kind") in ("adv", "ret") and c.get("d"):
                cls = " class=\"" + ("up" if c["kind"] == "adv" else "down") + "\""
                mark = f'<small>{e(t(c["kind"], lang).format(d=c["d"]))}</small>'
            elif c:
                cls, mark = ' class="up"', f'<small>{e(t("chg", lang))}</small>'
            tds.append(f"<td{cls}><b>{e(cell_date(v, lang))}</b>{mark}</td>")
        rows.append(f'<tr><th scope="row"><b>{e(label)}</b><span>{e(desc)}</span></th>{"".join(tds)}</tr>')
    return (f'<section class="vb-chart"><h3>{e(t(group, lang))} · {e(t(kind, lang))}</h3><p class="vb-d">{e(t(kind + "_d", lang))}</p>'
            f'<div class="vb-scroll"><table><thead><tr><th>{e(t("col_cat", lang))}</th>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div></section>')


def page_body(lang: str, rec: dict[str, Any], recs: list[dict[str, Any]], up: str, article_href: str | None) -> str:
    y, m = int(rec["year"]), int(rec["month"])
    changes = rec.get("changes") or []
    n_adv = sum(1 for c in changes if c.get("kind") == "adv")
    n_ret = sum(1 for c in changes if c.get("kind") == "ret")
    chips = []
    if n_adv:
        chips.append(f'<span class="vb-chip up">{e(t("s_adv", lang).format(n=n_adv))}</span>')
    if n_ret:
        chips.append(f'<span class="vb-chip down">{e(t("s_ret", lang).format(n=n_ret))}</span>')
    if not chips:
        chips.append(f'<span class="vb-chip">{e(t("s_none", lang))}</span>')
    u = rec.get("uscis") or {}

    def uname(v: Any) -> str:
        return t("u_final", lang) if v == "final" else t("u_filing", lang) if v == "filing" else t("u_none", lang)

    uscis = f'<p class="vb-uscis">{e(t("uscis", lang).format(fam=uname(u.get("family")), emp=uname(u.get("employment"))))}</p>' if isinstance(u, dict) else ""
    months = "".join(
        f'<a href="{r["key"]}.html"{" aria-current=\"page\"" if r["key"] == rec["key"] else ""}>{e(month_label(int(r["year"]), int(r["month"]), lang))}</a>'
        for r in reversed(recs))
    links = [f'<a class="btn" href="{e(rec.get("source_url") or "")}" rel="noopener" target="_blank">{e(t("official", lang))} ↗</a>']
    if article_href:
        links.insert(0, f'<a class="btn" href="{e(article_href)}">{e(t("article", lang))}</a>')
    tables = "".join(_table(lang, rec, g, k) for g, k in CHARTS)
    return f"""<main class="wrap vb">
<section class="hero"><h1>{e(t("h1", lang).format(m=month_label(y, m, lang)))}</h1><p>{e(t("intro", lang))}</p></section>
<div class="vb-top"><div><b>{e(t("summary", lang))}</b> {"".join(chips)}</div>{uscis}<p class="vb-k">{e(t("korea_note", lang))}</p></div>
{tables}
<p class="vb-legend">{e(t("legend", lang))}</p>
<div class="vb-links">{"".join(links)}</div>
<nav class="vb-months" aria-label="{e(t("months", lang))}"><b>{e(t("months", lang))}</b>{months}</nav>
<p class="note">{e(t("note", lang))}</p>
</main>"""


CSS = r"""
.navlink{font-size:14px;font-weight:700;color:var(--ink);text-decoration:none;padding:6px 10px;border-radius:999px;border:1px solid var(--rule);background:var(--paper);white-space:nowrap}
.navlink[aria-current="page"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
header.top .brand{margin-right:auto}
@media (max-width:620px){header.top .langs{width:100%}}
.vb .hero p{color:var(--ink-2);max-width:760px}
.vb-top{display:flex;flex-direction:column;gap:8px;background:var(--paper);border:1px solid var(--rule);border-radius:12px;padding:14px 16px;margin:6px 0 18px}
.vb-chip{display:inline-block;font-size:13px;padding:3px 10px;border-radius:999px;background:var(--chip);color:var(--ink-2);margin:2px 4px 2px 0}
.vb-chip.up{background:#e7f6ec;color:#146c2e}.vb-chip.down{background:var(--hot-bg);color:var(--hot)}
.vb-uscis,.vb-k{margin:0;font-size:14px;color:var(--ink-2)}
.vb-chart{margin:26px 0}
.vb-chart h3{font-size:18px;margin:0 0 4px}
.vb-d{margin:0 0 10px;color:var(--muted);font-size:14px}
.vb-scroll{overflow-x:auto;border:1px solid var(--rule);border-radius:12px;background:var(--paper)}
.vb table{border-collapse:collapse;width:100%;min-width:640px;font-size:14px}
.vb th,.vb td{padding:9px 10px;border-bottom:1px solid var(--hair);text-align:left;vertical-align:top}
.vb thead th{background:var(--chip);font-size:13px;color:var(--ink-2);white-space:nowrap}
.vb tbody th{font-weight:400;min-width:180px;position:sticky;left:0;background:var(--paper);z-index:1}
.vb thead th:first-child{position:sticky;left:0;z-index:2}
@media (max-width:620px){.vb tbody th{min-width:128px;max-width:150px}}
.vb tbody th b{display:block;font-size:14px}
.vb tbody th span{display:block;font-size:12px;color:var(--muted);line-height:1.4}
.vb td b{display:block;font-variant-numeric:tabular-nums;white-space:nowrap;font-weight:600}
.vb td small{display:block;font-size:11.5px;white-space:nowrap}
.vb td.up{background:rgba(22,163,74,.08)}.vb td.up small{color:#15803d}
.vb td.down{background:rgba(220,38,38,.08)}.vb td.down small{color:var(--hot)}
.vb-legend{font-size:13px;color:var(--muted)}
.vb-links{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}
.vb-months{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:18px 0}
.vb-months b{margin-right:6px;font-size:14px}
.vb-months a{font-size:13px;padding:5px 10px;border:1px solid var(--rule);border-radius:999px;text-decoration:none;color:var(--ink-2);background:var(--paper)}
.vb-months a[aria-current="page"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .vb-chip.up{background:#12301e;color:#7ee2a0}:root:not([data-theme="light"]) .vb td.up small{color:#7ee2a0}}
"""
