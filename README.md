# navigation_3d

`navigation_3d` is the public integration repository for the `embodied-navigation`
organization. It is the current primary development entrypoint for a ROS 2 based 3D
navigation framework targeting legged robots, with an initial focus on quadrupeds and
humanoids.

## Repository Role

This repository is the current integration repository for:

- workspace integration and dependency assembly
- launch and runtime assembly
- Docker-based development environment bootstrap
- project governance, documentation, scripts, and CI
- repository-level version locking across child repositories

Formal implementation now happens in a hybrid model:

- child repositories host active module development
- `navigation_3d` remains the single integration, launch, documentation, environment, and
  validation entrypoint

## Branch Model

This repository follows a `main + develop` model:

- `develop` is the default integration branch for daily work
- `main` is the stable, release-oriented branch
- normal work should start from `develop` using a topic branch
- direct pushes to `main` are not part of the normal workflow

Detailed branch, commit, and PR rules live in [`AGENTS.md`](./AGENTS.md) and
[`CONTRIBUTING.md`](./CONTRIBUTING.md).

## Planned ROS 2 Modules

The long-term repository boundary is centered on these ROS 2 packages:

- `nav_common`
- `nav_protocol`
- `map_manager`
- `slam`
- `perception`
- `planner`
- `controller`
- `task_manager`
- `nav_launch`

The legacy `core/` and `interfaces/` layouts are no longer part of the intended long-term
structure. They have been retired from the active repository shape and are retained only in
historical documentation and commit history.

## Child Repositories

The `embodied-navigation` organization uses dedicated child repositories for active module
development.

Current rule:

- `navigation_3d` is the only formal integration repository
- module development happens in child repositories
- workspace assembly, Docker environment, launch orchestration, CI, and smoke validation are
  still owned by this repository
- `repos/private.repos` is the workspace manifest that pins the active `develop` branches for
  the child repositories participating in the current minimal navigation system
- the current minimal navigation MVP is assembled through `repos/private.repos`
- all child repositories are currently governed through `develop`

See [`docs/repository-plan.md`](./docs/repository-plan.md) for the detailed policy.

## Workspace Sources

The repository uses a `vcstool` manifest under `repos/` as the primary workspace source
entrypoint.

Initial import:

```bash
mkdir -p src
vcs import src < repos/private.repos
```

Update existing sources:

```bash
vcs pull src
```

`repos/private.repos` is the current main source of truth for child repository assembly and
currently pins the active `develop` branches for:

- `nav_protocol`
- `slam`
- `map_manager`
- `planner`
- `controller`
- `nav_launch`

`base.repos` is retained only as a historical compatibility manifest and is no longer the
recommended main entrypoint.

## Development Environment

The standard development environment is Docker-based and centered on Ubuntu 22.04 + ROS 2
Humble. Host-side builds are not the recommended primary workflow.

Build the image:

```bash
./docker/build.sh
```

Run the development shell:

```bash
./docker/run.sh
```

Inside the container, a typical sequence is:

```bash
./scripts/setup_workspace.sh /workspace
./scripts/build_workspace.sh /workspace
./scripts/test.sh
```

`docker/run.sh` mounts the repository as `/workspace`, preserves `ROS_DOMAIN_ID`, forwards
X11 and NVIDIA settings when available, and sources [`env.sh`](./env.sh) on shell entry.

For the DDS shared-memory baseline, the repository provides
[`config/fastdds_shm.xml`](./config/fastdds_shm.xml), which can be used as the default Fast
DDS profile inside the container.

For more detail, see [`docs/development-environment.md`](./docs/development-environment.md).

## CI Flow

The repository follows a two-level CI model:

- child repositories run fast repository-local CI
- `navigation_3d` runs workspace assembly and minimal navigation smoke tests

The detailed process is documented in [`docs/ci-flow.md`](./docs/ci-flow.md).

## Local Commands

Primary helper entrypoints:

```bash
./scripts/configure.sh
./scripts/build.sh
./scripts/test.sh
./scripts/format_check.sh
./scripts/setup_workspace.sh .
```

## Planning And Design Records

Planning and design artifacts live under `docs/superpowers/`:

- `docs/superpowers/plans/`
- `docs/superpowers/specs/`

These records remain useful historical references, but current repository governance and
workspace strategy are defined by the documents in `docs/` and the active root-level
scripts.
