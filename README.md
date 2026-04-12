# navigation_3d

`navigation_3d` is the public integration repository for the embodied-navigation organization.

## Role

This repository is the current primary development entrypoint for the `navigation_3d` framework.
It is responsible for:

- ROS 2 workspace integration
- launch and runtime assembly
- development environment bootstrap
- documentation, scripts, and CI
- future repository split planning

## Current Status

The project currently follows a single-main-repository development model.
Future repository split work is planned, but the public development entrypoint remains this repository.

## Planned ROS 2 Packages

- `nav_common`
- `nav_protocol`
- `map_manager`
- `slam`
- `perception`
- `planner`
- `controller`
- `task_manager`
- `nav_launch`

## Development Environment

The standard development environment is Docker-based and centered on Ubuntu 22.04 + ROS 2 Humble.
