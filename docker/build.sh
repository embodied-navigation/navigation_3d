#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_VERSION_NAV="$(<"${ROOT_DIR}/docker/IMAGE_VERSION_NAV")"
IMAGE_VERSION_SIM="$(<"${ROOT_DIR}/docker/IMAGE_VERSION_SIM")"
TARGET="${1:-nav}"

build_nav() {
    docker build \
        -t "navigation_3d:${IMAGE_VERSION_NAV}" \
        -t "navigation_3d:current" \
        --build-arg IMAGE_VERSION="${IMAGE_VERSION_NAV}" \
        -f "${ROOT_DIR}/docker/Dockerfile" \
        "${ROOT_DIR}"
}

build_sim() {
    docker build \
        -t "simulator_3d:${IMAGE_VERSION_SIM}" \
        -t "simulator_3d:current" \
        --build-arg IMAGE_VERSION="${IMAGE_VERSION_SIM}" \
        -f "${ROOT_DIR}/docker/Dockerfile.sim" \
        "${ROOT_DIR}"
}

case "${TARGET}" in
    nav)
        build_nav
        ;;
    sim)
        build_sim
        ;;
    all)
        build_nav
        build_sim
        ;;
    *)
        echo "Usage: $0 [nav|sim|all]" >&2
        exit 1
        ;;
esac