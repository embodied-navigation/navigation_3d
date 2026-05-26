#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_VERSION_NAV="$(<"${ROOT_DIR}/docker/IMAGE_VERSION_NAV")"
IMAGE_REF="navigation_3d:${IMAGE_VERSION_NAV}"

WORKSPACE_DIR="${ROOT_DIR}"
ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
ACCEL_MODE="${ACCEL_MODE:-cpu}"
CONTAINER_HOME="${CONTAINER_HOME:-/root}"
CONTAINER_NAV_ENV="${CONTAINER_HOME}/navigation_3d"

if [[ "${ACCEL_MODE}" != "cpu" && "${ACCEL_MODE}" != "gpu" ]]; then
    echo "Invalid accel mode: ${ACCEL_MODE}"
    echo "Usage: ROS_DOMAIN_ID=<id> ACCEL_MODE=<cpu|gpu> bash docker/run.sh"
    exit 1
fi

if ! docker image inspect "${IMAGE_REF}" >/dev/null 2>&1; then
    echo "Required image not found: ${IMAGE_REF}"
    echo "Build it first with: bash docker/build.sh"
    exit 1
fi

xhost +local:root > /dev/null 2>&1

DOCKER_ARGS=(
    -it --rm
    --privileged
    -e "DISPLAY=${DISPLAY}"
    -v "/tmp/.X11-unix:/tmp/.X11-unix:rw"
    -e "QT_X11_NO_MITSHM=1"
    -e "ROS_DOMAIN_ID=${ROS_DOMAIN_ID}"
    -e "HOME=${CONTAINER_HOME}"
    -v "${WORKSPACE_DIR}:${CONTAINER_NAV_ENV}/"
    -v "${HOME}/resource:${CONTAINER_HOME}/resource"
    -w "${CONTAINER_NAV_ENV}"
    --network=host
    --device /dev:/dev
    --ipc=host
)

if [[ "${ACCEL_MODE}" == "gpu" ]]; then
    DOCKER_ARGS+=(
        --gpus all
        -e NVIDIA_DRIVER_CAPABILITIES=all
        -e NVIDIA_VISIBLE_DEVICES=all
    )
fi

CONTAINER_CMD=$(cat <<'EOF'
rm -rf /dev/shm/*
# source "${HOME}/navigation_3d/docker/runtime_env.sh"
exec /bin/bash
EOF
)

docker run "${DOCKER_ARGS[@]}" \
    "${IMAGE_REF}" \
    /bin/bash -lc "${CONTAINER_CMD}"
    