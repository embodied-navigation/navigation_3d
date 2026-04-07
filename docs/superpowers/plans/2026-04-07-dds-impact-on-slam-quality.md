# DDS Impact On SLAM Quality Plan

## Objective

Validate whether switching DDS to a Fast DDS shared-memory-oriented runtime baseline improves SLAM mapping quality, and make that baseline reproducible in the Docker workflow.

## Scope

- focus on the specific Fast DDS shared-memory configuration proposed for the RS Airy workflow
- treat DDS as a runtime and transport-layer variable, not a SLAM front-end tuning variable
- change Docker runtime environment loading before considering any SLAM code changes
- cover the verified RS Airy workflow first, and only extend to other datasets if the DDS effect is reproducible

## Current Facts

- the existing SLAM quality plan already fixed algorithm-level baselines for RS Airy and NCLT
- DDS configuration has now been observed to affect mapping quality
- build and runtime validation must remain inside Docker unless explicitly changed later
- current RS Airy baseline config is `src/lightning_lm/config/default_rs_airy_front.yaml`
- DDS effects may change effective message timing even when bag input and SLAM config remain unchanged
- the intended runtime change is to source an `env.sh` file from `docker/run.sh`
- the intended DDS baseline is Fast DDS with XML-driven QoS and shared-memory data sharing on `/rslidar_points`

## Working Assumption

The most likely DDS-related failure modes are:

- delayed or bursty IMU delivery
- delayed or bursty point cloud delivery
- changed callback ordering or scheduling behavior
- QoS incompatibility or hidden drops
- transport overhead that changes synchronization stability

This task should therefore validate DDS as an input-timing variable before reopening normal SLAM parameter tuning.

The working implementation direction is:

- set `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`
- set `FASTRTPS_DEFAULT_PROFILES_FILE=~/config/fastdds_shm.xml`
- set `RMW_FASTRTPS_USE_QOS_FROM_XML=1`
- source those exports from `env.sh` when entering the Docker shell through `docker/run.sh`

## Quality Goals

- repeated runs under the same DDS settings produce comparable map quality
- DDS changes can be linked to concrete runtime symptoms rather than vague visual impressions
- one Fast DDS shared-memory baseline can be named as the default for RS Airy quality validation
- future SLAM tuning work can assume DDS is fixed unless a new transport issue appears

## Evaluation Method

1. freeze one bag, one SLAM config, and one launch command
2. implement the Docker entrypoint change so the DDS environment is loaded consistently
3. change only DDS-related settings between runs
4. record for each run:
   - DDS implementation and profile used
   - key ROS environment variables
   - observed topic timing or drop symptoms
   - resulting map quality symptoms
5. compare the Fast DDS shared-memory baseline against the previous non-shared-memory runtime baseline
6. reject any conclusion that cannot be reproduced in at least one repeated run

## Baseline Runtime

1. dataset
   - `/resource/dataset/CSPID/rosbag2_2026_03_29-16_27_32`

2. SLAM command
   - `ros2 run lightning run_slam_offline --input_bag /resource/dataset/CSPID/rosbag2_2026_03_29-16_27_32 --config /workspace/src/lightning_lm/config/default_rs_airy_front.yaml`

3. fixed algorithm assumptions
   - keep `default_rs_airy_front.yaml` unchanged during DDS validation
   - keep IMU pre-rotation enabled
   - keep loop closing and visualization choices fixed unless the test explicitly studies DDS impact on them

4. runtime environment baseline to implement
   - source `env.sh` from `docker/run.sh`
   - export `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`
   - export `FASTRTPS_DEFAULT_PROFILES_FILE=~/config/fastdds_shm.xml`
   - export `RMW_FASTRTPS_USE_QOS_FROM_XML=1`

## DDS Variables To Test

- whether `env.sh` is sourced automatically from `docker/run.sh`
- `RMW_IMPLEMENTATION=rmw_fastrtps_cpp` versus the previous runtime choice
- `FASTRTPS_DEFAULT_PROFILES_FILE=~/config/fastdds_shm.xml`
- `RMW_FASTRTPS_USE_QOS_FROM_XML=1`
- `/rslidar_points` XML profile settings:
  - `publishMode.kind=ASYNCHRONOUS`
  - `data_sharing.kind=AUTOMATIC`
  - `historyMemoryPolicy=DYNAMIC`
- participant socket buffer sizing from the XML profile

## Observation Checklist

- startup discovery stability
- topic subscription success and consistency
- message lag or burst delivery
- IMU and LiDAR synchronization stability
- obvious packet or sample loss symptoms
- drift
- double wall
- pose jump
- unstable initialization
- run-to-run reproducibility

## Constraints

- do not mix DDS changes with SLAM parameter tuning in the same experiment
- do not change dataset, bag segment, or config path during DDS comparison
- do not treat a single visually improved run as sufficient proof
- keep all validation inside the project Docker workflow
- keep the first implementation limited to Docker environment loading and DDS XML configuration

## Risks

- DDS effects may be intermittent and require repeated runs to confirm
- apparent DDS issues may actually be caused by CPU scheduling or container resource contention
- runtime logging may be insufficient unless additional timing instrumentation is added later
- `~` expansion inside `FASTRTPS_DEFAULT_PROFILES_FILE` may depend on where the export is evaluated
- host-container path differences may make the XML profile unavailable unless `env.sh` and `fastdds_shm.xml` are placed deliberately

## Immediate Next Steps

1. add an `env.sh` file that exports the Fast DDS shared-memory environment variables
2. update `docker/run.sh` so the Docker shell sources `env.sh` on entry
3. create `~/config/fastdds_shm.xml` with the shared-memory-oriented Fast DDS profile
4. run repeated offline RS Airy playback with and without the DDS baseline enabled
5. record whether the Fast DDS shared-memory baseline should become the default quality-validation runtime

## Open Questions

- Is the observed quality gain coming from Fast DDS itself, the XML QoS override, or the shared-memory path on `/rslidar_points`?
- Is the effect reproducible across multiple runs of the same bag?
- Does the same DDS sensitivity appear in NCLT, or is it specific to the RS Airy path?
- Should the XML profile remain topic-specific to `/rslidar_points`, or should IMU-related topics also receive explicit profiles?
