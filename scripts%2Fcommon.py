# -*- coding: utf-8 -*-
"""共用工具：路径、北京时间、日期种子、历史记录、黑名单判断。

仅使用 Python 标准库，兼容 GitHub Actions 的 Python 3.12 与本地 3.11+。
"""
import json
import os
import random
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config", "topics.json")
OUTPUT_DIR = os.path.join(ROOT, "output")
HISTORY_PATH = os.path.join(OUTPUT_DIR, "history.json")

# 北京时间固定偏移（UTC+8），避免 runner 时区或 tzdata 缺失导致日期错位
BJT = timezone(timedelta(hours=8))


def now_bjt():
    return datetime.now(BJT)


def today_str(now=None):
    now = now or now_bjt()
    return now.strftime("%Y-%m-%d")


def gen_time_str(now=None):
    now = now or now_bjt()
    return now.strftime("%Y-%m-%d %H:%M:%S 北京时间")


def date_seed(date_str):
    """把日期字符串转成稳定整数种子，同一天多次运行结果一致。"""
    return int(date_str.replace("-", ""))


def load_json(path, default=None):
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_history():
    data = load_json(HISTORY_PATH, {"entries": []})
    if not isinstance(data, dict) or "entries" not in data:
        return {"entries": []}
    return data


def recent_titles(history, days):
    """取最近 days 天内已用过的标题，用于避重。"""
    titles = set()
    cutoff = None
    entries = history.get("entries", [])
    for e in entries[-days:]:
        titles.add(e.get("title", ""))
    return titles


def is_blacklisted(text, blacklist):
    t = (text or "").lower()
    for kw in blacklist:
        if kw.lower() in t:
            return True, kw
    return False, None


def pick_topic(config, history, rng=None):
    """按日期种子选题：优先避开近期用过的主题与黑名单词。

    返回 (topic_dict, category_name, reason)。
    """
    rng = rng or random.Random(date_seed(today_str()))
    blacklist = config.get("blacklist", [])
    recent = recent_titles(history, config.get("avoid_recent_days", 21))

    # 先按类别打散，再在类别内挑未近期重复的题目
    categories = config.get("categories", [])
    cat = rng.choice(categories)
    pool = [t for t in cat["topics"] if t["title"] not in recent]
    if not pool:
        # 该类近期用过，换一个有剩余题目的类别
        for c in categories:
            avail = [t for t in c["topics"] if t["title"] not in recent]
            if avail:
                cat, pool = c, avail
                break
    if not pool:
        # 全部近期用过，放宽到全池
        pool = [t for c in categories for t in c["topics"]]

    safe = [t for t in pool if not is_blacklisted(t["title"], blacklist)[0]]
    if not safe:
        safe = pool
    topic = rng.choice(safe)
    return topic, cat["name"], "seeded"
