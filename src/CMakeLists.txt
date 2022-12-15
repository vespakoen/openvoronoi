project(OpenVoronoi)

message(STATUS "CMAKE_CURRENT_SOURCE_DIR: " ${CMAKE_CURRENT_SOURCE_DIR})
cmake_minimum_required(VERSION 3.15...3.25)

if(COMMAND cmake_policy)
  cmake_policy(SET CMP0003 NEW)
  cmake_policy(SET CMP0025 NEW)
  cmake_policy(SET CMP0091 NEW) # for multithreaded  https://cmake.org/cmake/help/latest/policy/CMP0091.html
  cmake_policy(SET CMP0094 NEW) # for Python*_FIND_STRATEGY=LOCATION
  cmake_policy(SET CMP0042 NEW)
  cmake_policy(SET CMP0054 NEW)
endif(COMMAND cmake_policy)

# install targets in root of the build dir, using $<0:> generator expression to force it from not being overwritten
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/$<0:>)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/$<0:>)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/$<0:>)
foreach(OUTPUTCONFIG ${CMAKE_CONFIGURATION_TYPES})
  string(TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG} ${CMAKE_BINARY_DIR}/$<0:>)
  set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_${OUTPUTCONFIG} ${CMAKE_BINARY_DIR}/$<0:>)
  set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${OUTPUTCONFIG} ${CMAKE_BINARY_DIR}/$<0:>)
endforeach()

set(CMAKE_CXX_STANDARD 14)

if(WIN32)
  set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL")
endif()

option(BUILD_PYTHON_MODULE "Build python-module? " OFF)
option(BUILD_PY_TESTS "Build/configure Python tests?" OFF)
option(BUILD_DOC "Build doxygen documentation? " OFF)
option(BUILD_CPP_TESTS "Build c++ tests?" OFF)

# figure out the gcc version
include(gcc_version.cmake)

# uninstall target
configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake.in"
  "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
  IMMEDIATE @ONLY)

add_custom_target(uninstall
  COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake)

# experimental use of clang, since it detects more warnings/errors than gcc
option(USE_CLANG "build application with clang" OFF) # OFF is the default
# Note: useful packages: clang, llvm, gcc-multilib
# see: http://stackoverflow.com/questions/7031126/switching-between-gcc-and-clang-llvm-using-cmake
if(USE_CLANG)
  set(CMAKE_C_COMPILER             "/usr/bin/clang")
  set(CMAKE_C_FLAGS                "-Wall -std=c99")
  set(CMAKE_C_FLAGS_DEBUG          "-g")
  set(CMAKE_C_FLAGS_MINSIZEREL     "-Os -DNDEBUG")
  set(CMAKE_C_FLAGS_RELEASE        "-O4 -DNDEBUG")
  set(CMAKE_C_FLAGS_RELWITHDEBINFO "-O2 -g")

  set(CMAKE_CXX_COMPILER             "/usr/bin/clang++")
  set(CMAKE_CXX_FLAGS                "-Wall")
  set(CMAKE_CXX_FLAGS_DEBUG          "-g")
  set(CMAKE_CXX_FLAGS_MINSIZEREL     "-Os -DNDEBUG")
  set(CMAKE_CXX_FLAGS_RELEASE        "-DNDEBUG") # -O3 gives "argument unused" ?
  set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O2 -g")

  add_definitions(-O3)
  # -Wno-error=uninitialized -Wno-deprecated -Wno-long-long
  add_definitions(-Werror -Wall -Wundef  -Wshadow -pedantic -pedantic-errors)
  add_definitions(-fPIC)
endif()

message(STATUS " Your compiler is = " ${CMAKE_CXX_COMPILER})
message(STATUS " Your linker is = " ${CMAKE_LINKER})

#
# Turn compiler warnings up to 11, at least with gcc.  I don't know how to
# do this with other compilers we might support and I'm leaving it up to
# the relevant platform maintainers...
# #include'ing the boost graph-library creates deprecated warnings
# thus we use now use -Wno-deprecated here.
#
if(UNIX AND NOT APPLE)
  message(STATUS "setting strict gcc options: -Wall -Werror etc...")
  add_definitions(-Werror -Wall -Wundef -Wno-error=uninitialized -Wshadow  -Wno-long-long -Wno-deprecated -pedantic -pedantic-errors)

  # some reasons why we don't enable certain errors:
  # -Wfloat-equal        gives warning when comparing float/double with != or ==:
  # -Winline             gives warnings for BGL

  add_definitions(-fPIC)
endif()

# uncomment one of these to change build-type
# Release runs much faster than the others
# Debug/Profile/Coverage run slower but are useful for testing

# set(CMAKE_BUILD_TYPE Release)
# set(CMAKE_BUILD_TYPE Debug)
# set(CMAKE_BUILD_TYPE Profile)
# set(CMAKE_BUILD_TYPE Coverage)
message(STATUS " CMAKE_BUILD_TYPE  = " ${CMAKE_BUILD_TYPE})

if(CMAKE_BUILD_TYPE MATCHES "Profile")
  set(CMAKE_CXX_FLAGS_PROFILE "-p -g -DNDEBUG")
  message(STATUS " CMAKE_CXX_FLAGS_PROFILE = " ${CMAKE_CXX_FLAGS_PROFILE})
  set(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS_PROFILE})
endif()

if(CMAKE_BUILD_TYPE MATCHES "Release")
  message(STATUS " CMAKE_CXX_FLAGS_RELEASE = " ${CMAKE_CXX_FLAGS_RELEASE})
  set(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS_RELEASE})
endif()

if(CMAKE_BUILD_TYPE MATCHES "Debug")
  message(STATUS " CMAKE_CXX_FLAGS_DEBUG = " ${CMAKE_CXX_FLAGS_DEBUG})
  #message(STATUS " CMAKE_CXX_FLAGS = " ${CMAKE_CXX_FLAGS})
endif()
message(STATUS " CMAKE_CXX_FLAGS = " ${CMAKE_CXX_FLAGS})

# build the library for code-coverage testing
if(CMAKE_BUILD_TYPE MATCHES "Coverage")
  set(CMAKE_CXX_FLAGS "-O0 -fprofile-arcs -ftest-coverage -fno-inline ${CMAKE_CXX_FLAGS_DEBUG}")
  message(STATUS " CMAKE_CXX_FLAGS = " ${CMAKE_CXX_FLAGS})
endif()

message(STATUS "build type = ${CMAKE_BUILD_TYPE}")

################ create version_string.hpp, http://stackoverflow.com/questions/3780667
include(version_string.cmake)
set(MY_VERSION "${GIT_MAJOR_VERSION}.${GIT_MINOR_VERSION}.${GIT_PATCH_VERSION}" CACHE STRING "version")
# include the output directory, where version_string.hpp is generated
include_directories(${CMAKE_CURRENT_BINARY_DIR})

# this defines the source-files
set(OVD_SRC
  ${PROJECT_SOURCE_DIR}/voronoidiagram.cpp
  ${PROJECT_SOURCE_DIR}/vertex.cpp
  ${PROJECT_SOURCE_DIR}/edge.cpp
  ${PROJECT_SOURCE_DIR}/checker.cpp
  ${PROJECT_SOURCE_DIR}/common/point.cpp
  ${PROJECT_SOURCE_DIR}/vertex_positioner.cpp
  ${PROJECT_SOURCE_DIR}/common/numeric.cpp
  ${PROJECT_SOURCE_DIR}/medial_axis_pocket.cpp
  ${PROJECT_SOURCE_DIR}/medial_axis_walk.cpp
  ${PROJECT_SOURCE_DIR}/offset.cpp
  )

set(OVD_INCLUDE_FILES
  ${PROJECT_SOURCE_DIR}/graph.hpp
  ${PROJECT_SOURCE_DIR}/voronoidiagram.hpp
  ${PROJECT_SOURCE_DIR}/vertex.hpp
  ${PROJECT_SOURCE_DIR}/edge.hpp
  ${PROJECT_SOURCE_DIR}/site.hpp
  ${PROJECT_SOURCE_DIR}/checker.hpp
  ${PROJECT_SOURCE_DIR}/vertex_positioner.hpp
  ${PROJECT_SOURCE_DIR}/kdtree.hpp

  ${PROJECT_SOURCE_DIR}/offset.hpp
  ${PROJECT_SOURCE_DIR}/offset_sorter.hpp

  ${PROJECT_SOURCE_DIR}/filter.hpp
  ${PROJECT_SOURCE_DIR}/medial_axis_filter.hpp
  ${PROJECT_SOURCE_DIR}/medial_axis_walk.hpp
  ${PROJECT_SOURCE_DIR}/medial_axis_pocket.hpp
  ${PROJECT_SOURCE_DIR}/polygon_interior_filter.hpp
  ${PROJECT_SOURCE_DIR}/island_filter.hpp

  ${CMAKE_CURRENT_BINARY_DIR}/version_string.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/version.hpp
  )

set(OVD_INCLUDE_COMMON_FILES
  ${PROJECT_SOURCE_DIR}/common/numeric.hpp
  ${PROJECT_SOURCE_DIR}/common/point.hpp
  ${PROJECT_SOURCE_DIR}/common/halfedgediagram.hpp
  )

set(OVD_INCLUDE_UTIL_FILES
  ${PROJECT_SOURCE_DIR}/utility/vd2svg.hpp
  ${PROJECT_SOURCE_DIR}/utility/simple_svg_1.0.0.hpp
  )


set(OVD_INCLUDE_SOLVERS_FILES
  ${PROJECT_SOURCE_DIR}/solvers/solution.hpp
  ${PROJECT_SOURCE_DIR}/solvers/solver.hpp

  ${PROJECT_SOURCE_DIR}/solvers/solver_lll.hpp
  ${PROJECT_SOURCE_DIR}/solvers/solver_lll_para.hpp

  ${PROJECT_SOURCE_DIR}/solvers/solver_ppp.hpp
  ${PROJECT_SOURCE_DIR}/solvers/solver_qll.hpp

  ${PROJECT_SOURCE_DIR}/solvers/solver_sep.hpp
  ${PROJECT_SOURCE_DIR}/solvers/solver_alt_sep.hpp
  )

# include directories
include_directories(${PROJECT_SOURCE_DIR})

# find the qd library
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/../cmake) # Findqd.cmake is in this dir
find_package(qd REQUIRED)
message(STATUS "libqd include dir = ${QD_INCLUDE_DIR}")
message(STATUS "libqd library = ${QD_LIBRARY}")
include_directories(${QD_INCLUDE_DIR})

if(DEFINED ENV{BOOST_ROOT})
  set(Boost_NO_SYSTEM_PATHS ON)
endif()
set(Boost_DEBUG ON CACHE BOOL "boost-debug")
set(Boost_USE_STATIC_LIBS ON CACHE BOOL "boost-use-static-libs")
if(CMAKE_BUILD_TYPE MATCHES Debug)
	set(Boost_USE_DEBUG_LIBS     ON)
	set(Boost_USE_RELEASE_LIBS   OFF)
else()
	set(Boost_USE_DEBUG_LIBS     OFF)
	set(Boost_USE_RELEASE_LIBS   ON)
endif()
set(Boost_USE_MULTITHREADED  ON)
if(WIN32)
  # use static python lib
  if(Boost_USE_STATIC_LIBS)
    add_definitions(-D BOOST_PYTHON_STATIC_LIB)
  endif()
  # disable autolinking in boost
  add_definitions(-D BOOST_ALL_NO_LIB) # avoid LNK1104 on Windows: http://stackoverflow.com/a/28902261/122441
endif()

# the Python module
if(${BUILD_PYTHON_MODULE} MATCHES ON)
  # find boost-python
  find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
  find_package(Boost COMPONENTS python${Python_VERSION_MAJOR}${Python_VERSION_MINOR} REQUIRED)

  # static c++ library, linked with the python module below
  add_library(
    openvoronoi_static
  STATIC
    ${OVD_SRC}
    )

  target_link_libraries(openvoronoi_static PRIVATE Boost::boost)

  # the Python module itself
  Python_add_library(
    openvoronoi
  MODULE
    pythonlib/open_voronoi_py.cpp
    )

  target_link_libraries(
    openvoronoi
  PRIVATE
    openvoronoi_static
    Boost::boost
    Boost::python${Python_VERSION_MAJOR}${Python_VERSION_MINOR}
    Python::Module
    ${QD_LIBRARY}
    )

  # this installs the python library
  install(
    TARGETS openvoronoi
    LIBRARY
    DESTINATION "openvoronoi"
    )

  # this installs the python VTK-visualization helper py-files
  # install(
  #   FILES ${PROJECT_SOURCE_DIR}/py/ovdvtk.py
  #   ${PROJECT_SOURCE_DIR}/py/ngc_writer.py
  #   ${PROJECT_SOURCE_DIR}/py/ovdgenerators.py
  #   DESTINATION "openvoronoi"
  #   PERMISSIONS OWNER_READ GROUP_READ WORLD_READ
  #   )
else()
  find_package(Boost REQUIRED)

  # the pure c++ shared library
  add_library(
    openvoronoi
  SHARED
    ${OVD_SRC}
    )

  if(WIN32)
    # on windows, prefix the library with lib, and make sure the .lib file is installed as well
    set_target_properties(openvoronoi PROPERTIES
      PREFIX "lib"
      WINDOWS_EXPORT_ALL_SYMBOLS ON)
  endif()

  include(GNUInstallDirs)

  # this installs the c++ include headers
  install(
    FILES ${OVD_INCLUDE_FILES}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/openvoronoi
    PERMISSIONS OWNER_READ GROUP_READ WORLD_READ
    COMPONENT headers
    )
  install(
    FILES ${OVD_INCLUDE_COMMON_FILES}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/openvoronoi/common
    PERMISSIONS OWNER_READ GROUP_READ WORLD_READ
    )
  install(
    FILES ${OVD_INCLUDE_UTIL_FILES}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/openvoronoi/utility
    PERMISSIONS OWNER_READ GROUP_READ WORLD_READ
    )
  install(
    FILES ${OVD_INCLUDE_SOLVERS_FILES}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/openvoronoi/solvers
    PERMISSIONS OWNER_READ GROUP_READ WORLD_READ
    )

  # add include directories
  target_include_directories(openvoronoi
    PRIVATE
      ${PROJECT_SOURCE_DIR}/common
      ${PROJECT_SOURCE_DIR}/utility
      ${PROJECT_SOURCE_DIR}/solvers
      ${PROJECT_SOURCE_DIR}
    PUBLIC
      $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
      $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}/openvoronoi>
  )

  target_link_libraries(openvoronoi PUBLIC Boost::boost ${QD_LIBRARY})

  # c++lib for coverage testing
  add_library(
    openvoronoi-coverage
  SHARED
  EXCLUDE_FROM_ALL # not built by default
    ${OVD_SRC}
    )

  # set_target_properties(openvoronoi-coverage PROPERTIES PREFIX "")
  set_target_properties(
    openvoronoi-coverage
  PROPERTIES
    CMAKE_BUILD_TYPE Coverage
    CMAKE_CXX_FLAGS "-O0 -fprofile-arcs -ftest-coverage -fno-inline ${CMAKE_CXX_FLAGS_DEBUG}"
    )

  # this installs the c++ library
  install(
    TARGETS openvoronoi
    EXPORT openvoronoitargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}/openvoronoi
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}/openvoronoi
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}/openvoronoi
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/openvoronoi
    PERMISSIONS OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE
  )

  # this install the cmake targets
  install(
    EXPORT openvoronoitargets
    FILE "${PROJECT_NAME}Targets.cmake"
    DESTINATION "share/cmake/${PROJECT_NAME}"
    NAMESPACE "${PROJECT_NAME}::"
  )

  # this creates the cmake config
  include(CMakePackageConfigHelpers)
  configure_package_config_file(
    "${PROJECT_SOURCE_DIR}/../cmake/${PROJECT_NAME}Config.cmake.in"
    "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
    INSTALL_DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake
  )

  # this installs the cmake config
  install(FILES "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/${PROJECT_NAME}
  )

  # tests
  if(${BUILD_CPP_TESTS} MATCHES ON)
    include(${CMAKE_CURRENT_SOURCE_DIR}/test/ovd_cpp_tests.cmake) # cmake file defines c++ tests
  endif()
  if(${BUILD_PY_TESTS} MATCHES ON)
    include(${CMAKE_CURRENT_SOURCE_DIR}/test/ovd_py_tests.cmake) # cmake file defines Python tests
  endif()

endif() # end Python module

# doxygen documentation
include(doxygen.cmake)

# coverage-report target
# running "make coverage-report" produces a code-coverate report for the tests
# uses ctest, lcov, genhtml
message(STATUS "lcov cmake src dir ${CMAKE_CURRENT_SOURCE_DIR}")
add_custom_target(coverage-report
  COMMAND lcov --directory ./ --zerocounters
  # COMMAND make ExperimentalCoverage
  # COMMAND ctest -D Experimental Coverage -R cpptest
  COMMAND ctest -R cpptest -E "cpptest_arc\\|cpptest_ttt_glyph_big_7\\|cpptest_ttt_glyph_small_35" # exclude failing tests!
  COMMAND lcov --directory ./ --capture  --output-file testcoverage.info # --base-directory ${CMAKE_CURRENT_SOURCE_DIR}
  COMMAND lcov --directory ./ --extract testcoverage.info \"*/openvoronoi*\" --output-file testcoverage_ext.info
  COMMAND genhtml --show-details --prefix \"${CMAKE_CURRENT_SOURCE_DIR}\" --output-directory coverage-report --title OpenVoronoi testcoverage_ext.info
  )

# Debian package
# "make package" will build a binary package
# "make spackage" will build a source-package (for uploading to a PPA)
set(SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR})
include(${CMAKE_CURRENT_SOURCE_DIR}/deb/package_details.cmake)
add_custom_target(spackage
  ${CMAKE_COMMAND} -D SRC_DIR:STRING=${CMAKE_CURRENT_SOURCE_DIR}
  -D MY_VERSION:STRING=${MY_VERSION}
  -C ${CMAKE_CURRENT_SOURCE_DIR}/deb/package_details.cmake # a lot of variables etc. defined here
  -P ${CMAKE_CURRENT_SOURCE_DIR}/deb/DebSourcePPA.cmake # the script that builds a debian package
  )
include(CPack) # this should be last
