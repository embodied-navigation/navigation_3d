#!/usr/bin/env bash
set -euo pipefail

commit_msg_file="${1:-}"

if [ -z "${commit_msg_file}" ] || [ ! -f "${commit_msg_file}" ]; then
  echo "commit message file is required" >&2
  exit 1
fi

first_line="$(head -n 1 "${commit_msg_file}")"

if [[ "${first_line}" =~ ^(feat|fix|docs|refactor|style|test|chore)(\([a-z0-9_-]+\))?!?:\ [a-z0-9] ]]; then
  exit 0
fi

echo "invalid commit message: ${first_line}" >&2
echo "expected Conventional Commits, for example: feat: add world model interface" >&2
exit 1
