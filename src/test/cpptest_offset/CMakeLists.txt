project(cpp_offset)

cmake_minimum_required(VERSION 3.15...3.25)

message(STATUS "configuring c++ test: " ${PROJECT_NAME})

find_package(OpenVoronoi REQUIRED)
find_package(Boost COMPONENTS program_options REQUIRED)

set(SOURCE_FILES offset.cpp)
add_executable(${PROJECT_NAME} ${SOURCE_FILES} )

target_link_libraries(
    ${PROJECT_NAME}
    OpenVoronoi::openvoronoi
    Boost::program_options
)

add_test(${PROJECT_NAME} ${PROJECT_NAME})
