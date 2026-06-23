#!/usr/bin/env bash
# Markdown <-> 飞书云文档 批量同步(基于 riba2534/feishu-cli)
#
# 用法:
#   ./sync.sh push [group]     本地 Markdown -> 飞书云文档
#   ./sync.sh pull [group]     飞书云文档 -> 本地 Markdown
# 环境:
#   SYNC_UPDATE_ONLY=1         仅更新已有 doc_id 的条目,绝不新建(CI 默认)
#   SYNC_MAP=path              指定映射表(默认 sync-map.yaml)
#
# 凭证:从 feishu/.env 读取(FEISHU_APP_ID / FEISHU_APP_SECRET / FEISHU_DOMAIN)。
# 说明:feishu-cli 子命令以 `feishu-cli --help` 实际为准,如有出入按需调整下方调用。

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
MAP="${SYNC_MAP:-$HERE/sync-map.yaml}"
ACTION="${1:-push}"
GROUP="${2:-}"
UPDATE_ONLY="${SYNC_UPDATE_ONLY:-0}"

# 加载凭证
if [[ -f "$ROOT/feishu/.env" ]]; then
  set -a; # shellcheck disable=SC1091
  source "$ROOT/feishu/.env"; set +a
fi
if [[ -z "${FEISHU_APP_ID:-}" || -z "${FEISHU_APP_SECRET:-}" ]]; then
  echo "::notice:: 未配置 FEISHU_APP_ID/SECRET,跳过同步。" >&2
  exit 0
fi
if [[ ! -f "$MAP" ]]; then
  echo "::notice:: 未找到映射表 $MAP,跳过同步(首次入库见 README)。" >&2
  exit 0
fi
command -v feishu-cli >/dev/null 2>&1 || { echo "ERROR: 未安装 feishu-cli" >&2; exit 1; }

# 用 Python 解析 YAML -> 逐行输出 "file<TAB>doc_id<TAB>title"
mapfile -t ENTRIES < <(python3 - "$MAP" "$GROUP" <<'PY'
import sys, yaml
path, group = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "")
data = yaml.safe_load(open(path, encoding="utf-8")) or {}
for gname, items in (data.get("groups") or {}).items():
    if group and gname != group:
        continue
    for it in (items or []):
        f = it.get("file", ""); d = it.get("doc_id", "") or ""; t = it.get("title", "")
        if f:
            print(f"{f}\t{d}\t{t}")
PY
)

[[ ${#ENTRIES[@]} -eq 0 ]] && { echo "::notice:: 映射表无匹配条目(group='$GROUP')。"; exit 0; }

push_one() {
  local file="$1" doc_id="$2" title="$3"
  local abs="$ROOT/$file"
  [[ -f "$abs" ]] || { echo "  跳过(本地缺文件): $file" >&2; return; }
  if [[ -n "$doc_id" ]]; then
    echo "  更新 <- $file"
    feishu-cli doc update --doc-id "$doc_id" --file "$abs"
  elif [[ "$UPDATE_ONLY" == "1" ]]; then
    echo "  跳过(update-only 且无 doc_id): $file"
  else
    echo "  新建 <- $file"
    feishu-cli doc import "$abs" --title "${title:-$file}"
  fi
}

pull_one() {
  local file="$1" doc_id="$2"
  [[ -n "$doc_id" ]] || { echo "  跳过(无 doc_id): $file"; return; }
  echo "  拉取 -> $file"
  feishu-cli doc export "$doc_id" --output "$ROOT/$file"
}

echo "[$ACTION] 条目数: ${#ENTRIES[@]}  update_only=$UPDATE_ONLY  group='${GROUP:-ALL}'"
for line in "${ENTRIES[@]}"; do
  IFS=$'\t' read -r file doc_id title <<<"$line"
  case "$ACTION" in
    push) push_one "$file" "$doc_id" "$title" ;;
    pull) pull_one "$file" "$doc_id" ;;
    *) echo "未知动作: $ACTION (用 push|pull)" >&2; exit 1 ;;
  esac
done
echo "完成。"
