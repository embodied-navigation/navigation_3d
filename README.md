# navigation_3d

`navigation_3d` 是 `embodied-navigation` 组织的公开集成仓库，也是基于 ROS 2 的三维导航框架的主要开发入口，目标平台为腿足机器人，当前重点支持四足机器人与人形机器人。

## 仓库职责

本仓库承担以下集成职责：

- 工作空间集成与依赖组装
- 启动（launch）与运行时编排
- 基于 Docker 的开发环境引导
- 项目治理、文档、脚本与 CI
- 跨子仓库的版本锁定

当前采用混合开发模型：

- 子仓库负责各模块的主动开发
- `navigation_3d` 保持为唯一的集成、启动、文档、环境与验证入口

## 分支模型

本仓库遵循 `main + develop` 模型：

- `develop` 是日常工作的默认集成分支
- `main` 是稳定的面向发布的分支
- 常规工作应从 `develop` 创建主题分支开始
- 不建议直接向 `main` 推送提交

详细的分支、提交与 PR 规则请参见 [`AGENTS.md`](./AGENTS.md) 和 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。

## 规划中的 ROS 2 模块

仓库长期边界围绕以下 ROS 2 包展开：

- `nav_common`
- `nav_protocol`
- `map_manager`
- `slam`
- `perception`
- `planner`
- `controller`
- `task_manager`
- `nav_launch`

旧有的 `core/` 和 `interfaces/` 目录结构已不再是预期的长期架构，已从活跃仓库中退役，仅保留在历史文档和提交记录中。

## 子仓库

`embodied-navigation` 组织使用专属子仓库进行各模块的主动开发。

当前规则：

- `navigation_3d` 是唯一的正式集成仓库
- 模块开发在子仓库中进行
- 工作空间组装、Docker 环境、launch 编排、CI 和冒烟验证仍由本仓库负责
- `repos/private.repos` 是工作空间清单，用于锁定参与当前最小导航系统的子仓库的 `develop` 分支
- 当前最小导航 MVP 通过 `repos/private.repos` 组装
- 所有子仓库当前均通过 `develop` 分支治理

详细策略请参见 [`docs/repository-plan.md`](./docs/repository-plan.md)。

## 工作空间源

仓库使用 `repos/` 目录下的 `vcstool` 清单作为主要工作空间源入口。

初次导入：

```bash
mkdir -p src
vcs import src < repos/private.repos
```

更新已有源码：

```bash
vcs pull src
```

`repos/private.repos` 是子仓库组装的当前主要依据，当前锁定以下模块的 `develop` 分支：

- `nav_protocol`
- `slam`
- `map_manager`
- `planner`
- `controller`
- `nav_launch`

`base.repos` 仅作为历史兼容清单保留，不再是推荐的主要入口。

## 开发环境

标准开发环境基于 Docker，以 Ubuntu 22.04 + ROS 2 Humble 为基础，不推荐在宿主机直接构建。

构建镜像：

```bash
./docker/build.sh
```

进入开发容器：

```bash
./docker/run.sh
```

在容器内，典型操作序列如下：

```bash
./scripts/setup_workspace.sh /workspace
./scripts/build_workspace.sh /workspace
./scripts/test.sh
```

`docker/run.sh` 会将仓库挂载为 `/workspace`，默认使用仅本机 ROS 2 网络模式（`ROS_LOCALHOST_ONLY=1`，Docker `bridge` 网络），保留 `ROS_DOMAIN_ID`，并在可用时转发 X11 和 NVIDIA 配置，容器启动时自动 source [`env.sh`](./env.sh)。

DDS 共享内存基线配置请参见 [`config/fastdds_shm.xml`](./config/fastdds_shm.xml)，可在容器内作为默认 Fast DDS profile 使用。

更多详情请参见 [`docs/development-environment.md`](./docs/development-environment.md)。

## CI 流程

本仓库采用两级 CI 模型：

- 子仓库运行快速的仓库本地 CI
- `navigation_3d` 运行工作空间组装与最小导航冒烟测试

详细流程文档请参见 [`docs/ci-flow.md`](./docs/ci-flow.md)。

## 周报评审

本仓库还运行每周 AI 辅助评审摘要，汇总 `navigation_3d` 及所有子仓库的开放 PR 与仓库健康状态。

- 周报指南：[`docs/weekly-review.md`](./docs/weekly-review.md)
- 工作流：[`.github/workflows/weekly-review.yml`](./.github/workflows/weekly-review.yml)
- 输出：Markdown 邮件 + JSON 制品

## 发布说明

发布说明基于 tag 范围和 Conventional Commits 自动生成。

- 生成规则：[`docs/release-notes.md`](./docs/release-notes.md)
- 生成脚本：[`scripts/release_notes.py`](./scripts/release_notes.py)
- 滚动变更日志：[`CHANGELOG.md`](./CHANGELOG.md)

## 本地命令

主要辅助入口：

```bash
./scripts/build_workspace.sh .
./scripts/test.sh
./scripts/test_minimal_navigation.sh .
./scripts/format_check.sh
./scripts/setup_workspace.sh .
```

## 启动 MVP 导航栈

### 仅后台节点（无可视化）

```bash
source install/setup.bash
ros2 launch nav_launch minimal_navigation.launch.py
```

### 带 RViz 可视化

```bash
source install/setup.bash
ros2 launch nav_launch minimal_navigation_rviz.launch.py
```

此命令会启动完整 MVP 栈（地图服务、costmap lifecycle 节点、控制器）并自动打开 RViz2，加载预配置的 `minimal_navigation.rviz`（含地图、局部代价地图显示）。

> **前提**：需在容器内执行，且宿主机已配置 X11 转发（`docker/run.sh` 默认已处理 `DISPLAY` 与 X11 socket 挂载）。

## 规划与设计记录

规划和设计产出物存放在 `docs/superpowers/` 目录下：

- `docs/superpowers/plans/`
- `docs/superpowers/specs/`

这些记录是有价值的历史参考，但当前仓库治理和工作空间策略以 `docs/` 中的文档和根目录脚本为准。
