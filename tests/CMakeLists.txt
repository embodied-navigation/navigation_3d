add_executable(navigation_3d_smoke_test smoke_test.cpp)
target_link_libraries(
  navigation_3d_smoke_test
  PRIVATE
    navigation_3d_world_model
    navigation_3d_robot_model
    navigation_3d_traversability
    navigation_3d_global_planner
    navigation_3d_local_planner
)
add_test(NAME navigation_3d_smoke_test COMMAND navigation_3d_smoke_test)
