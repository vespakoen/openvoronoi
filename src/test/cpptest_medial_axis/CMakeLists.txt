project(cpp_medial_axis)

cmake_minimum_required(VERSION 3.15...3.25)

message(STATUS "configuring c++ test: " ${PROJECT_NAME})

find_package(OpenVoronoi REQUIRED)

set(SOURCE_FILES medial_axis.cpp)
add_executable(${PROJECT_NAME} ${SOURCE_FILES})

target_link_libraries(${PROJECT_NAME} OpenVoronoi::openvoronoi)

add_test(${PROJECT_NAME} ${PROJECT_NAME})
