"""销售管道 → 飞书多维表格(Bitable)看板。

把每单的推进状态沉到多维表格,销售/管理层在飞书里看实时看板,
而不是在散落的 Markdown 里翻。配合 🐑 Project Shepherd 与 🗺️ Account Strategist 使用。

表结构见 fields.example.json。用法:
    source ../.env
    python pipeline_base.py add --project "示例项目" --customer "XX 集团" \\
        --stage "赢主题" --owner 张三 --amount 120 --next "下周技术答辩"
    python pipeline_base.py list
    python pipeline_base.py set-stage --record recXXXX --stage "答辩自检"

app_token / table_id 默认取 .env 的 FEISHU_PIPELINE_APP_TOKEN / FEISHU_PIPELINE_TABLE_ID。
"""
from __future__ import annotations

import argparse
import sys

from lark_oapi.api.bitable.v1 import (
    AppTableRecord,
    CreateAppTableRecordRequest,
    ListAppTableRecordRequest,
    UpdateAppTableRecordRequest,
)

from lark_client import build_client, env

# 五段流程(与 curriculum/04-流程篇 对齐),作为"阶段"字段的取值约定
STAGES = ["挖需求", "赢主题", "技术主体", "交付计划", "答辩自检"]


def _ctx(args):
    app_token = args.app_token or env("FEISHU_PIPELINE_APP_TOKEN", required=True)
    table_id = args.table_id or env("FEISHU_PIPELINE_TABLE_ID", required=True)
    return build_client(), app_token, table_id


def cmd_add(args) -> int:
    client, app_token, table_id = _ctx(args)
    fields: dict[str, object] = {
        "项目": args.project,
        "客户": args.customer,
        "阶段": args.stage,
        "负责人": args.owner,
    }
    if args.amount is not None:
        fields["金额(万)"] = args.amount
    if args.next:
        fields["下一步"] = args.next

    request = (
        CreateAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .request_body(AppTableRecord.builder().fields(fields).build())
        .build()
    )
    resp = client.bitable.v1.app_table_record.create(request)
    if not resp.success():
        print(f"✗ 新增失败 code={resp.code} msg={resp.msg}", file=sys.stderr)
        return 1
    print(f"✓ 已新增:{args.project} / {args.customer} → record_id={resp.data.record.record_id}")
    return 0


def cmd_list(args) -> int:
    client, app_token, table_id = _ctx(args)
    request = (
        ListAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .page_size(100)
        .build()
    )
    resp = client.bitable.v1.app_table_record.list(request)
    if not resp.success():
        print(f"✗ 查询失败 code={resp.code} msg={resp.msg}", file=sys.stderr)
        return 1
    items = resp.data.items or []
    if not items:
        print("(空表)")
        return 0
    print(f"{'RECORD_ID':<20} {'阶段':<10} {'项目':<16} {'客户':<14} 负责人")
    for it in items:
        f = it.fields or {}
        print(f"{it.record_id:<20} {str(f.get('阶段','')):<10} "
              f"{str(f.get('项目','')):<16} {str(f.get('客户','')):<14} {f.get('负责人','')}")
    return 0


def cmd_set_stage(args) -> int:
    client, app_token, table_id = _ctx(args)
    fields: dict[str, object] = {"阶段": args.stage}
    if args.next:
        fields["下一步"] = args.next
    request = (
        UpdateAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .record_id(args.record)
        .request_body(AppTableRecord.builder().fields(fields).build())
        .build()
    )
    resp = client.bitable.v1.app_table_record.update(request)
    if not resp.success():
        print(f"✗ 更新失败 code={resp.code} msg={resp.msg}", file=sys.stderr)
        return 1
    print(f"✓ {args.record} 阶段 → {args.stage}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="销售管道多维表格看板")
    p.add_argument("--app-token", default="", help="覆盖 .env 的 app_token")
    p.add_argument("--table-id", default="", help="覆盖 .env 的 table_id")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="新增一单")
    a.add_argument("--project", required=True)
    a.add_argument("--customer", required=True)
    a.add_argument("--stage", default="挖需求", choices=STAGES)
    a.add_argument("--owner", default="")
    a.add_argument("--amount", type=float, default=None, help="金额(万元)")
    a.add_argument("--next", default="", help="下一步动作")
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list", help="列出全部单")
    l.set_defaults(func=cmd_list)

    s = sub.add_parser("set-stage", help="推进某单到新阶段")
    s.add_argument("--record", required=True, help="record_id(用 list 查)")
    s.add_argument("--stage", required=True, choices=STAGES)
    s.add_argument("--next", default="")
    s.set_defaults(func=cmd_set_stage)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
