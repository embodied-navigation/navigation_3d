#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-${NAVIGATION_3D_BUILD_DIR:-build}}"

ctest --test-dir "${build_dir}" --output-on-failure
