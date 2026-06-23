# 第② 层 · 文档同步(Markdown ↔ 飞书云文档)

> 目标:本仓库里的**方案、教材、模板**是 Markdown;客户和销售在飞书云文档/知识库里协作。这一层做**双向无损同步**——推上去给人看,改回来进 Git。
>
> 上游:[riba2534/feishu-cli](https://github.com/riba2534/feishu-cli)(社区,⭐1.2k),核心能力是 Markdown ↔ 飞书文档 40+ 块类型无损互转(含表格、代码块、Mermaid)。

## 安装

```bash
# 方式一(推荐):一键脚本
curl -fsSL https://raw.githubusercontent.com/riba2534/feishu-cli/main/install.sh | bash
# 方式二:Go ≥ 1.21
go install github.com/riba2534/feishu-cli@latest
```

## 配凭证

```bash
export FEISHU_APP_ID=cli_xxx FEISHU_APP_SECRET=xxx   # 或 source feishu/.env
# 需要写个人知识库等用户态能力时:
feishu-cli auth login
```

## 两条核心命令

```bash
# 推:Markdown → 新建飞书云文档
feishu-cli doc import curriculum/案例标杆/太空舱方案-逐段批注.md \
  --title "太空舱方案-逐段批注" --verbose

# 拉:飞书云文档 → Markdown(连图片一起下)
feishu-cli doc export <doc_id> -o curriculum/案例标杆/太空舱方案-逐段批注.md \
  --download-images
```

`<doc_id>` 取自文档 URL `https://xxx.feishu.cn/docx/<doc_id>` 的最后一段。

## 批量同步:`sync.sh`

逐个文件敲命令太累。本目录的 [`sync.sh`](sync.sh) 读取 [`sync-map.yaml`](sync-map.example.yaml) 里的映射表,一条命令批量推/拉:

```bash
cp feishu/02-doc-sync/sync-map.example.yaml feishu/02-doc-sync/sync-map.yaml
# 编辑 sync-map.yaml,把要同步的文件 ↔ 飞书 doc_id 配好

source feishu/.env
feishu/02-doc-sync/sync.sh push      # 本地 → 飞书(改了方案/教材后推上去)
feishu/02-doc-sync/sync.sh pull      # 飞书 → 本地(把评审修改拉回来进 Git)
feishu/02-doc-sync/sync.sh push proposals   # 只同步某个分组
```

> `sync-map.yaml`(去掉 `.example`)按惯例不入库——它含具体 doc_id,属于一次方案的工作态。`sync-map.example.yaml` 是脱敏模板。

## 典型用法

| 场景 | 命令 |
|---|---|
| 方案初稿给客户协作 | `doc import 方案.md` → 把链接发群,客户在飞书上批注 |
| 客户改完拉回来留痕 | `doc export <id>` → `git diff` 看改了什么 → commit |
| 教材发到知识库 | `feishu-cli wiki ...`(子命令见上游 README 的 `wiki` 组) |
| 整批方案/教材一键推 | `sync.sh push` |

## 定时同步到知识库(GitHub Actions CI)

仓库已带工作流 [`.github/workflows/feishu-sync.yml`](../../.github/workflows/feishu-sync.yml):**每周一**(可手动触发)自动把教材/标杆目录 `sync.sh push` 到飞书知识库,保持内容最新。

- **幂等**:CI 以 `SYNC_UPDATE_ONLY=1` 运行,**只更新已有 `doc_id` 的条目,绝不新建**,不会往知识库塞重复文档。
- **首次入库一次性人工操作**(把一篇 Markdown 放进知识库):
  ```bash
  feishu-cli doc import curriculum/案例标杆/船舶方案-架构思路.md --title "船舶方案-架构思路"
  feishu-cli wiki spaces                       # 取目标知识库 space_id
  feishu-cli wiki move-docs <doc_token> --space-id <space_id>   # 移入知识库
  ```
  然后把该文档的 `doc_id` 写进映射表,CI 之后便自动保鲜。
- **配置 CI**:在仓库 `Settings → Secrets and variables → Actions` 配置
  - Secret `FEISHU_APP_ID` / `FEISHU_APP_SECRET`:应用凭证
  - Secret `FEISHU_SYNC_MAP`:`sync-map.yaml` 的完整内容(含各教材文件 ↔ `doc_id`;因含具体 id 不入库,故走 Secret)
  - 可选 Variable `FEISHU_DOMAIN`:`cn`(默认)或 `intl`
- **改 cron**:编辑工作流 `on.schedule.cron`(用的是 UTC)。

## 最小权限集

云文档读写 `docx:document` + 云空间 `drive:drive`;要发知识库再加 `wiki:wiki`。

## 与第①层的分工

- **第① 层 MCP**:Agent 在对话里**即时**建/改单篇文档(写的时候顺手推)。
- **第② 层 feishu-cli**:**批量、可脚本化、可进 CI** 的目录级同步与回流留痕。
两者同源凭证,按"单篇即时" vs "整批留痕"分工,不冲突。
