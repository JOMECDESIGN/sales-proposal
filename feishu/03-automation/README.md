# 第③ 层 · 自动化(官方 Python SDK)

> 目标:把方案产线接上飞书的**主动能力**——状态变更**机器人卡片通知**、销售管道**多维表格看板**。脚本化、可进 CI、可被 Agent 调用。
>
> 上游:[larksuite/oapi-sdk-python](https://github.com/larksuite/oapi-sdk-python)(官方,⭐525),包名 `lark-oapi`。

## 装环境

```bash
cd feishu/03-automation
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env     # 然后填凭证
source ../.env
```

## 两个脚本

| 脚本 | 干什么 | 给谁用 |
|---|---|---|
| [`notify.py`](notify.py) | 方案状态 → 群里一张**消息卡片**(配色分 🟢🟡🔴) | 🏋️ Coach 自检完、🐑 Shepherd 到节点 |
| [`pipeline_base.py`](pipeline_base.py) | 销售管道 → **多维表格**看板增删改查 | 🐑 Shepherd、🗺️ Account Strategist |
| [`lark_client.py`](lark_client.py) | 共享鉴权(其它脚本 import 它) | — |

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

## 最小权限集

- `notify.py`:`im:message`(发消息)。机器人需**先被拉进目标群**。
- `pipeline_base.py`:`bitable:app`(读写多维表格)。应用需对该表格有协作者权限。

## 给 Agent 当工具

这两个脚本是确定性的命令行,Agent(尤其 🐑 Shepherd)可在产线收尾时直接调用:

> "方案定稿了。用 `feishu/03-automation/pipeline_base.py set-stage` 把本单推进到『答辩自检』,再用 `notify.py` 发张绿色卡片到群里汇报,附上云文档链接。"

> 与第①层 MCP 的取舍:**临时、一次性**操作走 MCP 对话即可;**固定动作、要可复现/进 CI** 的(每日同步、状态播报)用这层脚本。
