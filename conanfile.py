#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class MbedTLSConan(ConanFile):
    name = "mbedtls"
    version = "2.13.0"
    description = "An open source, portable, easy to use, readable and flexible SSL library "
    url = "https://github.com/bincrafters/conan-mbedtls"
    homepage = "https://github.com/ARMmbed/mbedtls"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "Apache-2.0"
    exports = ["LICENSE.md"]
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        source_url = "https://github.com/ARMmbed/mbedtls"
        tools.get("{0}/archive/{1}-{2}.tar.gz".format(source_url, self.name, self.version))
        # Not a mistake, name is actually mbedtls-mbedtls-version
        extracted_dir = '{0}-{0}-{1}'.format(self.name, self.version)
        os.rename(extracted_dir, self.source_subfolder)

        tools.replace_in_file(os.path.join(self.source_subfolder, 'CMakeLists.txt'),
                              'set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /WX")', '')

        x509_crt_h = os.path.join(self.source_subfolder, 'include', 'mbedtls', 'x509_crt.h')
        tools.replace_in_file(x509_crt_h,
                              '#if defined(MBEDTLS_X509_CRT_PARSE_C)',
                              '#if defined(MBEDTLS_X509_CRT_PARSE_C)\n'
                              '#ifdef _MSC_VER\n'
                              '    #if defined(X509_USE_SHARED)\n'
                              '        #define X509_EXPORT __declspec(dllimport)\n'
                              '    #elif defined(X509_BUILD_SHARED)\n'
                              '        #define X509_EXPORT __declspec(dllexport)\n'
                              '    #else\n'
                              '        #define X509_EXPORT extern\n'
                              '    #endif\n'
                              '#else\n'
                              '    #define X509_EXPORT extern\n'
                              '#endif\n')
        tools.replace_in_file(x509_crt_h,
                              'extern const mbedtls_x509_crt_profile mbedtls_x509_crt_profile_default;',
                              'X509_EXPORT const mbedtls_x509_crt_profile mbedtls_x509_crt_profile_default;')
        tools.replace_in_file(x509_crt_h,
                              'extern const mbedtls_x509_crt_profile mbedtls_x509_crt_profile_next;',
                              'X509_EXPORT const mbedtls_x509_crt_profile mbedtls_x509_crt_profile_next;')
        tools.replace_in_file(x509_crt_h,
                              'extern const mbedtls_x509_crt_profile mbedtls_x509_crt_profile_suiteb;',
                              'X509_EXPORT const mbedtls_x509_crt_profile mbedtls_x509_crt_profile_suiteb;')
        tools.replace_in_file(os.path.join(self.source_subfolder, 'include', 'mbedtls', 'bn_mul.h'),
                              '#if defined(__i386__) && defined(__OPTIMIZE__)',
                              '#if defined(__i386__) && defined(__OPTIMIZE__) && !defined(__PIC__)')

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.definitions["ENABLE_TESTING"] = "Off"
        cmake.definitions["ENABLE_PROGRAMS"] = "Off"
        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        if self.settings.os == "Windows" and self.options.shared:
            cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = "On"

        cmake.definitions["USE_SHARED_MBEDTLS_LIBRARY"] = self.options.shared
        cmake.definitions["USE_STATIC_MBEDTLS_LIBRARY"] = not self.options.shared
        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()
        
    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)
        self.copy(pattern="apache-2.0.txt", dst="licenses", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()
        
    def package_info(self):
        self.cpp_info.libs = ['mbedtls', 'mbedx509', 'mbedcrypto']
        if self.settings.compiler == 'Visual Studio':
            if int(str(self.settings.compiler.version)) < 14:
                self.cpp_info.defines.append("MBEDTLS_PLATFORM_SNPRINTF_MACRO=MBEDTLS_PLATFORM_STD_SNPRINTF")
            else:
                self.cpp_info.defines.append("MBEDTLS_PLATFORM_SNPRINTF_MACRO=snprintf")
        if self.options.shared:
            self.cpp_info.defines.append('X509_USE_SHARED')
        self.cpp_info.bindirs.append('lib')
