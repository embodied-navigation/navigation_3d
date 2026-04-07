# Legged Navigation Framework Plan

## Objective

Define the first implementation stage of a 3D navigation framework that can support both quadruped and humanoid robots.

## Scope for Phase 1

- focus on navigation, not full locomotion control
- support uneven terrain and obstacle-rich 3D environments
- keep robot-specific differences behind configuration and adapter interfaces
- target a simulation-friendly architecture before hardware integration

## Current Status

- the initial architecture spec has been written in `docs/superpowers/specs/2026-04-04-legged-navigation-framework-design.md`
- the recommended first internal representation is the hybrid terrain model described in that spec
- this planning step is complete and future work should start from the recorded module boundaries and framework abstractions
