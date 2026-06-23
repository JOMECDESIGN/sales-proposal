"""从飞书Wiki/文档直接获取内容的脚本。

使用 urllib 直连飞书 OpenAPI，绕过网页版代理限制。

用法:
    python feishu/03-automation/fetch_wiki_content.py <wiki_node_token_or_url>

示例:
    python feishu/03-automation/fetch_wiki_content.py MUQywWtn8iXbYMkCTFlcyEXQnpf
    python feishu/03-automation/fetch_wiki_content.py https://wu35s592xy.feishu.cn/wiki/MUQywWtn8iXbYMkCTFlcyEXQnpf
"""
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
    """轻量加载 feishu/.env。"""
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


def parse_token(s: str) -> str:
    """从 URL 或直接 token 中提取 token。"""
    m = re.search(r"/wiki/([A-Za-z0-9]+)", s)
    return m.group(1) if m else s.strip()


def get_node_info(t: str, node_token: str) -> dict:
    """获取节点信息。尝试不同的 obj_type。"""
    for obj_type in ["wiki", "docx", "doc"]:
        q = urllib.parse.urlencode({"token": node_token, "obj_type": obj_type})
        r = req("GET", f"{host()}/open-apis/wiki/v2/spaces/get_node?{q}", t)
        if r.get("code") in (0, None):
            return r.get("data", {}).get("node", {})

    # 如果都失败，返回最后一个错误
    raise SystemExit(f"✗ 获取节点信息失败:code={r.get('code')} msg={r.get('msg')}")


def get_doc_content(t: str, doc_token: str) -> str:
    """获取文档的原始文本内容。"""
    # 先尝试 docx raw content
    r = req("GET", f"{host()}/open-apis/docx/v1/documents/{doc_token}/raw_content", t)
    if r.get("code") not in (0, None):
        raise SystemExit(f"✗ 获取文档内容失败:code={r.get('code')} msg={r.get('msg')}")
    return r.get("data", {}).get("content", "")


def get_wiki_content(node_token: str) -> None:
    """主流程:获取并打印 wiki 节点的内容。"""
    print(f"· 目标节点 token:{node_token}")

    t = token()
    print("✓ 已取 tenant_access_token")

    node = get_node_info(t, node_token)
    title = node.get("title", "(无标题)")
    node_type = node.get("obj_type", "unknown")
    print(f"✓ 节点信息:《{title}》({node_type})")

    # 获取实际的文档 token(wiki 节点可能需要转换)
    doc_token = node.get("child_token") or node_token

    content = get_doc_content(t, doc_token)
    print("\n" + "=" * 60)
    print(f"【{title}】")
    print("=" * 60)
    print(content)
    print("=" * 60)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    node_token = parse_token(sys.argv[1])
    try:
        get_wiki_content(node_token)
        return 0
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ 出错:{type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
