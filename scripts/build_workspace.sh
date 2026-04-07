#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"

set +u
source /opt/ros/humble/setup.bash
set -u
cd "${workspace_root}"

colcon build --base-paths src --symlink-install
