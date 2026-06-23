"""销售管道 -> 飞书多维表格(Bitable)看板:新增 / 更新一条机会记录。

用法:
  # 新增
  python pipeline_base.py add --name "XX项目" --customer "XX公司" \
        --stage 答辩中 --owner 张三 --amount 120 --close-date 2026-07-31
  # 更新(按 record_id)
  python pipeline_base.py update --record-id recXXXX --stage 已提交

字段定义见 fields.example.json;请先在飞书手建表并把字段名对齐。
前置:应用开通 bitable:app,且对该多维表格有写权限。
"""
from __future__ import annotations
import argparse

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import (
    AppTableRecord,
    CreateAppTableRecordRequest,
    UpdateAppTableRecordRequest,
)

from lark_client import get_client, env


def build_fields(args) -> dict:
    """命令行参数 -> Bitable 字段字典(空值不写,便于增量更新)。"""
    f = {}
    if args.name:        f["方案名称"] = args.name
    if args.customer:    f["客户"] = args.customer
    if args.stage:       f["阶段"] = args.stage
    if args.owner:       f["负责人"] = args.owner
    if args.amount is not None: f["预计金额(万)"] = float(args.amount)
    if args.close_date:  f["预计签约日"] = args.close_date
    if args.link:        f["方案链接"] = {"text": "打开", "link": args.link}
    if args.note:        f["备注"] = args.note
    return f


def main() -> None:
    ap = argparse.ArgumentParser(description="销售管道多维表格看板")
    ap.add_argument("op", choices=["add", "update"])
    ap.add_argument("--record-id", default="", help="update 时必填")
    ap.add_argument("--name"); ap.add_argument("--customer")
    ap.add_argument("--stage"); ap.add_argument("--owner")
    ap.add_argument("--amount", type=float)
    ap.add_argument("--close-date"); ap.add_argument("--link"); ap.add_argument("--note")
    ap.add_argument("--app-token", default=""); ap.add_argument("--table-id", default="")
    args = ap.parse_args()

    app_token = args.app_token or env("FEISHU_PIPELINE_APP_TOKEN")
    table_id = args.table_id or env("FEISHU_PIPELINE_TABLE_ID")
    client = get_client()
    fields = build_fields(args)

    if args.op == "add":
        req = (
            CreateAppTableRecordRequest.builder()
            .app_token(app_token).table_id(table_id)
            .request_body(AppTableRecord.builder().fields(fields).build())
            .build()
        )
        resp = client.bitable.v1.app_table_record.create(req)
    else:
        if not args.record_id:
            raise SystemExit("update 需要 --record-id")
        req = (
            UpdateAppTableRecordRequest.builder()
            .app_token(app_token).table_id(table_id).record_id(args.record_id)
            .request_body(AppTableRecord.builder().fields(fields).build())
            .build()
        )
        resp = client.bitable.v1.app_table_record.update(req)

    if not resp.success():
        raise SystemExit(f"写入失败 code={resp.code} msg={resp.msg} log_id={resp.get_log_id()}")
    rec_id = resp.data.record.record_id if resp.data and resp.data.record else "?"
    print(f"{args.op} 成功:record_id={rec_id}")


if __name__ == "__main__":
    main()
