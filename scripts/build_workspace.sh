#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"
: "${COLCON_PARALLEL_WORKERS:=2}"
: "${CMAKE_BUILD_PARALLEL_LEVEL:=2}"

set +u
source /opt/ros/humble/setup.bash
set -u
cd "${workspace_root}"

CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL}" \
  colcon build --base-paths src --symlink-install --parallel-workers "${COLCON_PARALLEL_WORKERS}"
