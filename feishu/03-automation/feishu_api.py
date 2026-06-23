"""飞书 OpenAPI 直连小工具(纯 urllib,无第三方依赖)。

为什么不用官方 SDK:在 Claude Code 网页版里,SDK/MCP 走的出口代理会拦飞书域名;
而直连 urllib(Bash 路径)实测可达。本模块给同目录的 init_pipeline / grant_access /
list_chats / wiki_publish 等脚本共用。

凭证:FEISHU_APP_ID/SECRET 或 LARK_APP_ID/SECRET(任一组);也会自动加载 feishu/.env。
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path


def _load_env() -> None:
    """轻量加载 feishu/.env(无 python-dotenv 依赖;不覆盖已有进程变量)。"""
    p = Path(__file__).resolve().parents[1] / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_env()


def host(domain: str | None = None) -> str:
    d = (domain or os.getenv("FEISHU_DOMAIN", "cn")).lower()
    return "https://open.larksuite.com" if d in ("intl", "lark", "global") else "https://open.feishu.cn"


def creds() -> tuple[str, str]:
    aid = os.getenv("FEISHU_APP_ID") or os.getenv("LARK_APP_ID")
    sec = os.getenv("FEISHU_APP_SECRET") or os.getenv("LARK_APP_SECRET")
    if not aid or not sec:
        raise SystemExit("✗ 缺少凭证:请设置 FEISHU_APP_ID/SECRET 或 LARK_APP_ID/SECRET(或写入 feishu/.env)")
    return aid, sec


def req(method: str, url: str, token: str | None = None, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=30) as x:
            raw = x.read().decode()
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
    except urllib.error.URLError as e:
        return {"code": -1, "msg": f"network error: {e.reason}"}
    raw = raw.strip()
    if not raw:
        return {"code": -1, "msg": "empty response"}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"code": -1, "msg": f"non-JSON response: {raw[:160]}"}


def token() -> str:
    aid, sec = creds()
    r = req("POST", f"{host()}/open-apis/auth/v3/tenant_access_token/internal",
            body={"app_id": aid, "app_secret": sec})
    if r.get("code") not in (0, None) or not r.get("tenant_access_token"):
        raise SystemExit(f"✗ 取 tenant_access_token 失败:code={r.get('code')} msg={r.get('msg')}")
    return r["tenant_access_token"]


def check(resp: dict, step: str) -> dict:
    if resp.get("code") not in (0, None):
        raise SystemExit(f"✗ {step} 失败:code={resp.get('code')} msg={resp.get('msg')}")
    return resp
