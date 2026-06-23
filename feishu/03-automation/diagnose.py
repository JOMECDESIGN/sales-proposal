"""诊断飞书环境和权限。"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from pathlib import Path


def _load_env() -> None:
    p = Path(__file__).resolve().parents[1] / ".env"
    if not p.exists():
        print("⚠ 未找到 feishu/.env")
        return
    print("✓ 加载 feishu/.env")
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_env()

HOST = "https://open.feishu.cn"


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
    try:
        return json.loads(raw)
    except:
        return {"code": -1, "msg": f"non-JSON: {raw[:100]}"}


print("\n=== 环境诊断 ===")

aid = os.getenv("FEISHU_APP_ID") or os.getenv("LARK_APP_ID")
sec = os.getenv("FEISHU_APP_SECRET") or os.getenv("LARK_APP_SECRET")

if not aid or not sec:
    print("✗ 缺少凭证")
else:
    print(f"✓ App ID: {aid[:8]}...")
    print(f"✓ App Secret: {sec[:8]}...")

print("\n=== 获取 Token ===")
r = req("POST", f"{HOST}/open-apis/auth/v3/tenant_access_token/internal",
        body={"app_id": aid, "app_secret": sec})

if r.get("code") not in (0, None):
    print(f"✗ 获取 token 失败: {r}")
else:
    t = r["tenant_access_token"]
    print(f"✓ Token: {t[:20]}...")

    print("\n=== 检查应用权限 ===")
    r2 = req("GET", f"{HOST}/open-apis/auth/v3/tenant_access_token/internal?app_id={aid}", t)
    print(f"  {r2}")

    print("\n=== 尝试列出我的文档(云空间根目录) ===")
    r3 = req("GET", f"{HOST}/open-apis/drive/explorer/v2/root_folder/meta", t)
    if r3.get("code") in (0, None):
        print(f"✓ 根目录 token: {r3['data'].get('token')}")
    else:
        print(f"✗ 失败: {r3}")

    print("\n=== 尝试查询指定节点 MUQywWtn8iXbYMkCTFlcyEXQnpf ===")
    for obj_type in ["wiki", "docx", "doc"]:
        r4 = req("GET", f"{HOST}/open-apis/wiki/v2/spaces/get_node?token=MUQywWtn8iXbYMkCTFlcyEXQnpf&obj_type={obj_type}", t)
        print(f"  obj_type={obj_type}: code={r4.get('code')} msg={r4.get('msg')}")
