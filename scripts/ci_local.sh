#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"
build_dir="${NAVIGATION_3D_BUILD_DIR:-build-ci}"

cd "${workspace_root}"

rm -rf "${build_dir}"

export NAVIGATION_3D_BUILD_DIR="${build_dir}"

./scripts/format_check.sh
./scripts/configure.sh
./scripts/build.sh
./scripts/test.sh
