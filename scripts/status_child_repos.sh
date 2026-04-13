#!/usr/bin/env bash
set -euo pipefail

workspace_root="${1:-$(pwd)}"
src_dir="${workspace_root}/src"
manifest_path="${2:-${workspace_root}/repos/private.repos}"

if [[ ! -d "${src_dir}" ]]; then
  echo "missing workspace src directory: ${src_dir}" >&2
  exit 1
fi

if [[ ! -f "${manifest_path}" ]]; then
  echo "missing manifest: ${manifest_path}" >&2
  exit 1
fi

mapfile -t repo_names < <(
  python3 - "${manifest_path}" <<'PY'
import sys
from pathlib import Path

import yaml

manifest_path = Path(sys.argv[1])
data = yaml.safe_load(manifest_path.read_text())

for name in data.get("repositories", {}):
    print(name)
PY
)

for repo_name in "${repo_names[@]}"; do
  repo_path="${src_dir}/${repo_name}"
  if [[ ! -d "${repo_path}/.git" ]]; then
    printf '%-16s %-12s %s\n' "${repo_name}" "missing" "${repo_path}"
    continue
  fi

  branch="$(git -C "${repo_path}" branch --show-current || true)"
  if [[ -z "${branch}" ]]; then
    branch="DETACHED"
  fi

  upstream="$(git -C "${repo_path}" rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)"
  if [[ -z "${upstream}" ]]; then
    upstream="-"
  fi

  dirty="$(git -C "${repo_path}" status --porcelain | wc -l | tr -d ' ')"
  if [[ "${dirty}" != "0" ]]; then
    dirty="dirty:${dirty}"
  else
    dirty="clean"
  fi

  printf '%-16s %-12s %-28s %s\n' "${repo_name}" "${branch}" "${upstream}" "${dirty}"
done
