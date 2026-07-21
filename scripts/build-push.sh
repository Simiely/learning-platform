#!/usr/bin/env bash
# 一次性构建并推送镜像到 ghcr.io（或 Docker Hub）。
# 在“有 Docker 的机器”上运行一次，之后部署端只需 `docker compose up` 拉镜像即可。
#
# 首次使用需先登录：
#   ghcr.io : docker login ghcr.io -u Simiely -p <GitHub PAT，需有 write:packages 权限>
#   Docker Hub: docker login -u <你的Docker Hub用户名>   （并把下方 IMAGE 改成 simiely/learning-platform:latest）
set -euo pipefail

# 镜像名（默认 ghcr.io；换 Docker Hub 改这一行）
IMAGE=ghcr.io/simiely/learning-platform:latest

echo "==> Building $IMAGE"
docker build -t "$IMAGE" .

echo "==> Pushing $IMAGE"
docker push "$IMAGE"

echo "==> Done. 部署端现在可以运行："
echo "    docker compose up -d"
