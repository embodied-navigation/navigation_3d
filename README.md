# navigation_3d

`navigation_3d` is a repository for developing a 3D navigation framework for legged robots, with an initial focus on quadrupeds and humanoids.

## Workflow

This repository uses a simple `main + develop` branch model:

- `develop` is the default integration branch for daily development.
- `main` is reserved for stable, release-ready states.
- New work should start from `develop` and land through focused commits or pull requests.

The repository also keeps planning and design artifacts under `docs/superpowers/`:

- `docs/superpowers/plans/` for short task plans
- `docs/superpowers/specs/` for implementation and design notes

Agent and contributor instructions live in `AGENTS.md`.

## Engineering Baseline

The repository now includes a first-pass engineering baseline for repeatable development:

- `.clang-format`, `.clang-tidy`, `.editorconfig`
- `CONTRIBUTING.md` with commit and branch rules
- `docker/` for a reproducible dev environment
- `.github/workflows/ci.yml` for format, build, and test automation
- `docs/superpowers/` for task plans and design records
- `base.repos` plus `scripts/setup_workspace.sh` and `scripts/build_workspace.sh` for workspace bootstrapping

The long-lived repository boundary is being defined as a single integration root with top-level modules such as `slam/`, `perceptor/`, `pnc/`, `nav_protocol/`, `nav_launch/`, and `nav_common/`. The current `core/`, `interfaces/`, and `tests/` directories remain part of the bootstrap-stage layout while that boundary is still evolving.

## Product Direction

The framework is intended to support robots that cannot rely on flat-ground 2D navigation assumptions. The initial target is a reusable stack for:

- 3D environment representation
- traversability analysis for legged robots
- global and local planning in uneven terrain
- interfaces that can be adapted to both quadrupeds and humanoids

## Current Status

The repository is intentionally minimal and is currently in the definition and architecture stage.

## Local Commands

Use the helper scripts from the repository root. Workspace compilation and testing should run inside Docker rather than directly on the host.

Typical command entrypoints:

```bash
./scripts/configure.sh
./scripts/build.sh
./scripts/test.sh
./scripts/format_check.sh
```

## Workspace Sources

This repository can also be used as the root of a workspace source manifest.

- `base.repos` contains the minimal source set for the current stage

Typical usage with `vcstool`:

```bash
mkdir -p src
vcs import src < base.repos
```

Treat `navigation_3d` itself as the workspace root directory, then run:

```bash
./scripts/setup_workspace.sh .
./scripts/build_workspace.sh .
```

## Phase 1 SLAM Integration

The first validation phase treats an external ROS 2 SLAM system as the primary functional target.

Current external source:

- `lightning-lm` via [`base.repos`](/home/csp/workspace/gaojie_ws/navigation_3d/base.repos)

Recommended workspace layout:

```text
navigation_3d/
  base.repos
  src/
    lightning_lm/
  docker/
  scripts/
  docs/
```

## Docker Workflow

The Docker environment is the default place for ROS 2 Humble workspace development, compilation, testing, and SLAM validation. Avoid running `colcon build` or `colcon test` on the host unless you intentionally want to debug a host-only issue.

Build the image:

```bash
./docker/build.sh
```

Run a shell with `navigation_3d` mounted as `/workspace`:

```bash
./docker/run.sh
```

`docker/run.sh` automatically mounts `${HOME}/resource` to `/resource` when that directory exists, preserves `ROS_DOMAIN_ID`, and forwards X11 and NVIDIA settings when the host environment provides them.

Inside the container, a typical sequence is:

```bash
./scripts/setup_workspace.sh /workspace
./scripts/build_workspace.sh /workspace
./scripts/run_lightning_demo.sh /workspace
```
