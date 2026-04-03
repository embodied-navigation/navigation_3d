#!/usr/bin/env bash
set -euo pipefail

branch_name="${1:-}"

if [ -z "${branch_name}" ]; then
  echo "branch name is required" >&2
  exit 1
fi

if [ "${branch_name}" = "main" ] || [ "${branch_name}" = "develop" ]; then
  exit 0
fi

if [[ "${branch_name}" =~ ^(feature|fix|docs|refactor|test|chore|release)/[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  exit 0
fi

echo "invalid branch name: ${branch_name}" >&2
echo "expected: <type>/<short-kebab-description>" >&2
echo "allowed types: feature, fix, docs, refactor, test, chore, release" >&2
exit 1
