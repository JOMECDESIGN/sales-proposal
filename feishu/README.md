# 飞书打通 · 集成工程

> 把这套**售前方案产线**与飞书深度打通,分三层落地。三层共用一份凭证([`.env.example`](.env.example)),互不依赖,可单独启用。
>
> 面向**新人**的"该叫哪个 Agent、连飞书的什么能力"对照,见 [`curriculum/05-飞书打通-使用手册.md`](../curriculum/05-飞书打通-使用手册.md)。

## 三层架构(一图看懂)

```
                售前 Agent 团队(7 个专家)
                          │
   ┌──────────────────────┼──────────────────────┐
   ▼                      ▼                      ▼
① Agent 层             ② 文档同步层            ③ 自动化层
lark-openapi-mcp       feishu-cli             官方 Python SDK
(官方 MCP)            (Markdown↔云文档)      (通知 + 多维表格看板)
   │                      │                      │
   ▼                      ▼                      ▼
Agent 直接读写飞书     方案/教材 ↔ 云文档       管道看板 / 卡片通知
云文档·多维表格·消息   知识库 双向无损同步      审批 / 复盘库
```

| 层 | 目录 | 上游仓库 | 解决什么 |
|---|---|---|---|
| ① Agent 层 | [`01-agent-mcp/`](01-agent-mcp/) | [larksuite/lark-openapi-mcp](https://github.com/larksuite/lark-openapi-mcp)(官方,⭐742) | 让 7 个 Agent **原生操作**飞书云文档/多维表格/消息 |
| ② 文档同步层 | [`02-doc-sync/`](02-doc-sync/) | [riba2534/feishu-cli](https://github.com/riba2534/feishu-cli)(社区,⭐1.2k) | 方案与教材 **Markdown ↔ 飞书云文档**双向无损同步 |
| ③ 自动化层 | [`03-automation/`](03-automation/) | [larksuite/oapi-sdk-python](https://github.com/larksuite/oapi-sdk-python)(官方,⭐525) | 方案状态 **→ 机器人卡片通知**;销售管道 **→ 多维表格看板** |

## 快速开始(5 步)

1. **建应用**:飞书开放平台创建企业自建应用,拿到 `App ID` / `App Secret`。
2. **配凭证**:`cp feishu/.env.example feishu/.env`,填入凭证。
3. **开权限**:在应用后台开通所需权限(各层 README 列了最小权限集),发布版本。
4. **挑层启用**:
   - 要让 Agent 直接干活 → 看 [`01-agent-mcp/README.md`](01-agent-mcp/README.md)
   - 要同步方案/教材 → 看 [`02-doc-sync/README.md`](02-doc-sync/README.md)
   - 要通知/看板 → 看 [`03-automation/README.md`](03-automation/README.md)
5. **拉机器人进群**:把应用机器人加入目标群,`feishu-cli chat list` 取 `chat_id` 回填 `.env`。

## 安全约定

- **凭证只进 `.env`,永不入库**(已在根 [`.gitignore`](../.gitignore) 屏蔽)。仓库里凡是 `*.example.*` 都是脱敏模板。
- MCP 默认用 `tenant_access_token`(应用身份)。需要"以本人身份"读写个人文档时,才按 ① 层文档切到 OAuth 用户态。
- 给应用**最小权限**:只开各层 README 列出的 scope,不要图省事开全量。
