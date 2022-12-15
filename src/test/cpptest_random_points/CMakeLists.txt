project(cpp_random_points)

cmake_minimum_required(VERSION 3.15...3.25)

message(STATUS "configuring c++ test: " ${PROJECT_NAME})

find_package(OpenVoronoi REQUIRED)
find_package(Boost COMPONENTS program_options REQUIRED)

set(SOURCE_FILES random_points.cpp)
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

add_test(${PROJECT_NAME}_b ${PROJECT_NAME} --b 2)
add_test(${PROJECT_NAME}_200 ${PROJECT_NAME} --n 200)

# for coverage-testing this takes too long..
#add_test(${PROJECT_NAME}_10000 ${PROJECT_NAME} --n 10000)
