#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文本文件行数/字符统计与按行去重。默认只统计预览，加 --write 才写出去重文件。"""
import argparse
import os
import sys


def main():
    ap = argparse.ArgumentParser(description="文本统计与按行去重（默认预览）")
    ap.add_argument("file", help="要处理的文本文件路径")
    ap.add_argument("--write", action="store_true", help="写出去重后的 .dedup.txt；不加则只统计")
    args = ap.parse_args()

    if not os.path.isfile(args.file):
        print(f"文件不存在：{args.file}")
        sys.exit(1)

    with open(args.file, "r", encoding="utf-8-sig", errors="ignore") as f:
        lines = f.read().splitlines()

    total = len(lines)
    nonempty = [ln for ln in lines if ln.strip()]
    chars = sum(len(ln) for ln in nonempty)
    seen = set()
    dedup = []
    for ln in nonempty:
        if ln not in seen:
            seen.add(ln)
            dedup.append(ln)

    print(f"总行数：{total}")
    print(f"非空行数：{len(nonempty)}")
    print(f"非空字符数：{chars}")
    print(f"去重后行数：{len(dedup)}（移除 {len(nonempty) - len(dedup)} 行重复）")

    if not args.write:
        print("\n这是预览，未写出文件。确认后加 --write 生成 .dedup.txt。")
        return

    base, ext = os.path.splitext(args.file)
    out = base + ".dedup" + (ext or ".txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(dedup) + "\n")
    print(f"\n已写出：{out}")


if __name__ == "__main__":
    main()
