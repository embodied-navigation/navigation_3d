#!/usr/bin/env bash
set -euo pipefail

if ! command -v clang-format >/dev/null 2>&1; then
  echo "clang-format not found; install it locally or run the check in Docker/CI." >&2
  exit 1
fi

files=$(find core tests -type f \( -name '*.hpp' -o -name '*.cpp' \))

if [ -z "${files}" ]; then
  exit 0
fi

clang-format --dry-run --Werror ${files}
