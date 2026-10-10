#!/usr/bin/env bash
# coding=utf-8
# @desc 构建 Fastreat 版 MaxKB 全量镜像并推送到私有仓库（默认 ai.fastreat.com:5000/maxkb:fastreat）
#
# 用法:
#   REGISTRY_PASSWORD='xxxx' ./installer/build-and-push-fastreat.sh
#   PLATFORM=linux/amd64 REGISTRY_PASSWORD='xxxx' ./installer/build-and-push-fastreat.sh
#   PREPARE_ONLY=1 ./installer/build-and-push-fastreat.sh    # 只准备构建上下文，不构建（无需 docker）
#
# 可配置项（全部通过环境变量，均有默认值）:
#   REGISTRY           仓库地址           默认 ai.fastreat.com:5000
#   IMAGE_PATH         仓库内路径         默认 maxkb        -> <REGISTRY>/<IMAGE_PATH>:<tag>
#   IMAGE_TAG          镜像标签           默认 fastreat
#   REGISTRY_USER      仓库账号           默认 admin
#   REGISTRY_PASSWORD  仓库密码           默认空（为空且有终端时交互输入，避免写进 shell 历史）
#   LOCAL_ALIAS        本地额外打的 tag   默认 maxkb:fastreat
#   PLATFORM           目标平台           默认空=当前主机架构；x86 服务器用 linux/amd64
#   EXPECT_TITLE       期望的前端标题     默认 Fastreat（镜像内校验不通过会阻止推送）
#   NO_CACHE=1         构建时不使用缓存
#   SKIP_LOGIN=1       跳过 docker login（使用已有登录态）
#   SKIP_PUSH=1        只构建不推送
#   FORCE=1            标题校验失败仍然推送（不建议）
set -euo pipefail

REGISTRY="${REGISTRY:-ai.fastreat.com:5000}"
IMAGE_PATH="${IMAGE_PATH:-maxkb}"
IMAGE_TAG="${IMAGE_TAG:-fastreat}"
REGISTRY_USER="${REGISTRY_USER:-admin}"
REGISTRY_PASSWORD="${REGISTRY_PASSWORD:-}"
LOCAL_ALIAS="${LOCAL_ALIAS:-maxkb:fastreat}"
PLATFORM="${PLATFORM:-}"
EXPECT_TITLE="${EXPECT_TITLE:-Fastreat}"
NO_CACHE="${NO_CACHE:-0}"
SKIP_LOGIN="${SKIP_LOGIN:-0}"
SKIP_PUSH="${SKIP_PUSH:-0}"
PREPARE_ONLY="${PREPARE_ONLY:-0}"
FORCE="${FORCE:-0}"

FULL_IMAGE="${REGISTRY}/${IMAGE_PATH}:${IMAGE_TAG}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

log() { printf '\033[1;34m[%s]\033[0m %s\n' "$(date +%H:%M:%S)" "$*"; }
warn() { printf '\033[1;33m[WARN]\033[0m %s\n' "$*" >&2; }
die() { printf '\033[1;31m[ERROR]\033[0m %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1; }

usage() {
    sed -n '2,30p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit 0
}
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    usage
fi

insecure_registry_hint() {
    cat >&2 <<EOF

私有仓库 ${REGISTRY} 是明文 HTTP（非 HTTPS），docker 默认会拒绝访问。请先放行：

  Linux:
    sudo tee /etc/docker/daemon.json >/dev/null <<'JSON'
    { "insecure-registries": ["${REGISTRY}"] }
    JSON
    sudo systemctl restart docker

  Docker Desktop (macOS/Windows):
    Settings -> Docker Engine，把 "insecure-registries": ["${REGISTRY}"] 合并进 JSON，Apply & Restart

  部署镜像的目标服务器同样需要上面这段配置，否则 docker pull 也会失败。

注意：明文 HTTP 下 docker login 的账号密码以 Basic 认证明文传输，建议仅在内网使用，
      或给仓库配置 TLS 证书后改用 https://${REGISTRY}。

EOF
}

# ---------------------------------------------------------------- 准备构建上下文
# Dockerfile 的 web-build 阶段有一句 `if [ -d "dist" ]; then exit 0; fi`：
# 只要上下文里存在 ui/dist，就会跳过 npm 构建、直接沿用旧产物。本仓库本地存在
# ui/dist（其 <title> 仍是 MaxKB），因此这里复制一份干净上下文，排除 ui/dist、
# ui/node_modules（macOS 上的原生二进制会污染 alpine 构建）等无关内容。
prepare_context() {
    CTX="$(mktemp -d "${TMPDIR:-/tmp}/fastreat-ctx.XXXXXX")"
    log "准备干净构建上下文: ${CTX}"

    if need rsync; then
        rsync -a \
            --exclude '.git' --exclude '.venv' --exclude '.uv-cache' --exclude '.ruff_cache' \
            --exclude '.local' --exclude '.idea' --exclude 'data' \
            --exclude 'ui/node_modules' --exclude 'ui/dist' \
            --exclude '__pycache__' --exclude '*.pyc' --exclude '*.log' \
            "${REPO_ROOT}/" "${CTX}/"
    else
        warn "未找到 rsync，改用 tar 复制上下文"
        ( cd "${REPO_ROOT}" && tar \
            --exclude='./.git' --exclude='./.venv' --exclude='./.uv-cache' --exclude='./.ruff_cache' \
            --exclude='./.local' --exclude='./.idea' --exclude='./data' \
            --exclude='./ui/node_modules' --exclude='./ui/dist' \
            --exclude='__pycache__' --exclude='*.pyc' --exclude='*.log' \
            -cf - . ) | tar -xf - -C "${CTX}"
    fi

    [ -f "${CTX}/installer/Dockerfile" ] || die "构建上下文缺少 installer/Dockerfile"
    [ -d "${CTX}/ui/dist" ] && die "构建上下文里仍存在 ui/dist，Dockerfile 会跳过前端构建"
    [ -f "${CTX}/ui/env/.env" ] || die "构建上下文缺少 ui/env/.env"

    grep -q "VITE_APP_TITLE *= *'${EXPECT_TITLE}'" "${CTX}/ui/env/.env" \
        || die "ui/env/.env 中未找到 VITE_APP_TITLE='${EXPECT_TITLE}'，请先改好标题再构建"
    grep -q "VITE_APP_TITLE *= *'${EXPECT_TITLE}'" "${CTX}/ui/env/.env.chat" \
        || die "ui/env/.env.chat 中未找到 VITE_APP_TITLE='${EXPECT_TITLE}'"

    log "上下文自检通过: 无 ui/dist、无 ui/node_modules、两个 env 的标题均为 ${EXPECT_TITLE}"
    log "上下文大小: $(du -sh "${CTX}" 2>/dev/null | cut -f1)"
}

CTX=""
cleanup() {
    if [ -n "${CTX}" ] && [ "${PREPARE_ONLY}" != "1" ]; then
        rm -rf "${CTX}"
    fi
    return 0
}
trap cleanup EXIT INT TERM

prepare_context

if [ "${PREPARE_ONLY}" = "1" ]; then
    log "PREPARE_ONLY=1，仅准备上下文，不做构建。上下文保留在: ${CTX}"
    log "可自行检查: ls ${CTX}; grep title ${CTX}/ui/env/.env"
    exit 0
fi

# ---------------------------------------------------------------- 构建机自检
log "仓库根目录: ${REPO_ROOT}"
need docker || die "未找到 docker CLI，本机（或本构建机）无法构建镜像"
docker info >/dev/null 2>&1 || die "docker daemon 不可达，请检查 docker 是否启动（或 DOCKER_HOST/context 配置）"
need git || warn "未找到 git，GITHUB_COMMIT 将记为 unknown"

COMMIT="$(cd "${REPO_ROOT}" && git rev-parse --short HEAD 2>/dev/null || echo unknown)"
BUILD_AT="$(TZ=Asia/Shanghai date +'%Y-%m-%dT%H:%M')"

# ---------------------------------------------------------------- 登录仓库
if [ "${SKIP_LOGIN}" != "1" ]; then
    if [ -z "${REGISTRY_PASSWORD}" ]; then
        if [ -t 0 ]; then
            read -r -s -p "请输入 ${REGISTRY_USER}@${REGISTRY} 的密码: " REGISTRY_PASSWORD
            echo
        else
            die "非交互环境请用环境变量提供密码，例如: REGISTRY_PASSWORD='xxxx' $0"
        fi
    fi
    log "登录私有仓库 ${REGISTRY}（用户 ${REGISTRY_USER}，密码经 stdin 传入）"
    if ! printf '%s' "${REGISTRY_PASSWORD}" | docker login "${REGISTRY}" -u "${REGISTRY_USER}" --password-stdin; then
        insecure_registry_hint
        die "docker login ${REGISTRY} 失败"
    fi
else
    log "SKIP_LOGIN=1，使用已有登录态"
fi

# ---------------------------------------------------------------- 构建镜像
build_cmd=(docker build --file "${CTX}/installer/Dockerfile"
    --tag "${FULL_IMAGE}"
    --tag "${LOCAL_ALIAS}"
    --build-arg "DOCKER_IMAGE_TAG=${IMAGE_TAG}"
    --build-arg "BUILD_AT=${BUILD_AT}"
    --build-arg "GITHUB_COMMIT=${COMMIT}")
[ -n "${PLATFORM}" ] && build_cmd+=(--platform "${PLATFORM}")
[ "${NO_CACHE}" = "1" ] && build_cmd+=(--no-cache)
build_cmd+=("${CTX}")

log "开始构建镜像: ${FULL_IMAGE}（本地别名 ${LOCAL_ALIAS}）"
log "平台: ${PLATFORM:-当前主机架构}    commit: ${COMMIT}    build at: ${BUILD_AT}"
log "首次构建需在容器内 npm install + vue-tsc + vite build 并安装 Python 依赖，耗时通常 20-60 分钟"
printf '    %s\n' "${build_cmd[*]}"
"${build_cmd[@]}"

# ---------------------------------------------------------------- 校验镜像内标题
log "校验镜像内前端 <title> 是否为 ${EXPECT_TITLE}"
titles="$(docker run --rm --entrypoint sh "${FULL_IMAGE}" -c \
    'grep -h -o "<title>[^<]*</title>" /opt/maxkb-app/ui/dist/admin/index.html /opt/maxkb-app/ui/dist/chat/index.html' \
    2>/dev/null || true)"
printf '%s\n' "${titles}" | sed '/^$/d' | sed 's/^/    /'
ok_count="$(printf '%s\n' "${titles}" | grep -c "<title>${EXPECT_TITLE}</title>" || true)"

if [ "${ok_count}" -eq 0 ]; then
    if [ "${FORCE}" = "1" ]; then
        warn "镜像内未找到 <title>${EXPECT_TITLE}</title>，但 FORCE=1，继续推送"
    else
        die "镜像内前端标题不是 ${EXPECT_TITLE}，已阻止推送。请确认 ui/env/.env(.chat) 的 VITE_APP_TITLE，或设 FORCE=1 强制推送"
    fi
elif [ "${ok_count}" -lt 2 ]; then
    warn "只校验到 ${ok_count} 个 ${EXPECT_TITLE} 标题（admin/chat 应为 2 个）"
else
    log "标题校验通过（admin + chat 均为 ${EXPECT_TITLE}）"
fi

# ---------------------------------------------------------------- 推送
if [ "${SKIP_PUSH}" = "1" ]; then
    log "SKIP_PUSH=1，跳过推送。镜像已在本地: ${FULL_IMAGE} / ${LOCAL_ALIAS}"
    exit 0
fi

log "推送镜像: ${FULL_IMAGE}"
docker push "${FULL_IMAGE}"

digest="$(docker inspect --format '{{range .RepoDigests}}{{println .}}{{end}}' "${FULL_IMAGE}" 2>/dev/null | sed '/^$/d' || true)"
log "推送完成"
[ -n "${digest}" ] && log "镜像 digest: ${digest}"
cat <<EOF

镜像: ${FULL_IMAGE}
本地别名: ${LOCAL_ALIAS}
目标服务器拉取（同样需配置 insecure-registries）:
  docker pull ${FULL_IMAGE}
  运行: docker run -d --name maxkb --restart=always -p 8080:8080 -v /opt/maxkb:/opt/maxkb ${FULL_IMAGE}

EOF
