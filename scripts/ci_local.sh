#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"
build_dir="${NAVIGATION_3D_BUILD_DIR:-build-ci}"
install_dir="${NAVIGATION_3D_INSTALL_DIR:-install-ci}"
log_dir="${NAVIGATION_3D_LOG_DIR:-log-ci}"

cd "${workspace_root}"

rm -rf "${build_dir}"
rm -rf "${install_dir}"
rm -rf "${log_dir}"

export NAVIGATION_3D_BUILD_DIR="${build_dir}"
export NAVIGATION_3D_INSTALL_DIR="${install_dir}"
export NAVIGATION_3D_LOG_DIR="${log_dir}"
export NAVIGATION_3D_CLEAN_BUILD="${NAVIGATION_3D_CLEAN_BUILD:-1}"

./scripts/format_check.sh
./scripts/build_workspace.sh "${workspace_root}"
./scripts/test_minimal_navigation.sh "${workspace_root}"
