# Webots Go2 RL Locomotion Integration Design

## Problem Statement

The `navigation_3d` project needs a quadruped simulation that goes beyond a
simple wheeled robot. Unitree Go2 is the target hardware. A velocity-tracking
RL policy trained with `unitree_rl_lab` (Isaac Lab back-end) already exists and
produces stable flat-ground gait. The missing piece is a simulation bridge that
lets the policy run inside a Webots scene and exposes a standard `/cmd_vel`
interface to the existing Nav2-based navigation stack.

## Design Goals

- Load Go2 into Webots from the existing URDF with correct physical parameters
- Run the ONNX policy at 50 Hz inside a ROS 2 node
- Expose `/cmd_vel` → locomotion → `/go2/odom` so Nav2 needs no changes
- Keep all Go2-specific code in one new package `webots_ros2_go2`

## Non-Goals

- Gait algorithm changes (policy is fixed)
- Hardware deployment
- Uneven terrain or stair climbing
- Sensor simulation beyond IMU and ground-truth odometry

## Interfaces

| Topic | Type | Direction | Notes |
|-------|------|-----------|-------|
| `/cmd_vel` | `geometry_msgs/Twist` | Nav2 → policy node | vx ∈ [-1,1], vy ∈ [-0.4,0.4], yaw ∈ [-1,1] |
| `/go2/joint_states` | `sensor_msgs/JointState` | driver → policy | 12 joints, URDF order |
| `/go2/imu` | `sensor_msgs/Imu` | driver → policy | angular velocity + orientation |
| `/go2/joint_commands` | `std_msgs/Float64MultiArray` | policy → driver | 12 target positions, URDF order |
| `/go2/odom` | `nav_msgs/Odometry` | driver → Nav2 | ground-truth from Webots GPS |

## Observation Vector (45-dim, from deploy.yaml)

```
[base_ang_vel * 0.2,          # 3
 projected_gravity * 1.0,     # 3
 cmd_vel * 1.0,               # 3  (vx, vy, yaw)
 joint_pos_rel * 1.0,         # 12 (relative to default_pos)
 joint_vel_rel * 0.05,        # 12
 last_action * 1.0]           # 12
```

## Joint Mapping

URDF joint order (index 0–11):
```
FL_hip, FL_thigh, FL_calf,
FR_hip, FR_thigh, FR_calf,
RL_hip, RL_thigh, RL_calf,
RR_hip, RR_thigh, RR_calf
```

`joint_ids_map = [3, 0, 9, 6, 4, 1, 10, 7, 5, 2, 11, 8]`
maps rl_lab internal index → URDF index.

## Action Decoding

```python
target_pos_rl   = default_joint_pos + action * 0.25
# default_joint_pos = [0.1,-0.1,0.1,-0.1, 0.8,0.8, 1.0,1.0, -1.5,-1.5,-1.5,-1.5]
target_pos_urdf = inverse_remap(target_pos_rl, joint_ids_map)
```

## Physical Parameters (must match Isaac Lab training config)

| Parameter | Value | Source |
|-----------|-------|--------|
| Joint stiffness (kp) | 25.0 (all 12) | deploy.yaml |
| Joint damping (kd) | 0.5 (all 12) | deploy.yaml |
| Joint friction | 0.01 | env.yaml articulation_props |
| Ground static friction | 1.0 | env.yaml physics_material |
| Ground dynamic friction | 1.0 | env.yaml physics_material |
| Ground restitution | 0.0 | env.yaml physics_material |
| Control dt | 0.02 s (50 Hz) | deploy.yaml step_dt |
| Physics step | 0.001 s (1 kHz) | Webots timestep |

## Package Layout

```
src/simulator/webots_ros2/webots_ros2_go2/
├── package.xml
├── CMakeLists.txt
├── resource/
│   └── go2.proto
├── worlds/
│   └── go2_flat.wbt
├── webots_ros2_go2/
│   ├── __init__.py
│   ├── go2_driver.py        # webots_ros2_driver plugin
│   └── rl_policy_node.py    # ONNX inference node
├── config/
│   ├── deploy.yaml          # copied from unitree_rl_lab export
│   └── env.yaml
└── launch/
    └── go2_launch.py
```

## Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Sim-to-sim gap (PhysX vs ODE) causes unstable gait | Medium | Align friction, kp/kd, joint friction to training values |
| Wrong joint remapping causes violent shaking | High | Unit-test remapping with known default pose before full simulation |
| Webots control callback jitter at 50 Hz | Low | Set Webots `basicTimeStep` to 1 ms, trigger control every 20 steps |
| ODE solver diverges with high kp | Low | Reduce kp gradually if needed, keep kd/kp ratio fixed |

## Follow-up Work

- Add lidar sensor to Go2 for obstacle avoidance
- Replace ground-truth odometry with VIO or LIO estimator
- Extend to uneven terrain once flat-ground integration is stable
