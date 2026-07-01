# CLAUDE.md

本仓库是一套**售前方案产线**:一支角色化的 Agent 团队 + 一套培养新人驾驭它的训练营教材。

## 仓库结构

### Agent 团队(根目录,售前全生命周期的 7 个专家)
| 角色 | 文件 | 职责 |
|---|---|---|
| 🏹 Proposal Strategist | [sales-proposal-strategist.md](sales-proposal-strategist.md) | 赢主题、叙事架构、执行摘要 |
| 🛠️ Sales Engineer | [sales-engineer.md](sales-engineer.md) | 技术发现、Demo/POC、能力→价值翻译 |
| 🗺️ Account Strategist | [sales-account-strategist.md](sales-account-strategist.md) | 干系人地图、受众分层、商务路径 |
| 🧭 Product Manager | [product-manager.md](product-manager.md) | 产品全景、平台演进、路线图 |
| 📐 UX Architect | [design-ux-architect.md](design-ux-architect.md) | 技术架构、UX、可视化 |
| 🐑 Project Shepherd | [project-management-project-shepherd.md](project-management-project-shepherd.md) | 交付计划、验收、风险 |
| 🏋️ Sales Coach | [sales-coach.md](sales-coach.md) | 方案自检、答辩演练、复盘 |

### 培训教材(`curriculum/`)
教新人驾驭上面这支团队。**总入口:[curriculum/00-README-学习路径.md](curriculum/00-README-学习路径.md)**
- 学:`01-认知篇` · `02-方法论-招式卡片`(16招)· `03-Agent团队使用手册` · `04-流程篇`
- 练:`案例标杆/`(太空舱、船舶两份标杆)· `练习/`(E1/E2/E3)
- 产:`模板库/`(4 件可填模板)
- 出片:`06-排版篇-把方案变好看.md`(开源 Markdown → 专业 PDF / 答辩 deck;Marp · Slidev · Pandoc)

## 怎么用这个仓库

- **要做一份方案** → 按 [curriculum/04-流程篇](curriculum/04-流程篇-从挖需求到拿单.md) 的五段流程,依次召唤对应 Agent。
- **要查某个方法/招式** → 看 [curriculum/02-方法论-招式卡片.md](curriculum/02-方法论-招式卡片.md)(16 招,分三组,每招标注由哪个 Agent 执行)。
- **要知道该叫哪个 Agent、怎么喂料** → 看 [curriculum/03-Agent团队使用手册.md](curriculum/03-Agent团队使用手册.md)。
- **新人入门** → 从 [curriculum/00-README](curriculum/00-README-学习路径.md) 选一条学习路径。
- **要把方案产线接进飞书** → 看 [curriculum/05-飞书打通-使用手册.md](curriculum/05-飞书打通-使用手册.md)(用法)与 [feishu/README.md](feishu/README.md)(工程实现)。
- **要把方案排成好看的版面 / 出 PDF / 出答辩 deck** → 看 [curriculum/06-排版篇](curriculum/06-排版篇-把方案变好看.md)(开源 Markdown 出片选型 + 植入步骤)。

## 飞书集成(`feishu/`,三层)
- **① Agent 层**:官方 MCP [lark-openapi-mcp](https://github.com/larksuite/lark-openapi-mcp),根目录 [.mcp.json](.mcp.json) 已内置,让 7 个 Agent 直接读写飞书云文档/多维表格/消息。
- **② 文档同步层**:[feishu-cli](https://github.com/riba2534/feishu-cli),Markdown ↔ 云文档双向无损;批量同步脚本 `feishu/02-doc-sync/sync.sh`。
- **③ 自动化层**:官方 [oapi-sdk-python](https://github.com/larksuite/oapi-sdk-python),`notify.py`(状态卡片播报)、`pipeline_base.py`(管道多维表格看板)。
- 凭证只进 `feishu/.env`(已 `.gitignore`);仓库内 `*.example.*` 均为脱敏模板,勿强加 `.env` / `sync-map.yaml`。
- 凭证变量名兼容两组:`FEISHU_APP_ID/SECRET` 与 `LARK_APP_ID/SECRET`(网页版默认注入后者),脚本与 MCP 包装脚本均自动识别。
- **网页版限制**:Claude Code 网页版给 MCP 子进程套了出口代理白名单,`open.feishu.cn` 不在内,`mcp__lark__*` 可能报 `private IP`/`Missing access token`;此为平台网络策略,非代码问题。要原生 MCP 用桌面/本地版,或放开环境网络策略。第③层直连脚本不受影响,已验证可用。

## 业务领域(两大主营,各有标杆)
- 智能座舱 / 展陈 / 人机交互 → 标杆:`curriculum/案例标杆/太空舱方案-*.md`
- 船舶智能化 / 智能航运(元启晨星)→ 标杆:`curriculum/案例标杆/船舶方案-架构思路.md`(**运营域**)
- 造船智能制造 / 智能船厂(元启晟)→ 标杆:`curriculum/案例标杆/造船智能制造-AI无纸化-知识卡片.md`(**制造域**:12 把懂行尺子 + AI 红线 + 候选新招)
- 跨域架构参考(航空 IMA / 船舶 IBS·IAS / 智能座舱域控制器,三域共通的"集成式架构"模式)→ 标杆:`curriculum/案例标杆/集成系统架构-跨域知识卡片.md`(为船舶与座舱两条线的**招 7 架构地图**提供技术锚点,不对应单一客户案例)

## 维护约定
- 教材内所有交叉引用使用相对路径,改文件名时同步更新引用(根 README、CLAUDE.md、curriculum 内部)。
- 16 招与 7 个 Agent 是一一对应关系(招式由 Agent 执行);新增招式时,同步更新 `02` 速查表和 `03` 对应 Agent 卡片。
- `feishu/` 下脚本改了命令/接口,同步更新对应层 README 与 `curriculum/05-飞书打通-使用手册.md` 的命令示例;新增飞书能力时,先在 `05` 的「Agent → 飞书能力对照」表登记由哪个 Agent 经哪一层使用。
