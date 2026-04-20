#!/usr/bin/env bash
set -euo pipefail

image_name="${NAVIGATION_3D_IMAGE:-navigation_3d:humble-dev}"
workspace_dir="$(pwd)"
resource_dir="${HOME}/resource"
host_ld_library_path="${LD_LIBRARY_PATH:-}"
workspace_config_dir="${workspace_dir}/config"
container_home="/root"
container_config_dir="${container_home}/config"
container_env_file="/workspace/env.sh"
shell_command="if [[ -f ${container_env_file} ]]; then source ${container_env_file}; fi; exec /bin/bash"
non_interactive_command=""
docker_network_mode="${NAVIGATION_3D_DOCKER_NETWORK_MODE:-host-only}"
ros_localhost_only="${NAVIGATION_3D_ROS_LOCALHOST_ONLY:-1}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -c|--command)
      shift
      if [[ $# -eq 0 ]]; then
        echo "Missing command after -c/--command" >&2
        exit 1
      fi
      non_interactive_command="$1"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      echo "Usage: $0 [-c|--command \"<cmd>\"]" >&2
      exit 1
      ;;
  esac
done

if [[ -n "${non_interactive_command}" ]]; then
  shell_command="if [[ -f ${container_env_file} ]]; then source ${container_env_file}; fi; ${non_interactive_command}"
fi

docker_args=(
  --rm
  --privileged
  --ipc=host
  --shm-size=1g
  -e "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-0}"
  -e "ROS_LOCALHOST_ONLY=${ros_localhost_only}"
  -e "LD_LIBRARY_PATH=/usr/local/lib:${host_ld_library_path}"
  -w /workspace
  -v "${workspace_dir}:/workspace"
)

if [[ -n "${non_interactive_command}" ]]; then
  docker_args+=(-i)
else
  docker_args+=(-it)
fi

case "${docker_network_mode}" in
  host)
    docker_args+=(--net=host)
    ;;
  host-only|bridge)
    docker_args+=(--network=bridge)
    ;;
  none)
    docker_args+=(--network=none)
    ;;
  *)
    echo "Unsupported NAVIGATION_3D_DOCKER_NETWORK_MODE: ${docker_network_mode}" >&2
    echo "Supported values: host, host-only, bridge, none" >&2
    exit 1
    ;;
esac

if [[ -d "${resource_dir}" ]]; then
  docker_args+=(-v "${resource_dir}:/resource")
fi

if [[ -d "${workspace_config_dir}" ]]; then
  docker_args+=(-v "${workspace_config_dir}:${container_config_dir}:ro")
fi

if [[ -n "${DISPLAY:-}" ]]; then
  docker_args+=(
    -e "DISPLAY=${DISPLAY}"
    -e "QT_X11_NO_MITSHM=1"
  )
fi

if [[ -d /tmp/.X11-unix ]]; then
  docker_args+=(-v /tmp/.X11-unix:/tmp/.X11-unix:rw)
fi

if [[ -n "${XAUTHORITY:-}" && -f "${XAUTHORITY}" ]]; then
  docker_args+=(
    -e "XAUTHORITY=${XAUTHORITY}"
    -v "${XAUTHORITY}:${XAUTHORITY}:ro"
  )
fi

if [[ -d /dev/dri ]]; then
  docker_args+=(--device /dev/dri:/dev/dri)
fi

if command -v nvidia-smi >/dev/null 2>&1; then
  docker_args+=(
    --gpus all
    -e "NVIDIA_VISIBLE_DEVICES=all"
    -e "NVIDIA_DRIVER_CAPABILITIES=all"
    -e "__GLX_VENDOR_LIBRARY_NAME=nvidia"
    -e "__NV_PRIME_RENDER_OFFLOAD=1"
    -e "VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json"
  )
fi

docker run "${docker_args[@]}" "${image_name}" /bin/bash -lc "${shell_command}"
