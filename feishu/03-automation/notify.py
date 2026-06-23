"""方案状态 → 飞书机器人消息卡片。

🏋️ Sales Coach 出完自检、🐑 Project Shepherd 推进到节点时,一行命令把进展播到群里。

用法:
    source ../.env
    python notify.py --title "示例项目 · 执行摘要定稿" --stage "答辩自检" \\
        --status green --owner 张三 \\
        --note "Coach 自检 12 项过 11;CTA 已补具体下一步" \\
        --link "https://xxx.feishu.cn/docx/xxxxx"

--chat 省略时用 .env 里的 FEISHU_NOTIFY_CHAT_ID。
--status: green=正常 / yellow=有风险 / red=阻塞,决定卡片配色与图标。
"""
from __future__ import annotations

import argparse
import json
import sys

import lark_oapi as lark
from lark_oapi.api.im.v1 import (
    CreateMessageRequest,
    CreateMessageRequestBody,
)

from lark_client import build_client, env

_STATUS = {
    "green": ("green", "🟢", "正常推进"),
    "yellow": ("yellow", "🟡", "存在风险"),
    "red": ("red", "🔴", "阻塞待处理"),
}


def build_card(title: str, stage: str, status: str, owner: str,
               note: str, link: str | None) -> str:
    color, icon, status_text = _STATUS[status]
    fields = [
        {"is_short": True, "text": {"tag": "lark_md", "content": f"**阶段**\n{stage}"}},
        {"is_short": True, "text": {"tag": "lark_md", "content": f"**状态**\n{icon} {status_text}"}},
        {"is_short": True, "text": {"tag": "lark_md", "content": f"**负责人**\n{owner or '—'}"}},
    ]
    elements: list[dict] = [{"tag": "div", "fields": fields}]
    if note:
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"**说明**\n{note}"}})
    if link:
        elements.append({
            "tag": "action",
            "actions": [{
                "tag": "button",
                "text": {"tag": "plain_text", "content": "查看方案文档"},
                "type": "primary",
                "url": link,
            }],
        })
    elements.append({"tag": "hr"})
    elements.append({
        "tag": "note",
        "elements": [{"tag": "plain_text", "content": "来自售前方案产线 · 自动播报"}],
    })

    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": color,
            "title": {"tag": "plain_text", "content": f"{icon} {title}"},
        },
        "elements": elements,
    }
    return json.dumps(card, ensure_ascii=False)


def main() -> int:
    p = argparse.ArgumentParser(description="发送方案状态卡片到飞书群")
    p.add_argument("--title", required=True, help="方案/事项标题")
    p.add_argument("--stage", required=True, help="所处阶段,如 挖需求/赢主题/答辩自检/交付")
    p.add_argument("--status", choices=list(_STATUS), default="green")
    p.add_argument("--owner", default="", help="负责人")
    p.add_argument("--note", default="", help="补充说明")
    p.add_argument("--link", default="", help="方案云文档链接")
    p.add_argument("--chat", default="", help="目标群 chat_id(默认取 FEISHU_NOTIFY_CHAT_ID)")
    args = p.parse_args()

    chat_id = args.chat or env("FEISHU_NOTIFY_CHAT_ID", required=True)
    client = build_client()

    content = build_card(args.title, args.stage, args.status,
                         args.owner, args.note, args.link or None)
    request = (
        CreateMessageRequest.builder()
        .receive_id_type("chat_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type("interactive")
            .content(content)
            .build()
        )
        .build()
    )

    resp = client.im.v1.message.create(request)
    if not resp.success():
        print(f"✗ 发送失败 code={resp.code} msg={resp.msg} "
              f"log_id={resp.get_log_id()}", file=sys.stderr)
        return 1
    print(f"✓ 已发送到 {chat_id},message_id={resp.data.message_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
