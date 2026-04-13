#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"
manifest_path="${2:-${workspace_root}/repos/private.repos}"
src_dir="${workspace_root}/src"

if [[ ! -f "${manifest_path}" ]]; then
  echo "missing manifest: ${manifest_path}" >&2
  exit 1
fi

if [[ ! -d "${src_dir}" ]]; then
  echo "missing workspace src directory: ${src_dir}" >&2
  exit 1
fi

mapfile -t repo_versions < <(
  python3 - "${manifest_path}" <<'PY'
import sys
from pathlib import Path

import yaml

manifest_path = Path(sys.argv[1])
data = yaml.safe_load(manifest_path.read_text())

for name, spec in data.get("repositories", {}).items():
    print(f"{name}\t{spec['version']}")
PY
)

for entry in "${repo_versions[@]}"; do
  repo_name="${entry%%$'\t'*}"
  repo_version="${entry#*$'\t'}"
  repo_path="${src_dir}/${repo_name}"

  if [[ ! -d "${repo_path}/.git" ]]; then
    echo "skip ${repo_name}: not a git repository at ${repo_path}" >&2
    continue
  fi

  if [[ -n "$(git -C "${repo_path}" status --porcelain)" ]]; then
    echo "skip ${repo_name}: working tree is dirty" >&2
    continue
  fi

  echo "sync ${repo_name} -> ${repo_version}"
  git -C "${repo_path}" fetch --all --prune

  if git -C "${repo_path}" ls-remote --heads origin "${repo_version}" | grep -q .; then
    git -C "${repo_path}" checkout -B "${repo_version}" "origin/${repo_version}"
    git -C "${repo_path}" branch --set-upstream-to="origin/${repo_version}" "${repo_version}" >/dev/null 2>&1 || true
    continue
  fi

  if git -C "${repo_path}" ls-remote --tags origin "${repo_version}" | grep -q .; then
    git -C "${repo_path}" checkout "${repo_version}"
    continue
  fi

  if [[ "${repo_version}" =~ ^[0-9a-f]{7,40}$ ]]; then
    git -C "${repo_path}" checkout --detach "${repo_version}"
    continue
  fi

  git -C "${repo_path}" checkout "${repo_version}"
done
