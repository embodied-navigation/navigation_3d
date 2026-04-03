#pragma once

namespace navigation_3d::robot_model
{
  struct RobotCapabilities
  {
    double max_step_height{0.0};
    double max_slope_degrees{0.0};
    double min_passage_width{0.0};
    double body_clearance{0.0};
  };
} // namespace navigation_3d::robot_model
