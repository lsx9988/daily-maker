#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量文件按「前缀_序号.扩展名」重命名。默认仅预览（dry-run），加 --apply 才执行。"""
import argparse
import os
import sys


def main():
    ap = argparse.ArgumentParser(description="批量文件按序号重命名（默认预览）")
    ap.add_argument("--dir", default=".", help="目标目录，默认当前目录")
    ap.add_argument("--prefix", default="file", help="文件名前缀，默认 file")
    ap.add_argument("--start", type=int, default=1, help="序号起始，默认 1")
    ap.add_argument("--apply", action="store_true", help="真正执行重命名；不加则只预览")
    args = ap.parse_args()

    if not os.path.isdir(args.dir):
        print(f"目录不存在：{args.dir}")
        sys.exit(1)

    files = sorted(
        f for f in os.listdir(args.dir)
        if os.path.isfile(os.path.join(args.dir, f)) and not f.startswith(".")
    )
    if not files:
        print("目录里没有可处理的文件。")
        return

    plan = []
    for i, name in enumerate(files, start=args.start):
        ext = os.path.splitext(name)[1]
        new = f"{args.prefix}_{i:03d}{ext}"
        plan.append((name, new))

    for old, new in plan:
        print(f"  {old}  ->  {new}")

    if not args.apply:
        print("\n这是预览，未改动任何文件。确认无误后加 --apply 执行。")
        return

    for old, new in plan:
        if old == new:
            continue
        os.rename(os.path.join(args.dir, old), os.path.join(args.dir, new))
    print(f"\n已重命名 {len(plan)} 个文件。")


if __name__ == "__main__":
    main()
