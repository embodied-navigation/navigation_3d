# docker

本目录存放构建与启动开发/仿真容器的脚本。

## 脚本概览

- `build.sh`：构建开发或仿真镜像。
- `run.sh`：启动导航开发容器（镜像 `navigation_3d:${IMAGE_VERSION_NAV}`，版本从 `IMAGE_VERSION_NAV` 文件读取）。
- `run_sim.sh`：启动仿真容器（镜像 `simulator_3d:${IMAGE_VERSION_SIM}`，版本从 `IMAGE_VERSION_SIM` 文件读取）。

## 参数传递方式

`run.sh` 与 `run_sim.sh` 都通过 **环境变量** 接收可选参数，不接受位置参数。统一形式：

```bash
VAR="${VAR:-default}"
```

若调用方未设置或设置为空，则使用默认值；否则沿用调用方提供的值，并通过 `-e VAR=...` 注入容器。

## 通用环境变量

### `ROS_DOMAIN_ID`

控制容器内 ROS 2 节点的 domain ID（同一 domain 才能相互发现）。

| 调用方式 | 容器内最终 `ROS_DOMAIN_ID` |
|---|---|
| `./run.sh` / `./run_sim.sh`（未设环境变量） | `0` |
| `ROS_DOMAIN_ID=42 ./run.sh` | `42` |
| `export ROS_DOMAIN_ID=7; ./run_sim.sh` | `7` |
| `ROS_DOMAIN_ID= ./run.sh`（空值） | `0`（`:-` 把空值视为未设置） |

> **提示**：多人共用同一局域网时，应为各自项目选择不同的 `ROS_DOMAIN_ID`，避免 ROS 2 节点跨项目相互发现。建议取值范围 `0–101`。

## `run.sh` 专用环境变量

### `ACCEL_MODE`

控制是否向容器透传 NVIDIA GPU（`--gpus all` 等参数）。

| 调用方式 | 容器内行为 |
|---|---|
| `./run.sh`（未设环境变量） | `cpu`，不透传 GPU |
| `ACCEL_MODE=gpu ./run.sh` | 启用 GPU 透传 |
| `ACCEL_MODE=cpu ./run.sh` | 显式禁用 GPU 透传 |

非 `cpu`/`gpu` 取值会被脚本拒绝并退出。

### 组合示例

```bash
ROS_DOMAIN_ID=42 ACCEL_MODE=gpu ./docker/run.sh
```
