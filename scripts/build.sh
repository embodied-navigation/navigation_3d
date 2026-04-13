#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-${NAVIGATION_3D_BUILD_DIR:-build}}"

cmake --build "${build_dir}"
