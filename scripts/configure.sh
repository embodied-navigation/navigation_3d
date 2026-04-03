#!/usr/bin/env bash
set -euo pipefail

if command -v ninja >/dev/null 2>&1; then
  cmake -S . -B build -G Ninja
else
  cmake -S . -B build -G "Unix Makefiles"
fi
