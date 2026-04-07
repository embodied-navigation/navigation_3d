# SLAM Quality Validation And Optimization Plan

## Objective

Validate and improve mapping quality for both the verified open-source dataset flow and the verified RS Airy custom dataset flow.

## Scope

- use the existing working runtime paths as the baseline
- focus on mapping quality rather than basic bring-up
- separate data/input issues from front-end parameter issues and back-end optimization issues

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

## Quality Goals

- local maps stay geometrically stable without obvious warping or tearing
- repeated structures align without large double walls or strong ghosting
- turns, corridors, and long straight segments remain consistent
- loop closing improves the map instead of introducing large global distortion
- results are reproducible with fixed bags and fixed configs
- RViz visualization should reach practical parity with the original Pangolin UI for debugging and evaluation

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

## UI Parity Targets

- frontend path
- backend or keyframe path
- explicit keyframe node markers
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

## Optimization Order

1. Baseline Assessment
   - freeze the current config and command for each dataset
   - capture the current visual result and the main failure symptoms

2. Input-Layer Validation
   - verify timestamp assumptions remain consistent on the chosen bags
   - verify IMU behavior, frame conventions, and installation assumptions
   - verify the current RS Airy pre-rotation remains stable across more than one bag

3. Visualization Parity
   - treat RViz as an alternative debug UI, not just a temporary topic dump
   - close the gap between Pangolin-visible information and RViz-visible information
   - prioritize global map, current pose marker, recent scan context, and explicit keyframe node markers

4. Front-End Optimization
   - test with loop closing disabled first
   - tune the parameters that affect de-skewing, downsampling, and scan-to-map stability
   - accept a change only if local-map quality improves on the same bag

5. Back-End Validation And Optimization
   - re-enable loop closing only after the front-end trajectory is locally stable
   - evaluate keyframe spacing, loop detection behavior, and graph optimization impact
   - reject settings that improve one loop but damage the rest of the map

6. Consolidation
   - keep one recommended config per validated dataset path
   - record the final command set, known limitations, and expected visual behavior

## Constraints

- do not mix integration changes with quality tuning unless a new data-path bug is proven
- do not tune multiple unrelated parameters in one experiment
- do not use host-side builds or runtime validation
- keep the RS Airy optimization path centered on the single maintained config

## Risks

- apparent quality issues may still be caused by hidden input assumptions rather than tunable parameters
- loop closing can mask front-end problems and lead to misleading conclusions
- visual judgment alone can cause false progress if screenshots and map outputs are not preserved

## Immediate Next Steps

1. treat `default_rs_airy_front.yaml` as the single maintained RS Airy runtime config
2. use the default RViz config when RViz-based diagnosis is needed
3. reopen parameter tuning only when a new concrete mapping-quality issue is being investigated

## Current Status

- RViz display support has been added for the main SLAM debug views
- the RS Airy configuration set has been consolidated back to a single maintained config
- this task phase is complete and future work should start from the consolidated RS Airy config and the current RViz layout
