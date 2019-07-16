cmake_minimum_required(VERSION 2.8.12)

project(CameraApp)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(camera src/main.cpp)
target_link_libraries(camera ${CONAN_LIBS})
