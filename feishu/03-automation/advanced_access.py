"""高级访问尝试：多种方式获取飞书文档内容。"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path


def _load_env() -> None:
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
        return {"code": -1, "msg": "non-JSON response", "raw": raw[:200]}


def token() -> str:
    aid = os.getenv("FEISHU_APP_ID") or os.getenv("LARK_APP_ID")
    sec = os.getenv("FEISHU_APP_SECRET") or os.getenv("LARK_APP_SECRET")
    if not aid or not sec:
        raise SystemExit("✗ 缺少凭证")
    r = req("POST", f"{HOST}/open-apis/auth/v3/tenant_access_token/internal",
            body={"app_id": aid, "app_secret": sec})
    if r.get("code") not in (0, None):
        raise SystemExit(f"✗ 获取token失败: {r}")
    return r["tenant_access_token"]


doc_token = "MUQywWtn8iXbYMkCTFlcyEXQnpf"
t = token()

print("=== 方案A: 尝试列出所有可访问的文档 ===")
r1 = req("GET", f"{HOST}/open-apis/drive/v1/files?page_size=50", t)
print(f"code={r1.get('code')} msg={r1.get('msg')}")
if r1.get("code") in (0, None):
    files = r1.get("data", {}).get("files", [])
    print(f"找到 {len(files)} 个文件")
    for f in files[:5]:
        print(f"  - {f.get('name')} ({f.get('type')})")
        if doc_token in f.get('name', ''):
            print(f"    ✓ 匹配!")

print("\n=== 方案B: 尝试访问知识库节点列表 ===")
# 先找space_id
r2 = req("GET", f"{HOST}/open-apis/wiki/v2/spaces", t)
print(f"列出spaces: code={r2.get('code')}")
if r2.get("code") in (0, None):
    spaces = r2.get("data", {}).get("items", [])
    print(f"找到 {len(spaces)} 个知识库")
    for space in spaces:
        print(f"  - {space.get('name')}")
        # 尝试在这个space里找节点
        space_id = space.get("space_id")
        r3 = req("GET", f"{HOST}/open-apis/wiki/v2/spaces/{space_id}/nodes", t)
        if r3.get("code") in (0, None):
            nodes = r3.get("data", {}).get("items", [])
            print(f"    {len(nodes)} 个节点")
            for node in nodes[:3]:
                print(f"      - {node.get('title')} (token={node.get('node_token')})")
                if doc_token in node.get('node_token', ''):
                    print(f"        ✓✓✓ 找到目标节点!")

print("\n=== 方案C: 尝试grant权限(申请访问) ===")
# 尝试为应用授权这个文档
r4 = req("POST", f"{HOST}/open-apis/drive/v1/permissions/member/create", t,
         body={
             "token": doc_token,
             "type": "doc",
             "member": {
                 "member_type": "app",
                 "app_id": os.getenv("FEISHU_APP_ID") or os.getenv("LARK_APP_ID"),
             },
             "perm": "view",
             "notify": False,
         })
print(f"授权: code={r4.get('code')} msg={r4.get('msg')}")

print("\n=== 方案D: 尝试get_node用tenant token再试一次 ===")
r5 = req("GET", f"{HOST}/open-apis/wiki/v2/spaces/get_node?token={doc_token}&obj_type=wiki", t)
print(f"wiki: code={r5.get('code')} msg={r5.get('msg')}")
if r5.get("code") in (0, None):
    print(f"✓ 节点信息:")
    node = r5.get("data", {}).get("node", {})
    print(f"  标题: {node.get('title')}")
    print(f"  类型: {node.get('obj_type')}")
    print(f"  space_id: {node.get('space_id')}")
    child_token = node.get("child_token")
    if child_token:
        print(f"  child_token: {child_token}")
        # 尝试用child_token获取内容
        r6 = req("GET", f"{HOST}/open-apis/docx/v1/documents/{child_token}/raw_content", t)
        print(f"\n  获取child_token内容: code={r6.get('code')}")
        if r6.get("code") in (0, None):
            content = r6.get("data", {}).get("content", "")
            print(f"  内容({len(content)}字符):\n{content[:500]}")

print("\n=== 方案E: 尝试搜索文档内容 ===")
r7 = req("POST", f"{HOST}/open-apis/docx/v1/search", t,
         body={
             "query": "深度解读",
             "limit": 5,
         })
print(f"搜索: code={r7.get('code')} msg={r7.get('msg')}")
