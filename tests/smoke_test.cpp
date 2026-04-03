#include "navigation_3d/global_planner/path_request.hpp"
#include "navigation_3d/local_planner/local_plan.hpp"
#include "navigation_3d/robot_model/robot_capabilities.hpp"
#include "navigation_3d/traversability/traversability_score.hpp"
#include "navigation_3d/world_model/world_model.hpp"

int main()
{
  navigation_3d::world_model::WorldQuery query{};
  navigation_3d::robot_model::RobotCapabilities robot{};
  navigation_3d::traversability::TraversabilityScore score{};
  navigation_3d::global_planner::PathRequest request{};
  navigation_3d::local_planner::LocalPlanWindow window{};

  const bool smoke_test_passed = query.x == 0.0 && robot.max_step_height == 0.0 &&
                                 score.feasibility == 0.0 && request.goal_x == 0.0 &&
                                 window.horizon_seconds == 0.0;

  return smoke_test_passed ? 0 : 1;
}
