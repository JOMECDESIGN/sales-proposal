# 第① 层 · Agent 层(官方 lark-openapi-mcp)

> 目标:让本仓库的 **7 个 Agent 直接操作飞书**——读写云文档、增删多维表格记录、发消息——而不是只在本地生成 Markdown。这是"深度打通"里价值最高的一层。
>
> 上游:[larksuite/lark-openapi-mcp](https://github.com/larksuite/lark-openapi-mcp)(官方维护),npm 包 `@larksuiteoapi/lark-mcp`。

## 它怎么接进来

仓库根目录已内置 [`/.mcp.json`](../../.mcp.json),Claude Code 启动时会自动发现这个 MCP server。你只需要:

1. 安装 Node ≥ 18(`npx` 会按需拉起 `@larksuiteoapi/lark-mcp`,无需全局安装)。
2. 在 shell 里导出凭证(与 `feishu/.env` 同源):
   ```bash
   export FEISHU_APP_ID=cli_xxx
   export FEISHU_APP_SECRET=xxx
   ```
   `.mcp.json` 用 `${FEISHU_APP_ID}` / `${FEISHU_APP_SECRET}` 占位,Claude Code 会做环境变量展开。
3. 重启 Claude Code,在 `/mcp` 里确认 `lark` 已连接、批准其工具。

> 国际版 Lark:在 `.mcp.json` 的 args 里追加 `"--domain", "https://open.larksuite.com"`。

## 手动验证(不依赖 Claude Code)

```bash
# 前台跑一次,看是否正常握手
npx -y @larksuiteoapi/lark-mcp mcp -a "$FEISHU_APP_ID" -s "$FEISHU_APP_SECRET"
```

## 工具预设(`-t`)

`.mcp.json` 默认启用了贴合本产线的预设,避免一次性灌入上百个工具把上下文撑爆:

| 预设 | 给谁用 | 典型动作 |
|---|---|---|
| `preset.doc.default` | 🏹 Strategist · 📐 UX · 🧭 PM | 创建/更新云文档、写入块、读文档 |
| `preset.bitable.default` | 🐑 Shepherd · 🗺️ Account · 🛠️ SE | 多维表格记录增删改查 |
| `preset.im.default` | 🏋️ Coach · 🐑 Shepherd | 发消息 / 消息卡片 |
| `preset.default` | 通用 | 通讯录、群、基础元信息 |

需要更多能力时,把对应预设或具体 API 名追加到 `.mcp.json` 的 `-t` 列表。全部预设见上游 README。

## 应用身份 vs 用户身份

- **默认(应用态 `tenant_access_token`)**:够用于"机器人在共享空间里建/改文档、操作团队多维表格"。
- **用户态(OAuth)**:需要"以你本人身份"访问个人云空间文档时启用。先登录再改配置:
  ```bash
  npx -y @larksuiteoapi/lark-mcp login -a "$FEISHU_APP_ID" -s "$FEISHU_APP_SECRET"
  ```
  然后在 `.mcp.json` 的 args 末尾加 `"--oauth", "--token-mode", "user_access_token"`。

## 最小权限集(应用后台开通)

- 云文档:`docx:document`(读写文档)、`drive:drive`(云空间)
- 多维表格:`bitable:app`(读写多维表格)
- 消息:`im:message`、`im:chat:readonly`(发消息 / 读群信息)

> 用到哪类能力开哪类;改完权限记得在开放平台**发布新版本**才生效。

## 让 Agent 用起来(示例提示词)

> 给 🐑 Project Shepherd:
> "把刚生成的《交付物与验收表》同步进飞书多维表格 `${FEISHU_PIPELINE_APP_TOKEN}`,每个交付物一条记录,字段含交付物/验收标准/负责人/截止日。完成后在群 `${FEISHU_NOTIFY_CHAT_ID}` 发条卡片汇报。"

> 给 🏹 Proposal Strategist:
> "把这版执行摘要创建成一篇飞书云文档,标题用『项目名-执行摘要-日期』,放到我们的方案知识库里。"
