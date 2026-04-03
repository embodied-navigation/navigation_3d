#pragma once

namespace navigation_3d::global_planner
{
  struct PathRequest
  {
    double start_x{0.0};
    double start_y{0.0};
    double start_z{0.0};
    double goal_x{0.0};
    double goal_y{0.0};
    double goal_z{0.0};
  };
} // namespace navigation_3d::global_planner
