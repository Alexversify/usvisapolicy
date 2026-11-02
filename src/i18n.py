"""화면 문구. 언어를 추가하려면 각 키에 값을 넣고 settings.yaml languages에 코드를 추가합니다."""

from __future__ import annotations

LANG_LABEL = {"ko": "한국어", "en": "English", "es": "Español", "zh": "中文", "ja": "日本語"}
HTML_LANG = {"ko": "ko", "en": "en", "es": "es", "zh": "zh-Hans", "ja": "ja"}

T: dict[str, dict[str, str]] = {
    "tagline": {
        "ko": "USCIS·국무부 이민 정책 업데이트를 5개 언어로",
        "en": "USCIS and State Department policy updates in five languages",
        "es": "Novedades de USCIS y el Departamento de Estado en cinco idiomas",
        "zh": "以五种语言追踪 USCIS 与美国国务院移民政策更新",
        "ja": "USCIS・米国務省の移民政策アップデートを5言語で",
    },
    "latest": {"ko": "최신 업데이트", "en": "Latest updates", "es": "Últimas novedades", "zh": "最新动态", "ja": "最新アップデート"},
    "all_sources": {"ko": "모든 출처", "en": "All sources", "es": "Todas las fuentes", "zh": "全部来源", "ja": "すべての出典"},
    "category": {"ko": "분류", "en": "Category", "es": "Categoría", "zh": "分类", "ja": "分類"},
    "all": {"ko": "전체", "en": "All", "es": "Todo", "zh": "全部", "ja": "すべて"},
    "search": {"ko": "검색 (예: H-1B, EB-5, 수수료)", "en": "Search (e.g. H-1B, EB-5, fees)", "es": "Buscar (p. ej. H-1B, EB-5, tarifas)", "zh": "搜索（如 H-1B、EB-5、费用）", "ja": "検索（例: H-1B、EB-5、手数料）"},
    "important": {"ko": "중요", "en": "Key", "es": "Clave", "zh": "重要", "ja": "重要"},
    "only_important": {"ko": "중요 건만", "en": "Key updates only", "es": "Solo clave", "zh": "仅看重要", "ja": "重要のみ"},
    "published": {"ko": "게시일", "en": "Published", "es": "Publicado", "zh": "发布日期", "ja": "公開日"},
    "effective": {"ko": "시행일", "en": "Effective", "es": "Vigencia", "zh": "生效日期", "ja": "施行日"},
    "key_points": {"ko": "핵심 내용", "en": "Key points", "es": "Puntos clave", "zh": "要点", "ja": "ポイント"},
    "who": {"ko": "영향 대상", "en": "Who is affected", "es": "A quién afecta", "zh": "影响对象", "ja": "対象者"},
    "action": {"ko": "확인할 일", "en": "What to do", "es": "Qué hacer", "zh": "建议行动", "ja": "取るべき対応"},
    "original": {"ko": "원문 보기", "en": "Read the official source", "es": "Ver la fuente oficial", "zh": "查看官方原文", "ja": "公式原文を見る"},
    "archived": {"ko": "원문이 내려간 경우 보관본 보기", "en": "Archived copy (if the original is removed)", "es": "Copia archivada (si se retira el original)", "zh": "原文删除时查看存档", "ja": "原文が削除された場合のアーカイブ"},
    "issues": {"ko": "주요 이슈", "en": "Key issues", "es": "Temas clave", "zh": "重点议题", "ja": "主要トピック"},
    "issues_hint": {"ko": "주제를 누르면 관련 소식만 모아 봅니다.", "en": "Tap a topic to see only related updates.", "es": "Toque un tema para ver solo sus novedades.", "zh": "点击主题，只看相关动态。", "ja": "トピックを押すと関連ニュースだけを表示します。"},
    "count": {"ko": "{n}건", "en": "{n} updates", "es": "{n} novedades", "zh": "{n} 条", "ja": "{n}件"},
    "all_agencies": {"ko": "모든 기관", "en": "All agencies", "es": "Todas las agencias", "zh": "全部机构", "ja": "すべての機関"},
    "more_topics": {"ko": "주제 {n}개 더 보기", "en": "Show {n} more topics", "es": "Ver {n} temas más", "zh": "再显示 {n} 个主题", "ja": "ほか{n}件のトピック"},
    "clear": {"ko": "전체 보기", "en": "Show all", "es": "Ver todo", "zh": "显示全部", "ja": "すべて表示"},
    "original_title": {"ko": "원문 제목", "en": "Original title", "es": "Título original", "zh": "原文标题", "ja": "原文タイトル"},
    "back": {"ko": "목록으로", "en": "All updates", "es": "Todas las novedades", "zh": "返回列表", "ja": "一覧へ"},
    "empty": {"ko": "아직 게시된 업데이트가 없습니다. 첫 수집이 끝나면 여기에 표시됩니다.", "en": "No updates yet. They will appear here after the first collection run.", "es": "Aún no hay novedades. Aparecerán aquí tras la primera recopilación.", "zh": "暂无更新。首次采集完成后将在此显示。", "ja": "まだ更新はありません。初回収集後にここに表示されます。"},
    "pg_prev": {"ko": "이전", "en": "Prev", "es": "Anterior", "zh": "上一页", "ja": "前へ"},
    "pg_next": {"ko": "다음", "en": "Next", "es": "Siguiente", "zh": "下一页", "ja": "次へ"},
    "pg_per": {"ko": "페이지당", "en": "Per page", "es": "Por página", "zh": "每页", "ja": "表示件数"},
    "pg_total": {"ko": "총 {n}건", "en": "{n} updates", "es": "{n} novedades", "zh": "共 {n} 条", "ja": "全{n}件"},
    "no_match": {"ko": "조건에 맞는 업데이트가 없습니다.", "en": "No updates match your filters.", "es": "Ninguna novedad coincide con los filtros.", "zh": "没有符合条件的更新。", "ja": "条件に合う更新はありません。"},
    "ai_note": {
        "ko": "이 글은 공식 발표를 요약·번역한 것입니다. 법적 효력은 영문 원문에만 있습니다.",
        "en": "This is a summary of the official announcement. Only the official source is authoritative.",
        "es": "Este es un resumen del anuncio oficial. Solo la fuente oficial tiene validez.",
        "zh": "本文根据官方公告摘要翻译，仅英文官方原文具有法律效力。",
        "ja": "本記事は公式発表を要約・翻訳したものです。法的効力は英語の公式原文のみにあります。",
    },
    "disclaimer": {
        "ko": "usvisapolicy.com은 미국 정부(USCIS, 국무부, 국토안보부 등)나 그 밖의 어느 나라 정부 기관이 운영하거나 승인한 사이트가 아닌 민간 정보 사이트입니다. 게시물은 공식 발표를 요약·번역한 것으로 오역, 누락, 지연이 있을 수 있으며 정확성과 최신성을 보장하지 않습니다. 이 사이트의 정보는 법률 자문이 아니며, 사이트 운영자는 이 정보를 이용해 생긴 결과에 책임을 지지 않습니다. 법적 효력은 공식 원문에만 있으므로, 중요한 판단 전에는 각 게시물의 원문 링크에서 공식 원문을 확인하십시오.",
        "en": "usvisapolicy.com is a private information site. It is not operated by, endorsed by, or affiliated with the U.S. government (including USCIS, the Department of State, and DHS) or any other government. Posts are summaries and translations of official releases and may contain translation errors, omissions, or delays; accuracy and timeliness are not guaranteed. Nothing on this site is legal advice, and the site operator accepts no liability for any outcome arising from its use. Only the official source text has legal effect. Before relying on any information, check the official original through the source link in each post.",
        "es": "usvisapolicy.com es un sitio informativo privado. No está operado, avalado ni afiliado con el gobierno de EE. UU. (incluidos USCIS, el Departamento de Estado y DHS) ni con ningún otro gobierno. Las publicaciones son resúmenes y traducciones de comunicados oficiales y pueden contener errores de traducción, omisiones o retrasos; no se garantiza su exactitud ni su actualidad. Nada de este sitio constituye asesoría legal, y el operador del sitio no asume responsabilidad por los resultados derivados de su uso. Solo el texto oficial original tiene efecto legal. Antes de tomar decisiones, consulte el original oficial mediante el enlace a la fuente de cada publicación.",
        "zh": "usvisapolicy.com 是民间信息网站，并非由美国政府（包括 USCIS、国务院、国土安全部等）或任何其他国家政府运营、认可或关联。帖子为对官方发布内容所作的摘要和翻译，可能存在误译、遗漏或延迟，不保证准确性和时效性。本网站内容不构成法律意见，网站运营方对因使用本网站信息而产生的任何结果不承担责任。只有官方原文具有法律效力。作出重要决定前，请通过每篇帖子中的原文链接查阅官方原文。",
        "ja": "usvisapolicy.com は民間の情報サイトであり、米国政府（USCIS、国務省、国土安全保障省など）やその他いずれの国の政府機関が運営・承認するものでも、関係するものでもありません。投稿は公式発表を要約・翻訳したもので、誤訳・欠落・遅れが含まれる場合があり、正確性と最新性は保証されません。本サイトの情報は法的助言ではなく、サイト運営者は本サイトの情報の利用により生じた結果について責任を負いません。法的効力を持つのは公式原文のみです。重要な判断の前に、各投稿の原文リンクから公式原文をご確認ください。",
    },
    "consult": {"ko": "이 변경이 내 케이스에 미치는 영향 상담하기", "en": "Ask how this affects your case", "es": "Consulte cómo afecta a su caso", "zh": "咨询此变化对您案件的影响", "ja": "ご自身のケースへの影響を相談する"},
    "contact": {"ko": "문의·건의", "en": "Contact & feedback", "es": "Contacto y sugerencias", "zh": "联系与建议", "ja": "お問い合わせ・ご意見"},
    "operated_by": {"ko": "운영", "en": "Operated by", "es": "Operado por", "zh": "运营方", "ja": "運営"},
    "updated": {"ko": "마지막 갱신", "en": "Last updated", "es": "Última actualización", "zh": "最后更新", "ja": "最終更新"},
    "feedback": {"ko": "피드백", "en": "Feedback", "es": "Comentarios", "zh": "反馈", "ja": "フィードバック"},
    "fb_title": {"ko": "피드백 보내기", "en": "Send feedback", "es": "Enviar comentarios", "zh": "发送反馈", "ja": "フィードバックを送る"},
    "fb_type": {"ko": "유형", "en": "Type", "es": "Tipo", "zh": "类型", "ja": "種類"},
    "fb_t_translation": {"ko": "번역 오류", "en": "Translation error", "es": "Error de traducción", "zh": "翻译错误", "ja": "翻訳の誤り"},
    "fb_t_content": {"ko": "내용 오류", "en": "Wrong information", "es": "Información incorrecta", "zh": "内容错误", "ja": "内容の誤り"},
    "fb_t_feature": {"ko": "기능·디자인 제안", "en": "Feature or design idea", "es": "Idea de función o diseño", "zh": "功能或设计建议", "ja": "機能・デザインの提案"},
    "fb_t_other": {"ko": "기타", "en": "Other", "es": "Otro", "zh": "其他", "ja": "その他"},
    "fb_msg": {"ko": "내용을 적어주세요", "en": "Tell us what to fix or add", "es": "Cuéntenos qué corregir o añadir", "zh": "请告诉我们需要修改或新增的内容", "ja": "修正・追加してほしい内容をご記入ください"},
    "fb_email": {"ko": "이메일 (선택, 회신용)", "en": "Email (optional)", "es": "Correo (opcional)", "zh": "邮箱（可选）", "ja": "メール（任意）"},
    "fb_send": {"ko": "보내기", "en": "Send", "es": "Enviar", "zh": "提交", "ja": "送信"},
    "fb_cancel": {"ko": "닫기", "en": "Close", "es": "Cerrar", "zh": "关闭", "ja": "閉じる"},
    "fb_ok": {"ko": "접수되었습니다. 감사합니다.", "en": "Received. Thank you.", "es": "Recibido. Gracias.", "zh": "已收到，谢谢。", "ja": "受け付けました。ありがとうございます。"},
    "fb_fail": {"ko": "전송에 실패해 메일 작성 화면을 엽니다.", "en": "Could not send. Opening your email app instead.", "es": "No se pudo enviar. Abriendo su correo.", "zh": "发送失败，将打开邮件应用。", "ja": "送信できませんでした。メールアプリを開きます。"},
    "rss": {"ko": "RSS", "en": "RSS", "es": "RSS", "zh": "RSS", "ja": "RSS"},
    "imp_high": {"ko": "중요", "en": "Key", "es": "Clave", "zh": "重要", "ja": "重要"},
}

CATEGORY_LABEL: dict[str, dict[str, str]] = {
    "policy": {"ko": "정책·규정", "en": "Policy & Rules", "es": "Políticas y normas", "zh": "政策法规", "ja": "政策・規則"},
    "fees": {"ko": "수수료", "en": "Fees", "es": "Tarifas", "zh": "费用", "ja": "手数料"},
    "processing": {"ko": "접수·처리", "en": "Filing & Processing", "es": "Trámites", "zh": "申请与处理", "ja": "申請・審査"},
    "enforcement": {"ko": "단속·사기", "en": "Enforcement & Fraud", "es": "Fraude y sanciones", "zh": "执法与欺诈", "ja": "取締り・不正"},
    "notice": {"ko": "공고·기타", "en": "Notices", "es": "Avisos", "zh": "公告", "ja": "告示・その他"},
}
CATEGORY_ORDER = ["policy", "fees", "processing", "enforcement", "notice"]

# 발표 기관. 번역 단계에서 Claude가 고르고, 없으면 taxonomy.rule_classify 가 출처로 채웁니다.
AGENCY_LABEL: dict[str, dict[str, str]] = {
    "uscis": {"ko": "이민국(USCIS)", "en": "USCIS", "es": "USCIS", "zh": "移民局 (USCIS)", "ja": "移民局 (USCIS)"},
    "state": {"ko": "국무부", "en": "State Dept.", "es": "Dpto. de Estado", "zh": "国务院", "ja": "国務省"},
    "dhs": {"ko": "국토안보부(DHS)", "en": "DHS", "es": "DHS", "zh": "国土安全部 (DHS)", "ja": "国土安全保障省 (DHS)"},
    "ice": {"ko": "이민세관단속국(ICE)", "en": "ICE", "es": "ICE", "zh": "移民海关执法局 (ICE)", "ja": "移民・関税執行局 (ICE)"},
    "cbp": {"ko": "세관국경보호청(CBP)", "en": "CBP", "es": "CBP", "zh": "海关与边境保护局 (CBP)", "ja": "税関・国境警備局 (CBP)"},
    "dol": {"ko": "노동부", "en": "Dept. of Labor", "es": "Dpto. de Trabajo", "zh": "劳工部", "ja": "労働省"},
    "doj": {"ko": "법무부·이민법원", "en": "DOJ / Immigration Courts", "es": "DOJ / Tribunales de Inmigración", "zh": "司法部·移民法院", "ja": "司法省・移民裁判所"},
    "president": {"ko": "대통령·백악관", "en": "White House", "es": "Casa Blanca", "zh": "总统·白宫", "ja": "大統領・ホワイトハウス"},
    "courts": {"ko": "연방법원", "en": "Federal courts", "es": "Tribunales federales", "zh": "联邦法院", "ja": "連邦裁判所"},
    "other": {"ko": "기타 기관", "en": "Other agencies", "es": "Otras agencias", "zh": "其他机构", "ja": "その他の機関"},
}
AGENCY_ORDER = list(AGENCY_LABEL)

# 주제. 기사 하나에 1~3개. 첫 화면 '주요 이슈' 보드가 이 단위로 묶습니다.
TOPIC_LABEL: dict[str, dict[str, str]] = {
    "h1b": {"ko": "H-1B·전문직", "en": "H-1B & specialty workers", "es": "H-1B y profesionales", "zh": "H-1B 专业人士", "ja": "H-1B・専門職"},
    "students": {"ko": "유학생·OPT", "en": "Students & OPT", "es": "Estudiantes y OPT", "zh": "留学生与 OPT", "ja": "留学生・OPT"},
    "employment": {"ko": "취업이민·노동허가", "en": "Employment immigration & EAD", "es": "Inmigración laboral y EAD", "zh": "职业移民与工卡", "ja": "就労移民・就労許可"},
    "eb5": {"ko": "투자이민 EB-5", "en": "EB-5 investors", "es": "Inversionistas EB-5", "zh": "EB-5 投资移民", "ja": "EB-5 投資移民"},
    "family": {"ko": "가족이민·영주권", "en": "Family & green cards", "es": "Familia y green card", "zh": "亲属移民与绿卡", "ja": "家族移民・グリーンカード"},
    "citizenship": {"ko": "시민권·귀화", "en": "Citizenship & naturalization", "es": "Ciudadanía y naturalización", "zh": "公民与入籍", "ja": "市民権・帰化"},
    "humanitarian": {"ko": "난민·망명·TPS", "en": "Refugees, asylum & TPS", "es": "Refugio, asilo y TPS", "zh": "难民·庇护·TPS", "ja": "難民・亡命・TPS"},
    "travel": {"ko": "입국·비자발급", "en": "Entry & visa issuance", "es": "Ingreso y emisión de visas", "zh": "入境与签证签发", "ja": "入国・ビザ発給"},
    "visa_bulletin": {"ko": "비자 문호", "en": "Visa Bulletin", "es": "Boletín de Visas", "zh": "签证公告", "ja": "ビザ・ブリテン"},
    "fees": {"ko": "수수료", "en": "Fees", "es": "Tarifas", "zh": "费用", "ja": "手数料"},
    "enforcement": {"ko": "단속·추방·사기", "en": "Enforcement & fraud", "es": "Control y fraude", "zh": "执法·遣返·欺诈", "ja": "取締り・送還・不正"},
    "other": {"ko": "기타", "en": "Other", "es": "Otros", "zh": "其他", "ja": "その他"},
}
TOPIC_ORDER = list(TOPIC_LABEL)


def agency(key: str, lang: str) -> str:
    row = AGENCY_LABEL.get(key or "other", AGENCY_LABEL["other"])
    return row.get(lang) or row["en"]


def topic(key: str, lang: str) -> str:
    row = TOPIC_LABEL.get(key or "other", TOPIC_LABEL["other"])
    return row.get(lang) or row["en"]


def cat(key: str, lang: str) -> str:
    row = CATEGORY_LABEL.get(key or "notice", CATEGORY_LABEL["notice"])
    return row.get(lang) or row["en"]


SOURCE_LABEL: dict[str, dict[str, str]] = {
    "uscis_news": {"ko": "USCIS", "en": "USCIS", "es": "USCIS", "zh": "USCIS", "ja": "USCIS"},
    "dos_visa_news": {"ko": "국무부", "en": "State Dept.", "es": "Dpto. de Estado", "zh": "国务院", "ja": "国務省"},
    "visa_bulletin": {"ko": "비자 문호", "en": "Visa Bulletin", "es": "Boletín de Visas", "zh": "签证公告", "ja": "ビザ・ブリテン"},
    "federal_register": {"ko": "연방관보", "en": "Federal Register", "es": "Registro Federal", "zh": "联邦公报", "ja": "連邦官報"},
    "presidential": {"ko": "대통령령", "en": "White House", "es": "Casa Blanca", "zh": "白宫", "ja": "大統領令"},
    "fr_public_inspection": {"ko": "연방관보 공개열람", "en": "Federal Register (Public Inspection)", "es": "Registro Federal (Inspección Pública)", "zh": "联邦公报（公开预览）", "ja": "連邦官報（事前公開）"},
    "uscis_policy_manual": {"ko": "USCIS 정책매뉴얼", "en": "USCIS Policy Manual", "es": "Manual de Políticas de USCIS", "zh": "USCIS 政策手册", "ja": "USCIS ポリシーマニュアル"},
    "uscis_vb_chart": {"ko": "비자블러틴", "en": "Visa Bulletin", "es": "Boletín de Visas", "zh": "签证公告", "ja": "ビザ・ブリテン"},
    "state_press": {"ko": "국무부", "en": "State Dept.", "es": "Dpto. de Estado", "zh": "国务院", "ja": "国務省"},
    "dhs_news": {"ko": "국토안보부", "en": "DHS", "es": "DHS", "zh": "国土安全部", "ja": "国土安全保障省"},
}


def t(key: str, lang: str) -> str:
    row = T.get(key, {})
    return row.get(lang) or row.get("en") or key


def src(key: str, lang: str) -> str:
    row = SOURCE_LABEL.get(key, {})
    return row.get(lang) or row.get("en") or key
