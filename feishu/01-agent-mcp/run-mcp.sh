#!/usr/bin/env bash
# 启动飞书官方 MCP(@larksuiteoapi/lark-mcp),凭证按优先级解析,兼容多环境:
#   1) feishu/.env(若存在)
#   2) 进程环境变量 FEISHU_APP_ID / FEISHU_APP_SECRET(本仓库约定 / 本地/桌面版)
#   3) 进程环境变量 LARK_APP_ID / LARK_APP_SECRET(Claude Code 网页版默认注入)
# 解决的问题:网页版注入的是 LARK_*,而 .mcp.json 旧写法只认 ${FEISHU_APP_ID},
# 展开为空导致 lark-mcp 报 “Missing access token”。
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$HERE/../.env"
if [ -f "$ENV_FILE" ]; then
  set -a; . "$ENV_FILE"; set +a
fi

APP_ID="${FEISHU_APP_ID:-${LARK_APP_ID:-}}"
APP_SECRET="${FEISHU_APP_SECRET:-${LARK_APP_SECRET:-}}"

DOMAIN_ARGS=()
case "${FEISHU_DOMAIN:-cn}" in
  intl|lark|global|larksuite) DOMAIN_ARGS=(--domain https://open.larksuite.com) ;;
esac

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
  echo "lark-mcp: 缺少应用凭证(FEISHU_APP_ID/SECRET 或 LARK_APP_ID/SECRET 或 feishu/.env)" >&2
  exit 1
fi

# 自检模式:只验证凭证解析,不真正拉起服务(供 CI / 排查用)
if [ -n "${LARK_MCP_CHECK:-}" ]; then
  echo "OK 凭证已解析,app_id 前缀=${APP_ID:0:6}  domain=${FEISHU_DOMAIN:-cn}"
  exit 0
fi

exec npx -y @larksuiteoapi/lark-mcp mcp \
  -a "$APP_ID" -s "$APP_SECRET" \
  -t "preset.default,preset.doc.default,preset.bitable.default,preset.im.default" \
  "${DOMAIN_ARGS[@]}"
