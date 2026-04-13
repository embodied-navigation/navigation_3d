#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"
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
source "${workspace_root}/install/setup.bash"
set -u

cd "${workspace_root}"

ros2 launch nav_launch minimal_navigation_smoke.launch.py >"${log_file}" 2>&1 &
launch_pid="$!"

goal_seen=0
plan_seen=0
controller_seen=0

for _ in $(seq 1 30); do
  if grep -q "published goal" "${log_file}"; then
    goal_seen=1
  fi

  if [[ "${goal_seen}" -eq 1 && "${plan_seen}" -eq 0 ]]; then
    if timeout 1s ros2 topic echo --once /plan >/dev/null 2>&1; then
      plan_seen=1
    fi
  fi

  if [[ "${controller_seen}" -eq 0 ]]; then
    if timeout 1s ros2 topic echo --once /controller/status >/dev/null 2>&1; then
      controller_seen=1
    fi
  fi

  if [[ "${goal_seen}" -eq 1 && "${plan_seen}" -eq 1 && "${controller_seen}" -eq 1 ]]; then
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
echo "navigation smoke test timed out before observing goal publication, plan output, and controller status" >&2
exit 1
