project(cpp_polygon)

cmake_minimum_required(VERSION 3.15...3.25)

message(STATUS "configuring c++ test: " ${PROJECT_NAME})

find_package(OpenVoronoi REQUIRED)
find_package(Boost COMPONENTS program_options REQUIRED)

set(SOURCE_FILES polygon.cpp)
add_executable(${PROJECT_NAME} ${SOURCE_FILES})

target_link_libraries(
    ${PROJECT_NAME}
    OpenVoronoi::openvoronoi
    Boost::program_options
)

add_test(${PROJECT_NAME} ${PROJECT_NAME})

add_test(${PROJECT_NAME}_help ${PROJECT_NAME} --help)
set_property(
    TEST ${PROJECT_NAME}_help
    PROPERTY WILL_FAIL TRUE
)

add_test(${PROJECT_NAME}_d ${PROJECT_NAME} --d) # run in debug mode
