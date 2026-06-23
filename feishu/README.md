# 售前方案产线 · 飞书深度打通

把本仓库(售前 Agent 团队 + 训练营教材,均以 Markdown 为载体)与飞书打通,让产出能在飞书侧**协作、播报、看板化**管理。

## 三层架构(共用一份应用凭证,互不依赖、可单独启用)

| 层 | 组件 | 解决什么 | 目录 |
|---|---|---|---|
| ① Agent 层 | [lark-openapi-mcp](https://github.com/larksuite/lark-openapi-mcp)(官方 MCP) | 让 7 个 Agent 在对话中原生读写飞书云文档 / 多维表格 / 消息 | [`01-agent-mcp/`](01-agent-mcp/) + 根 [`.mcp.json`](../.mcp.json) |
| ② 文档同步层 | [feishu-cli](https://github.com/riba2534/feishu-cli)(社区) | 方案 / 教材 Markdown ↔ 飞书云文档双向无损同步 | [`02-doc-sync/`](02-doc-sync/) |
| ③ 自动化层 | [oapi-sdk-python](https://github.com/larksuite/oapi-sdk-python)(官方 SDK) | 方案状态 → 机器人卡片播报;销售管道 → 多维表格看板 | [`03-automation/`](03-automation/) |

**分工原则**
- 文档类产出走 ②(无损、留痕、进 Git);
- 结构化 / 状态类产出走 ③(看板、播报);
- 对话中即时、零散的操作走 ① MCP。

## 快速开始(5 步)

1. **建应用**:在[飞书开放平台](https://open.feishu.cn/)创建企业自建应用,拿到 App ID / App Secret。
2. **填凭证**:`cp feishu/.env.example feishu/.env`,填入 App ID / Secret(以及后续的群、表 id)。
3. **开权限 + 发版本**:按各层 README 的最小权限集开通 scope,**改完必须在开放平台发布新版本才生效**(最易漏)。
4. **装工具**:① `npx @larksuiteoapi/lark-mcp`(MCP,Claude Code 自动拉起);② 安装 feishu-cli;③ `pip install -r 03-automation/requirements.txt`。
5. **跑通**:对话里让 Agent 调 MCP;`02-doc-sync/sync.sh` 同步文档;`python 03-automation/notify.py ...` 发一张测试卡片。

## 安全约定

- 凭证只进 `feishu/.env` / GitHub Secret,**永不入库**(已 gitignore);仓库内 `*.example.*` 均为脱敏模板。
- 改了权限 scope 必须在开放平台**发布新版本**才生效。
- 机器人**未进群直接发消息必然失败**,先把机器人拉进群再取 `chat_id`。
- CI 默认 `update-only`:`sync-map` 里没填 `doc_id` 的条目不会被同步,首次入库需人工一次(见 [`02-doc-sync/README.md`](02-doc-sync/README.md))。

> 凭证类人工动作(建应用、开权限、拉群、建表、回填 id)无法由 Agent 代办,清单见本仓库根目录交接说明与各层 README。
