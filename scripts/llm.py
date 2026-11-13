# -*- coding: utf-8 -*-
"""可选的 LLM 归纳层。

读取环境变量 OPENROUTER_API_KEY（存 GitHub Secrets）。无 Key、超时、解析失败时
统一返回 None，由上层走模板拼装 / 兜底条目，不阻塞当天产出。
仅用标准库 urllib，OpenAI 兼容 /chat/completions 接口。
"""
import json
import os
import re
import urllib.request

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
TIMEOUT = 60

# 依次尝试的免费模型；可用环境变量 OPENROUTER_MODEL 覆盖为单个模型
DEFAULT_MODELS = [
    "google/gemma-4-31b-it:free",
    "baidu/ernie-5.5-flash-preview:free",
]

SYSTEM_PROMPT = (
    "你是一名严谨的实用教程作者。根据用户给出的主题和公开资料摘要，"
    "整理成一份中文、可照做的结构化教程。要求：\n"
    "1. 步骤具体、顺序清晰，每步有动作和一个关键提示；\n"
    "2. 只依据素材与通用常识，不编造具体型号参数、电压数值或工具尺寸；素材不足时写通用做法；\n"
    "3. 涉及电气、高温、锋利工具、化学品、登高、车辆等，在 cautions 里给安全提醒，不写危险操作细节；\n"
    "4. 不提供医疗、法律、理财、武器、爆炸物、毒品、破解入侵等内容；\n"
    "5. 严格只输出一个 JSON 对象，不要注释、不要多余文字。"
)

JSON_SCHEMA_HINT = (
    '输出 JSON 字段：title(字符串), intro(一句话简介), level(入门/进阶), '
    'tools(字符串数组), materials(字符串数组), '
    'steps(数组，每项 {step:数字, action:字符串, tip:字符串}), '
    'cautions(字符串数组), troubleshooting(字符串数组), success(一句话验收标准)。'
)


def _payload(model, topic, sources):
    src_lines = []
    for i, s in enumerate(sources, 1):
        src_lines.append(f"[{i}] {s['title']} —— {s['snippet']}（来源：{s['url']}）")
    src_text = "\n".join(src_lines) or "（本次未检索到公开摘要，按通用常识编写通用步骤）"

    user = (
        f"主题：{topic['title']}\n类别：{topic.get('category', '')}\n"
        f"检索到的公开摘要：\n{src_text}\n\n"
        f"{JSON_SCHEMA_HINT}"
    )
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ],
        "temperature": 0.4,
        "max_tokens": 1600,
    }


def _extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    return json.loads(text[start:end + 1])


def _normalize(obj):
    """补齐字段、清洗类型；steps 为空则判为无效。"""
    if not isinstance(obj, dict):
        return None
    steps = obj.get("steps") or []
    if not isinstance(steps, list) or not steps:
        return None
    clean_steps = []
    for i, s in enumerate(steps, 1):
        if not isinstance(s, dict):
            continue
        action = str(s.get("action", "")).strip()
        if not action:
            continue
        clean_steps.append({
            "step": i,
            "action": action,
            "tip": str(s.get("tip", "")).strip(),
        })
    if not clean_steps:
        return None

    def _list(v):
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str) and v.strip():
            return [v.strip()]
        return []

    return {
        "title": str(obj.get("title") or "").strip() or "未命名教程",
        "intro": str(obj.get("intro") or "").strip(),
        "level": str(obj.get("level") or "入门").strip(),
        "tools": _list(obj.get("tools")),
        "materials": _list(obj.get("materials")),
        "steps": clean_steps,
        "cautions": _list(obj.get("cautions")),
        "troubleshooting": _list(obj.get("troubleshooting")),
        "success": str(obj.get("success") or "").strip(),
    }


def generate_guide(topic, sources):
    """返回规范化教程 dict；不可用/失败返回 None。"""
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        print("[llm] 未配置 OPENROUTER_API_KEY，跳过 LLM 归纳")
        return None

    models = [os.environ.get("OPENROUTER_MODEL", "").strip()] if os.environ.get("OPENROUTER_MODEL") else DEFAULT_MODELS
    last_err = None
    for model in models:
        if not model:
            continue
        try:
            req = urllib.request.Request(
                BASE_URL,
                data=json.dumps(_payload(model, topic, sources)).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/lsx9988/daily-maker",
                    "X-Title": "daily-maker",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                obj = json.loads(resp.read().decode("utf-8", "ignore"))
            text = obj["choices"][0]["message"]["content"]
            guide = _normalize(_extract_json(text))
            if guide:
                guide["_model"] = model
                print(f"[llm] 归纳成功 -> {model}")
                return guide
            last_err = "JSON 校验未通过"
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            print(f"[llm] 模型 {model} 失败: {last_err}")
            continue

    print(f"[llm] 全部模型不可用: {last_err}")
    return None
