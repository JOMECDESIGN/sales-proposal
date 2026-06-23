"""创建『销售管道』多维表格(字段照 fields.example.json),供 pipeline_base.py 读写。

一次性建表脚本。建好后把打印出的 app_token / table_id 填进 feishu/.env 的
FEISHU_PIPELINE_APP_TOKEN / FEISHU_PIPELINE_TABLE_ID。

用法:
    python init_pipeline.py [--name 售前销售管道看板] [--table 销售管道]
"""
from __future__ import annotations

import argparse

from feishu_api import check, host, req, token

STAGES = ["挖需求", "赢主题", "技术主体", "交付计划", "答辩自检"]


def main() -> int:
    p = argparse.ArgumentParser(description="创建销售管道多维表格")
    p.add_argument("--name", default="售前销售管道看板", help="多维表格(Base)名称")
    p.add_argument("--table", default="销售管道", help="数据表名称")
    args = p.parse_args()

    tok = token()
    h = host()

    app = req("POST", f"{h}/open-apis/bitable/v1/apps", tok, body={"name": args.name})
    check(app, "创建 Base")
    app_token = app["data"]["app"]["app_token"]

    table_body = {"table": {
        "name": args.table,
        "default_view_name": "管道总览",
        "fields": [
            {"field_name": "项目", "type": 1},
            {"field_name": "客户", "type": 1},
            {"field_name": "阶段", "type": 3,
             "property": {"options": [{"name": s} for s in STAGES]}},
            {"field_name": "负责人", "type": 1},
            {"field_name": "金额(万)", "type": 2},
            {"field_name": "下一步", "type": 1},
        ]}}
    tbl = req("POST", f"{h}/open-apis/bitable/v1/apps/{app_token}/tables", tok, body=table_body)
    check(tbl, "创建数据表")
    table_id = tbl["data"]["table_id"]

    print("✓ 销售管道多维表格已创建:")
    print(f"  FEISHU_PIPELINE_APP_TOKEN={app_token}")
    print(f"  FEISHU_PIPELINE_TABLE_ID={table_id}")
    print("  ⮑ 把上面两行填进 feishu/.env,pipeline_base.py 即可读写。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
