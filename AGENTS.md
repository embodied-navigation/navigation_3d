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

- Commit 提交信息使用 Conventional Commits 风格，格式为：`<type>: <subject>`。
- `subject` 使用简短、明确的中文描述。

## Pull Request Rules

- Pull Request 标题使用 Conventional Commits 风格。
- Pull Request 描述默认使用 `.github/pull_request_template.md` 模板。
- 使用 AI 工具生成 Pull Request 内容时，应基于 `.github/pull_request_template.md` 模板填写。
- 除非用户明确指定其他目标分支，否则默认目标分支为 `develop`。
- 当变更影响架构、工作流或开发者环境时，需在同一分支中同步更新相关文档。


## C++ Formatting Rules

- 对 C/C++ 相关文件的修改，必须遵循仓库根目录 `.clang-format` 的格式规则。
- 在完成 C/C++ 代码修改后，优先使用 `.clang-format` 对受影响文件进行格式化。
- 不要凭个人习惯调整括号、缩进、换行或对齐方式；以 `.clang-format` 为准。
- 若当前环境无法运行格式化工具，最终说明中必须明确说明未执行格式化。

## Validation

- Run the smallest useful validation for each change.
- If validation cannot run, state that clearly in the final report.
- Avoid changing unrelated files during setup work.
