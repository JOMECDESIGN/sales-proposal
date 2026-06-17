# CLAUDE.md

本仓库是一套**售前方案产线**:一支角色化的 Agent 团队 + 一套培养新人驾驭它的训练营教材。

## 仓库结构

### Agent 团队(根目录,售前全生命周期的 6 个专家)
| 角色 | 文件 | 职责 |
|---|---|---|
| 🏹 Proposal Strategist | [sales-proposal-strategist.md](sales-proposal-strategist.md) | 赢主题、叙事架构、执行摘要 |
| 🛠️ Sales Engineer | [sales-engineer.md](sales-engineer.md) | 技术发现、Demo/POC、能力→价值翻译、干系人地图 |
| 🧭 Product Manager | [product-manager.md](product-manager.md) | 产品全景、平台演进、路线图 |
| 📐 UX Architect | [design-ux-architect.md](design-ux-architect.md) | 技术架构、UX、可视化 |
| 🐑 Project Shepherd | [project-management-project-shepherd.md](project-management-project-shepherd.md) | 交付计划、验收、风险 |
| 🏋️ Sales Coach | [sales-coach.md](sales-coach.md) | 方案自检、答辩演练、复盘 |

### 培训教材(`curriculum/`)
教新人驾驭上面这支团队。**总入口:[curriculum/00-README-学习路径.md](curriculum/00-README-学习路径.md)**
- 学:`01-认知篇` · `02-方法论-招式卡片`(16招)· `03-Agent团队使用手册`(+ `03-附录-Agent人设与售前角色对照`)· `04-流程篇`
- 练:`案例标杆/`(太空舱、船舶两份标杆)· `练习/`(E1/E2/E3)
- 产:`模板库/`(4 件可填模板)

## 怎么用这个仓库

- **要做一份方案** → 按 [curriculum/04-流程篇](curriculum/04-流程篇-从挖需求到拿单.md) 的五段流程,依次召唤对应 Agent。
- **要查某个方法/招式** → 看 [curriculum/02-方法论-招式卡片.md](curriculum/02-方法论-招式卡片.md)(16 招,分三组,每招标注由哪个 Agent 执行)。
- **要知道该叫哪个 Agent、怎么喂料** → 看 [curriculum/03-Agent团队使用手册.md](curriculum/03-Agent团队使用手册.md)。
- **新人入门** → 从 [curriculum/00-README](curriculum/00-README-学习路径.md) 选一条学习路径。

## 业务领域(两大主营,各有标杆)
- 智能座舱 / 展陈 / 人机交互 → 标杆:`curriculum/案例标杆/太空舱方案-*.md`
- 船舶智能化 / 智能航运(元启晨星)→ 标杆:`curriculum/案例标杆/船舶方案-架构思路.md`

## 维护约定
- 教材内所有交叉引用使用相对路径,改文件名时同步更新引用(根 README、CLAUDE.md、curriculum 内部)。
- 16 招与 6 个 Agent 是对应关系(每招都由确定的 Agent 执行);新增招式时,同步更新 `02` 速查表和 `03` 对应 Agent 卡片。
