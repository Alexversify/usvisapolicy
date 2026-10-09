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
    "no_match": {"ko": "조건에 맞는 업데이트가 없습니다.", "en": "No updates match your filters.", "es": "Ninguna novedad coincide con los filtros.", "zh": "没有符合条件的更新。", "ja": "条件に合う更新はありません。"},
    "ai_note": {
        "ko": "이 글은 공식 발표를 AI가 요약·번역한 것입니다. 법적 효력은 영문 원문에만 있습니다.",
        "en": "This summary was produced with AI from the official announcement. Only the official source is authoritative.",
        "es": "Este resumen fue elaborado con IA a partir del anuncio oficial. Solo la fuente oficial tiene validez.",
        "zh": "本文由 AI 根据官方公告摘要翻译，仅英文官方原文具有法律效力。",
        "ja": "本記事は公式発表をAIで要約・翻訳したものです。法的効力は英語の公式原文のみにあります。",
    },
    "disclaimer": {
        "ko": "본 사이트의 내용은 일반 정보 제공 목적이며 법률 자문이 아닙니다. 구체적인 사안은 변호사와 상담하십시오.",
        "en": "Content on this site is general information, not legal advice. Consult an attorney about your specific case.",
        "es": "El contenido de este sitio es información general y no constituye asesoría legal. Consulte a un abogado sobre su caso.",
        "zh": "本网站内容仅供一般参考，不构成法律意见。具体情况请咨询律师。",
        "ja": "本サイトの内容は一般的な情報提供であり、法的助言ではありません。個別の案件は弁護士にご相談ください。",
    },
    "consult": {"ko": "이 변경이 내 케이스에 미치는 영향 상담하기", "en": "Ask how this affects your case", "es": "Consulte cómo afecta a su caso", "zh": "咨询此变化对您案件的影响", "ja": "ご自身のケースへの影響を相談する"},
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
    "visa_bulletin": {"ko": "비자블러틴", "en": "Visa Bulletin", "es": "Boletín de Visas", "zh": "签证公告", "ja": "ビザ・ブリテン"},
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
    "visa_bulletin": {"ko": "비자블러틴", "en": "Visa Bulletin", "es": "Boletín de Visas", "zh": "签证公告", "ja": "ビザ・ブリテン"},
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
