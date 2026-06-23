#!/usr/bin/env bash
# ── 批量同步 Markdown ↔ 飞书云文档 ──────────────────────────
# 依赖:feishu-cli(见本目录 README)、python3 + PyYAML(解析映射表)
# 用法:
#   ./sync.sh push  [group]     本地 → 飞书(改了就推;import 新建 / 已知 id 则更新)
#   ./sync.sh pull  [group]     飞书 → 本地(把云端修改拉回,连图片)
#   ./sync.sh list              列出映射表里的全部条目
# 省略 group 则处理全部分组。
#
# 环境变量:
#   SYNC_UPDATE_ONLY=1  push 时只更新已有 doc_id 的条目,跳过无 id 的(不新建)。
#                       定时 CI 必开,避免每次跑都新建文档造成知识库重复。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MAP="$SCRIPT_DIR/sync-map.yaml"

die() { echo "✗ $*" >&2; exit 1; }

command -v feishu-cli >/dev/null || die "未找到 feishu-cli,先按 README 安装"
command -v python3   >/dev/null || die "未找到 python3(用于解析 sync-map.yaml)"
[[ -f "$MAP" ]] || die "缺少映射表:$MAP(先 cp sync-map.example.yaml sync-map.yaml)"
[[ -n "${FEISHU_APP_ID:-}" && -n "${FEISHU_APP_SECRET:-}" ]] || die "未设置 FEISHU_APP_ID/SECRET(先 source feishu/.env)"

# 解析 YAML → TSV:group \t file \t title \t doc_id
read_map() {
  python3 - "$MAP" "${1:-}" <<'PY'
import sys, yaml
path, only = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "")
data = yaml.safe_load(open(path, encoding="utf-8")) or {}
for group, items in (data.get("groups") or {}).items():
    if only and group != only:
        continue
    for it in (items or []):
        print("\t".join([group, it.get("file",""), it.get("title",""), it.get("doc_id","") or ""]))
PY
}

CMD="${1:-}"; GROUP="${2:-}"
[[ -n "$CMD" ]] || die "用法:./sync.sh {push|pull|list} [group]"

case "$CMD" in
  list)
    printf "%-12s %-50s %s\n" "GROUP" "FILE" "DOC_ID"
    while IFS=$'\t' read -r g f t d; do
      printf "%-12s %-50s %s\n" "$g" "$f" "${d:-<未建>}"
    done < <(read_map "$GROUP")
    ;;

  push)
    while IFS=$'\t' read -r g f t d; do
      src="$REPO_ROOT/$f"
      [[ -f "$src" ]] || { echo "⚠ 跳过(文件不存在):$f"; continue; }
      if [[ -z "$d" && -n "${SYNC_UPDATE_ONLY:-}" ]]; then
        echo "↷ 跳过(update-only,无 doc_id):$f"; continue
      fi
      if [[ -z "$d" ]]; then
        echo "↑ [新建] $f  →  「$t」"
        feishu-cli doc import "$src" --title "$t" --upload-images --verbose
        echo "  ⮑ 记得把新建文档的 doc_id 回填到 sync-map.yaml 的该条目"
      else
        echo "↑ [更新] $f  →  $d"
        # 已知 id:整篇覆盖更新(feishu-cli 用 doc content-update,不是 doc import/update)
        feishu-cli doc content-update "$d" --mode overwrite --markdown "$(cat "$src")" \
          || echo "  ⚠ 更新失败:确认 feishu-cli 版本支持 doc content-update"
      fi
    done < <(read_map "$GROUP")
    ;;

  pull)
    while IFS=$'\t' read -r g f t d; do
      [[ -n "$d" ]] || { echo "⚠ 跳过(无 doc_id):$f"; continue; }
      dst="$REPO_ROOT/$f"
      mkdir -p "$(dirname "$dst")"
      echo "↓ $d  →  $f"
      feishu-cli doc export "$d" -o "$dst" --download-images
    done < <(read_map "$GROUP")
    echo "完成。用 \`git diff\` 查看云端改动,确认后再 commit。"
    ;;

  *) die "未知命令:$CMD(支持 push|pull|list)";;
esac
