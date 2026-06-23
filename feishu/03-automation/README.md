# 第③ 层 · 自动化(官方 Python SDK)

> 目标:把方案产线接上飞书的**主动能力**——状态变更**机器人卡片通知**、销售管道**多维表格看板**。脚本化、可进 CI、可被 Agent 调用。
>
> 上游:[larksuite/oapi-sdk-python](https://github.com/larksuite/oapi-sdk-python)(官方,⭐525),包名 `lark-oapi`。
>
> **选 Python 的理由**:与本仓库文档调性、新人上手成本最匹配。若团队想要**全 Go 一套**,可改用官方 [larksuite/cli](https://github.com/larksuite/cli)(⭐14.6k,200+ 命令)+ 社区 [chyroc/lark](https://github.com/chyroc/lark)(⭐472,全量 Open API)重写本层脚本,能力等价。

## 官方 SDK(纳入方式 = 锁版本依赖,不入库源码)

| 项 | 值 |
|---|---|
| 仓库 | [larksuite/oapi-sdk-python](https://github.com/larksuite/oapi-sdk-python)(官方) |
| 包名 / 版本 | `lark-oapi` == **1.6.8**(已钉在 `requirements.txt`) |
| 许可 | MIT |
| 默认域 | **中国版飞书 `open.feishu.cn`**(`.domain(lark.LARK)` 才切国际版) |
| 运行依赖 | httpx · requests · requests-toolbelt · pycryptodome · websockets(`pip install` 自动带上) |

**为什么只锁版本、不把源码复刻进仓**:该 SDK 是按 API spec **自动生成**的,源码树达 **104MB / 1.1 万文件 / 60 个服务模块**;直接入库会让仓库膨胀百倍、冻结版本、且无法连带它的 5 个三方依赖,得不偿失。锁版本依赖才能可复现 + 可 `pip` 升级。
- **升级**:改 `requirements.txt` 的版本号即可。
- **离线/内网**:`pip download lark-oapi==1.6.8 -d vendor/` 拿 7.8MB 的 wheel,部署端 `pip install --no-index --find-links vendor/ lark-oapi`。
- 本层脚本若遇网页版 SDK 网络抖动,可改走同目录 `feishu_api.py`(纯 urllib 直连,无需 SDK)。

## 装环境

```bash
cd feishu/03-automation
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env     # 然后填凭证
source ../.env
```

## 脚本清单

**业务脚本**

| 脚本 | 干什么 | 给谁用 |
|---|---|---|
| [`notify.py`](notify.py) | 方案状态 → 群里一张**消息卡片**(配色分 🟢🟡🔴) | 🏋️ Coach 自检完、🐑 Shepherd 到节点 |
| [`pipeline_base.py`](pipeline_base.py) | 销售管道 → **多维表格**看板增删改查 | 🐑 Shepherd、🗺️ Account Strategist |
| [`wiki_publish.py`](wiki_publish.py) | 把 Markdown **直接发布到知识库指定节点下**(导入→移动入库一步到位) | 🧭 PM · 🏹 Strategist |

**搭建/运维脚本(一次性或偶发)**

| 脚本 | 干什么 |
|---|---|
| [`init_pipeline.py`](init_pipeline.py) | 创建销售管道多维表格(字段照 fields.example.json),打印 app_token/table_id |
| [`grant_access.py`](grant_access.py) | 给群/用户开放某资源(多维表格/文档/wiki)的 view/edit 权限 |
| [`list_chats.py`](list_chats.py) | 列出机器人所在的群 + chat_id(配 notify 播报群时用) |

**共享模块**

| 文件 | 干什么 |
|---|---|
| [`feishu_api.py`](feishu_api.py) | 直连 OpenAPI 小工具(取 token / 请求 / 加载 .env),`init/grant/list` 共用;纯 urllib,网页版可用 |
| [`lark_client.py`](lark_client.py) | 官方 SDK 鉴权(notify/pipeline 用) |

> 另:[`../tools/gen_material_docx.py`](../tools/gen_material_docx.py) 生成《飞书深度打通-技术选型与实施材料》Word(依赖 `python-docx`)。

### 一次性搭建三连(配 .env 前)

```bash
python init_pipeline.py                  # 建管道表 → 拿 app_token/table_id 填进 .env
python list_chats.py --grep 群名关键字     # 找播报群 chat_id 填进 .env
python grant_access.py --token <app_token> --type bitable --chat <chat_id> --perm edit  # 给群授权
```

### notify.py —— 状态卡片

```bash
python notify.py --title "示例项目 · 执行摘要定稿" --stage "答辩自检" \
  --status green --owner 张三 \
  --note "Coach 自检 12 项过 11;CTA 已补具体下一步" \
  --link "https://xxx.feishu.cn/docx/xxxxx"
```
`--status` 取 `green|yellow|red`;`--chat` 省略时用 `.env` 的 `FEISHU_NOTIFY_CHAT_ID`。

### pipeline_base.py —— 管道看板

先在飞书手建一张多维表格,字段照 [`fields.example.json`](fields.example.json) 设置,把 `app_token`、`table_id` 填进 `.env`,然后:

```bash
python pipeline_base.py add --project "示例项目" --customer "XX 集团" \
  --stage "赢主题" --owner 张三 --amount 120 --next "下周技术答辩"
python pipeline_base.py list
python pipeline_base.py set-stage --record recXXXX --stage "答辩自检"
```
阶段取值与 [`curriculum/04-流程篇`](../../curriculum/04-流程篇-从挖需求到拿单.md) 的五段一一对齐。

### wiki_publish.py —— 直接发布到知识库指定节点

填补 lark-mcp / feishu-cli 都缺的「移动到指定 wiki 节点」能力,直接走 OpenAPI 四步链路:
取 token → `get_node` 解析父节点拿 space_id → 导入 Markdown 成 docx(`medias/upload_all` 带
`extra` → `import_tasks` 轮询)→ `move_docs_to_wiki`(带 `parent_wiki_token`)。

```bash
# 凭证用 FEISHU_APP_ID/SECRET 或 LARK_APP_ID/SECRET 均可
python wiki_publish.py \
  --md ../../飞书深度打通-技术选型与实施材料.md \
  --node "https://<租户>.feishu.cn/wiki/<父节点token>" \
  --title "文档标题"
# 输出:✓ 已发布到知识库 + 新节点链接
```

- `--node` 既收 wiki 节点 token,也收完整 URL(自动提取 token)。
- 幂等性:**每次运行都会新建一个子节点**(非更新)。需要更新已有节点内容请走第②层 feishu-cli `doc content-update <id> --mode overwrite --markdown ...`。
- 关键坑:`ccm_import_open` 上传通道必须带 `extra={"obj_type":"docx","file_extension":"md"}`,否则报 `1061004 forbidden`。

> **网络注记**:在 Claude Code 网页版环境里,飞书官方 MCP 走的代理会拦截飞书 API 域名
> (报 `Host resolves to a private/reserved IP`),但 **Bash 工具能直连** `open.feishu.cn`。
> 因此自动化层脚本(本文件)在网页版里可直接跑通,而 MCP 工具未必可用。

## 最小权限集

- `notify.py`:`im:message`(发消息)。机器人需**先被拉进目标群**。
- `pipeline_base.py`:`bitable:app`(读写多维表格)。应用需对该表格有协作者权限。
- `wiki_publish.py`:`drive:drive`(云盘读写,用于导入)+ `wiki:wiki`(知识库写)。应用需是目标知识库成员且有编辑权限。

## 给 Agent 当工具

这两个脚本是确定性的命令行,Agent(尤其 🐑 Shepherd)可在产线收尾时直接调用:

> "方案定稿了。用 `feishu/03-automation/pipeline_base.py set-stage` 把本单推进到『答辩自检』,再用 `notify.py` 发张绿色卡片到群里汇报,附上云文档链接。"

> 与第①层 MCP 的取舍:**临时、一次性**操作走 MCP 对话即可;**固定动作、要可复现/进 CI** 的(每日同步、状态播报)用这层脚本。
