# Contributing

## Branching

- Base new work on `develop`.
- Prefer topic branches instead of working directly on `develop`.
- Name branches as `<type>/<short-kebab-description>`.
- Allowed branch types: `feature`, `fix`, `docs`, `refactor`, `test`, `chore`, `release`.
- Examples:
  - `feature/bootstrap-engineering-foundation`
  - `fix/world-model-bounds-check`
  - `docs/add-planning-workflow`
- Merge stable release-ready work into `main`.

## Commits

Use Conventional Commits:

- `feat:`
- `fix:`
- `docs:`
- `refactor:`
- `style:`
- `test:`
- `chore:`

Examples:

- `feat: add traversability scoring interface`
- `fix: handle empty terrain patch in planner`
- `style: align headers with clang-format`

Commit titles may also use an optional scope:

- `feat(world_model): add terrain query interface`
- `fix(traversability): guard empty support region`
- `style(global_planner): normalize include order`

## Pull Requests

- Keep pull requests focused.
- Describe the motivation, technical approach, and validation.
- Link to related plan or spec documents when the change affects architecture.
- Avoid mixing refactors with feature delivery unless required.
- Use a Conventional Commits style PR title such as `feat: ...`, `fix: ...`, or `docs: ...`.
- Target `develop` for normal development work.
- Prefer `Squash and merge` so `develop` keeps a clean history.
- Delete merged topic branches after the PR lands.

Recommended PR description structure:

- `Summary`
- `Scope`
- `Validation`
- `Follow-up`

## Validation

Before opening a pull request, run the smallest relevant checks available for the change:

- formatting
- static checks
- build
- tests

For architecture or workflow changes, also update the related docs:

- `docs/superpowers/specs/`
- `AGENTS.md`
- `README.md`

## Automated Checks

The repository runs policy checks in GitHub Actions for:

- branch naming
- commit message format
- pull request title format

The same checks live in `scripts/` so they can also be reused locally later.
