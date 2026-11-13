# -*- coding: utf-8 -*-
"""把规范化教程渲染成自包含 HTML、Markdown，并重建 README 每日索引。"""
import html
import os

from common import OUTPUT_DIR, ROOT, today_str

README_PATH = os.path.join(ROOT, "README.md")


def esc(v):
    return html.escape(str(v if v is not None else ""), quote=True)


def _svg_placeholder(category):
    """按类别给一个简单几何占位示意，纯内联 SVG，无外部依赖。"""
    palette = {
        "电子制作": "#4f6b9a", "数码与家用维修": "#9a6a2f", "工具改进与自制": "#3f8a6b",
        "小开发与脚本": "#6a5a9a", "居家手工与改造": "#a14e50", "实用生活技巧": "#5f7a3f",
        "改进与升级思路": "#3d7a8a", "实用清单": "#5f6670",
    }
    color = palette.get(category, "#4f6b9a")
    return f"""<svg viewBox="0 0 320 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="示意">
  <rect x="0" y="0" width="320" height="140" rx="10" fill="#f2f4f7"/>
  <circle cx="80" cy="70" r="34" fill="none" stroke="{color}" stroke-width="6"/>
  <rect x="150" y="46" width="120" height="48" rx="8" fill="none" stroke="{color}" stroke-width="6"/>
  <line x1="80" y1="36" x2="80" y2="104" stroke="{color}" stroke-width="3" opacity="0.4"/>
  <line x1="46" y1="70" x2="114" y2="70" stroke="{color}" stroke-width="3" opacity="0.4"/>
</svg>"""


def _list_html(items, empty="—"):
    if not items:
        return f"<li>{esc(empty)}</li>"
    return "".join(f"<li>{esc(x)}</li>" for x in items)


def render_html(ctx):
    guide, meta, sources, disclaimer = ctx["guide"], ctx["meta"], ctx["sources"], ctx["disclaimer"]
    steps = "".join(
        f"<li class='step'><div class='step-no'>{s['step']}</div>"
        f"<div><div class='action'>{esc(s['action'])}</div>"
        + (f"<div class='tip'>提示：{esc(s['tip'])}</div>" if s.get("tip") else "")
        + "</div></li>"
        for s in guide["steps"]
    )
    src_rows = "".join(
        f"<li>{esc(s['title'])}（{esc(s['source'])}）—— "
        f"<a href='{esc(s['url'])}' target='_blank' rel='noopener noreferrer'>{esc(s['url'])}</a></li>"
        if s.get("url") else f"<li>{esc(s['title'])}（{esc(s['source'])}）</li>"
        for s in sources
    ) or "<li>本次未取到外部来源，内容为通用整理。</li>"
    dis = "".join(f"<li>{esc(x)}</li>" for x in disclaimer)

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>第 {meta['issue']} 期 · {esc(guide['title'])}</title>
<style>
body{{margin:0;padding:24px 16px;background:#f7f7f5;color:#1a1b1c;font-family:-apple-system,'Segoe UI','Microsoft YaHei',sans-serif;line-height:1.7}}
.wrap{{max-width:860px;margin:0 auto}}
.head{{margin-bottom:16px}}
.kicker{{font-size:13px;color:#5f6670;letter-spacing:.5px}}
h1{{font-size:24px;margin:6px 0 8px}}
.meta{{font-size:13px;color:#5f6670}}
.badges{{margin:8px 0 0}}
.badge{{display:inline-block;font-size:12px;color:#3d434b;background:#eef1f5;border-radius:10px;padding:2px 10px;margin-right:6px}}
.btn{{display:inline-block;margin-top:12px;background:#4f6b9a;color:#fff;text-decoration:none;border-radius:8px;padding:10px 16px;font-weight:600}}
.btn:hover{{background:#3d5a82}}
.card{{background:#fff;padding:16px 18px;border-radius:8px;margin-bottom:14px}}
h2{{font-size:16px;margin:0 0 10px;padding-left:9px;border-left:3px solid #4f6b9a}}
.two{{display:flex;flex-wrap:wrap;gap:14px}}
.two>div{{flex:1 1 260px;background:#fff;border-radius:8px;padding:14px 16px}}
ul{{margin:4px 0;padding-left:20px}}
li{{margin:5px 0}}
.step{{display:flex;gap:12px;margin:12px 0}}
.step-no{{flex:0 0 28px;height:28px;border-radius:50%;background:#4f6b9a;color:#fff;text-align:center;line-height:28px;font-weight:700}}
.action{{font-weight:600}}
.tip{{font-size:13px;color:#9a6a2f;margin-top:2px}}
.warn{{background:#fff;border-left:3px solid #a14e50;padding:12px 16px;font-size:13px;border-radius:4px}}
.note{{background:#fff;border-left:3px solid #3f8a6b;padding:12px 16px;font-size:13px;border-radius:4px}}
.svg{{max-width:320px;margin:6px 0}}
a{{color:#4f6b9a}}
.footer{{margin-top:24px;font-size:12px;color:#8a9099}}
</style></head><body><div class="wrap">
<div class="head">
  <div class="kicker">daily-maker · 第 {meta['issue']} 期</div>
  <h1>{esc(guide['title'])}</h1>
  <div class="meta">日期：{esc(meta['date'])}　·　生成时间：{esc(meta['gen_time'])}　·　选题种子：{esc(meta['seed'])}</div>
  <div class="badges">
    <span class="badge">类别：{esc(meta['category'])}</span>
    <span class="badge">难度：{esc(guide.get('level', '入门'))}</span>
    <span class="badge">生成方式：{esc(meta['route'])}</span>
  </div>
  <a class="btn" href="app.html">打开今日工具 ↗</a>
</div>

<div class="card">{_svg_placeholder(meta['category'])}</div>

<div class="card"><h2>简介</h2><p>{esc(guide.get('intro', ''))}</p></div>

<div class="two">
  <div><h2>工具清单</h2><ul>{_list_html(guide.get('tools', []))}</ul></div>
  <div><h2>材料 / 零件</h2><ul>{_list_html(guide.get('materials', []))}</ul></div>
</div>

<div class="card"><h2>操作步骤</h2><ol style="list-style:none;padding-left:0">{steps}</ol></div>

<div class="warn"><h2 style="border-color:#a14e50">注意事项</h2><ul>{_list_html(guide.get('cautions', []))}</ul></div>

<div class="card"><h2>常见问题与排查</h2><ul>{_list_html(guide.get('troubleshooting', []))}</ul></div>

<div class="note"><h2 style="border-color:#3f8a6b">验收标准</h2><p>{esc(guide.get('success', ''))}</p></div>

<div class="card"><h2>参考来源</h2><ul>{src_rows}</ul></div>

<div class="warn"><h2 style="border-color:#a14e50">免责声明</h2><ol>{dis}</ol></div>

<div class="footer">生成器：daily-maker（个人自动化项目）　·　本期编号 {meta['issue']}　·　{esc(meta['date'])}</div>
</div></body></html>"""


def render_md(ctx):
    guide, meta, sources, disclaimer = ctx["guide"], ctx["meta"], ctx["sources"], ctx["disclaimer"]
    lines = [
        f"# 第 {meta['issue']} 期 · {guide['title']}",
        "",
        f"- 日期：{meta['date']}　·　生成时间：{meta['gen_time']}　·　选题种子：{meta['seed']}",
        f"- 类别：{meta['category']}　·　难度：{guide.get('level', '入门')}　·　生成方式：{meta['route']}",
        "",
        f"## 简介",
        guide.get("intro", ""),
        "",
        f"[打开今日工具 app.html](app.html)",
        "",
        "## 工具清单",
    ]
    lines += [f"- {x}" for x in guide.get("tools", [])] or ["- —"]
    lines += ["", "## 材料 / 零件"]
    lines += [f"- {x}" for x in guide.get("materials", [])] or ["- —"]
    lines += ["", "## 操作步骤"]
    for s in guide["steps"]:
        lines.append(f"{s['step']}. {s['action']}" + (f"（提示：{s['tip']}）" if s.get("tip") else ""))
    lines += ["", "## 注意事项"]
    lines += [f"- {x}" for x in guide.get("cautions", [])] or ["- —"]
    lines += ["", "## 常见问题与排查"]
    lines += [f"- {x}" for x in guide.get("troubleshooting", [])] or ["- —"]
    lines += ["", "## 验收标准", guide.get("success", ""), "", "## 参考来源"]
    for s in sources:
        lines.append(f"- {s['title']}（{s['source']}）：{s['url']}")
    if not sources:
        lines.append("- 本次未取到外部来源，内容为通用整理。")
    lines += ["", "## 免责声明"]
    lines += [f"{i}. {x}" for i, x in enumerate(disclaimer, 1)]
    lines += ["", f"---", f"daily-maker · 第 {meta['issue']} 期 · {meta['date']}", ""]
    return "\n".join(lines)


def update_readme(history):
    """扫描历史索引重建 README 的每日清单（只放链接，不改写当日作品内容）。"""
    entries = history.get("entries", [])
    rows = []
    for e in reversed(entries):
        link = f"output/{e['date']}/index.html"
        rows.append(f"| {e['date']} | [#{e['issue']} {e['title']}]({link}) | {e.get('category', '')} | {e.get('level', '')} | {e.get('route', '')} |")
    table = "\n".join(rows) or "| 日期 | 标题 | 类别 | 难度 | 生成方式 |\n|---|---|---|---|---|"

    body = f"""# daily-maker

每天自动产出一个**能直接打开使用**的小工具/小作品，配一份图文说明：颜色设计、文本处理、换算计算、计时专注、决策随机、清单对照、生成艺术等方向轮转。成品是本地单文件网页（离线可用、不上传数据），按日期归档，历史作品不回写、不覆盖。

## 它每天做什么

1. **选题**：按当天日期作随机种子，从 `config/topics.json` 选题池抽取，自动避开近期用过的题目与敏感词。
2. **取材**：检索多个公开来源的摘要（维基 / DuckDuckGo / StackExchange），保留参考链接。
3. **归纳**：配置了 LLM Key 时由模型把素材整理成结构化教程；无 Key 或调用失败时，自动降级为模板拼装；素材也不足时使用内置兜底条目。
4. **产出**：写入 `output/YYYY-MM-DD/`（`app.html` 可直接使用的成品、`index.html` 图文说明、`guide.md` 可读版、`meta.json` 元数据），并在下表登记索引。

## 每日产出

| 日期 | 标题 | 类别 | 难度 | 生成方式 |
|---|---|---|---|---|
{table}

## 目录结构

```
daily-maker/
├── config/topics.json        # 选题池、黑名单、兜底条目、免责文案
├── scripts/common.py         # 路径 / 北京时间 / 种子 / 历史记录
├── scripts/research.py       # 公开来源检索（多源降级）
├── scripts/llm.py            # 可选 LLM 归纳（OpenRouter 兼容）
├── scripts/render.py         # HTML / Markdown / README 索引渲染
├── scripts/templates.py      # 本地已测可用的单文件成品模板库
├── scripts/generate.py       # 主流程
├── output/YYYY-MM-DD/        # 当日作品归档
└── .github/workflows/daily.yml
```

## 手动运行

```bash
python scripts/generate.py            # 完整流程
python scripts/generate.py --date 2026-11-13   # 指定日期调试
```

## 配置说明

- **LLM（可选）**：在仓库 Settings → Secrets and variables → Actions 添加 `OPENROUTER_API_KEY`；不配置也能跑，走模板降级。
- **选题与方向**：改 `config/topics.json` 即可增删主题类别与题目。
- **仅用 Python 标准库**，Actions 无需安装第三方依赖。

## 免责声明

本项目由公开资料检索后经 AI 归纳自动生成教程，可能存在错误或过时；实操前请核对官方文档与专业来源。涉及电气、高温、锋利工具、化学品、登高、车辆等操作请遵守安全规范，不确定时咨询专业人员。本内容不构成医疗、法律、财务等专业建议，照搬操作的风险由操作者自行承担。
"""
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(body)
