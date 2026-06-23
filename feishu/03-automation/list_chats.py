"""列出机器人所在的群及其 chat_id(配置 notify.py 的播报群时用)。

用法:
    python list_chats.py            # 列全部
    python list_chats.py --grep PMO # 只看名字含 PMO 的群
"""
from __future__ import annotations

import argparse

from feishu_api import check, host, req, token


def main() -> int:
    p = argparse.ArgumentParser(description="列出机器人所在的群")
    p.add_argument("--grep", default="", help="按群名过滤(子串匹配)")
    args = p.parse_args()

    tok = token()
    r = req("GET", f"{host()}/open-apis/im/v1/chats?page_size=100", tok)
    check(r, "查询群列表")
    items = r.get("data", {}).get("items", [])
    if not items:
        print("机器人当前不在任何群。先把应用机器人拉进目标群(群设置 → 群机器人 → 添加)。")
        return 0
    print(f"{'CHAT_ID':<24} 群名")
    for it in items:
        name = it.get("name") or "(无名)"
        if args.grep and args.grep not in name:
            continue
        print(f"{it.get('chat_id'):<24} {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
