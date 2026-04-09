# AGENTS.md

## Purpose
This repository is for building `navigation_3d` using a lightweight planning-first workflow inspired by the user's superpower workflow.

## Project Structure

- **`docker/`**: 存放构建 Docker 镜像和进入 Docker 环境的脚本。
- **`scripts/`**: 存放编译和打包工程的脚本；工程编译需在 Docker 环境中进行。
- **`src/`**: 存放工程核心源代码。

## Branch Rules

- Base normal development on `develop`.
- Treat `main` as stable and release-oriented.
- Do not push directly to `main` unless the user explicitly requests it.
- Prefer topic branches over committing directly on `develop`.
- Use branch names in the form `<type>/<short-kebab-description>`.
- Allowed branch types: `feature`, `fix`, `docs`, `refactor`, `test`, `chore`, `release`.
- Examples: `feature/bootstrap-engineering-foundation`, `fix/traversability-empty-grid`, `docs/update-architecture-notes`.
- Keep changes small, reviewable, and easy to validate.

## Commit Rules

- 使用 Conventional Commits 格式：`<type>: <subject>`。
- 允许的 `type`：`feat`, `fix`, `docs`。
- `<subject>` 要简短、使用祈使语气且表达具体（例如：`feat: 新增局部规划器open_planner`）。

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
