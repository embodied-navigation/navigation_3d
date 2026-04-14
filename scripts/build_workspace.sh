#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"
: "${NAVIGATION_3D_BUILD_DIR:=build}"
: "${NAVIGATION_3D_INSTALL_DIR:=install}"
: "${NAVIGATION_3D_LOG_DIR:=log}"
: "${NAVIGATION_3D_CLEAN_BUILD:=0}"
: "${COLCON_PARALLEL_WORKERS:=2}"
: "${CMAKE_BUILD_PARALLEL_LEVEL:=2}"

set +u
source /opt/ros/humble/setup.bash
set -u
cd "${workspace_root}"

if [[ "${NAVIGATION_3D_CLEAN_BUILD}" == "1" ]]; then
  rm -rf "${NAVIGATION_3D_BUILD_DIR}" "${NAVIGATION_3D_INSTALL_DIR}" "${NAVIGATION_3D_LOG_DIR}"
fi

CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL}" \
  colcon --log-base "${NAVIGATION_3D_LOG_DIR}" build \
    --base-paths src \
    --build-base "${NAVIGATION_3D_BUILD_DIR}" \
    --install-base "${NAVIGATION_3D_INSTALL_DIR}" \
    --symlink-install \
    --parallel-workers "${COLCON_PARALLEL_WORKERS}"
