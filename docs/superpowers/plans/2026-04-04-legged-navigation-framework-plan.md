# Legged Navigation Framework Plan

## Objective

Define the first implementation stage of a 3D navigation framework that can support both quadruped and humanoid robots.

## Scope for Phase 1

- focus on navigation, not full locomotion control
- support uneven terrain and obstacle-rich 3D environments
- keep robot-specific differences behind configuration and adapter interfaces
- target a simulation-friendly architecture before hardware integration

## Phase 1 Deliverables

- common world model abstractions
- traversability evaluation interfaces
- global route planning over 3D terrain
- local motion corridor or foothold-aware planning hooks
- robot model adapter for morphology-specific constraints

## Recommended Development Order

1. define the core map and cost abstractions
2. define robot capability and constraint interfaces
3. implement a baseline global planner on a simplified 3D representation
4. add traversability scoring for slopes, steps, clearance, and support area
5. add a local planner interface that can later connect to gait or MPC modules

## Risks

- coupling navigation too tightly to one robot morphology
- over-designing full-body planning before basic navigation primitives are stable
- choosing a map representation that is too expensive for fast replanning

## Immediate Next Step

Write the initial architecture spec and choose the first internal terrain representation.
