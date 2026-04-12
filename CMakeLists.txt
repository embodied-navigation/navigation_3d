cmake_minimum_required(VERSION 3.16)
project(navigation_3d LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(NAVIGATION_3D_BUILD_TESTS "Enable CTest integration for navigation_3d" ON)

add_library(navigation_3d_project_options INTERFACE)
target_compile_features(navigation_3d_project_options INTERFACE cxx_std_20)
target_compile_options(
  navigation_3d_project_options
  INTERFACE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra -Wpedantic>
)

if(NAVIGATION_3D_BUILD_TESTS)
  include(CTest)
  enable_testing()
endif()
