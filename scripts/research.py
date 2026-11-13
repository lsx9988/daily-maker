# -*- coding: utf-8 -*-
"""公开资料检索层。

只取公开来源的摘要/片段用于归纳，不整篇搬运正文；每个来源保留标题、链接与摘要。
全部源超时或失败时返回空 sources，由上层走模板/兜底降级，保证每天一定有产出。
仅用标准库 urllib。
"""
import gzip
import json
import re
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 daily-maker/1.0")

TIMEOUT = 10


def _get(url, timeout=TIMEOUT):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json,text/plain,*/*",
        "Accept-Encoding": "gzip",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return raw.decode("utf-8", "ignore")


def _get_json(url, timeout=TIMEOUT):
    txt = _get(url, timeout=timeout)
    if not txt.strip():
        return None
    return json.loads(txt)


def _clean(text, limit=300):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _wiki(query, lang):
    """Wikipedia 摘要。query 用英文标题命中更稳，中文站作补充。"""
    q = urllib.parse.quote(query.replace(" ", "_"))
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{q}"
    obj = _get_json(url)
    if not obj or obj.get("type") == "disambiguation" or not obj.get("extract"):
        return None
    page = (obj.get("content_urls") or {}).get("desktop", {}).get("page")
    return {
        "title": obj.get("title", query),
        "url": page or url,
        "snippet": _clean(obj.get("extract", "")),
        "source": f"Wikipedia({lang})",
    }


def _ddg(query):
    url = ("https://api.duckduckgo.com/?q=" + urllib.parse.quote(query) +
           "&format=json&no_html=1&skip_disambig=1")
    obj = _get_json(url)
    if not obj:
        return []
    out = []
    if obj.get("AbstractText"):
        out.append({
            "title": obj.get("Heading") or query,
            "url": obj.get("AbstractURL") or "",
            "snippet": _clean(obj["AbstractText"]),
            "source": "DuckDuckGo",
        })
    for rt in (obj.get("RelatedTopics") or [])[:3]:
        if isinstance(rt, dict) and rt.get("Text") and rt.get("FirstURL"):
            out.append({
                "title": _clean(rt["Text"], 80),
                "url": rt["FirstURL"],
                "snippet": _clean(rt["Text"]),
                "source": "DuckDuckGo",
            })
    return out


def _stackexchange(query, site="electronics"):
    url = ("https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance"
           "&pagesize=3&site=" + site + "&q=" + urllib.parse.quote(query))
    obj = _get_json(url)
    if not obj:
        return []
    out = []
    for item in (obj.get("items") or [])[:3]:
        out.append({
            "title": item.get("title", query),
            "url": item.get("link", ""),
            "snippet": _clean(item.get("excerpt", "")),
            "source": "StackExchange/" + site,
        })
    return out


def _github(query, limit=6):
    """GitHub 仓库搜索（开源项目推荐用）。无 token 也可调，限速较宽。"""
    if not query:
        return []
    q = urllib.parse.quote(query)
    url = (f"https://api.github.com/search/repositories?q={q}&sort=stars"
           f"&order=desc&per_page={limit}")
    obj = _get_json(url)
    if not obj:
        return []
    out = []
    for it in (obj.get("items") or [])[:limit]:
        lic = (it.get("license") or {}).get("spdx_id") or "未知"
        out.append({
            "title": it.get("full_name", query),
            "url": it.get("html_url", ""),
            "snippet": _clean(it.get("description") or "（该仓库未填写简介）", 200),
            "source": "GitHub",
            "license": lic,
            "stars": it.get("stargazers_count", 0),
            "lang": it.get("language") or "",
        })
    return out


def research(topic):
    """聚合多源摘要。返回 {"sources": [...], "errors": [...]}。"""
    sources, errors = [], []
    seen = set()

    def add(items):
        for it in items:
            if not it or not it.get("snippet"):
                continue
            key = it["url"] or it["title"]
            if key in seen:
                continue
            seen.add(key)
            sources.append(it)

    tool_type = topic.get("tool_type", "")

    # 开源推荐类：以 GitHub 仓库搜索为主，DuckDuckGo 补摘要
    if tool_type == "software-pick":
        try:
            add(_github(topic.get("query_en", topic.get("title", ""))))
        except Exception as e:  # noqa: BLE001
            errors.append(f"github: {type(e).__name__}")
        try:
            add(_ddg(topic.get("query_zh", topic.get("title", ""))))
        except Exception as e:  # noqa: BLE001
            errors.append(f"ddg:{type(e).__name__}")
        return {"sources": sources[:8], "errors": errors}

    queries = [("en", topic.get("query_en", "")), ("zh", topic.get("query_zh", ""))]
    for lang, q in queries:
        if not q:
            continue
        try:
            add([_wiki(q, lang)])
        except Exception as e:  # noqa: BLE001
            errors.append(f"wiki:{lang}: {type(e).__name__}")
        try:
            add(_ddg(q))
        except Exception as e:  # noqa: BLE001
            errors.append(f"ddg:{lang}: {type(e).__name__}")

    try:
        add(_stackexchange(topic.get("query_en", topic.get("title", ""))))
    except Exception as e:  # noqa: BLE001
        errors.append(f"stackexchange: {type(e).__name__}")

    return {"sources": sources[:8], "errors": errors}
