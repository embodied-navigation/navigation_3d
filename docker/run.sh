#!/usr/bin/env bash
set -euo pipefail

docker run --rm -it \
  --net=host \
  -e ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}" \
  -e LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH:-}" \
  -v "$(pwd)":/workspace \
  -v "${HOME}/resource":/resource \
  -w /workspace \
  navigation_3d:humble-dev /bin/bash
