add_library(navigation_3d_local_planner INTERFACE)
target_include_directories(navigation_3d_local_planner INTERFACE include)
target_link_libraries(
  navigation_3d_local_planner
  INTERFACE
    navigation_3d_project_options
    navigation_3d_world_model
    navigation_3d_robot_model
    navigation_3d_traversability
)
