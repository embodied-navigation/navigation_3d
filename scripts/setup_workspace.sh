#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"
src_dir="${workspace_root}/src"
manifest_path="${workspace_root}/base.repos"

mkdir -p "${src_dir}"

if [ ! -f "${manifest_path}" ]; then
  echo "missing manifest: ${manifest_path}" >&2
  exit 1
fi

vcs import "${src_dir}" < "${manifest_path}"
