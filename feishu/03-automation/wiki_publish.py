"""把一份 Markdown 直接发布为飞书知识库(wiki)某节点下的子文档。

填补能力空白:lark-mcp / feishu-cli 都没有「把文档移动到指定 wiki 节点」的现成命令,
本脚本直接走 OpenAPI 四步链路实现:
  1) 取 tenant_access_token
  2) get_node 解析父节点 → space_id
  3) 导入 Markdown → 临时 docx(medias/upload_all → import_tasks → 轮询)
  4) move_docs_to_wiki(parent_wiki_token=父节点)→ 返回新节点链接

凭证从环境变量读取(任一组):FEISHU_APP_ID/SECRET 或 LARK_APP_ID/SECRET。

用法:
    python wiki_publish.py --md 文件.md --node <wiki节点token或URL> [--title 标题] [--domain cn|intl]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request


def _host(domain: str) -> str:
    return "https://open.larksuite.com" if domain.lower() in ("intl", "lark", "global") else "https://open.feishu.cn"


def _creds() -> tuple[str, str]:
    app_id = os.getenv("FEISHU_APP_ID") or os.getenv("LARK_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET") or os.getenv("LARK_APP_SECRET")
    if not app_id or not app_secret:
        sys.exit("✗ 缺少凭证:请设置 FEISHU_APP_ID/SECRET 或 LARK_APP_ID/SECRET")
    return app_id, app_secret


def _req(method: str, url: str, token: str | None = None, body: dict | None = None,
         raw: bytes | None = None, headers: dict | None = None) -> dict:
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    h = {"Content-Type": "application/json; charset=utf-8"}
    if headers:
        h = headers
    if token:
        h["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode() or "{}")


def _check(resp: dict, step: str) -> dict:
    if resp.get("code") not in (0, None):
        sys.exit(f"✗ {step} 失败:code={resp.get('code')} msg={resp.get('msg')}")
    return resp


def get_token(host: str, app_id: str, app_secret: str) -> str:
    resp = _req("POST", f"{host}/open-apis/auth/v3/tenant_access_token/internal",
                body={"app_id": app_id, "app_secret": app_secret})
    _check(resp, "获取 tenant_access_token")
    return resp["tenant_access_token"]


def parse_node_token(s: str) -> str:
    m = re.search(r"/wiki/([A-Za-z0-9]+)", s)
    return m.group(1) if m else s.strip()


def get_node(host: str, token: str, node_token: str, obj_type: str = "wiki") -> dict:
    q = urllib.parse.urlencode({"token": node_token, "obj_type": obj_type})
    resp = _req("GET", f"{host}/open-apis/wiki/v2/spaces/get_node?{q}", token)
    _check(resp, "get_node 查询节点")
    return resp["data"]["node"]


def delete_folder(host: str, token: str, folder_token: str) -> None:
    _req("DELETE", f"{host}/open-apis/drive/v1/files/{folder_token}?type=folder", token)


def root_folder(host: str, token: str) -> str:
    resp = _req("GET", f"{host}/open-apis/drive/explorer/v2/root_folder/meta", token)
    _check(resp, "取应用根目录")
    return resp["data"]["token"]


def make_temp_folder(host: str, token: str, parent: str) -> str:
    """在根目录下建临时子文件夹作为导入挂载点(根目录本身不允许 ccm_import 上传)。"""
    resp = _req("POST", f"{host}/open-apis/drive/v1/files/create_folder", token,
                body={"name": "_wiki_import_tmp", "folder_token": parent})
    _check(resp, "建临时导入文件夹")
    return resp["data"]["token"]


def upload_for_import(host: str, token: str, md_path: str, folder: str) -> str:
    """multipart/form-data 上传 md 源文件,返回 file_token。"""
    with open(md_path, "rb") as f:
        content = f.read()
    fname = os.path.basename(md_path)
    boundary = "----feishuwikipublish7f3a2b"
    fields = {
        "file_name": fname,
        "parent_type": "ccm_import_open",
        "parent_node": folder,
        "size": str(len(content)),
        # ccm_import_open 通道必须带 extra,否则报 1061004 forbidden
        "extra": json.dumps({"obj_type": "docx", "file_extension": "md"}),
    }
    parts = []
    for k, v in fields.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fname}\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n".encode()
        + content + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    payload = b"".join(parts)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    resp = _req("POST", f"{host}/open-apis/drive/v1/medias/upload_all",
                raw=payload, headers=headers)
    _check(resp, "上传 Markdown 源文件")
    return resp["data"]["file_token"]


def import_to_docx(host: str, token: str, file_token: str, title: str, folder: str) -> dict:
    body = {
        "file_extension": "md",
        "file_token": file_token,
        "type": "docx",
        "file_name": title,
        "point": {"mount_type": 1, "mount_key": folder},
    }
    resp = _req("POST", f"{host}/open-apis/drive/v1/import_tasks", token, body=body)
    _check(resp, "创建导入任务")
    ticket = resp["data"]["ticket"]
    for _ in range(30):
        time.sleep(2)
        r = _req("GET", f"{host}/open-apis/drive/v1/import_tasks/{ticket}", token)
        _check(r, "轮询导入任务")
        result = r["data"]["result"]
        status = result.get("job_status")
        if status == 0:
            return result          # 成功:含 token(docx token)、url
        if status not in (1, 2):   # 1/2 = 处理中
            sys.exit(f"✗ 导入失败:job_status={status} msg={result.get('job_error_msg')}")
    sys.exit("✗ 导入超时")


def move_to_wiki(host: str, token: str, space_id: str, parent_node: str, obj_token: str) -> dict:
    url = f"{host}/open-apis/wiki/v2/spaces/{space_id}/nodes/move_docs_to_wiki"
    body = {"parent_wiki_token": parent_node, "obj_type": "docx", "obj_token": obj_token, "apply": True}
    resp = _req("POST", url, token, body=body)
    _check(resp, "move_docs_to_wiki")
    return resp["data"]


def main() -> int:
    p = argparse.ArgumentParser(description="把 Markdown 发布到飞书知识库指定节点下")
    p.add_argument("--md", required=True, help="Markdown 文件路径")
    p.add_argument("--node", required=True, help="目标父节点:wiki 节点 token 或完整 URL")
    p.add_argument("--title", default="", help="文档标题(默认取文件名)")
    p.add_argument("--domain", default=os.getenv("FEISHU_DOMAIN", "cn"), help="cn(默认)或 intl")
    args = p.parse_args()

    if not os.path.isfile(args.md):
        sys.exit(f"✗ 文件不存在:{args.md}")
    title = args.title or os.path.splitext(os.path.basename(args.md))[0]
    host = _host(args.domain)
    app_id, app_secret = _creds()
    parent = parse_node_token(args.node)

    print(f"· 目标父节点 token:{parent}")
    token = get_token(host, app_id, app_secret)
    print("· 已取 tenant_access_token")

    node = get_node(host, token, parent)
    space_id = node["space_id"]
    print(f"· 父节点所属知识库 space_id:{space_id}(《{node.get('title','')}》)")

    folder = make_temp_folder(host, token, root_folder(host, token))
    print(f"· 临时导入文件夹:{folder}")
    file_token = upload_for_import(host, token, args.md, folder)
    print(f"· 源文件已上传 file_token:{file_token}")

    result = import_to_docx(host, token, file_token, title, folder)
    docx_token = result["token"]
    print(f"· 已导入为 docx:{docx_token}")

    move_to_wiki(host, token, space_id, parent, docx_token)
    # 反查该 docx 在知识库里的节点,拿到稳定的节点 token
    new_node = get_node(host, token, docx_token, obj_type="docx")
    wiki_token = new_node.get("node_token")
    delete_folder(host, token, folder)  # 清理临时导入文件夹(best-effort)

    base = re.match(r"https?://[^/]+", args.node)
    link = f"{base.group(0)}/wiki/{wiki_token}" if (base and wiki_token) else f"(已入库,节点 token={wiki_token})"
    print("✓ 已发布到知识库:")
    print(f"  父节点:{parent}")
    print(f"  新节点:{link}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
