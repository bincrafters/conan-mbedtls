#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class MbedTLS(ConanFile):
    name = "mbedtls"
    version = "2.11.0"
    description = "An open source, portable, easy to use, readable and flexible SSL library "
    url = "https://github.com/bincrafters/conan-mbedtls"
    license = "Apache-2.0"
    exports = ["LICENSE.md"]
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False] }
    default_options = "shared=False"

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def source(self):
        source_url = "https://github.com/ARMmbed/mbedtls"
        tools.get("{0}/archive/{1}-{2}.tar.gz".format(source_url, self.name, self.version))
        # Not a mistake, name is actually mbedtls-mbedtls-version
        extracted_dir = '{0}-{0}-{1}'.format(self.name, self.version)
        os.rename(extracted_dir, self.source_subfolder)

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.definitions["ENABLE_TESTING"] = "Off"
        cmake.definitions["ENABLE_PROGRAMS"] = "Off"

        if self.settings.os == "Windows" and self.options.shared:
            cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = "On"

        # if self.settings.compiler == 'Visual Studio':
            # cmake.definitions["CMAKE_C_FLAGS"] = "-DMBEDTLS_PLATFORM_SNPRINTF_MACRO=snprintf"
            # cmake.definitions["CMAKE_CXX_FLAGS"] = "-DMBEDTLS_PLATFORM_SNPRINTF_MACRO=snprintf"
       
        cmake.definitions["USE_SHARED_MBEDTLS_LIBRARY"] = self.options.shared
        cmake.definitions["USE_STATIC_MBEDTLS_LIBRARY"] = not self.options.shared
        cmake.configure(build_folder=self.build_subfolder)
        return cmake
    
    def build(self):
        cmake = self.configure_cmake()
        cmake.build()
        
    def package(self):   
        cmake = self.configure_cmake()
        cmake.install()
        
    def package_info(self):
        # the order below matters. If changed some linux builds may fail.
        self.cpp_info.libs = [ 'mbedtls', 'mbedx509', 'mbedcrypto' ]

        if self.settings.os == "Windows":
            self.cpp_info.defines.append("MBEDTLS_PLATFORM_SNPRINTF_MACRO=snprintf")
