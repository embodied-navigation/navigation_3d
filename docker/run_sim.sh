#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "${SCRIPT_DIR}")"
IMAGE_VERSION="2026.04.02"
IMAGE_REF="simulator_3d:${IMAGE_VERSION}"
WORKSPACE_DIR="${ROOT_DIR}"
WEBOTS_ASSETS_DIR="${WEBOTS_ASSETS_DIR:-${HOME}/software/assets-R2023b}"
WEBOTS_ROS2_DIR="${WEBOTS_ROS2_DIR:-${ROOT_DIR}/src/simulator/webots_ros2}"
WEBOTS_HOME_DIR="${WEBOTS_HOME_DIR:-${HOME}/software/webots-R2023b-x86-64/webots}"
SIMULATION_WS_DIR="${SIMULATION_WS_DIR:-${HOME}/software/simulation_ws}"

if ! docker image inspect "${IMAGE_REF}" >/dev/null 2>&1; then
    echo "Required image not found: ${IMAGE_REF}"
    echo "Build it first with: bash docker/build.sh sim"
    exit 1
fi

mkdir -p "${SIMULATION_WS_DIR}/src"

xhost +local:root >/dev/null 2>&1 || true

DOCKER_ARGS=(
    -it --rm
    --privileged
    -e "DISPLAY=${DISPLAY:-}"
    -e ROS_DOMAIN_ID=126 \
    -v "/tmp/.X11-unix:/tmp/.X11-unix:rw"
    -e "QT_X11_NO_MITSHM=1"
    -e "QTWEBENGINE_DISABLE_SANDBOX=1"
    -e "WEBOTS_HOME=/usr/local/webots"
    --gpus all
    -e NVIDIA_DRIVER_CAPABILITIES=all
    -e NVIDIA_VISIBLE_DEVICES=all
    -v "${WORKSPACE_DIR}:/navigation_3d/"
    -v "${HOME}/resource:/resource"
    -v "${SIMULATION_WS_DIR}:/simulation_ws:rw"
    -w /simulation_ws
    --network=host
    --device /dev:/dev
    --ipc=host
)

if [ -d "${WEBOTS_ASSETS_DIR}" ]; then
    echo "Using Webots assets: ${WEBOTS_ASSETS_DIR}"
    DOCKER_ARGS+=(
        -v "${WEBOTS_ASSETS_DIR}:/root/.cache/Cyberbotics/Webots/assets:rw"
    )
else
    echo "Webots assets directory not found: ${WEBOTS_ASSETS_DIR}"
    echo "Webots may try to download assets at runtime."
fi

if [ -d "${WEBOTS_HOME_DIR}" ]; then
    echo "Using Webots home: ${WEBOTS_HOME_DIR}"
    DOCKER_ARGS+=(
        -v "${WEBOTS_HOME_DIR}:/usr/local/webots:rw"
    )
else
    echo "Webots home directory not found: ${WEBOTS_HOME_DIR}"
    echo "Expected directory like: ${HOME}/software/webots-R2023b-x86-64/webots"
    exit 1
fi

if [ -d "${WEBOTS_ROS2_DIR}" ]; then
    echo "Using webots_ros2 source: ${WEBOTS_ROS2_DIR}"
    DOCKER_ARGS+=(
        -v "${WEBOTS_ROS2_DIR}:/simulation_ws/src/webots_ros2:rw"
    )
else
    echo "webots_ros2 source directory not found: ${WEBOTS_ROS2_DIR}"
fi

docker run "${DOCKER_ARGS[@]}" \
    "${IMAGE_REF}" /bin/bash -lc 'rm -rf /dev/shm/* && if [ -f /simulation_ws/install/setup.bash ]; then source /simulation_ws/install/setup.bash; fi && exec /bin/bash'