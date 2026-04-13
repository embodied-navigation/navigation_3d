# Repository Plan

## Purpose

This document defines the current repository governance and workspace strategy for
`navigation_3d`.

## Current Repository Model

`navigation_3d` is the integration repository in the `embodied-navigation` organization at
the current stage.

The matching child repositories already exist:

- `nav_common`
- `nav_protocol`
- `map_manager`
- `slam`
- `perception`
- `planner`
- `controller`
- `task_manager`
- `nav_launch`

Current status:

- `nav_protocol`, `slam`, `map_manager`, `planner`, `controller`, and `nav_launch` are active
  development repositories for the current MVP
- `nav_common`, `perception`, and `task_manager` remain reserved for later stages
- `navigation_3d` continues to own integration, launch, environment, CI, and version locking

## Branch Strategy

- `develop` is the default integration branch
- `main` is the stable branch
- normal development should happen through topic branches based on `develop`
- `main` must remain release-oriented
- repository protection should prevent direct pushes to `main`
- `develop` should also be protected so that integration happens through pull requests

## Workspace Source Strategy

The current workspace source manifest entrypoint is:

```bash
vcs import src < repos/private.repos
```

Update existing child repositories with:

```bash
vcs pull src
```

`repos/private.repos` is the current main source of truth for child repository assembly and
pins the active MVP branches for the child repositories participating in the current
minimal navigation system.

`base.repos` remains only as a historical compatibility manifest from the earlier bootstrap
phase and is no longer the recommended main workflow entrypoint.

## Development Environment

The standard development environment is Docker-based.

Current policy:

- workspace setup, build, and test should run in Docker by default
- host-side builds are not the standard supported workflow
- root-level helper scripts are the official entrypoints for setup, build, test, and format
  validation

## Legacy Layout Policy

The previous `core/` and `interfaces/` layouts are no longer part of the active repository
shape. They should not be used as the basis for current architecture or repository planning.

Current policy:

- do not add new code under the old layout
- do not describe the old layout as the long-term repository structure
- keep migration planning separate from implementation work

## Current Multi-Repository Rule

The active rule is:

- child repositories own module implementation
- `navigation_3d` owns system assembly and validation
- a child repository change is not complete until the main repository updates
  `repos/private.repos` and the Docker-based smoke test passes

## Future Migration Direction

The next repository structure target is expected to center on these ROS 2 packages under
`src/`:

- `src/nav_common`
- `src/nav_protocol`
- `src/map_manager`
- `src/slam`
- `src/perception`
- `src/planner`
- `src/controller`
- `src/task_manager`
- `src/nav_launch`

The next modules expected to become active repositories are `perception` and `task_manager`,
but they are intentionally not part of the current minimal navigation MVP.
