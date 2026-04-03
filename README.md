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
- `core/`, `interfaces/`, and `tests/` as the initial module layout

## Product Direction

The framework is intended to support robots that cannot rely on flat-ground 2D navigation assumptions. The initial target is a reusable stack for:

- 3D environment representation
- traversability analysis for legged robots
- global and local planning in uneven terrain
- interfaces that can be adapted to both quadrupeds and humanoids

## Current Status

The repository is intentionally minimal and is currently in the definition and architecture stage.

## Local Commands

Typical local workflow:

```bash
./scripts/configure.sh
./scripts/build.sh
./scripts/test.sh
./scripts/format_check.sh
```
