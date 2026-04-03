#pragma once

namespace navigation_3d::traversability
{
  struct TraversabilityScore
  {
    double feasibility{0.0};
    double terrain_cost{0.0};
    double stability_margin{0.0};
  };
} // namespace navigation_3d::traversability
