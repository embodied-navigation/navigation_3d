# RS Airy Dataset Integration Plan

## Objective

Run `lightning` on the robot's RoboSense RS Airy dataset inside the project Docker environment.

## Current Facts

- `lightning` builds successfully in Docker with `MAKEFLAGS="-j4"`.
- The ROS 2 online workflow runs in Docker with host networking enabled.
- The custom dataset publishes `/rslidar_points` as `sensor_msgs/msg/PointCloud2`.
- The custom dataset publishes `/rslidar_imu_data` as `sensor_msgs/msg/Imu`.
- The point cloud includes `x`, `y`, `z`, `intensity`, `ring`, and `timestamp` fields.
- The current approach is to reuse `lightning`'s RoboSense preprocessing path before considering code changes.
- The confirmed RS Airy scan line count is `96`.
- The current working direction is to pre-rotate IMU measurements into the LiDAR frame and keep runtime extrinsics at identity.
- The visual offline validation for RS Airy now uses the IMU pre-rotation path as the primary integration route.

## Constraints

- keep build and runtime validation inside Docker
- avoid speculative parser changes before the first offline validation
- preserve the stock sample configs by introducing an RS Airy specific config file

## Next Steps

1. treat `default_rs_airy_front.yaml` as the single RS Airy runtime config
2. use the IMU pre-rotation route as the default RS Airy integration strategy
3. validate online playback only when the visual offline workflow needs to be repeated outside rosbag replay
4. revisit point timestamp handling only if drift reappears in later bags

## Risks

- RoboSense point timestamps may still need format verification on longer runs
- the IMU pre-rotation matrix may be only approximately correct for all bags
- UI or runtime library issues may hide data-path problems during early testing

## Open Questions

- Does the IMU pre-rotation strategy remain stable across additional RS Airy bags?
- Does the same strategy hold for online playback, not just offline processing?

## Immediate Next Step

Use the current RS Airy configuration as the baseline and only reopen integration work if later bags expose new drift or frame-alignment issues.
