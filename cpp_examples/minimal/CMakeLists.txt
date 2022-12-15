project(OVD_TST)

cmake_minimum_required(VERSION 2.4)

if (CMAKE_BUILD_TOOL MATCHES "make")
    add_definitions(-Wall -Werror -Wno-deprecated -pedantic-errors)
endif (CMAKE_BUILD_TOOL MATCHES "make")

find_package(OpenVoronoi)

set(OVD_TST_SRC
    ${OVD_TST_SOURCE_DIR}/main.cpp
)

add_executable(
    ovd_tst
    ${OVD_TST_SRC}
)
target_link_libraries(ovd_tst OpenVoronoi::openvoronoi)
