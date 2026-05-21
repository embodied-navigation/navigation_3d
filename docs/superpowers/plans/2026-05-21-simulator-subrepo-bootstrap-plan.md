# Simulator Subrepo Bootstrap Plan

## Objective

将当前通过拷贝方式引入的 `src/simulator` 目录转换为独立子仓库，
并在本次开发周期内完成子仓库与主仓库的双仓提交收尾。

## Background

- 当前主仓库通过 `.gitignore` 规则忽略 `src/*`。
- `src/simulator` 已包含大量仿真相关源码与运行产物目录。
- 需要将其整理为可独立演进、可独立提交的子仓库。

## Plan

1. 在 `src/simulator` 初始化 Git 仓库。
2. 增加子仓库级 `.gitignore`，过滤 `build/`、`install/`、`log/` 等产物。
3. 完成子仓库首个初始化提交（包含当前有效源码与文档）。
4. 在主仓库补充本计划文档并提交，记录本轮子仓库化决策与交付。

## Validation

- 子仓库执行 `git status` 为 clean。
- 子仓库存在首个提交记录。
- 主仓库存在本计划与收尾文档提交记录。

## Deliverables

- 子仓库：`src/simulator` 的独立提交历史。
- 主仓库：本计划文档与本轮收尾文档的提交记录。

## Status

- 2026-05-21：计划创建，进入执行。
