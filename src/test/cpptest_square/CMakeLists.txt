project(cpp_square)

cmake_minimum_required(VERSION 3.15...3.25)

message(STATUS "configuring c++ test: " ${PROJECT_NAME})

find_package(OpenVoronoi REQUIRED)

set(SOURCE_FILES polygon_square.cpp)
add_executable(${PROJECT_NAME} ${SOURCE_FILES})

target_link_libraries(
    ${PROJECT_NAME}
    OpenVoronoi::openvoronoi
)

add_test(NAME ${PROJECT_NAME} COMMAND ${PROJECT_NAME})
