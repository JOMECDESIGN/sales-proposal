"""共享:构造官方飞书客户端 + 读取 feishu/.env。

其它脚本统一 `from lark_client import build_client, env` 使用,避免到处重复鉴权。
官方 SDK:larksuite/oapi-sdk-python(包名 lark_oapi)。
"""
from __future__ import annotations

import os
from pathlib import Path

import lark_oapi as lark
from dotenv import load_dotenv

# feishu/.env(本目录的上一级),不存在也不报错——允许直接用进程环境变量
_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_ENV_PATH)


def env(key: str, default: str | None = None, *, required: bool = False) -> str:
    """读环境变量;required=True 时缺失即报错,提示去 .env 配。"""
    val = os.getenv(key, default)
    if required and not val:
        raise SystemExit(
            f"✗ 缺少环境变量 {key}。请在 feishu/.env 配置(参考 feishu/.env.example)。"
        )
    return val  # type: ignore[return-value]


def build_client() -> lark.Client:
    """用 App ID/Secret 构造应用态(tenant_access_token)客户端。

    凭证兼容两组命名:FEISHU_APP_ID/SECRET(本仓库约定)与
    LARK_APP_ID/SECRET(Claude Code 网页版环境的默认注入),任一组即可。
    """
    app_id = os.getenv("FEISHU_APP_ID") or os.getenv("LARK_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET") or os.getenv("LARK_APP_SECRET")
    if not app_id or not app_secret:
        raise SystemExit(
            "✗ 缺少应用凭证:请设置 FEISHU_APP_ID/SECRET 或 LARK_APP_ID/SECRET"
            "(参考 feishu/.env.example)。"
        )

    builder = (
        lark.Client.builder()
        .app_id(app_id)
        .app_secret(app_secret)
        .log_level(lark.LogLevel.INFO)
    )
    # 国际版 Lark
    if env("FEISHU_DOMAIN", "cn").lower() in ("intl", "lark", "global"):
        builder = builder.domain(lark.LARK)
    return builder.build()
