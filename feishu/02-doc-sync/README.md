# ② 文档同步层 · Markdown ↔ 飞书云文档

用 [feishu-cli](https://github.com/riba2534/feishu-cli)(社区,核心能力即 Markdown ↔ 飞书文档 40+ 块类型无损双向转换)把方案 / 教材同步到飞书,并支持反向导出回 Git。与本仓库"方案 / 教材即 Markdown、交叉引用走相对路径"的形态完全契合。

## 安装

```bash
# 需要 Go;详见 feishu-cli 仓库 README
go install github.com/riba2534/feishu-cli@latest
feishu-cli config create-app --save      # 交互式填入 App ID / Secret(或复用 feishu/.env)
```

## 映射表

复制 [`sync-map.example.yaml`](sync-map.example.yaml) 为 `sync-map.yaml`(已 gitignore,含真实 `doc_id`),按"文件 ↔ doc_id"维护;按 `groups` 分组,便于只同步某一类。

## 用法

```bash
# 推送:本地 Markdown -> 飞书云文档
./sync.sh push                 # 同步映射表中全部条目
./sync.sh push curriculum      # 只同步某个分组
SYNC_UPDATE_ONLY=1 ./sync.sh push   # 仅更新已有 doc_id 的条目,绝不新建(CI 默认)

# 拉取:飞书云文档 -> 本地 Markdown(反向留痕)
./sync.sh pull
```

## 首次入库(一次性人工操作)

feishu-cli 的知识库无直接 import 命令;把一篇 Markdown 首次放进**知识库**的标准做法是"先建文档、再移入知识库空间",之后 CI 便能按 `doc_id` 自动更新其内容:

```bash
feishu-cli doc import <file.md> --title <标题>          # 建文档,记下 doc token
feishu-cli wiki spaces                                  # 取目标知识库 space_id
feishu-cli wiki move-docs <doc_token> --space-id <id>   # 移入知识库
# 然后把 doc_id 写进 sync-map.yaml,CI 即可自动保鲜
```

> feishu-cli 子命令 / 参数以 `feishu-cli --help` 实际输出为准;若版本有出入,按实际子命令调整 `sync.sh`。
