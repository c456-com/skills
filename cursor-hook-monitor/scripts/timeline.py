#!/usr/bin/env python3
"""把 <conversation_id>.jsonc 事件流渲染成可读时间线（事后观测用）。

用法：
    timeline.py <log_dir> <conversation_id>
    timeline.py <path/to/xxx.jsonc>

只读，不修改任何文件。
"""
import sys
import os
import json
import time


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue          # 跳过半截行
    return rows


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)

    arg = sys.argv[1]
    if len(sys.argv) >= 3:
        path = os.path.join(arg, f"{sys.argv[2]}.jsonc")
    else:
        path = arg

    if not os.path.exists(path):
        sys.exit(f"文件不存在：{path}")

    rows = load(path)
    if not rows:
        sys.exit("事件流为空")

    # 按 generation_id 分轮，统计每轮时长
    rounds = {}
    order = []
    for r in rows:
        g = r.get("generation_id")
        if g not in rounds:
            rounds[g] = {"start": None, "end": None, "events": []}
            order.append(g)
        rd = rounds[g]
        rd["events"].append(r.get("event"))
        if r.get("event") == "beforeSubmitPrompt":
            rd["start"] = r.get("ts")
        if r.get("event") == "stop":
            rd["end"] = r.get("ts")

    base = rows[0].get("ts")
    print(f"事件流：{path}")
    print(f"事件数：{len(rows)}   轮数：{len(order)}")
    print(f"conversation_id：{rows[0].get('conversation_id')}")
    print(f"workspace_roots：{rows[0].get('workspace_roots')}")
    print()

    for i, g in enumerate(order, 1):
        rd = rounds[g]
        st, en = rd["start"], rd["end"]
        if st and en:
            dur = f"{en - st:.2f}s"
            st_s = time.strftime("%H:%M:%S", time.localtime(st))
            en_s = time.strftime("%H:%M:%S", time.localtime(en))
        elif st:
            dur = "进行中"
            st_s = time.strftime("%H:%M:%S", time.localtime(st))
            en_s = "-"
        else:
            dur, st_s, en_s = "无起点", "-", "-"
        print(f"轮 {i}  gen={str(g)[:8]}  {st_s} → {en_s}  ({dur})")
        print(f"        事件：{' → '.join(rd['events'])}")
        print()


if __name__ == "__main__":
    main()
