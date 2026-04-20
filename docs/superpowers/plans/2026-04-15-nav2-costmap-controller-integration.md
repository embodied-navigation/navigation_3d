# Nav2 Costmap Controller Integration Plan

## Objective

Introduce a navigation-safe control layer for `navigation_3d` by reusing Nav2's
`nav2_costmap_2d` package as a local obstacle representation, then teaching the
existing controller stack to use that costmap for stop/slowdown decisions.

## Scope for Phase 1

- keep the existing planner stack unchanged
- keep the current pure-pursuit controller as the baseline tracking algorithm
- add a lightweight costmap node instead of importing the full Nav2 controller stack
- use static map + inflation first, then add obstacle sensing later
- publish controller safety state in a way that can be consumed by RViz and logs

## Constraints

- preserve the current `planner / controller / nav_protocol / nav_launch` split
- avoid coupling the controller to Nav2 behavior-tree or controller-server internals
- keep the first integration small enough to validate in the existing smoke test flow
- support the current fake SLAM and static map setup before introducing real sensors

## Implementation Changes

- add a new costmap package/node that wraps `nav2_costmap_2d`
- load `StaticLayer` and `InflationLayer` in the first version
- expose the local costmap on a ROS topic for the controller to subscribe to
- extend controller status reporting with safety-related fields such as:
  - `has_costmap`
  - `safe_to_track`
  - `collision_risk`
  - `safety_mode`
  - `safety_message`
- add a minimal controller safety check:
  - slow down when the lookahead point falls into high-cost cells
  - stop when the forward cells are lethal or collision risk is high
- add RViz visibility for the local costmap so the control decision can be inspected

## Test Plan

- start the current minimal navigation launch and confirm the costmap topic appears
- verify the costmap display in RViz alongside `/map`, `/plan`, and controller markers
- confirm the controller still tracks normally in free space
- confirm the controller slows or stops when the lookahead path enters high-cost areas
- keep the existing minimal navigation smoke test as the regression gate

## Assumptions

- the first integration should use an independent costmap node, not in-controller costmap ownership
- the first phase will not include dynamic obstacle perception
- the first phase will focus on safety gating, not full local replanning
- the current pure-pursuit controller remains the baseline until a later controller plugin is added

## Open Questions

- whether the costmap topic should be published as a raw `OccupancyGrid` or via a dedicated adapter interface
- whether controller safety should fail closed to `STOPPED` or `FAULT` when the costmap is missing
- whether the costmap node should live under `src/costmap/` or be placed inside the current `nav_launch` integration area
