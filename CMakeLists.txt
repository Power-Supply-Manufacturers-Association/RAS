cmake_minimum_required(VERSION 3.15)
project(RAS LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if (NOT CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif()

# --- nlohmann/json (header-only, WASM-safe) ---
include(FetchContent)
FetchContent_Declare(json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG tags/v3.11.3)
FetchContent_MakeAvailable(json)

# --- Generated typed header: quicktype(schemas) -> RAS.hpp (the MAS.hpp pattern) ---
find_program(QUICKTYPE quicktype REQUIRED)
set(RAS_HPP "${CMAKE_CURRENT_BINARY_DIR}/RAS.hpp")
set(PEAS_SCHEMAS "${CMAKE_CURRENT_SOURCE_DIR}/../PEAS/schemas")
add_custom_command(
    OUTPUT "${RAS_HPP}"
    COMMAND "${QUICKTYPE}" -l c++ -s schema
            "${CMAKE_CURRENT_SOURCE_DIR}/schemas/RAS.json"
            -S "${CMAKE_CURRENT_SOURCE_DIR}/schemas/resistor.json"
            -S "${CMAKE_CURRENT_SOURCE_DIR}/schemas/varistor.json"
            -S "${CMAKE_CURRENT_SOURCE_DIR}/schemas/inputs.json"
            -S "${CMAKE_CURRENT_SOURCE_DIR}/schemas/inputs/designRequirements.json"
            -S "${CMAKE_CURRENT_SOURCE_DIR}/schemas/outputs.json"
            -S "${CMAKE_CURRENT_SOURCE_DIR}/schemas/utils.json"
            -S "${PEAS_SCHEMAS}/utils.json"
            -S "${PEAS_SCHEMAS}/inputs/twoTerminalOperatingPoint.json"
            -S "${PEAS_SCHEMAS}/inputs/operatingConditions.json"
            -S "${PEAS_SCHEMAS}/inputs/operatingPointExcitation.json"
            -S "${PEAS_SCHEMAS}/outputs/outputBase.json"
            -S "${PEAS_SCHEMAS}/outputs/measurementCondition.json"
            -o "${RAS_HPP}"
            --namespace RAS --source-style single-source --type-style pascal-case
            --member-style underscore-case --enumerator-style upper-underscore-case --no-boost
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/schemas/RAS.json"
            "${CMAKE_CURRENT_SOURCE_DIR}/schemas/resistor.json"
            "${CMAKE_CURRENT_SOURCE_DIR}/schemas/varistor.json"
            "${CMAKE_CURRENT_SOURCE_DIR}/schemas/inputs/designRequirements.json"
    COMMENT "Generating RAS.hpp via quicktype"
    VERBATIM)
add_custom_target(ras_generated_header DEPENDS "${RAS_HPP}")

# --- Core library ---
add_library(RAS STATIC src/RasConverter.cpp)
add_dependencies(RAS ras_generated_header)
target_include_directories(RAS PUBLIC
    src
    "${CMAKE_CURRENT_BINARY_DIR}"                 # generated RAS.hpp
    "${CMAKE_CURRENT_SOURCE_DIR}/../PEAS/src")    # Fidelity.hpp
target_link_libraries(RAS PUBLIC nlohmann_json::nlohmann_json)
# quicktype emits `#include "json.hpp"`; expose nlohmann's header dir so it resolves.
target_include_directories(RAS PRIVATE "${json_SOURCE_DIR}/include/nlohmann")

# --- Tests ---
if (NOT EMSCRIPTEN)
    # --- native tests ---
    option(RAS_BUILD_TESTS "Build RAS unit tests" ON)
    if (RAS_BUILD_TESTS)
        enable_testing()
        FetchContent_Declare(Catch2
            GIT_REPOSITORY https://github.com/catchorg/Catch2.git GIT_TAG v3.8.1)
        FetchContent_MakeAvailable(Catch2)
        add_executable(ras_tests tests/test_ras.cpp)
        target_link_libraries(ras_tests PRIVATE RAS Catch2::Catch2WithMain)
        add_test(NAME ras_tests COMMAND ras_tests)
    endif()

    # --- pybind11 module: PyRAS ---
    option(RAS_BUILD_PYBIND "Build the PyRAS pybind11 module" ON)
    if (RAS_BUILD_PYBIND)
        FetchContent_Declare(pybind11
            GIT_REPOSITORY https://github.com/pybind/pybind11.git GIT_TAG v2.13.6)
        FetchContent_Declare(pybind11_json
            GIT_REPOSITORY https://github.com/pybind/pybind11_json.git)
        FetchContent_MakeAvailable(pybind11 pybind11_json)
        pybind11_add_module(PyRAS src/bindings.cpp)
        add_dependencies(PyRAS ras_generated_header)
        target_include_directories(PyRAS PRIVATE
            src "${CMAKE_CURRENT_SOURCE_DIR}/../PEAS/src"
            "${pybind11_json_SOURCE_DIR}/include")
        target_link_libraries(PyRAS PRIVATE RAS)
    endif()
else()
    # --- emscripten/WASM module: libRAS (JSON-string ABI via embind) ---
    add_executable(libRAS src/libRAS.cpp)
    add_dependencies(libRAS ras_generated_header)
    target_include_directories(libRAS PRIVATE
        src "${CMAKE_CURRENT_SOURCE_DIR}/../PEAS/src")
    target_link_libraries(libRAS PRIVATE RAS)
    set_target_properties(libRAS PROPERTIES SUFFIX ".wasm.js")
    target_compile_options(libRAS PRIVATE -fwasm-exceptions)
    target_link_options(libRAS PRIVATE
        -fwasm-exceptions -sWASM=1 -sALLOW_MEMORY_GROWTH -sEXPORT_ES6=1
        -sMODULARIZE=1 -sENVIRONMENT=web,node --bind)
endif()
