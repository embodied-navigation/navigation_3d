# Fast DDS Shared Memory Runtime Design

## Problem Statement

SLAM mapping quality has been observed to change when DDS runtime behavior changes. The repository therefore needs one explicit, repeatable DDS runtime baseline rather than relying on whatever middleware defaults happen to be present in the container session.

The immediate target is the RS Airy workflow, where LiDAR delivery behavior on `/rslidar_points` appears sensitive to DDS configuration.

## Design Goals

- make the DDS runtime baseline explicit when entering the Docker development shell
- keep the first implementation outside the SLAM algorithm code path
- prefer one shared runtime hook over per-command manual exports
- use Fast DDS XML profiles to control topic-specific behavior for `/rslidar_points`
- keep the change reversible so the previous baseline can still be compared

## Non-Goals

- changing SLAM front-end or back-end parameters
- changing bag contents or ROS message definitions
- introducing a large DDS abstraction layer in repository code
- tuning every ROS topic before the `/rslidar_points` path is validated

## Proposed Design

### 1. Docker shell environment hook

When entering the development container through `docker/run.sh`, source an `env.sh` file before handing control to the interactive shell.

The intended exports are:

```bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export FASTRTPS_DEFAULT_PROFILES_FILE=~/config/fastdds_shm.xml
export RMW_FASTRTPS_USE_QOS_FROM_XML=1
```

This keeps DDS runtime selection and XML profile loading in one predictable place rather than depending on users to re-enter exports manually.

### 2. Fast DDS XML baseline

The DDS profile file should live at:

```text
~/config/fastdds_shm.xml
```

Initial baseline content:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
  <participant profile_name="participant_profile_ros2" is_default_profile="true">
    <rtps>
      <name>profile_for_ros2_context</name>
      <sendSocketBufferSize>104857600</sendSocketBufferSize>
      <listenSocketBufferSize>104857600</listenSocketBufferSize>
    </rtps>
  </participant>

  <data_writer profile_name="default publisher profile" is_default_profile="true">
    <historyMemoryPolicy>DYNAMIC</historyMemoryPolicy>
  </data_writer>

  <data_reader profile_name="default subscription profile" is_default_profile="true">
    <historyMemoryPolicy>DYNAMIC</historyMemoryPolicy>
  </data_reader>

  <data_writer profile_name="/rslidar_points">
    <qos>
      <publishMode>
        <kind>ASYNCHRONOUS</kind>
      </publishMode>
      <data_sharing>
        <kind>AUTOMATIC</kind>
      </data_sharing>
    </qos>
    <historyMemoryPolicy>DYNAMIC</historyMemoryPolicy>
  </data_writer>

  <data_reader profile_name="/rslidar_points">
    <qos>
      <data_sharing>
        <kind>AUTOMATIC</kind>
      </data_sharing>
    </qos>
    <historyMemoryPolicy>DYNAMIC</historyMemoryPolicy>
  </data_reader>
</profiles>
```

### 3. Runtime intent

The intended effect of this baseline is:

- force ROS 2 to use `rmw_fastrtps_cpp`
- load DDS QoS and transport-related behavior from XML
- allow Fast DDS to use automatic data sharing on `/rslidar_points`
- keep memory policy dynamic for both default readers and writers
- increase participant socket buffer sizes so bursty traffic is less likely to be bottlenecked by default buffers

### 4. Validation boundary

The first validation stage should change only:

- Docker shell environment loading
- Fast DDS XML profile selection

It should not change:

- `default_rs_airy_front.yaml`
- IMU pre-rotation settings
- loop closing configuration
- bag path
- offline command line

## Interface And File Layout

Expected file and hook layout:

- `docker/run.sh`
- repository-root `env.sh`
- user-home `~/config/fastdds_shm.xml`

Expected runtime flow:

1. run `./docker/run.sh`
2. Docker shell sources `env.sh`
3. ROS 2 processes inherit Fast DDS environment variables
4. Fast DDS loads `~/config/fastdds_shm.xml`
5. offline SLAM validation runs under the shared-memory-oriented DDS baseline

## Key Tradeoffs

The main tradeoff is between speed of deployment and portability.

Sourcing `env.sh` from `docker/run.sh` is simple and visible, but it assumes the XML path and home-directory layout are stable for the intended user workflow.

Topic-specific XML tuning is also pragmatic for the current RS Airy bottleneck, but it may need to expand later if IMU timing or other topics are shown to be DDS-sensitive as well.

## Risks

- `FASTRTPS_DEFAULT_PROFILES_FILE=~/config/fastdds_shm.xml` depends on the final shell environment resolving `~` as intended
- the XML profile may exist on the host but not in the expected location inside the container
- the quality gain may come from asynchronous publish mode rather than shared memory specifically
- the observed improvement may be workload-specific to RS Airy and not generalize
- container networking or CPU contention may still dominate the observed behavior

## Follow-Up Work

- record the exact before-and-after quality comparison for RS Airy
- decide whether `env.sh` should become a tracked repository file
- decide whether `fastdds_shm.xml` should also become a tracked repository asset instead of a user-home file
- extend topic-specific XML tuning only if `/rslidar_imu_data` or other topics show similar sensitivity

## Current Decision

Adopt Fast DDS with XML-driven QoS and automatic data sharing on `/rslidar_points` as the first DDS runtime candidate to validate for RS Airy SLAM quality.
