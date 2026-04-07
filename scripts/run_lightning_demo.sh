#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"

set +u
source /opt/ros/humble/setup.bash
source "${workspace_root}/install/setup.bash"
set -u

echo "lightning-lm demo entrypoint placeholder" >&2
echo "Run one of the official commands after your dataset path is ready, for example:" >&2
echo "  ros2 run lightning run_slam_offline --ros-args -p config_file:=<config> -p bag_path:=<bag>" >&2
