"""飞书官方 SDK(lark-oapi)客户端工厂 —— 三层自动化共用。

凭证读取顺序:进程环境变量 > feishu/.env(经 python-dotenv 载入)。
仅用应用态(tenant_access_token);操作个人资源时请改用用户态或 ① 层 MCP。
"""
from __future__ import annotations
import os

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:  # 未装 python-dotenv 时退化为只读进程环境变量
    pass

import lark_oapi as lark


def get_client() -> "lark.Client":
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    if not app_id or not app_secret:
        raise SystemExit("缺少 FEISHU_APP_ID / FEISHU_APP_SECRET,请先 cp feishu/.env.example feishu/.env 并填写。")
    builder = lark.Client.builder().app_id(app_id).app_secret(app_secret)
    domain = os.environ.get("FEISHU_DOMAIN", "https://open.feishu.cn")
    builder = builder.domain(lark.LARK_DOMAIN if "larksuite" in domain else lark.FEISHU_DOMAIN)
    return builder.log_level(lark.LogLevel.INFO).build()


def env(name: str, required: bool = True) -> str:
    val = os.environ.get(name, "")
    if required and not val:
        raise SystemExit(f"缺少环境变量 {name}(见 feishu/.env.example)。")
    return val
