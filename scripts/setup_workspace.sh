#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"
src_dir="${workspace_root}/src"
default_manifest="${workspace_root}/repos/private.repos"
legacy_manifest="${workspace_root}/base.repos"
manifest_path="${2:-${default_manifest}}"

mkdir -p "${src_dir}"

if [ ! -f "${manifest_path}" ]; then
  if [ "${manifest_path}" = "${default_manifest}" ] && [ -f "${legacy_manifest}" ]; then
    echo "warning: ${default_manifest} not found; falling back to historical manifest ${legacy_manifest}" >&2
    manifest_path="${legacy_manifest}"
  else
    echo "missing manifest: ${manifest_path}" >&2
    exit 1
  fi
fi

vcs import "${src_dir}" < "${manifest_path}"
