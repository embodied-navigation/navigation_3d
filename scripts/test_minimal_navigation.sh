#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"
install_dir="${NAVIGATION_3D_INSTALL_DIR:-${workspace_root}/install}"
log_file="$(mktemp)"
launch_pid=""

cleanup() {
  if [[ -n "${launch_pid}" ]] && kill -0 "${launch_pid}" 2>/dev/null; then
    kill "${launch_pid}" 2>/dev/null || true
    wait "${launch_pid}" 2>/dev/null || true
  fi
  rm -f "${log_file}"
}

trap cleanup EXIT

set +u
source /opt/ros/humble/setup.bash
source "${install_dir}/setup.bash"
set -u

cd "${workspace_root}"

ros2 launch nav_launch minimal_navigation_smoke.launch.py >"${log_file}" 2>&1 &
launch_pid="$!"

for _ in $(seq 1 45); do
  if grep -q "completed requested goal count" "${log_file}"; then
    cat "${log_file}"
    exit 0
  fi

  if ! kill -0 "${launch_pid}" 2>/dev/null; then
    cat "${log_file}"
    wait "${launch_pid}"
  fi

  sleep 1
done

cat "${log_file}"
echo "minimal navigation smoke test timed out before completion" >&2
exit 1
