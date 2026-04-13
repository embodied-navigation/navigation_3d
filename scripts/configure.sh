#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-${NAVIGATION_3D_BUILD_DIR:-build}}"

if command -v ninja >/dev/null 2>&1; then
  cmake -S . -B "${build_dir}" -G Ninja
else
  cmake -S . -B "${build_dir}" -G "Unix Makefiles"
fi
