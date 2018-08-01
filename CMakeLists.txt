cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(MSVC)
    add_definitions(-DMBEDTLS_PLATFORM_SNPRINTF_MACRO=snprintf)
endif()

add_subdirectory("source_subfolder")
