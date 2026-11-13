# daily-maker

每天自动产出一个**能直接使用**的小工具/小作品，配一份图文说明。成品分三类：本地单文件网页工具（离线可用、不上传数据）、纯标准库 Python 小脚本、开源项目推荐卡片（只链官方仓库，不复制安装包/源码）。按日期归档，历史作品不回写、不覆盖。

## 它每天做什么

1. **选题**：按当天日期作随机种子，从 `config/topics.json` 选题池抽取，自动避开近期用过的题目与敏感词。
2. **取材**：检索多个公开来源的摘要（维基 / DuckDuckGo / StackExchange / GitHub），保留参考链接。
3. **归纳**：配置了 LLM Key 时由模型把素材整理成结构化教程；无 Key 或调用失败时，自动降级为模板拼装；素材也不足时使用内置兜底条目。
4. **产出**：写入 `output/YYYY-MM-DD/`（`app.html` 成品页、`index.html` 图文说明、`guide.md` 可读版、`meta.json` 元数据；脚本类另附 `tool.py`），并在下表登记索引。

## 每日产出

| 日期 | 标题 | 类别 | 难度 | 生成方式 |
|---|---|---|---|---|
| 2026-11-13 | [#1 文本字数与格式统计工具](output/2026-11-13/index.html) | 文本处理工具 | 入门 | 模板生成 |

## 目录结构

```
daily-maker/
├── config/topics.json        # 选题池、黑名单、兜底条目、免责文案
├── scripts/common.py         # 路径 / 北京时间 / 种子 / 历史记录
├── scripts/research.py       # 公开来源检索（多源降级）
├── scripts/llm.py            # 可选 LLM 归纳（OpenRouter 兼容）
├── scripts/render.py         # HTML / Markdown / README 索引渲染
├── scripts/templates.py      # 本地已测模板库（网页工具 / Python 脚本 / 开源推荐卡片）
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
