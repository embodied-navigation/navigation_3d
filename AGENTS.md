# AGENTS.md

## Purpose

This repository is for building `navigation_3d` using a lightweight planning-first workflow inspired by the user's superpower workflow.

## Branch Rules

- Base normal development on `develop`.
- Treat `main` as stable and release-oriented.
- Do not push directly to `main` unless the user explicitly requests it.
- Prefer topic branches over committing directly on `develop`.
- Use branch names in the form `<type>/<short-kebab-description>`.
- Allowed branch types: `feature`, `fix`, `docs`, `refactor`, `test`, `chore`, `release`.
- Examples: `feature/bootstrap-engineering-foundation`, `fix/traversability-empty-grid`, `docs/update-architecture-notes`.
- Keep changes small, reviewable, and easy to validate.

## Working Style

- Read the repository state before making structural decisions.
- Prefer minimal, direct changes over speculative refactors.
- Record meaningful planning decisions in `docs/superpowers/plans/`.
- Record design choices, assumptions, and technical tradeoffs in `docs/superpowers/specs/`.
- Update `README.md` when the setup or workflow changes materially.

## Documentation Rules

- Create one plan file per meaningful task or milestone.
- Keep plan files short and action-oriented.
- Write specs only when a design choice, interface, or architecture needs to be preserved.
- Prefer dated file names so the history stays searchable.

## Validation

- Run the smallest useful validation for each change.
- If validation cannot run, state that clearly in the final report.
- Avoid changing unrelated files during setup work.

## Pull Request Rules

- Follow the PR rules defined in `CONTRIBUTING.md`.
- Use Conventional Commits style PR titles.
- Target `develop` unless the user explicitly asks for another base branch.
- When a change affects architecture, workflow, or developer setup, update the relevant docs in the same branch.
