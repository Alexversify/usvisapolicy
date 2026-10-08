"""docs/ 정적 사이트 생성. GitHub Pages(또는 Cloudflare Pages)가 이 폴더를 그대로 게시합니다.

docs/index.html               브라우저 언어로 /ko/ /en/ ... 이동
docs/<lang>/index.html        최신 업데이트 목록 (필터, 검색)
docs/<lang>/news/<id>.html    기사
docs/<lang>/rss.xml           언어별 RSS
docs/assets/site.css|site.js  공통 스타일, 필터, 피드백 위젯
docs/sitemap.xml robots.txt CNAME 404.html
"""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import shutil
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xesc

import yaml

from src import assets, store
from src.i18n import CATEGORY_ORDER, HTML_LANG, LANG_LABEL, SOURCE_LABEL, cat, src, t

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
e = html.escape
# 자산이 바뀌면 주소가 바뀌어 브라우저 캐시가 갱신됩니다.
VER = hashlib.sha1((assets.CSS + assets.JS).encode()).hexdigest()[:8]


def site_cfg() -> dict[str, Any]:
    p = ROOT / "config" / "site.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


# ---------------------------------------------------------------- 조각


def head(sc: dict[str, Any], lang: str, title: str, desc: str, path: str, langs: list[str], depth: int, alt_paths: dict[str, str] | None = None) -> str:
    site = sc.get("site", {})
    base = f"https://{site.get('domain')}" if site.get("domain") else ""
    up = "../" * depth
    alts = ""
    if base and alt_paths:
        alts = "".join(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{base}/{p}">' for l, p in alt_paths.items())
        alts += f'<link rel="alternate" hreflang="x-default" href="{base}/{alt_paths.get("en", next(iter(alt_paths.values())))}">'
    canon = f'<link rel="canonical" href="{base}/{path}">' if base else ""
    an = sc.get("analytics") or {}
    ga = an.get("ga4_id") or ""
    ga_tag = (
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={e(ga)}"></script>'
        f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{e(ga)}');</script>"
        if ga else ""
    )
    verify = f'<meta name="google-site-verification" content="{e(an["search_console"])}">' if an.get("search_console") else ""
    ads = sc.get("adsense") or {}
    ad_tag = (
        f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={e(ads["client_id"])}" crossorigin="anonymous"></script>'
        if ads.get("client_id") else ""
    )
    font = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">' if lang == "ko" else ""
    rss = f'<link rel="alternate" type="application/rss+xml" href="{up}{lang}/rss.xml">'
    return f"""<!doctype html>
<html lang="{HTML_LANG[lang]}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website">
{canon}{alts}{rss}{verify}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect x='2' y='3' width='20' height='18' rx='3' fill='%2313233a'/%3E%3Cpath d='M6 8h12M6 12h8M6 16h10' stroke='white' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E">
{font}<link rel="stylesheet" href="{up}assets/site.css?v={VER}">
{ga_tag}{ad_tag}
</head>"""


def body_open(sc: dict[str, Any], lang: str, article_id: str = "") -> str:
    fb = sc.get("feedbal") or {}
    site = sc.get("site") or {}
    attrs = {
        "data-fb-endpoint": fb.get("endpoint") or "",
        "data-fb-site": fb.get("site_key") or "",
        "data-fb-mail": site.get("contact_email") or "",
        "data-fb-ok": t("fb_ok", lang),
        "data-fb-fail": t("fb_fail", lang),
        "data-article": article_id,
    }
    return "<body " + " ".join(f'{k}="{e(v)}"' for k, v in attrs.items()) + ">"


def topbar(sc: dict[str, Any], lang: str, langs: list[str], up: str, lang_paths: dict[str, str]) -> str:
    title = (sc.get("site") or {}).get("title", "US Visa Policy")
    links = "".join(
        f'<a href="{up}{lang_paths[l]}" data-lang="{l}" hreflang="{HTML_LANG[l]}" aria-current="{str(l == lang).lower()}">{e(LANG_LABEL[l])}</a>'
        for l in langs if l in lang_paths
    )
    return f"""<header class="top"><div class="wrap">
<a class="brand" href="{up}{lang}/">{assets.LOGO}<span>{e(title)}</span></a>
<nav class="langs" aria-label="Language">{links}</nav>
</div></header>"""


def feedback(sc: dict[str, Any], lang: str) -> str:
    fb = sc.get("feedbal") or {}
    if fb.get("widget_script"):
        return f'<script src="{e(fb["widget_script"])}" data-site="{e(fb.get("site_key", ""))}" data-lang="{lang}" defer></script>'
    opts = "".join(f'<option value="{k}">{e(t("fb_t_" + k, lang))}</option>' for k in ("translation", "content", "feature", "other"))
    return f"""<button id="fb-btn" type="button">{e(t('feedback', lang))}</button>
<dialog id="fb-dlg"><form method="dialog">
<h3>{e(t('fb_title', lang))}</h3>
<label>{e(t('fb_type', lang))}<select name="type">{opts}</select></label>
<label>{e(t('fb_msg', lang))}<textarea name="message" required maxlength="4000"></textarea></label>
<label>{e(t('fb_email', lang))}<input type="email" name="email" autocomplete="email"></label>
<div id="fb-msg" role="status"></div>
<div class="acts"><button type="button" data-close>{e(t('fb_cancel', lang))}</button><button type="submit">{e(t('fb_send', lang))}</button></div>
</form></dialog>"""


def footer(sc: dict[str, Any], lang: str, up: str, updated: str) -> str:
    site = sc.get("site") or {}
    mail = site.get("contact_email")
    contact = f' · <a href="mailto:{e(mail)}">{e(mail)}</a>' if mail else ""
    return f"""<footer><div class="wrap">
<p>{e(t('disclaimer', lang))}</p>
<p>{e(t('operated_by', lang))}: {e(site.get('operator', ''))}{contact}</p>
<p>{e(t('updated', lang))}: {e(updated)} · <a href="{up}{lang}/rss.xml">RSS</a></p>
</div></footer>
{feedback(sc, lang)}
<script src="{up}assets/site.js?v={VER}" defer></script>
</body></html>"""


def fmt_date(d: str | None, lang: str) -> str:
    if not d:
        return ""
    try:
        x = dt.date.fromisoformat(d[:10])
    except ValueError:
        return d
    if lang in ("ko",):
        return f"{x.year}. {x.month}. {x.day}."
    if lang in ("zh", "ja"):
        return f"{x.year}年{x.month}月{x.day}日"
    if lang == "es":
        return x.strftime("%d/%m/%Y")
    return x.strftime("%b %-d, %Y")


# ---------------------------------------------------------------- 페이지


def page_list(sc: dict[str, Any], lang: str, langs: list[str], arts: list[dict[str, Any]], sources_used: list[str], updated: str) -> str:
    title = (sc.get("site") or {}).get("title", "US Visa Policy")
    lang_paths = {l: f"{l}/" for l in langs}
    out = [head(sc, lang, f"{title} · {t('latest', lang)}", t("tagline", lang), f"{lang}/", langs, 1, lang_paths), body_open(sc, lang)]
    out.append(topbar(sc, lang, langs, "../", lang_paths))
    out.append(f'<main class="wrap"><section class="hero"><h1>{e(t("tagline", lang))}</h1><p>{e(t("updated", lang))}: {e(updated)}</p></section>')
    counts = {c: sum(1 for a in arts if (a.get("category") or "notice") == c) for c in CATEGORY_ORDER}
    tabs = [f'<button class="tab" data-filter-cat="all" aria-pressed="true">{e(t("all", lang))} <span>{len(arts)}</span></button>']
    tabs += [f'<button class="tab" data-filter-cat="{c}" aria-pressed="false">{e(cat(c, lang))} <span>{counts[c]}</span></button>'
             for c in CATEGORY_ORDER if counts[c]]
    opts = f'<option value="all">{e(t("all_sources", lang))}</option>' + "".join(
        f'<option value="{s}">{e(src(s, lang))}</option>' for s in sources_used)
    out.append(
        f'<div class="bar"><nav class="tabs" aria-label="{e(t("category", lang))}">{"".join(tabs)}</nav>'
        f'<div class="row"><select class="srcsel" data-filter-src aria-label="source">{opts}</select>'
        f'<button class="chip hot" data-filter-hot aria-pressed="false">{e(t("only_important", lang))}</button>'
        f'<input class="search" type="search" placeholder="{e(t("search", lang))}" aria-label="{e(t("search", lang))}"></div></div>')
    if not arts:
        out.append(f'<p class="empty">{e(t("empty", lang))}</p>')
    else:
        out.append('<ol class="list">')
        for a in arts:
            L = a["langs"][lang]
            c = a.get("category") or "notice"
            q = " ".join([L["title"], L["summary"], " ".join(a.get("tags", [])), a.get("original_title", ""), src(a["source"], lang), cat(c, lang)]).lower()
            hot = '<span class="badge hot">' + e(t("imp_high", lang)) + "</span>" if a.get("importance") == "high" else ""
            tags = "".join(f'<span class="tag">#{e(x)}</span>' for x in a.get("tags", [])[:4])
            eff = f'<div class="eff">{e(t("effective", lang))}: {e(fmt_date(a.get("effective_date"), lang))}</div>' if a.get("effective_date") else ""
            out.append(
                f'<li class="card" data-cat="{e(c)}" data-src="{e(a["source"])}" data-imp="{e(a.get("importance", ""))}" data-q="{e(q)}">'
                f'<time datetime="{e(a.get("published") or "")}">{e(fmt_date(a.get("published"), lang))}</time>'
                f'<div><div class="meta"><span class="badge cat-{e(c)}">{e(cat(c, lang))}</span><span class="badge">{e(src(a["source"], lang))}</span>{hot}{tags}</div>'
                f'<h2><a href="news/{a["id"]}.html">{e(L["title"])}</a></h2><p>{e(L["summary"])}</p>{eff}</div></li>'
            )
        out.append("</ol>")
        out.append(f'<p class="empty" id="no-match" hidden>{e(t("no_match", lang))}</p>')
    out.append("</main>")
    out.append(footer(sc, lang, "../", updated))
    return "\n".join(out)


def page_article(sc: dict[str, Any], lang: str, langs: list[str], a: dict[str, Any], updated: str) -> str:
    L = a["langs"][lang]
    title = (sc.get("site") or {}).get("title", "US Visa Policy")
    avail = [l for l in langs if l in a["langs"]]
    lang_paths = {l: f"{l}/news/{a['id']}.html" for l in avail}
    out = [head(sc, lang, f"{L['title']} · {title}", L["summary"], lang_paths[lang], langs, 2, lang_paths), body_open(sc, lang, a["id"])]
    out.append(topbar(sc, lang, avail, "../../", lang_paths))
    hot = '<span class="badge hot">' + e(t("imp_high", lang)) + "</span>" if a.get("importance") == "high" else ""
    tags = "".join(f'<span class="tag">#{e(x)}</span>' for x in a.get("tags", []))
    facts = [f'<span>{e(t("published", lang))} <b>{e(fmt_date(a.get("published"), lang))}</b></span>']
    if a.get("effective_date"):
        facts.append(f'<span>{e(t("effective", lang))} <b>{e(fmt_date(a["effective_date"], lang))}</b></span>')
    points = "".join(f"<li>{e(p)}</li>" for p in L.get("points", []))
    who = f'<h2>{e(t("who", lang))}</h2><p>{e(L["who"])}</p>' if L.get("who") else ""
    action = f'<h2>{e(t("action", lang))}</h2><div class="callout">{e(L["action"])}</div>' if L.get("action") else ""
    site = sc.get("site") or {}
    consult = (sc.get("cta") or {}).get("consult_url") or (f"mailto:{site['contact_email']}?subject=" + html.escape(f"[usvisapolicy] {a['original_title'][:80]}") if site.get("contact_email") else "")
    cta = f'<a class="cta" href="{e(consult)}">{e(t("consult", lang))}</a>' if consult else ""
    ads = sc.get("adsense") or {}
    ad = ""
    if ads.get("client_id") and (ads.get("slots") or {}).get("article_bottom"):
        ad = (f'<ins class="adsbygoogle" style="display:block;margin-top:20px" data-ad-client="{e(ads["client_id"])}" data-ad-slot="{e(ads["slots"]["article_bottom"])}" '
              'data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({});</script>')
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "NewsArticle", "headline": L["title"][:110],
        "datePublished": a.get("published"), "dateModified": a.get("added", "")[:10] or a.get("published"),
        "inLanguage": HTML_LANG[lang], "isBasedOn": a["url"],
        "publisher": {"@type": "Organization", "name": site.get("operator", "")},
    }, ensure_ascii=False).replace("</", "<\\/")
    out.append(f"""<main class="wrap">
<a class="backlink" href="../">← {e(t('back', lang))}</a>
<article class="doc">
<div class="meta"><span class="badge cat-{e(a.get('category') or 'notice')}">{e(cat(a.get('category') or 'notice', lang))}</span><span class="badge">{e(src(a['source'], lang))}</span>{hot}{tags}</div>
<h1>{e(L['title'])}</h1>
<div class="facts">{''.join(facts)}</div>
<p class="lede">{e(L['summary'])}</p>
<h2>{e(t('key_points', lang))}</h2><ul>{points}</ul>
{who}{action}
<div class="src">{e(t('original_title', lang))}: {e(a['original_title'])}<br>
<a class="btn" href="{e(a['url'])}" rel="noopener" target="_blank">{e(t('original', lang))} ↗</a>
<a class="arch" href="https://web.archive.org/web/{e(a['url'])}" rel="noopener" target="_blank">{e(t('archived', lang))}</a>
<p class="note">{e(t('ai_note', lang))}</p></div>
{cta}{ad}
</article>
<script type="application/ld+json">{ld}</script>
</main>""")
    out.append(footer(sc, lang, "../../", updated))
    return "\n".join(out)


def page_root(sc: dict[str, Any], langs: list[str], prefix: str = "") -> str:
    links = "".join(f'<li><a href="{prefix}{l}/" hreflang="{HTML_LANG[l]}">{e(LANG_LABEL[l])}</a></li>' for l in langs)
    site = sc.get("site") or {}
    base = f"https://{site['domain']}" if site.get("domain") else ""
    alts = "".join(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{base}/{l}/">' for l in langs) if base else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(site.get('title', 'US Visa Policy'))}</title>
<meta name="description" content="{e(t('tagline', 'en'))}">{alts}
<link rel="stylesheet" href="{prefix}assets/site.css?v={VER}">
<script>(function(){{var L={json.dumps(langs)},c=null;
try{{c=localStorage.getItem('uvp-lang')}}catch(e){{}}
if(!c||L.indexOf(c)<0){{var n=(navigator.languages||[navigator.language||'en']);for(var i=0;i<n.length;i++){{var k=String(n[i]).slice(0,2).toLowerCase();if(L.indexOf(k)>=0){{c=k;break}}}}}}
location.replace('{prefix}'+(c&&L.indexOf(c)>=0?c:(L.indexOf('en')>=0?'en':L[0]))+'/');}})();</script>
</head><body><main class="wrap"><section class="hero"><h1>{e(site.get('title', 'US Visa Policy'))}</h1><p>{e(t('tagline', 'en'))}</p></section>
<ul>{links}</ul></main></body></html>"""


def rss(sc: dict[str, Any], lang: str, arts: list[dict[str, Any]]) -> str:
    site = sc.get("site") or {}
    base = f"https://{site.get('domain', '')}"
    items = []
    for a in arts[:40]:
        L = a["langs"][lang]
        try:
            pub = dt.datetime.fromisoformat(a["published"][:10]).strftime("%a, %d %b %Y 00:00:00 +0000")
        except (ValueError, TypeError, KeyError):
            pub = ""
        items.append(
            f"<item><title>{xesc(L['title'])}</title><link>{base}/{lang}/news/{a['id']}.html</link>"
            f"<guid isPermaLink=\"false\">{a['id']}-{lang}</guid><pubDate>{pub}</pubDate>"
            f"<category>{xesc(src(a['source'], lang))}</category><description>{xesc(L['summary'])}</description></item>"
        )
    return (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
            f"<title>{xesc(site.get('title', 'US Visa Policy'))} ({LANG_LABEL[lang]})</title><link>{base}/{lang}/</link>"
            f"<description>{xesc(t('tagline', lang))}</description><language>{HTML_LANG[lang]}</language>"
            + "".join(items) + "</channel></rss>")


def sitemap(sc: dict[str, Any], langs: list[str], arts: list[dict[str, Any]]) -> str:
    base = f"https://{(sc.get('site') or {}).get('domain', '')}"
    rows = []

    def entry(paths: dict[str, str], lastmod: str | None) -> None:
        for p in paths.values():
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{HTML_LANG[l]}" href="{base}/{q}"/>' for l, q in paths.items())
            lm = f"<lastmod>{lastmod[:10]}</lastmod>" if lastmod else ""
            rows.append(f"<url><loc>{base}/{p}</loc>{lm}{alts}</url>")

    entry({l: f"{l}/" for l in langs}, dt.date.today().isoformat())
    for a in arts:
        entry({l: f"{l}/news/{a['id']}.html" for l in langs if l in a["langs"]}, a.get("published"))
    return ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">' + "".join(rows) + "</urlset>")


# ---------------------------------------------------------------- 실행


def kst(stamp: str) -> str:
    """'2026-10-03T01:23Z' 같은 UTC 표기를 KST 문자열로. 못 읽으면 그대로."""
    try:
        t = dt.datetime.strptime(stamp, "%Y-%m-%dT%H:%MZ").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return stamp
    return t.astimezone(dt.timezone(dt.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M KST")


def render_all(cfg: dict[str, Any]) -> str:
    sc = site_cfg()
    langs = cfg["languages"]
    index = store.load_index()
    arts = []
    for row in index:
        a = store.load_article(row["id"])
        if not a or not a.get("langs"):
            continue
        # 한 번 올린 기사는 언어가 하나 빠져도 내리지 않습니다. 빠진 언어는 영어(없으면 있는 언어)로 채웁니다.
        fallback = a["langs"].get("en") or next(iter(a["langs"].values()))
        a["langs"] = {l: a["langs"].get(l) or fallback for l in langs}
        arts.append(a)
    arts.sort(key=lambda a: (a.get("published") or "", a.get("added") or ""), reverse=True)
    order = list(SOURCE_LABEL)
    sources_used = sorted({a["source"] for a in arts}, key=lambda s: order.index(s) if s in order else 99)
    if not sources_used:
        sources_used = [k for k, v in cfg["sources"].items() if v.get("enabled", True)]
    # 렌더 시각이 아니라 마지막 수집 시각을 씁니다. --render-only 로 다시 만들어도 바뀌지 않고,
    # 기사 페이지는 기사 자신의 추가 시각을 써서 새 기사가 없을 때 수백 개 파일이 매번 바뀌지 않습니다.
    checked = store.load_status().get("checked") or max((a.get("added") or "" for a in arts), default="")
    now = kst(checked)

    # 기사 파일은 매번 새로 씁니다. 지워진 기사가 남지 않도록 언어 폴더를 비웁니다.
    for l in langs:
        shutil.rmtree(DOCS / l, ignore_errors=True)
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    (DOCS / "assets" / "site.css").write_text(assets.CSS.strip() + "\n", encoding="utf-8")
    (DOCS / "assets" / "site.js").write_text(assets.JS.strip() + "\n", encoding="utf-8")

    for l in langs:
        (DOCS / l / "news").mkdir(parents=True, exist_ok=True)
        (DOCS / l / "index.html").write_text(page_list(sc, l, langs, arts, sources_used, now), encoding="utf-8")
        (DOCS / l / "rss.xml").write_text(rss(sc, l, arts), encoding="utf-8")
        for a in arts:
            (DOCS / l / "news" / f"{a['id']}.html").write_text(page_article(sc, l, langs, a, kst(a.get("added") or checked)), encoding="utf-8")

    (DOCS / "index.html").write_text(page_root(sc, langs), encoding="utf-8")
    (DOCS / "404.html").write_text(page_root(sc, langs, "/"), encoding="utf-8")
    domain = (sc.get("site") or {}).get("domain")
    if domain:
        (DOCS / "CNAME").write_text(domain + "\n", encoding="utf-8")
        (DOCS / "sitemap.xml").write_text(sitemap(sc, langs, arts), encoding="utf-8")
        (DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: https://{domain}/sitemap.xml\n", encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    return f"docs/ 생성 완료: 기사 {len(arts)}건 x {len(langs)}개 언어"
