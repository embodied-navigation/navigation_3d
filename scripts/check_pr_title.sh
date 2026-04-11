#!/usr/bin/env bash
set -euo pipefail

pr_title="${1:-}"

if [ -z "${pr_title}" ]; then
  echo "pull request title is required" >&2
  exit 1
fi

if [[ "${pr_title}" =~ ^(feat|fix|docs|refactor|style|test|chore)(\([a-z0-9_-]+\))?!?:\ .+ ]]; then
  exit 0
fi

echo "invalid pull request title: ${pr_title}" >&2
echo "expected Conventional Commits, for example: feat: 新增工程基础能力" >&2
exit 1
