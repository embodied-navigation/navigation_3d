#!/usr/bin/env bash
set -euo pipefail

image_name="${NAVIGATION_3D_IMAGE:-navigation_3d:humble-dev}"
workspace_dir="$(pwd)"
resource_dir="${HOME}/resource"
host_ld_library_path="${LD_LIBRARY_PATH:-}"

docker_args=(
  --rm
  --privileged
  -it
  --net=host
  -e "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-0}"
  -e "LD_LIBRARY_PATH=/usr/local/lib:${host_ld_library_path}"
  -w /workspace
  -v "${workspace_dir}:/workspace"
)

if [[ -d "${resource_dir}" ]]; then
  docker_args+=(-v "${resource_dir}:/resource")
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

docker run "${docker_args[@]}" "${image_name}" /bin/bash
