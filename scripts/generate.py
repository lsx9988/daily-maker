# -*- coding: utf-8 -*-
"""daily-maker 主流程。

每天：选题 -> 公开来源取材 -> (可选)LLM 归纳说明 -> 生成本地已测可用的单文件成品
app.html + 图文说明 index.html + guide.md + meta.json，按日期归档并登记索引。
历史日期目录不回写、不覆盖；仅追加当天条目。
"""
import argparse
import json
import os
import random

import common
import research
import llm
import render
import templates


def build_template_guide(topic, sources, config):
    """无 LLM 时的模板拼装：用检索摘要 + 通用骨架组织说明。"""
    snippet = sources[0]["snippet"] if sources else ""
    intro = snippet or f"本主题围绕「{topic['title']}」展开，配套成品可在当日目录的 app.html 直接打开使用。"
    steps = [
        {"step": 1, "action": "先阅读本说明，了解这个工具/作品用来做什么、适用场景。", "tip": "对照下方工具清单与材料确认前提。"},
        {"step": 2, "action": "打开同目录下的 app.html，页面在浏览器中加载后即可操作使用。", "tip": "本地单文件，无需联网、无需安装。"},
        {"step": 3, "action": "按页面提示交互试用，观察结果是否符合预期。", "tip": "可反复操作，刷新页面即恢复初始状态。"},
        {"step": 4, "action": "对照验收标准确认成品可用；遇到问题查看下方排查项。", "tip": "本工具不上传任何本地数据。"},
    ]
    return {
        "title": topic["title"],
        "intro": intro,
        "level": topic.get("level", "入门"),
        "tools": ["现代浏览器（Chrome / Edge / Firefox 等）"],
        "materials": [],
        "steps": steps,
        "cautions": ["页面为本地工具，请勿在不明来源的同类页面中输入敏感信息。"],
        "troubleshooting": ["页面空白或按钮无响应：刷新浏览器后重试，或更换现代浏览器打开。"],
        "success": "app.html 能正常打开并完成一次交互操作。",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="指定日期 YYYY-MM-DD（调试用），默认今天（北京时间）")
    args = ap.parse_args()

    config = common.load_json(common.CONFIG_PATH, {})
    history = common.load_history()

    date_str = args.date or common.today_str()
    seed = common.date_seed(date_str)
    rng = random.Random(seed)
    now = common.now_bjt()
    gen_time = common.gen_time_str(now)

    # 1. 选题
    topic, category, _ = common.pick_topic(config, history, rng)
    print(f"[1/5] 选题：{topic['title']}（{category} / {topic.get('tool_type')}）")

    # 2. 公开来源取材
    print("[2/5] 检索公开来源 ...")
    fetched = research.research(topic)
    sources = fetched["sources"]
    print(f"      来源 {len(sources)} 条；错误：{', '.join(fetched['errors']) or '无'}")

    # 3. 归纳说明（可选 LLM），失败逐级降级
    guide = llm.generate_guide(topic, sources)
    route = "LLM 归纳"
    if guide is None:
        guide = build_template_guide(topic, sources, config)
        route = "模板生成"
    if not guide.get("steps"):
        guide = config.get("fallback", {})
        route = "兜底条目"

    issue = len(history.get("entries", [])) + 1

    # 4. 生成成品 + 文档
    day_dir = os.path.join(common.OUTPUT_DIR, date_str)
    os.makedirs(day_dir, exist_ok=True)

    tpl_params = {
        "title": guide["title"],
        "seed": seed,
        "date": date_str,
        "issue": issue,
        "items": [s["action"] for s in guide.get("steps", [])],
    }
    app_html = templates.render_app(topic.get("tool_type", "counter"), tpl_params)

    meta = {
        "issue": issue,
        "date": date_str,
        "gen_time": gen_time,
        "seed": seed,
        "category": category,
        "level": guide.get("level", "入门"),
        "tool_type": topic.get("tool_type", "counter"),
        "route": route,
        "model": guide.get("_model", ""),
        "source_count": len(sources),
        "tags": topic.get("tags", []),
    }
    ctx = {"guide": guide, "meta": meta, "sources": sources,
           "disclaimer": config.get("disclaimer", [])}

    with open(os.path.join(day_dir, "app.html"), "w", encoding="utf-8") as f:
        f.write(app_html)
    with open(os.path.join(day_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(render.render_html(ctx))
    with open(os.path.join(day_dir, "guide.md"), "w", encoding="utf-8") as f:
        f.write(render.render_md(ctx))
    with open(os.path.join(day_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "sources": sources}, f, ensure_ascii=False, indent=2)

    # 5. 登记历史索引（只追加当天条目，不改旧条目）
    entries = history.get("entries", [])
    entries = [e for e in entries if e.get("date") != date_str]
    entries.append({
        "date": date_str, "issue": issue, "title": guide["title"],
        "category": category, "level": guide.get("level", "入门"),
        "route": route, "tool_type": topic.get("tool_type", "counter"),
        "source_count": len(sources),
    })
    history["entries"] = entries
    history["updated"] = date_str
    common.save_json(common.HISTORY_PATH, history)

    render.update_readme(history)

    print(f"[5/5] 完成 -> output/{date_str}/（第 {issue} 期，{route}）")
    return {"issue": issue, "date": date_str, "title": guide["title"],
            "route": route, "sources": len(sources), "tool_type": topic.get("tool_type")}


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, ensure_ascii=False))
