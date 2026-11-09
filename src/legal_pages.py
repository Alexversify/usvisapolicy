"""사이트 소개(about)와 개인정보처리방침(privacy) 페이지 문구. 5개 언어.

애드센스 심사와 이용자 안내용입니다. 운영자 이름은 넣지 않습니다.
본문은 (제목, [문단 또는 ("ul", [항목...])]) 형태의 절 목록입니다. {mail} 은 문의 메일로 바뀝니다.
"""
from __future__ import annotations

import html
from typing import Any

EFFECTIVE = "2026-11-09"

LABEL = {
    "about": {"ko": "사이트 소개", "en": "About", "es": "Acerca de", "zh": "关于本站", "ja": "このサイトについて"},
    "privacy": {"ko": "개인정보처리방침", "en": "Privacy Policy", "es": "Política de privacidad", "zh": "隐私政策", "ja": "プライバシーポリシー"},
    "effective": {"ko": "시행일", "en": "Effective date", "es": "Fecha de entrada en vigor", "zh": "生效日期", "ja": "施行日"},
}

ABOUT_DESC = {
    "ko": "US Visa Policy는 미국 정부의 비자·이민 공식 발표를 모아 5개 언어로 정리하는 독립 정보 사이트입니다.",
    "en": "US Visa Policy is an independent site that collects official U.S. visa and immigration announcements and presents them in five languages.",
    "es": "US Visa Policy es un sitio independiente que reúne los anuncios oficiales de visas e inmigración de EE. UU. y los presenta en cinco idiomas.",
    "zh": "US Visa Policy 是一个独立信息网站，汇集美国政府发布的签证与移民官方公告，并以五种语言整理呈现。",
    "ja": "US Visa Policy は、米国政府が発表するビザ・移民の公式情報を集め、5言語で整理して届ける独立した情報サイトです。",
}

ABOUT = {
    "ko": [
        ("무엇을 하는 사이트인가요", [
            "US Visa Policy는 미국 이민국(USCIS), 국무부, 국토안보부, 노동부, 법무부 등 미국 정부 기관이 공개한 비자·이민 관련 발표를 모아 한국어, 영어, 스페인어, 중국어, 일본어로 정리해 제공합니다.",
            "각 글에는 핵심 요약, 원문 전체, 번역 전문, 그리고 정부 원문 링크가 함께 실립니다. 매월 발표되는 비자 문호(Visa Bulletin)는 별도 페이지에서 표로 비교해 볼 수 있습니다.",
        ]),
        ("업데이트 방식", [
            "공식 발표 페이지와 보도자료를 하루 여러 차례 확인해 새 소식을 반영합니다. 원문이 수정되면 내용을 다시 확인합니다.",
        ]),
        ("유의 사항", [("ul", [
            "이 사이트는 민간이 운영하는 정보 사이트이며, 미국 정부나 각국 정부가 운영하거나 보증하는 사이트가 아닙니다.",
            "번역과 요약에는 오류나 누락이 있을 수 있습니다. 중요한 결정 전에는 반드시 각 글의 정부 원문을 확인하세요.",
            "이 사이트의 내용은 일반 정보 제공 목적이며 법률 자문이 아닙니다. 개별 사안은 자격을 갖춘 전문가와 상담하세요.",
        ])]),
        ("문의", ["오역 제보, 건의, 기타 문의는 {mail} 로 보내 주세요. 화면 오른쪽 아래 피드백 버튼도 이용할 수 있습니다."]),
    ],
    "en": [
        ("What this site does", [
            "US Visa Policy collects visa and immigration announcements published by U.S. government agencies, including USCIS, the Department of State, DHS, the Department of Labor and the Department of Justice, and presents them in Korean, English, Spanish, Chinese and Japanese.",
            "Each post includes a short summary, the full original text, a full translation and a link to the government source. The monthly Visa Bulletin has its own page with comparison tables.",
        ]),
        ("How updates work", ["Official announcement pages and press releases are checked several times a day. When a source is revised, the post is reviewed again."]),
        ("Please note", [("ul", [
            "This is a privately operated information site. It is not operated or endorsed by the U.S. government or any other government.",
            "Translations and summaries may contain errors or omissions. Always check the government source linked in each post before making important decisions.",
            "Content is for general information only and is not legal advice. Consult a qualified professional about your own situation.",
        ])]),
        ("Contact", ["Send translation corrections, suggestions and other questions to {mail}. You can also use the feedback button at the bottom right of the page."]),
    ],
    "es": [
        ("Qué hace este sitio", [
            "US Visa Policy reúne los anuncios sobre visas e inmigración publicados por agencias del gobierno de EE. UU., como USCIS, el Departamento de Estado, DHS, el Departamento de Trabajo y el Departamento de Justicia, y los presenta en coreano, inglés, español, chino y japonés.",
            "Cada publicación incluye un resumen, el texto original completo, una traducción completa y el enlace a la fuente oficial. El Boletín de Visas mensual tiene su propia página con tablas comparativas.",
        ]),
        ("Cómo se actualiza", ["Las páginas oficiales y los comunicados de prensa se revisan varias veces al día. Cuando una fuente se modifica, la publicación se vuelve a revisar."]),
        ("Aviso", [("ul", [
            "Este es un sitio informativo privado. No está operado ni respaldado por el gobierno de EE. UU. ni por ningún otro gobierno.",
            "Las traducciones y los resúmenes pueden contener errores u omisiones. Consulte siempre la fuente oficial enlazada en cada publicación antes de tomar decisiones importantes.",
            "El contenido es solo informativo y no constituye asesoría legal. Consulte a un profesional calificado sobre su caso.",
        ])]),
        ("Contacto", ["Envíe correcciones, sugerencias y otras consultas a {mail}. También puede usar el botón de comentarios en la esquina inferior derecha."]),
    ],
    "zh": [
        ("本站简介", [
            "US Visa Policy 汇集美国移民局（USCIS）、国务院、国土安全部、劳工部、司法部等美国政府机构发布的签证与移民公告，并以韩语、英语、西班牙语、中文和日语整理呈现。",
            "每篇文章包含摘要、完整原文、完整译文以及政府原文链接。每月发布的签证公告（Visa Bulletin）另设页面，以表格对比查看。",
        ]),
        ("更新方式", ["本站每天多次查看官方公告页面和新闻稿。原文修订时会重新核对内容。"]),
        ("注意事项", [("ul", [
            "本站为民间运营的信息网站，并非由美国政府或任何国家政府运营或认可。",
            "译文和摘要可能存在错误或遗漏。作出重要决定前，请务必查看各文章所附的政府原文。",
            "本站内容仅供一般参考，不构成法律意见。个人情况请咨询具备资格的专业人士。",
        ])]),
        ("联系方式", ["翻译纠错、建议及其他问题请发送至 {mail}。也可以使用页面右下角的反馈按钮。"]),
    ],
    "ja": [
        ("このサイトについて", [
            "US Visa Policy は、米国移民局（USCIS）、国務省、国土安全保障省、労働省、司法省など米国政府機関が公表したビザ・移民関連の発表を集め、韓国語、英語、スペイン語、中国語、日本語で整理して提供しています。",
            "各記事には要約、原文全文、翻訳全文、政府の原文リンクを掲載しています。毎月発表されるビザ・ブレティン（Visa Bulletin）は専用ページで表にして比較できます。",
        ]),
        ("更新について", ["公式の発表ページとプレスリリースを1日に複数回確認し、新しい情報を反映します。原文が修正された場合は内容を再確認します。"]),
        ("ご注意", [("ul", [
            "本サイトは民間が運営する情報サイトであり、米国政府その他の政府が運営または保証するものではありません。",
            "翻訳や要約には誤りや漏れが含まれる場合があります。重要な判断の前には必ず各記事の政府原文をご確認ください。",
            "掲載内容は一般的な情報提供を目的とするもので、法的助言ではありません。個別の事案は資格のある専門家にご相談ください。",
        ])]),
        ("お問い合わせ", ["誤訳のご指摘、ご意見、その他のお問い合わせは {mail} までお送りください。画面右下のフィードバックボタンもご利用いただけます。"]),
    ],
}

PRIVACY_DESC = {
    "ko": "US Visa Policy의 개인정보 수집·이용, 쿠키와 광고에 관한 안내입니다.",
    "en": "How US Visa Policy handles personal information, cookies and advertising.",
    "es": "Cómo US Visa Policy trata la información personal, las cookies y la publicidad.",
    "zh": "US Visa Policy 关于个人信息、Cookie 和广告的说明。",
    "ja": "US Visa Policy における個人情報、Cookie、広告の取り扱いについて。",
}

ADS = "https://policies.google.com/technologies/partner-sites"
ADSET = "https://adssettings.google.com"
AAI = "https://www.aboutads.info"

PRIVACY = {
    "ko": [
        ("1. 회원가입 없음", ["이 사이트는 회원가입이나 로그인 없이 이용할 수 있으며, 이름, 연락처 등 개인정보를 이용 조건으로 요구하지 않습니다."]),
        ("2. 이용자가 직접 보내는 정보", ["피드백 버튼이나 이메일로 문의하실 때 적어 주신 내용과 (선택 입력한) 이메일 주소는 답변과 사이트 개선 목적으로만 사용하며, 목적을 달성한 뒤 지체 없이 삭제합니다. 법령에 따른 경우를 제외하고 제3자에게 제공하지 않습니다."]),
        ("3. 브라우저 저장 정보", ["선택한 언어, 목록 표시 개수 같은 화면 설정은 이용자 브라우저의 로컬 저장소에만 보관되며 서버로 전송되지 않습니다. 브라우저 설정에서 언제든 지울 수 있습니다."]),
        ("4. 광고와 쿠키 (Google 애드센스)", [
            "이 사이트는 Google 애드센스를 통해 광고를 게재합니다. Google을 포함한 제3자 광고 사업자는 쿠키를 사용해 이용자가 이 사이트와 다른 사이트를 방문한 기록을 바탕으로 광고를 표시할 수 있습니다.",
            ("ul", [
                "Google의 광고 쿠키 사용으로 Google과 파트너는 이용자의 방문 기록에 기반한 광고를 제공할 수 있습니다.",
                f'맞춤 광고는 <a href="{ADSET}" rel="noopener">Google 광고 설정</a>에서 끌 수 있으며, <a href="{AAI}" rel="noopener">www.aboutads.info</a>에서 다른 제3자 사업자의 맞춤 광고 쿠키도 거부할 수 있습니다.',
                f'Google의 데이터 사용 방식은 <a href="{ADS}" rel="noopener">Google 파트너 사이트 정책</a>에서 확인할 수 있습니다.',
            ]),
        ]),
        ("5. 접속 기록", ["사이트를 호스팅하는 서비스(Cloudflare)는 보안과 안정적 운영을 위해 IP 주소, 브라우저 정보, 접속 시각 같은 기술 기록을 자동으로 처리할 수 있습니다. 이 사이트는 이 기록으로 개인을 식별하지 않습니다."]),
        ("6. 외부 링크", ["각 글의 원문 링크 등 외부 사이트는 해당 사이트의 개인정보 정책을 따릅니다."]),
        ("7. 문의와 변경", ["개인정보 관련 문의, 열람·삭제 요청은 {mail} 로 보내 주세요. 이 방침이 바뀌면 이 페이지에 게시하고 시행일을 갱신합니다."]),
    ],
    "en": [
        ("1. No account required", ["You can use this site without signing up or logging in. We do not require your name or contact details to use the site."]),
        ("2. Information you send us", ["If you contact us through the feedback button or by email, we use your message and any email address you choose to provide only to reply and to improve the site, and delete it once that purpose is met. We do not share it with third parties except where required by law."]),
        ("3. Settings stored in your browser", ["Display settings such as your language and the number of items per page are kept only in your browser's local storage and are not sent to our servers. You can clear them in your browser settings at any time."]),
        ("4. Advertising and cookies (Google AdSense)", [
            "This site shows ads through Google AdSense. Third-party vendors, including Google, use cookies to serve ads based on your prior visits to this site or other websites.",
            ("ul", [
                "Google's use of advertising cookies enables it and its partners to serve ads based on your visits to this site and/or other sites on the Internet.",
                f'You may opt out of personalized advertising in <a href="{ADSET}" rel="noopener">Google Ads Settings</a>, and opt out of other third-party vendors\' cookies at <a href="{AAI}" rel="noopener">www.aboutads.info</a>.',
                f'Learn how Google uses data in its <a href="{ADS}" rel="noopener">partner sites policy</a>.',
            ]),
        ]),
        ("5. Access logs", ["Our hosting provider (Cloudflare) may automatically process technical records such as IP address, browser information and access time for security and reliable operation. We do not use these records to identify individuals."]),
        ("6. External links", ["External sites, including the government sources linked in each post, are governed by their own privacy policies."]),
        ("7. Contact and changes", ["Send privacy questions and requests for access or deletion to {mail}. If this policy changes, we will post the update here and revise the effective date."]),
    ],
    "es": [
        ("1. Sin registro", ["Puede usar este sitio sin registrarse ni iniciar sesión. No pedimos su nombre ni sus datos de contacto para usarlo."]),
        ("2. Información que usted nos envía", ["Si nos escribe mediante el botón de comentarios o por correo, usamos su mensaje y el correo que decida darnos solo para responder y mejorar el sitio, y los eliminamos cuando se cumple ese fin. No los compartimos con terceros salvo obligación legal."]),
        ("3. Ajustes guardados en su navegador", ["Ajustes como el idioma y el número de elementos por página se guardan solo en el almacenamiento local de su navegador y no se envían a nuestros servidores. Puede borrarlos cuando quiera."]),
        ("4. Publicidad y cookies (Google AdSense)", [
            "Este sitio muestra anuncios mediante Google AdSense. Proveedores externos, incluido Google, usan cookies para mostrar anuncios según sus visitas anteriores a este u otros sitios web.",
            ("ul", [
                "El uso de cookies publicitarias permite a Google y a sus socios mostrar anuncios basados en sus visitas a este sitio y a otros sitios de Internet.",
                f'Puede desactivar la publicidad personalizada en la <a href="{ADSET}" rel="noopener">Configuración de anuncios de Google</a> y rechazar las cookies de otros proveedores en <a href="{AAI}" rel="noopener">www.aboutads.info</a>.',
                f'Consulte cómo usa Google los datos en su <a href="{ADS}" rel="noopener">política de sitios asociados</a>.',
            ]),
        ]),
        ("5. Registros de acceso", ["Nuestro proveedor de alojamiento (Cloudflare) puede procesar automáticamente registros técnicos como la dirección IP, el navegador y la hora de acceso por seguridad y estabilidad. No usamos estos registros para identificar a personas."]),
        ("6. Enlaces externos", ["Los sitios externos, incluidas las fuentes oficiales enlazadas, se rigen por sus propias políticas de privacidad."]),
        ("7. Contacto y cambios", ["Envíe consultas de privacidad y solicitudes de acceso o eliminación a {mail}. Si esta política cambia, publicaremos la actualización aquí y modificaremos la fecha de entrada en vigor."]),
    ],
    "zh": [
        ("1. 无需注册", ["本站无需注册或登录即可使用，不以提供姓名、联系方式等个人信息作为使用条件。"]),
        ("2. 您主动发送的信息", ["您通过反馈按钮或电子邮件联系我们时填写的内容及（自愿提供的）电子邮箱，仅用于回复和改进网站，目的达成后即予删除。除法律要求外，不向第三方提供。"]),
        ("3. 浏览器中保存的设置", ["您选择的语言、每页显示数量等界面设置仅保存在您浏览器的本地存储中，不会发送到服务器。您可随时在浏览器设置中清除。"]),
        ("4. 广告与 Cookie（Google AdSense）", [
            "本站通过 Google AdSense 展示广告。包括 Google 在内的第三方供应商会使用 Cookie，根据您以往访问本站或其他网站的记录投放广告。",
            ("ul", [
                "Google 使用广告 Cookie，使其及其合作伙伴能够根据您对本站和/或互联网上其他网站的访问情况投放广告。",
                f'您可以在 <a href="{ADSET}" rel="noopener">Google 广告设置</a>中关闭个性化广告，也可以在 <a href="{AAI}" rel="noopener">www.aboutads.info</a> 拒绝其他第三方供应商的 Cookie。',
                f'有关 Google 如何使用数据，请参阅 <a href="{ADS}" rel="noopener">Google 合作伙伴网站政策</a>。',
            ]),
        ]),
        ("5. 访问记录", ["本站的托管服务商（Cloudflare）可能为安全和稳定运行自动处理 IP 地址、浏览器信息、访问时间等技术记录。本站不会利用这些记录识别个人。"]),
        ("6. 外部链接", ["各文章所附原文链接等外部网站适用其各自的隐私政策。"]),
        ("7. 联系与变更", ["隐私相关问题及查阅、删除请求请发送至 {mail}。本政策如有变更，将在本页公布并更新生效日期。"]),
    ],
    "ja": [
        ("1. 会員登録は不要です", ["本サイトは会員登録やログインなしでご利用いただけます。氏名や連絡先などの個人情報を利用の条件として求めることはありません。"]),
        ("2. ご自身で送信される情報", ["フィードバックボタンまたはメールでお問い合わせいただいた内容と（任意で入力された）メールアドレスは、回答とサイト改善の目的にのみ使用し、目的達成後は速やかに削除します。法令に基づく場合を除き、第三者に提供しません。"]),
        ("3. ブラウザに保存される設定", ["選択した言語や一覧の表示件数などの画面設定は、お使いのブラウザのローカルストレージにのみ保存され、サーバーには送信されません。ブラウザの設定からいつでも削除できます。"]),
        ("4. 広告と Cookie（Google AdSense）", [
            "本サイトは Google AdSense を利用して広告を掲載しています。Google などの第三者配信事業者は Cookie を使用して、本サイトや他のサイトへの過去のアクセス情報に基づいて広告を配信します。",
            ("ul", [
                "Google が広告 Cookie を使用することにより、Google やそのパートナーは本サイトや他のサイトへのアクセス情報に基づいて広告を配信できます。",
                f'パーソナライズ広告は <a href="{ADSET}" rel="noopener">Google 広告設定</a>で無効にできます。また <a href="{AAI}" rel="noopener">www.aboutads.info</a> で他の第三者配信事業者の Cookie を無効にできます。',
                f'Google によるデータの使用については <a href="{ADS}" rel="noopener">Google パートナーサイトのポリシー</a>をご覧ください。',
            ]),
        ]),
        ("5. アクセス記録", ["本サイトのホスティング事業者（Cloudflare）は、セキュリティと安定運用のため、IP アドレス、ブラウザ情報、アクセス日時などの技術的記録を自動的に処理する場合があります。本サイトはこれらの記録で個人を特定しません。"]),
        ("6. 外部リンク", ["各記事の原文リンクなど外部サイトには、それぞれのプライバシーポリシーが適用されます。"]),
        ("7. お問い合わせと変更", ["個人情報に関するお問い合わせ、開示・削除のご依頼は {mail} までお送りください。本ポリシーを変更する場合は、このページに掲載し施行日を更新します。"]),
    ],
}


def _para(text: str, mail: str) -> str:
    # 문구 안의 <a> 링크는 이 파일에서 직접 쓴 것이므로 그대로 둡니다. 메일 주소만 이스케이프해 넣습니다.
    m = f'<a href="mailto:{html.escape(mail)}">{html.escape(mail)}</a>' if mail else ""
    return text.replace("{mail}", m)


def body(kind: str, lang: str, mail: str) -> str:
    secs = (ABOUT if kind == "about" else PRIVACY)[lang]
    out = ['<main class="wrap"><article class="doc">', f"<h1>{html.escape(LABEL[kind][lang])}</h1>"]
    if kind == "about":
        out.append(f"<p>{html.escape(ABOUT_DESC[lang])}</p>")
    else:
        out.append(f'<p class="meta">{html.escape(LABEL["effective"][lang])}: {EFFECTIVE}</p>')
    for h, parts in secs:
        out.append(f"<h2>{html.escape(h)}</h2>")
        for p in parts:
            if isinstance(p, tuple):
                out.append("<ul>" + "".join(f"<li>{_para(x, mail)}</li>" for x in p[1]) + "</ul>")
            else:
                out.append(f"<p>{_para(p, mail)}</p>")
    out.append("</article></main>")
    return "\n".join(out)


def desc(kind: str, lang: str) -> str:
    return (ABOUT_DESC if kind == "about" else PRIVACY_DESC)[lang]


def links(lang: str, up: str) -> str:
    return " · ".join(f'<a href="{up}{lang}/{k}.html">{html.escape(LABEL[k][lang])}</a>' for k in ("about", "privacy"))


def all_kinds() -> list[str]:
    return ["about", "privacy"]


__all__: list[Any] = ["body", "desc", "links", "all_kinds", "LABEL"]
