# RS Airy Lightning Integration Design

## Problem Statement

`navigation_3d` needs a repeatable way to run `lightning` on a custom RoboSense RS Airy dataset without relying on ad hoc command sequences or dataset-specific guesswork.

The integration needs to preserve the current Docker-first workflow, reuse the existing `lightning` RoboSense ingestion path when possible, and make the first validation path easy to debug.

## Confirmed Inputs

- LiDAR topic: `/rslidar_points`
- LiDAR message type: `sensor_msgs/msg/PointCloud2`
- IMU topic: `/rslidar_imu_data`
- IMU message type: `sensor_msgs/msg/Imu`
- Point cloud fields observed so far: `x`, `y`, `z`, `intensity`, `ring`, `timestamp`

These inputs are compatible with the current `lightning` RoboSense preprocessing path at the field level.

## Design Goals

- keep the integration inside the project Docker workflow
- avoid modifying upstream `lightning` code unless the dataset proves incompatible
- isolate RS Airy settings in a dedicated YAML file
- prefer an offline first-run path before online playback validation
- document the minimum data assumptions needed for future RoboSense datasets

## Non-Goals

- tuning final SLAM quality before the dataset is confirmed runnable
- generalizing all RoboSense models behind a new abstraction layer
- changing `lightning` core algorithms before basic dataset compatibility is proven

## Proposed Design

### 1. Dataset-specific configuration

Create a dedicated RS Airy configuration derived from `default_robosense.yaml`.

The dedicated config should own:

- LiDAR topic name
- IMU topic name
- `lidar_type: 4`
- the confirmed `scan_line` value
- IMU pre-rotation settings that align IMU measurements into the LiDAR frame before ingestion
- any RS Airy specific runtime toggles needed during validation

This keeps the upstream example configs intact and makes later comparisons easier.

### 2. IMU frame alignment strategy

For the current RS Airy dataset, the preferred integration path is:

- rotate incoming IMU angular velocity into the LiDAR frame before passing it into `lightning`
- rotate incoming IMU linear acceleration into the LiDAR frame before passing it into `lightning`
- use identity LiDAR-IMU rotation and zero translation in the runtime config after that pre-rotation step

This is the chosen strategy because the direct calibrated extrinsic path still produced unstable map behavior, while IMU pre-rotation with identity extrinsics produced a stable-looking mapping result in validation.

The current baseline runtime config for this strategy is `src/lightning_lm/config/default_rs_airy_front.yaml`.
The same config now also owns the default UI toggles for both Pangolin and RViz-based debugging:

- keep `use_rviz: false` for the default runtime path
- set `use_rviz: true` when RViz visualization is needed
- keep `step_on_kf: false` by default and enable it only for focused debugging

### 3. Docker-first runtime model

Build, test, and runtime validation should continue inside the project Docker environment.

Required runtime assumptions:

- host networking enabled for ROS 2 discovery
- workspace mounted at `/workspace`
- dataset directory mounted at `/resource`
- Pangolin runtime libraries available from `/usr/local/lib`

This preserves one canonical execution environment for both offline and online runs.

### 4. Validation order

The first validation path should be:

1. confirm LiDAR scan line count from the `ring` range
2. run `run_slam_offline` against the RS Airy bag
3. inspect startup, parsing, and synchronization behavior
4. compare frame-alignment strategies if the map still diverges
5. only after offline success, validate `run_slam_online` with bag playback

Offline-first is preferred because it reduces ROS 2 runtime variables and makes the first failure easier to classify.

## Interface Contract

For the current RoboSense preprocessing path to remain valid, the RS Airy dataset is assumed to provide:

- `sensor_msgs/msg/PointCloud2` on `/rslidar_points`
- `sensor_msgs/msg/Imu` on `/rslidar_imu_data`
- point fields `x`, `y`, `z`, `intensity`, `ring`, and `timestamp`
- point timestamps interpretable by the existing RoboSense preprocessing logic

If any of these assumptions fail during offline validation, the next step is not parameter tuning. The next step is to inspect and adapt the point cloud preprocessing path or the IMU frame-alignment path.

## Key Tradeoff

The main tradeoff is speed of first validation versus up-front generalization.

Reusing the existing RoboSense path is the fastest route to a first run, but it depends on the RS Airy message layout being close enough to the assumptions already encoded in `lightning`.

## Risks

- `scan_line` may be set incorrectly if it is inferred without checking the full `ring` range
- per-point `timestamp` semantics may differ from what `lightning` expects
- the chosen IMU pre-rotation matrix may still need refinement if later bags expose drift
- UI and runtime-library issues may mask data-path failures during the first online run
- successful startup may still hide point ordering or timing problems until synchronization begins

## Follow-Up Work

- record the confirmed RS Airy `scan_line` and first working command sequence
- document the IMU pre-rotation matrix provenance and coordinate-frame assumption
- document any required config overrides beyond topic names
- if preprocessing changes are required, write a follow-up spec for RoboSense point format normalization

## Current Decision

Adopt the IMU pre-rotation strategy as the default RS Airy integration path and keep `default_rs_airy_front.yaml` as the single maintained runtime config for this dataset.
