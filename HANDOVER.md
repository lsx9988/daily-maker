# HANDOVER — daily-maker

## 一句话
跑在 GitHub Actions 上的日更项目：每天 00:00（北京时间）自动产出一个可直接打开使用的单文件小工具/小作品，配图文说明，按日期归档，历史不回写。

## 运行链路
1. `scripts/generate.py` 主流程：选题 → 取材 → 归纳/降级 → 生成成品与文档 → 登记历史。
2. `scripts/common.py`：路径、北京时间（UTC+8）、日期种子、历史读写、黑名单。
3. `scripts/research.py`：维基 / DuckDuckGo / StackExchange 多源摘要检索，失败返回空，不阻塞。
4. `scripts/llm.py`：可选 OpenRouter 兼容归纳；无 Key / 超时 / 解析失败返回 None，走降级。
5. `scripts/templates.py`：本地已测可用的成品模板库（纯前端 HTML/CSS/JS，零依赖离线可开）。
6. `scripts/render.py`：说明页 HTML、Markdown、README 索引渲染。

## 当日产物（`output/YYYY-MM-DD/`）
- `app.html`：成品工具/作品，浏览器直接打开即用。
- `index.html`：图文说明，含「打开今日工具」入口、步骤、注意事项、排查、验收、来源、免责。
- `guide.md`：可读版说明。
- `meta.json`：期号、日期、生成时间、种子、类别、难度、生成方式、模型、来源数。

## 三级降级（保证每天一定有产出）
1. LLM 归纳说明（需 Secret `OPENROUTER_API_KEY`）；
2. 无 LLM 时用检索摘要 + 通用骨架模板拼装；
3. 素材也不足时使用 `config/topics.json` 的 `fallback` 兜底条目。

成品 `app.html` 始终来自本地模板，不由 LLM 生成代码，避免出现跑不起来的页面。

## 如何新增一个成品工具
1. 在 `scripts/templates.py` 写 `render_xxx(params)`，返回完整自包含 HTML；
2. 在 `TEMPLATES` 字典登记 `tool_type`；
3. 在 `config/topics.json` 的某类别下加 topic，`tool_type` 对上即可；
4. 本地用 `python scripts/generate.py --date <日期>` 验证，浏览器打开 `app.html` 确认交互可用、控制台无报错。

## 定时与认证
- 工作流：`.github/workflows/daily.yml`，cron `0 16 * * *`（UTC）= 北京 00:00；另支持 `workflow_dispatch` 手动补跑。
- 提交身份为 github-actions[bot]，`GITHUB_TOKEN` 自带，无需 PAT。
- 可选 Secret：`OPENROUTER_API_KEY`、`OPENROUTER_MODEL`。

## 已知限制
- GitHub 定时任务可能延迟数十分钟，非精确整点。
- Actions runner 在海外；本地网络访问维基等可能超时属正常，runner 环境另行验证。
- 说明文字由 AI 归纳，可能有误，页面已附免责声明，实操前请核对可靠来源。
- 纯本地模板阶段，成品丰富度取决于模板库规模，后续可继续补模板。
