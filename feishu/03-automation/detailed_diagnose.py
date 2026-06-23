"""详细诊断飞书权限和可访问资源。"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
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
        return {"code": -1, "msg": f"non-JSON response"}


aid = os.getenv("FEISHU_APP_ID") or os.getenv("LARK_APP_ID")
sec = os.getenv("FEISHU_APP_SECRET") or os.getenv("LARK_APP_SECRET")

print(f"App ID: {aid}")

r = req("POST", f"{HOST}/open-apis/auth/v3/tenant_access_token/internal",
        body={"app_id": aid, "app_secret": sec})
t = r["tenant_access_token"]

print("\n=== 尝试列出所有知识库(wiki spaces) ===")
# 尝试列出知识库
r1 = req("GET", f"{HOST}/open-apis/wiki/v1/spaces", t)
print(f"列出知识库: code={r1.get('code')} msg={r1.get('msg')}")
if r1.get("code") in (0, None):
    spaces = r1.get("data", {}).get("items", [])
    print(f"  找到 {len(spaces)} 个知识库:")
    for space in spaces:
        print(f"    - {space.get('name')} (space_id={space.get('space_id')})")

print("\n=== 直接尝试多种方式访问 MUQywWtn8iXbYMkCTFlcyEXQnpf ===")

# 方式1: 获取节点信息
print("\n1. 获取节点信息(wiki type):")
r2 = req("GET", f"{HOST}/open-apis/wiki/v2/spaces/get_node?token=MUQywWtn8iXbYMkCTFlcyEXQnpf&obj_type=wiki", t)
print(f"   code={r2.get('code')} msg={r2.get('msg')}")
if r2.get("code") in (0, None):
    node = r2.get("data", {}).get("node", {})
    print(f"   节点信息: {json.dumps(node, ensure_ascii=False, indent=2)}")

# 方式2: 尝试docx type
print("\n2. 获取节点信息(docx type):")
r3 = req("GET", f"{HOST}/open-apis/wiki/v2/spaces/get_node?token=MUQywWtn8iXbYMkCTFlcyEXQnpf&obj_type=docx", t)
print(f"   code={r3.get('code')} msg={r3.get('msg')}")

# 方式3: 尝试获取文档内容
print("\n3. 获取文档内容(docx raw_content):")
r4 = req("GET", f"{HOST}/open-apis/docx/v1/documents/MUQywWtn8iXbYMkCTFlcyEXQnpf/raw_content", t)
print(f"   code={r4.get('code')} msg={r4.get('msg')}")
if r4.get("code") in (0, None):
    content = r4.get("data", {}).get("content", "")
    print(f"   内容长度: {len(content)} 字符")
    if len(content) < 500:
        print(f"   内容: {content}")

# 方式4: 获取文档块内容
print("\n4. 获取文档块内容(blocks):")
r5 = req("GET", f"{HOST}/open-apis/docx/v1/documents/MUQywWtn8iXbYMkCTFlcyEXQnpf/blocks?page_size=100", t)
print(f"   code={r5.get('code')} msg={r5.get('msg')}")
if r5.get("code") in (0, None):
    blocks = r5.get("data", {}).get("items", [])
    print(f"   找到 {len(blocks)} 个文本块")

# 方式5: 搜索Wiki
print("\n5. 在Wiki中搜索(search):")
r6 = req("GET", f"{HOST}/open-apis/wiki/v1/nodes/search?query=MUQywWtn8iXbYMkCTFlcyEXQnpf", t)
print(f"   code={r6.get('code')} msg={r6.get('msg')}")
if r6.get("code") in (0, None):
    items = r6.get("data", {}).get("items", [])
    print(f"   搜索结果: {len(items)} 项")

# 方式6: 检查应用对象权限
print("\n6. 尝试查询该token的权限信息:")
r7 = req("POST", f"{HOST}/open-apis/drive/v1/permissions/check", t,
         body={"token": "MUQywWtn8iXbYMkCTFlcyEXQnpf", "type": "doc"})
print(f"   code={r7.get('code')} msg={r7.get('msg')}")

print("\n=== 检查应用的云文档权限 ===")
r8 = req("GET", f"{HOST}/open-apis/drive/explorer/v2/root_folder/meta", t)
if r8.get("code") in (0, None):
    root = r8.get("data", {}).get("token")
    print(f"✓ 可以访问应用根目录: {root}")

    # 尝试列出根目录内容
    print("\n  根目录内容:")
    r9 = req("GET", f"{HOST}/open-apis/drive/explorer/v2/folder/{root}", t)
    if r9.get("code") in (0, None):
        items = r9.get("data", {}).get("children", [])
        print(f"  找到 {len(items)} 个项目:")
        for item in items[:10]:
            print(f"    - {item.get('name')} ({item.get('type')})")
