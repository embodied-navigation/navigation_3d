#!/usr/bin/env bash
set -euo pipefail

docker run --rm -it \
  -v "$(pwd)":/workspace/navigation_3d \
  -w /workspace/navigation_3d \
  navigation_3d:dev
