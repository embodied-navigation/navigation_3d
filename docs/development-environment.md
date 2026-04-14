# Development Environment

## Standard Environment

The standard development environment for `navigation_3d` is Docker on Ubuntu 22.04 with ROS 2
Humble.

Current baseline includes:

- Docker-based workspace shell
- `vcstool` for child repository import
- `cmake` / `ctest`
- `clang-format`
- root-level helper scripts for setup, build, and test

## Workspace Bootstrap

Create or refresh the workspace sources:

```bash
mkdir -p src
vcs import src < repos/private.repos
```

Refresh existing sources:

```bash
vcs pull src
```

You can also use the repository helper script:

```bash
./scripts/setup_workspace.sh .
```

## Docker Workflow

Build the image:

```bash
./docker/build.sh
```

Enter the development shell:

```bash
./docker/run.sh
```

Inside the container:

```bash
./scripts/setup_workspace.sh /workspace
./scripts/build_workspace.sh /workspace
./scripts/test.sh
```

## Notes

- Docker is the standard environment for setup, build, and test
- `docker/run.sh` defaults to host-only ROS 2 networking (`ROS_LOCALHOST_ONLY=1` plus
  Docker `bridge` networking); use `NAVIGATION_3D_DOCKER_NETWORK_MODE=host` only when you
  intentionally need LAN discovery
- host-side builds are not the preferred default
- `base.repos` is retained only for historical compatibility and should not be used as the
  primary source import entrypoint for new workflows
