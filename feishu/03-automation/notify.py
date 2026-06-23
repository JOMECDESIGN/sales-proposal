"""方案状态 -> 飞书机器人卡片播报。

用法:
  python notify.py --title "XX项目方案" --status 答辩中 --owner 张三 \
                   --link https://... --note "周五现场演示"

前置:机器人已被拉进 FEISHU_NOTIFY_CHAT_ID 指向的群;应用开通 im:message。
"""
from __future__ import annotations
import argparse
import json

import lark_oapi as lark
from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody

from lark_client import get_client, env

# 状态 -> 卡片主题色
STATUS_COLOR = {
    "立项": "blue", "挖需求": "turquoise", "撰写中": "wathet",
    "自检": "purple", "答辩中": "orange", "已提交": "green",
    "赢单": "green", "丢单": "grey", "搁置": "grey",
}


def build_card(title: str, status: str, owner: str, link: str, note: str) -> dict:
    fields = [
        {"is_short": True, "text": {"tag": "lark_md", "content": f"**状态**\n{status}"}},
        {"is_short": True, "text": {"tag": "lark_md", "content": f"**负责人**\n{owner or '—'}"}},
    ]
    if note:
        fields.append({"is_short": False, "text": {"tag": "lark_md", "content": f"**备注**\n{note}"}})
    elements = [{"tag": "div", "fields": fields}]
    if link:
        elements.append({"tag": "action", "actions": [
            {"tag": "button", "text": {"tag": "plain_text", "content": "打开方案"},
             "type": "primary", "url": link}
        ]})
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": STATUS_COLOR.get(status, "blue"),
            "title": {"tag": "plain_text", "content": f"📄 {title}"},
        },
        "elements": elements,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="发送方案状态卡片到飞书群")
    ap.add_argument("--title", required=True)
    ap.add_argument("--status", required=True)
    ap.add_argument("--owner", default="")
    ap.add_argument("--link", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--chat-id", default="", help="覆盖 FEISHU_NOTIFY_CHAT_ID")
    args = ap.parse_args()

    chat_id = args.chat_id or env("FEISHU_NOTIFY_CHAT_ID")
    client = get_client()

    card = build_card(args.title, args.status, args.owner, args.link, args.note)
    req = (
        CreateMessageRequest.builder()
        .receive_id_type("chat_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type("interactive")
            .content(json.dumps(card, ensure_ascii=False))
            .build()
        )
        .build()
    )
    resp = client.im.v1.message.create(req)
    if not resp.success():
        raise SystemExit(f"发送失败 code={resp.code} msg={resp.msg} log_id={resp.get_log_id()}")
    print(f"已发送:{args.title} [{args.status}] -> {chat_id}")


if __name__ == "__main__":
    main()
