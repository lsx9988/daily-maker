#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按扩展名把目录里的散文件归类到子文件夹。默认预览，加 --apply 才移动。"""
import argparse
import os
import sys


def bucket(name):
    ext = os.path.splitext(name)[1].lower().lstrip(".")
    return ext if ext else "_noext"


def main():
    ap = argparse.ArgumentParser(description="按扩展名归类文件（默认预览）")
    ap.add_argument("--dir", default=".", help="目标目录，默认当前目录")
    ap.add_argument("--apply", action="store_true", help="真正移动文件；不加则只预览")
    args = ap.parse_args()

    if not os.path.isdir(args.dir):
        print(f"目录不存在：{args.dir}")
        sys.exit(1)

    moves = []
    for name in sorted(os.listdir(args.dir)):
        full = os.path.join(args.dir, name)
        if not os.path.isfile(full) or name.startswith("."):
            continue
        moves.append((name, bucket(name)))

    if not moves:
        print("目录里没有可处理的文件。")
        return

    for name, b in moves:
        print(f"  {name}  ->  {b}/")

    if not args.apply:
        print("\n这是预览，未移动任何文件。确认无误后加 --apply 执行。")
        return

    for name, b in moves:
        folder = os.path.join(args.dir, b)
        os.makedirs(folder, exist_ok=True)
        os.rename(os.path.join(args.dir, name), os.path.join(folder, name))
    print(f"\n已归类 {len(moves)} 个文件。")


if __name__ == "__main__":
    main()
