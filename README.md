# sales-proposal
This agent team is designed for developing high-quality pre-sales technical proposals for complex innovation prototype projects, especially smart cabin, intelligent cockpit, vehicle exhibition demo, human-machine interaction, and ship/marine intelligence (smart shipping) scenarios.

> ## ⚡ 一页速览
>
> **这是什么**:一条**售前方案产线** = 🤖 7 个角色化 Agent + 📚 学练产训练营(`curriculum/` 00–06)+ 🪶 飞书三层深度集成。方案与教材皆为 Markdown,可一键同步到飞书协作。
>
> **目录速记**
> - 根目录 7 个 `*.md` = **7 个 Agent 人设**(每个顶部有「🎯 本仓库售前用法」)
> - `curriculum/` = 01 认知 · 02 方法论 16 招 · 03 Agent 手册 · 04 流程 · **05 飞书打通** · **06 排版出片** · 案例标杆 · 练习 · 模板库
> - `feishu/` = ① MCP ② 文档双向同步 ③ 自动化脚本;`.github/` = 教材定时同步知识库 CI
>
> **飞书三步上手**
> 0. 装依赖:`pip install -r requirements.txt`(纯 urllib 的脚本可跳过;notify/pipeline/出片才需要)
> 1. `cp feishu/.env.example feishu/.env` 填凭证(脚本认 `FEISHU_*` 或 `LARK_*`)
> 2. 搭建:`python feishu/03-automation/init_pipeline.py`(建管道表)· `list_chats.py`(找群 id)· `grant_access.py`(授权)
> 3. 日常:`pipeline_base.py`(管道看板)· `notify.py`(群卡片播报)· `wiki_publish.py`(发知识库指定节点)
>
> **状态**:第②③层(直连脚本)已实测可用——发布文档进知识库 / 销售管道多维表格 / 群卡片播报全部跑通。
> 第①层 `mcp__lark__*` 在**网页版**受平台出口代理白名单限制可能不通,改用桌面/本地版或放开环境网络策略;脚本不受影响。详见 [`feishu/README.md`](feishu/README.md)。

本仓库 = **一支售前 Agent 团队** + **一套培养新人驾驭它的训练营**。

## 🤖 Agent 团队(7 个售前专家)

| 角色 | 文件 | 职责 |
|---|---|---|
| 🏹 Proposal Strategist | [sales-proposal-strategist.md](sales-proposal-strategist.md) | 赢主题、叙事架构、执行摘要 |
| 🛠️ Sales Engineer | [sales-engineer.md](sales-engineer.md) | 技术发现、Demo/POC、能力→价值翻译 |
| 🗺️ Account Strategist | [sales-account-strategist.md](sales-account-strategist.md) | 干系人地图、受众分层、商务路径 |
| 🧭 Product Manager | [product-manager.md](product-manager.md) | 产品全景、平台演进、路线图 |
| 📐 UX Architect | [design-ux-architect.md](design-ux-architect.md) | 技术架构、UX、可视化 |
| 🐑 Project Shepherd | [project-management-project-shepherd.md](project-management-project-shepherd.md) | 交付计划、验收、风险 |
| 🏋️ Sales Coach | [sales-coach.md](sales-coach.md) | 方案自检、答辩演练、复盘 |

## 📚 培训教材(`curriculum/`)

把纯新人(应届/转岗)带到"能独立驾驭 Agent 团队、交付一份打得出去的方案"。

> **总入口:[curriculum/00-README-学习路径.md](curriculum/00-README-学习路径.md)**

- **学** — [01 认知篇](curriculum/01-认知篇-售前与方案.md) · [02 方法论·16招](curriculum/02-方法论-招式卡片.md) · [03 Agent 团队使用手册](curriculum/03-Agent团队使用手册.md) · [04 流程篇](curriculum/04-流程篇-从挖需求到拿单.md)
- **练** — [太空舱标杆批注](curriculum/案例标杆/太空舱方案-逐段批注.md) · [船舶标杆思路](curriculum/案例标杆/船舶方案-架构思路.md) · [船舶核心产品·智能船机交互系统](curriculum/案例标杆/船舶-智能船机交互系统-核心产品说明.md) · [船舶 Yog IOT 技术底座](curriculum/案例标杆/船舶-Yog-IOT-技术底座解读.md) · [岸基远控综合平台·项目素材](curriculum/案例标杆/船舶-岸基远控综合平台-中远海运重工舟山-项目素材.md) · [造船制造标杆卡](curriculum/案例标杆/造船智能制造-AI无纸化-知识卡片.md) · [练习 E1/E2/E3](curriculum/练习/)
- **产** — [模板库](curriculum/模板库/)(对比矩阵 / 验收表 / 风险登记 / 关键路径)
- **出片** — [06 排版篇](curriculum/06-排版篇-把方案变好看.md)(把 `.md` 一键变专业 PDF 文档 / 答辩 deck;Marp · Slidev · Pandoc)
- **通** — [05 飞书打通使用手册](curriculum/05-飞书打通-使用手册.md) · 工程实现见 [`feishu/`](feishu/)

## 🪶 飞书打通(`feishu/`)

把方案产线与飞书深度集成,三层可单独启用:① 官方 [lark-openapi-mcp](https://github.com/larksuite/lark-openapi-mcp) 让 7 个 Agent 直接操作飞书(根 [`.mcp.json`](.mcp.json) 已内置);② [feishu-cli](https://github.com/riba2534/feishu-cli) 做方案/教材 Markdown ↔ 云文档双向同步;③ 官方 [oapi-sdk-python](https://github.com/larksuite/oapi-sdk-python) 做状态卡片播报与销售管道多维表格看板。落地步骤见 [`feishu/README.md`](feishu/README.md)。

> **状态**:飞书集成已并入 `main`,可直接使用。
> - 凭证:脚本与 MCP 同时认 `FEISHU_APP_ID/SECRET` 与 `LARK_APP_ID/SECRET`(网页版默认注入后者),也可放进本地 `feishu/.env`(不入库)。
> - **第③层(脚本)已验证可用**:发布文档进知识库、销售管道多维表格、群卡片播报均实测跑通。
> - **第①层(MCP)** 在 Claude Code **网页版**受平台出口代理白名单限制(`open.feishu.cn` 不在白名单),`mcp__lark__*` 可能不通;改用**桌面/本地版**(无此限制)或放开环境网络策略即可。详见 [`feishu/01-agent-mcp/README.md`](feishu/01-agent-mcp/README.md)。

## 快速上手

| 你想做什么 | 去哪 |
|---|---|
| 做一份方案 | [04 流程篇](curriculum/04-流程篇-从挖需求到拿单.md) 五段流程,依次召唤 Agent |
| 查某个方法/招式 | [02 方法论·16招](curriculum/02-方法论-招式卡片.md) |
| 不知道该叫哪个 Agent | [03 Agent 团队使用手册](curriculum/03-Agent团队使用手册.md) |
| 新人从零入门 | [00 学习路径](curriculum/00-README-学习路径.md) |
| 把方案排成好看的版面 / 出 PDF / deck | [06 排版篇](curriculum/06-排版篇-把方案变好看.md) |
