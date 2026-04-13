#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"
image_name="${NAVIGATION_3D_IMAGE:-navigation_3d:humble-dev}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required to run the integration smoke test" >&2
  exit 1
fi

if ! docker image inspect "${image_name}" >/dev/null 2>&1; then
  ./docker/build.sh
fi

docker_args=(
  --rm
  --privileged
  --ipc=host
  --shm-size=1g
  --net=host
  -w /workspace
  -e "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-0}"
  -e "LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH:-}"
  -e "GIT_SSH_COMMAND=ssh -o StrictHostKeyChecking=accept-new"
  -v "${workspace_root}:/workspace"
  -v "${workspace_root}/config:/root/config:ro"
)

if [[ -n "${SSH_AUTH_SOCK:-}" && -S "${SSH_AUTH_SOCK}" ]]; then
  docker_args+=(
    -e "SSH_AUTH_SOCK=${SSH_AUTH_SOCK}"
    -v "${SSH_AUTH_SOCK}:${SSH_AUTH_SOCK}"
  )
fi

docker run "${docker_args[@]}" "${image_name}" /bin/bash -lc '
  set -euo pipefail
  source /workspace/env.sh
  rm -rf /workspace/build /workspace/install /workspace/log
  ./scripts/setup_workspace.sh /workspace /workspace/repos/private.repos
  ./scripts/build_workspace.sh /workspace
  ./scripts/test_navigation_smoke.sh /workspace
'
