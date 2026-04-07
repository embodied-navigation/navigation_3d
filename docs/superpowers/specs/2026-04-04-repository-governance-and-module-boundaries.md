# Repository Governance And Module Boundaries

## Purpose

Define how `navigation_3d` should be organized as a long-lived engineering repository while the architecture is still evolving.

## Recommended Repository Model

Use a single main repository, `navigation_3d`, as the integration and governance root.

Within that repository, organize the system as top-level modules rather than immediately splitting into multiple git repositories.

Recommended top-level modules:

- `slam/`
- `perceptor/`
- `pnc/`
- `nav_protocol/`
- `nav_launch/`
- `nav_common/`
- `docs/`
- `docker/`
- `scripts/`
- `.github/`

## Why Not Split Into Multiple Repositories Yet

At the current stage, interfaces between perception, mapping, traversability, planning, and system launch are still evolving. Splitting them into separate repositories too early would increase:

- version synchronization cost
- cross-repository pull request coordination
- CI complexity
- integration friction during architecture changes

The repository should therefore behave as a monorepo for now, even if the internal module boundaries are designed as if some of them may later become independent repositories.

## Module Responsibilities

### `slam/`

- localization and mapping
- robot pose estimation inputs to navigation
- map production for downstream consumers

`slam/` should not depend on `pnc/`.

### `perceptor/`

- terrain perception
- obstacle extraction
- semantic or geometric environment understanding

`perceptor/` should provide environment information without depending on planning logic.

### `pnc/`

- navigation-relevant planning and control bridge logic
- route planning, local motion decision layers, and execution-facing planning outputs

This module should stay scoped to navigation-related planning and command generation. It should not silently expand into full-body locomotion control without an explicit architecture decision.

### `nav_protocol/`

- interface contracts
- message schemas
- service definitions
- actions, enums, shared status codes, and stable data contracts

This module should stay stable and lightweight. Avoid placing business logic here.

### `nav_launch/`

- launch files
- runtime composition
- parameter orchestration
- development and deployment entry points

`nav_launch/` is an integration layer and may depend on other modules. Other modules should not depend on it.

### `nav_common/`

- shared utility code
- configuration helpers
- common data types with low business coupling
- math and geometry helpers that are broadly reusable
- logging and error-handling wrappers

This module must be kept narrow. It should not become a dumping ground for unrelated code.

## Dependency Direction Rules

Recommended dependency constraints:

- `nav_protocol/` should have minimal dependencies
- `nav_common/` should have minimal dependencies
- `slam/`, `perceptor/`, and `pnc/` may depend on `nav_protocol/` and `nav_common/`
- `nav_launch/` may depend on all runtime modules
- `slam/` must not depend on `pnc/`
- `perceptor/` must not depend on `pnc/`
- `pnc/` may consume outputs produced by `slam/` and `perceptor/`, preferably through stable contracts
- no module should depend on `nav_launch/`

## Governance Rules

- keep `navigation_3d` as the single source of truth for system integration
- evolve module boundaries in-tree first
- only split a module into a separate repository after its interface and release cadence are stable
- document boundary changes in `docs/superpowers/specs/`
- prefer changes that reduce cross-module coupling, even if they add a small amount of adapter code

## Conditions For Future Repository Extraction

A top-level module may be considered for extraction into its own repository only if most of the following are true:

- its interface contract is stable
- it has an independent release lifecycle
- it is reused outside `navigation_3d`
- it can be versioned without tightly synchronized changes in other modules
- CI and integration tests can be expressed cleanly across repository boundaries

## Suggested Next Step

Adopt this top-level module layout inside `navigation_3d`, then define which of those modules should become ROS 2 packages, libraries, or pure interface/configuration directories.
