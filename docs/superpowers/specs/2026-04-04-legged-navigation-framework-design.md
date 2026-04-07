# Legged Navigation Framework Design

## Problem Statement

Quadruped and humanoid robots operate in environments where classic planar navigation is not enough. The framework needs to reason about terrain shape, support quality, body clearance, slope, steps, and robot-specific motion constraints while still exposing a reusable navigation stack.

## Design Goals

- support both quadruped and humanoid robots from one shared framework
- separate robot-agnostic navigation logic from robot-specific capability models
- allow multiple terrain representations behind stable interfaces
- start with simulation and offline evaluation before hardware-specific integration

## Non-Goals for the First Stage

- full-body whole-body control
- gait generation
- actuator-level control
- production-grade multi-robot orchestration

## Proposed Architecture

### Core layers

1. `world_model`
   - owns terrain and obstacle representations
   - provides query interfaces for height, occupancy, clearance, and local surface properties

2. `robot_model`
   - describes robot envelope, support geometry, step limits, slope limits, and locomotion constraints
   - enables morphology-specific adaptation without changing planners

3. `traversability`
   - computes terrain cost and feasibility from world and robot models
   - exposes reusable scoring for slope, roughness, step height, gap width, and support confidence

4. `global_planner`
   - plans coarse routes through the environment
   - initially can operate on a voxel grid, elevation map, or sparse traversability graph

5. `local_planner`
   - refines short-horizon motion decisions
   - should expose hooks for foothold-aware or body corridor planning

6. `interfaces`
   - simulation adapters
   - sensor/map ingestion adapters
   - external command and visualization interfaces

## Recommended First Internal Representation

Start with a hybrid terrain model:

- local elevation or signed-height representation for fast terrain queries
- obstacle occupancy layer for collision checks
- derived traversability grid or graph for planning

This is a pragmatic first step because it is simpler than a full semantic 3D scene graph while still covering most navigation decisions needed by legged robots.

## Robot Abstraction Strategy

The framework should treat quadrupeds and humanoids as different parameterizations of a shared capability interface rather than separate stacks.

Suggested capability inputs:

- body footprint or swept volume
- nominal support polygon assumptions
- maximum climbable step height
- allowable slope range
- minimum passage width
- body clearance requirements
- dynamic stability margin hints

## Suggested Repository Evolution

The repository should remain a single integration root while internal boundaries mature. A practical next structure is:

- `slam/`
- `perceptor/`
- `pnc/`
- `nav_protocol/`
- `nav_launch/`
- `nav_common/`
- `docs/`
- `docker/`
- `scripts/`
- `.github/`

Inside those modules, the navigation framework should still preserve the core abstractions described earlier, such as world model, robot model, traversability, and planner layers.

## Key Technical Tradeoff

The main tradeoff is between representation richness and replanning speed. A dense 3D model improves fidelity, but a legged navigation framework still needs planning abstractions that can answer feasibility queries quickly.

## Suggested First Milestone

Build a simulation-only prototype that:

- ingests a simple terrain map
- loads robot capability parameters
- computes traversability costs
- outputs a 3D global path across uneven terrain
