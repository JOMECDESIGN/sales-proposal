"""给群 / 用户开放某个飞书资源(多维表格 / 文档 / 知识库节点等)的读写权限。

整群授权用 --chat(member_type=openchat,群内成员含后续加入者自动继承);
个人授权用 --user(open_id)。

用法:
    # 给某群只读看板
    python grant_access.py --token <app_token> --type bitable --chat oc_xxx --perm view
    # 给某群可编辑
    python grant_access.py --token <app_token> --type bitable --chat oc_xxx --perm edit
    # 给某人查看文档
    python grant_access.py --token <docx_token> --type docx --user ou_xxx --perm view
"""
from __future__ import annotations

import argparse

from feishu_api import check, host, req, token

TYPES = ["doc", "docx", "sheet", "file", "wiki", "bitable", "mindnote", "slides"]


def main() -> int:
    p = argparse.ArgumentParser(description="给群/用户开放飞书资源权限")
    p.add_argument("--token", required=True, help="资源 token(多维表格 app_token / 文档 token / wiki 节点 token)")
    p.add_argument("--type", required=True, choices=TYPES, help="资源类型")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--chat", help="群 chat_id(oc_...),整群授权")
    g.add_argument("--user", help="用户 open_id(ou_...)")
    p.add_argument("--perm", default="view", choices=["view", "edit", "full_access"], help="权限角色")
    args = p.parse_args()

    if args.chat:
        member_type, member_id = "openchat", args.chat
    else:
        member_type, member_id = "openid", args.user

    tok = token()
    h = host()
    url = f"{h}/open-apis/drive/v1/permissions/{args.token}/members?type={args.type}"
    r = req("POST", url, tok, body={"member_type": member_type, "member_id": member_id, "perm": args.perm})
    check(r, "添加协作者")
    print(f"✓ 已授权:{member_type} {member_id} → {args.perm}（{args.type} {args.token}）")

    lst = req("GET", url, tok)
    print("当前协作者:")
    for m in lst.get("data", {}).get("items", []):
        print(f"  - {m.get('member_type')} {m.get('member_id')} -> {m.get('perm')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
