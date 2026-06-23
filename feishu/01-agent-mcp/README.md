# ① Agent 层 · 飞书官方 OpenAPI MCP

让本仓库的 7 个 Agent 在 Claude Code 对话中**原生读写飞书**(云文档 / 多维表格 / 消息),无需写脚本即时落地。

## 接入

MCP 已配置在仓库根 [`.mcp.json`](../../.mcp.json),通过 `npx` 拉起官方包 `@larksuiteoapi/lark-mcp`:

```jsonc
{
  "mcpServers": {
    "lark": {
      "command": "npx",
      "args": ["-y", "@larksuiteoapi/lark-mcp", "mcp",
               "-a", "${FEISHU_APP_ID}", "-s", "${FEISHU_APP_SECRET}",
               "-d", "${FEISHU_DOMAIN:-https://open.feishu.cn}",
               "-t", "preset.doc.default,preset.base.default,preset.im.default"]
    }
  }
}
```

启动前需让 `FEISHU_APP_ID` / `FEISHU_APP_SECRET` 进入 Claude Code 的环境变量,最简单的方式:

```bash
set -a && source feishu/.env && set +a   # 导出 .env 后再启动 claude
```

`-t` 预设了 **doc / base(多维表格)/ im(消息)** 三组工具;需要日历、任务等可追加 `preset.calendar.default,preset.task.default`(完整列表见官方 README)。

## 应用态 vs 用户态

- **应用态(tenant_access_token,默认)**:用应用身份操作"应用自己的资源",免逐用户授权,适合机器人发消息、写应用拥有的多维表格。
- **用户态(user_access_token)**:读写"某个人的"云文档 / 个人空间时需要,启用 OAuth:
  ```bash
  npx @larksuiteoapi/lark-mcp login -a <app_id> -s <app_secret>   # 浏览器授权,token 本地安全存储
  ```
  并在 args 增加 `--oauth --token-mode user_access_token`。

## 最小权限集(按需在开放平台开通,改完务必发版本)

| 用途 | 典型 scope |
|---|---|
| 读写云文档 | `docx:document`、`docs:document`(用户态读个人文档另需对应读权限) |
| 多维表格看板 | `bitable:app`(读写记录、字段) |
| 群消息播报 | `im:message`、`im:chat:readonly`(取 chat 列表) |
| 知识库 | `wiki:wiki`(移动 / 读取节点) |

> 原则:只开当前要用的 scope;越权 scope 会拖慢审批、增加风险面。

## 给 Agent 的提示词示例

> "用 lark MCP 把本次《XX 项目方案》执行摘要建成一篇飞书云文档,放进知识库 `售前方案` 空间,并在 `#售前播报` 群发一张包含标题、负责人、状态的卡片。"

> "读 `销售管道` 多维表格里所有"答辩中"的记录,汇总成一张对比表返回给我。"

各 Agent 与飞书能力的对照、嵌入五段流程的用法,见 [`curriculum/05-飞书打通-使用手册.md`](../../curriculum/05-飞书打通-使用手册.md)。
