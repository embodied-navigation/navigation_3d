#pragma once

namespace navigation_3d::local_planner
{
  struct LocalPlanWindow
  {
    double horizon_seconds{0.0};
    double corridor_width{0.0};
  };
} // namespace navigation_3d::local_planner
