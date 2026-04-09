# SLAM 建图质量优化计划

## Objective

围绕已经跑通的 SLAM 数据流，系统诊断并优化建图质量，当前重点放在 RS Airy 路径上的 DDS 运行时基线、位姿抖动诊断，以及它们对最终建图质量的影响。

## Scope

- use the existing working runtime paths as the baseline
- focus on mapping quality rather than basic bring-up
- separate data/input issues from front-end parameter issues and back-end optimization issues
- treat DDS runtime behavior and pose jitter as first-class quality variables before reopening generic parameter tuning

## Current Facts

- the open-source `lightning` dataset flow has been validated functionally
- the RS Airy custom dataset flow has been validated functionally
- the RS Airy baseline runtime config is `src/lightning_lm/config/default_rs_airy_front.yaml`
- the NCLT front-end-only baseline config is `src/lightning_lm/config/default_nclt_frontend_only.yaml`
- RS Airy integration currently uses IMU pre-rotation into the LiDAR frame with runtime extrinsics kept at identity
- build and runtime validation must remain inside Docker
- the current RS Airy baseline bag path is `/resource/dataset/CSPID/rosbag2_2026_03_29-16_27_32`
- the current NCLT baseline bag path is `/resource/dataset/20130110`
- RViz display support now covers the main debug views needed for quality analysis
- the Docker workflow now supports a Fast DDS shared-memory-oriented runtime baseline through `env.sh`
- the current DDS baseline uses:
  - `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`
  - `FASTRTPS_DEFAULT_PROFILES_FILE=${HOME}/config/fastdds_shm.xml`
- the 3D RViz display path now applies a display-only pose rotation outside the core LIO state update
- RViz keyframe outputs now include keyframe path, node markers, and a dedicated pose-array topic, and these keyframe displays are aligned to the same display-pose transform as the scan and trajectory views
- RViz point-cloud publishing has been simplified to `/lightning/recent_scans`, matching the intended Pangolin-style rolling local cloud view
- the Docker build helper now defaults to bounded parallelism instead of unconstrained compilation
  - `RMW_FASTRTPS_USE_QOS_FROM_XML=1`
- after applying the DDS fix, the observed sensor rate recovered to the expected `10 Hz`
- pose jitter has still been observed during dataset playback and may still be affecting de-skewing and scan registration

## Quality Goals

- local maps stay geometrically stable without obvious warping or tearing
- repeated structures align without large double walls or strong ghosting
- turns, corridors, and long straight segments remain consistent
- loop closing improves the map instead of introducing large global distortion
- results are reproducible with fixed bags and fixed configs
- RViz visualization should reach practical parity with the original Pangolin UI for debugging and evaluation
- the restored `10 Hz` sensor delivery rate remains stable across repeated runs
- pose jitter is reduced or explained well enough that it no longer obscures mapping-quality diagnosis

## Evaluation Method

1. define one baseline bag per dataset family
2. fix one baseline runtime command per bag
3. save screenshots and map outputs for each experiment
4. record observed failures using a small set of labels:
   - drift
   - double wall
   - local distortion
   - loop failure
   - pose jump
   - unstable initialization
5. compare each change against the same baseline instead of changing multiple variables at once
6. keep DDS runtime settings fixed while diagnosing pose jitter unless the test explicitly studies DDS timing behavior

## Baseline Commands

1. RS Airy baseline
   - `ros2 run lightning run_slam_offline --input_bag /resource/dataset/CSPID/rosbag2_2026_03_29-16_27_32 --config /workspace/src/lightning_lm/config/default_rs_airy_front.yaml`

2. NCLT front-end-only baseline
   - `ros2 run lightning run_slam_offline --input_bag /resource/dataset/20130110 --config /workspace/src/lightning_lm/config/default_nclt_frontend_only.yaml`

## Observation Checklist

- overall drift
- double wall or ghosting
- turn distortion
- corridor or long straight segment distortion
- local structural stability
- whether disabling or enabling loop closing changes the failure mode
- whether sensor delivery remains near the expected `10 Hz`
- whether pose jitter appears during the startup static segment
- whether the frontend path, backend pose, and current scan jitter together or only one display element does

## UI Parity Targets

- frontend path
- backend or keyframe path
- explicit keyframe node markers
- keyframe node pose array output for direct RViz point inspection
- current scan
- scan history or recent scan context
- accumulated global map
- optional dynamic map layer when available
- pose or vehicle marker for the current frontend pose
- pose or vehicle marker for the current backend pose
- a reusable default RViz config file for the validated debug layout

## RViz Analysis Enhancements

- immediate value
  - keyframe node markers for corner-jump diagnosis
  - keyframe node pose arrays for coordinate sanity checks against the path
  - current frontend and backend pose markers
  - recent scan history to show local registration continuity
  - accumulated global map for long-corridor drift visibility
- next useful additions
  - local map window or cropped neighborhood map
  - keyframe IDs or timestamps on selected markers
  - loop candidate and accepted loop edges when loop closing is enabled
  - point count or keyframe count overlays if performance debugging becomes necessary
- lower priority extras
  - velocity vector markers
  - IMU gravity or heading debug markers
  - residual or confidence overlays if they prove necessary for parameter tuning

## DDS Runtime Baseline

- use the Fast DDS shared-memory-oriented runtime baseline as the current RS Airy default
- enter Docker through `docker/run.sh`, which now sources `env.sh`
- load `config/fastdds_shm.xml` through `FASTRTPS_DEFAULT_PROFILES_FILE`
- keep `/rslidar_points` on the XML profile that uses:
  - `publishMode.kind=ASYNCHRONOUS`
  - `data_sharing.kind=AUTOMATIC`
  - `historyMemoryPolicy=DYNAMIC`

This baseline should now be treated as part of runtime correctness, not only as an optional optimization, because the observed sensor rate recovered to `10 Hz` after the DDS fix.

## Pose Jitter Diagnosis

The current jitter diagnosis order is:

1. Static-Segment Check
   - inspect the bag start segment
   - if pose already jitters while the robot is expected to be still, prioritize IMU initialization, gravity alignment, and timestamp stability

2. Display Versus State Check
   - compare frontend path, backend pose marker, and current scan together
   - if only one display element jitters, suspect visualization issues first
   - if path and scan both jitter, treat it as a true estimation problem

3. Timing Check
   - verify that the restored DDS baseline delivers stable timing, not only average `10 Hz`
   - inspect burst delivery, delayed callback behavior, and LiDAR/IMU timing consistency

4. IMU Initialization Check
   - verify whether the bag provides enough initial static data
   - verify whether startup begins during motion
   - inspect whether gravity direction and angular velocity settle as expected

5. IMU Pre-Rotation Check
   - compare the current `pre_rotate_imu_to_lidar` path against a controlled alternative
   - treat major jitter changes as evidence that frame alignment is contributing

6. Frame And Extrinsic Check
   - re-check axis conventions and sign assumptions
   - verify that the LiDAR-frame interpretation remains internally consistent

## Optimization Order

1. Baseline Assessment
   - freeze the current config and command for each dataset
   - capture the current visual result and the main failure symptoms

2. DDS Runtime Validation
   - keep the Fast DDS shared-memory baseline enabled
   - confirm that the restored `10 Hz` sensor rate remains stable across repeated runs
   - compare map quality before and after the DDS baseline using the same bag and config

3. Input-Layer Validation
   - verify timestamp assumptions remain consistent on the chosen bags
   - verify IMU behavior, frame conventions, and installation assumptions
   - verify the current RS Airy pre-rotation remains stable across more than one bag
   - diagnose whether pose jitter begins in the startup static segment or only after motion starts

4. Visualization Parity
   - treat RViz as an alternative debug UI, not just a temporary topic dump
   - close the gap between Pangolin-visible information and RViz-visible information
   - prioritize global map, current pose marker, recent scan context, and explicit keyframe node markers

5. Front-End Optimization
   - test with loop closing disabled first
   - tune the parameters that affect de-skewing, downsampling, and scan-to-map stability
   - accept a change only if local-map quality improves on the same bag

6. Back-End Validation And Optimization
   - re-enable loop closing only after the front-end trajectory is locally stable
   - evaluate keyframe spacing, loop detection behavior, and graph optimization impact
   - reject settings that improve one loop but damage the rest of the map

7. Consolidation
   - keep one recommended config per validated dataset path
   - keep one recommended DDS runtime baseline for RS Airy quality validation
   - record the final command set, known limitations, and expected visual behavior

## Constraints

- do not mix integration changes with quality tuning unless a new data-path bug is proven
- do not tune multiple unrelated parameters in one experiment
- do not use host-side builds or runtime validation
- keep the RS Airy optimization path centered on the single maintained config
- do not change DDS settings and IMU alignment settings in the same diagnosis run

## Risks

- apparent quality issues may still be caused by hidden input assumptions rather than tunable parameters
- loop closing can mask front-end problems and lead to misleading conclusions
- visual judgment alone can cause false progress if screenshots and map outputs are not preserved
- average topic frequency may look healthy while per-message timing is still unstable
- pose jitter may come from more than one cause at the same time, especially timing plus frame alignment

## Immediate Next Steps

1. treat `default_rs_airy_front.yaml` as the single maintained RS Airy runtime config
2. keep the Fast DDS shared-memory runtime baseline enabled while running RS Airy quality validation
3. verify whether the restored `10 Hz` runtime remains stable across repeated runs
4. diagnose whether current pose jitter is caused by IMU initialization, timing instability, or IMU-LiDAR frame alignment
5. reopen generic parameter tuning only after DDS and pose-jitter diagnosis stop being the dominant uncertainty

## Current Status

- RViz display support has been added for the main SLAM debug views
- the RS Airy configuration set has been consolidated back to a single maintained config
- the Docker workflow now includes the Fast DDS shared-memory-oriented runtime baseline
- the observed sensor rate has recovered to the expected `10 Hz` after the DDS fix
- the current open quality issue is pose jitter during playback
- the 3D display orientation has been corrected with an explicit display-pose transform at the `LaserMapping` call site
- RViz keyframe node displays now follow the same corrected display coordinates as the visible scan and trajectory outputs
- the current RS Airy visualization baseline is considered acceptable: display orientation is corrected and observed mapping quality is normal
- this plan is now the single active quality-optimization plan for SLAM mapping work
