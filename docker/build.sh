#!/usr/bin/env bash
set -euo pipefail

docker build -t navigation_3d:humble-dev -f docker/Dockerfile .
