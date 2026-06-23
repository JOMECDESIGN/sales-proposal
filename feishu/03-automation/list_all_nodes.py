"""列出知识库中的所有节点，包括子节点。"""
from __future__ import annotations

import json
import os
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

import urllib.request
import urllib.error

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
        return {"code": -1, "msg": "non-JSON response"}


aid = os.getenv("FEISHU_APP_ID") or os.getenv("LARK_APP_ID")
sec = os.getenv("FEISHU_APP_SECRET") or os.getenv("LARK_APP_SECRET")

r = req("POST", f"{HOST}/open-apis/auth/v3/tenant_access_token/internal",
        body={"app_id": aid, "app_secret": sec})
t = r["tenant_access_token"]

target = "MUQywWtn8iXbYMkCTFlcyEXQnpf"

# 获取所有spaces
r_spaces = req("GET", f"{HOST}/open-apis/wiki/v2/spaces", t)
spaces = r_spaces.get("data", {}).get("items", []) if r_spaces.get("code") in (0, None) else []

print(f"找到 {len(spaces)} 个知识库\n")

for space in spaces:
    space_id = space.get("space_id")
    space_name = space.get("name")
    print(f"【{space_name}】(space_id={space_id})")

    # 列出该space的所有节点（分页）
    page_token = None
    all_nodes = []
    while True:
        params = {"page_size": 50}
        if page_token:
            params["page_token"] = page_token
        query = "&".join(f"{k}={v}" for k, v in params.items())
        r_nodes = req("GET", f"{HOST}/open-apis/wiki/v2/spaces/{space_id}/nodes?{query}", t)
        if r_nodes.get("code") not in (0, None):
            print(f"  ✗ 列出节点失败: {r_nodes.get('msg')}")
            break

        items = r_nodes.get("data", {}).get("items", [])
        all_nodes.extend(items)

        page_token = r_nodes.get("data", {}).get("page_token")
        if not page_token:
            break

    print(f"  共 {len(all_nodes)} 个节点:")
    for node in all_nodes:
        token_val = node.get("node_token")
        title = node.get("title", "(无标题)")
        indent = "    " if node.get("has_child") else "    "
        marker = "📁" if node.get("has_child") else "📄"

        print(f"{indent}{marker} {title}")
        print(f"{indent}  token={token_val}")

        # 检查是否匹配
        if token_val == target:
            print(f"{indent}  ✓✓✓ 找到目标! ✓✓✓")

        # 如果有子节点，递归列出
        if node.get("has_child"):
            child_nodes = []
            c_page_token = None
            while True:
                c_params = {"page_size": 50}
                if c_page_token:
                    c_params["page_token"] = c_page_token
                c_query = "&".join(f"{k}={v}" for k, v in c_params.items())
                r_child = req("GET", f"{HOST}/open-apis/wiki/v2/spaces/{space_id}/nodes/{token_val}/children?{c_query}", t)
                if r_child.get("code") not in (0, None):
                    break
                c_items = r_child.get("data", {}).get("items", [])
                child_nodes.extend(c_items)
                c_page_token = r_child.get("data", {}).get("page_token")
                if not c_page_token:
                    break

            for child in child_nodes:
                child_token = child.get("node_token")
                child_title = child.get("title", "(无标题)")
                c_marker = "📁" if child.get("has_child") else "📄"
                print(f"      {c_marker} {child_title}")
                print(f"        token={child_token}")
                if child_token == target:
                    print(f"        ✓✓✓ 找到目标! ✓✓✓")
    print()

print("\n=== 总结 ===")
print(f"目标token: {target}")
print("如果上面列出的节点中没有找到，说明该token属于其他知识库或用户私密文档。")
