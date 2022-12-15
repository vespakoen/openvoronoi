project(cpp_medial_axis_pocket)

message(STATUS "configuring c++ test: " ${PROJECT_NAME})

find_package(OpenVoronoi REQUIRED)
find_package(Boost COMPONENTS program_options REQUIRED)

set(SOURCE_FILES medial_axis_pocket.cpp)

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

add_test(${PROJECT_NAME}_debug ${PROJECT_NAME} --d )
