# Webots Go2 RL Locomotion Integration Plan

## Objective

在 Webots 仿真中集成 Unitree Go2 四足机器人，使用已训练的 RL 步态 policy
（`policy.onnx`）驱动底层运动控制，对外暴露标准 `/cmd_vel` 接口，与
`navigation_3d` 导航栈对接。

详细设计见：
`docs/superpowers/specs/2026-05-21-webots-go2-rl-locomotion-design.md`

## Constraints

- Policy 已训练完成，不修改步态算法
- 控制频率必须保持 50 Hz（与真机 deploy 一致）
- 所有 Go2 仿真代码集中在 `webots_ros2_go2` 包内
- 物理参数必须对齐 Isaac Lab 训练配置（见 spec）

## Implementation Steps

### Phase 1 — 静态模型（目标：Go2 出现在 Webots 场景中）

1. **URDF → Webots PROTO**
   - 输入：`unitree_ros/robots/go2_description/urdf/go2_description.urdf`
   - 工具：`ros2 run webots_ros2_importer urdf2webots`
   - 手动补充：每个关节加 `friction 0.01`

2. **新建 `webots_ros2_go2` 包骨架**
   - `package.xml` / `CMakeLists.txt`
   - 目录：`resource/`, `worlds/`, `webots_ros2_go2/`, `config/`, `launch/`
   - 验证：`colcon build --packages-select webots_ros2_go2` 通过

3. **创建平地仿真场景 `go2_flat.wbt`**
   - 放入 Go2 PROTO 实例
   - 地面 `coulombFriction 1.0`, `bounce 0.0`
   - 验证：Webots 打开，Go2 静止不塌陷

### Phase 2 — 传感器/执行器桥接（目标：ROS2 收到关节状态和 IMU）

4. **实现 `go2_driver.py`**（webots_ros2_driver 插件）
   - 50 Hz 控制循环（`basicTimeStep=1ms`，每 20 步触发）
   - 发布 `/go2/joint_states`（12 关节，URDF 顺序）
   - 发布 `/go2/imu`
   - 订阅 `/go2/joint_commands` 写关节目标位置
   - 发布 `/go2/odom`（Webots GPS 地面真值）
   - 验证：`ros2 topic echo /go2/joint_states` 有数据

5. **编写 Phase 2 版 `go2_launch.py`**（只启动 Webots + driver）

### Phase 3 — RL Policy 推理（目标：Go2 能站立并响应 cmd_vel）

6. **实现 `rl_policy_node.py`**
   - 加载 `deploy.yaml` + `policy.onnx`（onnxruntime）
   - 构建 45 维 obs 向量（见 spec）
   - 严格按 `joint_ids_map=[3,0,9,6,4,1,10,7,5,2,11,8]` 重排关节
   - 50 Hz 推理，发布 `/go2/joint_commands`
   - **先单独测试重排逻辑**（不启动 Webots，用假数据验证）
   - 验证：零速指令，Go2 原地站立稳定 ≥ 10 秒

7. **物理参数调优**
   - 按 spec 中参数表对齐 PROTO 物理属性
   - 验证：`lin_vel_x=0.3`，Go2 能平稳前进

### Phase 4 — 接入 navigation_3d（目标：Go2 完成自主导航）

8. **配置 Nav2 参数**
   - `robot_radius`, `max_vel_x=1.0`, `max_vel_y=0.4`, `max_vel_theta=1.0`

9. **端到端验证**
   - 在地图上设置目标点，Go2 自主导航到达

## Open Questions

- Webots ODE 的关节 PD 控制是否支持直接设置 stiffness/damping，
  还是需要在 driver 里手动实现 PD 控制器？
- `webots_ros2_a100` 包的结构是否可以作为参考模板？

## Closure Summary (2026-05-21)

### Plan Status

- 状态：收尾完成（范围内开发任务完成，效果验收部分保留）
- 结论：Webots 链路已打通并可运行，但控制稳定性与 MuJoCo 基线仍有明显差距。

### Completed Scope

- Phase 1：完成静态模型与场景搭建，Go2 可在 Webots 场景加载。
- Phase 2：完成 driver 与 Phase 2 启动文件，关节状态、IMU、里程计可发布。
- Phase 3：完成 RL policy 推理链路、关节重排测试与联合启动，`/cmd_vel` 可驱动运动。
- Phase 4：完成 Nav2 参数、地图与集成启动文件，具备端到端联调入口。

### Residual Gaps

- 物理与控制效果未达到 MuJoCo 同级稳定性：存在晃动与翻倒风险。
- Phase 4 端到端导航到点验收未形成稳定通过结论。

### Decisions for This Cycle

- 不修改 policy 算法本体，优先做执行层与接触参数的工程侧收敛。
- Webots 优化先告一段落，本阶段以“可运行 + 可复现 + 可继续调参”为交付标准。

### Next Entry Point

- 下轮若继续 Webots 优化，优先项：
   1. 执行层参数化（跟踪增益、速度限幅、步进限幅）。
   2. 接触参数网格扫描（地面-足端摩擦与阻尼）。
   3. 固定基准用例（前进 10s / 转向 10s）建立可量化对比。
